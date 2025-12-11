import gradio as gr
import requests
import json
import matplotlib.pyplot as plt
import numpy as np

API_URL = "http://localhost:8000/analyze"

def create_radar_chart(scores):
    # Simple radar chart generator
    labels = list(scores.keys())
    values = list(scores.values())
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='cyan', alpha=0.25)
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    
    return fig

def process_video(video, topic):
    # Call the Backend
    files = {'file': open(video, 'rb')}
    data = {'topic': topic}
    
    try:
        response = requests.post(API_URL, files=files, data=data)
        result = response.json()
        
        # Parse Results for UI
        ov_score = result['overall_score']
        
        # Data for Radar Chart
        radar_data = {
            "Content": result['pipelines']['content']['content_score'],
            "Visual Impact": result['pipelines']['visual']['visual_score'],
            "Vocal Clarity": result['pipelines']['audio']['prosody_score'],
            "Pace": result['pipelines']['audio']['details']['pace_bpm'] / 20 # Normalized roughly
        }
        radar_plot = create_radar_chart(radar_data)
        
        # Construct Feedback Text
        feedback_md = f"""
        # 🏆 Overall Score: {ov_score}/10
        
        ### 🧠 Content Analysis
        * **Accuracy:** {result['pipelines']['content']['accuracy_score']}
        * **Structure:** {result['pipelines']['content']['structure_score']}
        * **Missing Concepts:** {", ".join(result['pipelines']['content'].get('missing_concepts', []))}
        
        ### 🗣️ Speech & Prosody
        * **Pace:** {result['pipelines']['audio']['details']['pace_bpm']} BPM
        * **Silence Ratio:** {result['pipelines']['audio']['details']['silence_ratio']}
        
        ### 👁️ Visual Engagement
        * **Eye Contact Score:** {result['pipelines']['visual']['details']['engagement']}
        * **Gesture Energy:** {result['pipelines']['visual']['details']['energy']}
        """
        
        return feedback_md, radar_plot, result['transcript']
        
    except Exception as e:
        return f"Error: {str(e)}", None, ""

# --- Layout ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎓 AI Mentor Evaluator")
    gr.Markdown("Upload a teaching video to get a multimodal evaluation on Content, Delivery, and Engagement.")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_video = gr.Video(label="Upload Session")
            input_topic = gr.Textbox(label="Teaching Topic", placeholder="e.g. React Hooks")
            submit_btn = gr.Button("Analyze Performance 🚀", variant="primary")
        
        with gr.Column(scale=1):
            score_display = gr.Markdown("## Waiting for input...")
            radar_viz = gr.Plot(label="Skill Radar")
    
    with gr.Row():
        transcript_box = gr.Textbox(label="Generated Transcript", lines=10)

    submit_btn.click(
        fn=process_video,
        inputs=[input_video, input_topic],
        outputs=[score_display, radar_viz, transcript_box]
    )

if __name__ == "__main__":
    demo.launch()