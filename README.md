# 🎬 YouTube Transcript Generator

> A fast, modern, and production-ready web application for extracting YouTube video transcripts with a clean user experience, intelligent caching, and built-in rate limiting.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production_Ready-success)
![Responsive](https://img.shields.io/badge/Responsive-Yes-brightgreen)

---

## 📖 Overview

YouTube Transcript Generator allows users to instantly retrieve transcripts from YouTube videos by simply pasting a video URL.

Designed with performance, scalability, and clean architecture in mind, this project demonstrates production-oriented backend development using Flask, efficient caching, robust error handling, and API protection.

---

## ✨ Features

### 🚀 Core Features

* Paste any YouTube video URL
* Automatic Video ID extraction
* Fetch transcripts in seconds
* Timestamped transcript view
* Plain text transcript view
* One-click copy transcript
* Download transcript as TXT
* Search within transcript
* Transcript statistics

  * Word count
  * Character count
  * Duration
  * Number of transcript segments

---

### ⚡ Performance

* Intelligent in-memory caching
* Automatic cache cleanup
* Retry mechanism with exponential backoff
* Reduced API calls
* Fast response times

---

### 🔒 Security

* API rate limiting
* Daily request quota
* Input validation
* Secure HTTP headers
* Graceful error handling
* Protection against abusive requests

---

### 📱 User Experience

* Responsive design
* Modern UI
* Loading indicators
* Error notifications
* Mobile friendly
* Clean typography

---

## 🏗️ Tech Stack

### Backend

* Python
* Flask
* Flask-Limiter
* youtube-transcript-api

### Frontend

* HTML5
* CSS3
* JavaScript (Vanilla)

### Deployment

* Gunicorn
* Render
* Cloudflare (optional)

---

## 📂 Project Structure

```text
.
├── app.py
├── requirements.txt
├── services/
│   └── transcript.py
├── static/
│   ├── style.css
│   ├── script.js
│   └── favicon.svg
└── templates/
    └── index.html
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Move into the project

```bash
cd YOUR_REPOSITORY
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

## 🌐 Live Demo

Try the application here:

🚀 https://yt-subtitle-generator-1.onrender.com

No installation required paste a YouTube URL and retrieve the transcript instantly.

## 🛡️ Production Features

* Request validation
* Centralized error handling
* Structured logging
* Rate limiting
* Intelligent caching
* Retry mechanism
* Security headers
* Health endpoint
* Scalable architecture
* Clean project structure

---

## 📈 Future Improvements

* Export as SRT
* Export as VTT
* Multi-language transcript selection
* AI-powered transcript summarization
* Chapter generation
* Keyword extraction
* Sentiment analysis
* Docker support
* Redis caching
* PostgreSQL support
* User authentication
* REST API documentation

---

## 💡 What This Project Demonstrates

This project showcases practical software engineering skills beyond basic CRUD applications.

* REST API development
* Backend architecture
* Production-ready Flask development
* API security
* Caching strategies
* Error handling
* Performance optimization
* Clean code organization
* Deployment readiness

---

## 🤝 Contributing

Contributions, feature requests, and bug reports are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Mohit Bhatt**

Master's in Computer Science

If you found this project useful, consider giving it a ⭐ on GitHub.

