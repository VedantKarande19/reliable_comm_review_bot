# """
# Reliable Communication Call Rating Desk
# Upload Call Audio & Custom Markdown Evaluation Rubrics to run complete automated QA audits.
# """

# from __future__ import annotations

# import html
# import json
# import os
# import re
# import tempfile
# from pathlib import Path

# import streamlit as st
# from groq import APIStatusError, Groq

# from aligned_transcript import _load_dotenv
# from call_audio_pipeline import process_call_recording

# SCRIPT_DIR = Path(__file__).resolve().parent
# DEFAULT_RUBRIC_PATH = SCRIPT_DIR / "TVS_3wheeler_call_qa_rubric.md"

# CRITERION_LABELS: dict[str, str] = {
#     "1.1": "Greeting & identity",
#     "1.2": "Purpose & consent",
#     "1.3": "Callback handling",
#     "1.4": "Not interested path",
#     "2.1": "Customer details",
#     "2.2": "Buying intent & lead tag",
#     "2.3": "Product / scheme pitch",
#     "2.4": "MH eligibility & documents",
#     "2.5": "Closing",
#     "3.1": "Follow-up script",
#     "3.2": "Enquiry in progress (E1–E5)",
# }


# def init_page_styles():
#     """
#     Sets up page layout and explicitly overrides Streamlit theme structures.
#     Locks colors into a professional corporate scheme to prevent system appearance mode shifts.
#     """
#     st.set_page_config(
#         page_title="Reliable Communication | Professional QA Audit Desk",
#         page_icon="📞",
#         layout="wide",
#     )

#     # Hard-locked appearance CSS configuration (Bypasses dark/light mode shifts entirely)
#     locked_theme_css = """
#     <style>
#         /* Force Root Streamlit Variables to remain fixed in Corporate Light Palette */
#         :root, [data-theme="light"], [data-theme="dark"], .stApp {
#             --primary-color: #328CC1 !important;
#             --background-color: #F4F6F9 !important;
#             --secondary-background-color: #FFFFFF !important;
#             --text-color: #0F172A !important;
#         }

#         /* Main Workspace Canvas Override */
#         html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"], .stApp {
#             background-color: #F4F6F9 !important;
#             color: #0F172A !important;
#         }

#         /* Prevent system dark mode from flipping text color in the workspace */
#         [data-testid="stAppViewContainer"] p,
#         [data-testid="stAppViewContainer"] label,
#         [data-testid="stAppViewContainer"] span,
#         [data-testid="stAppViewContainer"] h1,
#         [data-testid="stAppViewContainer"] h2,
#         [data-testid="stAppViewContainer"] h3,
#         [data-testid="stAppViewContainer"] h4,
#         [data-testid="stAppViewContainer"] h5,
#         [data-testid="stAppViewContainer"] div {
#             color: #0F172A !important;
#         }

#         /* Lock Sidebar Panel to Corporate Deep Navy Accent */
#         [data-testid="stSidebar"], 
#         [data-testid="stSidebarUserContent"], 
#         [data-testid="stSidebarNav"],
#         [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
#             background-color: #0F294A !important;
#             color: #FFFFFF !important;
#         }

#         /* Enforce high-visibility white text for all sidebar elements regardless of theme setting */
#         [data-testid="stSidebar"] p, 
#         [data-testid="stSidebar"] label, 
#         [data-testid="stSidebar"] span, 
#         [data-testid="stSidebar"] h1, 
#         [data-testid="stSidebar"] h2, 
#         [data-testid="stSidebar"] h3,
#         [data-testid="stSidebar"] h4,
#         [data-testid="stSidebar"] div,
#         [data-testid="stSidebar"] small {
#             color: #FFFFFF !important;
#         }

#         /* Form elements and file uploaders container normalization */
#         [data-testid="stSidebar"] section[role="dialog"] {
#             background-color: #16365C !important;
#             border: 1px dashed #328CC1 !important;
#         }

#         /* Form input fields & textareas formatting control */
#         textarea, .stTextArea textarea, div[role="textbox"], input {
#             background-color: #FFFFFF !important;
#             color: #0F172A !important;
#             border: 1px solid #CBD5E1 !important;
#             -webkit-text-fill-color: #0F172A !important;
#         }

#         /* Specifically force disabled textareas to retain readability */
#         textarea:disabled, .stTextArea textarea:disabled {
#             background-color: #FFFFFF !important;
#             color: #0F172A !important;
#             -webkit-text-fill-color: #0F172A !important;
#             opacity: 1 !important;
#         }

#         /* Branding Typography */
#         .brand-header {
#             font-size: 2.2rem;
#             font-weight: 800;
#             color: #0F294A !important;
#             margin-top: -10px;
#             margin-bottom: 0px;
#             letter-spacing: -0.5px;
#         }
        
