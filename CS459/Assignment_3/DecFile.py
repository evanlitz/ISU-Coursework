import sys
import os
import struct
import hashlib
import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
@author Evan Litzer

This file is responsible for taking the receiver KEM private key, sender DSA public key, and ciphertext file to do the following:
= Parse the binary file
- Verify the signature
- Decapsulate KEM ciphertext
- Re-derive the AES key
- Decrypt and print the plaintext


"""

# python DecFile.py <receiver_kem_private_key> <sender_dsa_public_key> <ciphertext_file>
def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(1)
# Get the info from the arguments in command line through argv array
    receiver_kem_private_key_file = sys.argv[1]
    sender_dsa_public_key_file = sys.argv[2]
    ciphertext_file = sys.argv[3]
# Decryption algorithms
    kem_alg = "ML-KEM-768"
    sig_alg = "ML-DSA-65"

    try:
        # Read keys and ciphertext
        with open(receiver_kem_private_key_file, "rb") as f:
            receiver_kem_private_key = f.read()

        with open(sender_dsa_public_key_file, "rb") as f:
            sender_dsa_public_key = f.read()

        with open(ciphertext_file, "rb") as f:
            blob = f.read()

        if len(blob) < 4 + 4 + 12 + 16:
            raise ValueError("Ciphertext file too short to be valid.")

    # Parse the ciphertext format.
    # Format is the 4 byte kem_length, then kem cyphertext, followed by 12 byte nonce, then aes ciphertext, followed by 16 byte tag, signature, and 4 byte sig length
        sig_len = struct.unpack(">I", blob[-4:])[0]
        if sig_len <= 0:
            raise ValueError("Invalid signature length.")

        if len(blob) < 4 + sig_len + 4:
            raise ValueError("Ciphertext file too short")

        signature_start = len(blob) - 4 - sig_len
        signature = blob[signature_start:signature_start + sig_len]

        # Everything before the signature is as follows: [kem_len][kem_ct][nonce][aes_ct][tag]
        core = blob[:signature_start]

        if len(core) < 4 + 12 + 16:
            raise ValueError("Ciphertext core too short to contain fields")

        kem_len = struct.unpack(">I", core[:4])[0]
        if kem_len <= 0:
            raise ValueError("Invalid KEM ciphertext length")

        pos = 4
        if len(core) < pos + kem_len + 12 + 16:
            raise ValueError("Ciphertext core too short for KEM length.")

        kem_ct = core[pos:pos + kem_len]
        pos += kem_len

        nonce = core[pos:pos + 12]
        pos += 12

        # Tag is always the last 16 bytes of core
        tag = core[-16:]

        # AES ciphertext is whatever is between nonce and tag
        aes_ct = core[pos:-16]
        if len(aes_ct) < 0:
            raise ValueError("Invalid AES ciphertext length.")

        # Verify the signature, and once over is kem_ct, nonce, aes_ct, and then tag
        signed_message = kem_ct + nonce + aes_ct + tag

        with oqs.Signature(sig_alg) as sig:
            is_valid = sig.verify(signed_message, signature, sender_dsa_public_key)

        print(f"Signature valid: {is_valid}")
        if not is_valid:
            print("Signature verification did not work.")
            sys.exit(1)

        # Decapsulate the shared secret --> ML-KEM-768
        try:
            with oqs.KeyEncapsulation(kem_alg, secret_key=receiver_kem_private_key) as kem:
                shared_secret = kem.decap_secret(kem_ct)
        except TypeError:
            # Fallback for other API variants
            with oqs.KeyEncapsulation(kem_alg) as kem:
                if hasattr(kem, "set_secret_key"):
                    kem.set_secret_key(receiver_kem_private_key)
                    shared_secret = kem.decap_secret(kem_ct)
                else:
                    raise RuntimeError("Cannot load ML-KEM private key."
                )

        # Derive AES-128 key as: SHA256(shared_secret)[0:16]
        aes_key = hashlib.sha256(shared_secret).digest()[:16]

        # AES-GCM decryption.
        # The cryptography expects the ciphertext and tag together
        aesgcm = AESGCM(aes_key)
        plaintext = aesgcm.decrypt(nonce, aes_ct + tag, None)

        # Print the plaintext (as bytes decoded if possible; otherwise show raw bytes)
        print("Decryption worked")
        try:
            print(plaintext.decode("utf-8"))
        except UnicodeDecodeError:
            print(plaintext)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()