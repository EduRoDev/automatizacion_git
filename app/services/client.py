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
    
async def comment(repo: str, pr: int, body: str) -> None:
    token = await get_installation_token()
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr}/comments"

    headers = {
        "Authorization": f"Bearer {token}",
         "Accept": "application/vnd.github+json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"body": body}, headers=headers)
        response.raise_for_status()

async def comment_on_line(repo:str, pr:int, commit_sha: str, path: str, line: int, body: str) -> None:
    token = await get_installation_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr}/comments"

    payload = {
        "body": body,
        "commit_id": commit_sha,
        "path": path,
        "line": line,
        "side": "RIGHT"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()