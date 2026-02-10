import streamlit as st
import os
import shutil
import uuid
from backend.processor import PDFProcessor
from backend.rag_engine import RAGEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

st.set_page_config(page_title="Multilingual PDF Assistant", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Multilingual PDF Assistant")
st.write("Upload a PDF to get summaries and chat with your document in any language.")

# Initialize Backend Modules
if 'processor' not in st.session_state:
    st.session_state.processor = PDFProcessor()
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = None

# Sidebar
with st.sidebar:
    st.header("Document Controls")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and (st.session_state.session_id is None or uploaded_file.name != st.session_state.get('last_file')):
        with st.spinner("Processing PDF..."):
            session_id = str(uuid.uuid4())
            save_path = f"backend/storage/{session_id}.pdf"
            os.makedirs("backend/storage", exist_ok=True)
            
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            text, chunks, lang = st.session_state.processor.process_pdf(save_path)
            
            if text:
                st.session_state.session_id = session_id
                st.session_state.pdf_text = text
                st.session_state.vector_store = st.session_state.rag_engine.create_vector_store(chunks)
                st.session_state.detected_lang = lang
                st.session_state.last_file = uploaded_file.name
                st.success(f"Processed! Detected Language: {lang}")
            else:
                st.error("Could not extract text from this PDF.")

    if st.session_state.session_id:
        st.divider()
        st.header("Summary Settings")
        target_lang = st.selectbox("Output Language", ["en", "es", "fr", "de", "zh", "ja", "hi", "ar"])
        summary_style = st.selectbox("Summary Style", ["Short Summary", "Detailed Summary", "Bullet Points", "ELI5"])
        
        if st.button("Generate/Update Summary"):
            with st.spinner("Generating summary..."):
                summary = st.session_state.rag_engine.get_summary(
                    st.session_state.pdf_text, 
                    style=summary_style, 
                    language=target_lang
                )
                st.session_state.summary = summary

# Main Area
if st.session_state.session_id:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Summary")
        if 'summary' in st.session_state:
            st.info(st.session_state.summary)
        else:
            st.write("Click 'Generate Summary' in the sidebar to begin.")

    with col2:
        st.subheader("Chat with PDF")
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about the document..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    qa_chain = st.session_state.rag_engine.get_qa_chain(
                        st.session_state.vector_store, 
                        language=target_lang
                    )
                    response = qa_chain.invoke(prompt)
                    st.markdown(response["result"])
                    st.session_state.messages.append({"role": "assistant", "content": response["result"]})
else:
    st.info("Please upload a PDF file in the sidebar to start.")