#         .brand-sub {
#             font-size: 1.05rem;
#             color: #475569 !important;
#             font-weight: 500;
#             margin-bottom: 25px;
#         }

#         .section-title {
#             font-size: 1.25rem;
#             font-weight: 700;
#             color: #0F294A !important;
#             margin-bottom: 12px;
#             border-bottom: 2px solid #E2E8F0;
#             padding-bottom: 6px;
#         }

#         /* Premium Standard Metric Scorecard Elements */
#         .metric-card {
#             background-color: #FFFFFF !important;
#             border-left: 4px solid #328CC1 !important;
#             border-top: 1px solid #E2E8F0 !important;
#             border-right: 1px solid #E2E8F0 !important;
#             border-bottom: 1px solid #E2E8F0 !important;
#             padding: 14px 16px;
#             border-radius: 6px;
#             margin-bottom: 12px;
#             box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
#             color: #0F172A !important;
#         }
        
#         .metric-card * {
#             color: #0F172A !important;
#         }

#         /* Extracted Transcript Window Styles */
#         .transcript-box {
#             background-color: #FFFFFF !important;
#             color: #0F172A !important;
#             border: 1px solid #CBD5E1 !important;
#             padding: 16px;
#             border-radius: 6px;
#             font-size: 0.95rem;
#             line-height: 1.6;
#             max-height: 650px;
#             overflow-y: auto;
#         }
#     </style>
#     """
#     st.markdown(locked_theme_css, unsafe_allow_html=True)


# def load_active_rubric(uploaded_file) -> str:
#     """Loads text from either an uploaded custom rubric file or the local default fallback."""
#     if uploaded_file is not None:
#         try:
#             return uploaded_file.read().decode("utf-8")
#         except Exception as e:
#             st.sidebar.error(f"Error reading uploaded rubric: {e}")
#             return ""
            
#     if DEFAULT_RUBRIC_PATH.is_file():
#         return DEFAULT_RUBRIC_PATH.read_text(encoding="utf-8")
#     return ""


# def parse_llm_json(raw_text: str) -> dict | None:
#     cleaned = raw_text.strip()
#     match = re.search(r"\{.*\}", cleaned, re.DOTALL)
#     if match:
#         cleaned = match.group(0)
#     try:
#         return json.loads(cleaned)
#     except Exception:
#         return None


# def run_qa_scoring(transcript: str, rubric_text: str) -> dict | None:
#     groq_key = os.getenv("GROQ_API_KEY") or st.session_state.get("GROQ_API_KEY")
#     if not groq_key:
#         st.error("GROQ_API_KEY is missing. Configure it in your environment or sidebar configuration.")
#         return None

#     client = Groq(api_key=groq_key)
#     system_prompt = (
#         "You are an expert operational Quality Auditor for Reliable Communication. "
#         "Analyze the provided call transcript and evaluate performance based precisely on the instructions inside the rubric. "
#         "Return your evaluation strictly in valid JSON format adhering to this structure:\n"
#         "{\n"
#         '  "criteria": [\n'
#         '    {"criterion_id": "1.1", "stars": 5, "one_line_evidence": "...", "notes": "..."}\n'
#         "  ],\n"
#         '  "overall_call_quality_stars": 4,\n'
#         '  "top_strength": "...",\n'
#         '  "top_improvement_area": "..."\n'
#         "}"
#     )

#     user_content = f"--- TARGET EVALUATION RUBRIC ---\n{rubric_text}\n\n--- TARGET CALL TRANSCRIPT ---\n{transcript}"

#     try:
#         completion = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_content},
#             ],
#             temperature=0.1,
#             response_format={"type": "json_object"},
#         )
#         return parse_llm_json(completion.choices[0].message.content or "")
#     except APIStatusError as e:
#         st.error(f"Groq API Error: {e}")
#         return None


# def _render_rating_block(rating_data: dict):
#     overall = rating_data.get("overall_call_quality_stars", "N/A")
#     st.markdown(f"#### Overall Call Performance: **{overall} / 5 ⭐**")

#     c_str, c_imp = st.columns(2)
#     with c_str:
#         st.info(f"**Top Strength:**\n{rating_data.get('top_strength', 'None identified.')}")
#     with c_imp:
#         st.warning(f"**Area of Improvement:**\n{rating_data.get('top_improvement_area', 'None identified.')}")

#     st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

#     criteria_list = rating_data.get("criteria", [])
#     criteria_map = {str(item.get("criterion_id")): item for item in criteria_list if "criterion_id" in item}

#     for cid, label in CRITERION_LABELS.items():
#         item = criteria_map.get(cid)
#         if item:
#             stars = item.get("stars", "N/A")
#             evidence = item.get("one_line_evidence", "No direct quote cited.")
#             notes = item.get("notes", "")
            
