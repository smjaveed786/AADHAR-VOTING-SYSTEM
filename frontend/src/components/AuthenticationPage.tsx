import React, { useState, useEffect } from 'react';
import { ArrowLeft, Smartphone, Shield, AlertCircle, CheckCircle } from 'lucide-react';
import IndianFlagVotingLogo from './IndianFlagVotingLogo';
import { api } from '../services/api';

interface AuthenticationPageProps {
  onSuccess: (aadhaar: string) => void;
  onBack: () => void;
}

const AuthenticationPage: React.FC<AuthenticationPageProps> = ({ onSuccess, onBack }) => {
  const [step, setStep] = useState<'aadhaar' | 'otp'>('aadhaar');
  const [aadhaar, setAadhaar] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const validateAadhaar = (value: string) => {
    return /^\d{12}$/.test(value);
  };

  const handleAadhaarSubmit = async () => {
    if (!validateAadhaar(aadhaar)) {
      setError('Please enter a valid 12-digit Aadhaar number');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.auth.sendOTP(aadhaar);
      setLoading(false);
      setOtpSent(true);
      setStep('otp');
      setCountdown(30);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || 'Failed to send OTP. Please try again.');
    }
  };

  const handleOtpSubmit = async () => {
    if (otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await api.auth.verifyOTP(aadhaar, otp);
      setLoading(false);
      if (result.success) {
        onSuccess(aadhaar);
      } else {
        setError(result.message || 'Invalid OTP. Please try again.');
      }
    } catch (err: any) {
      setLoading(false);
      setError(err.message || 'Failed to verify OTP. Please try again.');
    }
  };

  const resendOtp = async () => {
    setError('');
    try {
      await api.auth.sendOTP(aadhaar);
      setCountdown(30);
      setOtpSent(true);
    } catch (err: any) {
      setError(err.message || 'Failed to resend OTP. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
        <div className="bg-white rounded-b-lg shadow-xl p-8">
          {/* Back Button */}
          <button
            onClick={onBack}
            className="flex items-center text-gray-600 hover:text-gray-800 mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </button>

          {/* Authentication Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-center mb-6">
              <div className="bg-gradient-to-r from-orange-500 to-green-600 p-3 rounded-full">
                {step === 'aadhaar' ? (
                  <IndianFlagVotingLogo size="md" />
                ) : (
                  <Smartphone className="w-8 h-8 text-white" />
                )}
              </div>
            </div>
            <h1 className="text-2xl font-bold text-gray-800 text-center mb-2">
              {step === 'aadhaar' ? 'Verify Your Identity' : 'Enter OTP'}
            </h1>
            <p className="text-gray-600 text-center">
              {step === 'aadhaar' 
                ? 'Enter your Aadhaar number to proceed with secure authentication'
                : `We've sent a 6-digit OTP to your registered mobile number`
              }
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-md">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          )}

          {otpSent && step === 'otp' && (
            <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded-md">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                <p className="text-green-700">OTP sent successfully!</p>
              </div>
            </div>
          )}

          {step === 'aadhaar' ? (
            <form onSubmit={(e) => { e.preventDefault(); handleAadhaarSubmit(); }}>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Aadhaar Number
                </label>
                <input
                  type="text"
                  value={aadhaar}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '').slice(0, 12);
                    setAadhaar(value);
                    setError('');
                  }}
                  placeholder="Enter 12-digit Aadhaar number"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-center text-lg tracking-widest"
                  maxLength={12}
                />
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Your Aadhaar number is encrypted and secure
                </p>
              </div>
              <button
                type="submit"
                disabled={loading || !validateAadhaar(aadhaar)}
                className="w-full bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 disabled:from-gray-300 disabled:to-gray-400 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying...' : 'Send OTP'}
              </button>
            </form>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); handleOtpSubmit(); }}>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter OTP
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                    setOtp(value);
                    setError('');
                  }}
                  placeholder="000000"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-center text-2xl tracking-widest"
                  maxLength={6}
                />
                <div className="flex justify-end items-center mt-2">
                  {countdown > 0 ? (
                    <p className="text-xs text-gray-500">
                      Resend in {countdown}s
                    </p>
                  ) : (
                    <button
                      type="button"
                      onClick={resendOtp}
                      className="text-xs text-orange-600 hover:text-orange-800 underline"
                    >
                      Resend OTP
                    </button>
                  )}
                </div>
              </div>
              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-300 disabled:to-gray-400 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthenticationPage;