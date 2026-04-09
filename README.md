# Blockchain-Based Voting System with Biometric Verification

A secure electronic voting system featuring dual-layer biometric verification (liveness detection + face recognition) and blockchain-based vote storage for tamper-proof elections.

## 🎯 Features

- **Liveness Detection** - AI-powered spoof detection to prevent photo/video attacks
- **Face Recognition** - InsightFace-based identity verification against registered voters
- **Blockchain Storage** - PostgreSQL-backed blockchain for immutable vote records
- **Admin Dashboard** - Voter registration with multi-photo face enrollment
- **Real-time Verification** - Webcam-based verification with instant feedback
- **Secure Voting Tokens** - Time-limited tokens issued after successful verification

## 📁 Project Structure

```
project_final/
├── frontend/                    # React + TypeScript frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   │   ├── FaceVerificationPage.tsx
│   │   │   ├── VotingPage.tsx
│   │   │   └── admin/          # Admin dashboard components
│   │   ├── services/api.ts     # API client
│   │   └── App.tsx             # Main application
│   └── package.json
│
├── backend/                     # FastAPI Python backend
│   ├── api/routes/             # API endpoints
│   │   ├── verification.py     # Liveness + face verification
│   │   ├── voting.py           # Vote submission
│   │   └── admin.py            # Voter registration
│   ├── services/
│   │   ├── liveness_service.py # Liveness detection model
│   │   ├── face_service.py     # Face recognition (InsightFace)
│   │   └── blockchain_service.py
│   ├── app.py                  # FastAPI application
│   ├── settings.py             # Configuration
│   └── requirements.txt
│
├── database/
│   ├── blockchain.py           # Blockchain implementation
│   └── schema.sql              # Database schema
│
├── models/
│   ├── liveness_detector_production.pth  # Trained liveness model
│   └── face_detector/          # OpenCV DNN face detector
│
├── data/
│   ├── voters.json             # Registered voters
│   ├── registered_faces/       # Face embeddings (.npy files)
│   └── candidates.csv          # Candidate data
│
└── notebooks/
    ├── liveness_training_clean.ipynb  # Liveness model training
    └── face_recognition.ipynb         # Face recognition experiments
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (for blockchain)
- Webcam

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python app.py
```

Backend runs on: **http://localhost:5001**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:5173**

### 3. Database Setup (Optional - for blockchain)

```bash
# Create PostgreSQL database
createdb voting_system

# Apply schema
psql voting_system < database/schema.sql
```

## 🔐 Verification Flow

1. **Voter enters Aadhaar number** on the authentication page
2. **Webcam captures multiple frames** for verification
3. **Liveness Detection** - AI model checks if it's a real face (not photo/video)
4. **Face Recognition** - Compares against registered voter's face embedding
5. **Voting Token issued** - 5-minute time-limited token for voting
6. **Vote submitted** - Anonymous vote hash stored on blockchain

## 🛡️ Security Features

| Feature | Description |
|---------|-------------|
| **Anti-Spoofing** | MobileNetV2-based model trained on OULU-NPU + Tapakah68 datasets |
| **Face Detection** | OpenCV DNN detector crops face before liveness check |
| **Embedding Comparison** | Cosine similarity with configurable threshold |
| **Vote Anonymity** | Only hashed votes stored, no voter-vote linkage |
| **Blockchain Integrity** | Chain verification prevents tampering |

## 🛠️ Technology Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- Lucide Icons

### Backend
- FastAPI (Python web framework)
- PyTorch (liveness detection model)
- InsightFace (face recognition)
- OpenCV (image processing)
- PostgreSQL + psycopg2 (blockchain storage)

### AI/ML
- MobileNetV2 backbone for liveness detection
- InsightFace buffalo_l model for face embeddings
- OpenCV DNN for face detection

## � Model Performance

| Model | Accuracy | Dataset |
|-------|----------|---------|
| Liveness Detection | 99.47% | OULU-NPU + Tapakah68 + Replay frames |
| Face Recognition | ~99% | InsightFace buffalo_l pretrained |

## 👤 Admin Access

- **URL**: http://localhost:5173 → "Admin Login"
- **Username**: `admin`
- **Password**: `admin123`

### Admin Features
- Register new voters with Aadhaar, phone, constituency
- Capture 3 photos for face embedding generation
- View registered voters and voting statistics

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/verify/complete` | POST | Complete verification (liveness + face) |
| `/api/vote/candidates/{constituency}` | GET | Get candidates for constituency |
| `/api/vote/submit` | POST | Submit vote with token |
| `/api/admin/register` | POST | Register new voter |
| `/api/admin/voters` | GET | List registered voters |

## 🧪 Testing

### Test Liveness Detection
1. Use the webcam with your real face → Should pass
2. Hold up a photo on your phone → Should show "Spoof Detected"

### Test Face Matching
1. Register a voter with your face
2. Verify with the same face → Should pass
3. Verify with a different person → Should show "Face Not Matched"

## 📝 License

Private project for educational purposes.
