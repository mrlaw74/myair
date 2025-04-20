import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from pyppeteer import connect
# from src.tasks import dotask  # Import the dotask function
from src.tasks.dotask import dotask
from src.api.gpm_login_api import GPMLoginApiV3

async def handle_profile(api: GPMLoginApiV3, profile_id, win_scale=None, win_pos=None, win_size=None):
    print(f"[{profile_id}] Starting profile...")

    start_result = await api.start_profile_async(profile_id, win_scale, win_pos, win_size)
    if start_result is None:
        print(f"[{profile_id}] Failed to start.")
        return

    driver_path = start_result["data"]["driver_path"]
    remote_address = start_result["data"]["remote_debugging_address"]

    print(f"[{profile_id}] Profile started successfully.")

    # --- Selenium Setup ---
    chrome_dir = str(Path(driver_path).parent)
    chrome_executable = str(Path(driver_path).name)

    chrome_service = ChromeService(executable_path=os.path.join(chrome_dir, chrome_executable))
    chrome_options = Options()
    chrome_options.debugger_address = remote_address

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    print(f"[{profile_id}] Selenium opened page.")

    # --- Puppeteer Setup ---
    browser_url = f"http://{remote_address}"
    browser = await connect(browserURL=browser_url)
    page = await browser.newPage()

    # Perform the task using Puppeteer
    await dotask(page, profile_id)

    await browser.close()
    driver.quit()
    print(f"[{profile_id}] Done.")