# CS459 Assignment 6: Secure Data/Computation Outsourcing

**Course**: ComS/CprE 459/559 – Introduction to Cloud Computing Security, Iowa State University

## Overview

Written assignment covering cryptographic protocols for secure outsourcing of data and computation to untrusted servers. Topics span attribute-based encryption, oblivious RAM, garbled circuits, searchable encryption, and multi-party computation.

## Topics Covered

### Part 1 – Attribute-Based Encryption (ABE)
Policy-based access control over encrypted data. Analyzes which access policies can and cannot be expressed using ABE alone (AND/OR trees over static attributes), and what inputs are required for encryption vs. decryption.

### Part 2 – Oblivious RAM (ORAM)
Protocol for hiding access patterns from an untrusted server. Covers Path-ORAM specifically: what the client must maintain locally (position map / leaf assignments), the structure of the server-side binary tree, and the read/re-encrypt/write-back access procedure.

### Part 3 – Garbled Circuits
Two-party computation where one party garbles a boolean circuit and the other evaluates it without learning the garbler's inputs. Covers key assignment (two keys per wire), garbled gate construction (encrypted truth table rows, randomly permuted), and what the evaluator receives.

### Part 4 – Searchable Encryption
Allows a server to search over encrypted documents without learning the plaintext. Covers the components required by a basic searchable encryption scheme and the information the server learns during a search query.

### Part 5 – Multi-Party Computation (MPC)
Covers 1-out-of-2 Oblivious Transfer (OT) and secret-shared multiplication. Includes computing output shares for a product given additive input shares.

### Part 6 – Shamir Secret Sharing
Threshold secret sharing over a finite field. Includes computing shares using a polynomial over Z₁₁ and reconstructing the secret via Lagrange interpolation.

### Part 7 – MPC with Secret Sharing
Addition and reconstruction of secret-shared values over Z₇. Identifies which operations (addition, scalar multiplication) are local and which (multiplication, reconstruction) require interaction.

## Deliverable

`HW6_Report.pdf` — written answers to all questions.
