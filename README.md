# 🎓 AI-Powered Mentor Evaluation Platform

> A multi-modal AI system that evaluates teaching performance by analyzing video (body language), audio (prosody/pacing), and text (content quality) in real-time.

## 🏆 Project Overview
This platform solves the challenge of subjective teaching feedback. Instead of relying on human bias, we use a hybrid AI pipeline to objectively score mentors on:
- **Clarity:** Does the content make sense? (Llama 3)
- **Engagement:** Eye contact, gestures, and energy. (MediaPipe)
- **Delivery:** Pacing, tone variety, and pauses. (Librosa)

## 🏗️ Architecture
The system runs three parallel analysis pipelines:
1.  **Visual Pipeline:** Uses **MediaPipe** to track 478 face landmarks and 33 pose landmarks to calculate "Energy" and "Eye Contact" scores.
2.  **Audio Pipeline:** Uses **Librosa** to extract pitch, tempo (BPM), and silent intervals to measure vocal confidence.
3.  **Content Pipeline:** Uses **OpenAI Whisper** for transcription and **Llama 3 (via Ollama)** as a pedagogical judge to rate technical accuracy and structure.

## 🚀 Tech Stack
- **Frontend:** Next.js 14, Tailwind CSS, Shadcn UI, Recharts
- **Backend:** Python, FastAPI, Uvicorn
- **AI/ML:** Llama 3 (8B), Ollama, MediaPipe, Librosa, MoviePy, Whisper
- **Infrastructure:** Local GPU inference + Vercel Frontend

## 🛠️ Setup Instructions

### Prerequisites
1.  **Node.js 18+** & **Python 3.10+**
2.  **FFmpeg** installed and added to System PATH.
3.  **Ollama** installed and running (`ollama run llama3`).

### Installation
1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/pihu58/mentor-eval-platform.git](https://github.com/pihu58/mentor-eval-platform.git)
    cd mentor-eval-platform
    ```

2.  **Start the Backend:**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # or .\venv\Scripts\activate on Windows
    pip install -r requirements.txt
    python main.py
    ```
    *Server runs at http://localhost:8000*

3.  **Start the Frontend:**
    ```bash
    cd ../frontend
    npm install
    npm run dev
    ```
    *App runs at http://localhost:3000*

## 📊 Evaluation Criteria & Weights
The final score is a weighted average of:
- **Content Quality (35%):** Accuracy & Relevance (LLM Judge)
- **Vocal Delivery (35%):** Pacing & Tone (Signal Processing)
- **Visual Impact (30%):** Engagement & Confidence (Computer Vision)

## 🔮 Future Roadmap
- [ ] Integration with Canvas LMS.
- [ ] Real-time emotion detection using DeepFace.
- [ ] "Compare with Expert" mode.