#             notes_html = ""
#             if notes:
#                 notes_html = f"<div style='margin-top:2px; font-size:0.85rem; color:#64748B;'><b>Auditor Notes:</b> {html.escape(notes)}</div>"
            
#             st.markdown(
#                 f"<div class='metric-card'>"
#                 f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
#                 f"<strong>[{cid}] {label}</strong>"
#                 f"<span style='color:#328CC1; font-weight:700;'>{stars} ⭐</span>"
#                 f"</div>"
#                 f"<div style='margin-top:6px; font-size:0.88rem;'><b>Evidence:</b> <i>\"{html.escape(evidence)}\"</i></div>"
#                 f"{notes_html}"
#                 f"</div>",
#                 unsafe_allow_html=True
#             )
#         else:
#             st.markdown(
#                 f"<div class='metric-card' style='opacity: 0.55; border-left: 4px solid #CBD5E1;'>"
#                 f"<strong>[{cid}] {label}</strong> — <span style='color:#64748B;'>Not Applicable / Omitted</span>"
#                 f"</div>",
#                 unsafe_allow_html=True
#             )


# def main():
#     _load_dotenv(SCRIPT_DIR / ".env")
#     init_page_styles()

#     # Fixed App Workspace Branding
#     st.markdown('<div class="brand-header">Reliable Communication</div>', unsafe_allow_html=True)
#     st.markdown('<div class="brand-sub">Direct Sales & Call Operations — QA Performance Evaluation Desk</div>', unsafe_allow_html=True)

#     if "aligned_text" not in st.session_state:
#         st.session_state.aligned_text = ""
#     if "english_translation" not in st.session_state:
#         st.session_state.english_translation = ""
#     if "tvs_rating" not in st.session_state:
#         st.session_state.tvs_rating = None

#     # Sidebar Component Management Dashboard
#     with st.sidebar:
#         st.subheader("🔑 Authentication Details")
#         groq_env = os.getenv("GROQ_API_KEY", "")
#         if not groq_env:
#             groq_input = st.text_input("Groq API Key", type="password")
#             if groq_input:
#                 st.session_state["GROQ_API_KEY"] = groq_input

#         pyannote_env = os.getenv("PYANNOTE_API_KEY", "")
#         if not pyannote_env:
#             pyannote_input = st.text_input("Pyannote API Key", type="password")
#             if pyannote_input:
#                 st.session_state["PYANNOTE_API_KEY"] = pyannote_input

#         # FIX: Repositioned Media Intake Pipeline to be above the Custom Quality Rubric module
#         st.markdown("<hr style='margin:15px 0; border-color:#2B4C7E;'/>", unsafe_allow_html=True)
#         st.subheader("🎵 Media Intake Pipeline")
#         audio_file = st.file_uploader("Upload Call Audio Recording", type=["mp3", "wav", "m4a"])
#         process_btn = st.button("Process & Transcribe Audio", disabled=audio_file is None, use_container_width=True)

#         st.markdown("<hr style='margin:15px 0; border-color:#2B4C7E;'/>", unsafe_allow_html=True)
#         st.subheader("📑 Custom Quality Rubric")
#         uploaded_rubric = st.file_uploader(
#             "Upload Evaluation Rubric (.md)", 
#             type=["md"],
#             help="Upload custom evaluation scorecards. If blank, defaults to local template."
#         )

#         st.markdown("<hr style='margin:15px 0; border-color:#2B4C7E;'/>", unsafe_allow_html=True)
#         score_btn = st.button(
#             "Execute Quality Scorecard Audit", 
#             disabled=not st.session_state.aligned_text, 
#             use_container_width=True,
#             type="primary"
#         )

#     # Core Logic Pipeline Hook Execution 
#     if process_btn and audio_file:
#         with st.spinner("Processing timeline transcription alignments via pipeline..."):
#             try:
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.name).suffix) as tmp:
#                     tmp.write(audio_file.read())
#                     tmp_path = Path(tmp.name)

#                 result = process_call_recording(tmp_path)
                
#                 st.session_state.aligned_text = result.get("text", "")
#                 st.session_state.english_translation = result.get("english_translation", "")
#                 st.session_state.tvs_rating = None  # Reset historical reviews
#                 st.success("Audio analysis pipeline finished successfully!")
                
#                 try:
#                     os.unlink(tmp_path)
#                 except Exception:
#                     pass
#             except Exception as e:
#                 st.error(f"Processing Error Encountered: {e}")

