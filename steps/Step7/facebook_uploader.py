import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def remove_non_bmp(text: str) -> str:
    """Removes unsupported Unicode characters and quotes."""
    text = ''.join(c for c in text if ord(c) <= 0xFFFF)
    return text.replace('"', '').replace("'", '').strip()


def upload_to_facebook(video_url: str, caption: str, username: str, password: str) -> bool:
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    success = False

    try:
        # Step 1: Open YouTube video page
        driver.get(video_url)
        time.sleep(5)

        # Step 2: Click Share button
        try:
            share_xpath = "//yt-button-view-model[contains(@class, 'ytd-menu-renderer')]//button"
            wait.until(EC.element_to_be_clickable((By.XPATH, share_xpath))).click()
        except:
            raise RuntimeError("❌ Failed to click YouTube Share button.")

        # Step 3: Click Facebook option
        try:
            fb_xpath = "//yt-share-target-renderer[.//div[@id='title' and text()='Facebook']]//button[@id='target']"
            wait.until(EC.element_to_be_clickable((By.XPATH, fb_xpath))).click()
        except:
            raise RuntimeError("❌ Failed to select Facebook share option.")

        # Step 4: Switch to Facebook tab
        try:
            driver.switch_to.window(driver.window_handles[1])
        except:
            raise RuntimeError("❌ Failed to switch to Facebook tab.")

        # Step 5: Facebook Login
        try:
            wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
            driver.find_element(By.ID, "pass").send_keys(password + Keys.ENTER)
        except:
            raise RuntimeError("❌ Facebook login failed.")

        # Step 6: CAPTCHA detection (manual handling)
        time.sleep(5)
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            captcha_detected = any("recaptcha" in (iframe.get_attribute("src") or "") for iframe in iframes)
            if captcha_detected:
                input("🔓 Solve CAPTCHA and press ENTER to continue...")
        except:
            pass

        # Step 7: Handle 'Not Now' dialog
        try:
            not_now_xpath = "//div[@role='button' and .//span[text()='Not now']]"
            not_now_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, not_now_xpath)))
            driver.execute_script("arguments[0].click();", not_now_btn)
        except:
            pass

        # Step 8: Enter Caption
        try:
            caption_xpath = "//div[@role='textbox' and @contenteditable='true' and contains(@aria-placeholder, \"What's on your mind\")]"
            post_box = wait.until(EC.element_to_be_clickable((By.XPATH, caption_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_box)
            post_box.click()
            time.sleep(1)

            cleaned = remove_non_bmp(caption)
            for line in cleaned.splitlines():
                post_box.send_keys(line)
                post_box.send_keys(Keys.SHIFT, Keys.ENTER)
        except:
            try:
                driver.save_screenshot("error_typing_caption.png")
            except:
                pass
            raise RuntimeError("❌ Failed to enter caption.")

        # Step 9: Click Share
        try:
            share_btn_xpath = "//div[@aria-label='Share' and @role='button']"
            share_btn = wait.until(EC.element_to_be_clickable((By.XPATH, share_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", share_btn)
            time.sleep(1)
            share_btn.click()
        except:
            try:
                driver.save_screenshot("error_click_share.png")
            except:
                pass
            raise RuntimeError("❌ Failed to click Share button.")

        # Step 10: Wait for posting to complete
        time.sleep(8)
        success = True

    except:
        try:
            driver.save_screenshot("error_facebook_upload.png")
        except:
            pass
        success = False

    finally:
        driver.quit()
        return success
