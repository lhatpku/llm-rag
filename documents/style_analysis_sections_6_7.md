# Style Analysis Whitepaper — Sections 6–7

## 6. Applications in Target‑Date Fund (TDF) Glidepath Construction

Target‑date funds (TDFs) are multi‑asset portfolios whose asset mix evolves over time according to a glidepath. Because they are widely used as qualified default investment alternatives (QDIAs) in defined‑contribution plans, understanding their risk profile is a fiduciary priority. Style analysis is one of the primary tools used to evaluate and compare TDFs.

### 6.1 Why Glidepath Analysis Requires Style Analysis

A TDF series typically invests in a set of underlying funds (mutual funds, CITs, or ETFs), which in turn hold thousands of securities. The disclosed glidepath—e.g., “90% equity at age 25, 40% equity at retirement”—only tells part of the story. In practice:

- Equity allocations may be biased towards certain regions (e.g., U.S. vs. international, EM).  
- Style tilts (value, growth, quality, momentum) can differ across providers.  
- Fixed‑income exposures vary in duration, credit quality, and securitised vs. government mix.  
- Real‑asset and inflation‑hedging components may be present or absent.  

Style analysis allows consultants and plan sponsors to look through the layers and measure the **true economic exposures** of each vintage.

### 6.2 Holdings‑Based Glidepath Analysis

Using holdings‑based style analysis, one can:

- Aggregate all underlying holdings across the equity, fixed‑income, and real‑asset building blocks for a given vintage.  
- Compute factor exposures: equity region and style, duration, credit, inflation sensitivity, sector tilts, currency exposures.  
- Compare these exposures across vintages (e.g., age‑25 vs. age‑45 vs. retirement).  
- Check whether risk exposures change smoothly along the glidepath or exhibit jumps and irregularities.

This helps answer questions such as:

- Does equity risk decline roughly in proportion to the stated equity allocation?  
- Are there unintended spikes in EM or HY exposure at certain ages?  
- Does duration increase too quickly or too slowly as participants age?  
- How much inflation protection is embedded, and where?

### 6.3 Return‑Based Glidepath Analysis

Return‑based analysis complements holdings‑based analysis by focusing on **behaviour**:

- For each vintage, run RBSA against broad factor indices (U.S. equity, international equity, EM, core bonds, HY, TIPS, REITs, etc.).  
- Estimate effective equity vs. bond exposure and other factor tilts.  
- Compare the implied exposures with those suggested by holdings and by the provider’s marketing materials.

This can reveal, for example, that:

- The true equity beta is consistently 5–10 percentage points higher than the stated equity weight.  
- Fixed‑income behaviour is dominated by credit risk rather than duration.  
- Certain vintages behave more aggressively than others at the same distance from retirement.

Because RBSA naturally incorporates actual return paths, it provides insight into how the glidepath has behaved in different market environments.

### 6.4 Cross‑Vintage Consistency

A well‑designed TDF series should exhibit:

- Monotonic de‑risking: equity beta, volatility, and drawdown potential should gradually decline with age.  
- Smooth transitions: no sharp jumps in risk exposures between adjacent vintages.  
- Consistent implementation: the same investment philosophy applied across the series.

Style analysis can detect:

- **Non‑monotonic risk patterns**, e.g., the 2040 fund being riskier than the 2045 and 2035 funds.  
- **Inconsistent regional or style allocations** across vintages.  
- **Changes over time** in building blocks that materially alter the glidepath’s behaviour.

Such findings are highly relevant for committee discussions about whether a given TDF series remains appropriate for the plan.

### 6.5 Provider Comparison

Plan sponsors often choose between multiple TDF providers (e.g., Vanguard, Fidelity, T. Rowe Price, BlackRock, State Street). Style analysis enables apples‑to‑apples comparison by:

- Mapping each provider’s vintages into common factor exposures (equity style, regions, duration, credit, inflation beta).  
- Comparing risk levels at key ages (e.g., 30 years to retirement, retirement date, post‑retirement).  
- Examining differences in structural tilts (e.g., more EM, more HY, more real assets).

This makes it possible to understand not only “who has more equity at retirement” but also **what kind** of equity and fixed‑income exposure each series is taking.

### 6.6 Custom and “White‑Label” Glidepaths

For custom TDF solutions and “white‑label” retirement date funds, style analysis is equally critical:

