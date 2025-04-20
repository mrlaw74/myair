import httpx

async def fetch_profiles(api_url, group_id="1", page=1, per_page=100):
    params = {
        "group_id": group_id,
        "page": page,
        "per_page": per_page,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()  # Raise an error for HTTP errors
        data = response.json()
        print(f"API Response: {data}")  # Log the full API response
        if data.get("success"):
            return data.get("data", [])
        else:
            raise Exception(f"API Error: {data.get('message', 'Unknown error')}")