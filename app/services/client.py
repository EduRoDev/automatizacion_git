import httpx 
from app.services.auth import GITHUB_API_URL, get_installation_token

async def fetch_diff(url: str) -> str:
    token = await get_installation_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        return response.text