#     if score_btn and st.session_state.aligned_text:
#         with st.spinner("Analyzing audio context against structural rubric benchmarks..."):
#             active_rubric_content = load_active_rubric(uploaded_rubric)
#             if not active_rubric_content:
#                 st.error("No valid rubric rules available. Please upload a .md template file.")
#             else:
#                 scores = run_qa_scoring(st.session_state.aligned_text, active_rubric_content)
#                 if scores:
#                     st.session_state.tvs_rating = scores
#                     st.success("Audit verification completed!")

#     # Layout Output Panels
#     if st.session_state.aligned_text:
#         col_transcript, col_scorecard = st.columns([1, 1], gap="large")

#         with col_transcript:
#             st.markdown('<div class="section-title">📝 Generated Conversational Transcript</div>', unsafe_allow_html=True)
#             st.text_area(
#                 "transcript",
#                 st.session_state.aligned_text,
#                 height=650,
#                 label_visibility="collapsed",
#                 disabled=True
#             )
#             if st.session_state.english_translation:
#                 with st.expander("View Consolidated English Translation Block"):
#                     st.markdown(
#                         '<div class="transcript-box">'
#                         + html.escape(st.session_state.english_translation).replace("\n", "<br/>")
#                         + "</div>",
#                         unsafe_allow_html=True,
#                     )

#         with col_scorecard:
#             st.markdown('<div class="section-title">🎯 Automated Performance Audit Scorecard</div>', unsafe_allow_html=True)
#             if not st.session_state.tvs_rating:
#                 st.info("Transcript ready. Press 'Execute Quality Scorecard Audit' in the setup panel to display findings.")
#             else:
#                 with st.container(height=650, border=True):
#                     _render_rating_block(st.session_state.tvs_rating)
                
#                 with st.expander("Raw Structural Model Output Data (JSON)"):
#                     st.code(json.dumps(st.session_state.tvs_rating, ensure_ascii=False, indent=2), language="json")
#     else:
#         # FIX: Replaced the blank start page with a polished corporate workflow landing view
#         st.markdown("""
#         <div style='background-color: #FFFFFF; padding: 35px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); margin-top: 5px;'>
#             <h3 style='color: #0F294A; margin-top: 0; font-weight: 700; font-size: 1.4rem;'>Quality Assurance Automated Workspace</h3>
#             <p style='color: #475569; font-size: 1rem; line-height: 1.5;'>
#                 Welcome to the operational rating desk. This platform allows you to evaluate agent conversation performance seamlessly against complex compliance matrices using direct audio pipeline analytics.
#             </p>
#             <hr style='border-color: #F1F5F9; margin: 25px 0;'/>
#             <h4 style='color: #0F294A; margin-bottom: 18px; font-weight: 600; font-size: 1.1rem;'>🚀 Operational Instructions Workflow:</h4>
#             <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;'>
#                 <div style='background-color: #F8FAFC; padding: 22px; border-radius: 6px; border-left: 4px solid #328CC1;'>
#                     <div style='font-weight: 800; color: #328CC1; font-size: 1.25rem; margin-bottom: 6px;'>01</div>
#                     <strong style='color: #0F294A; font-size: 0.95rem; display: block; margin-bottom: 4px;'>Media Intake Processing</strong>
#                     <p style='color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.4;'>Upload an MP3, WAV, or M4A call recording in the sidebar pipeline panel, then trigger transcription execution.</p>
#                 </div>
#                 <div style='background-color: #F8FAFC; padding: 22px; border-radius: 6px; border-left: 4px solid #328CC1;'>
#                     <div style='font-weight: 800; color: #328CC1; font-size: 1.25rem; margin-bottom: 6px;'>02</div>
#                     <strong style='color: #0F294A; font-size: 0.95rem; display: block; margin-bottom: 4px;'>Rubric Matrix Mapping</strong>
#                     <p style='color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.4;'>Provide an updated evaluation rule profile (.md file). If left unselected, the platform applies default system guidelines.</p>
#                 </div>
#                 <div style='background-color: #F8FAFC; padding: 22px; border-radius: 6px; border-left: 4px solid #328CC1;'>
#                     <div style='font-weight: 800; color: #328CC1; font-size: 1.25rem; margin-bottom: 6px;'>03</div>
#                     <strong style='color: #0F294A; font-size: 0.95rem; display: block; margin-bottom: 4px;'>Performance Scorecard</strong>
#                     <p style='color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.4;'>Run the verification audit module to output automated turn transcripts, cross-referenced criteria quotes, and action items.</p>
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)


# if __name__ == "__main__":
#     main()

"""
Reliable Communication Call Rating Desk
Upload Call Audio (including MP4) & Custom Markdown Evaluation Rubrics to run automated QA audits.
"""

from __future__ import annotations

import html
import json
import os
import re
import tempfile
from pathlib import Path

import streamlit as st
from groq import APIStatusError, Groq

