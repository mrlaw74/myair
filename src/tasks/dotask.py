import asyncio
import random
from .helpers import click_signup_button, get_email_from_temp_mail

async def dotask(page, profile_id):
    await page.goto("https://sosovalue.com/exp", timeout=60000)
    print(f"[{profile_id}] Puppeteer opened page.")
    await asyncio.sleep(5)  # Wait for page to load

    await click_signup_button(page)
    # Try to get temp mail
    email, mail_tab = await get_email_from_temp_mail(page)

    if email:
        # back to the previous tab to do task with the email get
        print(f"[{profile_id}] Retrieved email: {email}")

        # Get all open pages (tabs)
        pages = await page.browser.pages()
        print(f"[{profile_id}] All open pages: {pages}")

        # Switch back to the second tab (your original page)
        if len(pages) > 1:
            original_tab = pages[1]
            await original_tab.bringToFront()

            # try:
            #     # Enter email into form (update with class-based selector)
            #     email_input = await original_tab.waitForSelector('input[placeholder="Enter email"][type="text"]', timeout=5000)
            #     await email_input.click()
            #     await email_input.type(email, {'delay': random.randint(50, 150)})
            #     print(f"[{profile_id}] Email entered into form.")
            #     await asyncio.sleep(3)  # Sleep for 3 seconds

            #     # Enter password
            #     password_input = await original_tab.waitForSelector('input[placeholder="Enter password"][type="password"]', timeout=5000)
            #     await password_input.click()
            #     await password_input.type("@A15051999a", {'delay': random.randint(50, 150)})
            #     print(f"[{profile_id}] Password entered into form.")
            #     await asyncio.sleep(3)  # Sleep for 3 seconds

            #     # Confirm password
            #     confirm_password_input = await original_tab.waitForSelector('input[placeholder="Enter password"][type="password"]', timeout=5000)
            #     await confirm_password_input.click()
            #     await confirm_password_input.type("@A15051999a", {'delay': random.randint(50, 150)})
            #     print(f"[{profile_id}] Confirm password entered into form.")
            #     await asyncio.sleep(3)  # Sleep for 3 seconds

            # except Exception as e:
            #     print(f"[{profile_id}] Could not enter email or password: {e}")

    await page.screenshot({'path': f"screenshot_{profile_id}.png"})
    print(f"[{profile_id}] Screenshot saved.")