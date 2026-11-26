# ISL Chat App

Indian Sign Language conversational platform with Gemini AI, real-time chat, and voice playback.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env   # then add GEMINI_API_KEY
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend/isl-chat-ui
npm install && npm run dev
```

Login at http://localhost:5173 — OTP is 123456 (simulation mode).

## Features
- Mobile OTP authentication (Firebase / simulation)
- ISL sign recognition (35 signs, 97.7% accuracy)
- Gemini AI conversational responses
- Voice playback on every message (Gemini TTS / browser)
- Real-time WebSocket multi-user chat
- RAG-enhanced responses from ISL knowledge base

## Stack
Backend: Django 5, DRF, Channels, SimpleJWT
Frontend: React 19, TypeScript, Vite
AI: Google Gemini 2.0 Flash (free tier)
ML: TensorFlow/Keras, MediaPipe

## Env Variables
Copy backend/.env.example to backend/.env
GEMINI_API_KEY - free from https://aistudio.google.com/apikey
FIREBASE_SERVICE_ACCOUNT_KEY - optional, for real OTP

Repo: https://github.com/venkatashivabramha/OCAP-106-Capstone
