import sys
import os
import struct
import hashlib
import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
@author Evan Litzer

This file is responsible for generating Alice's ML-DSA-65 public and private signing key pair
Then store both of the keys as raw bytes and print the algorithm name and key sizes.


"""

def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(1)

    public_key_file = sys.argv[1]
    private_key_file = sys.argv[2]

    alg = "ML-DSA-65"

    try:
        # Create an ML-DSA-65 signature object and generate a keypair to use for Alice
        with oqs.Signature(alg) as sig:
            public_key = sig.generate_keypair()      # bytes
            private_key = sig.export_secret_key()    # bytes

        # Store keys as raw byte arrays for both public and private
        with open(public_key_file, "wb") as f_pub:
            f_pub.write(public_key)

        with open(private_key_file, "wb") as f_priv:
            f_priv.write(private_key)

        # Output as assignment indicates
        print(f"Algorithm name: {alg}")
        print(f"Public key size (in bytes): {len(public_key)}")
        print(f"Private key size (in bytes): {len(private_key)}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
