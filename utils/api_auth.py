"""
API key handling for the Django API.

The API stores only bcrypt hashes of the allowed keys, hex encoded and separated by spaces,
in the environment variable API_AUTH_ALLOWED_KEYS. Clients send the plain key in the
X-Api-Key header. The environment is loaded by the Django settings (env/.env or env/.env.prod).

Generate the hash for a new key with:

    python -m utils.api_auth <key>
"""
import os
import sys
from typing import List

from bcrypt import hashpw, gensalt, checkpw

ALLOWED_KEYS_ENV_VAR = "API_AUTH_ALLOWED_KEYS"


def encrypt_api_auth_token(api_token) -> bytes:
    """
    Encrypts the API token using bcrypt.

    This function only serves to encrypt a new API token for customers and should never get called in production.
    """
    return hashpw(
        password=api_token.encode("utf-8"),
        salt=gensalt(),
    )


def check_hash(api_token, encrypted_api_token) -> bool:
    """
    Checks if the API token matches the encrypted API token.
    """
    return checkpw(
        password=api_token.encode("utf-8"),
        hashed_password=encrypted_api_token,
    )


def _get_allowed_key_hashes() -> List[bytes]:
    hashes = []
    for allowed_api_key in os.getenv(ALLOWED_KEYS_ENV_VAR, "").split():
        try:
            hashes.append(bytes.fromhex(allowed_api_key))
        except ValueError:
            print(
                f"Ignoring an entry in {ALLOWED_KEYS_ENV_VAR} that is not a hex encoded hash.",
                file=sys.stderr,
            )
    return hashes


def is_api_key_valid(api_key) -> bool:
    """
    Validates the API key against the hashes in API_AUTH_ALLOWED_KEYS.

    Returns False if no keys are configured, so the API is never open by accident.
    """
    for key_hash in _get_allowed_key_hashes():
        try:
            if check_hash(api_key, key_hash):
                return True
        except ValueError:
            # entry is valid hex, but not a bcrypt hash
            continue
    return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m utils.api_auth <key>", file=sys.stderr)
        sys.exit(1)
    print(encrypt_api_auth_token(sys.argv[1]).hex())
