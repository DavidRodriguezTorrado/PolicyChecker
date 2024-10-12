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
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--start-maximized'
        ]
    )

    context = browser.new_context(
        viewport=None,  # Use full screen
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/114.0.5735.110 Safari/537.36",
        locale='en-US,en;q=0.9',
        timezone_id='America/New_York',
        geolocation={'longitude': -74.0060, 'latitude': 40.7128},
        permissions=['geolocation'],
        ignore_https_errors=True,
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
    )

    # Open a new page
    page = context.new_page()

    # Stealth modifications
    page.add_init_script("""
        // Pass the Chrome Test.
        Object.defineProperty(window, 'chrome', {
            get: () => ({
                runtime: {},
                // etc.
            }),
        });

        // Pass the Permissions Test.
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Pass the Plugins Length Test.
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Pass the Languages Test.
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Pass the Webdriver Test.
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // Pass the Platform Test.
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });

        // Mock User-Agent
        Object.defineProperty(navigator, 'userAgent', {
            get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/114.0.5735.110 Safari/537.36',
        });

        // Mock Screen Dimensions
        Object.defineProperty(screen, 'width', { get: () => 1920 });
        Object.defineProperty(screen, 'height', { get: () => 1080 });

        // Mock Device Memory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,  // 8GB of device memory
        });

        // Mock Hardware Concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,  // 8 CPU cores
        });

        // Mock Battery Status
        navigator.getBattery = async () => {
            return {
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1.0
            };
        };

        // Mock ClientRects
        const originalGetBoundingClientRect = HTMLElement.prototype.getBoundingClientRect;
        HTMLElement.prototype.getBoundingClientRect = function () {
            const rect = originalGetBoundingClientRect.apply(this, arguments);
            rect.x += Math.random() * 0.1 - 0.05;
            rect.y += Math.random() * 0.1 - 0.05;
            rect.width += Math.random() * 0.1 - 0.05;
            rect.height += Math.random() * 0.1 - 0.05;
            return rect;
        };

        // Mock Max Touch Points
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => 5,
        });

        // Mock Touch Event Support
        window.ontouchstart = true;

        // Mock Clipboard API
        Object.defineProperty(navigator, 'clipboard', {
            get: () => ({
                writeText: async () => {},
                readText: async () => 'clipboard text',
            }),
        });

        // Mock Screen Orientation
        Object.defineProperty(screen, 'orientation', {
            get: () => ({
                type: 'landscape-primary',
                angle: 0,
            }),
        });
    """)

    time.sleep(1000)

    # # Navigate to example.com with random delay
    # time.sleep(random.uniform(1.5, 3.0))  # Random delay before navigating
    # page.goto("https://platform.openai.com/", wait_until='networkidle')
    # time.sleep(random.uniform(1.5, 3.0))  # Random delay after loading
    #
    # # Simulate human-like scrolling
    # for _ in range(random.randint(3, 7)):
    #     page.mouse.wheel(0, random.randint(100, 300))
    #     time.sleep(random.uniform(0.5, 2.0))  # Random delay between scrolls
    #
    # # Look for the "Log in" button
    # login_button = page.wait_for_selector("text=Log in", timeout=10000)
    #
    # # Move mouse to the "Log in" button with human-like movements
    # box = login_button.bounding_box()
    # x = box['x'] + box['width'] / 2 + random.uniform(-5, 5)
    # y = box['y'] + box['height'] / 2 + random.uniform(-5, 5)
    # page.mouse.move(x, y, steps=random.randint(20, 40))
    # time.sleep(random.uniform(0.5, 1.0))
    #
    # # Click the "Log in" button
    # page.mouse.click(x, y)
    # time.sleep(random.uniform(0.5, 1.5))
    #
    # # Wait until the new page is fully loaded
    # page.wait_for_load_state('networkidle')
    #
    # # Enter the email in the input field with human-like typing
    # email_input = page.wait_for_selector("#email-input", timeout=10000)
    # email_input.click()
    # human_like_typing(page, "#email-input", "david.rodriguez_torrado@kcl.ac.uk")
    #
    # # Wait for the "Continue" button and click it
    # continue_button = page.wait_for_selector(".continue-btn", timeout=10000)
    # box = continue_button.bounding_box()
    #
    # x = box['x'] + random.uniform(0.1 * box['width'], 0.9 * box['width'])
    # y = box['y'] + random.uniform(0.1 * box['height'], 0.9 * box['height'])
    # page.mouse.move(x, y, steps=random.randint(20, 40))
    # time.sleep(random.uniform(0.5, 1.0))
    # page.mouse.click(x, y)
    # time.sleep(random.uniform(1.0, 2.0))
    #
    # # Enter the password in the input field with human-like typing
    # password_input = page.wait_for_selector("#password", timeout=10000)
    # password_input.click()
    # human_like_typing(page, "#password", "2NV68/,qxuGyX7/")
    #
    # # Wait for the "Continue" button and click it
    # continue_button = page.wait_for_selector("button._button-login-password", timeout=10000)
    # box = continue_button.bounding_box()
    #
    # # Human-like interactions before clicking the continue button
    # # Hover over the button a few times
    # for _ in range(random.randint(1, 3)):
    #     page.mouse.move(box['x'] + random.uniform(-10, 10), box['y'] + random.uniform(-10, 10))
    #     time.sleep(random.uniform(0.5, 1.5))
    #
    # x = box['x'] + random.uniform(0.1 * box['width'], 0.9 * box['width'])
    # y = box['y'] + random.uniform(0.1 * box['height'], 0.9 * box['height'])
    # page.mouse.move(x, y, steps=random.randint(20, 40))
    # time.sleep(random.uniform(0.5, 1.0))
    # page.mouse.click(x, y)
    # time.sleep(random.uniform(1.0, 2.0))
    #
    # # Optionally perform some actions on the new page
    # time.sleep(random.uniform(5, 10))

    # Close the browser
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
