# CS474 HW3: Support Vector Machines — Theory

**Course**: CS474 – Introduction to Machine Learning, Iowa State University

## Overview

Written assignment covering the mathematical theory of hard-margin SVMs: the dual formulation, KKT conditions, and kernel validity.

## Problems

### Q1 – SVM Dual Problem (20 pts)
Sets up and solves the dual problem for a toy 3-point dataset `{([0,0],-1), ([2,2],-1), ([2,0],+1)}`. Steps include:
- Augmenting each point with a bias coordinate
- Computing the kernel matrix `K` and label-weighted matrix `Q = yᵢyⱼKᵢⱼ`
- Solving `Qα = 1` via row reduction to find optimal Lagrange multipliers `α* = (1.5, 0.5, 1.0)`
- Recovering the primal weight vector `w* = [-1, 1, -1]`

### Q2 – KKT Converse is False (20 pts)
Proves that the converse of the KKT complementary slackness condition does not hold: a point can lie on the SVM margin (`yᵢ(wᵀxᵢ) = 1`) while having `αᵢ = 0`. Demonstrated via toy dataset `{([0,0],+1), ([1,0],+1), ([0,1],-1)}` where all three points are on the boundary yet `α₂ = 0` for the second point.

### Q3 – Invalid Kernel Function
Proves that `K(xᵢ, xⱼ) = -xᵢᵀxⱼ` is **not** a valid SVM kernel by constructing a 2-point dataset for which the resulting Gram matrix `G = diag(-1, -1)` is not positive semi-definite (`cᵀGc = -1 < 0`).
