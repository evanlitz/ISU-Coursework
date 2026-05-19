# CS417 Final Project: LLM-Based Test Generation

**Course**: CS417 – Software Testing, Iowa State University  
**Team**: Evan Litzer, John Hartnett, Daniel Hargrave, Nolan Hoenert

## Overview

Explores **LLM-based automated test generation** using the TestPilot framework and the OpenAI API. The same two programs used throughout the course (`PrimeNumberFinder` and `TriangleType`) are ported to JavaScript, and multiple rounds of LLM-generated test suites are produced and compared against each other and against manually written tests.

## Programs Under Test

Both programs contain the same seeded faults studied in Assignments 1–4:

**`PrimeNumberFinder.js`**
- `computeSumOfPrimes()` — incorrect single-element handling
- `isPrime()` — incorrect result for certain inputs
- `findPrimes()` — off-by-one on upper bound

**`TriangleType.js`**
- Isosceles check: `(s1 === s3) || (s2 === s3) || (s1 === s3)` — `s1 === s2` is never tested

## Approach

TestPilot sends function signatures and docstrings to an LLM (GPT-3.5-turbo-instruct) which generates Mocha test cases. Multiple generation runs produce independent test suites:

| Directory | Description |
|-----------|-------------|
| `test-n306VJ/` | First LLM-generated test suite (~150+ test files) |
| `test-SKLFR8/` | Second generation run |
| `test-vDxFze/` | Third generation run |

Each generated suite is run against the faulty implementations and coverage is measured with **nyc** (Istanbul) to evaluate how well the LLM-generated tests detect the seeded faults.

## Project Structure

```
CS417-LLMTesting/
├── PrimeNumberFinder.js    # Faulty JavaScript implementation
├── TriangleType.js         # Faulty JavaScript triangle classifier
├── Triangle.js             # Triangle type enum
├── index.js                # Module exports
├── generateTests.ts        # TypeScript driver for TestPilot
├── testpilot.config.json   # LLM endpoint and generation config
├── .env.example            # OpenAI API key template
├── package.json            # Dependencies: mocha, nyc
├── src/                    # Original Java reference implementations
└── testpilot-main/         # TestPilot framework source
```

## Setup

```bash
cd CS417-LLMTesting
npm install

# Configure OpenAI API key
cp .env.example .env
# Add your API key to .env

# Run a generated test suite
npx mocha test-n306VJ/

# Run with coverage
npx nyc mocha test-n306VJ/
```

## Dependencies

- **Node.js** / **TypeScript**
- **Mocha** `^11.7.5` — test runner
- **nyc** `^17.1.0` — Istanbul-based coverage tool
- **TestPilot** — LLM test generation framework
- **OpenAI API** — GPT-3.5-turbo-instruct (completion endpoint)
