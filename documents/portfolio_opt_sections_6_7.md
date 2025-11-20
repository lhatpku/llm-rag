# Portfolio Optimization Whitepaper — Sections 6–7

## 6. Portfolio Optimization in Qualified Accounts and Plan Lineups

Qualified retirement accounts (401(k), 403(b), IRAs, and similar vehicles) introduce additional structure and constraints into portfolio optimization:

- Investors typically choose from a **finite plan lineup** of mutual funds, CITs, and TDFs.  
- Tax treatment differs from taxable accounts (tax deferral, RMDs, contribution limits).  
- Default options such as TDFs or managed accounts (QDIA) play a central role.  
- Recordkeepers and plan sponsors impose operational rules about trading frequency and allowable vehicles.

Optimization in this environment is **menu‑constrained**:  
rather than allocating directly to asset classes, the engine must allocate to **funds**, each of which is a composite of underlying exposures.

---

### 6.1 From Asset Classes to Fund Menus

To apply MVO or risk‑based methods on a plan lineup:

1. **Define a set of canonical asset or factor exposures**  
   (e.g., U.S. large equity, U.S. small equity, international equity, EM, core bonds, long bonds, HY, TIPS, REITs).

2. **Use style analysis** (return-based and holdings-based) to map each fund into this factor space.  
   This yields a factor exposure vector for each fund.

3. **Construct a fund-level covariance matrix**  
   from the factor covariance matrix and the funds’ exposures.

4. **Apply optimization in fund space**  
   using the derived expected returns and risk metrics.

The result is an allocation over the **available plan funds** that approximates the desired risk–return trade‑off in factor space.

---

### 6.2 Model Portfolios and Risk-Based Models in DC Plans

Many DC platforms offer **model portfolios** or risk-based model suites (Conservative, Moderate, Aggressive). These are typically built through:

- an **offline optimization process** using CMAs and constraints relevant to the plan’s lineup,  
- periodic review and re‑estimation of CMAs and correlations,  
- translation of investor‑level inputs (age, risk tolerance, horizon) to one of the model portfolios.

The optimization engine described earlier provides the foundation for these model portfolios. Once the weights are determined, they can be:

- stored as strategic targets per risk band,  
- used by advice engines to generate personalised recommendations,  
- periodically re‑evaluated as CMAs and menus evolve.

---

### 6.3 TDF Series vs. Custom Optimized Portfolios

Within qualified accounts, participants may choose between:

- off‑the‑shelf TDF series,  
- custom model portfolios driven by optimization,  
- managed accounts that integrate optimization with individual data.

Optimization provides a way to:

- **compare** TDF risk–return characteristics to custom portfolios,  
- **design custom glidepaths** for large plans with unique demographics,  
- **overlay constraints** specific to the sponsor (e.g., company stock limits).

In advisory APIs, one can expose endpoints that:

- compute an optimal portfolio given plan menu, CMAs, and constraints,  
- or generate a glidepath of portfolios indexed by years to retirement.

---

### 6.4 Tax and Regulatory Considerations

While tax‑loss harvesting and capital gains management are central in taxable accounts, qualified accounts emphasize:

- **asset location decisions** across taxable vs. tax‑deferred vs. tax‑exempt buckets,  
- RMDs (required minimum distributions) at older ages,  
- contribution and maximum deferral limits,  
- plan‑specific restrictions (e.g., trading blackout periods, limits on company stock).

An integrated optimization framework should be able to:

- treat each account type as a “bucket” with different tax rules,  
- optimally spread asset classes across buckets to maximize **after‑tax** wealth,  
- respect qualified‑plan constraints and employer rules.

---

## 7. Putting It All Together: Implementation Blueprint

This final section provides a high‑level blueprint for implementing a production‑grade portfolio optimization engine suitable for integration into advice platforms, robo‑advisors, or internal tools.

---

### 7.1 Conceptual Architecture

A robust architecture typically includes:

1. **Data and Market Engine**
   - Ingest prices, yields, fundamentals, and macro data.  
   - Maintain security master and mapping to asset classes/factors.  
   - Estimate CMAs (\(\mu\), \(\Sigma\), factor data, scenarios).

2. **Portfolio Construction Engine**
   - Implement MVO, Black–Litterman, and risk-based optimizers.  
   - Encode constraints (long-only, group bounds, turnover, plan rules).  
   - Support menu‑constrained optimization for 401(k)/403(b) plans.  
   - Expose APIs for “optimize portfolio given inputs”.

3. **Style and Risk Analysis Module**
   - Perform return-based and holdings-based style analysis.  
   - Map funds to factor exposures and generate fund‑level risk metrics.  
   - Provide diagnostics on diversification, factor tilts, and risk contributions.

4. **Advice and Goal-Based Planning Layer**
   - Capture investor goals, risk preferences, time horizons.  
   - Translate goals into risk bands, spending paths, or success probability targets.  
   - Call the optimization engine with appropriate inputs and constraints.

5. **Execution and Monitoring**
   - Turn optimized weights into trades, respecting lot sizes and plan rules.  
   - Monitor drift vs. targets, risk changes, and tracking error.  
   - Trigger re‑optimization and rebalancing when conditions warrant.

---

### 7.2 Practical Design Choices

Some practical choices that materially improve robustness and usability:

- **Prefer stable building blocks** (broad indices, core funds) as the backbone of portfolios.  
- **Use Black–Litterman or similar Bayesian methods** to moderate expected return estimates.  
- **Apply shrinkage to covariance matrices** and validate correlations under stress.  
- **Avoid overly aggressive use of small alpha signals**; incorporate them as modest tilts.  
- **Impose sensible constraints** to prevent extreme allocations and ensure explainability.  
- **Test portfolios under multiple scenarios** (e.g., inflation shock, rate spike, equity crash).  
- **Maintain clear documentation** that links methodology to fiduciary and regulatory expectations.

---

### 7.3 Summary

Portfolio optimization, when implemented carefully, is a powerful engine for:

- constructing diversified portfolios aligned with investor objectives,  
- managing risk in a quantitative and transparent way,  
- delivering scalable, rules-based advice in both taxable and qualified accounts,  
- and supporting advanced use-cases such as custom glidepaths and menu‑constrained solutions.

However, optimization is **not a magic box**. Its quality depends critically on:

- the realism of the CMAs,  
- the appropriateness of constraints,  
- the robustness of estimation and risk models,  
- and the clarity with which its outputs are integrated into a broader advice process.

The frameworks presented in this whitepaper—mean–variance, Black–Litterman, risk‑based methods, and menu‑constrained optimization for qualified accounts—provide a practical foundation for building institutional‑grade portfolio construction capabilities into modern advisory systems.

---

(End of Sections 6–7)
