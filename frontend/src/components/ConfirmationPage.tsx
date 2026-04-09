import React, { useEffect, useState } from 'react';
import { CheckCircle, Trophy, Home } from 'lucide-react';
import IndianFlagVotingLogo from './IndianFlagVotingLogo';

interface ConfirmationPageProps {
  onRestart: () => void;
}

const ConfirmationPage: React.FC<ConfirmationPageProps> = ({ onRestart }) => {
  const [showConfetti, setShowConfetti] = useState(false);
  const [animateFlag, setAnimateFlag] = useState(false);

  useEffect(() => {
    setShowConfetti(true);
    setAnimateFlag(true);

    const timer = setTimeout(() => {
      setShowConfetti(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Confetti Animation */}
      {showConfetti && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className={`absolute w-2 h-2 ${i % 3 === 0 ? 'bg-orange-500' : i % 3 === 1 ? 'bg-white' : 'bg-green-500'
                } animate-ping`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${1 + Math.random()}s`
              }}
            />
          ))}
        </div>
      )}

      <div className="w-full max-w-2xl z-10">
        <div className={`bg-gradient-to-r from-orange-500 via-white to-green-600 h-3 rounded-t-lg ${animateFlag ? 'animate-pulse' : ''}`}></div>
        <div className="bg-white rounded-b-lg shadow-2xl p-8 md:p-12">
          {/* Success Icon */}
          <div className="text-center mb-8">
            <div className="bg-green-100 p-6 rounded-full inline-block mb-6 animate-bounce">
              <CheckCircle className="w-16 h-16 text-green-600" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              Thank You for Voting!
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Your vote has been successfully recorded and encrypted.
              You have exercised your fundamental democratic right!
            </p>
          </div>

          {/* Logo Animation */}
          <div className="text-center mb-8">
            <div className={`inline-block ${animateFlag ? 'animate-wave' : ''}`}>
              <div className="bg-gradient-to-b from-orange-100 to-green-100 p-6 rounded-full shadow-lg border-2 border-gray-200">
                <IndianFlagVotingLogo size="lg" />
              </div>
            </div>
          </div>

          {/* Vote Statistics */}
          <div className="bg-gradient-to-r from-orange-50 to-green-50 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-center mb-4">
              <Trophy className="w-8 h-8 text-amber-600 mr-2" />
              <h3 className="text-xl font-semibold text-gray-800">Your Participation Matters</h3>
            </div>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="bg-white rounded-lg p-4">
                <div className="text-2xl font-bold text-orange-600">✓</div>
                <p className="text-sm text-gray-600">Vote Recorded</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">🔒</div>
                <p className="text-sm text-gray-600">Secure & Anonymous</p>
              </div>
            </div>
          </div>

          {/* Motivational Message */}
          <div className="text-center mb-8">
            <blockquote className="text-gray-600 italic mb-4">
              "Democracy is not just a political system, it is a way of life based on respect for human dignity."
            </blockquote>
            <p className="text-sm text-gray-500">- Dr. A.P.J. Abdul Kalam</p>
          </div>

          {/* Enhanced Bottom Pattern - Single Color Sequence */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-6">
              <div className="w-5 h-5 rounded-full bg-orange-500 shadow-lg animate-pulse"></div>
              <div className="w-5 h-5 rounded-full bg-white border-2 border-gray-300 shadow-lg animate-pulse" style={{ animationDelay: '0.5s' }}></div>
              <div className="w-5 h-5 rounded-full bg-green-600 shadow-lg animate-pulse" style={{ animationDelay: '1s' }}></div>
            </div>
          </div>

          {/* Action Button */}
          <div className="text-center">
            <button
              onClick={onRestart}
              className="bg-gradient-to-r from-orange-500 to-green-600 hover:from-orange-600 hover:to-green-700 text-white font-bold py-4 px-8 rounded-full text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 inline-flex items-center"
            >
              <Home className="w-5 h-5 mr-2" />
              Return to Home
            </button>
            <p className="text-sm text-gray-500 mt-4">
              Thank you for participating in India's democratic process
            </p>
          </div>
        </div>
      </div>


    </div>
  );
};

export default ConfirmationPage;