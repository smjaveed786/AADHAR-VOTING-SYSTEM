# FORM 2
## THE PATENTS ACT, 1970
### (39 of 1970)
### AND
## THE PATENTS RULES, 2003
## COMPLETE SPECIFICATION
### (See Section 10; rule 13)

---

# TITLE OF THE INVENTION

## Secure Electronic Voting System with Aadhaar-OTP Verification, Face Recognition, Anti-Spoofing Liveness Detection and Blockchain Based Anonymous Vote Storage

---

## Field and Background of this Invention

The present invention relates to the application of deep learning and computer vision in secure electronic voting systems and biometric authentication domains. It discloses a novel system for voter identity verification that integrates real-time liveness detection using convolutional neural networks, face recognition using deep neural networks, two-factor authentication via OTP, and blockchain technology for anonymous and tamper-proof vote recording.

Electronic voting systems have gained significant attention worldwide due to their potential to increase voter participation, reduce costs, and provide faster results. However, existing e-voting solutions face critical challenges related to voter identity verification and prevention of fraudulent activities. Traditional voting systems rely on physical identity documents and manual verification, which are prone to human error and impersonation attacks. Earlier digital voting implementations using simple password-based authentication or basic biometric matching have proven vulnerable to various spoofing attacks including presentation of photographs, video replays, and 3D masks.

The lack of robust anti-spoofing mechanisms in current biometric voting systems poses a significant security threat. Malicious actors can potentially use printed photographs, recorded videos, or digital displays showing a legitimate voter's face to bypass facial recognition systems. This vulnerability undermines the integrity of the entire electoral process and erodes public trust in electronic voting mechanisms.

The present invention addresses these critical gaps by implementing a comprehensive dual-layer verification architecture that combines deep learning based liveness detection with face recognition, supplemented by OTP-based two-factor authentication, ensuring that only legitimate, physically present voters can cast their votes.

---

## Summary of this Invention

The current invention provides a secure voter verification and voting system that comprises:

- A two-factor authentication module that validates voter identity through Aadhaar number verification and OTP sent to the registered mobile number.

- A real-time liveness detection module utilizing a MobileNetV2-based deep learning model that analyzes video frames to distinguish between live persons and spoofing attempts such as photographs, video replays, and printed cutouts.

- A face recognition module employing InsightFace with ArcFace architecture that generates 512-dimensional facial embeddings and compares them against pre-registered voter embeddings using cosine similarity matching.

- A voter registration subsystem that captures multiple facial images, extracts embeddings, and stores averaged normalized embeddings for enhanced matching accuracy.

- A blockchain-based vote recording mechanism that creates anonymous vote hashes using SHA-256, ensuring vote integrity while maintaining voter anonymity.

- A web-based user interface that delivers real-time verification feedback and provides a secure voting interface accessible from standard browsers.

The complete system provides multi-layered security verification in a single integrated deployment.

---

## Detailed Description of this Invention

The system includes several interconnected components that work systematically to ensure secure voter authentication and anonymous vote recording. This invention utilizes camera-based video capture, deep learning models for liveness detection and face recognition, cryptographic hashing for vote anonymization, and blockchain technology for immutable vote storage.

### Two-Factor Authentication Module

The authentication process initiates with Aadhaar-based identity verification where voters enter their 12-digit Aadhaar number. The system validates the format and triggers an OTP generation sent to the voter's registered mobile number. The OTP has a limited validity period and supports resend functionality.

### Video Frame Acquisition

The system captures real-time video frames from the voter's device camera. Multiple frames are captured to enable temporal analysis and majority voting in liveness detection, improving accuracy over single-frame approaches.

### Pre-processing Pipeline

The captured video frames undergo preprocessing including color space conversion, image resizing, normalization, and tensor conversion for model inference.

### Liveness Detection

A MobileNetV2-based convolutional neural network performs real-time spoof detection with binary classification output distinguishing Real (live person) from Spoof (attack). Multiple frames are analyzed independently and results are aggregated using majority voting. A verdict of "SPOOF" is returned if the majority of frames indicate spoofing attempts.

### Face Recognition and Matching

The face recognition module utilizes InsightFace with RetinaFace for face detection and ArcFace for embedding extraction, generating 512-dimensional normalized vectors. Cosine similarity computation is used for face matching with configurable threshold.

During voter registration, multiple photographs are captured from different angles, embeddings are extracted and averaged to create a robust reference embedding. During verification, embeddings from live video frames are compared against the registered embedding using cosine similarity.

### Dual-Layer Verification Flow

The complete verification implements sequential dual-layer security:

1. Liveness detection is performed first on submitted video frames
2. If liveness check fails, verification is immediately rejected
3. If liveness check passes, face recognition proceeds
4. Face embedding is extracted and compared against registered embedding
5. If similarity exceeds threshold, a time-limited voting token is issued

This sequential approach ensures that spoofing attempts are blocked before face matching occurs.

### Blockchain-Based Anonymous Vote Recording

Upon successful verification, voters receive a cryptographic token enabling vote submission. The voting process implements complete anonymity through:

- Vote hash generation using SHA-256 combining voter_id, timestamp, candidate_id, and random salt
- Storage of only the hash and candidate selection in the blockchain, with no voter identification
- Immutable chain structure with each block containing previous block hash

This architecture ensures that individual votes cannot be traced back to specific voters, maintaining ballot secrecy.

### Administrative Interface

The system includes a secure administrative dashboard with JWT-based authentication, voter registration interface, constituency and candidate management, and real-time voting statistics.

