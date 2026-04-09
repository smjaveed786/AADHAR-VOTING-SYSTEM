import { useState } from 'react';
import LandingPage from './components/LandingPage';
import AuthenticationPage from './components/AuthenticationPage';
import FaceVerificationPage from './components/FaceVerificationPage';
import VotingPage from './components/VotingPage';
import ConfirmationPage from './components/ConfirmationPage';
import AdminLogin from './components/admin/AdminLogin';
import AdminDashboard from './components/admin/AdminDashboard';

type PageType = 'landing' | 'auth' | 'face-verification' | 'voting' | 'confirmation' | 'admin-login' | 'admin-dashboard';

interface UserData {
  aadhaar: string;
  constituencyNo: number;
  voterId: string;
  token: string;
  otpVerified: boolean;
  faceVerified: boolean;
  hasVoted: boolean;
}

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('landing');
  const [userData, setUserData] = useState<UserData>({
    aadhaar: '',
    constituencyNo: 0,
    voterId: '',
    token: '',
    otpVerified: false,
    faceVerified: false,
    hasVoted: false
  });

  const navigateToPage = (page: PageType) => {
    setCurrentPage(page);
  };

  const updateUserData = (data: Partial<UserData>) => {
    setUserData(prev => ({ ...prev, ...data }));
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'landing':
        return (
          <LandingPage
            onStart={() => navigateToPage('auth')}
            onAdminLogin={() => navigateToPage('admin-login')}
          />
        );
      case 'admin-login':
        return (
          <AdminLogin
            onLoginSuccess={() => navigateToPage('admin-dashboard')}
            onBack={() => navigateToPage('landing')}
          />
        );
      case 'admin-dashboard':
        return (
          <AdminDashboard
            onLogout={() => navigateToPage('landing')}
          />
        );
      case 'auth':
        return (
          <AuthenticationPage
            onSuccess={(aadhaar) => {
              updateUserData({ aadhaar, otpVerified: true });
              navigateToPage('face-verification');
            }}
            onBack={() => navigateToPage('landing')}
          />
        );
      case 'face-verification':
        return (
          <FaceVerificationPage
            aadhaar={userData.aadhaar}
            onSuccess={(data) => {
              updateUserData({
                faceVerified: true,
                constituencyNo: data.constituencyNo,
                voterId: data.voterId,
                token: data.token
              });
              navigateToPage('voting');
            }}
            onBack={() => navigateToPage('auth')}
          />
        );
      case 'voting':
        return (
          <VotingPage
            onVoteSubmit={() => {
              updateUserData({ hasVoted: true });
              navigateToPage('confirmation');
            }}
            onBack={() => navigateToPage('face-verification')}
            constituencyNo={userData.constituencyNo}
            token={userData.token}
            voterId={userData.voterId}
          />
        );
      case 'confirmation':
        return <ConfirmationPage onRestart={() => {
          setUserData({
            aadhaar: '',
            constituencyNo: 0,
            voterId: '',
            token: '',
            otpVerified: false,
            faceVerified: false,
            hasVoted: false
          });
          navigateToPage('landing');
        }} />;
      default:
        return <LandingPage onStart={() => navigateToPage('auth')} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-green-50">
      {renderCurrentPage()}
    </div>
  );
}

export default App;