# Style Analysis Whitepaper — Sections 1–3

## 1. Introduction to Style Analysis

Style analysis is one of the foundational analytical frameworks in modern investment management. It enables investors, asset managers, consultants, and fiduciaries to understand what drives a portfolio’s behaviour, how its performance is generated, and whether it behaves consistently with its stated mandate. Although often associated with equity mutual funds, style analysis is used broadly across equities, fixed income, multi‑asset strategies, factor‑based portfolios, and target‑date funds (TDFs).

At a high level, style analysis answers the question:

> What underlying exposures are responsible for a portfolio’s risk and return?

Every portfolio reflects a mixture of systematic influences: value vs. growth, small‑cap vs. large‑cap, domestic vs. international, interest‑rate vs. credit exposure, cyclical vs. defensive sectors, and macro sensitivities such as inflation or economic growth. Some of these are intentional (e.g., a value manager deliberately tilting to cheap stocks); others are incidental or the result of drift. Style analysis seeks to make those influences explicit and quantifiable.

### 1.1 Why Style Analysis Matters

In modern practice, style analysis underpins a wide range of tasks:

- **Fund due‑diligence and manager research**  
  Validate that a manager is doing what they claim, detect style drift, and separate skill from systematic factor bets.

- **Portfolio construction and diversification**  
  Understand whether multiple funds in a portfolio provide genuinely distinct exposures or are redundant.

- **Target‑date fund and glidepath evaluation**  
  Look through the layers of underlying funds to see the true mix of equity, fixed income, real assets, and factors at each point on the glidepath.

- **Plan lineup design and optimisation**  
  Analyse a defined‑contribution plan’s investment menu to identify gaps (e.g., no EM equity) and overlaps (e.g., three nearly identical large‑cap funds).

- **Risk management and scenario analysis**  
  Relate portfolio outcomes to macro and factor shocks via measured exposures.

Behind all of these use‑cases is a simple idea: labels (“large‑cap growth”, “core bond”, “balanced”) are not enough. Style analysis replaces labels with **measured exposures**.

### 1.2 Return‑Based vs. Holdings‑Based Approaches (High‑Level)

Two complementary methodologies dominate institutional practice:

1. **Return‑Based Style Analysis (RBSA)**  
   - Uses only the portfolio’s historical returns.  
   - Regresses returns on a set of style or factor indices.  
   - Captures *behaviour* – how the portfolio has actually behaved through time.  
   - Excellent for long‑term analysis, TDF reverse‑engineering, and working with opaque vehicles.  
   - Slower to pick up recent changes and sensitive to regime shifts.

2. **Holdings‑Based Style Analysis**  
   - Uses the portfolio’s current holdings and a risk model.  
   - Measures exposures from the characteristics and factor loadings of individual securities.  
   - Provides granular, up‑to‑date information; ideal for compliance and mandate testing.  
   - Dependent on timely, complete holdings and on the chosen risk model.

Neither method is sufficient alone. Return‑based analysis can lag and be noisy; holdings‑based analysis can miss behavioural nuances and intra‑period trading. In practice, serious investors use *both* and reconcile the story between them.

### 1.3 Dimensions Captured by Style Analysis

Although “style” started with the equity style box (large/small, value/growth), modern style analysis spans multiple dimensions:

- **Equity dimensions**
  - Size (large, mid, small)
  - Value vs. growth
  - Momentum
  - Quality / profitability
  - Low‑volatility vs. high‑beta
  - Sector and industry
  - Region and country
  - ESG‑related attributes (where relevant)

- **Fixed‑income dimensions**
  - Interest‑rate exposure (duration, key‑rate durations)
  - Credit quality (AAA–CCC, IG vs. HY)
  - Spread sectors (govt, corporate, securitised, EM debt)
  - Currency exposure
  - Liquidity profile

- **Multi‑asset & macro dimensions**
  - Equity beta
  - Real vs. nominal rate sensitivity
  - Inflation beta
  - Exposure to commodities and real assets
  - Sensitivity to volatility, carry, and trend strategies

A robust style analysis framework allows these exposures to be measured systematically across funds and portfolios.

### 1.4 Role in Risk Management

