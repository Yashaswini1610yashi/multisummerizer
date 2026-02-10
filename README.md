# 📄 Multisummerizer - Multilingual PDF Assistant

Multisummerizer is a premium, AI-powered document assistant that can process PDF files in any language, generate structured summaries in your preferred language, and answer complex questions strictly based on the document content.

## 🚀 Features

- **🌐 Multilingual Support**: Upload PDFs in any language and get outputs in English, Spanish, French, German, and more.
- **📝 Multiple Summary Styles**:
  - **Short Summary**: Concise and high-level.
  - **Detailed Summary**: Structured with Key Points and Insights.
  - **Bullet Points**: Easy to scan information.
  - **ELI5**: Simple explanations (Explain Like I'm 5).
- **💬 Strict Q&A**: A RAG (Retrieval-Augmented Generation) pipeline ensures that the AI only answers based on the provided document—no hallucinations.
- **🎨 Premium UI**: Modern glassmorphism design with smooth animations and responsive layout.
- **⚡ Dual-Mode Operation**: Run it as a full-stack React/FastAPI app or a lightweight Streamlit app.

---

## 📂 Project Structure

```
multisummerizer/
├── backend/            # FastAPI Server (RAG & PDF Logic)
│   ├── main.py         # API entry point
│   ├── processor.py    # PDF Text Extraction (PyMuPDF)
│   ├── rag_engine.py   # AI Chains & Vector Store (FAISS)
│   └── storage/        # Local PDF storage (ignored by git)
├── frontend/           # React + Vite Frontend (Premium UI)
│   ├── src/            # Components, CSS, and Assets
│   └── public/         # Static assets
├── streamlit_app.py    # All-in-one Streamlit Interface
├── requirements.txt    # Unified backend/streamlit dependencies
└── .gitignore          # Git exclusion rules
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js (for React frontend)
- Google Generative AI API Key (Gemini)

### 2. Configure Environment
Create a `.env` file inside the `backend/` directory or root with your API key:
```env
GOOGLE_API_KEY=your_api_key_here
```

### 3. Running the Streamlit App (Fastest)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### 4. Running the Full Web App
**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Strict Guardrails
- If the information is not in the document, the assistant reflects: *"I could not find this information in the uploaded document."*
- Strictly PDF only.
- Privacy focused: Documents are processed and stored locally in your session.

---

## 📜 License
MIT License. Created with ❤️ for intelligent document analysis.
