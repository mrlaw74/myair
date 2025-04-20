import asyncio
from src.api.gpm_login_api import GPMLoginApiV3

async def handle_profile(api: GPMLoginApiV3, profile_id, win_scale=None, win_pos=None, win_size=None):
    print(f"[{profile_id}] Starting profile...")

    start_result = await api.start_profile_async(profile_id, win_scale, win_pos, win_size)
    if start_result is None:
        print(f"[{profile_id}] Failed to start.")
        return

    driver_path = start_result["data"]["driver_path"]
    remote_address = start_result["data"]["remote_debugging_address"]

    # Add your logic here...
    print(f"[{profile_id}] Profile started successfully.")