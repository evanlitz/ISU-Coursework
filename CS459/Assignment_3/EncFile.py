import sys
import os
import struct
import hashlib
import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
@author Evan Litzer

This file is responsible for combining the DSA private key, receiver KEM public key, plaintext file, and output ciphertext file to then do the following.

- KEM encapsulation
- Derives AES key from shared secret using SHA-256
- AES-GCM encrypts the plaintext
- Sign the structured encrypted data
- And then write the output in the binary format

"""

def main() -> None:
    if len(sys.argv) != 5:
        sys.exit(1)

    sender_dsa_private_key_file = sys.argv[1]
    receiver_kem_public_key_file = sys.argv[2]
    plaintext_file = sys.argv[3]
    ciphertext_file = sys.argv[4]

    # Algorithms used for encryption
    kem_alg = "ML-KEM-768"
    sig_alg = "ML-DSA-65"

    try:
        # Read the input in as raw bytes
        with open(sender_dsa_private_key_file, "rb") as f:
            sender_dsa_private_key = f.read()

        with open(receiver_kem_public_key_file, "rb") as f:
            receiver_kem_public_key = f.read()

        with open(plaintext_file, "rb") as f:
            plaintext = f.read()

        # Key Encapsulation to get the kem_ciphertext and shared secret
        with oqs.KeyEncapsulation(kem_alg) as kem:
            kem_ciphertext, shared_secret = kem.encap_secret(receiver_kem_public_key)

        # Derive AES-128 key as a SHA256(shared_secret)[0:16]
        aes_key = hashlib.sha256(shared_secret).digest()[:16]

        # For AES-GCM Encryption (AES-128-GCM), generate a 12 byte random nonce
        nonce = os.urandom(12)

        # Encrypt the plaintext with the AES-128-GCM.
        aesgcm = AESGCM(aes_key)

        # AESGCM.encrypt from the cryptography lib returns ciphertext and byte tag
        ct_and_tag = aesgcm.encrypt(nonce, plaintext, None)

        # Split it into AES ciphertext and a 16-byte authentication tag
        if len(ct_and_tag) < 16:
            raise ValueError("AES-GCM output too short to contain a 16-byte tag.")

        aes_ciphertext = ct_and_tag[:-16]
        tag = ct_and_tag[-16:]

        # Digital signature (ML-DSA-65) : Sign is KEM ciphertext + nonce + AES ciphertext + tag
        to_sign = kem_ciphertext + nonce + aes_ciphertext + tag

        to_sign = kem_ciphertext + nonce + aes_ciphertext + tag

        # Load the private key for signing.
        try:
            # Preferred pattern for many versions: pass secret_key into constructor
            with oqs.Signature(sig_alg, secret_key=sender_dsa_private_key) as sig:
                signature = sig.sign(to_sign)
        except TypeError:
            # Fallback: try alternate method name if constructor doesn't accept secret_key
            with oqs.Signature(sig_alg) as sig:
                if hasattr(sig, "set_secret_key"):
                    sig.set_secret_key(sender_dsa_private_key)
                    signature = sig.sign(to_sign)
                else:
                    raise RuntimeError("Cannot load ML-DSA private key (no secret_key ctor and no set_secret_key).")

        # Output the ciphertext file with 4 byte KEM ciphertext length and KEM ciphertext, 12 byte nonce, AES ciphertext, 16 byte tag, ML-DSA signature, and 4 byte signature length
        # Store the lengths as 4-byte big endian unsigned ints
        kem_len_bytes = struct.pack(">I", len(kem_ciphertext))
        sig_len_bytes = struct.pack(">I", len(signature))

        with open(ciphertext_file, "wb") as out:
            out.write(kem_len_bytes)
            out.write(kem_ciphertext)
            out.write(nonce)
            out.write(aes_ciphertext)
            out.write(tag)
            out.write(signature)
            out.write(sig_len_bytes)

        # Output for file indicated by the assignment, print completion, and lengths
        print("Encryption complete")
        print(f"KEM ciphertext length: {len(kem_ciphertext)}")
        print(f"AES ciphertext length: {len(aes_ciphertext)}")
        print(f"Signature length: {len(signature)}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
