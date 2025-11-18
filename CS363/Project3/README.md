# Project 3 - MongoDB COVID-19 Literature Analysis

CS 363 - Introduction to Database Management Systems

## Overview

This project demonstrates MongoDB database operations for analyzing COVID-19 scientific literature. The dataset contains 1,000 documents from the LitCovid database in BioC JSON format.

## Features

- MongoDB connection and collection management
- JSON data import and bulk insertion
- Document counting and field inspection
- Aggregation pipelines for journal and author analytics
- Text indexing and full-text search queries
- Phrase matching and boolean text search operations

## Requirements

- Python 3.x
- MongoDB (local instance on port 27017)
- PyMongo library

## Key Queries Implemented

1. **Document Statistics** - Count total documents in corpus
2. **Journal Analytics** - Aggregate publications by journal with filtering
3. **Author Analysis** - Identify prolific authors (5+ publications)
4. **Co-authorship Search** - Find papers by specific author combinations
5. **Text Search** - Full-text queries for "COVID-19 Vaccine", "COVID-19", and "SARS-CoV-2"

## Data Source

LitCovid BioC JSON format containing biomedical literature metadata including:
- PMID identifiers
- Journal information
- Author lists
- Publication passages and text content

## Author

Evan Litzer
