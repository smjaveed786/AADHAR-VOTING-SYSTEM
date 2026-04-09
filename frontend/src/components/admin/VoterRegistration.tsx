import React, { useState, useRef, useEffect } from 'react';
import { Camera, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

interface VoterRegistrationProps {
    onCancel: () => void;
}

const VoterRegistration: React.FC<VoterRegistrationProps> = ({ onCancel }) => {
    const [formData, setFormData] = useState({
        name: '',
        aadhaar_number: '',
        phone_number: '',
        constituency_no: '',
    });

    const [photos, setPhotos] = useState<File[]>([]);
    const [photoPreviews, setPhotoPreviews] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');
    const [cameraReady, setCameraReady] = useState(false);

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [stream, setStream] = useState<MediaStream | null>(null);

    useEffect(() => {
        startCamera();
        return () => {
            stopCamera();
        };
    }, []);

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    const startCamera = async () => {
        try {
            setCameraReady(false);
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: 640, height: 480 },
                audio: false
            });

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                setStream(mediaStream);
                setCameraReady(true);
            }
        } catch (err) {
            setError('Could not access camera. Please allow permissions.');
        }
    };

    const capturePhoto = () => {
        if (!videoRef.current || !canvasRef.current || !cameraReady) return;

        if (photos.length >= 3) {
            setError('Maximum 3 photos allowed (Front, Left, Right)');
            return;
        }

        const canvas = canvasRef.current;
        const video = videoRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext('2d');
        if (!context) return;

        // Flip horizontally
        context.save();
        context.scale(-1, 1);
        context.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
        context.restore();

        canvas.toBlob((blob) => {
            if (blob) {
                const file = new File([blob], `photo_${photos.length + 1}.jpg`, { type: 'image/jpeg' });
                setPhotos(prev => [...prev, file]);
                setPhotoPreviews(prev => [...prev, URL.createObjectURL(blob)]);
            }
        }, 'image/jpeg', 0.9);
    };

    const clearPhotos = () => {
        setPhotos([]);
        setPhotoPreviews([]);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (photos.length < 1) {
            setError('At least 1 photo is required');
            return;
        }

        setLoading(true);

        try {
            await api.admin.registerVoter({
                ...formData,
                constituency_no: parseInt(formData.constituency_no),
                photos
            });
            setSuccess(true);
            stopCamera();
        } catch (err) {
            setError('Failed to register voter. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
                <div className="bg-green-100 p-4 rounded-full inline-block mb-6">
                    <CheckCircle className="w-12 h-12 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Voter Registered!</h2>
                <p className="text-gray-600 mb-6">
                    Voter ID has been generated and face data has been securely stored.
                </p>
                <button
                    onClick={onCancel}
                    className="bg-gray-900 text-white px-6 py-2 rounded-lg hover:bg-gray-800"
                >
                    Return to Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-800">New Voter Registration</h2>
                <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
                    Cancel
                </button>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded flex items-center">
                    <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                    <p className="text-red-700 text-sm">{error}</p>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Form Section */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                        <input
                            type="text"
                            required
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            value={formData.name}
                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Aadhaar Number</label>
                        <input
                            type="text"
                            required
                            pattern="[0-9]{12}"
                            maxLength={12}
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            value={formData.aadhaar_number}
                            onChange={e => setFormData({ ...formData, aadhaar_number: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                        <input
                            type="tel"
                            required
                            pattern="[0-9]{10}"
                            maxLength={10}
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            value={formData.phone_number}
                            onChange={e => setFormData({ ...formData, phone_number: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Constituency Number</label>
                        <input
                            type="number"
                            required
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            value={formData.constituency_no}
                            onChange={e => setFormData({ ...formData, constituency_no: e.target.value })}
                        />
                    </div>

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={loading || photos.length === 0}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Processing...' : 'Register Voter'}
                        </button>
                    </div>
                </form>

                {/* Camera Section */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Face Capture ({photos.length}/3)
                    </label>
                    <div className="relative rounded-lg overflow-hidden bg-black aspect-video mb-4">
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className={`w-full h-full object-cover ${!cameraReady ? 'hidden' : ''}`}
                            style={{ transform: 'scaleX(-1)' }}
                        />
                        {!cameraReady && (
                            <div className="absolute inset-0 flex items-center justify-center text-white">
                                <p>Loading Camera...</p>
                            </div>
                        )}
                        <canvas ref={canvasRef} className="hidden" />
                    </div>

                    <div className="flex space-x-2 mb-4">
                        <button
                            type="button"
                            onClick={capturePhoto}
                            disabled={photos.length >= 3 || !cameraReady}
                            className="flex-1 bg-white border border-gray-300 text-gray-700 font-medium py-2 rounded-lg hover:bg-gray-50 flex items-center justify-center disabled:opacity-50"
                        >
                            <Camera className="w-4 h-4 mr-2" />
                            Capture
                        </button>
                        <button
                            type="button"
                            onClick={clearPhotos}
                            disabled={photos.length === 0}
                            className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
                        >
                            <RefreshCw className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Previews */}
                    <div className="grid grid-cols-3 gap-2">
                        {[0, 1, 2].map((idx) => (
                            <div key={idx} className="aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200 relatiive">
                                {photoPreviews[idx] ? (
                                    <img src={photoPreviews[idx]} alt={`Capture ${idx + 1}`} className="w-full h-full object-cover" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                                        {idx === 0 ? 'Front' : idx === 1 ? 'Left' : 'Right'}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                        Capture 3 photos: 1 looking straight, 1 slightly left, 1 slightly right.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default VoterRegistration;
