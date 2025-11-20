# Style Analysis Whitepaper — Sections 4–5

## 4. Combining Return‑Based and Holdings‑Based Style Analysis

Return‑based and holdings‑based style analyses each provide valuable but incomplete views of a portfolio. The most reliable picture emerges when both are used together and their results are reconciled. In institutional practice, this combined approach is standard for manager due‑diligence, TDF research, and plan lineup analysis.

### 4.1 Complementary Strengths

A useful way to think about the two methods is:

- **Return‑based (RBSA)**
  - What has the portfolio *done*?
  - Captures realised behaviour over time.
  - Naturally incorporates all sources of return, including derivatives, trading, and implementation effects.

- **Holdings‑based**
  - What does the portfolio *own* right now?
  - Shows current positioning in granular detail.
  - Ideal for mandate compliance, sector/region checks, and factor‑aware optimisation.

Because RBSA is historical and behavioural while holdings‑based is cross‑sectional and structural, disagreements between them are often more informative than agreements.

### 4.2 A Simple Combined Framework

A practical combined framework typically involves the following steps:

1. **Compute holdings‑based exposures (\(\beta^{HB}\))** for all relevant factors using the latest holdings and a chosen risk model.  
2. **Run RBSA** over an appropriate lookback window to obtain return‑based exposures (\(\beta^{RBSA}\)).  
3. **Compare \(\beta^{HB}\) and \(\beta^{RBSA}\)** for each factor:
   \[
   \Delta \beta_k = \beta^{HB}_k - \beta^{RBSA}_k.
   \]
4. **Diagnose discrepancies**:
   - Are they due to recent positioning changes?
   - Are derivatives or overlays missing from the holdings data?
   - Is the RBSA window too short or too long?
   - Has the manager changed process?

5. **Construct blended exposures**:
   \[
   \beta^{\text{blend}}_k =
   \omega \cdot \beta^{HB}_k + (1 - \omega) \cdot \beta^{RBSA}_k,
   \]
   where \(\omega\) reflects how much weight to give recent holdings vs. behavioural history.

These blended exposures can then be used in reporting, risk analysis, and optimisation.

### 4.3 Interpreting Divergences

Differences between holdings‑based and return‑based exposures often signal important phenomena:

- **\(\beta^{HB}\) shows a new tilt; \(\beta^{RBSA}\) has not yet moved**  
  → The manager has changed positioning recently; RBSA needs more data.

- **\(\beta^{RBSA}\) shows persistent exposure not visible in \(\beta^{HB}\)**  
  → There may be derivatives, intraday trading, or leverage not captured in static holdings snapshots.

- **Both measures move together but diverge from the stated mandate**  
  → Genuine style drift or mis‑labelled product.

Rather than treating discrepancies as errors, sophisticated teams treat them as **signals** about how the strategy is being implemented and how it may behave going forward.

### 4.4 Use in Due‑Diligence and Oversight

Combined style analysis enables:

- **Mandate validation**: does both holdings‑ and return‑based evidence confirm the target style?  
- **Early warning on style drift**: holdings‑based measures often shift before RBSA; RBSA confirms whether the new tilt is persistent.  
- **Manager communication**: discrepancies can be used as a basis for questions to the manager (“We see your EM exposure rising in holdings, but not yet in behaviour; is this a structural shift?”).

For boards and investment committees, the ability to show both perspectives builds confidence that mandates are monitored thoroughly.

### 4.5 Use in TDF Glidepath and Provider Comparison

When evaluating or designing TDF glidepaths:

- **Holdings‑based analysis** reveals the building blocks, sector and region exposures, duration and credit risk, and any real‑asset or inflation‑hedging components.  
- **RBSA** reveals the effective equity vs. bond mix, factor tilts, and risk behaviour across economic regimes.

A combined view allows consultants and plan sponsors to:

- Compare different providers’ glidepaths on a common factor basis.  
- Assess whether changes in underlying funds are altering glidepath risk.  
- Ensure that risk levels move smoothly across vintages and over time.

### 4.6 Use in Plan Lineup Optimisation

For a given plan menu, combined style analysis allows the optimisation engine to work with:

