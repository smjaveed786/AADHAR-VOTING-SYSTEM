import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, Camera, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react';
import IndianFlagVotingLogo from './IndianFlagVotingLogo';

import { api } from '../services/api';

interface VerificationResult {
  constituencyNo: number;
  voterId: string;
  token: string;
}

interface AlreadyVotedInfo {
  votedAt: string;
}

interface FaceVerificationPageProps {
  aadhaar: string;
  onSuccess: (data: VerificationResult) => void;
  onBack: () => void;
}

const FaceVerificationPage: React.FC<FaceVerificationPageProps> = ({ aadhaar, onSuccess, onBack }) => {
  const [step, setStep] = useState<'instructions' | 'capture' | 'processing' | 'already_voted' | 'spoof_detected' | 'face_not_matched'>('instructions');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string>('');
  const [cameraReady, setCameraReady] = useState(false);
  const [videoElementReady, setVideoElementReady] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [alreadyVotedInfo, setAlreadyVotedInfo] = useState<AlreadyVotedInfo | null>(null);

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
    };
  }, [stream]);

  // Effect to handle step changes and ensure video element is ready
  useEffect(() => {
    if (step === 'capture' && videoRef.current) {
      console.log('Video element is now available in DOM');
      setVideoElementReady(true);
    } else {
      setVideoElementReady(false);
    }
  }, [step]);

  // Effect to start camera when video element becomes ready
  useEffect(() => {
    if (videoElementReady && step === 'capture' && !stream) {
      console.log('Starting camera automatically...');
      startCamera();
    }
  }, [videoElementReady, step, stream]);

  const startCamera = async () => {
    try {
      setError('');
      setCameraReady(false);
      console.log('Requesting camera access...');

      // Stop any existing stream first
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }

      // Check if video element is available
      if (!videoRef.current) {
        console.error('Video element not found in DOM');
        setError('Camera interface not ready. Please try again in a moment.');
        return;
      }

      const constraints = {
        video: {
          width: { ideal: 640, min: 320, max: 1280 },
          height: { ideal: 480, min: 240, max: 720 },
          facingMode: 'user'
        },
        audio: false
      };

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      console.log('Camera access granted');

      // Double check video element is still available
      if (videoRef.current) {
        const video = videoRef.current;

        video.onloadedmetadata = () => {
          video.play().then(() => setCameraReady(true)).catch(console.error);
        };

        // Assign the stream
        video.srcObject = mediaStream;
        setStream(mediaStream);
      } else {
        // Clean up the stream if video element is not available
        mediaStream.getTracks().forEach(track => track.stop());
        throw new Error('Video element became unavailable during setup');
      }
    } catch (err) {
      console.error('Camera access error:', err);
      let errorMessage = 'Unable to access camera. ';

      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          errorMessage += 'Please allow camera permissions in your browser and try again.';
        } else if (err.name === 'NotFoundError') {
          errorMessage += 'No camera found on this device.';
        } else if (err.name === 'NotReadableError') {
          errorMessage += 'Camera is being used by another application. Please close other camera apps and try again.';
        } else if (err.name === 'OverconstrainedError') {
          errorMessage += 'Camera does not support the required settings.';
        } else if (err.message.includes('Video element')) {
          errorMessage += 'Camera interface not ready. Please wait a moment and try again.';
        } else {
          errorMessage += `Error: ${err.message}. Please check permissions and try again.`;
        }
      }

      setError(errorMessage);
      setStep('instructions');
    }
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current || !cameraReady) {
      setError('Camera not ready. Please wait for the camera to load and try again.');
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;

    // Ensure video is playing and has valid dimensions
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      setError('Video dimensions not available. Please ensure camera is working.');
      return;
    }

    try {
      console.log('Starting verification process...');
      setStep('processing');
      setError('');

      // Capture 3 frames
      const frames: string[] = [];
      const context = canvas.getContext('2d');
      if (!context) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      for (let i = 0; i < 3; i++) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        frames.push(canvas.toDataURL('image/jpeg', 0.8));
        await new Promise(resolve => setTimeout(resolve, 200)); // 200ms delay
      }

      // Stop stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
      setCameraReady(false);
      setCapturedImage(frames[0]); // Show first frame

      // Call API
      const result = await api.verification.complete(aadhaar || "123456789012", frames);

      if (result.success) {
        setSuccess(true);
        // Store token if needed, or app logic handles it
        // The result has constituency_no
        setTimeout(() => {
          onSuccess({
            constituencyNo: result.constituency_no,
            voterId: result.voter_id,
            token: result.token
          });
        }, 2000);
      } else if (result.stage === 'already_voted') {
        // Handle already voted case - show dedicated screen
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
          setStream(null);
        }
        setAlreadyVotedInfo({ votedAt: result.voted_at || '' });
        setStep('already_voted');
      } else {
        throw new Error(result.message || "Verification failed");
      }

    } catch (err: any) {
      console.error('Error verifying:', err);
      // Show dedicated screens for different failure types
      if (err.message && (err.message.includes('Spoof') || err.message.includes('Liveness check failed'))) {
        setStep('spoof_detected');
      } else if (err.message && (err.message.includes('Face verification failed') || err.message.includes('similarity') || err.message.includes('match') || err.message.includes('Match'))) {
        setStep('face_not_matched');
      } else {
        setError(err.message || 'Verification process failed. Please try again.');
        setStep('instructions');
        startCamera();
      }
    }
  };

  const retakePhoto = () => {
    console.log('Retaking photo - cleaning up...');
    setCapturedImage('');
    setCameraReady(false);
    setStep('instructions');
    setSuccess(false);
    setError('');

    // Clean up video stream
    if (stream) {
      stream.getTracks().forEach(track => {
        track.stop();
        console.log('Camera track stopped during retake');
      });
      setStream(null);
    }

    // Clean up video element
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  // Format the voted_at timestamp for display
  const formatVotedTime = (isoString: string) => {
    if (!isoString) return 'Unknown time';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-IN', {
        dateStyle: 'full',
        timeStyle: 'short',
        timeZone: 'Asia/Kolkata'
      });
    } catch {
      return isoString;
    }
  };

  // Already voted screen
  if (step === 'already_voted') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
          <div className="bg-white rounded-b-lg shadow-xl p-8 text-center">
            <div className="bg-blue-100 p-4 rounded-full inline-block mb-6">
              <CheckCircle className="w-12 h-12 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">You Have Already Voted</h2>
            <p className="text-gray-600 mb-4">
              Your vote has been securely recorded on the blockchain.
            </p>
            {alreadyVotedInfo?.votedAt && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <p className="text-sm text-gray-500 mb-1">Vote cast on:</p>
                <p className="text-lg font-semibold text-gray-800">
                  {formatVotedTime(alreadyVotedInfo.votedAt)}
                </p>
              </div>
            )}
            <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded-md text-left">
              <p className="text-sm text-green-700">
                <strong>Thank you for participating!</strong> Your vote contributes to the democratic process.
              </p>
            </div>
            <button
              onClick={onBack}
              className="w-full bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
            >
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Spoof detected screen
  if (step === 'spoof_detected') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
          <div className="bg-white rounded-b-lg shadow-xl p-8 text-center">
            <div className="bg-red-100 p-4 rounded-full inline-block mb-6">
              <AlertCircle className="w-12 h-12 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-red-700 mb-4">Spoof Detected!</h2>
            <p className="text-gray-600 mb-4">
              Our security system detected that you may be using a photo or video instead of your real face.
            </p>
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-md text-left">
              <p className="text-sm text-red-700 mb-2">
                <strong>For security reasons, verification failed.</strong>
              </p>
              <p className="text-sm text-red-600">
                Please ensure you are presenting your real face directly to the camera, not a photo or screen.
              </p>
            </div>
            <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6 rounded-md text-left">
              <p className="text-sm text-amber-800 font-medium mb-2">Tips for successful verification:</p>
              <ul className="text-sm text-amber-700 space-y-1">
                <li>• Use your real face, not a photo</li>
                <li>• Ensure good lighting conditions</li>
                <li>• Face the camera directly</li>
                <li>• Remove any obstructions</li>
              </ul>
            </div>
            <button
              onClick={() => {
                setStep('instructions');
                setError('');
                startCamera();
              }}
              className="w-full bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Face not matched screen
  if (step === 'face_not_matched') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
          <div className="bg-white rounded-b-lg shadow-xl p-8 text-center">
            <div className="bg-orange-100 p-4 rounded-full inline-block mb-6">
              <AlertCircle className="w-12 h-12 text-orange-600" />
            </div>
            <h2 className="text-2xl font-bold text-orange-700 mb-4">Face Not Matched</h2>
            <p className="text-gray-600 mb-4">
              Your face does not match the registered voter profile for this Aadhaar number.
            </p>
            <div className="bg-orange-50 border-l-4 border-orange-400 p-4 mb-6 rounded-md text-left">
              <p className="text-sm text-orange-700 mb-2">
                <strong>Identity verification failed.</strong>
              </p>
              <p className="text-sm text-orange-600">
                Please ensure you are the registered voter associated with this Aadhaar number.
              </p>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6 rounded-md text-left">
              <p className="text-sm text-blue-800 font-medium mb-2">Possible reasons:</p>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Wrong Aadhaar number entered</li>
                <li>• Poor lighting affecting face detection</li>
                <li>• Significant appearance change since registration</li>
                <li>• Camera angle or positioning issue</li>
              </ul>
            </div>
            <div className="flex gap-3">
              <button
                onClick={onBack}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-6 rounded-lg transition-all duration-300"
              >
                Go Back
              </button>
              <button
                onClick={() => {
                  setStep('instructions');
                  setError('');
                  startCamera();
                }}
                className="flex-1 bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'processing') {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
          <div className="bg-white rounded-b-lg shadow-xl p-8 text-center">
            {success ? (
              <>
                <div className="bg-green-100 p-4 rounded-full inline-block mb-6">
                  <CheckCircle className="w-12 h-12 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Face Verified Successfully!</h2>
                <p className="text-gray-600 mb-6">Identity confirmed. Redirecting to voting page...</p>
                {capturedImage && (
                  <div className="mb-4">
                    <img
                      src={capturedImage}
                      alt="Captured face"
                      className="w-32 h-32 rounded-full mx-auto object-cover border-4 border-green-500"
                    />
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="bg-blue-100 p-4 rounded-full inline-block mb-6">
                  <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Verifying Your Identity</h2>
                <p className="text-gray-600 mb-6">Please wait while we process your verification...</p>
                {capturedImage && (
                  <div className="mb-4">
                    <img
                      src={capturedImage}
                      alt="Captured face"
                      className="w-32 h-32 rounded-full mx-auto object-cover border-4 border-blue-500"
                    />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
        <div className="bg-white rounded-b-lg shadow-xl p-8">
          <button
            onClick={onBack}
            className="flex items-center text-gray-600 hover:text-gray-800 mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </button>

          <div className="mb-8">
            <div className="flex items-center justify-center mb-6">
              <div className="bg-gradient-to-r from-orange-500 to-green-600 p-3 rounded-full">
                {step === 'instructions' ? (
                  <IndianFlagVotingLogo size="md" />
                ) : (
                  <Camera className="w-8 h-8 text-white" />
                )}
              </div>
            </div>
            <h1 className="text-2xl font-bold text-gray-800 text-center mb-2">
              Face Verification
            </h1>
            <p className="text-gray-600 text-center">
              {step === 'instructions'
                ? 'Secure your vote with biometric verification'
                : 'Position your face in the frame and click capture'
              }
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-md">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {step === 'instructions' ? (
            <div>
              <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6 rounded-md">
                <div className="flex items-start">
                  <Lightbulb className="w-5 h-5 text-amber-500 mr-2 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-amber-800 mb-2">Tips for successful verification:</h3>
                    <ul className="text-sm text-amber-700 space-y-1">
                      <li>• Ensure proper lighting on your face</li>
                      <li>• Face the camera directly</li>
                      <li>• Remove sunglasses or face coverings</li>
                      <li>• Keep a neutral expression</li>
                      <li>• Stay still during capture</li>
                    </ul>
                  </div>
                </div>
              </div>

              <button
                onClick={() => {
                  setError('');
                  setStep('capture');
                }}
                className="w-full bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
              >
                Start Camera
              </button>
            </div>
          ) : (
            <div>
              <div className="relative mb-6 rounded-lg overflow-hidden bg-gray-900">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-96 object-cover"
                  style={{ transform: 'scaleX(-1)' }} // Mirror effect for selfie
                  onLoadedMetadata={() => console.log('Video metadata loaded event')}
                  onCanPlay={() => console.log('Video can play event')}
                  onPlay={() => console.log('Video play event')}
                  onError={(e) => console.error('Video element error:', e)}
                />
                {!cameraReady && (
                  <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
                    <div className="text-center text-white">
                      <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      <p className="text-sm">Initializing camera...</p>
                    </div>
                  </div>
                )}
                <div className="absolute inset-0 border-4 border-dashed border-white/50 rounded-lg m-4"></div>
                <div className="absolute top-4 left-4 right-4">
                  <div className="bg-black/70 text-white px-3 py-1 rounded-full text-sm text-center">
                    {cameraReady ? 'Position your face within the frame' : 'Loading camera...'}
                  </div>
                </div>
                {/* Face outline guide */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-48 h-56 border-2 border-green-400 rounded-full opacity-50"></div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={capturePhoto}
                  disabled={!cameraReady}
                  className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 disabled:cursor-not-allowed"
                >
                  {cameraReady ? 'Capture Photo' : 'Loading...'}
                </button>
                <button
                  onClick={retakePhoto}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <canvas ref={canvasRef} className="hidden" />
        </div>
      </div>
    </div>
  );
};

export default FaceVerificationPage;