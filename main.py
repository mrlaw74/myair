import asyncio
import json
from src.tasks.profile_handler import handle_profile
from src.utils.config import API_URL
from src.api.gpm_login_api import GPMLoginApiV3

async def main():
    with open("profiles.json", "r", encoding="utf-8") as f:
        profile_configs = json.load(f)

    api = GPMLoginApiV3(API_URL)
    await asyncio.gather(*(handle_profile(
        api,
        cfg["id"],
        win_pos=cfg.get("win_pos"),
        win_size=cfg.get("win_size"),
        win_scale=0.7
    ) for cfg in profile_configs))

if __name__ == "__main__":
    asyncio.run(main())