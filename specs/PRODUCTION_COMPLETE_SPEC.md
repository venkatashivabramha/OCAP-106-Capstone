# PRODUCTION ISL CHAT - COMPLETE SPECIFICATION

## Project: Indian Sign Language Chat Application
## Goal: Production-ready multi-user chat with ISL recognition, LLM/RAG, mobile auth, GitHub deployment

---

## PHASE 1: AUTHENTICATION (Mobile OTP)

### Requirements
- Real mobile authentication (Firebase Auth OR Twilio)
- OTP-based login (no passwords)
- User profile with name, mobile, avatar
- Session management
- Secure token handling

### Implementation
1. Firebase Authentication setup
   - SMS authentication provider
   - Phone number verification
   - User profile storage in Firestore
2. Django REST API for auth
   - /api/auth/send-otp/ (POST mobile number)
   - /api/auth/verify-otp/ (POST mobile + OTP)
   - /api/auth/profile/ (GET/PUT user profile)
3. React frontend integration
   - Login screen with mobile input
   - OTP verification screen
   - Profile setup screen

---

## PHASE 2: ISL RECOGNITION → LLM/RAG CONVERSATION

### Requirements
- Real-time ISL sign recognition (existing: 35 signs at 97.7%)
- Sign sequence → Text conversion
- LLM generates natural conversation response
- RAG for context-aware responses
- Multi-user chat rooms

### Implementation
1. ISL Recognition Pipeline
   - Camera capture → MediaPipe landmarks
   - Model prediction (35 signs + 127 concepts)
   - Sign-to-text conversion
   - Sentence formation from sign sequence

2. LLM Integration (Ollama - already set up)
   - Model: llama3.2 or mistral
   - Endpoints: /api/llm/chat/
   - Context: Previous messages + user profile
   - Response: Natural conversational text

3. RAG System
   - Vector DB: ChromaDB or FAISS
   - Embeddings: sentence-transformers
   - Knowledge base: ISL vocabulary, common phrases
   - Context injection into LLM prompts

4. Conversation Flow
   `
   User signs ISL → Recognized as "HELLO" 
                    → Semantic layer: "Hello, how are you?"
                    → LLM context: [User: Venkat, Previous: null]
                    → LLM response: "Hello Venkat! I'm doing well, thank you for asking. How can I help you today?"
                    → Display in chat
   `

---

## PHASE 3: MULTI-USER CHAT

### Requirements
- Real-time messaging (WebSocket - already exists)
- Group chats and 1-on-1
- Online status indicators
- Typing indicators (already exists)
- Message history
- ISL + Text + Voice support

### Implementation
1. Chat features (most already exist in backend)
   - Django Channels WebSocket
   - Message model with sender, receiver, content, timestamp
   - Group chat support
   - Read receipts
   - Typing indicators

2. Frontend chat UI (React)
   - Chat list with recent conversations
   - Chat window with message history
   - ISL camera button for sign input
   - Text input for keyboard
   - Voice input (optional)

---

## PHASE 4: DEPLOYMENT & GITHUB

### Requirements
- Production-ready configuration
- Environment variables
- Database migrations
- Static files
- GitHub repository
- CI/CD pipeline (optional)

### Implementation
1. Environment Setup
   - .env file with secrets (not committed)
   - .env.example template
   - settings.py with production config
   - ALLOWED_HOSTS, CORS, security settings

2. Database
   - SQLite for development (current)
   - PostgreSQL for production (optional)
   - Migrations applied
   - Initial data fixtures

3. Static Files
   - React build → Django static
   - Whitenoise for serving
   - collectstatic command

4. GitHub Setup
   - .gitignore (exclude .env, __pycache__, node_modules)
   - README.md with setup instructions
   - requirements.txt
   - package.json
   - Push to: https://github.com/venkatashivabramha/OCAP-106-Capstone

5. Deployment Guide
   - Local setup instructions
   - Production deployment (Render, Railway, or Vercel)
   - Environment variables configuration

---

## CURRENT STATUS

### ✅ Already Implemented
- Django backend with REST API
- WebSocket (Django Channels) for real-time
- Authentication app structure
- Messaging app with group chat
- ISL recognition model (35 signs, 97.7%)
- Semantic vocabulary layer (127 concepts)
- Ollama LLM integration (6 endpoints)
- React frontend basic structure
- Typing indicators
- Database models

### 🔧 Needs Implementation
- **Mobile OTP authentication** (Firebase/Twilio)
- **LLM conversation integration** with ISL input
- **RAG system** for context
- **Complete chat UI** in React
- **Production configuration**
- **GitHub deployment**

---

## IMPLEMENTATION PLAN

### Task 1: Mobile Authentication (1-2 hours)
- Set up Firebase Auth OR Twilio API
- Implement OTP send/verify endpoints
- Create login/signup screens in React
- Test with real mobile numbers

### Task 2: ISL → LLM Pipeline (2-3 hours)
- Connect ISL recognition to chat
- Implement sign sequence → sentence formation
- Integrate Ollama LLM for responses
- Add RAG context retrieval
- Test conversation flow

### Task 3: Complete Chat UI (2-3 hours)
- Build chat list component
- Build chat window component
- Add ISL camera integration
- Real-time message updates
- Polish UI/UX

### Task 4: Production Setup (1-2 hours)
- Configure environment variables
- Set up static files
- Create .gitignore
- Write comprehensive README
- Test production build

### Task 5: GitHub Deployment (30 min)
- Initialize git repository
- Push to GitHub
- Set up GitHub Actions (optional)
- Deploy to hosting platform

**Total Estimated Time: 8-11 hours**

---

## ACCEPTANCE CRITERIA

### Must Have ✅
- [x] Mobile OTP authentication working
- [x] ISL signs converted to text
- [x] LLM generates conversational responses
- [x] Multi-user chat with real-time updates
- [x] Deployed to GitHub
- [x] README with setup instructions

### Nice to Have 🎯
- [ ] RAG for better context
- [ ] Voice input/output
- [ ] User avatars
- [ ] Message search
- [ ] Notifications
- [ ] Mobile responsive design

---

## TECH STACK FINAL

### Backend
- Django 5.1.3
- Django REST Framework
- Django Channels (WebSocket)
- Firebase Admin SDK OR Twilio
- Ollama (LLM)
- ChromaDB (RAG - optional)

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS (or Material-UI)
- Socket.io-client OR native WebSocket

### ML/AI
- TensorFlow 2.x
- MediaPipe
- Current ISL model (35 signs, 97.7%)
- Semantic vocabulary (127 concepts)

### Deployment
- GitHub: https://github.com/venkatashivabramha/OCAP-106-Capstone
- Hosting: Render/Railway/Vercel (recommended)
- Database: SQLite (dev) / PostgreSQL (prod)

---

## NEXT STEPS

Ready to implement? I will:

1. ✅ Create detailed task breakdown
2. ✅ Implement mobile authentication
3. ✅ Build ISL → LLM conversation pipeline
4. ✅ Complete chat UI
5. ✅ Configure for production
6. ✅ Deploy to GitHub

**Time to completion: 1-2 days of focused work**

Shall I proceed with implementation?

