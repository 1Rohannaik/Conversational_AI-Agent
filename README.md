# 🎤 AI Voice Assistant with PDF Intelligence

**🚀 Talk to your documents! Upload PDFs and have natural voice conversations powered by AI.**

> A sophisticated voice-enabled conversational AI assistant that processes PDF documents and provides intelligent responses through speech interaction. Built with React, FastAPI, Groq Whisper, and Google Gemini.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## 📋 Table of Contents

- [🌟 Features](#-features)
- [📊 System Flow](#-system-flow)
- [🛠️ Technology Stack](#️-technology-stack)
- [⚡ Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🎯 API Endpoints](#-api-endpoints)
- [🤖 AI Capabilities](#-ai-capabilities)
- [🎨 UI Components](#-ui-components)
- [🔄 State Management](#-state-management)
- [📱 Screenshots](#-screenshots)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🌟 Features

### 🎯 Core Capabilities
- **📄 PDF Processing**: Upload and parse PDF documents with intelligent text extraction
- **🎤 Voice Input**: Real-time speech-to-text using Groq Whisper API
- **🔊 Voice Output**: Natural text-to-speech using Google TTS (gTTS)
- **🧠 AI Conversations**: Intelligent responses powered by Google Gemini and Groq LLMs
- **📚 RAG Pipeline**: Retrieval-Augmented Generation with ChromaDB vector storage
- **🎓 Interactive Interviews**: AI-powered interview sessions based on document content
- **💬 Conversational Flow**: Contextual multi-turn conversations

### 🎨 User Experience
- **✨ Modern UI**: Beautiful, responsive interface with glassmorphism design
- **🎭 Visual Feedback**: Dynamic animations and state indicators
- **🌈 Color-coded States**: Blue (idle), Red (recording), Purple (thinking)
- **📱 Mobile-first**: Optimized for touch devices and desktop
- **🌙 Dark Theme**: Elegant dark mode interface

## 📊 System Flow

### 🔄 Complete Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant STT as Groq Whisper
    participant LLM as Gemini/Groq
    participant TTS as Google TTS
    participant DB as ChromaDB
    
    Note over User,DB: PDF Upload Flow
    User->>Frontend: Upload PDF
    Frontend->>API: POST /upload/upload_pdf/
    API->>DB: Store embeddings
    API->>Frontend: Return file ID
    
    Note over User,DB: Voice Conversation Flow
    User->>Frontend: Press mic button
    Frontend->>Frontend: Start recording
    User->>Frontend: Speak question
    Frontend->>Frontend: Stop recording
    
    Frontend->>STT: Audio file
    STT->>Frontend: Transcript
    
    Frontend->>API: POST /flow/ask
    API->>DB: Retrieve context
    DB->>API: Relevant chunks
    API->>LLM: Generate response
    LLM->>API: AI response
    
    API->>TTS: Text to speech
    TTS->>API: Audio blob
    API->>Frontend: Response + Audio
    Frontend->>User: Play audio response
```

### 🎯 State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Idle: App Start
    
    Idle --> UploadingPDF: Click Upload
    UploadingPDF --> PDFReady: Upload Success
    UploadingPDF --> Idle: Upload Error
    
    PDFReady --> Listening: Click Mic
    Listening --> Processing: Stop Recording
    Processing --> Thinking: STT Complete
    Thinking --> Speaking: LLM Response
    Speaking --> PDFReady: Audio Complete
    
    PDFReady --> InterviewMode: Start Interview
    InterviewMode --> InterviewActive: Begin Questions
    InterviewActive --> InterviewActive: Q&A Loop
    InterviewActive --> PDFReady: End Interview
    
    state Processing {
        [*] --> AudioCapture
        AudioCapture --> SpeechToText
        SpeechToText --> [*]
    }
    
    state Thinking {
        [*] --> RetrieveContext
        RetrieveContext --> GenerateResponse
        GenerateResponse --> [*]
    }
    
    state Speaking {
        [*] --> TextToSpeech
        TextToSpeech --> PlayAudio
        PlayAudio --> [*]
    }
```

## 🛠️ Technology Stack

### 🎨 Frontend
- **React 18+** - Modern UI framework with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Web Audio API** - Real-time audio recording
- **MediaRecorder API** - Audio capture and processing

### ⚡ Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.10+** - Modern Python with type hints
- **SQLAlchemy** - SQL ORM for database operations
- **MySQL** - Relational database for metadata
- **ChromaDB** - Vector database for embeddings
- **Cloudinary** - Cloud storage for PDF files

### 🤖 AI & ML
- **Groq Whisper** - Ultra-fast speech-to-text
- **Google Gemini** - Advanced language model
- **Groq LLaMA** - Alternative LLM for diversity
- **Google TTS (gTTS)** - Natural speech synthesis
- **Sentence Transformers** - Text embeddings
- **LangChain** - LLM application framework

### 🔧 DevOps & Tools
- **Docker** - Containerization (optional)
- **Git** - Version control
- **ESLint** - JavaScript linting
- **Prettier** - Code formatting

## ⚡ Quick Start

### 📋 Prerequisites

```bash
# Required software
- Node.js 18+ and npm
- Python 3.10+
- MySQL 8.0+
- Git
```

### 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-voice-assistant.git
cd ai-voice-assistant
```

2. **Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and database config
```

3. **Setup Frontend**
```bash
cd ../frontend

# Install dependencies
npm install

# Setup environment (optional)
cp .env.example .env.local
```

4. **Configure Environment Variables**

Create `backend/.env`:
```env
# API Keys
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Database
DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/ai_assistant

# Cloudinary (for file storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

5. **Start the Application**

```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

6. **Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
📦 ai-voice-assistant/
├── 📁 backend/
│   ├── 📁 db/                    # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py              # Base model
│   │   └── session.py           # Database session
│   ├── 📁 models/               # Data models
│   │   ├── __init__.py
│   │   └── pdf.py              # PDF model
│   ├── 📁 routers/             # API routes
│   │   ├── conversation.py     # Conversation endpoints
│   │   ├── flow.py            # Main flow controller
│   │   ├── interview.py       # Interview system
│   │   ├── qa.py             # Q&A endpoints
│   │   └── uploads.py        # File upload
│   ├── 📁 services/           # Business logic
│   │   ├── conversational_interview.py
│   │   ├── embeddings.py     # Text embeddings
│   │   ├── interview.py      # Interview logic
│   │   ├── llm.py           # Language model integration
│   │   ├── orchestrator.py  # Request orchestration
│   │   ├── pdf_reader.py    # PDF processing
│   │   ├── rag_pipeline.py  # RAG implementation
│   │   └── vectorstore.py   # Vector database
│   ├── 📁 stt_services/      # Speech-to-Text
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── whisper_model.py
│   ├── 📁 tts_service/       # Text-to-Speech
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── tts_model.py
│   ├── 📁 utils/             # Utilities
│   │   └── cloudinary.py    # File storage
│   ├── main.py              # FastAPI app
│   └── requirements.txt     # Python dependencies
├── 📁 frontend/
│   ├── 📁 public/           # Static assets
│   ├── 📁 src/
│   │   ├── 📁 components/   # React components
│   │   │   ├── GalaxyDots.jsx    # Orb visualization
│   │   │   ├── MicButton.jsx     # Microphone control
│   │   │   ├── Orb.jsx          # Main orb component
│   │   │   ├── Subtitle.jsx     # Text display
│   │   │   └── UploadButton.jsx # File upload
│   │   ├── 📁 hooks/        # React hooks
│   │   │   └── useVoiceAssistant.js # Main logic
│   │   ├── 📁 utils/        # Utilities
│   │   │   └── api.js       # API client
│   │   ├── App.jsx          # Main app component
│   │   ├── App.css          # Styles and animations
│   │   └── main.jsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Build configuration
└── README.md               # This file
```

## 🔧 Configuration

### 🔑 API Keys Setup

1. **Groq API Key** (for Whisper STT)
   - Visit: https://console.groq.com/
   - Create account and generate API key
   - Add to `.env`: `GROQ_API_KEY=your_key_here`

2. **Google API Key** (for Gemini LLM)
   - Visit: https://aistudio.google.com/
   - Create project and enable Gemini API
   - Add to `.env`: `GOOGLE_API_KEY=your_key_here`

3. **Cloudinary** (for file storage)
   - Visit: https://cloudinary.com/
   - Create account and get credentials
   - Add to `.env`: Cloud name, API key, and secret

4. **MySQL Database**
   - Install MySQL 8.0+
   - Create database: `ai_assistant`
   - Update connection string in `.env`

### 🗄️ Database Setup

```sql
-- Create database
CREATE DATABASE ai_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional)
CREATE USER 'ai_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ai_assistant.* TO 'ai_user'@'localhost';
FLUSH PRIVILEGES;
```

## 🎯 API Endpoints

### 📤 Upload Endpoints
- `POST /upload/upload_pdf/` - Upload PDF document
- `GET /upload/config_status` - Check Cloudinary configuration

### 💬 Conversation Endpoints
- `POST /flow/ask` - Main conversation endpoint
- `POST /qa/ask` - Simple Q&A
- `GET /qa/status/{file_id}` - Check processing status

### 🎓 Interview Endpoints
- `POST /interview/start` - Start interview session
- `POST /interview/answer` - Submit interview answer
- `GET /interview/status/{session_id}` - Interview status

### 🎤 Audio Endpoints
- `POST /api/v1/stt` - Speech-to-text conversion
- `POST /api/v1/tts` - Text-to-speech synthesis

### 🏥 Health Endpoints
- `GET /` - API health check
- `GET /db/health` - Database health check

## 🤖 AI Capabilities

### 🧠 Intelligent Features

1. **📚 Document Understanding**
   - PDF text extraction and chunking
   - Semantic embeddings with Sentence Transformers
   - Context-aware retrieval

2. **💭 Conversational AI**
   - Multi-turn conversations with memory
   - Intent recognition and routing
   - Contextual response generation

3. **🎓 Interview System**
   - Dynamic question generation
   - Difficulty level adaptation
   - Topic focus customization

4. **🔍 RAG Pipeline**
   - Efficient similarity search
   - Relevant context retrieval
   - Source attribution

### 🎛️ Model Configuration

```python
# LLM Models
GEMINI_MODEL = "gemini-1.5-flash"
GROQ_MODEL = "llama-3.1-70b-versatile"

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Audio Models
STT_MODEL = "whisper-large-v3"
TTS_LANGUAGE = "en"
```

## 🎨 UI Components

### 🔮 Orb Component
- **Visual States**: Idle, Listening, Speaking
- **Particle Animation**: Galaxy-like dot patterns
- **Color Themes**: Blue (idle), Red (recording), Purple (thinking)

### 🎤 Microphone Button
- **State Indicators**: Color-coded backgrounds
- **Animations**: Scale, glow, and pulse effects
- **Accessibility**: ARIA labels and keyboard support

### ➕ Upload Button
- **Drag & Drop**: File drop zone
- **Progress Indication**: Loading animations
- **Validation**: PDF file type checking

### 💬 Subtitle Display
- **Dynamic Text**: Auto-sizing and positioning
- **Thinking Indicator**: Animated dots
- **Fade Animations**: Smooth transitions

## 🔄 State Management

### 📊 Voice Assistant Hook

```javascript
const {
  isListening,    // Recording state
  subtitle,       // Display text
  error,          // Error messages
  busy,          // Processing state
  fileId,        // Uploaded file ID
  startListening, // Start recording
  stopListening,  // Stop recording
  setFileId      // Set active document
} = useVoiceAssistant()
```

### 🔄 Conversation Flow

1. **PDF Upload** → Document Processing → Embedding Storage
2. **Voice Input** → Speech Recognition → Text Processing
3. **AI Processing** → Context Retrieval → Response Generation
4. **Voice Output** → Text-to-Speech → Audio Playback

## 📱 Screenshots

### 🏠 Main Interface
![Main Interface](screenshots/main-interface.png)
*Clean, modern interface with orb visualization*

### 🎤 Voice Recording
![Voice Recording](screenshots/voice-recording.png)
*Recording state with red microphone indicator*

### 💭 Thinking State
![Thinking State](screenshots/thinking-state.png)
*Processing with animated thinking indicator*

### 📄 PDF Upload
![PDF Upload](screenshots/pdf-upload.png)
*Drag and drop file upload interface*

## 🚀 Deployment

### 🐳 Docker Deployment

1. **Create Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+mysqlconnector://user:pass@db:3306/ai_assistant
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: ai_assistant
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

2. **Deploy**
```bash
docker-compose up -d
```

### ☁️ Cloud Deployment

- **Frontend**: Vercel, Netlify, or AWS S3
- **Backend**: Railway, Heroku, or AWS ECS
- **Database**: PlanetScale, AWS RDS, or Google Cloud SQL
- **Vector DB**: Pinecone or Weaviate Cloud

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### 📝 Development Guidelines

- Follow ESLint and Prettier configurations
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

### 🐛 Bug Reports

Please use the GitHub Issues template and include:
- Browser and OS information
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for Whisper model inspiration
- **Google** for Gemini LLM and TTS services
- **Groq** for ultra-fast inference
- **ChromaDB** for vector storage
- **React** and **FastAPI** communities

## 📞 Support

- 📧 Email: support@yourproject.com
- 💬 Discord: [Join our community](https://discord.gg/yourserver)
- 📚 Docs: [Documentation site](https://docs.yourproject.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ai-voice-assistant/issues)

---

<div align="center">

**Built with ❤️ by [Your Team Name]**

[⭐ Star us on GitHub](https://github.com/yourusername/ai-voice-assistant) • [🐦 Follow on Twitter](https://twitter.com/yourhandle) • [💼 LinkedIn](https://linkedin.com/company/yourcompany)

</div>