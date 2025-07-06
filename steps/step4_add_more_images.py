import streamlit as st

def add_more_images(content_context):
    """
    Step 4 (Optional): Upload more images without generating captions or alt text.
    Only visible when content type is 'image'.
    """
    if content_context.get("type") != "image":
        return  # Only applicable for image posts

    st.markdown("## 🖼️ Step 4 (Optional): Add More Images")

    # Initialize session key
    st.session_state.setdefault("additional_images", [])

    # File uploader
    more_images = st.file_uploader(
        "🧩 Upload additional image(s) for posting (no caption/alt text will be generated)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="additional_image_uploader"
    )

    # Store only new images
    if more_images:
        for img in more_images:
            existing_names = [existing.name for existing in st.session_state.additional_images]
            if img.name not in existing_names:
                st.session_state.additional_images.append(img)

    # Show previews
    if st.session_state.additional_images:
        st.markdown("### 📸 Additional Uploaded Images:")
        for img in st.session_state.additional_images:
            st.image(img, caption=img.name, use_container_width=True)

    st.markdown("---")
