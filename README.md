# AI Interview Services

A comprehensive AI-powered interview system with question generation and intelligent interview management.

## 🏗️ Project Structure

```
GENAI/
├── README.md                 # This file
├── requirements.txt          # Main Python dependencies
├── .gitignore               # Git ignore patterns
│
├── 📂 generator/            # Question Generator Service
│   ├── main.py              # FastAPI backend
│   ├── streamlit_app.py     # Streamlit frontend
│   ├── requirements.txt     # Service dependencies
│   └── ...
│
├── 📂 interview/            # Interview Conductor Service  
│   ├── main.py              # FastAPI backend
│   ├── streamlit_app.py     # Streamlit frontend
│   ├── requirements.txt     # Service dependencies
│   └── ...
│
├── 📂 utils/                # Shared Utilities
│   ├── gemini.py            # Google AI integration
│   ├── perplexcity.py       # Perplexity API integration
│   └── ...
│
├── 📂 scripts/              # Management Scripts
│   ├── deploy.sh            # Deploy to Google Cloud
│   ├── setup-gcloud.sh      # Initial GCP setup
│   ├── services-up.sh       # Scale up all services
│   ├── services-down.sh     # Scale down all services
│   └── services-status.sh   # Check service status
│
├── 📂 config/               # Configuration Files
│   ├── docker-compose.yml   # Local development
│   ├── env_template.txt     # Environment variables template
│   └── deploy/              # Cloud deployment configs
│       ├── backend.yaml
│       └── frontend.yaml
│
└── 📂 docs/                 # Documentation
    ├── DEPLOYMENT.md        # Deployment guide
    └── SERVICE_MANAGEMENT.md # Service management guide
```

## 🚀 Quick Start

### 1. **Scale Up Services**
```bash
./scripts/services-up.sh
```

### 2. **Access Your Applications**
- **📝 Question Generator**: Create and manage interview questions
- **🤖 Interview System**: Conduct AI-powered interviews

### 3. **Scale Down When Done** (Save Costs)
```bash
./scripts/services-down.sh
```

## 🔧 Development

### Local Development
```bash
# Run with Docker Compose
docker-compose -f config/docker-compose.yml up
```

### Check Service Status
```bash
./scripts/services-status.sh
```

## 📚 Documentation

- **[🚀 Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - **START HERE** - Complete step-by-step deployment
- **[Service Management](docs/SERVICE_MANAGEMENT.md)** - Managing your services
- **[Generator Service](generator/README_STREAMLIT.md)** - Question generator details
- **[Interview Service](interview/README.md)** - Interview system details

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Streamlit
- **Database**: MongoDB (Cloud)
- **AI**: Google Gemini, Perplexity API
- **Deployment**: Google Cloud Run
- **Containerization**: Docker

## 💰 Cost Management

The project includes built-in cost optimization:
- **Active Development**: ~$10-50/month
- **Scaled Down**: ~$1-5/month  
- **Automatic Scaling**: Services scale to 0 when idle

## 🤝 Support

Check the documentation in the `docs/` folder for detailed guides on deployment, management, and troubleshooting. 