import streamlit as st
from steps.step1_welcome import show_welcome
from steps.step2_content_input import content_input
from steps.step3_generate_caption import generate_caption
from steps.step4_add_more_images import add_more_images
from steps.step5_platform_select import select_platforms
from steps.step6_credentials import enter_credentials
from steps.step7_upload_post import upload_post
from utils.credential_handler import load_credentials

# ---------------------
# 🔧 Page Configuration
# ---------------------
st.set_page_config(
    page_title="LinkToPost",
    page_icon="🔗",
    layout="centered"
)

# ---------------------
# 🧠 App Header
# ---------------------
st.title("🔗 LinkToPost")
st.markdown("### AI-powered automation for social media uploads")
st.markdown("---")

# ---------------------
# 🔄 Shared Content Context
# ---------------------
content_context = {}

# ---------------------
# 🪜 Step-by-Step Workflow
# ---------------------
show_welcome()

# Step 2: Input content (video/image)
content_input(content_context)

# Step 3: Generate captions from AI
generate_caption(content_context)

# Step 4: Add more images (only for image-type content)
if content_context.get("type") == "image":
    add_more_images(content_context)

# Step 5: Select platforms
platforms = select_platforms()

# Step 6: Enter credentials
enter_credentials(platforms)

# Step 7: Upload post to selected platforms
if platforms:
    credentials = load_credentials()
    upload_post(content_context, platforms, credentials)

# ---------------------
# 📎 Footer
# ---------------------
st.markdown("---")
st.markdown("**LinkToPost** | Powered by **Streamlit**, **HuggingFace**, **ImgBB**, and **Selenium**")
