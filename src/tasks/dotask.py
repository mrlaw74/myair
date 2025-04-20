import asyncio
import random

async def dotask(page, profile_id):
    await page.goto("https://sosovalue.com/exp", timeout=60000)
    print(f"[{profile_id}] Puppeteer opened page.")
    await asyncio.sleep(5)  # Wait for page to load

    from .helpers import click_signup_button, get_email_from_temp_mail
    await click_signup_button(page)
    email, mail_tab = await get_email_from_temp_mail(page)

    if email:
        print(f"[{profile_id}] Retrieved email: {email}")
        # Additional logic here...

    await page.screenshot({'path': f"screenshot_{profile_id}.png"})
    print(f"[{profile_id}] Screenshot saved.")