import time
import os
import uuid
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def upload_to_instagram(username: str, password: str, image_urls: list[str], caption: str, video_path: str = None) -> bool:
    options = Options()
    # options.add_argument("--headless=new")  # Enable this in production if needed
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    downloaded_paths = []
    success = False

    try:
        # Step 1: Login
        driver.get("https://www.instagram.com/accounts/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Step 2: Handle 'Not Now' popups
        try:
            not_now = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and normalize-space()='Not now']"))
            )
            not_now.click()
            time.sleep(1)
        except:
            pass

        # Step 3: Wait for home feed
        wait.until(EC.presence_of_element_located((By.XPATH, "//nav")))

        # Step 4: Click Create > Post
        driver.find_element(By.XPATH, "//span[normalize-space()='Create']").click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Post']"))).click()

        # Step 5: Upload media
        input_file = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))

        if video_path:
            input_file.send_keys(os.path.abspath(video_path))
        else:
            local_paths = [_download_and_save(url) for url in image_urls[:1]]
            downloaded_paths.extend(local_paths)
            input_file.send_keys(local_paths[0])

        time.sleep(3)

        # Step 6: Handle Reels popup if shown
        try:
            ok_btn = driver.find_element(By.XPATH, "//button[text()='OK']")
            if ok_btn.is_displayed():
                ok_btn.click()
        except:
            pass

        # Step 7: Click Next twice
        for _ in range(2):
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Next']")))
            next_btn.click()
            time.sleep(1)

        # Step 8: Enter caption
        try:
            caption_div = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@aria-label='Write a caption...' and @contenteditable='true']"))
            )
            caption_div.click()
            time.sleep(0.5)

            for char in caption:
                caption_div.send_keys(char)
                time.sleep(0.02)
        except:
            try:
                driver.save_screenshot("error_typing_caption.png")
            except:
                pass

        # Step 9: Share the post
        try:
            share_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='button' and contains(text(), 'Share')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView(true);", share_btn)
            time.sleep(1)
            share_btn.click()
        except:
            try:
                driver.execute_script("arguments[0].click();", share_btn)
            except:
                raise

        # Step 10: Wait for confirmation
        try:
            WebDriverWait(driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, "//h3[text()='Your post has been shared.']"))
            )
            success = True
        except:
            try:
                driver.save_screenshot("upload_maybe_failed.png")
            except:
                pass

    except:
        try:
            driver.save_screenshot("error_instagram_upload.png")
        except:
            pass
        success = False

    finally:
        for path in downloaded_paths:
            try:
                os.remove(path)
            except:
                pass
        driver.quit()
        return success


def _download_and_save(image_url: str) -> str:
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        ext = ".jpg"
        filename = os.path.join(os.getcwd(), f"{uuid.uuid4()}{ext}")
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    except Exception as e:
        raise RuntimeError(f"❌ Failed to download image from URL: {e}")
