# Tax Lot Optimization in Tax-Aware Portfolio Management

## 1. Introduction

In taxable accounts, the selection of which tax lot to sell has a direct impact on realized capital gains and the investor’s tax liability. This document details tax lot selection strategies, optimization methods, and multi-account coordination for maximum tax deferral and after-tax return.

---

## 2. Tax Lot Basics

Each purchase of a security creates a unique **tax lot**, characterized by:

- **Acquisition Date**
- **Cost Basis**
- **Quantity**
- **Holding Period (Short/Long)**

---

## 3. Lot Selection Methods

### 3.1 FIFO (First In, First Out)

Sells the oldest tax lots first.

- Pros: Simple, default for many custodians
- Cons: Tends to realize larger gains due to lower cost basis

### 3.2 LIFO (Last In, First Out)

Sells the most recent purchases first.

- Can delay realizing large gains
- Not widely supported for tax reporting

### 3.3 HIFO (Highest In, First Out)

Sells the lots with the highest cost basis first.

- Minimizes realized capital gains
- Popular for TLH

### 3.4 MinTax Algorithm

Generalized version of HIFO that also considers:

- Short vs. long-term rates
- Future capital gain expectations
- Tax bracket phase-outs

---

## 4. Mathematical Formulation

### 4.1 Objective Function

```math
\min_{x} \sum_{i=1}^{N} x_i \cdot G_i \cdot T_i
```

Where:
- \( x_i \): Fraction of lot i to sell  
- \( G_i \): Realized gain from lot i  
- \( T_i \): Marginal tax rate on lot i (depends on short/long status)

### 4.2 Constraints

- \( \sum x_i \cdot q_i = Q_{target} \): sell target quantity
- \( 0 \leq x_i \leq 1 \)

This is a linear program solvable with simplex or greedy heuristics.

---

## 5. Multi-Account Coordination

In a household setting, optimal lot selection must span across:

- Taxable brokerage accounts
- Spousal accounts
- Entity-owned portfolios (trusts, 529s)

### 5.1 Wash Sale Cross-Account

All accounts under common control must be scanned to avoid triggering wash sales.

### 5.2 Deferred Gain Budgeting

Model each lot’s tax liability vs. deferral benefit:

```math
\text{Deferral Value}_i = G_i \cdot T_i \cdot (1 - D_i)
```

Where \( D_i \) is the discount factor for deferring the gain (e.g., 0.85 for 3 years).

---

## 6. Gain Budgeting for Rebalancing

Rather than minimizing tax outright, investors may allocate a **realized gain budget** for strategic rebalancing.

Example:

- Allow $2,500 in long-term gains this quarter
- Select trades to maximize tracking error reduction within that budget

```math
\max_{x} \quad \text{Tracking Error Reduction}(x) \quad \text{s.t.} \quad \sum x_i G_i T_i \leq B
```

---

## 7. Conclusion

Tax-lot optimization is a critical component of tax-efficient investing, requiring granular lot-level data, flexible execution tools, and cross-account coordination. Advanced lot selection models like MinTax and gain-budgeting frameworks provide the foundation for maximizing after-tax returns over time.

