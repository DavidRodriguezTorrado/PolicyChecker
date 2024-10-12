from appium import webdriver
from appium.options.common import AppiumOptions  # Import AppiumOptions
import time
from appium.webdriver.common.appiumby import AppiumBy

# Initialize AppiumOptions for macOS
options = AppiumOptions()
options.platform_name = "Mac"  # Correct platform name
options.platform_version = "15.0.1"  # Ensure this matches your macOS version
options.device_name = "Mac"  # Arbitrary device name for macOS
options.automation_name = "Mac2"  # Correct automation name

# Specify the bundle ID
options.set_capability("appium:bundleId", "com.apple.calculator")

# Set Appium-specific capabilities with the 'appium:' prefix
options.set_capability("appium:showServerLogs", True)  # Enable detailed logs
options.set_capability("appium:newCommandTimeout", 120)  # Increase timeout if needed
options.set_capability("appium:launchTimeout", 30000)  # 30 seconds

try:
    # Connect to the Appium server
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    print("Calculator app launched successfully.")

    # Click on a sequence of buttons: 1, +, 2, =
    driver.find_element("name", "1").click()  # Click button '1'
    driver.find_element("name", "Más").click()  # Click button '+'
    driver.find_element("name", "2").click()  # Click button '2'
    driver.find_element("name", "Es igual a").click()  # Click button '='

    buttons = driver.find_elements("class name", "XCUIElementTypeButton")
    for button in buttons:
        button.click()

    # Optional: Keep the app open for observation
    time.sleep(5)
    driver.quit()

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if 'driver' in locals():
        driver.quit()
        print("Session ended successfully.")