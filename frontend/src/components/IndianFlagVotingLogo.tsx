import React from 'react';

interface IndianFlagVotingLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const IndianFlagVotingLogo: React.FC<IndianFlagVotingLogoProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20'
  };

  return (
    <div className={`${sizeClasses[size]} ${className} relative`}>
      <svg 
        viewBox="0 0 100 100" 
        className="w-full h-full drop-shadow-lg"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Indian Flag Colors */}
          <linearGradient id="saffronGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#FF9933" />
            <stop offset="100%" stopColor="#FF6600" />
          </linearGradient>
          
          <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#138808" />
            <stop offset="100%" stopColor="#006600" />
          </linearGradient>
          
          {/* Shadow effect */}
          <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="rgba(0,0,0,0.3)"/>
          </filter>
        </defs>
        
        {/* Outer circle with shadow */}
        <circle 
          cx="50" 
          cy="50" 
          r="48" 
          fill="white"
          stroke="#ddd"
          strokeWidth="1"
          filter="url(#shadow)"
        />
        
        {/* Indian Flag Stripes */}
        {/* Saffron top stripe */}
        <path 
          d="M 15 25 Q 50 20 85 25 Q 85 35 85 40 Q 50 35 15 40 Q 15 35 15 25 Z" 
          fill="url(#saffronGradient)"
        />
        
        {/* White middle stripe */}
        <path 
          d="M 15 40 Q 50 35 85 40 Q 85 50 85 55 Q 50 50 15 55 Q 15 50 15 40 Z" 
          fill="white"
        />
        
        {/* Green bottom stripe */}
        <path 
          d="M 15 55 Q 50 50 85 55 Q 85 65 85 70 Q 50 65 15 70 Q 15 65 15 55 Z" 
          fill="url(#greenGradient)"
        />
        
        {/* Ashoka Chakra (enhanced) */}
        <circle 
          cx="50" 
          cy="47.5" 
          r="10" 
          fill="none" 
          stroke="#000080" 
          strokeWidth="1.5"
        />
        <circle 
          cx="50" 
          cy="47.5" 
          r="1.5" 
          fill="#000080"
        />
        
        {/* 24 spokes of Ashoka Chakra */}
        {Array.from({length: 24}, (_, i) => {
          const angle = (i * 15) * Math.PI / 180;
          const x1 = 50 + 3 * Math.cos(angle);
          const y1 = 47.5 + 3 * Math.sin(angle);
          const x2 = 50 + 9 * Math.cos(angle);
          const y2 = 47.5 + 9 * Math.sin(angle);
          return (
            <line 
              key={i}
              x1={x1} 
              y1={y1} 
              x2={x2} 
              y2={y2} 
              stroke="#000080" 
              strokeWidth="0.8"
            />
          );
        })}
        
        {/* Decorative elements in flag colors */}
        <circle cx="20" cy="30" r="2" fill="#FF9933" opacity="0.6" />
        <circle cx="80" cy="30" r="2" fill="#FF9933" opacity="0.6" />
        <circle cx="20" cy="65" r="2" fill="#138808" opacity="0.6" />
        <circle cx="80" cy="65" r="2" fill="#138808" opacity="0.6" />
      </svg>
    </div>
  );
};

export default IndianFlagVotingLogo;