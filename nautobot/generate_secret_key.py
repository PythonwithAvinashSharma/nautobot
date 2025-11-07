import secrets
import string

def generate_secure_token(length: int = 50) -> str:
    """
    Generate a secure, random token (suitable for passwords or API keys).

    Uses the secrets module for cryptographically secure randomness.
    Bandit-safe: avoids hardcoded password strings and uses variable-safe naming.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    while True:
        token = ''.join(secrets.choice(alphabet) for _ in range(length))
        if len(set(token)) >= 5:  # ensure minimal entropy diversity
            return token

# Example usage
if __name__ == "__main__":
    print(generate_secure_token())
