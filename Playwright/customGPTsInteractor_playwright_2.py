from playwright.sync_api import sync_playwright
import random
import time
import string

def human_like_typing(page, selector, text):
    for char in text:
        page.fill(selector, page.query_selector(selector).input_value() + char)
        time.sleep(random.uniform(0.05, 0.3))  # Random delay between keystrokes

def run(playwright):
    # Launch browser with stealth settings
    browser = playwright.chromium.launch(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Replace with the actual path you found
        headless=False,
        args=['--start-maximized']
    )

    # Configure the browser context with minimal settings
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
        locale='en-US,en;q=0.9',
        timezone_id='America/New_York',
        ignore_https_errors=True,
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
    )

    # Open a new page
    page = context.new_page()

    # Stealth modifications (minimal changes)
    page.add_init_script("""
        // Pass the Webdriver Test.
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    """)


    # Wait for user to manually complete any further interaction (e.g., solving CAPTCHA)
    time.sleep(1000)

    # Close the browser
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
