import httpx
from config import SUPABASE_URL, SUPABASE_ANON_KEY

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

async def supabase_insert(table: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=HEADERS,
            json=data
        )

async def supabase_select(table: str, filters: dict = None, select: str = "*"):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {}
    if filters:
        for k, v in filters.items():
            params[k] = f"eq.{v}"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            headers=HEADERS,
            params=params
        )
        return r.json() if r.status_code == 200 else []

async def ensure_guild_config(guild_id: int):
    existing = await supabase_select("guilds", {"guild_id": guild_id})
    if not existing:
        await supabase_insert("guilds", {"guild_id": guild_id})
