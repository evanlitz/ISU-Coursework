# CS417 Assignment 1: Code Coverage with JaCoCo

**Course**: CS417 – Software Testing, Iowa State University

## Overview

Introduction to code coverage measurement using **JaCoCo** (Java Code Coverage Library). Two programs with known faults are instrumented and their coverage reports are analyzed to understand what the tests exercise and what they miss.

## Programs Under Test

### PrimeNumberFinder
Finds all primes in a range using the 6k±1 optimization. Methods:
- `findPrimes(int lower, int upper)` — returns list of primes in range
- `computeSumOfPrimes(List<Integer>)` — sums a list of primes
- `isPrime(int)` — primality test

### TriangleType
Classifies a triangle given three side lengths as `SCALENE`, `ISOSCELES`, `EQUILATERAL`, or `INVALID`. Contains an intentionally introduced fault: the isosceles check uses `(s1 == s3)` twice instead of `(s1 == s2)`, causing it to miss the case where sides 1 and 2 are equal.

## Coverage Reports

| Report | Description |
|--------|-------------|
| `initial_report.html` | Coverage achieved by the initial test suite |
| `second_report.html` | Coverage after adding tests targeting uncovered branches |

Reports show line, branch, and instruction coverage percentages. Gaps in branch coverage for `TriangleType` reveal that the fault is difficult to detect without deliberately targeting the `s1 == s2` equivalence class.

## Tools

- **JaCoCo 0.8.12** — bytecode instrumentation agent; generates HTML/XML/CSV coverage reports
- **Maven** — build and test execution
- **JUnit** — test framework
