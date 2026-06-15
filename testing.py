from app.services.auth import generate_jwt, get_installation_token
import asyncio

# token = generate_jwt()
# print(token)
# print(f"Longitud: {len(token)}")

token = asyncio.run(get_installation_token())
print(token[:12],"...")
print(f"Longitud: {len(token)}")
