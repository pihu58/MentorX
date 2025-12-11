from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import asyncio
from analyzers import VisualAnalyzer, AudioAnalyzer, ContentAgent
from utils import extract_audio, clean_up

app = FastAPI()

# Allow the frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pipelines once (Load models into RAM)
print("⏳ Loading AI Models... (This might take 10-20 seconds)")
visual_engine = VisualAnalyzer()
audio_engine = AudioAnalyzer()
content_engine = ContentAgent()
print("✅ Models Loaded! API is ready.")

@app.post("/analyze")
async def analyze_mentor(
    file: UploadFile = File(...), 
    topic: str = Form("General")
):
    # 1. Save Temp File
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    audio_filename = "temp_audio.wav"
    
    try:
        # 2. Extract Audio (Blocking but fast)
        extract_audio(temp_filename, audio_filename)
        
        # 3. Parallel Execution Pipeline
        loop = asyncio.get_event_loop()
        
        # Task A: Visual Analysis
        future_visual = loop.run_in_executor(None, visual_engine.analyze_video, temp_filename)
        
        # Task B: Audio Analysis + Transcription
        future_audio = loop.run_in_executor(None, audio_engine.analyze_audio, audio_filename)
        
        # Wait for A & B to finish
        visual_results, audio_results = await asyncio.gather(future_visual, future_audio)
        
        # Task C: Content Analysis (Needs Transcript from Task B)
        transcript = audio_results['transcript']
        content_results = await loop.run_in_executor(None, content_engine.evaluate, transcript, topic)
        
        # 4. Multimodal Fusion (The Rubric)
        # Weights: Content 35%, Prosody 35%, Visual 30%
        final_score = (
            (content_results.get('content_score', 0) * 0.35) + 
            (audio_results.get('prosody_score', 0) * 0.35) + 
            (visual_results.get('visual_score', 0) * 0.30)
        )
        
        response_data = {
            "overall_score": round(final_score, 2),
            "pipelines": {
                "visual": visual_results,
                "audio": audio_results,
                "content": content_results
            },
            "transcript": transcript
        }
        
        return response_data

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return {"error": str(e)}

    finally:
        # Cleanup (Delete temp files so your laptop doesn't fill up)
        clean_up([temp_filename, audio_filename])

if __name__ == "__main__":
    import uvicorn
    # CHANGED: Use 127.0.0.1 instead of 0.0.0.0 to fix browser issues
    # ACCESS LINK: http://127.0.0.1:8000/docs
    uvicorn.run(app, host="127.0.0.1", port=8000)