from aligned_transcript import _load_dotenv
from call_audio_pipeline import process_call_recording

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RUBRIC_PATH = SCRIPT_DIR / "TVS_3wheeler_call_qa_rubric.md"

# Parameter mapping dictionary for the Reliable Communication Rubric schema mapping
RUBRIC_PARAM_MAP: dict[str, str] = {
    "EXC": "Excitement / Energy",
    "VOICEMOD": "Voice Modulation",
    "OBJ_HAND": "Objection Handling",
    "INTRO": "Introduction",
    "SHORT_STORY": "Short Story (3 Ws)",
    "PROBING": "Probing",
    "PRESENTATION": "Presentation",
    "PRICE": "Price",
    "CLOSE": "Close",
    "IFUG_I": "IFUG — Indifference",
    "IFUG_F": "IFUG — Fear of Loss",
    "IFUG_U": "IFUG — Urgency",
    "IFUG_G": "IFUG — Greed / Social Proof",
}

# Fallback labels maintained for backwards compatibility with the original template legacy runs
CRITERION_LABELS: dict[str, str] = {
    "1.1": "Greeting & identity",
    "1.2": "Purpose & consent",
    "1.3": "Callback handling",
    "1.4": "Not interested path",
    "2.1": "Customer details",
    "2.2": "Buying intent & lead tag",
    "2.3": "Product / scheme pitch",
    "2.4": "MH eligibility & documents",
    "2.5": "Closing",
    "3.1": "Follow-up script",
    "3.2": "Enquiry in progress (E1–E5)",
}


def init_page_styles():
    """
    Sets up page layout and explicitly overrides Streamlit theme structures.
    Locks colors into a professional corporate scheme to prevent system appearance mode shifts.
    """
    st.set_page_config(
        page_title="Reliable Communication | Professional QA Audit Desk",
        page_icon="📞",
        layout="wide",
    )

    # Hard-locked appearance CSS configuration (Bypasses dark/light mode shifts entirely)
    locked_theme_css = """
    <style>
        /* Force Root Streamlit Variables to remain fixed in Corporate Light Palette */
        :root, [data-theme="light"], [data-theme="dark"], .stApp {
            --primary-color: #328CC1 !important;
            --background-color: #F4F6F9 !important;
            --secondary-background-color: #FFFFFF !important;
            --text-color: #0F172A !important;
        }

        /* Main Workspace Canvas Override */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"], .stApp {
            background-color: #F4F6F9 !important;
            color: #0F172A !important;
        }

        /* Prevent system dark mode from flipping text color in the workspace */
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] h5,
        [data-testid="stAppViewContainer"] div {
            color: #0F172A !important;
        }

        /* Lock Sidebar Panel to Corporate Deep Navy Accent */
        [data-testid="stSidebar"], 
        [data-testid="stSidebarUserContent"], 
        [data-testid="stSidebarNav"],
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            background-color: #0F294A !important;
            color: #FFFFFF !important;
        }

        /* Enforce high-visibility white text for all sidebar elements */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] small {
            color: #FFFFFF !important;
        }

        /* Form elements and file uploaders container normalization */
        [data-testid="stSidebar"] section[role="dialog"] {
            background-color: #16365C !important;
            border: 1px dashed #328CC1 !important;
        }

        /* Form input fields & textareas formatting control */
        textarea, .stTextArea textarea, div[role="textbox"], input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            -webkit-text-fill-color: #0F172A !important;
        }

        /* Specifically force disabled textareas to retain readability */
        textarea:disabled, .stTextArea textarea:disabled {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
            opacity: 1 !important;
        }

        /* Branding Typography */
        .brand-header {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0F294A !important;
            margin-top: -10px;
            margin-bottom: 0px;
            letter-spacing: -0.5px;
        }
        
        .brand-sub {
            font-size: 1.05rem;
            color: #475569 !important;
            font-weight: 500;
            margin-bottom: 25px;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F294A !important;
            margin-bottom: 12px;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 6px;
        }

        /* Premium Metric Scorecard Elements */
        .metric-card {
            background-color: #FFFFFF !important;
            border-left: 4px solid #328CC1 !important;
            border-top: 1px solid #E2E8F0 !important;
            border-right: 1px solid #E2E8F0 !important;
            border-bottom: 1px solid #E2E8F0 !important;
            padding: 14px 16px;
            border-radius: 6px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            color: #0F172A !important;
        }
        
        .metric-card * {
            color: #0F172A !important;
        }

        /* Extracted Transcript Window Styles */
        .transcript-box {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            padding: 16px;
            border-radius: 6px;
            font-size: 0.95rem;
            line-height: 1.6;
            max-height: 650px;
            overflow-y: auto;
        }
    </style>
    """
    st.markdown(locked_theme_css, unsafe_allow_html=True)


