import cv2
import mediapipe as mp
import numpy as np
import librosa
import whisper
import requests
import json
import os

# --- 1. VISUAL PIPELINE (MediaPipe) ---
class VisualAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

    def analyze_video(self, video_path, sample_rate=5):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps / sample_rate) # Process ~5 frames per second
        
        metrics = {
            "eye_contact_frames": 0,
            "smile_frames": 0,
            "gesture_energy": [],
            "total_processed": 0
        }
        
        frame_idx = 0
        prev_wrist_y = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_idx % frame_interval == 0:
                metrics["total_processed"] += 1
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Face Analysis
                face_results = self.face_mesh.process(rgb_frame)
                if face_results.multi_face_landmarks:
                    metrics["eye_contact_frames"] += 1 # Naive assumption: Face detected = looking at cam
                    # Smile logic (simplified: lip corners vs lips center)
                    # Real implementation would calculate aspect ratio of lips
                
                # Pose/Gesture Analysis
                pose_results = self.pose.process(rgb_frame)
                if pose_results.pose_landmarks:
                    # Calculate wrist movement energy
                    landmarks = pose_results.pose_landmarks.landmark
                    wrist_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y + 
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y) / 2
                    metrics["gesture_energy"].append(abs(wrist_y - prev_wrist_y))
                    prev_wrist_y = wrist_y
            
            frame_idx += 1
            
        cap.release()
        
        # Normalize scores to 0-10
        total = metrics["total_processed"] if metrics["total_processed"] > 0 else 1
        engagement_score = (metrics["eye_contact_frames"] / total) * 10
        energy_score = min((sum(metrics["gesture_energy"]) * 100), 10) # Scaling factor
        
        return {
            "visual_score": round((engagement_score + energy_score) / 2, 2),
            "details": {
                "engagement": round(engagement_score, 2),
                "energy": round(energy_score, 2)
            }
        }

# --- 2. PROSODY PIPELINE (Librosa/Whisper) ---
class AudioAnalyzer:
    def __init__(self):
        # Load small model for speed (CPU friendly)
        self.asr_model = whisper.load_model("base") 

    def analyze_audio(self, audio_path):
        # A. Transcription
        transcription = self.asr_model.transcribe(audio_path)
        text = transcription['text']
        
        # B. Prosody (Librosa)
        y, sr = librosa.load(audio_path)
        
        # 1. Pitch Variety (Monotone vs Expressive)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        # Filter out background noise
        valid_pitches = pitches[magnitudes > np.median(magnitudes)]
        pitch_std = np.std(valid_pitches) if len(valid_pitches) > 0 else 0
        
        # 2. Speaking Rate (Tempo)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        # 3. Silent Intervals (Pauses)
        rms = librosa.feature.rms(y=y)[0]
        silent_ratio = np.sum(rms < 0.01) / len(rms)
        
        # Scoring logic
        clarity_score = 10 if tempo > 100 and tempo < 160 else 7 # Ideal range 100-160 BPM
        dynamics_score = min(pitch_std / 50, 10) # Normalize pitch variation
        
        return {
            "transcript": text,
            "prosody_score": round((clarity_score + dynamics_score) / 2, 2),
            "details": {
                "pace_bpm": round(tempo, 2),
                "pitch_variety": round(dynamics_score, 2),
                "silence_ratio": round(silent_ratio, 2)
            }
        }

# --- 3. CONTENT PIPELINE (Llama 3 via Ollama) ---
from groq import Groq # Make sure to pip install groq

class ContentAgent:
    def __init__(self):
        # We grab the key from the environment variables (safe for deployment)
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

    def evaluate(self, transcript, topic="General Technical Topic"):
        system_prompt = """
        You are a harsh but fair Judge evaluating a technical mentor. 
        Analyze the transcript based on: Relevance, Technical Accuracy, Structure, and Concept Explanation.
        You MUST return valid JSON only. Format:
        {
            "relevance_score": (0-10),
            "accuracy_score": (0-10),
            "structure_score": (0-10),
            "key_strengths": ["string", "string"],
            "missing_concepts": ["string", "string"]
        }
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Topic: {topic}\nTranscript: {transcript}"
                    }
                ],
                model="llama3-8b-8192", # Using Llama 3 on Groq
                response_format={"type": "json_object"}, # Enforce JSON
            )
            
            # Parse the response
            result = json.loads(chat_completion.choices[0].message.content)
            
            # Calculate average
            avg_score = (result.get('relevance_score', 0) + 
                         result.get('accuracy_score', 0) + 
                         result.get('structure_score', 0)) / 3
            result['content_score'] = round(avg_score, 2)
            return result

        except Exception as e:
            print(f"Groq API Error: {e}")
            return {
                "content_score": 0,
                "accuracy_score": 0, 
                "key_strengths": [], 
                "missing_concepts": [],
                "error": "AI Analysis Failed"
            }