- It helps design glidepaths that are consistent with the plan sponsor’s beliefs about appropriate risk levels, inflation protection, and diversification.  
- It ensures that the combination of underlying building blocks matches the intended style exposures at each age.  
- It supports ongoing monitoring to ensure that the implemented glidepath does not drift away from policy.

In short, style analysis is a core component of both off‑the‑shelf and custom glidepath governance.

---

## 7. Style Analysis for Portfolio Optimisation Within a Plan Lineup

Defined‑contribution participants and managed‑account providers rarely have access to a fully open investment universe. Instead, they must build portfolios from a finite plan lineup—often 10–25 funds. Optimising portfolios under these constraints is only sensible if one understands how each fund behaves in terms of underlying exposures. Style analysis is the tool that enables this.

### 7.1 From Plan Menu to Factor Universe

The first step is to turn the plan menu into a factor‑based representation:

1. For each fund in the lineup, compute **holdings‑based factor exposures** using a risk model.  
2. Run **RBSA** on each fund to obtain behavioural factor exposures over a relevant lookback window.  
3. Construct a **blended exposure vector** for each fund:
   \[
   \beta^{\text{blend}}_k(j) =
   \omega \cdot \beta^{HB}_k(j) +
   (1 - \omega) \cdot \beta^{RBSA}_k(j),
   \]
   where \(j\) indexes the fund and \(\omega\) reflects the weight given to current holdings vs. long‑term behaviour.

The result is a matrix \(B\) of size (number of factors) × (number of funds), which describes the lineup in factor space.

### 7.2 Deriving Correlations from Factor Exposures

To feed an optimiser, we need a reasonable covariance matrix for the funds. A common approach is:

- Obtain a factor covariance matrix \(\Sigma_f\) from the risk model.  
- Model fund return covariance as:
  \[
  \Sigma_{funds} = B^\top \Sigma_f B + D,
  \]
  where \(D\) is a diagonal matrix of idiosyncratic variances for each fund.

This yields a correlation structure that reflects shared factor exposures, rather than noisy fund‑to‑fund returns.

### 7.3 Identifying Redundancy and Gaps

With factor exposures in hand, it becomes clear where the lineup is:

- **Redundant**: multiple funds with very similar factor patterns (and hence high correlations).  
- **Incomplete**: missing important exposures such as EM equity, TIPS, real assets, or defensive equity.  
- **Unbalanced**: e.g., heavy tilts towards growth, credit, or a specific country.

Redundant funds can be down‑weighted or eliminated from optimisation. Gaps and imbalances can be addressed via lineup changes or, where impossible, via synthetic approximations.

### 7.4 Constructing Synthetic Exposures

If certain exposures are not available as standalone funds, style analysis can help approximate them through combinations of existing options. For example:

- EM exposure might be approximated using a global ex‑US equity fund plus an international small‑cap fund that historically behaves like EM.  
- Long‑duration exposure might be approximated using a core bond fund plus a smaller allocation to a long‑bond fund.

The optimiser can then work in factor space, using combinations of funds to target desired exposures as closely as possible.

### 7.5 Optimisation Frameworks

Once the factor representations and covariance matrix are in place, several optimisation frameworks are possible:

- **Mean–variance optimisation (MVO)** on the funds, with expected returns derived from factor views or capital market assumptions mapped through \(B\).  
- **Risk‑budgeting frameworks**, where the goal is to allocate risk (volatility or tracking error) across factors rather than across funds.  
- **Constraint‑rich optimisation**, where limits can be expressed at both the fund level (e.g., max 20% in any single fund) and the factor level (e.g., minimum 10% of risk from non‑U.S. equities).

In each case, style analysis ensures that the mathematical optimisation reflects the *economic* reality of the exposures being taken.

### 7.6 Ongoing Monitoring and Re‑Optimisation

Plan lineups and fund behaviour evolve over time:

- Funds may change benchmarks or managers.  
- Style drifts may accumulate.  
- New options may be added; old ones may be removed.

Style analysis enables ongoing monitoring:

- Periodic recalculation of factor exposures for each fund.  
- Updated covariance matrices and optimisation runs.  
- Detection of shifts that warrant changes in recommended portfolios or managed‑account strategies.

This closes the loop between **static plan design** and **dynamic portfolio management** within that plan.

---

(End of Sections 6–7)