Portfolios that appear diversified by number of funds or asset classes can be highly concentrated when viewed through style exposures. Examples:

- Two different “large‑cap core” funds that both tilt heavily to U.S. mega‑cap growth and end up with 0.95+ correlation.  
- A “core bond” fund that quietly holds 20–30% high yield and behaves like a mix of IG and equities in stress.  
- An “international equity” fund with heavy U.S. multinational exposure, thus adding less diversification than expected.

Style analysis exposes such situations by decomposing both **risk** and **return** into underlying drivers. This is essential for risk budgeting, scenario analysis, stress testing, and regulatory or fiduciary oversight.

### 1.5 Applications to Target‑Date Funds and Glidepaths

TDFs are multi‑layered structures: each vintage invests in underlying funds, which themselves hold securities. The glidepath—how the equity/fixed‑income/real asset mix evolves as retirement approaches—determines the majority of a participant’s long‑term risk and return.

Style analysis is used to:

- Look through to underlying exposures (e.g., how much EM equity truly exists in the age‑35 vintage?).  
- Compare glidepaths across providers on an apples‑to‑apples basis.  
- Assess consistency of risk levels across vintages.  
- Evaluate whether the TDF’s behaviour matches its stated objective and benchmark.

### 1.6 Applications to Plan Lineup Optimisation

In a defined‑contribution plan, participants and managed‑account providers must build portfolios from a **limited fund menu**. Style analysis is the bridge between:

- the **fund menu**, and  
- a **factor‑based universe** suitable for optimisation.

By mapping each fund to factor exposures, analysts can:

- detect redundancy among funds,  
- identify missing segments of the opportunity set,  
- construct synthetic exposures when certain building blocks are missing, and  
- feed sensible risk and correlation estimates into optimisation engines.

### 1.7 Structure of This Whitepaper

The remainder of this document is organised as follows:

1. **Section 2 – Return‑Based Style Analysis (RBSA):** regression‑based techniques, constrained vs. unconstrained forms, interpretation, and limitations.  
2. **Section 3 – Holdings‑Based Style Analysis:** factor models, aggregation from securities to portfolios, strengths, and weaknesses.  
3. **Section 4 – Combining Return‑ and Holdings‑Based Approaches:** how to reconcile and blend both views.  
4. **Section 5 – Applications in Fund Due‑Diligence and Manager Research.**  
5. **Section 6 – Applications in TDF Glidepath Construction and Comparison.**  
6. **Section 7 – Using Style Analysis for Optimisation on a Plan Lineup.**

---

## 2. Return‑Based Style Analysis (RBSA)

Return‑Based Style Analysis (RBSA), first formalised by William Sharpe, infers a portfolio’s underlying style exposures using only its historical returns. It is especially useful when holdings data are absent, unreliable, or lagged, and has become a standard tool for manager classification, performance attribution, and TDF analysis.

### 2.1 Core Regression Framework

In its canonical form, RBSA models the fund’s excess return as a linear combination of factor excess returns:

\[
R_p(t) - R_f(t) =
\alpha +
\sum_{k=1}^K \beta_k \big(F_k(t) - R_f(t)\big)
+ \varepsilon_t,
\]

where:

- \(R_p(t)\) is the portfolio’s return at time \(t\);  
- \(R_f(t)\) is the risk‑free rate;  
- \(F_k(t)\) is the return of factor or style index \(k\);  
- \(\beta_k\) is the exposure (beta) to factor \(k\);  
- \(\alpha\) is the regression intercept (often interpreted as “alpha”);  
- \(\varepsilon_t\) is the residual term.

The factor indices might represent asset classes (U.S. equity, international equity, core bonds), style buckets (large value, small growth), or risk premia (momentum, quality, low volatility). RBSA then searches for the combination of these factors that best explains the portfolio’s past returns.

### 2.2 Constrained RBSA (Sharpe‑Style)

Sharpe’s original formulation imposes constraints:

- \(\beta_k \ge 0\) for all \(k\);  
- \(\sum_{k=1}^K \beta_k = 1\).

This effectively treats the \(\beta_k\)’s as **weights** in a synthetic reference portfolio built from the factor indices. The interpretation becomes intuitive:

