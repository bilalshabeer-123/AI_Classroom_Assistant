import streamlit as st
from groq import Groq
import tempfile
import os

st.set_page_config(page_title="AI Lecture Notes Generator", layout="wide")

# ---------------- 🎨 UI Styling ----------------
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f7fb;
            color: #000000;
        }

        html, body, [class*="css"] {
            color: #000000 !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
        }

        p, label, span, div {
            color: #000000 !important;
        }

        .stButton>button {
            background-color: #4CAF50;
            color: white !important;
            border-radius: 8px;
        }

        .stFileUploader {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- 🔑 LOAD API KEY SAFELY ----------------
def get_api_key():
    # Try Streamlit secrets
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]

    # Fallback (optional, for local testing)
    if os.getenv("GROQ_API_KEY"):
        return os.getenv("GROQ_API_KEY")

    return None

GROQ_API_KEY = get_api_key()

# ---------------- App Title ----------------
st.title("🎓 AI Lecture Notes Generator")
st.write("Upload audio → Transcribe → Summarize → Generate Smart Notes")

# ---------------- ERROR HANDLING ----------------
if not GROQ_API_KEY:
    st.error("""
❌ Groq API key not found.

👉 Fix:
1. Create folder: `.streamlit`
2. Inside it create: `secrets.toml`
3. Add this:

GROQ_API_KEY = "your_actual_key"
""")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ---------------- Upload ----------------
uploaded_file = st.file_uploader("Upload Lecture Audio", type=["mp3", "wav", "m4a"])

if uploaded_file:

    st.audio(uploaded_file)

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    if st.button("🚀 Generate Notes"):

        # ---------- TRANSCRIBE ----------
        with st.spinner("Transcribing..."):
            try:
                with open(temp_path, "rb") as audio:
                    transcription = client.audio.transcriptions.create(
                        file=audio,
                        model="whisper-large-v3"
                    )
                transcript = transcription.text
            except Exception as e:
                st.error(f"Transcription Error: {e}")
                st.stop()

        st.subheader("📝 Transcript")
        st.write(transcript)

        # ---------- SUMMARY ----------
        with st.spinner("Summarizing..."):
            try:
                summary = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{
                        "role": "user",
                        "content": f"Summarize this lecture clearly:\n{transcript}"
                    }]
                )
                summary_text = summary.choices[0].message.content
            except Exception as e:
                st.error(f"Summary Error: {e}")
                st.stop()

        st.subheader("📌 Summary")
        st.write(summary_text)

        # ---------- SMART NOTES ----------
        with st.spinner("Generating Notes..."):
            try:
                notes = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{
                        "role": "user",
                        "content": f"""
Create structured lecture notes:

- Headings
- Bullet points
- Key concepts
- Definitions

Lecture:
{transcript}
"""
                    }]
                )
                notes_text = notes.choices[0].message.content
            except Exception as e:
                st.error(f"Notes Error: {e}")
                st.stop()

        st.subheader("📚 Smart Notes")
        st.write(notes_text)

        st.success("✅ Completed!")