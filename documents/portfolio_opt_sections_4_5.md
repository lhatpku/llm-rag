# Portfolio Optimization Whitepaper — Sections 4–5

## 4. Risk-Based and Alternative Optimization Approaches

While mean–variance and Black–Litterman frameworks focus explicitly on expected returns, many practitioners favour approaches that put **risk at the centre of the construction problem**, either because return forecasts are highly uncertain or because the objective is primarily risk control.

Common risk-based approaches include:

- **Minimum-variance portfolios**,  
- **Risk parity / equal risk contribution (ERC)**,  
- **Volatility targeting**,  
- **Factor risk budgeting**.

These methods often produce more stable allocations that are easier to explain and maintain through time.

---

### 4.1 Minimum-Variance Portfolios

The **minimum-variance (min‑var) portfolio** is the portfolio with the lowest possible variance among all fully invested portfolios that satisfy relevant constraints. It ignores expected returns entirely and solves:

\[
\begin{aligned}
\min_{w} \quad & w^\top \Sigma w \\
\text{s.t.} \quad & \sum_i w_i = 1, \\
& w_i \ge 0, \; \text{and other constraints.}
\end{aligned}
\]

Min‑var portfolios tend to:

- allocate more to lower‑volatility assets,  
- diversify away idiosyncratic risk,  
- sometimes appear “defensive” in equity space (tilting toward low‑vol and quality).

They are particularly attractive when **return forecasts are unreliable** but risk estimates are more robust.

In practice, min‑var often serves as:

- a **starting point** for constructing conservative or capital‑preservation portfolios,  
- a **component** in more complex strategies (e.g., mixing min‑var equity with traditional beta).

---

### 4.2 Risk Parity and Equal Risk Contribution (ERC)

**Risk parity** and **equal risk contribution** strategies allocate capital so that each asset (or asset class) contributes an equal share of total portfolio risk, rather than equal weight in capital.

For a portfolio with weights \(w\) and covariance \(\Sigma\):

- The total portfolio variance is \(\sigma_p^2 = w^\top \Sigma w\).  
- The **marginal contribution to risk** (MRC) of asset \(i\) is:
  \[
  \text{MRC}_i = \frac{\partial \sigma_p}{\partial w_i}
  = \frac{(\Sigma w)_i}{\sigma_p}.
  \]
- The **total risk contribution** (TRC) of asset \(i\) is:
  \[
  \text{TRC}_i = w_i \cdot \text{MRC}_i
  = w_i \frac{(\Sigma w)_i}{\sigma_p}.
  \]

Equal risk contribution aims to enforce:

\[
\text{TRC}_1 = \text{TRC}_2 = \dots = \text{TRC}_N.
\]

This is a non-linear optimization problem, usually solved by iterative numerical methods.

**Intuition:**

- Assets with higher volatility or stronger correlations receive lower weights so that their contribution to total risk is comparable to that of other assets.  
- When applied to broad asset classes (e.g., equity, bonds, commodities), risk parity often results in **leveraged balanced strategies** (if leverage is allowed), heavily weighting lower‑volatility assets like bonds.

---

### 4.3 Factor Risk Budgeting

Instead of assets, one can perform equal risk contribution or risk budgeting at the **factor level**:

- Use a factor model to break down portfolio variance into factor components (e.g., equity beta, rates, credit, inflation, value, momentum).  
- Allocate risk budgets to each factor (e.g., 40% to equity beta, 30% to rates, 20% to credit, 10% to alternatives).  
- Solve for asset weights that achieve these factor risk contributions.

This is especially relevant in multi‑asset portfolios where plan sponsors want **explicit control over macro and style factor risks**.

---

### 4.4 Volatility Targeting

Another alternative is to **target a specific volatility level** over time:

- Choose a target volatility \(\sigma^*\).  
- Estimate current or forward-looking volatility of the portfolio \(\hat\sigma_p\).  
- Scale risky assets (and/or cash position) to keep realised volatility near \(\sigma^*\).

Formally, if \(w^{\text{base}}\) is a base allocation, the scaled allocation may be:

\[
w^{\text{scaled}} = \min\left( L_{\max}, \frac{\sigma^*}{\hat\sigma_p} \right) w^{\text{base}},
\]

where \(L_{\max}\) is a leverage cap. This technique is common in risk‑controlled equity, managed futures, and absolute‑return strategies.

---

## 5. Constraints and Real-World Portfolio Construction

Regardless of whether one uses MVO, Black–Litterman, or risk‑based techniques, **real‑world portfolio construction is constraint‑driven**. The quality of the output is often determined more by constraint design than by the specific optimization algorithm.

---

### 5.1 Long-Only and Concentration Limits

Most advisory and retirement portfolios are **long‑only**. Enforcing \(w_i \ge 0\) is straightforward but can make some theoretical optima unattainable. Additionally, to avoid concentration risk, one imposes:

- maximum position sizes (e.g., \(w_i \le 20\%\)),  
- maximum exposure to certain sectors, regions, or asset classes.

These constraints can be encoded as linear inequalities and combined with the quadratic risk term.

---

### 5.2 Regulatory and Plan Constraints

Qualified accounts and institutional portfolios face additional rules:

- **ERISA and QDIA guidelines**,  
- investment policy statements (IPS),  
- restrictions on illiquid or complex instruments,  
- issuer concentration limits.

Optimization engines must be designed to **honour these rules by construction**, not as afterthoughts.

---

### 5.3 Turnover and Transaction Costs

Every rebalance incurs:

- explicit trading costs (bid–ask spreads, commissions),  
- implicit costs (market impact),  
- potential tax consequences (less relevant in tax‑deferred accounts but still important for after‑tax wealth).

A robust implementation includes turnover in the objective, for example:

\[
\max_w \quad w^\top \mu - \frac{\lambda}{2} w^\top \Sigma w
- \gamma \sum_i |w_i - w_i^{\text{current}}|,
\]

or constrains turnover directly:

\[
\sum_i |w_i - w_i^{\text{current}}| \le T_{\max}.
\]

Where \(T_{\max}\) is a turnover budget per period.

---

### 5.4 Multiple Objectives and Goal-Based Framing

In wealth and retirement planning, investors often have **multi‑dimensional objectives**, such as:

- reaching a target wealth or income level at retirement,  
- avoiding large drawdowns,  
- maintaining a certain funding ratio relative to liabilities.

While mean–variance optimization operates in risk–return space, it can be embedded within a broader **goal‑based planning framework**, where:

- CMAs and optimization produce candidate portfolio paths,  
- Monte Carlo simulations estimate distribution of outcomes,  
- decisions are made based on success probabilities and shortfall risk.

In a robo‑advisory or advice API, the optimization layer is typically one component in a chain:  
**goals → capital market engine → optimizer → trading & monitoring.**

---

(End of Sections 4–5)
