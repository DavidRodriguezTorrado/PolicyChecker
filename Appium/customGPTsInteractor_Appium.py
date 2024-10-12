from appium import webdriver
from appium.options.common import AppiumOptions  # Import AppiumOptions
import time

# Initialize AppiumOptions for macOS
options = AppiumOptions()
options.platform_name = "Mac"  # Correct platform name
options.platform_version = "15.0.1"  # Ensure this matches your macOS version
options.device_name = "Mac"  # Arbitrary device name for macOS
options.automation_name = "Mac2"  # Correct automation name

# Specify the bundle ID
options.set_capability("appium:bundleId", "com.openai.chat")

# Set Appium-specific capabilities with the 'appium:' prefix
options.set_capability("appium:showServerLogs", True)  # Enable detailed logs
options.set_capability("appium:newCommandTimeout", 120)  # Increase timeout if needed
options.set_capability("appium:launchTimeout", 30000)  # 30 seconds

try:
    # Connect to the Appium server
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    print("Calculator app launched successfully.")
    time.sleep(3)
    elements = driver.find_elements("name", "ChatGPT")
    for element in reversed(elements):
        element.click()
    #element = driver.find_element("predicate string", "label == 'ChatGPT' AND elementType == 'XCUIElementTypeButton'")
    #element.click()
    # Resize the application window to fit the desktop while keeping the bottom bar visible
    buttons = driver.find_elements("class name", "XCUIElementTypeButton")
    for button in buttons[3:]:
        button.click()


    #toolbar = driver.find_element("class name", "XCUIElementTypeNSToolbarView")
    #toolbar.click()
    #toolbar.click()
    # Optional: Keep the app open for observation
    time.sleep(15)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if 'driver' in locals():
        driver.quit()
        print("Session ended successfully.")