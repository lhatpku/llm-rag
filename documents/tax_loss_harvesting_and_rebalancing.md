# Tax-Loss Harvesting and Tax-Aware Rebalancing

## 1. Overview

Tax-loss harvesting (TLH) and tax-aware rebalancing are core strategies in tax-efficient investing. TLH seeks to realize capital losses to offset capital gains or ordinary income (up to $3,000/year), while rebalancing aims to maintain portfolio alignment with target allocations in a way that minimizes tax drag.

---

## 2. Mechanics of Tax-Loss Harvesting

### 2.1 Loss Realization Conditions

A loss can be harvested when:
- The current market value of a security is below its cost basis
- The position is not within the wash-sale window
- There is sufficient available capital gains or room for carryforward

**Realized Loss = Cost Basis – Sale Price**

### 2.2 Wash Sale Rule

If a “substantially identical” security is repurchased within ±30 days of sale, the loss is disallowed and added to the new basis.

### 2.3 TLH Opportunity Scanning

A TLH system typically:
- Scans all tax lots daily
- Computes unrealized loss thresholds
- Filters positions with high tracking error if harvested

---

## 3. TLH Replacement Strategy

### 3.1 ETF Substitution

To avoid wash sales:
- Sell ETF A and replace with ETF B from a different issuer with similar exposure
- Use correlation analysis to identify low tracking error replacements

### 3.2 Replacement ETF Screening

```math
\text{TE}_{i,j} = \sqrt{\sum_{t=1}^{T} (r_{i,t} - r_{j,t})^2}
```

Where:
- \( r_{i,t} \): Return of ETF i at time t
- \( r_{j,t} \): Return of ETF j at time t

---

## 4. Tax-Aware Rebalancing Framework

### 4.1 Optimization Objective

Minimize deviation from target while limiting realized capital gains.

```math
\min_{w} \quad \| w - w^* \|^2 + \lambda \cdot \text{Gains}(w)
```

Where:
- \( w \): New weights
- \( w^* \): Target weights
- \( \lambda \): Tax-sensitivity parameter
- \( \text{Gains}(w) \): Total realized gains from trade

### 4.2 Rebalancing Thresholds

Set thresholds to trigger rebalance only if:
- Drift > 5%
- TLH opportunities exceed tax alpha threshold

---

## 5. Interaction of TLH and Rebalancing

- TLH generates cash which can be reinvested toward drifted positions
- TLH activity can trigger rebalance indirectly
- Rebalancing trades may open new TLH opportunities

---

## 6. Annual TLH Yield and Tax Alpha

Tax alpha refers to the after-tax performance boost due to harvesting.

**Tax Alpha Estimate:**

```math
\text{Tax Alpha} \approx \theta \cdot L \cdot R
```

Where:
- \( \theta \): Tax rate
- \( L \): Annual harvested losses
- \( R \): Return deferral rate (e.g., 5-7%)

Typical tax alpha is 1%–2% annually for actively harvested portfolios.

---

## 7. Conclusion

A sophisticated TLH and rebalancing engine enables long-term tax alpha by combining intelligent loss harvesting, optimized replacement selection, and drift-aware portfolio rebalancing—all tuned to minimize realized taxes without sacrificing strategic asset allocation.

