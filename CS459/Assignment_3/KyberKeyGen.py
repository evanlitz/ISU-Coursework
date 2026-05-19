import sys
import os
import struct
import hashlib
import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
@author Evan Litzer

This file is responsible for generating Bob's ML-KEM-768 public and private key pair
It stores both as raw bytes and then prints the key sizes


"""

ALGORITHM = "ML-KEM-768" 

def main():

# Expect exactly outpute filename for public key and filename for private key
    if len(sys.argv) != 3:
        sys.exit(1)

# Output files provided by the user
    public_key_file = sys.argv[1]
    private_key_file = sys.argv[2]

    try:

        # Create ML-KEM-768 object and generate a keypair
        # Generate keypair function returns public key in bytes
        # Export secret key returns the private key in bytes
        with oqs.KeyEncapsulation(ALGORITHM) as kem:
            public_key = kem.generate_keypair()

            private_key = kem.export_secret_key()

        # Write the public key to disk as raw bytes
        with open(public_key_file, "wb") as pub_out:
            pub_out.write(public_key)

        # Write the private key to disk as raw bytes
        with open(private_key_file, "wb") as priv_out:
            priv_out.write(private_key)
    
        # Print the algorithm and key sizes in bytes
        print(f"Algorithm: {ALGORITHM}")
        print(f"Public key size: {len(public_key)} bytes")
        print(f"Private key size: {len(private_key)} bytes")

    # Catch errors and print for debugging
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Main function
if __name__ == "__main__":
    main()