- **Blended factor exposures** for each fund (which reflect both current holdings and long‑term behaviour).  
- **A factor‑based covariance matrix** that maps exposures into correlations.  
- **Constraints and objectives** expressed at the factor level (e.g., minimum EM equity, maximum HY credit) rather than solely at the fund level.

This leads to more robust and interpretable optimisation results.

---

## 5. Applications in Fund Due‑Diligence & Manager Research

Style analysis is central to professional fund research. It sits alongside performance, risk metrics, qualitative assessments, and operational due‑diligence as one of the pillars of manager evaluation.

### 5.1 Confirming Mandate Alignment

A fund’s stated style—“U.S. Large‑Cap Growth”, “Core Bond”, “Global ex‑U.S. Equity”—is effectively a promise to investors. Style analysis tests that promise.

Using **holdings‑based analysis**, researchers:

- check that sector, region, size, and factor exposures match the mandate;  
- verify that credit quality and duration fall within expected ranges;  
- ensure there is no persistent exposure to out‑of‑mandate assets (e.g., EM equity in a domestic fund).

Using **RBSA**, they:

- verify that long‑term behaviour matches the stated benchmark;  
- check for unexpected factor sensitivities;  
- see whether the fund behaves more like a different peer group.

Discrepancies between stated mandate and measured style raise immediate questions.

### 5.2 Detecting Style Drift

Style drift occurs when a manager gradually moves away from their stated style without a formal strategy change. It can erode diversification, distort peer comparisons, and create governance issues.

Combined style analysis detects drift in several ways:

- **Holdings‑based signals**: rising weights in out‑of‑style sectors, size buckets, or credit qualities.  
- **RBSA signals**: changing factor betas over rolling windows (e.g., a value fund increasingly loading on growth or momentum).

If both methods point to a consistent drift, the manager is likely pursuing a different strategy than originally communicated.

### 5.3 Separating Skill from Factor Bets

A central question in manager research is:

> Is the manager adding value beyond systematic factor exposures?

RBSA helps answer this using the regression intercept \(\alpha\) and factor betas:

- If performance is driven by persistent tilts to rewarded factors (e.g., value, quality) but alpha is near zero, the manager may be a factor provider rather than a stock‑picker.  
- If alpha is positive and robust across regimes, that is stronger evidence of genuine selection skill or timing.

Holdings‑based analysis provides further colour:

- Did outperformance come from stock selection within sectors and styles, or from top‑down allocation decisions?  
- Are factor tilts consistent with the stated philosophy (e.g., a value manager consistently holding cheap, profitable companies)?

### 5.4 Peer‑Group Classification and Benchmark Selection

Style analysis is also critical for placing funds into the correct peer groups and choosing appropriate benchmarks:

- A manager labelled “large‑cap core” but showing persistent mid‑cap and small‑cap tilts may belong in a different Morningstar category or peer universe.  
- An “international” fund with significant EM exposure might be better benchmarked to ACWI ex‑US rather than a developed‑only index.  
- A “core bond” fund with meaningful HY and EM allocations might fit better among multisector or unconstrained bond funds.

Accurate classification improves both performance evaluation and lineup construction.

### 5.5 Measuring Diversification Across Managers

Plan sponsors and multi‑manager portfolios often combine several active strategies. Style analysis helps ensure that:

- manager combinations provide genuine diversification, not redundant exposure;  
- correlations among managers are understood in terms of factor overlaps;  
- portfolio‑level style exposures (e.g., growth vs. value, quality vs. high beta) are consistent with the sponsor’s beliefs and risk appetite.

For example, blending two high‑conviction growth managers that both tilt to the same mega‑cap tech stocks may offer less diversification than combining a growth manager with a quality or low‑volatility strategy.

### 5.6 Identifying Hidden Risks

Lastly, style analysis frequently uncovers risks that are not obvious from marketing materials or fund names:

- a “defensive equity” fund that actually has strong momentum exposure and therefore can underperform abruptly in rotations;  
- a “core bond” fund that depends heavily on credit and EM spreads to generate yield;  
- an “income” equity fund whose high‑yielding stocks cluster in a few sectors (e.g., utilities, REITs, energy), creating sector concentration risk.

Bringing these issues to light is one of the most practical contributions of style analysis to fiduciary oversight.

---

(End of Sections 4–5)
