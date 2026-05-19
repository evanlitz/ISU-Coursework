# CS417 Assignment 4: Coverage Report Analysis

**Course**: CS417 – Software Testing, Iowa State University

## Overview

Analysis of JaCoCo HTML coverage reports for the `TriangleType` program. The annotated source highlights which lines and branches are covered, partially covered, or missed, connecting coverage gaps to the known fault in the implementation.

## Files

| File | Description |
|------|-------------|
| `index.html` | Coverage report index showing class-level coverage summary |
| `Triangle.java.html` | Annotated `TriangleType` source with line-by-line coverage highlighting |

## Key Observations

The `TriangleType` implementation contains a fault in the isosceles check:

```java
// Faulty (checks s1 == s3 twice, never checks s1 == s2):
if ((s1 == s3) || (s2 == s3) || (s1 == s3))

// Correct:
if ((s1 == s2) || (s2 == s3) || (s1 == s3))
```

The coverage report reveals missed branches on the isosceles condition — specifically the `s1 == s2` case is never taken because that branch is unreachable given the duplicate condition. This demonstrates how branch coverage gaps directly point to dead or faulty code.

## Takeaway

High line coverage does not guarantee fault detection. The faulty branch is executed (line is green), but the specific condition `s1 == s2` is never evaluated as true due to the fault, which only becomes visible through careful branch-level coverage inspection.
