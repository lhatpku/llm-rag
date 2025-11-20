"""
RAG Evaluation Script using DeepEval

Evaluates the RAG assistant against ground truth Q&A pairs from rag_evaluation_cases.json.
Measures answer quality, context relevance, and retrieval performance.
"""

import os

# Disable ChromaDB telemetry BEFORE any imports to avoid "capture() takes 1 positional argument but 3 were given" warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, ContextualRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.models import GPTModel, DeepEvalBaseLLM

# Import RAG assistant
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import RAGAssistant
from utils.file_utils import load_all_publications
from utils.paths import EVALUATION_CASES_PATH, EVALUATION_RESULTS_DIR, OUTPUTS_DIR

# Load environment variables
load_dotenv()

# Ensure results directory exists
Path(EVALUATION_RESULTS_DIR).mkdir(parents=True, exist_ok=True)

# Configuration: Number of evaluation cases to run
# Set to None to run all cases, or specify a number (e.g., 40) to limit
MAX_EVALUATION_CASES = 40


class RAGEvaluator:
    """
    RAG System Evaluator using DeepEval.
    
    Evaluates the RAG assistant against ground truth Q&A pairs and measures
    answer quality, context relevance, and retrieval performance.
    """
    
    def __init__(
        self,
        max_evaluation_cases: Optional[int] = None,
        use_openai_for_eval: bool = True,
        evaluation_cases_path: Optional[Path] = None,
        results_dir: Optional[Path] = None
    ):
        """
        Initialize the RAG Evaluator.
        
        Args:
            max_evaluation_cases: Maximum number of evaluation cases to run (None = all cases, defaults to MAX_EVALUATION_CASES)
            use_openai_for_eval: Whether to use OpenAI for evaluation metrics (better JSON parsing)
            evaluation_cases_path: Path to evaluation cases JSON file (defaults to EVALUATION_CASES_PATH)
            results_dir: Directory for evaluation results (defaults to EVALUATION_RESULTS_DIR)
        """
        self.max_evaluation_cases = max_evaluation_cases if max_evaluation_cases is not None else MAX_EVALUATION_CASES
        self.use_openai_for_eval = use_openai_for_eval
        
        # Set paths
        self.evaluation_cases_path = evaluation_cases_path or EVALUATION_CASES_PATH
        self.results_dir = results_dir or Path(EVALUATION_RESULTS_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache path
        self.test_cases_cache_path = self.results_dir / "test_cases_cache.json"
        
        # Initialize assistant (lazy loading)
        self._assistant = None

    def _get_assistant(self) -> RAGAssistant:
        """Lazy load and return the RAG assistant."""
        if self._assistant is None:
            print("\nInitializing RAG Assistant...")
            self._assistant = RAGAssistant()
            print("Loading documents...")
            docs = load_all_publications()
            self._assistant.add_documents(docs)
            print(f"Loaded {len(docs)} documents\n")
        return self._assistant
    
    def load_evaluation_cases(self, max_cases: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load evaluation cases from JSON file.
        
        Args:
            max_cases: Maximum number of cases to load (None = use self.max_evaluation_cases)
            
        Returns:
            List of evaluation cases (limited to max_cases if specified)
        """
        if max_cases is None:
            max_cases = self.max_evaluation_cases
        
        with open(self.evaluation_cases_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        
        if max_cases is not None and max_cases > 0:
            cases = cases[:max_cases]
            print(f"Limited to first {max_cases} evaluation cases")
        
        return cases

    def save_test_cases(self, test_cases: List[LLMTestCase], file_path: Optional[Path] = None, max_cases: Optional[int] = None) -> None:
        """
        Save test cases to disk for caching.
        
        Args:
            test_cases: List of LLMTestCase objects
            file_path: Path to save test cases (defaults to cache path)
            max_cases: Maximum number of cases (used for cache file naming)
        """
        if file_path is None:
            # Include max_cases in filename if specified
            if max_cases is not None:
                file_path = self.results_dir / f"test_cases_cache_{max_cases}cases.json"
            else:
                file_path = self.test_cases_cache_path
        
        # Convert test cases to serializable format
        serializable_cases = []
        for tc in test_cases:
            case_data = {
                "input": tc.input,
                "actual_output": tc.actual_output,
                "expected_output": tc.expected_output,
                "context": tc.context if tc.context else None,
                "retrieval_context": getattr(tc, 'retrieval_context', None),
                "metadata": getattr(tc, 'metadata', {}),
            }
            serializable_cases.append(case_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_cases, f, indent=2, ensure_ascii=False)
        
        print(f"Test cases saved to: {file_path}")

    def load_test_cases(self, file_path: Optional[Path] = None, max_cases: Optional[int] = None) -> Optional[List[LLMTestCase]]:
        """
        Load test cases from disk cache.
        
        Args:
            file_path: Path to load test cases from (defaults to cache path)
            max_cases: Maximum number of cases (used for cache file naming, but will try general cache if specific not found)
            
        Returns:
            List of LLMTestCase objects, or None if file doesn't exist
        """
        if max_cases is None:
            max_cases = self.max_evaluation_cases
        
        # Try multiple cache file locations in order of preference
        cache_paths = []
        
        if file_path is None:
            # First try max_cases-specific cache if specified
            if max_cases is not None:
                cache_paths.append(self.results_dir / f"test_cases_cache_{max_cases}cases.json")
            
            # Then try general cache (might have more cases)
            cache_paths.append(self.test_cases_cache_path)
        else:
            cache_paths.append(file_path)
        
        # Try each cache path until we find one that exists
        for cache_path in cache_paths:
            if cache_path.exists():
                print(f"Loading cached test cases from: {cache_path}")
                
                with open(cache_path, 'r', encoding='utf-8') as f:
                    case_data_list = json.load(f)
                
                test_cases = []
                for case_data in case_data_list:
                    test_case = LLMTestCase(
                        input=case_data["input"],
                        actual_output=case_data["actual_output"],
                        expected_output=case_data["expected_output"],
                        context=case_data.get("context"),
                        retrieval_context=case_data.get("retrieval_context"),
                    )
                    # Restore metadata
                    if "metadata" in case_data:
                        test_case.metadata = case_data["metadata"]
                    
                    test_cases.append(test_case)
                
                print(f"Loaded {len(test_cases)} cached test cases")
                return test_cases
        
        # No cache file found
        return None

    def create_test_cases(self, evaluation_cases: List[Dict[str, Any]]) -> List[LLMTestCase]:
        """
        Create DeepEval test cases by running queries through the RAG assistant.
        
        Args:
            evaluation_cases: List of evaluation cases with Question and Answer fields
            
        Returns:
            List of LLMTestCase objects for DeepEval
        """
        assistant = self._get_assistant()
        test_cases = []
        
        print(f"\n{'='*60}")
        print(f"Creating test cases from {len(evaluation_cases)} evaluation cases...")
        print(f"{'='*60}\n")
        
        for i, case in enumerate(evaluation_cases, 1):
            question = case["Question"]
            expected_output = case["Answer"]
            case_id = case.get("id", i)
            
            print(f"[{i}/{len(evaluation_cases)}] Processing: {question[:60]}...")
            
            # Get retrieval context and answer from RAG assistant
            # We need to capture the retrieved context for evaluation
            retrieved = assistant.vector_db.search(query=question, n_results=3)
            retrieved_docs = retrieved.get("documents", [])
            
            # Get the answer
            answer = assistant.invoke(question, n_results=3)
            
            # Create test case - DeepEval LLMTestCase expects context as a list of strings
            # Store metadata separately and attach it to the test case object
            test_case = LLMTestCase(
                input=question,
                actual_output=answer,
                expected_output=expected_output,
                context=retrieved_docs if retrieved_docs else None,  # Must be list of strings or None
                retrieval_context=retrieved_docs,
            )
            
            # Attach metadata as an attribute (not a parameter)
            test_case.metadata = {
                "case_id": case_id,
                "retrieved_doc_ids": retrieved.get("ids", []),
                "retrieval_distances": retrieved.get("distances", []),
            }
            
            test_cases.append(test_case)
        
        return test_cases

    def run_evaluation(
        self,
        test_cases: List[LLMTestCase],
        metrics: Optional[List] = None,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run evaluation using DeepEval.
        
        Args:
            test_cases: List of LLMTestCase objects
            metrics: List of DeepEval metrics to use (default: AnswerRelevancy, ContextualRelevancy, Faithfulness)
            save_results: Whether to save results to JSON file
            
        Returns:
            Dictionary containing evaluation results
        """
        # Configure evaluation model if OpenAI is available
        eval_model = None
        if self.use_openai_for_eval and os.getenv("OPENAI_API_KEY"):
            try:
                # Use GPT-4o-mini for evaluation (better at JSON than default models)
                eval_model = GPTModel(model="gpt-4o-mini")
                print("Using OpenAI GPT-4o-mini for evaluation metrics (better JSON parsing)")
            except Exception as e:
                print(f"Warning: Could not configure OpenAI for evaluation: {e}")
                print("Using default DeepEval evaluation model")
        
        if metrics is None:
            # Create metrics with evaluation model if available
            metric_kwargs = {}
            if eval_model:
                metric_kwargs["model"] = eval_model
            
            metrics = [
                AnswerRelevancyMetric(threshold=0.7, **metric_kwargs),
                ContextualRelevancyMetric(threshold=0.7, **metric_kwargs),
                FaithfulnessMetric(threshold=0.7, **metric_kwargs),
            ]
        
        print(f"\n{'='*60}")
        print(f"Running evaluation with {len(metrics)} metrics on {len(test_cases)} test cases...")
        print(f"{'='*60}\n")
        
        # Run evaluation with error handling for JSON parsing issues
        try:
            evaluate(test_cases, metrics=metrics)
        except ValueError as e:
            if "invalid JSON" in str(e) or "JSONDecodeError" in str(e):
                print(f"\n⚠️  Warning: Evaluation encountered JSON parsing errors.")
                print(f"   This may be due to the evaluation model returning invalid JSON.")
                print(f"   Some metrics may not have been computed correctly.")
                print(f"   Error: {str(e)[:200]}...\n")
                # Continue processing - some metrics may still have been computed
            else:
                raise
        
        # Compile summary statistics
        summary = {
            "total_cases": len(test_cases),
            "metrics": {},
            "overall_scores": {},
        }
        
        # Extract scores from test cases after evaluation
        for metric in metrics:
            metric_name = metric.__class__.__name__
            scores = []
            failed_cases = 0
            
            for test_case in test_cases:
                try:
                    # DeepEval stores results in test_case.metrics or metric object
                    if hasattr(test_case, 'metrics') and metric_name in test_case.metrics:
                        metric_result = test_case.metrics[metric_name]
                        score = metric_result.score if hasattr(metric_result, 'score') else metric_result
                        if score is not None:
                            scores.append(score)
                    elif hasattr(metric, 'score') and metric.score is not None:
                        # Some metrics store score directly
                        scores.append(metric.score)
                except (AttributeError, KeyError, TypeError) as e:
                    # Skip cases where metric evaluation failed
                    failed_cases += 1
                    continue
            
            if scores:
                summary["metrics"][metric_name] = {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "pass_rate": sum(1 for s in scores if s >= metric.threshold) / len(scores),
                    "evaluated_cases": len(scores),
                    "failed_cases": failed_cases,
                }
            else:
                summary["metrics"][metric_name] = {
                    "mean": None,
                    "min": None,
                    "max": None,
                    "pass_rate": None,
                    "evaluated_cases": 0,
                    "failed_cases": failed_cases,
                    "error": "No valid scores computed - likely due to JSON parsing errors"
                }
        
        # Calculate overall pass rate (all metrics must pass)
        pass_counts = {}
        for test_case in test_cases:
            all_passed = True
            for metric in metrics:
                metric_name = metric.__class__.__name__
                if hasattr(test_case, 'metrics') and metric_name in test_case.metrics:
                    metric_result = test_case.metrics[metric_name]
                    score = metric_result.score if hasattr(metric_result, 'score') else metric_result
                    if score < metric.threshold:
                        all_passed = False
                        break
            case_id = getattr(test_case, 'metadata', {}).get("case_id", "unknown")
            pass_counts[case_id] = all_passed
        
        summary["overall_pass_rate"] = sum(pass_counts.values()) / len(pass_counts) if pass_counts else 0
        
        # Save results if requested
        if save_results:
            results_path = self.results_dir / f"evaluation_results_{Path(__file__).stem}.json"
            
            # Prepare detailed results for saving
            detailed_results = {
                "summary": summary,
                "test_cases": [
                    {
                        "input": tc.input,
                        "expected_output": tc.expected_output,
                        "actual_output": tc.actual_output,
                        "context": tc.context if tc.context else [],  # Convert None to empty list for JSON
                        "context_joined": "\n\n".join(tc.context) if tc.context else "",  # For readability
                        "metadata": getattr(tc, 'metadata', {}),
                        "metrics": {
                            name: {
                                "score": metric.score if hasattr(metric, 'score') else metric,
                                "reason": getattr(metric, 'reason', None) if hasattr(metric, 'reason') else None,
                                "threshold": getattr(metric, 'threshold', None) if hasattr(metric, 'threshold') else None,
                            }
                            for name, metric in (tc.metrics.items() if hasattr(tc, 'metrics') else {})
                        }
                    }
                    for tc in test_cases
                ]
            }
            
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n{'='*60}")
            print(f"Results saved to: {results_path}")
            print(f"{'='*60}\n")
        
        return summary

    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print evaluation summary in a readable format."""
        print(f"\n{'='*60}")
        print("EVALUATION SUMMARY")
        print(f"{'='*60}\n")
        
        print(f"Total Test Cases: {summary['total_cases']}\n")
        
        print("Metric Scores:")
        print("-" * 60)
        for metric_name, stats in summary["metrics"].items():
            print(f"\n{metric_name}:")
            if stats.get("mean") is not None:
                print(f"  Mean Score: {stats['mean']:.3f}")
                print(f"  Range: {stats['min']:.3f} - {stats['max']:.3f}")
                print(f"  Pass Rate: {stats['pass_rate']:.1%}")
                if "evaluated_cases" in stats:
                    print(f"  Evaluated: {stats['evaluated_cases']} cases")
                    if stats.get("failed_cases", 0) > 0:
                        print(f"  Failed: {stats['failed_cases']} cases")
            else:
                print(f"  Error: {stats.get('error', 'No scores computed')}")
        
        print(f"\n{'='*60}")
        print(f"Overall Pass Rate (All Metrics): {summary['overall_pass_rate']:.1%}")
        print(f"{'='*60}\n")

    def evaluate(
        self,
        force_regenerate: bool = False,
        max_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main evaluation method.
        
        Args:
            force_regenerate: If True, regenerate test cases even if cache exists
            max_cases: Maximum number of evaluation cases to run (None = use self.max_evaluation_cases)
            
        Returns:
            Dictionary containing evaluation results
        """
        # Use self.max_evaluation_cases if max_cases not specified
        if max_cases is None:
            max_cases = self.max_evaluation_cases
        
        print("="*60)
        print("RAG System Evaluation using DeepEval")
        if max_cases is not None:
            print(f"Running {max_cases} evaluation cases")
        else:
            print("Running all evaluation cases")
        print("="*60)
        
        # Try to load cached test cases first
        test_cases = None
        if not force_regenerate:
            # Try to load from cache (try max_cases-specific cache first, then general cache)
            test_cases = self.load_test_cases(max_cases=max_cases)
            
            # If we have cached test cases but need to limit them, just slice them
            if test_cases is not None and max_cases is not None and len(test_cases) > max_cases:
                print(f"\nLimiting cached test cases from {len(test_cases)} to {max_cases}")
                test_cases = test_cases[:max_cases]
        
        if test_cases is None:
            # Need to generate test cases
            print("\nGenerating test cases (this may take a while)...")
            
            # Load evaluation cases (with limit)
            print("Loading evaluation cases...")
            evaluation_cases = self.load_evaluation_cases(max_cases=max_cases)
            print(f"Loaded {len(evaluation_cases)} evaluation cases\n")
            
            # Create test cases (assistant will be initialized lazily)
            test_cases = self.create_test_cases(evaluation_cases)
            
            # Save test cases for future use
            print("\nSaving test cases to cache...")
            self.save_test_cases(test_cases, max_cases=max_cases)
        else:
            print(f"\nUsing cached test cases (skipping generation)")
            print(f"Evaluating {len(test_cases)} test cases")
        
        # Run evaluation
        summary = self.run_evaluation(test_cases, save_results=True)
        
        # Print summary
        self.print_summary(summary)
        
        return summary


def main(force_regenerate: bool = False, max_cases: Optional[int] = None):
    """
    Main function for command-line usage.
    
    Args:
        force_regenerate: If True, regenerate test cases even if cache exists
        max_cases: Maximum number of evaluation cases to run (None = use default from RAGEvaluator)
    """
    # Default max_cases from class default
    if max_cases is None:
        max_cases = MAX_EVALUATION_CASES
    
    evaluator = RAGEvaluator(max_evaluation_cases=max_cases)
    return evaluator.evaluate(force_regenerate=force_regenerate, max_cases=max_cases)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate RAG system using DeepEval")
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help="Force regeneration of test cases even if cache exists"
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help=f"Maximum number of evaluation cases to run (default: {MAX_EVALUATION_CASES} from config, or None for all)"
    )
    args = parser.parse_args()
    
    # Use MAX_EVALUATION_CASES if --max-cases not provided
    max_cases = args.max_cases if args.max_cases is not None else MAX_EVALUATION_CASES
    
    main(force_regenerate=args.force_regenerate, max_cases=max_cases)
