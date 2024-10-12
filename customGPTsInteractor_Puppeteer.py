import time
from markdownify import markdownify as md
import requests
import json
from pyppeteer import connect
import asyncio
import random
from bs4 import BeautifulSoup, NavigableString, Tag
import re


# Function to get the WebSocket Debugger URL
def get_websocket_debugger_url():
    url = 'http://localhost:9222/json/version'

    # Make the request to get the debugger info
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the response contains an error
        data = response.json()  # Parse the JSON response

        # Extract the WebSocket debugger URL
        websocket_url = data.get('webSocketDebuggerUrl')
        if websocket_url:
            print(f"WebSocket Debugger URL: {websocket_url}")
            return websocket_url
        else:
            print("WebSocket Debugger URL not found in the response.")
            return None
    except requests.RequestException as e:
        print(f"Error retrieving the WebSocket Debugger URL: {e}")
        return None


# Function to simulate human-like typing
async def human_like_typing(page, selector, text):
    for char in text:
        await page.focus(selector)
        await page.type(selector, char)  # Type one character at a time
        await asyncio.sleep(random.uniform(0.02, 0.1))  # Random delay between keystrokes


# Function to perform a human-like click with random position within the button
async def human_like_click(page, selector):
    # Wait for the button to appear
    await page.waitForSelector(selector)

    # Hover over the button to simulate moving the mouse over it
    await page.hover(selector)

    # Add a random delay before clicking to simulate thinking time
    await asyncio.sleep(random.uniform(0.2, 1.0))

    # Get the button's position on the page
    button = await page.querySelector(selector)
    box = await button.boundingBox()

    # Calculate a random point within the button's bounding box for the click
    random_x = box['x'] + random.uniform(0, box['width'])
    random_y = box['y'] + random.uniform(0, box['height'])

    # Move the mouse to the random position within the button's area
    await page.mouse.move(random_x, random_y, steps=10)

    # Perform a click at the random position
    await page.mouse.click(random_x, random_y)


def convert_markdownify(html_content):
    html_content_no_images = re.sub(r'<img[^>]*>', '', html_content)
    # Convert HTML to Markdown, specifying options
    markdown_text = md(
        html_content_no_images,
        strip=['img'],
        heading_style='ATX',
        bullets='*',
        code_language=False
    )
    # Remove redundant newlines
    markdown_text = re.sub(r'\n\s*\n', '\n\n', markdown_text.strip())
    return markdown_text


async def prompt_and_response(page, prompt_message, turn=3):
    # Simulate human-like typing in the contenteditable div
    await human_like_typing(page, 'div#prompt-textarea[contenteditable="true"]',
                            prompt_message)

    # Wait for the button to appear
    await page.waitForSelector('button[data-testid="send-button"]')

    # Perform a human-like click on the button: send message
    await human_like_click(page, 'button[data-testid="send-button"]')

    time.sleep(5)

    # Wait for the button with the specific data-testid to appear
    await page.waitForSelector('button[data-testid="voice-play-turn-action-button"]')

    # [Getting the Response] Wait for the article element to appear (you can also use div or other selectors)
    await page.waitForSelector('article[data-testid="conversation-turn-{}"]'.format(turn))

    # Use backticks for template literals in JavaScript to incorporate the 'turn' variable
    # article_html = await page.evaluate(
    #     '''(turn) => {
    #         const element = document.querySelector(`article[data-testid="conversation-turn-${turn}"]`);
    #         return element ? element.innerHTML : "";
    #     }''',
    #     turn  # Pass 'turn' as an argument
    # )

    article_html = await page.evaluate(
        '''(turn) => {
            const element = document.querySelector(`article[data-testid="conversation-turn-${turn}"] div[data-message-author-role="assistant"]`);
            return element ? element.innerText : "";  // Fetch the innerText to keep formatting
        }''',
        turn  # Pass 'turn' as an argument
    )

    markdown = convert_markdownify(article_html)
    return markdown


# Function to automate Puppeteer using the retrieved WebSocket URL
async def run():
    """"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222"""

    websocket_url = get_websocket_debugger_url()
    if not websocket_url:
        print("Failed to retrieve WebSocket Debugger URL.")
        return

    # Connect to the running Chrome instance using the WebSocket URL
    browser = await connect(browserWSEndpoint=websocket_url)

    # Open a new page and automate tasks
    page = await browser.newPage()

    # Get the window dimensions using DevTools protocol
    dimensions = await page._client.send('Browser.getWindowForTarget')
    # print(f"Window Size: {dimensions['bounds']['width']}x{dimensions['bounds']['height']}")

    # Set the viewport using the actual integer values
    await page.setViewport({
        "width": int(dimensions['bounds']['width']*1.00),  # Use the width value
        "height": int(dimensions['bounds']['height']*1.00),  # Use the height value
    })

    # Stealth modifications (minimal changes)
    await page.evaluateOnNewDocument("""
        // Pass the Webdriver Test.
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    """)

    # https://chat.openai.com/gpts
    # await page.goto('https://chatgpt.com/g/g-aZQ1x6vqB-ai-osint')
    await page.goto('https://chatgpt.com/?model=auto')

    # Perform automation tasks (add your custom code here)
    print("Page loaded. You can now interact with the page...")

    # Wait for the contenteditable div to appear [Write prompt]
    await page.waitForSelector('div#prompt-textarea[contenteditable="true"]')

    # Here it goes the exchange of messages with the Chatbot:
    # List of prompts to be used in the loop
    prompts = ['Tell me a joke', 'Tell me another joke', 'What is the weather today?', 'What is your favorite color?']
    # Turn means which turn of the conversation we are at now. First response has turn 3 as per the HTML element numbering defined.
    turn = 3

    # Loop through prompts and get responses
    for prompt in prompts:
        response = await prompt_and_response(page=page, prompt_message=prompt, turn=turn)
        print(f"Extracted Response: {response}")
        turn += 2

    # Keep the browser open
    await asyncio.sleep(100000)  # Keep the browser open for a long time (adjust as needed)

    # Do not close the browser immediately
    # await browser.close()


# Entry point for running the script
asyncio.get_event_loop().run_until_complete(run())
