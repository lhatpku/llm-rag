# Deriving Asset Class Return and Risk Assumptions

## 1. Introduction

Robust capital market assumptions (CMAs) require a disciplined methodology to estimate future returns, volatilities, and correlations. This document explores various quantitative and fundamental strategies used by institutional investment teams to derive CMA inputs for long-term modeling.

---

## 2. Estimating Expected Returns

### 2.1 Historical Average

- Simple average of past returns (e.g., 10-, 20-, 30-year windows)
- **Pros**: Empirical basis, easy to calculate
- **Cons**: Backward-looking, may not reflect forward realities

### 2.2 Building Block Approach

A forward-looking model that sums components:

```math
\text{Expected Return} = \text{Yield} + \text{Earnings Growth} + \Delta \text{Valuation}
```

Example for U.S. Equity:
- Dividend Yield = 1.5%
- Real Earnings Growth = 1.5%
- Inflation = 2.0%
- Valuation Compression = –0.5%
- **Total Expected Return ≈ 4.5%**

### 2.3 Yield-Based Forecasting for Bonds

```math
\text{Bond Return} \approx \text{Yield to Maturity} - \Delta \text{Duration} \cdot \Delta \text{Rates}
```

Includes:
- Term premium
- Roll-down return
- Credit spread compensation

---

## 3. Estimating Volatility and Correlation

### 3.1 Sample Statistics

Annualized standard deviation and correlation based on historical monthly/quarterly returns.

### 3.2 Shrinkage Estimators

Blend sample covariance matrix with structured targets (e.g., identity or constant correlation matrix):

```math
\Sigma_{shrink} = \lambda T + (1 - \lambda) S
```

Where:
- \( S \) = sample covariance
- \( T \) = structured target
- \( \lambda \in [0,1] \) = shrinkage intensity

Improves stability in high-dimensional settings.

### 3.3 Regime-Switching Models

Model return distribution under multiple market states:
- Bull / Bear regimes
- High / low volatility periods

Often estimated via Hidden Markov Models or Bayesian filters.

---

## 4. Adjustments for Inflation and Currency

- Convert returns to real terms using expected inflation
- Hedge/unhedge foreign assets depending on currency strategy

---

## 5. Blending Multiple Sources

Best practice blends inputs from:
- Internal model forecasts
- Market-implied returns (e.g., equity risk premium, bond yields)
- Third-party sources: JP Morgan Long-Term CMA, Vanguard, BlackRock, Research Affiliates

Example:

```text
Final CMA Return = 40% Internal + 30% Market-Implied + 30% Peer CMAs
```

---

## 6. Review and Governance

- Recalibrate CMAs at least annually
- Document inputs and assumptions
- Apply consistency across related methodologies (e.g., simulation, optimization)

---

## 7. Conclusion

Effective CMA derivation requires a balance of data, judgment, and structural modeling. Combining historical context with forward expectations ensures a durable and defensible investment framework.

