import streamlit as st
from utils.caption_generator import (
    generate_emotional_caption,
    get_detailed_image_description,
    generate_caption_from_text,
    generate_hashtags,
    generate_alt_text,
)


def generate_caption(content_context):
    st.markdown("## ✍️ Step 3: AI Caption Generator")

    st.session_state.setdefault("caption_tone", "Emotional")
    st.session_state.setdefault("caption_persona", "Lifestyle Influencer")

    tone = st.selectbox(
        "💫 Select Caption Tone",
        ["Emotional", "Luxury", "Minimal", "Bold", "Inspirational"],
        index=["Emotional", "Luxury", "Minimal", "Bold", "Inspirational"].index(st.session_state.caption_tone),
        key="tone_select"
    )

    persona = st.selectbox(
        "🧠 Select Caption Persona",
        ["Lifestyle Influencer", "Photographer", "Motivational Coach", "Minimalist Creator"],
        index=["Lifestyle Influencer", "Photographer", "Motivational Coach", "Minimalist Creator"].index(st.session_state.caption_persona),
        key="persona_select"
    )

    st.session_state.caption_tone = tone
    st.session_state.caption_persona = persona
    st.markdown("---")

    # === VIDEO CAPTION ===
    if content_context.get("type") == "video":
        title = content_context.get("title", "")
        desc = content_context.get("description", "")

        if "video_caption" not in st.session_state:
            with st.spinner("🧠 Generating video caption..."):
                cap = generate_caption_from_text(title, desc, tone=tone, persona=persona)
            st.session_state.video_caption = cap
            st.session_state.video_caption_editable = cap
            st.session_state.video_caption_edit_mode = False
            st.session_state.video_hashtags = ""
            st.session_state.video_hashtags_editable = ""
            st.session_state.video_hashtags_edit_mode = False

        st.subheader("🎥 Video Caption")

        if st.button("✏️ Edit Video Caption"):
            st.session_state.video_caption_edit_mode = not st.session_state.video_caption_edit_mode

        if st.session_state.video_caption_edit_mode:
            st.session_state.video_caption_editable = st.text_area(
                "📝 Edit Caption", st.session_state.video_caption_editable, height=100
            )
        else:
            st.text_area("✨ Caption", st.session_state.video_caption_editable, height=100, disabled=True)

        if st.button("🔁 Regenerate Video Caption"):
            with st.spinner("🔁 Re-generating..."):
                cap = generate_caption_from_text(title, desc, tone=tone, persona=persona)
                st.session_state.video_caption = cap
                st.session_state.video_caption_editable = cap
                st.session_state.video_caption_edit_mode = False

        st.subheader("🏷️ Video Hashtags")
        if st.button("Generate Hashtags"):
            with st.spinner("📌 Generating hashtags..."):
                tags = generate_hashtags(desc)
                st.session_state.video_hashtags = tags
                st.session_state.video_hashtags_editable = tags

        if st.button("✏️ Edit Video Hashtags"):
            st.session_state.video_hashtags_edit_mode = not st.session_state.video_hashtags_edit_mode

        if st.session_state.video_hashtags_edit_mode:
            st.session_state.video_hashtags_editable = st.text_area("📝 Edit Hashtags", st.session_state.video_hashtags_editable, height=70)
        else:
            st.text_area("📌 Hashtags", st.session_state.video_hashtags_editable, height=70, disabled=True)

    # === IMAGE CAPTION ===
    elif content_context.get("type") == "image":
        for idx, url in enumerate(content_context.get("uploaded_urls", [])):
            entry = st.session_state.get(url, {
                "caption": None, "caption_editable": "", "caption_edit_mode": False,
                "hashtags": "", "hashtags_editable": "", "hashtags_edit_mode": False,
                "alt_text": "", "alt_text_editable": "", "alt_text_edit_mode": False
            })

            if entry["caption"] is None:
                try:
                    with st.spinner("🔍 Understanding image..."):
                        desc = get_detailed_image_description(url)
                    with st.spinner("✍️ Generating caption..."):
                        cap = generate_emotional_caption(desc, tone=tone, persona=persona)
                    entry["caption"] = cap
                    entry["caption_editable"] = cap
                except Exception as e:
                    st.error(f"❌ Failed to generate caption: {e}")
                    continue

            st.session_state[url] = entry

            st.markdown(f"### 🖼️ Image {idx + 1}")
            with st.expander("📝 Caption, Hashtags & Alt Text"):

                # Caption
                if st.button(f"✏️ Edit Caption for Image {idx + 1}", key=f"cap_edit_{url}"):
                    entry["caption_edit_mode"] = not entry["caption_edit_mode"]
                    st.session_state[url] = entry

                if entry["caption_edit_mode"]:
                    entry["caption_editable"] = st.text_area("📝 Edit Caption", entry["caption_editable"], key=f"cap_input_{url}", height=100)
                else:
                    st.text_area("✨ Caption", entry["caption_editable"], key=f"cap_display_{url}", height=100, disabled=True)

                if st.button(f"🔁 Regenerate Caption", key=f"regen_{url}"):
                    with st.spinner("♻️ Re-generating caption..."):
                        try:
                            desc = get_detailed_image_description(url)
                            new_cap = generate_emotional_caption(desc, tone=tone, persona=persona)
                            entry["caption"] = new_cap
                            entry["caption_editable"] = new_cap
                            entry["caption_edit_mode"] = False
                        except Exception as e:
                            st.error(f"❌ Caption regeneration failed: {e}")
                    st.session_state[url] = entry

                # Hashtags
                if st.button(f"🏷️ Generate Hashtags", key=f"hashtag_gen_{url}"):
                    with st.spinner("📌 Generating hashtags..."):
                        try:
                            tags = generate_hashtags(entry["caption_editable"])
                            entry["hashtags"] = tags
                            entry["hashtags_editable"] = tags
                        except Exception as e:
                            st.error(f"❌ Failed to generate hashtags: {e}")
                    st.session_state[url] = entry

                if st.button(f"✏️ Edit Hashtags", key=f"hashtag_edit_{url}"):
                    entry["hashtags_edit_mode"] = not entry["hashtags_edit_mode"]
                    st.session_state[url] = entry

                if entry["hashtags_edit_mode"]:
                    entry["hashtags_editable"] = st.text_area("📝 Edit Hashtags", entry["hashtags_editable"], key=f"hashtags_input_{url}", height=70)
                else:
                    st.text_area("🏷️ Hashtags", entry["hashtags_editable"], key=f"hashtags_display_{url}", height=70, disabled=True)

                # Alt Text
                if st.button(f"🔊 Generate Alt Text", key=f"alt_gen_{url}"):
                    with st.spinner("📢 Generating alt text..."):
                        try:
                            alt = generate_alt_text(entry["caption_editable"])
                            entry["alt_text"] = alt
                            entry["alt_text_editable"] = alt
                        except Exception as e:
                            st.error(f"❌ Failed to generate alt text: {e}")
                    st.session_state[url] = entry

                if st.button(f"✏️ Edit Alt Text", key=f"alt_edit_{url}"):
                    entry["alt_text_edit_mode"] = not entry["alt_text_edit_mode"]
                    st.session_state[url] = entry

                if entry["alt_text_edit_mode"]:
                    entry["alt_text_editable"] = st.text_area("📝 Edit Alt Text", entry["alt_text_editable"], key=f"alt_input_{url}", height=70)
                else:
                    st.text_area("📢 Alt Text", entry["alt_text_editable"], key=f"alt_display_{url}", height=70, disabled=True)

    st.markdown("---")
