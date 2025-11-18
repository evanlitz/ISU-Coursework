# King of the Beach Volleyball Tournament Analysis

Statistical analysis of player performance in a 2v2 beach volleyball tournament using linear regression models.

## Overview

This project analyzes match results from a "King of the Beach" volleyball tournament to estimate individual player strengths, predict win probabilities, and compare different modeling approaches. The analysis was completed as part of ISU STAT 461.

## Data

The dataset (`data/king_of_the_beach_volleyball.csv`) contains:
- 14 matches (42 total sets) from a best-of-3 tournament
- 8 players: Andy, Dan, Dave, German, Jarad, Mike, Perry, Stephen
- Each row represents one set with team compositions and scores (games to 21)

## Methodology

### Model 1: Margin of Victory
- Estimates player strength based on point differentials
- Design matrix: +1 for Team 1 players, -1 for Team 2 players
- Linear regression with no intercept (one player as baseline)
- Assumes margins follow a normal distribution

### Model 2: Offense-Defense Rating
- Separates player contributions into offensive and defensive components
- Models individual set scores rather than margins
- Combines scoring ability (offense) and opponent suppression (defense)

## Analysis Scripts

| Script | Purpose |
|--------|---------|
| `Q1-2Script.R` | Individual player strength estimates |
| `Q3Script.R` | Team strength and expected margins |
| `Q4Script.R` | Single set win probability |
| `Q5Script.R` | Best-of-3 match win probability |
| `Q6Script.R` | Head-to-head matchup predictions |
| `Q7-8Script.R` | Offense and defense ratings |
| `Q9Script.R` | Match probability using off-def model |
| `Q10Script.R` | Comprehensive margin-of-victory analysis |
| `Q11Script.R` | Model comparison and correlation |

## Requirements

- R (>= 3.6.0)
- tidyverse package

## Usage

```r
# Install dependencies
install.packages("tidyverse")

# Run individual analysis scripts
source("Q1-2Script.R")
source("Q3Script.R")
# etc.
```

## Key Outputs

- Individual player strength rankings
- Win probability predictions for specific matchups
- Offensive and defensive skill ratings
- Correlation analysis between different modeling approaches

## Project Structure

```
Volleyball/
├── README.md
├── data/
│   └── king_of_the_beach_volleyball.csv
├── Q1-2Script.R
├── Q3Script.R
├── Q4Script.R
├── Q5Script.R
├── Q6Script.R
├── Q7-8Script.R
├── Q9Script.R
├── Q10Script.R
└── Q11Script.R
```

## Course

STAT 461 - Iowa State University
