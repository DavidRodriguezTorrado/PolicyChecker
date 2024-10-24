import time
from markdownify import markdownify as md
import requests
from datetime import datetime
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


# Function to initialize browser and page
async def initialize_browser():
    """Initialize the browser and page with required settings."""
    websocket_url = get_websocket_debugger_url()
    if not websocket_url:
        print("Failed to retrieve WebSocket Debugger URL.")
        return None, None

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

    return browser, page


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


# Function to perform hover over the div and click the revealed button
async def delete_chat(page):
    """
    Hovers over a specific div to reveal a button and clicks the button.

    Args:
        page: The Pyppeteer page object.
        turn (int): The conversation turn number to target.
    """
    # Define the selector for the target div with escaped colons
    chat_selector = 'div.absolute.bottom-0.top-0.can-hover\\:group-hover\\:from-token-sidebar-surface-secondary'

    # Define the selector for the button that appears after hovering
    # Ensure that the button is within the specific article corresponding to the current turn
    button_selector = 'button[data-testid="history-item-0-options"]'

    try:
        # Wait for the target chat to be present in the DOM
        await page.waitForSelector(chat_selector, timeout=10000)  # waits up to 10 seconds

        # Use a random start coordinate before moving to target to simulate human-like approach
        random_start_x = random.randint(0, 100)
        random_start_y = random.randint(0, 100)
        await page.mouse.move(random_start_x, random_start_y, steps=5)
        await asyncio.sleep(random.uniform(0.2, 0.5))

        # Perform a hover over the chat
        await page.hover(chat_selector)

        # Wait for the new button to appear within the specific article
        await page.waitForSelector(button_selector, timeout=10000)

        # Perform a human-like click on the new button
        await human_like_click(page, button_selector)

        options = 'div[role="menuitem"]'
        elements = await page.querySelectorAll(options)
        await asyncio.sleep(random.uniform(0.3, 0.8))  # Random delay before selecting an option
        await elements[-1].click()

        confirm_deletion = 'button[data-testid="delete-conversation-confirm-button"]'
        await page.waitForSelector(confirm_deletion, timeout=10000)
        await asyncio.sleep(random.uniform(0.4, 1.2))  # Add hesitation before confirming
        await human_like_click(page, confirm_deletion)

    except asyncio.TimeoutError:
        print(f"Timeout: The target div or the button '{button_selector}' was not found.")
    except Exception as e:
        print(f"An error occurred in hover_and_click: {e}")


async def prompt_and_response(page, prompt_message, turn=3):
    # Simulate human-like typing in the contenteditable div
    await human_like_typing(page, 'div#prompt-textarea[contenteditable="true"]',
                            prompt_message)

    # Wait for the button to appear
    await page.waitForSelector('button[data-testid="send-button"]')

    # Perform a human-like click on the button: send message
    await human_like_click(page, 'button[data-testid="send-button"]')

    # [Waiting for Answer] Wait specifically for the voice-play button inside the targeted article
    await page.waitForSelector(
        f'article[data-testid="conversation-turn-{turn}"] button[data-testid="voice-play-turn-action-button"]',
        timeout=90000
    )

    # [Retrieve Answer] Use backticks for template literals in JavaScript to incorporate the 'turn' variable
    article_html = await page.evaluate(
        '''(turn) => {
            const element = document.querySelector(`article[data-testid="conversation-turn-${turn}"] div[data-message-author-role="assistant"]`);
            return element ? element.outerHTML : "";  // Fetch the outerHTML to get the raw HTML content
        }''',
        turn  # Pass 'turn' as an argument
    )

    markdown = convert_markdownify(article_html)
    return markdown


