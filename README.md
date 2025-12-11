# MentorX: Automated Multimodal Teaching Quality Evaluation

**Team ID:** Upsk-250439  
**Repository:** https://github.com/pihu58/MentorX

## 1. Project Overview
MentorX is an automated, multimodal, objective evaluation system designed to analyze teaching quality from video content. It solves the problem of manual, subjective and non-scalable evaluation in large education systems.

The system evaluates three dimensions:

- Content Quality (Text)
- Delivery and Communication (Audio)
- Engagement and Presence (Video)

## 2. Architecture Overview
MentorX uses an AI-first, decoupled microservices architecture with asyncio-based concurrent pipelines.

### Components

| Component | Technology | Function | Deployment |
|----------|------------|----------|------------|
| Frontend | Next.js 14 | Real-time visualization | Vercel |
| Backend | FastAPI (Dockerized) | Orchestration and splitting | Render |
| AI Inference | Hybrid (CPU + Groq LPU) | Metric extraction | Groq LPU + Local CPU |

### Pipelines

**Semantic Pipeline:** Whisper ASR + Llama 3-8B (Groq) for deterministic content scoring.  
**Visual Pipeline:** MediaPipe and OpenCV for Eye Contact Ratio, Gesture Energy, Posture Openness.  
**Acoustic Pipeline:** Librosa and FFmpeg for Pitch Variability, Pacing BPM, Pause Density.

## 3. Setup Instructions

### Clone repository
```bash
git clone https://github.com/pihu58/MentorX.git
cd MentorX
```

### Environment variables (`backend/.env`)
```
GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

### Folder structure
```
.
├── src/
├── models/
├── docs/
└── requirements.txt
```

## 4. Running Locally

### Backend
```bash
docker build -t mentorx-backend .
docker run -p 8000:8000 --env-file .env mentorx-backend
```

### Frontend
```bash
npm install
npm run dev
```

## 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/evaluate | Evaluate teaching video |
| GET | /health | Status check |


## 6. Example Input/Output
```json
{
  "total_score": 8.5,
  "content_quality": {
    "clarity_score": 9,
    "correctness_score": 8,
    "structure_score": 8,
    "concept_coverage_score": 9
  },
  "visual_delivery": {
    "eye_contact_ratio": 0.85,
    "gesture_energy_score": 7,
    "posture_openness_score": 8
  },
  "vocal_delivery": {
    "pitch_variability_score": 9,
    "pacing_bpm": 150,
    "pause_density": 0.05
  }
}
```

## 7. Dependencies
Semantic: Whisper, Llama 3-8B (Groq), asyncio  
Visual: MediaPipe, OpenCV  
Acoustic: Librosa, FFmpeg  
Backend: FastAPI, Docker  
Frontend: Next.js 14, Vercel  

## 8. Contributors
- Pihu Agrawal
- Sukriti Talwar
- Shubhank Gupta

