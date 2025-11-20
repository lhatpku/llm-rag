# Portfolio Optimization Whitepaper — Sections 1–3

## 1. Introduction and Role of Portfolio Optimization

Portfolio optimization is the quantitative process of deciding **how much to invest in each asset** (or fund) to achieve a desired balance between risk and return. At its core, the process is about **turning capital market assumptions and investor constraints into implementable portfolios**.

In practice, portfolio optimization must bridge three domains:

- **Capital market expectations**  
  Estimates of expected returns, volatilities, and correlations across asset classes or factors.

- **Investor objectives and constraints**  
  Risk tolerance, investment horizon, drawdown sensitivity, tax status, liquidity needs, regulatory or plan constraints.

- **Implementation realities**  
  Access to specific instruments (funds, ETFs, SMAs), transaction costs, taxes, trading frequency, and minimum-size rules.

This whitepaper focuses on “intermediate” quantitative toolkits used in institutional and high‑end advisory contexts, including:

- mean–variance optimization (MVO) and its practical variants,  
- robust approaches such as Bayesian adjustments and resampling,  
- Black–Litterman methodology for blending views with market equilibrium,  
- alternative risk-based techniques (minimum-variance, risk parity, equal risk contribution),  
- and specific considerations for **qualified retirement accounts** (e.g., 401(k), 403(b), IRAs) that invest through plan lineups and target-date funds.

The goal is not to present a purely academic treatment, but to offer a **practical blueprint** for building optimization engines that can be surfaced through APIs or advice platforms and integrated into a robo‑advising or advisory workflow.

---

## 1.1 Key Inputs: Capital Market Assumptions (CMAs)

Any optimization engine requires a view of the future. In practice, these views are summarised as **Capital Market Assumptions (CMAs)**:

- \(\mu\): vector of expected returns (e.g., long‑term annualized arithmetic or geometric means).  
- \(\Sigma\): covariance matrix (or correlation matrix + volatilities).  
- Optionally, additional structures such as:
  - tail risk measures (e.g., expected shortfall),  
  - factor loadings to macro drivers,  
  - regime-specific parameters (e.g., normal vs. stressed environment).

CMAs may be built from:

- historical data (appropriately adjusted),  
- valuation-based models (e.g., earnings yield, term premium),  
- macro forecasts,  
- or a blend of these.

For our purposes, we assume that for a set of \(N\) investable building blocks (asset classes, indices, or funds), we have:

- an \(N\)-dimensional expected return vector \(\mu\),  
- an \(N \times N\) covariance matrix \(\Sigma\).

These are the “raw materials” that feed into optimization.

---

## 1.2 Investor Objectives and the Efficient Frontier

In classic mean–variance theory (Markowitz), investors face a trade‑off between:

- **expected return**, and  
- **risk**, usually measured as standard deviation of returns.

The **efficient frontier** is the set of portfolios that offer the maximum expected return for a given level of risk (or, equivalently, the minimum risk for a given expected return). Formally, the set of efficient portfolios is obtained by solving:

\[
\begin{aligned}
\min_{w} \quad & w^\top \Sigma w \\
\text{s.t.} \quad & w^\top \mu = \mu^* \\
& \sum_{i=1}^N w_i = 1, \\
& w \in \mathcal{C},
\end{aligned}
\]

where:

- \(w\) is the vector of portfolio weights,  
- \(\mu^*\) is the target expected return,  
- \(\mathcal{C}\) encodes constraints (e.g., no short‑selling, long-only, max position sizes).

By varying \(\mu^*\), we trace out the efficient frontier. Many institutional asset allocation processes are built on this framework or its robust extensions.

---

## 1.3 Risk–Return Utility and the Tangency Portfolio

Rather than specifying \(\mu^*\), one can assign a **risk-aversion coefficient** \(\lambda > 0\) and maximize a quadratic utility:

\[
\max_{w} \quad U(w) = w^\top \mu - \frac{\lambda}{2} w^\top \Sigma w,
\]

subject to \(\sum_i w_i = 1\) and any additional constraints. The first term rewards expected return; the second penalises risk. A lower \(\lambda\) means the investor is more risk‑tolerant.

