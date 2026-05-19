# CS474 HW1: Perceptron & Logistic Regression Theory

**Course**: CS474 – Introduction to Machine Learning, Iowa State University

## Overview

Written assignment covering the mathematical foundations of linear classifiers: the perceptron, logistic regression, and the softmax function.

## Problems

### Q1 – Perceptron Decision Boundary (10 pts)
Derives the decision boundary of a 2D perceptron `h(x) = sign(wᵀx)`. Shows that the boundary `wᵀx = 0` reduces to a line `x₂ = ax₁ + b` where `a = -w₁/w₂` and `b = -w₀/w₂`. Includes plotted decision boundaries for `w = [1,2,3]ᵀ` and `w = -[1,2,3]ᵀ` with labeled positive/negative regions.

### Q2 – Logistic Regression
- **2A**: Derives the gradient of the logistic regression cross-entropy loss `E(w) = -1/N Σ yₙxₙ / (1 + exp(yₙwᵀxₙ))` using chain rule.
- **2B**: Proves the decision boundary is linear by showing `σ(wᵀx) = 0.5 ⟺ wᵀx = 0`.
- **2C**: Finds the boundary when the threshold is 0.9 — shows it occurs at `wᵀx = ln9`, still a linear boundary.
- **2D**: Explains that any invertible monotone function preserves linearity of the decision boundary.

### Q3 – Matrix Outer Product Identity
Using standard basis vectors, proves that `XY = Σᵢ xᵢyᵢᵀ` where Y is formed by stacking label vectors as rows.

### Q4 – Softmax Reduces to Sigmoid (C=2)
Shows that for C=2 classes, `softmax(y₁) = σ(y₁ - y₂)` and `softmax(y₂) = 1 - σ(y₁ - y₂)`, recovering the binary sigmoid.