async def interact_with_gpt_model(page, prompts, chat='auto'):
    # https://chat.openai.com/gpts
    # await page.goto('https://chatgpt.com/g/g-aZQ1x6vqB-ai-osint')
    # await page.goto('https://chatgpt.com/?model={}'.format(model))
    if chat == 'auto':
        await page.goto('https://chatgpt.com/?model={}'.format(chat))
    else:
        await page.goto(chat)

    # Wait for the Text bar where the prompt is going to be written to appear
    await page.waitForSelector('div#prompt-textarea[contenteditable="true"]')

    # Turn means which turn of the conversation we are at now. First response has turn 3 as per the HTML element numbering defined.
    turn = 3

    responses = []

    # Loop through prompts and get responses
    for prompt in prompts:
        response = await prompt_and_response(page=page, prompt_message=prompt, turn=turn)
        responses.append(response)
        # print(f"Extracted Response: {response}")
        turn += 2

    # We delete the chat to do not overload too much the website.
    await delete_chat(page)
    return responses


async def search_gpts_by_keywords(page, search_text, max_clicks=1):
    await page.goto('https://chat.openai.com/gpts', {'waitUntil': 'networkidle2'})
    # Wait for the parent div containing the input field to be visible
    parent_div_selector = 'div.group.relative.rounded-xl.z-20.mb-6.mt-2.flex-grow'
    await page.waitForSelector(parent_div_selector, {'visible': True})

    # Click on the parent div
    await page.click(parent_div_selector)

    is_visible = await page.evaluate('''() => {
        const el = document.querySelector('input[placeholder="Buscar GPT"]');
        return el && el.offsetParent !== null;
    }''')

    if not is_visible:
        await page.evaluate('''() => {
            const el = document.querySelector('input[placeholder="Buscar GPT"]');
            if (el) el.scrollIntoView();
        }''')
        await asyncio.sleep(0.5)  # Wait for the element to be visible

    # Focus on the input field
    await page.evaluate('''() => {
        const el = document.querySelector('input[placeholder="Buscar GPT"]');
        if (el) el.focus();
    }''')

    # Write down the text to search GPTs
    await human_like_typing(page=page, selector='input[placeholder="Buscar GPT"]', text=search_text)

    # Wait for the spinner to appear first (meaning it's processing our request)
    await page.waitForSelector('svg.animate-spin', {'visible': True})

    # Wait for the spinner to disappear (meaning results have been found)
    await page.waitForFunction('document.querySelector("svg.animate-spin") === null')

    # Initialize data collection
    gpts = []
    unique_keys = set()  # Set to keep track of unique (title, description, developer)

    # Define a helper function to gather GPT data
    async def gather_gpt_data():
        nonlocal gpts, unique_keys
        # Look for the results
        await page.waitForSelector('[id^="headlessui-popover-panel-"]', {'visible': True})

        # Get all the <a> elements within the specified div using a CSS selector
        links = await page.querySelectorAll('[id^="headlessui-popover-panel-"] a')

        # Iterate over the ElementHandles to interact with each link
        for link in links:
            text = await link.getProperty('innerText')
            text_value = await text.jsonValue()

            # Get the information from the search list.
            text_list = text_value.split('\n')

            # Default values for each field
            title = text_list[0] if len(text_list) > 0 else ''
            description = ''
            developer = ''
            num_conversations = ''

            # Check if there's a description and developer
            if len(text_list) > 2:
                description = text_list[1]
                developer = text_list[2][text_list[2].find(' ') + 1:]
                num_conversations = text_list[3] if len(text_list) > 3 else ''
            elif len(text_list) == 2:
                # If there's no description, assume the second element is the developer
                developer = text_list[1][text_list[1].find(' ') + 1:]
                num_conversations = text_list[2] if len(text_list) > 2 else ''

            # Create a unique key for each GPT
            key = (title, description, developer)

            # Check if this GPT is already processed
            if key in unique_keys:
                continue

            # Mark this GPT as processed
            unique_keys.add(key)

            # Click on the element to open the GPT details
            await link.click()

            # Wait for the spinner to disappear (meaning results have been found)
            await page.waitForFunction('document.querySelector("svg.animate-spin") === null')

            # Wait for the GPT details page to load
            await page.waitForSelector('div.text-2xl.font-semibold', {'visible': True})

            # Retrieve the values within the dialog div
            elements_data = await page.evaluate('''() => {
                const data = {};
                const dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return data;
                const elements = Array.from(dialog.querySelectorAll('div.flex.flex-col.items-center'));
                elements.forEach(el => {
                    const header = el.querySelector('div.text-xl.font-semibold.text-center');
                    const description = el.querySelector('div.text-xs.text-token-text-tertiary');
                    if (header && description) {
                        const headerText = header.innerText.trim();
                        const descriptionText = description.innerText.trim();
                        // Check if this element is the rating value
                        if (headerText.match(/^\d+\.\d+$/) && descriptionText.includes('Valoraciones')) {
                            data.ratingValue = headerText;
                            const numRatingsMatch = descriptionText.match(/\((\d+\+)\)/);
                            data.numRatings = numRatingsMatch ? numRatingsMatch[1] : '';
                        } 
                        // Check if this element is the conversation count
                        else if (descriptionText.includes('Conversaciones')) {
                            data.numConversations = headerText;
                        } 
                        // Check if this element is the category
                        else if (descriptionText.includes('Categoría')) {
                            data.category = headerText;
                        }
                    }
                });
                return data;
            }''')

            rating_value = elements_data.get('ratingValue', '')
            num_ratings = elements_data.get('numRatings', '')
            category = elements_data.get('category', '')
            num_conversations_detail = elements_data.get('numConversations', '')

            sample_prompts = await page.evaluate('''() => {
                const elements = Array.from(document.querySelectorAll('a[href*="?q="]'));
                return elements.map(el => el.innerText.trim());
            }''')

            chat_url = await page.evaluate('''() => {
                const button = document.querySelector('a.btn-primary[href*="/g/"]');
                return button ? button.href : null;
            }''')

            timestamp = datetime.utcnow().isoformat()  # Generate the timestamp in Python

            gpts.append({
                'timestamp': timestamp,
                'title': title,
                'description': description,
                'developer': developer,
                'num_conversations': num_conversations_detail or num_conversations,
                'category': category,
                'rating_value': rating_value,
                'num_ratings': num_ratings,
                'sample_prompts': sample_prompts,
                'chat_url': chat_url
            })

            # Close the popup window
            close_button = await page.querySelector('button[data-testid="close-button"]')
            if close_button:
                await close_button.click()

    # Initial data gathering
    await gather_gpt_data()

    # Click the "Ver más" button up to max_clicks times
    for _ in range(max_clicks):
        try:
            # Click the "Ver más" button if it exists
            await page.waitForSelector('button.btn-secondary', {'visible': True, 'timeout': 10000})
            ver_mas_button = await page.querySelector('button.btn-secondary')
            if ver_mas_button:
                await ver_mas_button.click()
                # await page.waitForSelector('svg.animate-spin', {'visible': True})
                await page.waitForFunction('document.querySelector("svg.animate-spin") === null')
                await gather_gpt_data()
            else:
                break
        except:
            break

    return gpts


# Function to automate Puppeteer using the retrieved WebSocket URL
async def run():
    # Before run(), the following command should be executed in a terminal
    """"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222"""
    browser, page = await initialize_browser()
    if not browser or not page:
        return

    # input_prompts = ['Tell me a joke', 'Tell me another joke', 'What is the weather today?', 'What is your favorite color?']
    # responses = await interact_with_gpt_model(page=page, prompts=input_prompts, chat='auto')
    #
    # prompt_response_pairs = list(zip(input_prompts, responses))
    #
    # print("Prompt-Response Pairs:")
    # for idx, (prompt, response) in enumerate(prompt_response_pairs, 1):
    #     print(f"User {idx}: {prompt}")
    #     print(f"ChatGPT {idx}: {response}")

    gpts = await search_gpts_by_keywords(page=page, search_text='doctor', max_clicks=0)
    for gpt in gpts:
        print(gpt)

    # Keep the browser open
    await asyncio.sleep(100000)  # Keep the browser open for a long time (adjust as needed)

    # Do not close the browser immediately
    # await browser.close()


if __name__ == "__main__":
    # Entry point for running the script
    asyncio.get_event_loop().run_until_complete(run())