def load_active_rubric(uploaded_file) -> str:
    """Loads text from either an uploaded custom rubric file or the local default fallback."""
    if uploaded_file is not None:
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.sidebar.error(f"Error reading uploaded rubric: {e}")
            return ""
            
    if DEFAULT_RUBRIC_PATH.is_file():
        return DEFAULT_RUBRIC_PATH.read_text(encoding="utf-8")
    return ""


def parse_llm_json(raw_text: str) -> dict | None:
    cleaned = raw_text.strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except Exception:
        return None


def run_qa_scoring(transcript: str, rubric_text: str) -> dict | None:
    groq_key = os.getenv("GROQ_API_KEY") or st.session_state.get("GROQ_API_KEY")
    if not groq_key:
        st.error("GROQ_API_KEY is missing. Configure it in your environment or sidebar configuration.")
        return None

    client = Groq(api_key=groq_key)
    
    # Adaptive system prompt instructions that conform precisely to whatever scoring guidelines are provided
    system_prompt = (
        "You are an expert operational Quality Auditor. "
        "Analyze the provided call transcript and evaluate performance based precisely on the parameters, definitions, "
        "and scoring scale rules (e.g., 1-5 Stars, or D/P/N/NA grading) explicit in the user provided evaluation rubric text.\n\n"
        "Return your evaluation output strictly inside a valid JSON object matching this structure layout:\n"
        "{\n"
        '  "overall_rating": "Provide holistic rating/score matching the rubric methodology (e.g., EXCELLENT, or 4/5 Stars)",\n'
        '  "top_strength": "Dominant performance strength observed",\n'
        '  "top_improvement_area": "Primary workflow process requiring development",\n'
        '  "audit_remark": "Brief final analytical audit remark summary statement",\n'
        '  "parameters_evaluated": [\n'
        '    {\n'
        '      "id_or_name": "Parameter label name or numeric code evaluated",\n'
        '      "score": "The score assigned (e.g., D, P, 5, or NA)",\n'
        '      "evidence": "Brief word-for-word quote extracted directly from text to serve as proof",\n'
        '      "notes": "Contextual justification detail or operational audit context"\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    user_content = f"--- TARGET EVALUATION RUBRIC RULES ---\n{rubric_text}\n\n--- TARGET CALL TRANSCRIPT ---\n{transcript}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return parse_llm_json(completion.choices[0].message.content or "")
    except APIStatusError as e:
        st.error(f"Groq API Error: {e}")
        return None


def _render_rating_block(rating_data: dict):
    # Resolve overall score / quality rating seamlessly across schemas
    overall = (
        rating_data.get("overall_rating") 
        or rating_data.get("quality_rating") 
        or rating_data.get("overall_call_quality_stars") 
        or "N/A"
    )
    st.markdown(f"#### Performance Rating Score: **{overall}**")

    # Handle operational strengths mapping dynamically
    strength_text = rating_data.get("top_strength") or "Review evaluation markers for details."
    
    # Normalize improvements whether returned as a string text block or individual bullet points array
    improvements = rating_data.get("top_improvement_area")
    if not improvements and "top_3_improvements" in rating_data:
        imps = rating_data["top_3_improvements"]
        if isinstance(imps, list):
            improvements = "\n".join([f"- {i}" for i in imps])
        else:
            improvements = str(imps)
    if not improvements:
        improvements = "None identified."

    c_str, c_imp = st.columns(2)
    with c_str:
        st.info(f"**Top Strength:**\n{strength_text}")
    with c_imp:
        st.warning(f"**Area of Improvement:**\n{improvements}")
        
    remark = rating_data.get("audit_remark")
    if remark:
        st.markdown(f"> **Audit Remark:** {html.escape(str(remark))}")

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # Dynamic Parser Normalization Block
    eval_list = rating_data.get("parameters_evaluated")
    
    # Schema Route A: Handle Custom Structured Rubrics (e.g., Reliable Communication Rubric format)
    if not eval_list and "scores" in rating_data:
        eval_list = []
        for item in rating_data["scores"]:
            param_id = item.get("id") or item.get("param_id") or "Unknown"
            label = RUBRIC_PARAM_MAP.get(str(param_id), "")
            display_name = f"[{param_id}] {label}" if label else f"[{param_id}]"
            
            eval_list.append({
                "id_or_name": display_name,
                "score": item.get("score", "N/A"),
                "evidence": item.get("evidence") or item.get("one_line_evidence") or "No direct transcript citation provided.",
                "notes": item.get("notes", "")
            })

    # Schema Route B: Handle Legacy Scorecards
    if not eval_list and "criteria" in rating_data:
        eval_list = []
        for item in rating_data["criteria"]:
            cid = item.get("criterion_id")
            label = CRITERION_LABELS.get(str(cid), f"Parameter {cid}")
            score_val = item.get("stars", "N/A")
            eval_list.append({
                "id_or_name": f"[{cid}] {label}",
                "score": f"{score_val} ⭐" if str(score_val).isdigit() else score_val,
                "evidence": item.get("one_line_evidence", "No direct transcript citation provided."),
                "notes": item.get("notes", "")
            })

    # Dynamic interface generator loop
    if eval_list:
        for item in eval_list:
            p_name = item.get("id_or_name") or "Unlabeled Parameter"
            score = item.get("score", "N/A")
            evidence = item.get("evidence") or "No direct transcript citation provided."
            notes = item.get("notes", "")
            
            if str(score).isdigit():
                score = f"{score} ⭐"
            
            notes_html = ""
            if notes:
                notes_html = f"<div style='margin-top:2px; font-size:0.85rem; color:#64748B;'><b>Auditor Notes:</b> {html.escape(str(notes))}</div>"
            
            st.markdown(
                f"<div class='metric-card'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<strong>{html.escape(str(p_name))}</strong>"
                f"<span style='color:#328CC1; font-weight:700;'>{html.escape(str(score))}</span>"
                f"</div>"
                f"<div style='margin-top:6px; font-size:0.88rem;'><b>Evidence:</b> <i>\"{html.escape(str(evidence))}\"</i></div>"
                f"{notes_html}"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.warning("No dynamic evaluation metrics could be processed from the model output format layout.")


def main():
    _load_dotenv(SCRIPT_DIR / ".env")
    init_page_styles()

    # Fixed App Workspace Branding
    st.markdown('<div class="brand-header">Reliable Communication</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Direct Sales & Call Operations — QA Performance Evaluation Desk</div>', unsafe_allow_html=True)

    if "aligned_text" not in st.session_state:
        st.session_state.aligned_text = ""
    if "english_translation" not in st.session_state:
        st.session_state.english_translation = ""
    if "tvs_rating" not in st.session_state:
        st.session_state.tvs_rating = None

    # Sidebar Component Management Dashboard
    with st.sidebar:
        st.subheader("🔑 Authentication Details")
        groq_env = os.getenv("GROQ_API_KEY", "")
        if not groq_env:
            groq_input = st.text_input("Groq API Key", type="password")
            if groq_input:
                st.session_state["GROQ_API_KEY"] = groq_input

        pyannote_env = os.getenv("PYANNOTE_API_KEY", "")
        if not pyannote_env:
            pyannote_input = st.text_input("Pyannote API Key", type="password")
            if pyannote_input:
                st.session_state["PYANNOTE_API_KEY"] = pyannote_input

        # Media Intake Pipeline 
        st.markdown("<hr style='margin:15px 0; border-color:#2B4C7E;'/>", unsafe_allow_html=True)
        st.subheader("🎵 Media Intake Pipeline")
        audio_file = st.file_uploader("Upload Call Audio/Video Recording", type=["mp3", "wav", "m4a", "mp4"])
        process_btn = st.button("Process & Transcribe Audio", disabled=audio_file is None, use_container_width=True)

        # Custom Quality Rubric situated perfectly underneath Media Intake panel
        st.markdown("<hr style='margin:15px 0; border-color:#2B4C7E;'/>", unsafe_allow_html=True)
        st.subheader("📑 Custom Quality Rubric")
        uploaded_rubric = st.file_uploader(
            "Upload Evaluation Rubric (.md)", 
            type=["md"],
            help="Upload custom evaluation scorecards. If blank, defaults to local template."
        )

        st.markdown("<hr style='margin:15px 0; border-color:#2B4C7E;'/>", unsafe_allow_html=True)
        score_btn = st.button(
            "Execute Quality Scorecard Audit", 
            disabled=not st.session_state.aligned_text, 
            use_container_width=True,
            type="primary"
        )

    # Core Logic Pipeline Hook Execution 
    if process_btn and audio_file:
        file_suffix = Path(audio_file.name).suffix.lower()
        with st.spinner("Processing timeline transcription alignments via pipeline..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = Path(tmp.name)

                # Automated MP4 to MP3 Extraction Block
                if file_suffix == ".mp4":
                    st.info("Converting uploaded MP4 container to native MP3 format...")
                    try:
                        from pydub import AudioSegment
                        sound = AudioSegment.from_file(str(tmp_path), format="mp4")
                        converted_path = tmp_path.with_suffix(".mp3")
                        sound.export(str(converted_path), format="mp3")
                        try:
                            os.unlink(tmp_path)
                        except Exception:
                            pass
                        tmp_path = converted_path
                    except Exception as conv_err:
                        st.error("Audio conversion failed. Please verify 'pydub' and 'ffmpeg' are configured on the system host.")
                        raise conv_err

                result = process_call_recording(tmp_path)
                
                st.session_state.aligned_text = result.get("text", "")
                st.session_state.english_translation = result.get("english_translation", "")
                st.session_state.tvs_rating = None  # Reset historical reviews
                st.success("Audio analysis pipeline finished successfully!")
                
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
            except Exception as e:
                st.error(f"Processing Error Encountered: {e}")

    if score_btn and st.session_state.aligned_text:
        with st.spinner("Analyzing audio context against structural rubric benchmarks..."):
            active_rubric_content = load_active_rubric(uploaded_rubric)
            if not active_rubric_content:
                st.error("No valid rubric rules available. Please upload a .md template file.")
            else:
                scores = run_qa_scoring(st.session_state.aligned_text, active_rubric_content)
                if scores:
                    st.session_state.tvs_rating = scores
                    st.success("Audit verification completed!")

    # Layout Output Panels
    if st.session_state.aligned_text:
        col_transcript, col_scorecard = st.columns([1, 1], gap="large")

        with col_transcript:
            st.markdown('<div class="section-title">📝 Generated Conversational Transcript</div>', unsafe_allow_html=True)
            st.text_area(
                "transcript",
                st.session_state.aligned_text,
                height=650,
                label_visibility="collapsed",
                disabled=True
            )
            if st.session_state.english_translation:
                with st.expander("View Consolidated English Translation Block"):
                    st.markdown(
                        '<div class="transcript-box">'
                        + html.escape(st.session_state.english_translation).replace("\n", "<br/>")
                        + "</div>",
                        unsafe_allow_html=True,
                    )

        with col_scorecard:
            st.markdown('<div class="section-title">🎯 Automated Performance Audit Scorecard</div>', unsafe_allow_html=True)
            if not st.session_state.tvs_rating:
                st.info("Transcript ready. Press 'Execute Quality Scorecard Audit' in the setup panel to display findings.")
            else:
                with st.container(height=650, border=True):
                    _render_rating_block(st.session_state.tvs_rating)
                
                with st.expander("Raw Structural Model Output Data (JSON)"):
                    st.code(json.dumps(st.session_state.tvs_rating, ensure_ascii=False, indent=2), language="json")
    else:
        # Landing dashboard workspace
        st.markdown("""
        <div style='background-color: #FFFFFF; padding: 35px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); margin-top: 5px;'>
            <h3 style='color: #0F294A; margin-top: 0; font-weight: 700; font-size: 1.4rem;'>Quality Assurance Automated Workspace</h3>
            <p style='color: #475569; font-size: 1rem; line-height: 1.5;'>
                Welcome to the operational rating desk. This platform allows you to evaluate agent conversation performance seamlessly against complex compliance matrices using direct audio pipeline analytics.
            </p>
            <hr style='border-color: #F1F5F9; margin: 25px 0;'/>
            <h4 style='color: #0F294A; margin-bottom: 18px; font-weight: 600; font-size: 1.1rem;'>🚀 Operational Instructions Workflow:</h4>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;'>
                <div style='background-color: #F8FAFC; padding: 22px; border-radius: 6px; border-left: 4px solid #328CC1;'>
                    <div style='font-weight: 800; color: #328CC1; font-size: 1.25rem; margin-bottom: 6px;'>01</div>
                    <strong style='color: #0F294A; font-size: 0.95rem; display: block; margin-bottom: 4px;'>Media Intake Processing</strong>
                    <p style='color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.4;'>Upload an MP3, WAV, M4A, or MP4 recording in the sidebar pipeline panel, then trigger transcription execution.</p>
                </div>
                <div style='background-color: #F8FAFC; padding: 22px; border-radius: 6px; border-left: 4px solid #328CC1;'>
                    <div style='font-weight: 800; color: #328CC1; font-size: 1.25rem; margin-bottom: 6px;'>02</div>
                    <strong style='color: #0F294A; font-size: 0.95rem; display: block; margin-bottom: 4px;'>Rubric Matrix Mapping</strong>
                    <p style='color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.4;'>Provide an updated evaluation rule profile (.md file). If left unselected, the platform applies default system guidelines.</p>
                </div>
                <div style='background-color: #F8FAFC; padding: 22px; border-radius: 6px; border-left: 4px solid #328CC1;'>
                    <div style='font-weight: 800; color: #328CC1; font-size: 1.25rem; margin-bottom: 6px;'>03</div>
                    <strong style='color: #0F294A; font-size: 0.95rem; display: block; margin-bottom: 4px;'>Performance Scorecard</strong>
                    <p style='color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.4;'>Run the verification audit module to output automated turn transcripts, cross-referenced criteria quotes, and action items.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()