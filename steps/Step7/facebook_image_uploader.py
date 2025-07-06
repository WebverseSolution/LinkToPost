import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def upload_image_to_facebook(image_path: str, caption: str, username: str, password: str) -> bool:
    def remove_non_bmp(text: str) -> str:
        """Remove non-BMP characters and clean quotes."""
        return ''.join(c for c in text if ord(c) <= 0xFFFF).replace('"', '').replace("'", '').strip()

    # Configure browser options
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    success = False

    try:
        # Step 1: Login
        print("🔐 Logging into Facebook...")
        driver.get("https://www.facebook.com/")
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
        driver.find_element(By.ID, "pass").send_keys(password + Keys.ENTER)
        time.sleep(5)

        # Step 2: Navigate to homepage explicitly
        print("🏠 Navigating to homepage...")
        driver.get("https://www.facebook.com/")
        time.sleep(3)

        # Step 3: Open post modal
        print("📤 Opening post modal...")
        post_btn_xpath = "//span[contains(text(), \"What's on your mind\")]/ancestor::div[@role='button']"
        post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, post_btn_xpath)))
        driver.execute_script("arguments[0].click();", post_btn)
        time.sleep(3)

        # Step 4: Upload image
        print("🖼️ Uploading image...")
        file_input_xpath = "//input[@type='file' and contains(@accept, 'image')]"
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, file_input_xpath)))
        file_input.send_keys(os.path.abspath(image_path))
        time.sleep(5)

        # Step 5: Wait for image preview to appear
        wait.until(EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'scontent')]")))

        # Step 6: Type caption using ActionChains
        print("✍️ Typing caption...")
        paragraph_xpath = "//div[@role='textbox' and @contenteditable='true']//p"
        paragraph = wait.until(EC.presence_of_element_located((By.XPATH, paragraph_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", paragraph)
        driver.execute_script("arguments[0].focus();", paragraph)

        actions = ActionChains(driver)
        actions.move_to_element(paragraph).click()
        cleaned_caption = remove_non_bmp(caption)
        for line in cleaned_caption.splitlines():
            actions.send_keys(line)
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
        actions.perform()
        print("✅ Caption typed")

        # Step 7: Click Post button
        print("🚀 Clicking post button...")
        post_button_xpath = "//div[@aria-label='Post' and @role='button' and descendant::span[text()='Post']]"
        post_button = wait.until(EC.element_to_be_clickable((By.XPATH, post_button_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
        time.sleep(1)
        ActionChains(driver).move_to_element(post_button).pause(0.5).click().perform()
        print("✅ Post submitted")

        # Step 8: Confirm post was made
        print("⏳ Confirming post...")
        for _ in range(15):
            try:
                current_para = driver.find_element(By.XPATH, paragraph_xpath)
                if current_para.text.strip() == "":
                    print("✅ Caption cleared — likely posted")
                    success = True
                    break
            except:
                pass

            if not driver.find_elements(By.XPATH, "//img[contains(@src, 'scontent')]"):
                print("✅ Image preview gone — likely posted")
                success = True
                break

            time.sleep(1)

        if not success:
            raise RuntimeError("❌ Post confirmation failed — element still present")

        print("🎉 Post published successfully!")
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            screenshot_path = "error_fb_image_upload.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved at: {screenshot_path}")
        except Exception as screenshot_error:
            print(f"⚠️ Screenshot failed: {screenshot_error}")

    finally:
        if not success:
            print("🛑 Closing browser due to failure.")
            driver.quit()
        else:
            print("✅ Browser will remain open for manual verification.")
        return success
