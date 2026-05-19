# CS417 Assignment 3: Combinatorial Interaction Testing (CIT)

**Course**: CS417 – Software Testing, Iowa State University

## Overview

Applies **Combinatorial Interaction Testing** to two real-world systems: a Unix `sort`-like command and Firefox browser settings. TSL (Test Specification Language) models describe the parameter spaces, and a CIT tool generates minimal t-way covering arrays.

## Background

CIT reduces the number of test cases needed to cover all t-way interactions among parameters. For pairwise (t=2) testing, every pair of parameter values appears in at least one test case. This is particularly effective because the majority of real-world faults are triggered by interactions of 1–3 parameters.

## Q1 — Sort Command Testing

`Q1/sort.refined.tsl` specifies the parameter model for a sort utility:

| Parameter | Values |
|-----------|--------|
| `help` | on, off |
| `version` | on, off |
| `order` | numeric, alpha (default), random, reverse |
| `check` | yes, no |
| `unique` | yes, no |
| `file_contents` (env) | sorted alphabetically, sorted numerically, unsorted |
| `duplicates` (env) | yes, no |

`Q2/` contains CIT tool output files showing the generated test cases for 2-way and 3-way covering arrays applied to sort.

## Q3 — Firefox Configuration Testing

`Q3/firefox.tsl` models 9 Firefox preference parameters:

| Parameter | Values |
|-----------|--------|
| `default_search_engine` | Google, Bing, Amazon, DuckDuckGo, eBay, Wikipedia |
| `ctrltab_recent`, `autoscrolling`, `smooth_scrolling` | on, off |
| `newtab_links`, `switch_to_open_link`, `ask_before_closing_multiple_links`, `ask_before_quitting_xq` | on, off |
| `updates` | automatically install, ask to install |

## Q4 — Firefox Input Testing

`Q4/firefox.input.txt` is the raw CIT tool input file encoding the Firefox model as factor counts. `firefoxinput.out` is the resulting covering array.

## CIT Tool

The tool in `CIT_Tool/` accepts input in the format:
```
t k v1 n1 v2 n2 ...
```
Where `t` = interaction strength, `k` = number of factors, and each `vi ni` pair gives the number of values and repetition count for a group of parameters.

## Tools

- **CIT Tool** — pairwise/t-way covering array generator
- **TSL** (Test Specification Language) — declarative parameter modeling language
