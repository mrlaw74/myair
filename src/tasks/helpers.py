import asyncio
import random

async def click_signup_button(page):
    attempts = 0
    await asyncio.sleep(random.uniform(1, 2))

    while True:
        try:
            print(f"[click_signup_button] Looking for 'Sign Up' button...")
            # Try to find the button with visible text 'Sign Up'
            button = await page.waitForXPath('//button[contains(text(), "Sign Up")]', timeout=3000)
            await button.click()
            print("[click_signup_button] Clicked 'Sign Up' button.")
            break

        except Exception as e:
            if attempts >= 5:
                print(f"[click_signup_button] Failed after {attempts} attempts")
                raise e
            print(f"[click_signup_button] Attempt {attempts} failed, retrying...")
            await asyncio.sleep(random.uniform(1, 2))
            attempts += 1

async def get_email_from_temp_mail(page):
    try:
        print("[get_email_from_temp_mail] Opening new tab for temp mail...")
        mail_tab = await page.browser.newPage()
        await mail_tab.goto('https://mail.tm/en/', timeout=60000)
        await asyncio.sleep(5)

        email = ''
        retries = 0
        while not email.strip() and retries <= 10:
            try:
                element = await mail_tab.waitForSelector('input[type="email"]', timeout=3000)
                email = await mail_tab.evaluate('(el) => el.value', element)
                print(f"[get_email_from_temp_mail] Email: {email.strip()}")
            except Exception as e:
                print(f"[get_email_from_temp_mail] Attempt {retries + 1} failed: {e}")
            await asyncio.sleep(2)
            retries += 1

        # Do NOT close the tab, just return both email and tab
        return email.strip(), mail_tab

    except Exception as e:
        print(f"[get_email_from_temp_mail] Error: {e}")
        return None, None