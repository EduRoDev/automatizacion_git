import time
import jwt
import httpx

from app.core.config import get_settings

GITHUB_API_URL = "https://api.github.com"

def _read_private_keys() -> str:
    settings = get_settings()
    with open(settings.private_key, "r") as f:
        return f.read()


def generate_jwt() -> str:
    settings = get_settings()
    private = _read_private_keys()

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (9 * 60),
        "iss": settings.app_id,
    }

    return jwt.encode(payload, private, algorithm="RS256")

async def get_installation_id() -> int:
    token = generate_jwt()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}/app/installations", headers=headers)
        response.raise_for_status()
        data = response.json()

    if not data:
        raise RuntimeError("No installations found for the GitHub App.")

    return data[0]["id"]    

async def get_installation_token() -> str:
    installation_id = await get_installation_id()
    token = generate_jwt()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"{GITHUB_API_URL}/app/installations/{installation_id}/access_tokens"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data["token"]