If we assume a risk‑free asset with return \(r_f\) is available and short‑selling is allowed, the **tangency portfolio** maximizes the Sharpe ratio:

\[
\max_w \quad \frac{w^\top (\mu - r_f \mathbf{1})}{\sqrt{w^\top \Sigma w}}.
\]

The tangency portfolio lies on the efficient frontier and defines the **Capital Market Line (CML)**, along which investors mix the risk‑free asset and the tangency portfolio according to risk tolerance.

---

## 1.4 Practical Limitations of Pure Mean–Variance Theory

Although MVO and the efficient frontier are elegant, they are fragile in practice:

1. **Parameter uncertainty**
   - Small errors in \(\mu\) can produce large changes in optimal weights (“error maximisation”).  
   - Estimation errors in \(\Sigma\) can distort correlations and risk contributions.

2. **Non‑normal returns and tail risk**
   - Real‑world returns have fat tails and skewness.  
   - Variance does not fully capture drawdown risk or sequence risk, especially critical for retirement planning.

3. **Implementation constraints**
   - Long-only requirements.  
   - Concentration limits (e.g., max 20% per asset class).  
   - Regulatory rules and plan‑level constraints.  
   - Minimum trade sizes and transaction costs.

4. **Behavioral considerations**
   - Participants may care more about drawdowns, funding ratios, or probability of meeting goals than about abstract variance.

Despite these limitations, **mean–variance-based engines remain the backbone** of many institutional and advisory optimizers, provided they are augmented with:

- robust estimation techniques,  
- explicit constraints,  
- scenario analysis,  
- and additional risk metrics.

The remainder of this whitepaper explores these extensions.

---

## 2. Mean–Variance Optimization (MVO) in Practice

This section formalises the MVO problem and discusses practical variants that make it suitable for real‑world implementation in advisory platforms and robo‑advisors.

---

### 2.1 The Basic Long-Only MVO Problem

For a universe of \(N\) assets, the simplest long-only MVO formulation is:

\[
\begin{aligned}
\min_{w} \quad & w^\top \Sigma w \\
\text{s.t.} \quad & w^\top \mu \geq \mu^*, \\
& \sum_{i=1}^N w_i = 1, \\
& w_i \ge 0, \quad i = 1,\dots,N.
\end{aligned}
\]

Alternatively, to target a specific risk level \(\sigma^*\), we can solve:

\[
\begin{aligned}
\max_{w} \quad & w^\top \mu \\
\text{s.t.} \quad & w^\top \Sigma w \le (\sigma^*)^2, \\
& \sum_{i=1}^N w_i = 1, \\
& w_i \ge 0.
\end{aligned}
\]

These are convex quadratic programs and can be solved efficiently with standard solvers.

In a robo‑advisory context, one often pre‑computes a **grid of efficient portfolios** of increasing risk and then maps each investor’s risk tolerance into one of these points (e.g., “Conservative,” “Moderate,” “Aggressive”).

---

### 2.2 Incorporating Practical Constraints

Realistic optimization requires adding constraints such as:

- **Box constraints**:  
  \(w_i^{\min} \le w_i \le w_i^{\max}\).  
  E.g., at least 10% in bonds, no more than 60% in equities.

- **Group constraints**:  
  If assets are grouped (e.g., by region, asset class, factor family), we may impose:  
  \[
  L_g \le \sum_{i \in g} w_i \le U_g,
  \]
  where \(g\) indexes groups.

- **Cardinality constraints** (limit number of non-zero holdings):  
  These are non‑convex (combinatorial) and typically approximated via heuristics; often avoided in daily retail optimization but relevant for custom SMAs.

- **Turnover constraints and penalties**:  
  Add a cost term to penalise deviations from current weights \(w^{\text{current}}\):
  \[
  \max_w \; w^\top \mu - \frac{\lambda}{2} w^\top \Sigma w - \gamma \sum_i |w_i - w_i^{\text{current}}|,
  \]
  where \(\gamma\) is a turnover‑penalty parameter.

Proper constraint design is critical: it balances mathematical optimality with **robustness, explainability, and implementability**.

---

### 2.3 Robustifying MVO: Shrinkage and Resampling

