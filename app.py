import streamlit as st
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import random
import os
import tempfile
from pathlib import Path

# ==========================================
# 1. Authentication System
# ==========================================
USER_DB = {
    "admin": "admin123",
    "user1": "pass1",
    "user2": "pass2",
    "user3": "pass3",
    "user4": "pass4",
    "user5": "pass5",
    "user6": "pass6",
    "user7": "pass7",
    "user8": "pass8",
    "user9": "pass9",
    "user10": "pass10",
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Pro Trending Reels Builder Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username in USER_DB and USER_DB[username] == password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        return False
    return True

# ==========================================
# 2. Video Processing Logic
# ==========================================
def process_reel(bg_video_path, bg_audio_path, quote_text, use_shield):
    try:
        # Load Video
        clip = mp.VideoFileClip(bg_video_path)
        
        # --- 3. Anti-Copyright & Uniqueifier Logic ---
        if use_shield:
            # Random speed variation (1.02x to 1.04x)
            speed_factor = random.uniform(1.02, 1.04)
            clip = clip.fx(vfx.speedx, speed_factor)
            
            # Random color/contrast adjustment (0.95 to 1.05)
            color_factor = random.uniform(0.95, 1.05)
            clip = clip.fx(vfx.colorx, color_factor)

        # --- 4. Video Formatting (9:16 Full HD) ---
        target_w, target_h = 1080, 1920
        target_aspect = target_w / target_h
        
        curr_w, curr_h = clip.size
        curr_aspect = curr_w / curr_h
        
        if curr_aspect > target_aspect:
            # Too wide: Crop width
            new_w = curr_h * target_aspect
            clip = clip.crop(x_center=curr_w/2, width=new_w)
        elif curr_aspect < target_aspect:
            # Too tall: Crop height
            new_h = curr_w / target_aspect
            clip = clip.crop(y_center=curr_h/2, height=new_h)
            
        clip = clip.resize(newsize=(target_w, target_h))

        # Handle Audio
        if bg_audio_path:
            audio = mp.AudioFileClip(bg_audio_path)
            # Loop or trim audio to match clip duration
            if audio.duration > clip.duration:
                audio = audio.subclip(0, clip.duration)
            else:
                audio = audio.fx(vfx.loop, duration=clip.duration)
            clip = clip.set_audio(audio)
        
        # Text Overlay
        if quote_text:
            # Using method='caption' for automatic wrapping
            txt_clip = mp.TextClip(
                quote_text,
                fontsize=85,
                color='white',
                font='Liberation-Sans-Bold',
                stroke_color='black',
                stroke_width=3,
                method='caption',
                size=(950, None) 
            ).set_duration(clip.duration).set_position('center')
            
            clip = mp.CompositeVideoClip([clip, txt_clip])

        # --- 5. High Performance Export ---
        output_path = os.path.join(tempfile.gettempdir(), f"reel_{random.randint(1000,9999)}.mp4")
        
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            bitrate="8000k",
            preset="fast",
            threads=4,
            fps=30,
            logger=None
        )
        
        # Close clips to release memory/files
        clip.close()
        if bg_audio_path:
            mp.AudioFileClip(bg_audio_path).close()
            
        return output_path

    except Exception as e:
        st.error(f"Processing Error: {str(e)}")
        return None

# ==========================================
# 3. Main Application UI
# ==========================================
def main():
    if not check_password():
        return

    st.title("🎬 Pro Trending Reels Builder")
    st.markdown("Generate high-quality, unique 9:16 reels for Instagram and YouTube.")

    with st.sidebar:
        st.header("Settings")
        use_shield = st.checkbox("Enable Anti-Copyright Shield", value=True, help="Alters speed and color to make video unique.")
        st.info("All videos are exported in Full HD (1080x1920).")

    col1, col2 = st.columns(2)
    with col1:
        video_file = st.file_uploader("Upload Background Video (.mp4)", type=["mp4"])
    with col2:
        audio_file = st.file_uploader("Upload Background Audio (.mp3)", type=["mp3"])

    quote_text = st.text_area("Enter Quote or Fact", placeholder="Example: The Earth is 4.5 billion years old!")

    if st.button("🚀 Generate Full HD Reel"):
        if video_file is not None:
            with st.spinner("Processing your Reel... This may take up to 2 minutes."):
                # Save uploaded files to temp disk
                t_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                t_video.write(video_file.read())
                t_video.close()

                t_audio = None
                if audio_file:
                    t_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    t_audio.write(audio_file.read())
                    t_audio.close()

                result_path = process_reel(t_video.name, t_audio.name if t_audio else None, quote_text, use_shield)

                # Cleanup temp inputs
                os.unlink(t_video.name)
                if t_audio:
                    os.unlink(t_audio.name)

                if result_path:
                    st.success("Reel Generated Successfully!")
                    
                    # Video Preview
                    with open(result_path, "rb") as f:
                        st.video(f.read())
                    
                    # Download Button
                    with open(result_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Full HD Reel",
                            data=f,
                            file_name="trending_reel.mp4",
                            mime="video/mp4"
                        )
                    
                    # Final Cleanup
                    os.unlink(result_path)
        else:
            st.warning("Please upload a background video first!")

if __name__ == "__main__":
    main()
