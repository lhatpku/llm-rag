# Yield Curve Forecasting and Nelson-Siegel Models

## 1. Introduction

Accurate modeling of the yield curve is essential for forecasting returns on fixed income assets and for calibrating capital market assumptions (CMAs) in bond-heavy portfolios. The Nelson-Siegel (NS) and Nelson-Siegel-Svensson (NSS) models are widely used for fitting and forecasting term structures of interest rates.

---

## 2. Yield Curve Structure and Components

The yield curve reflects the term structure of interest rates across maturities. It embeds:

- **Level**: Long-term interest rate expectations
- **Slope**: Difference between short and long-term rates
- **Curvature**: Hump or dip in mid-term maturities

---

## 3. Nelson-Siegel Model

### 3.1 Functional Form

```math
y(\tau) = \beta_0 + \beta_1 \left( \frac{1 - e^{-\lambda \tau}}{\lambda \tau} \right) + \beta_2 \left( \frac{1 - e^{-\lambda \tau}}{\lambda \tau} - e^{-\lambda \tau} \right)
```

Where:
- \( y(\tau) \): Yield at maturity \( \tau \)
- \( \beta_0 \): Long-term rate (level)
- \( \beta_1 \): Short-term slope
- \( \beta_2 \): Medium-term curvature
- \( \lambda \): Decay factor determining curve shape

---

## 4. Nelson-Siegel-Svensson (NSS) Extension

Adds a fourth term to capture more flexible curvature:

```math
y(\tau) = \beta_0 + \beta_1 A(\tau) + \beta_2 B(\tau) + \beta_3 C(\tau)
```

Where:
- \( C(\tau) = \left( \frac{\tau}{\lambda_2} \right) e^{-\tau / \lambda_2} \)

- Provides better fit for longer-term yields
- Useful in retirement glidepaths and bond laddering strategies

---

## 5. Estimation Techniques

### 5.1 Cross-Sectional Fitting

- Calibrate model on observed Treasury yields
- Solve for \( \beta \) coefficients using least squares

### 5.2 Time Series Forecasting of NS Parameters

Use VAR (Vector Autoregression) or Kalman filters to model time series evolution of:
- \( \beta_0, \beta_1, \beta_2, \lambda \)

Can produce multi-step forward rate forecasts, enabling:
- Projected return distribution of bond indices
- Horizon-based risk modeling

---

## 6. Deriving Bond Asset Class Returns

Map forecasted yield curve to expected return using duration and convexity formulas:

```math
R \approx YTM - \text{Duration} \cdot \Delta Y + \frac{1}{2} \cdot \text{Convexity} \cdot (\Delta Y)^2
```

Can be applied to:
- U.S. Treasuries
- IG Corporate Bonds
- Global bonds with currency overlay

---

## 7. Use in Capital Market Assumptions

- Build bond return forecasts from forecasted NS yield curve
- Improve consistency between macroeconomic assumptions and asset return inputs
- Enable bond risk decomposition: rate risk vs credit vs curve risk

---

## 8. References and Industrial Use

Widely used by:
- BlackRock’s Aladdin model
- PIMCO duration modeling
- ECB, BIS, and Fed yield curve forecasts

Academic origin: Nelson & Siegel (1987), Diebold & Li (2006), Diebold & Rudebusch (2013)

---

## 9. Conclusion

Nelson-Siegel models offer a robust foundation for forecasting the term structure of interest rates. Their integration into CMA frameworks enhances the realism and coherence of bond return expectations in portfolio construction and financial planning.

