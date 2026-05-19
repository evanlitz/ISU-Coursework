# CS459 Assignment 3: Post-Quantum Cryptography

**Course**: ComS/CprE 459/559 – Introduction to Cloud Computing Security, Iowa State University

## Overview

Implements a hybrid post-quantum encryption system using NIST-standardized algorithms: **ML-KEM-768** (Kyber) for key encapsulation and **ML-DSA-65** (Dilithium) for digital signatures. Files are encrypted with AES-256-GCM using a key derived from the KEM shared secret, then signed for authentication.

## Cryptographic Design

| Layer | Algorithm | Purpose |
|-------|-----------|---------|
| Key encapsulation | ML-KEM-768 (Kyber) | Secure key agreement |
| Symmetric encryption | AES-256-GCM | Confidentiality |
| Key derivation | SHA-256 | Shared secret → AES key |
| Digital signature | ML-DSA-65 (Dilithium) | Authentication / non-repudiation |

## Files

| File | Description |
|------|-------------|
| `KyberKeyGen.py` | Generates an ML-KEM-768 key pair; writes public and private keys as raw bytes |
| `DilithiumKeyGen.py` | Generates an ML-DSA-65 key pair; writes public and private keys as raw bytes |
| `EncFile.py` | Encrypts a file using Kyber KEM + AES-256-GCM, then signs the ciphertext with Dilithium |
| `DecFile.py` | Verifies the Dilithium signature, decapsulates the shared secret, and decrypts the file |

## Binary File Format (output of `EncFile.py`)

```
[KEM_CT_LEN (4 bytes)] [KEM ciphertext] [AES nonce (12 bytes)]
[AES ciphertext] [GCM tag (16 bytes)] [Dilithium signature] [SIG_LEN (4 bytes)]
```

## Usage

```bash
# Generate key pairs
python KyberKeyGen.py        # -> kyber_public.key, kyber_private.key
python DilithiumKeyGen.py    # -> dilithium_public.key, dilithium_private.key

# Encrypt
python EncFile.py <input_file> <output_file>

# Decrypt
python DecFile.py <input_file> <output_file>
```

## Dependencies

- Python 3
- [`liboqs-python`](https://github.com/open-quantum-safe/liboqs-python) – Open Quantum Safe bindings for ML-KEM and ML-DSA
- `cryptography` – AES-GCM encryption
