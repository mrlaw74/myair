import aiohttp
import json
from urllib.parse import urlencode

class GPMLoginApiV3:
    START_ENDPOINT = "/api/v3/profiles/start/{id}"

    def __init__(self, api_url):
        self._api_url = api_url

    async def start_profile_async(self, profile_id, win_scale=None, win_pos=None, win_size=None):
        params = {}
        if win_scale is not None:
            params["win_scale"] = win_scale
        if win_pos is not None:
            params["win_pos"] = f"{win_pos[0]},{win_pos[1]}"
        if win_size is not None:
            params["win_size"] = f"{win_size[0]},{win_size[1]}"

        query_string = "?" + urlencode(params) if params else ""
        api_url = self._api_url + self.START_ENDPOINT.replace("{id}", profile_id) + query_string

        resp = await self.http_get_async(api_url)

        if resp is None:
            return None

        try:
            return json.loads(resp)
        except json.JSONDecodeError:
            return None

    async def http_get_async(self, api_url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        return await response.text()
                    raise Exception("Unknown error")
            except Exception:
                return None