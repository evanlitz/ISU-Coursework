# NFL Team Strength Estimation and Game Prediction

A statistical modeling project analyzing NFL game outcomes to estimate team strengths and predict game results using the 2024 NFL season data.

## Overview

This project applies linear regression and matrix-based statistical methods to:
- Estimate relative team strengths from game outcomes
- Quantify home-field advantage effects
- Predict game outcomes probabilistically
- Rank all 32 NFL teams by performance

## Project Structure

```
Project 1/
├── nfl.csv          # NFL game data (1966-2025)
├── NFL_P1.r         # Count unique teams in 2024
├── NFL_P2.r         # Count total regular season games
├── NFL_P3.r         # Calculate Vikings wins
├── NFL_P4.r         # Calculate Vikings losses
├── NFL_P5.r         # Linear model with lm()
├── NFL_P6.r         # Manual design matrix & home-field advantage
├── NFL_P7.r         # Team strength rankings
├── NFL_P8.r         # Constrained estimation (sum = 0)
├── NFL_P9.r         # Visualization of team strengths
├── NFL_P10.r        # Matchup prediction setup
├── NFL_P11.r        # Win probability (home game)
├── NFL_P12.r        # Win probability (away game)
└── README.md
```

## Data

The dataset (`nfl.csv`) contains 14,087 games spanning from 1966-2025 with 17 variables:

- **Game Info**: date, season, week, playoff indicator
- **Teams**: home team, away team
- **Scores**: home score, away score
- **Betting**: favorite, spread, over/under
- **Venue**: stadium, neutral site indicator
- **Weather**: temperature, wind, humidity, conditions

### 2024 Season Focus
- 32 NFL teams
- 272 regular season games (18 weeks)
- 5 playoff games through Super Bowl LIX

## Methodology

### 1. Team Strength Estimation

The core model estimates team strengths from margin of victory:

```
Margin of Victory = Home Team Strength - Away Team Strength + Home Field Advantage + Error
```

Two approaches are implemented:
- **R's `lm()` function**: Automatic factor handling and coefficient estimation
- **Manual matrix construction**: Design matrix with QR decomposition for deeper understanding

### 2. Model Identifiability

To ensure unique solutions, the project implements a sum-to-zero constraint:
```
sum(team_strengths) = 0
```

This makes team strengths interpretable as deviations from average team performance.

### 3. Win Probability Calculation

Game outcomes are predicted using the normal distribution:
```
P(Team A Wins) = P(Margin of Victory > 0)
                = 1 - Φ(-expected_margin / σ)
```

Where:
- Expected margin = Team A strength - Team B strength ± home field advantage
- σ = residual standard error from model fit

## Key Results

The analysis produces:
- **Team Rankings**: All 32 teams ranked by estimated strength
- **Home-Field Advantage**: Quantified point advantage for home teams
- **Win Probabilities**: Specific matchup predictions (e.g., Vikings vs Bears)
- **Model Diagnostics**: Residual standard error for prediction uncertainty

## Requirements

### R Packages
```r
install.packages("dplyr")
install.packages("ggplot2")
```

### Running the Analysis
Execute scripts sequentially:
```r
source("NFL_P1.r")  # Start with data exploration
source("NFL_P2.r")
# ... continue through NFL_P12.r
```

## Statistical Concepts

- **Linear Regression**: Estimating parameters from observed data
- **Design Matrices**: Binary encoding of categorical variables
- **QR Decomposition**: Numerically stable solution method
- **Constrained Optimization**: Ensuring model identifiability
- **Probability Forecasting**: Converting estimates to win probabilities
- **Residual Analysis**: Quantifying prediction uncertainty

## Example Output

From the team strength estimation:
- Teams with positive strength are above average
- Teams with negative strength are below average
- Home-field advantage typically ranges from 2-3 points

## Course Information

**STAT 461** - Statistical Modeling
Iowa State University

## License

Academic project for educational purposes.
