import gradio as gr
import torch
from PIL import Image
import numpy as np
from torchvision import transforms

from src.model import load_model
from src.gradcam import setup_gradcam, generate_heatmap
from src.report_generator import (
    create_pdf_report,
    format_report_markdown,
    generate_report,
)

# Load model once at startup
print("Loading model...")
model, device = load_model("models/best_chexnet.pth")
cam = setup_gradcam(model)
print(f"Model loaded on {device}")

# Transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def analyze(image):
    if image is None:
        return None, "No image", "No risk", "Upload an X-ray", None
    
    # Preprocess
    img_pil = Image.fromarray(image).convert('RGB')
    img_tensor = transform(img_pil).unsqueeze(0).to(device)
    img_array = np.array(img_pil.resize((224, 224))) / 255.0
    
    # Predict
    with torch.no_grad():
        prob = model(img_tensor).item()
    
    # Heatmap
    heatmap = generate_heatmap(model, cam, img_tensor, img_array)
    
    # Report
    report_data = generate_report(prob)
    report_text = format_report_markdown(report_data)
    report_pdf_path = create_pdf_report(report_data)
    
    # Risk badge
    if prob > 0.8:
        risk = "🔴 HIGH"
    elif prob > 0.5:
        risk = "🟡 MODERATE"
    else:
        risk = "🟢 LOW"
    
    return heatmap, f"{prob:.1%}", risk, report_text, report_pdf_path

# Gradio interface
with gr.Blocks(title="CheXNet AI") as demo:
    gr.Markdown("# 🫁 CheXNet AI: Pneumonia Detection")
    
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(label="Upload Chest X-ray")
            btn = gr.Button("Analyze", variant="primary")
        
        with gr.Column():
            heatmap = gr.Image(label="Grad-CAM Heatmap")
            prob = gr.Textbox(label="Probability")
            risk = gr.Textbox(label="Risk Level")
    
    report = gr.Markdown()
    report_pdf = gr.File(label="Download PDF Report")
    
    btn.click(
        analyze,
        inputs=input_img,
        outputs=[heatmap, prob, risk, report, report_pdf],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)