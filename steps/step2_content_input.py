import streamlit as st
from PIL import Image, UnidentifiedImageError
from utils.uploader import upload_to_imgbb
from yt_dlp import YoutubeDL
import os

def content_input(content_context):
    st.markdown("## 🎯 Step 2: Provide Your Content")

    # Initialize session state
    st.session_state.setdefault("input_locked", None)
    st.session_state.setdefault("content_context_cache", {})

    option = st.radio("Select content input type:", ("📹 Paste YouTube Link", "🖼️ Upload Image"))

    # === YOUTUBE INPUT ===
    if option == "📹 Paste YouTube Link":
        if st.session_state.input_locked == "image":
            st.warning("🛑 You've already uploaded an image. Please refresh the page to start over.")
            return

        yt_url = st.text_input("Enter YouTube URL (e.g., https://www.youtube.com/watch?v=...)")

        if yt_url:
            if "youtube.com/watch?v=" not in yt_url:
                st.warning("⚠️ Please enter a valid YouTube URL.")
            else:
                try:
                    ydl_opts = {
                        "quiet": True,
                        "skip_download": True,
                        "no_warnings": True
                    }
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(yt_url, download=False)
                        title = info.get("title", "Untitled")
                        description = info.get("description", "")
                        thumbnail = info.get("thumbnail", "")

                        st.video(yt_url)
                        st.success("✅ Video processed successfully")
                        st.markdown(f"**Title:** {title}")
                        st.markdown(f"**Description:** {description[:300]}...")

                        if thumbnail:
                            st.image(thumbnail, caption="Thumbnail Preview")

                        st.session_state.input_locked = "video"
                        ctx = {
                            "type": "video",
                            "title": title,
                            "description": description,
                            "video_url": yt_url
                        }
                        content_context.update(ctx)
                        st.session_state.content_context_cache = ctx

                except Exception as e:
                    st.error(f"❌ Error processing video: {e}")

    # === IMAGE INPUT ===
    elif option == "🖼️ Upload Image":
        if st.session_state.input_locked == "video":
            st.warning("🛑 You've already pasted a YouTube link. Please refresh the page to start over.")
            return

        uploaded_image = st.file_uploader(
            "Upload a single image (Max 16MB)",
            type=["jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff"],
            accept_multiple_files=False,
            key="image_uploader"
        )

        st.session_state.setdefault("uploaded_filenames", [])
        st.session_state.setdefault("uploaded_urls", [])

        if uploaded_image:
            if st.session_state.uploaded_urls:
                st.warning("⚠️ Only one image can be uploaded.")
            else:
                try:
                    image = Image.open(uploaded_image)
                    st.image(image, caption=uploaded_image.name, use_container_width=True)

                    url = upload_to_imgbb(uploaded_image)
                    st.session_state.uploaded_filenames.append(uploaded_image.name)
                    st.session_state.uploaded_urls.append(url)
                    st.success(f"✅ Image '{uploaded_image.name}' uploaded successfully")

                    temp_dir = os.path.abspath("temp_uploads")
                    os.makedirs(temp_dir, exist_ok=True)
                    local_path = os.path.join(temp_dir, uploaded_image.name)
                    with open(local_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())

                    st.session_state.input_locked = "image"
                    ctx = {
                        "type": "image",
                        "uploaded_urls": st.session_state.uploaded_urls,
                        "local_image_path": local_path
                    }
                    content_context.update(ctx)
                    st.session_state.content_context_cache = ctx

                except UnidentifiedImageError:
                    st.error("❌ Unsupported or corrupted image file.")
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

        if st.session_state.uploaded_urls:
            st.markdown("### 📁 Uploaded Image:")
            for url in st.session_state.uploaded_urls:
                st.image(url, caption="Uploaded", use_container_width=True)

    # Restore cached context
    if not content_context and st.session_state.content_context_cache:
        content_context.update(st.session_state.content_context_cache)

    st.markdown("---")
