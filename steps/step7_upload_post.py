import streamlit as st
import os
import threading
from steps.Step7.instagram_uploader import upload_to_instagram
from steps.Step7.facebook_uploader import upload_to_facebook
from steps.Step7.facebook_image_uploader import upload_image_to_facebook


def upload_post(content_context: dict, platforms: list[str], credentials: dict) -> None:
    st.markdown("## 🚀 Step 6: Upload Post to Selected Platforms")

    if not platforms:
        st.warning("⚠️ Please select at least one platform.")
        return
    if not credentials:
        st.warning("⚠️ Missing login credentials. Please complete Step 5.")
        return

    content_type = content_context.get("type")

    st.markdown("### 📤 Content Preview")
    st.markdown("---")

    if content_type == "image":
        uploaded_urls = content_context.get("uploaded_urls", [])
        additional_images = st.session_state.get("additional_images", [])
        additional_urls = []

        st.image(uploaded_urls[0], caption="Primary Image", use_container_width=True)
        for img in additional_images:
            if hasattr(img, "getvalue"):
                st.image(img, caption=img.name, use_container_width=True)

        caption = st.session_state.get(uploaded_urls[0], {}).get("caption_editable", "")
        st.markdown(f"**📝 Caption:** {caption}")
        st.markdown("---")

        if st.button("🚀 Start Upload"):
            threads = []
            results = {}

            def instagram_upload():
                st.info("📷 Uploading to Instagram...")
                try:
                    all_urls = uploaded_urls.copy()
                    for img in additional_images:
                        img_url = _upload_temp_to_imgbb(img)
                        all_urls.append(img_url)

                    success = upload_to_instagram(
                        username=credentials["instagram"]["username"],
                        password=credentials["instagram"]["password"],
                        image_urls=all_urls,
                        caption=caption
                    )
                    results["instagram"] = success
                except Exception as e:
                    st.error(f"❌ Instagram upload error: {e}")
                    results["instagram"] = False

            def facebook_upload():
                st.info("📘 Uploading to Facebook...")
                try:
                    local_path = content_context.get("local_image_path")
                    if not local_path or not os.path.exists(local_path):
                        raise FileNotFoundError("Local image file not found.")

                    success = upload_image_to_facebook(
                        image_path=local_path,
                        caption=caption,
                        username=credentials["facebook"]["username"],
                        password=credentials["facebook"]["password"]
                    )
                    results["facebook"] = success
                except Exception as e:
                    st.error(f"❌ Facebook upload error: {e}")
                    results["facebook"] = False

            if "instagram" in [p.lower() for p in platforms]:
                t = threading.Thread(target=instagram_upload)
                threads.append(t)
                t.start()

            if "facebook" in [p.lower() for p in platforms]:
                t = threading.Thread(target=facebook_upload)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            for platform in ["instagram", "facebook"]:
                if platform in results:
                    if results[platform]:
                        st.success(f"✅ Uploaded successfully to {platform.capitalize()}")
                    else:
                        st.error(f"❌ Failed to upload to {platform.capitalize()}")

    elif content_type == "video":
        video_path = content_context.get("video_path")
        video_url = content_context.get("video_url", "")
        caption = st.session_state.get("video_caption_editable", content_context.get("description", ""))

        if video_path:
            st.video(video_path)
        elif video_url:
            st.video(video_url)

        st.markdown(f"**📝 Caption:** {caption}")
        st.markdown("---")

        if st.button("🚀 Start Upload"):
            for platform in platforms:
                creds = credentials.get(platform.lower(), {})
                username = creds.get("username")
                password = creds.get("password")

                if not username or not password:
                    st.error(f"❌ Missing credentials for {platform}")
                    continue

                st.info(f"⏫ Uploading video to {platform}...")

                if platform.lower() == "instagram":
                    success = upload_to_instagram(
                        username=username,
                        password=password,
                        image_urls=[],
                        caption=caption,
                        video_path=video_path
                    )
                    if success:
                        st.success("✅ Video uploaded to Instagram successfully!")
                    else:
                        st.error("❌ Failed to upload video to Instagram.")

                elif platform.lower() == "facebook":
                    if not video_url:
                        st.error("❌ YouTube video URL missing for Facebook upload.")
                        continue

                    success = upload_to_facebook(
                        video_url=video_url,
                        caption=caption,
                        username=username,
                        password=password
                    )
                    if success:
                        st.success("✅ Video shared on Facebook successfully!")
                    else:
                        st.error("❌ Failed to share video on Facebook.")

                else:
                    st.warning(f"⚠️ Upload to {platform} not implemented yet.")

    else:
        st.error("❌ Unsupported content type.")
        return


def _upload_temp_to_imgbb(file) -> str:
    """Securely uploads a temporary in-memory file to ImgBB."""
    import requests
    import base64
    from PIL import Image
    from io import BytesIO

    API_KEY = os.getenv("IMGBB_API_KEY", "")
    if not API_KEY:
        raise Exception("❌ ImgBB API Key not set.")

    try:
        image = Image.open(file)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        encoded = base64.b64encode(buffered.getvalue()).decode()

        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": API_KEY,
                "image": encoded,
                "name": file.name
            }
        )
        if response.status_code == 200:
            return response.json()["data"]["url"]
        else:
            raise Exception(f"Upload failed: {response.text}")
    except Exception as e:
        raise Exception(f"❌ Failed to upload image to ImgBB: {e}")
