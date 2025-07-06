import streamlit as st

def select_platforms():
    st.markdown("## 🛰️ Step 4: Choose Platforms to Post")

    # Detect content type from cached context
    content_ctx = st.session_state.get("content_context_cache", {})
    content_type = content_ctx.get("type", "")
    local_image_path = content_ctx.get("local_image_path", "")
    is_video = content_type == "video"
    is_uploaded_image = content_type == "image" and bool(local_image_path)

    # Initialize session state
    st.session_state.setdefault("selected_platforms", [])
    selected_platforms = st.session_state.selected_platforms

    try:
        with st.form("platform_form"):
            platform_options = []
            disabled_options = []

            # === Logic for platform availability ===
            if is_video:
                # Only Facebook is supported for video (YouTube)
                st.info("🎥 YouTube video detected. Instagram posting is disabled for videos.")
                platform_options = ["Facebook"]
                disabled_options = []
            elif is_uploaded_image:
                # Facebook posting for local images is not yet implemented
                st.warning("⚠️ Facebook posting for uploaded images is 🛠️ **under construction**.")
                platform_options = ["Instagram", "Facebook"]
                disabled_options = ["Facebook"]
            else:
                # Default case — both options available
                platform_options = ["Facebook", "Instagram"]
                disabled_options = []

            # Only keep selections that are still valid
            default_selection = [
                p for p in selected_platforms if p in platform_options and p not in disabled_options
            ]

            # Show multi-select with disable logic
            platforms = st.multiselect(
                "📱 Select platform(s) for posting:",
                options=platform_options,
                default=default_selection,
                help="Choose the platforms where your content will be posted.",
                disabled=[p in disabled_options for p in platform_options]
            )

            submitted = st.form_submit_button("✅ Save Platform Selection")

            if submitted:
                if platforms:
                    st.session_state.selected_platforms = platforms
                    st.success(f"✅ Platforms saved: {', '.join(platforms)}")
                else:
                    st.warning("⚠️ Please select at least one platform to continue.")

    except Exception as e:
        st.error(f"❌ An error occurred while selecting platforms: {e}")

    # Display final selection (summary)
    if st.session_state.selected_platforms:
        st.info(f"📌 Current Selection: {', '.join(st.session_state.selected_platforms)}")

    st.markdown("---")
    return st.session_state.selected_platforms