> The fund behaves like a mix of X% U.S. large blend, Y% small value, Z% international, etc.

Constrained RBSA is particularly popular in:

- TDF glidepath reverse‑engineering  
- classifying funds into style boxes  
- decomposing manager behaviour into asset‑class weights  
- high‑level asset allocation analysis

### 2.3 Unconstrained RBSA

In other settings, especially when style factors are not mutually exclusive or when short positions and overlays are possible, the non‑negativity and sum‑to‑one constraints are relaxed:

\[
R_p(t) =
\alpha +
\sum_{k=1}^K \beta_k F_k(t) + \varepsilon_t,
\]

with \(\beta_k \in \mathbb{R}\). This allows:

- negative betas (implicit short exposure or hedging),  
- leverage‑like exposures,  
- more nuanced interpretation of multi‑factor strategies.

Unconstrained RBSA is often used for:

- hedge funds and alternatives,  
- complex multi‑asset and overlay strategies,  
- factor‑oriented research.

### 2.4 Choosing the Factor Set

The quality of RBSA depends heavily on the chosen factor list. Common examples:

- **Equity‑oriented analysis**
  - U.S. large value, U.S. large growth
  - U.S. small value, U.S. small growth
  - international developed equities
  - emerging markets
  - style factors: momentum, quality, low volatility

- **Multi‑asset analysis**
  - U.S. equity, international equity, EM equity
  - U.S. core bonds, global bonds
  - high yield, EM debt
  - REITs, commodities, TIPS

Factors should be:

- relevant to the fund’s mandate,  
- sufficiently broad to capture key risks,  
- not so numerous that multicollinearity dominates.

### 2.5 Interpreting RBSA Outputs

RBSA provides four main interpretive elements:

1. **Factor Exposures (\(\beta_k\))**  
   These describe how sensitive the fund has been to each factor. For example:
   - \(\beta_{\text{US Growth}} = 0.7\) and \(\beta_{\text{US Value}} = 0.1\) indicates a strong tilt to growth.  
   - A non‑trivial \(\beta_{\text{EM}}\) implies hidden EM exposure.

2. **Alpha (\(\alpha\))**  
   The intercept measures the portion of return unexplained by the factor set. A positive, statistically significant alpha over long periods is evidence (though not proof) of manager skill; a negative alpha suggests underperformance after accounting for systematic exposures.

3. **R² (Goodness of Fit)**  
   The regression’s R² measures how much of the fund’s variation is explained by the factors:
   - High R² (0.9+) → the fund behaves like a relatively stable, index‑like mix of exposures.  
   - Moderate R² (0.7–0.9) → a combination of systematic exposures and idiosyncratic decisions.  
   - Low R² (< 0.7) → highly active, niche, or non‑linear behaviour.

4. **Time‑Varying Exposures (Rolling RBSA)**  
   By estimating RBSA on rolling windows (e.g., 36‑ or 60‑month), analysts can track how exposures evolve through time. This is key for detecting style drift, changes in process, or regime‑dependent behaviour.

### 2.6 Strengths and Weaknesses of RBSA

**Strengths**

- Requires only return history; no holdings needed.  
- Captures *how* a fund has actually behaved.  
- Works well for opaque vehicles (CITs, some alternatives).  
- Ideal for reverse‑engineering glidepaths and comparing TDFs.  
- Helps distinguish skill (alpha) from structural bets (betas).

**Weaknesses**

- Slow to detect recent changes; relies on historical windows.  
- Sensitive to multicollinearity among factors.  
- Distorted by regime shifts or short sample periods.  
- Cannot reveal security‑level concentration or risk.  
- Cannot see intra‑period trading.

These limitations motivate the complementary **holdings‑based** approach.

---

## 3. Holdings‑Based Style Analysis

Holdings‑based style analysis starts from the actual positions in the portfolio—every stock, bond, or derivative—and aggregates their characteristics to infer the portfolio’s exposures. It is the standard in institutional risk systems (e.g., Barra, Axioma, MSCI, Morningstar risk models) and is indispensable for mandate monitoring and granular risk management.

