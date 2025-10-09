"""Token validation helper for USA Swimming API.

NOTE: Automatic token generation does not work reliably due to anti-automation
measures (session IDs expire in seconds, fingerprinting, etc.).

The recommended approach is to manually update the token periodically:
1. Visit https://data.usaswimming.org/datahub in browser
2. Open DevTools → Network tab
3. Search for a swimmer to trigger API call
4. Copy Bearer token from request headers
5. Update AUTH_TOKEN in usa_swimming.py

See docs/UPDATE_API_TOKEN.md for detailed instructions.
"""

from typing import Any

import requests


def validate_token(token: str) -> bool:
    """Test if a Sisense token is valid.

    Args:
        token: Sisense JWT token to validate

    Returns:
        True if token works, False otherwise
    """
    url = "https://usaswimming.sisense.com/api/datasources/Public%20Person%20Search/jaql"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    # Simple test query
    payload = {
        "metadata": [
            {"jaql": {"title": "Name", "dim": "[Persons.FullName]", "datatype": "text"}},
        ],
        "datasource": "Public Person Search",
        "count": 1,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def get_token_info(token: str) -> dict[str, Any]:
    """Get information about a JWT token.

    Args:
        token: JWT token to inspect

    Returns:
        Dictionary with token information
    """
    import base64
    import json

    try:
        # JWT format: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            return {"error": "Invalid JWT format"}

        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - (len(payload) % 4)
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)

        return {
            "valid_format": True,
            "user": data.get("user"),
            "tenant": data.get("tenantId"),
            "api_secret_present": "apiSecret" in data,
        }
    except Exception as e:
        return {"error": str(e)}
