# OCR Web Application

A modern, production-ready web application for extracting text from images and PDFs using advanced OCR technology. Built with FastAPI, React, and Tesseract OCR.

![OCR Web Application](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## ✨ Features

- 🎯 **High Accuracy OCR** - Advanced preprocessing pipeline for maximum text extraction accuracy
- 📁 **Multiple Format Support** - PNG, JPG, JPEG, and PDF files up to 10MB
- 🎨 **Modern UI** - Clean, professional interface inspired by Notion/Vercel/Linear
- 📊 **Confidence Metrics** - Real-time confidence scores and word count statistics
- 🚀 **Fast Processing** - Optimized image preprocessing and OCR extraction
- 💾 **Export Options** - Copy to clipboard or download as TXT file
- 🔒 **Secure** - File validation, sanitization, and automatic cleanup
- 🐳 **Docker Ready** - Containerized deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Tailwind CSS) │
└────────┬────────┘
         │ HTTP/JSON
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (Python 3.11)  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ Image  │ │ Tesseract│
│Preproc │ │   OCR    │
└────────┘ └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Tesseract OCR
- npm or yarn

### Installation

#### 1. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

#### 2. Clone Repository

```bash
cd "/home/ayham/Documents/OCR Application Online"
```

#### 3. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

#### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t ocr-app .

# Run container
docker run -p 8000:8000 ocr-app
```

## 📡 API Documentation

### Endpoints

#### `POST /api/ocr`
Extract text from uploaded image or PDF.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image or PDF)

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "Extracted text content...",
    "confidence": 92.5,
    "word_count": 150,
    "language": "eng",
    "original_filename": "document.pdf"
  },
  "message": "Text extracted successfully"
}
```

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "OCR Web Application",
  "version": "1.0.0"
}
```

#### `GET /api/languages`
Get supported OCR languages.

**Response:**
```json
{
  "languages": [
    {"code": "eng", "name": "English"},
    {"code": "spa", "name": "Spanish"}
  ],
  "default": "eng"
}
```

### Interactive API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

Edit `.env` file to customize settings:

```env
# Application
APP_NAME=OCR Web Application
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.png,.jpg,.jpeg,.pdf

# OCR
TESSERACT_LANG=eng
TESSERACT_CONFIG=--oem 3 --psm 3

# Processing
MAX_IMAGE_DIMENSION=4000
TARGET_DPI=300
```

## 🧪 Testing

### Backend Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

### Frontend Build Test

```bash
cd frontend
npm run build
```

## 📂 Project Structure

```
OCR Application Online/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── validators.py        # File validation
│   ├── ocr_processor.py     # OCR processing logic
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   └── docker-compose.yml  # Docker Compose setup
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main application
│   │   ├── components/
│   │   │   ├── UploadArea.jsx
│   │   │   ├── ResultsPanel.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── index.css       # Global styles
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
└── README.md
```

## 🎨 Design Philosophy

This application follows modern SaaS design principles:

- **Minimalist** - Clean, uncluttered interface
- **Professional** - Polished UI suitable for production
- **Responsive** - Works seamlessly on all devices
- **Accessible** - Clear visual hierarchy and feedback
- **Performant** - Optimized for speed and efficiency

## 🚀 Deployment

### Recommended Platforms

**Backend:**
- Railway.app (easiest, auto-detects Dockerfile)
- Render.com (free tier available)
- Google Cloud Run (serverless)
- AWS ECS/Fargate (production-grade)

**Frontend:**
- Vercel (optimized for React)
- Netlify (simple deployment)
- Cloudflare Pages (fast CDN)

### Environment Variables for Production

```env
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com
```

## 🔒 Security Features

- ✅ File size validation (10MB limit)
- ✅ MIME type verification
- ✅ Filename sanitization
- ✅ Path traversal protection
- ✅ Automatic file cleanup
- ✅ CORS configuration
- ✅ Error handling and logging

## ⚡ Performance Optimizations

- Image preprocessing pipeline (grayscale, blur, threshold)
- Automatic image resizing for large files
- Efficient temporary file management
- Optimized Tesseract configuration
- React component memoization
- Vite build optimization

## 🐛 Troubleshooting

### Tesseract Not Found

```bash
# Check if Tesseract is installed
tesseract --version

# If not found, install it (Ubuntu/Debian)
sudo apt-get install tesseract-ocr
```

### Port Already in Use

```bash
# Change port in .env file
PORT=8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### CORS Errors

Add your frontend URL to `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:5173,https://your-domain.com
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, React, and Tesseract OCR