### 3.1 From Security Characteristics to Portfolio Exposures

Suppose a portfolio holds \(N\) securities, with weights \(w_i\). For a given factor \(k\), each security has an exposure \(f_{ik}\) (e.g., a value score, duration, or sector dummy). The portfolio’s exposure to factor \(k\) is typically computed as:

\[
\beta_k^{\text{portfolio}} = \sum_{i=1}^N w_i \cdot f_{ik}.
\]

This framework generalises naturally to:

- style factors (value, growth, momentum, quality),
- sectors and industries,
- regions and countries,
- duration and credit buckets,
- liquidity and other risk dimensions.

Because exposures are computed directly from holdings, this method can deliver highly granular and timely insight into what the manager currently owns.

### 3.2 Fundamental vs. Statistical Factor Models

Most holdings‑based systems rely on one of two broad types of factor model:

- **Fundamental factor models**
  - Factors are defined using economically motivated characteristics (valuation ratios, growth metrics, quality indicators).  
  - Widely used in equity risk models (e.g., Barra, Axioma, Morningstar).  
  - Highly interpretable: “This fund has high exposure to value and quality.”  

- **Statistical factor models**
  - Factors are obtained via statistical techniques such as principal component analysis (PCA).  
  - Focus on explaining co‑movement in returns rather than on economic intuition.  
  - Adapt quickly to changing correlation structures but can be harder to interpret.

In practice, many institutions use hybrid approaches that blend economic factors with statistical structure.

### 3.3 Equity Style Exposures via Holdings

For equities, common dimensions include:

- **Size**: based on market capitalisation.  
- **Value vs. growth**: book‑to‑price, earnings yield, cash‑flow metrics.  
- **Momentum**: trailing 6–12‑month returns, adjusted for recent reversals.  
- **Quality**: profitability (ROE, ROIC), leverage, earnings stability.  
- **Volatility / Beta**: historical volatility, beta to a broad market index.  
- **Liquidity**: trading volume, bid–ask spreads.  
- **Sector and industry**: GICS or similar classifications.  
- **Region and country**: domicile or revenue‑based geography.

By aggregating these attributes, analysts can describe a fund as, for example, “tilted to mid‑cap value with a quality bias and modest EM exposure.”

### 3.4 Fixed‑Income Exposures via Holdings

For bonds and fixed‑income funds, holdings‑based analysis focuses on:

- **Duration and key‑rate durations**  
  - Sensitivity to parallel and non‑parallel yield‑curve moves.

- **Credit quality distribution**  
  - Ratings buckets (AAA, AA, A, BBB, BB, B, CCC).  

- **Sector composition**  
  - Treasuries, agencies, corporate IG, high yield, securitised (MBS/ABS/CMBS), EM debt.

- **Spread and curve positioning**  
  - Expected response to spread widening, curve steepening, etc.

- **Currency exposure**  
  - Important for global and EM bond funds.

Holdings‑based analysis thus reveals whether a “core bond” fund is truly high‑quality AGG‑like exposure, or whether it quietly carries large doses of credit and EM risk.

### 3.5 Strengths of Holdings‑Based Analysis

- **Timeliness**: as soon as holdings are updated, exposures can be recalculated.  
- **Granularity**: insight into individual securities, sectors, countries.  
- **Transparency**: vital for compliance, mandate oversight, and board reporting.  
- **Direct linkage to security selection**: supports detailed performance attribution.  
- **Ease of integration into optimisation**: factor exposures and covariance matrices plug directly into MVO and risk‑budgeting frameworks.

### 3.6 Limitations of Holdings‑Based Analysis

- **Dependence on data quality and frequency**: if holdings are infrequent or stale, exposures may misrepresent reality.  
- **Derivatives and overlays**: exposures from futures, options, and swaps can be difficult to capture without complete position data.  
- **Model dependence**: different risk models may compute different factor exposures.  
- **Snapshot nature**: holdings are a point‑in‑time view and do not fully reflect intra‑period trading or the path of returns.

These limitations are precisely why holdings‑based analysis should be complemented with return‑based analysis rather than used in isolation.

---

(End of Sections 1–3)
