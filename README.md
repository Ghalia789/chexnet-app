# 🫁 CheXNet AI: Pneumonia Detection System

A deep learning application for automated pneumonia detection in chest X-rays using DenseNet-121 with Grad-CAM visualization and clinical-style PDF report generation.

## Overview

CheXNet AI is a production-ready web application that:
- **Analyzes chest X-rays** using a trained DenseNet-121 deep learning model
- **Generates predictions** with probability scores and risk classification (LOW/MODERATE/HIGH)
- **Visualizes predictions** using Grad-CAM heatmaps to highlight relevant regions
- **Creates clinical reports** with structured findings, impressions, and recommendations
- **Exports PDF reports** for clinical integration and record-keeping
- **Runs locally via Gradio** for quick demos or containers for production deployment

## Key Features

✨ **AI-Powered Analysis**
- DenseNet-121 trained on chest X-ray datasets
- Binary classification: Pneumonia detection
- GPU acceleration support (CUDA)

🔍 **Explainability**
- Grad-CAM heatmaps highlight model attention regions
- Visual interpretability for clinicians
- Helps validate model decisions

📋 **Clinical Reporting**
- Structured markdown reports with:
  - Pneumonia probability and risk level
  - Radiologic findings
  - Clinical impression
  - Recommendations for follow-up
  - Model limitations and disclaimer
- PDF export for medical records integration

🌐 **User Interface**
- Web-based Gradio interface
- Drag-and-drop image upload
- Real-time analysis and visualization
- Downloadable PDF reports

🐳 **Containerization & Deployment**
- Docker support for consistent environments
- Kubernetes manifests for multi-environment deployments (dev/test/prod)
- GCP/GKE integration with cost-aware configurations

## Quick Start

### Prerequisites
- Python 3.11+
- PyTorch (with CUDA support optional)
- ~2GB disk space for model weights

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chexnet-app.git
   cd chexnet-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure model file is present**
   - Place your trained model at `models/best_chexnet.pth`
   - The model should be a saved PyTorch state dict

5. **Run the application**
   ```bash
   python app.py
   ```
   
   The application will start at `http://127.0.0.1:7860`

### Docker Installation

1. **Build the Docker image**
   ```bash
   docker build -t chexnet-app:local .
   ```

2. **Run the container**
   ```bash
   docker run -p 7860:7860 chexnet-app:local
   ```
   
   Access at `http://localhost:7860`

## Usage

### Web Interface

1. **Upload an X-ray image**
   - Click "Upload Chest X-ray" 
   - Select a chest X-ray image (PNG, JPG, etc.)

2. **Click "Analyze"**
   - Model processes the image
   - Displays probability and risk level
   - Shows Grad-CAM heatmap highlighting suspicious regions
   - Generates clinical report

3. **Review results**
   - Probability: Model's confidence (0-100%)
   - Risk Level: 🟢 LOW / 🟡 MODERATE / 🔴 HIGH
   - Heatmap: Visual attention map
   - Report: Structured clinical findings
   - Download PDF for records

### Application Flow

```
Upload X-ray
    ↓
Image Preprocessing (224×224, normalization)
    ↓
DenseNet-121 Inference
    ↓
Probability Score
    ↓
┌─────────────────────────────────────┐
├─ Grad-CAM Heatmap Generation        │
├─ Risk Classification                │
├─ Clinical Report Generation         │
└─ PDF Export                         │
    ↓
Display UI Results + Download Option
```

## Project Structure

