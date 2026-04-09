import React from 'react';
import { Shield, Users, CheckCircle } from 'lucide-react';
import IndianFlagVotingLogo from './IndianFlagVotingLogo';

interface LandingPageProps {
  onStart: () => void;
  onAdminLogin?: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStart, onAdminLogin }) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      {/* Header with Indian Flag Colors */}
      <div className="w-full max-w-3xl">
        <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg shadow-lg"></div>
        <div className="bg-white rounded-b-lg shadow-xl p-8 md:p-12">
          {/* Welcome Section */}
          <div className="text-center mb-12">
            <div className="flex justify-center mb-6">
              <div className="bg-gradient-to-r from-orange-500 to-green-600 p-4 rounded-full shadow-lg">
                <IndianFlagVotingLogo size="xl" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              भारतीय चुनाव प्रणाली
            </h1>
            <h2 className="text-2xl md:text-3xl font-semibold text-orange-600 mb-6">
              Indian Election System
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Exercise your fundamental right to vote in a secure, transparent, and user-friendly digital environment.
              Your voice matters in shaping India's future.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center p-6 bg-orange-50 rounded-xl hover:shadow-lg transition-all duration-300">
              <Shield className="w-10 h-10 text-orange-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Secure Authentication</h3>
              <p className="text-gray-600">Aadhaar-based verification with OTP and face recognition for maximum security</p>
            </div>
            <div className="text-center p-6 bg-green-50 rounded-xl hover:shadow-lg transition-all duration-300">
              <Users className="w-10 h-10 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Democratic Process</h3>
              <p className="text-gray-600">Transparent and fair voting system ensuring every citizen's voice is heard</p>
            </div>
            <div className="text-center p-6 bg-blue-50 rounded-xl hover:shadow-lg transition-all duration-300">
              <CheckCircle className="w-10 h-10 text-blue-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Easy & Accessible</h3>
              <p className="text-gray-600">User-friendly interface designed for citizens from all backgrounds</p>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <button
              onClick={onStart}
              className="bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 text-white font-bold py-4 px-12 rounded-full text-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              Start Voting Process
            </button>
            <p className="text-sm text-gray-500 mt-4">
              Secure • Transparent • Democratic
            </p>
            {onAdminLogin && (
              <div className="mt-4 flex justify-center">
                <button
                  onClick={onAdminLogin}
                  className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-900 text-gray-200 rounded-md transition-colors"
                >
                  🔐 Admin Portal
                </button>
              </div>
            )}
          </div>

          {/* Enhanced Bottom Pattern - Single Color Sequence */}
          <div className="mt-12 flex justify-center">
            <div className="flex items-center space-x-6">
              <div className="w-5 h-5 rounded-full bg-orange-500 shadow-lg animate-pulse"></div>
              <div className="w-5 h-5 rounded-full bg-white border-2 border-gray-300 shadow-lg animate-pulse" style={{ animationDelay: '0.5s' }}></div>
              <div className="w-5 h-5 rounded-full bg-green-600 shadow-lg animate-pulse" style={{ animationDelay: '1s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;