### Architecture

The system architecture comprises a React-based frontend, Python FastAPI backend, PostgreSQL database for voter data and blockchain storage, with RESTful API endpoints.

---

## Claims

1. A secure voter verification system comprising Aadhaar-OTP based two-factor authentication, real-time liveness detection using deep learning, and face recognition using ArcFace embeddings, wherein verification tokens are issued only upon successful completion of all authentication layers.

2. A method for preventing biometric spoofing comprising capturing multiple video frames, processing each frame through a MobileNetV2-based classifier, and aggregating predictions using majority voting to reject spoofing attempts.

3. The method as claimed in claim 2, wherein liveness detection classifies frames as Real (live person) or Spoof (presentation attack including photographs, video replays, and printed materials).

4. A dual-layer verification architecture that performs liveness detection before face recognition, wherein face matching proceeds only after successful liveness verification.

5. The system as claimed in claim 1, wherein face recognition generates 512-dimensional embeddings using ArcFace and performs matching using cosine similarity.

6. A voter registration method comprising capturing multiple facial photographs, extracting and averaging embeddings, and storing normalized embeddings as reference templates.

7. A blockchain-based anonymous vote recording system wherein votes are stored as SHA-256 hashes with only hash and candidate information persisted, maintaining voter anonymity.

8. The system as claimed in claim 7, wherein each block contains the previous block hash for chain integrity verification.

9. A time-limited voting token mechanism wherein successful verification issues a token with defined expiration, requiring re-verification upon expiry.

10. The system as claimed in claim 1, wherein the interface is a web application with real-time camera preview and verification feedback.

---

## Challenges and Considerations

Implementing this system involves addressing several technical challenges such as lighting variability affecting facial recognition accuracy, which is handled through user guidance and robust model design. Device compatibility issues arising from varying camera qualities are managed through adaptive resolution handling. Network latency concerns for real-time verification are addressed through frame compression and optimized API payloads. The MobileNetV2 architecture provides an excellent accuracy-to-size ratio suitable for web deployment. The modular architecture allows model updates to counter evolving spoofing attack methods without requiring system redesign.

---

## Novelty and Patentability

The novelty lies in the integrated dual-layer verification approach for electronic voting. Unlike conventional systems relying solely on face matching, this system implements sequential liveness-first architecture where liveness detection must succeed before face recognition, preventing spoofing attacks from reaching identity matching. Multi-frame temporal analysis with majority voting reduces false acceptance rates. The integration of OTP-based two-factor authentication with biometric verification creates a three-layer security model (mobile phone, Aadhaar, face). The combination of dual-layer biometric verification with blockchain-based vote anonymization ensures both voter authenticity and ballot secrecy. The averaged multi-angle embedding registration improves matching accuracy over single-image approaches.

---

## Abstract (150 words)

The invention presents a secure voter verification system integrating real-time liveness detection, face recognition, and blockchain-based anonymous vote recording. The system implements a dual-layer biometric verification architecture where liveness detection using a trained MobileNetV2 deep learning model precedes face recognition using ArcFace embeddings, ensuring that spoofing attempts are blocked before identity matching occurs. Two-factor authentication via Aadhaar validation and OTP verification provides preliminary identity confirmation. Multiple video frames are analyzed with majority voting aggregation for robust spoof detection. Successful verification issues time-limited cryptographic tokens enabling vote submission. Votes are recorded on a blockchain as anonymous hashes, maintaining ballot secrecy while ensuring immutability. The web-based interface provides real-time verification feedback and guides voters through the authentication process. This integrated approach addresses critical security vulnerabilities in existing electronic voting systems while maintaining usability and accessibility.

---

## Workflow of the Proposed System

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Aadhaar &     │    │   Video Frame   │    │    Liveness     │    │      Face       │
│ OTP Verification│───▶│    Capture      │───▶│   Detection     │───▶│  Recognition    │
│  (2FA Layer)    │    │  (Camera API)   │    │  (MobileNetV2)  │    │  (InsightFace)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │                       │
                                                      ▼                       ▼
                                               ┌─────────────┐         ┌─────────────┐
                                               │   SPOOF     │         │   MATCH     │
                                               │  Detected   │         │   Found     │
                                               └─────────────┘         └─────────────┘
                                                      │                       │
                                                      ▼                       ▼
                                               ┌─────────────┐         ┌─────────────┐
                                               │  REJECTED   │         │ Issue Token │
                                               │             │         │             │
                                               └─────────────┘         └─────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Confirmation  │◀───│   Blockchain    │◀───│  Anonymous Vote │◀───│    Voting       │
│    Receipt      │    │    Storage      │    │  Hash Creation  │    │   Interface     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Figure 1: Dual-Layer Biometric Voter Verification System with Blockchain-Based Anonymous Vote Recording**

---

## Technical Specifications

| Component | Technology | Specification |
|-----------|------------|---------------|
| Liveness Model | MobileNetV2 | 2.5M parameters, 99%+ accuracy |
| Face Detection | RetinaFace | 640x640 detection size |
| Face Embedding | ArcFace | 512-dimensional vectors |
| Similarity Metric | Cosine Similarity | Threshold: 0.5 |
| Hash Algorithm | SHA-256 | 256-bit output |
| Frontend | React + TypeScript | Vite build system |
| Backend | Python FastAPI | Async request handling |
| Database | PostgreSQL | Blockchain + voter storage |

---

*Document prepared for patent application under The Patents Act, 1970*