Because MVO is sensitive to \(\mu\) and \(\Sigma\) estimation error, practitioners use several techniques to make it more stable:

1. **Shrinkage of the covariance matrix**  
   Blend the sample covariance \(\hat\Sigma\) with a structured target (e.g., constant‑correlation or factor model):

   \[
   \Sigma^{\text{shrink}} = \delta T + (1 - \delta) \hat\Sigma, \quad 0 \le \delta \le 1.
   \]

2. **Bayesian / Black–Litterman adjustments to \(\mu\)**  
   Replace raw \(\mu\) with a combination of equilibrium returns and user views (covered in Section 4).

3. **Resampled efficient frontier**  
   - Draw many scenarios of \(\mu\) and \(\Sigma\) from their estimated distributions.  
   - For each scenario, compute the efficient frontier.  
   - Average the resulting weights across scenarios to obtain more stable allocations.

4. **Impose stronger constraints**  
   - Require minimum allocations to “core” assets (e.g., broad equity and bond indices).  
   - Limit the extent to which any single asset can dominate.

These methods help transform the theoretically optimal but fragile solutions of naive MVO into robust allocations suitable for real investors.

---

## 3. Beyond Classic MVO: Black–Litterman and View Integration

Classic MVO requires explicit expected returns \(\mu\), which are notoriously hard to estimate. The **Black–Litterman framework** provides a principled way to combine **market‑implied equilibrium returns** with **subjective views** in a Bayesian way, yielding more stable and interpretable inputs for optimization.

---

### 3.1 Market-Implied Equilibrium Returns

Under the CAPM intuition, the market portfolio (e.g., global market cap‑weighted portfolio) is mean–variance efficient. If we know:

- the global market‑cap weights \(w^{mkt}\),  
- the covariance matrix \(\Sigma\),  
- and the market’s overall risk aversion parameter \(\lambda\),

we can back out implied equilibrium excess returns:

\[
\pi = \lambda \Sigma w^{mkt}.
\]

Here, \(\pi\) is the vector of **equilibrium excess returns** (over cash), consistent with the assumption that the market portfolio is optimal for the representative investor.

---

### 3.2 Incorporating Investor Views

Suppose an investor (or research process) has **views** about certain assets or relative relationships, such as:

- Asset A will outperform asset B by 2% per year.  
- The EM equity index will have an excess return of 4% per year.  
- A particular sector will underperform the broad market.

We encode these views in a matrix \(P\) and a vector \(q\):

- Each row of \(P\) represents a linear combination of asset returns (e.g., +1 for A, −1 for B).  
- The corresponding element of \(q\) is the expected excess return for that combination.  
- We also specify a covariance matrix \(\Omega\) capturing **uncertainty** about each view.

Black–Litterman then combines \(\pi\) (the prior) and the views \((P, q, \Omega)\) to produce a **posterior** distribution for expected returns \(\mu^{BL}\):

\[
\mu^{BL} =
\left( (\tau \Sigma)^{-1} + P^\top \Omega^{-1} P \right)^{-1}
\left( (\tau \Sigma)^{-1} \pi + P^\top \Omega^{-1} q \right),
\]

where \(\tau\) is a scalar reflecting the confidence in the prior (typically a small number).

The Black–Litterman returns \(\mu^{BL}\):

- stay close to market‑implied returns when views are weak,  
- move toward the views where confidence is high,  
- avoid extreme or unintuitive allocations that arise from naive \(\mu\) estimation.

---

### 3.3 Using Black–Litterman in Advisory and Robo Contexts

In an advisory or robo‑advisory architecture:

- **Core CMAs** can be derived from a research team’s equilibrium model.  
- **Advisor inputs or AI‑driven views** (e.g., modest tilts to factors, regions, or sectors) can be encoded in \(P, q, \Omega\).  
- The resulting \(\mu^{BL}\) becomes the input to a standard MVO engine.

This offers a clean separation of responsibilities:

- A central research group controls the long‑term, diversified baseline.  
- Advisors or algorithms express **incremental, bounded views** without completely overriding the research CMAs.  
- Optimization translates the blended expectations into implementable model portfolios.

---

(End of Sections 1–3)
