# Capital Market Assumptions in Portfolio Optimization and Simulation

## 1. Introduction

Capital Market Assumptions (CMAs) are a key input to portfolio construction engines. They define the long-term statistical properties of asset class returns and provide the foundation for optimization models and stochastic simulations. This whitepaper outlines the role of CMAs in portfolio design, advice systems, and Monte Carlo forecasting.

---

## 2. Inputs to Optimization

CMAs feed into the following inputs:

- **Expected Return Vector (\( \mu \))**
- **Covariance Matrix (\( \Sigma \))**
- **Constraints**: Allocation bounds, turnover, asset availability
- **Investor Preferences**: Risk tolerance, glidepath profile, liquidity needs

---

## 3. Optimization Frameworks

### 3.1 Mean-Variance Optimization (MVO)

Classic framework minimizing variance for a given level of expected return:

```math
\min_w \quad w^T \Sigma w \quad \text{s.t.} \quad w^T \mu \geq r_{target}, \quad \sum w = 1, \quad w \geq 0
```

- Sensitive to estimation error in \( \mu \)
- Can produce concentrated portfolios

### 3.2 Black-Litterman Model

Combines market equilibrium with subjective views:

```math
\mu_{BL} = \left[(\tau \Sigma)^{-1} + P^T \Omega^{-1} P \right]^{-1} \left[ (\tau \Sigma)^{-1} \Pi + P^T \Omega^{-1} Q \right]
```

Where:
- \( \Pi \): implied market returns
- \( P, Q, \Omega \): views, expected outcomes, and uncertainty

### 3.3 Risk Parity

Allocates capital such that each asset contributes equally to total portfolio risk:

```math
\frac{w_i \cdot \sigma_i}{\sum w_j \cdot \sigma_j} = c
```

- CMA needed to estimate \( \sigma_i \)
- Used for diversification in low-conviction environments

---

## 4. Monte Carlo Simulation

CMAs define the return distribution for pathwise simulations.

### 4.1 Lognormal Model

Simulate returns as:

```math
R_t = \exp\left(\mu - \frac{\sigma^2}{2} + \sigma Z_t\right)
```

- \( \mu \), \( \sigma \) from CMA
- \( Z_t \sim N(0,1) \)
- Captures compounding and asymmetric risk

### 4.2 Correlated Asset Classes

Use Cholesky decomposition of \( \Sigma \):

```math
L = \text{chol}(\Sigma), \quad R_t = \mu + L Z_t
```

- Maintains inter-asset relationships
- Enables coherent portfolio-level risk modeling

---

## 5. Glidepath Construction

CMAs used to:
- Evaluate risk/return tradeoffs at each life stage
- Design equity-to-fixed income ratio over time
- Estimate downside risk at retirement (e.g., funded ratio, income replacement rate)

---

## 6. Advice and Financial Planning Integration

- Translate CMA-driven outcomes into user-facing advice (e.g., "80% chance of not running out of money")
- Align with user preferences and account types (tax-aware withdrawal simulation)
- Allow scenario overlays: inflation spike, equity crash, rate hike

---

## 7. Calibration by Profile

Tailor CMA scenarios based on:
- **Conservative clients**: Lower expected return, narrower distribution
- **Aggressive clients**: Higher volatility, more upside tails
- **Short horizon goals**: Emphasize capital preservation
- **Long horizon goals**: Focus on growth and inflation protection

---

## 8. Limitations and Governance

- Models are only as good as their assumptions
- Forecast error grows over time
- Regular review with investment and quant teams required

---

## 9. Conclusion

CMAs are not just planning artifacts—they are the backbone of personalized portfolio design and forward-looking advice. Their thoughtful application in optimization and simulation unlocks tailored, probabilistic guidance that meets investors where they are.