```
chexnet-app/
├── app.py                              # Main Gradio application entry point
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Docker image definition
├── .gitignore                          # Git ignore rules
├── README.md                           # This file
│
├── models/
│   └── best_chexnet.pth               # Trained DenseNet-121 weights
│
├── src/
│   ├── __init__.py
│   ├── model.py                        # Model loading and inference
│   ├── gradcam.py                      # Grad-CAM heatmap generation
│   ├── report_generator.py             # Clinical report + PDF creation
│   └── utils.py                        # Helper utilities
│
├── K8s/
│   ├── development.yaml                # Dev environment deployment
│   ├── test.yaml                       # Test environment deployment
│   ├── production.yaml                 # Prod environment deployment
│   ├── production-lb.yaml              # Production LoadBalancer config
│   ├── gcp-deploy-commands.template.txt # GCP deployment reference
│   └── lb-toggle-commands.txt          # Load balancer management
│
├── docs/
│   ├── README.md                       # This file
│   ├── PROJECT_STATUS.md               # Implementation progress
│   ├── GIT_SETUP.md                    # Git configuration
│   └── GCP_GKE_DEPLOYMENT_GUIDE.md    # Kubernetes deployment guide
│
└── .dockerignore                       # Docker build excludes
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | 2.11.0 | Deep learning framework |
| torchvision | 0.26.0 | Image processing & pretrained models |
| gradio | 6.13.0 | Web UI framework |
| grad-cam | 1.5.5 | Grad-CAM visualization |
| opencv-python | 4.13.0.92 | Image manipulation |
| pillow | 12.2.0 | Image I/O |
| numpy | 2.4.4 | Numerical computing |
| reportlab | 4.4.5 | PDF generation |

## Model Details

### Architecture
- **Base Model**: DenseNet-121 (ImageNet pretrained)
- **Task**: Binary classification (Pneumonia vs. Normal)
- **Input**: 224×224 RGB images
- **Output**: Probability score (0-1)

### Preprocessing
- Resize to 224×224
- Convert to RGB
- Normalize using ImageNet statistics:
  - Mean: [0.485, 0.456, 0.406]
  - Std: [0.229, 0.224, 0.225]

### Grad-CAM
- Highlights model attention regions
- Targets: DenseBlock4.DenseLayer16.Conv2
- Colormap: Jet
- Image weight: 0.6

## Deployment

### Local Development
```bash
python app.py
```

### Docker
```bash
docker build -t chexnet-app:local .
docker run -p 7860:7860 chexnet-app:local
```

### Kubernetes (GCP/GKE)

For detailed deployment instructions, see [docs/GCP_GKE_DEPLOYMENT_GUIDE.md](docs/GCP_GKE_DEPLOYMENT_GUIDE.md)

Quick start:
```bash
# Set GCP variables
export PROJECT_ID=your-project
export REGION=us-central1
export ZONE=us-central1-a
export REPO=chexnet-repo
export TAG=v1

# Configure
gcloud config set project $PROJECT_ID
gcloud auth configure-docker $REGION-docker.pkg.dev

# Push image
docker tag chexnet-app:local $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/chexnet-app:$TAG
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/chexnet-app:$TAG

# Deploy
kubectl apply -f K8s/production.yaml
```

**Environments:**
- `chexnet-dev`: Development (1 replica, ClusterIP)
- `chexnet-test`: Testing (1 replica, ClusterIP)
- `chexnet-prod`: Production (1-2 replicas with HPA, ClusterIP by default)

## Clinical Considerations

⚠️ **Important**: This application is for **research and educational purposes only**. It is **NOT** intended for clinical diagnosis or patient care.

### Limitations
- Model trained on limited dataset; performance varies by image quality
- Not a replacement for radiologist review
- Results should be validated by qualified medical professionals
- No accountability for incorrect predictions
- Consider demographic and population-specific biases

### Recommendations
- Use as supplementary tool, not diagnostic decision-maker
- Always correlate with clinical presentation
- Escalate uncertain or high-risk cases
- Maintain proper medical imaging protocols

## Development

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Running Tests
```bash
# Smoke test: verify imports
python -c "from src.model import load_model; from src.gradcam import setup_gradcam; from src.report_generator import generate_report; print('✓ All imports OK')"

# Launch app
python app.py
```

### Code Structure

**app.py**: Main application
- Loads model and Grad-CAM at startup
- Defines `analyze()` function for inference
- Creates Gradio UI
- Handles image preprocessing and result formatting

**src/model.py**: Model management
- `CheXNet` class: DenseNet-121 wrapper with sigmoid output
- `load_model()`: Loads trained weights and prepares for inference

**src/gradcam.py**: Explainability
- `setup_gradcam()`: Configures Grad-CAM for target layers
- `generate_heatmap()`: Produces visualization overlay

**src/report_generator.py**: Clinical reporting
- `generate_report()`: Creates structured report based on probability
- `format_report_markdown()`: Formats for UI display
- `create_pdf_report()`: Exports to PDF file

## License

[Add your license here - e.g., MIT, Apache 2.0, etc.]

## Citation

If you use this project in research, please cite:

```bibtex
@article{rajpurkar2018chexnet,
  title={CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning},
  author={Rajpurkar, Pranav and others},
  journal={arXiv preprint arXiv:1711.05225},
  year={2017}
}
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourusername/chexnet-app/issues)
- Check existing documentation in [docs/](docs/)
- Review [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for known limitations

## Acknowledgments

- Rajpurkar et al. for CheXNet research
- PyTorch and torchvision communities
- Gradio for the excellent web UI framework
- PyTorch Grad-CAM for visualization tools

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Status**: Active Development
