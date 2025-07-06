import streamlit as st
from utils.credential_handler import load_credentials, save_credentials

def enter_credentials(platforms):
    st.markdown("## 🔐 Step 5: Enter Platform Credentials")

    if not platforms:
        st.info("ℹ️ No platforms selected yet. Please complete **Step 4** first.")
        return

    # Load stored credentials from JSON (or empty)
    try:
        saved = load_credentials()
    except Exception as e:
        st.error(f"❌ Failed to load saved credentials: {e}")
        saved = {}

    for platform in platforms:
        platform_key = platform.lower()
        st.markdown(f"### 🔑 {platform} Credentials")

        with st.form(f"{platform_key}_form", clear_on_submit=False):
            username_key = f"{platform_key}_username"
            password_key = f"{platform_key}_password"

            default_username = saved.get(platform_key, {}).get("username", "")
            default_password = saved.get(platform_key, {}).get("password", "")

            username = st.text_input(f"{platform} Username", value=default_username, key=username_key)
            password = st.text_input(f"{platform} Password", value=default_password, type="password", key=password_key)

            submitted = st.form_submit_button("✅ Done")

            if submitted:
                if not username or not password:
                    st.warning("⚠️ Both fields are required.")
                else:
                    saved[platform_key] = {
                        "username": username,
                        "password": password
                    }
                    if save_credentials(saved):
                        st.success(f"✅ {platform} credentials saved.")
                    else:
                        st.error(f"❌ Failed to save {platform} credentials.")

    st.markdown("---")
