import React, { useState, useEffect } from 'react';
import { ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import IndianFlagVotingLogo from './IndianFlagVotingLogo';
import { api } from '../services/api';

interface VotingPageProps {
  onVoteSubmit: () => void;
  onBack: () => void;
  constituencyNo?: number;
  voterId?: string;
  token?: string;
}

interface Candidate {
  id: number;
  name: string;
  party: string;
  constituency_no?: number;
  constituency_name?: string;
}

const getPartySymbol = (party: string) => {
  if (!party) return '🗳️';
  const p = party.toLowerCase();
  if (p.includes('bjp') || p.includes('bharatiya')) return '🪷';
  if (p.includes('inc') || p.includes('congress')) return '✋';
  if (p.includes('aap')) return '🧹';
  if (p.includes('sp') || p.includes('samajwadi')) return '🚲';
  if (p.includes('bsp')) return '🐘';
  if (p.includes('tmc') || p.includes('trinamool')) return '🌸';
  if (p.includes('cpi') || p.includes('communist')) return '☭';
  if (p.includes('tdp') || p.includes('telugu')) return '🚲';
  if (p.includes('ysrcp')) return '🚁'; // Fan symbol approximation or use text
  if (p.includes('jsp')) return '🥛';
  if (p.includes('nota')) return '❌';
  return '🗳️';
};

const VotingPage: React.FC<VotingPageProps> = ({ onVoteSubmit, onBack, constituencyNo, voterId, token }) => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        if (!constituencyNo) {
          setLoading(false);
          return;
        }
        const data = await api.vote.getCandidates(constituencyNo);
        if (data && Array.isArray(data.candidates)) {
          setCandidates(data.candidates);
        } else {
          console.error("Unexpected response format:", data);
          setError("Failed to load candidates data.");
        }
      } catch (err) {
        console.error("Failed to fetch candidates:", err);
        setError("Unable to load candidates.");
      } finally {
        setLoading(false);
      }
    };

    fetchCandidates();
  }, [constituencyNo]);

  const handleCandidateSelect = (candidateId: number) => {
    setSelectedCandidate(candidateId);
  };

  const confirmVote = async () => {
    if (!selectedCandidate || !token || !voterId) return;

    setIsSubmitting(true);
    try {
      const result = await api.vote.submitVote(token, voterId, selectedCandidate);
      if (result.success) {
        onVoteSubmit();
      } else {
        throw new Error(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Vote submission failed');
      setShowConfirmation(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedCandidateData = candidates.find(c => c.id === selectedCandidate);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading candidates...</div>;
  }

  if (showConfirmation) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-lg">
          <div className="bg-gradient-to-r from-orange-500 via-white to-green-600 h-2 rounded-t-lg"></div>
          <div className="bg-white rounded-b-lg shadow-xl p-8">
            <div className="text-center">
              <div className="bg-amber-100 p-4 rounded-full inline-block mb-6">
                <IndianFlagVotingLogo size="md" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Confirm Your Vote</h2>

              {selectedCandidateData && (
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <div className="text-4xl mb-2">{getPartySymbol(selectedCandidateData.party)}</div>
                  <h3 className="text-lg font-semibold text-gray-800">{selectedCandidateData.party}</h3>
                  <p className="text-sm text-gray-600 mt-1">Candidate: {selectedCandidateData.name}</p>
                </div>
              )}

              {error && <p className="text-red-500 mb-4">{error}</p>}

              <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-md">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-red-500 mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-red-700">
                      <strong>Important:</strong> Once submitted, your vote cannot be changed.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => setShowConfirmation(false)}
                  disabled={isSubmitting}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Go Back
                </button>
                <button
                  onClick={confirmVote}
                  disabled={isSubmitting}
                  className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
                >
                  {isSubmitting ? 'Submitting...' : 'Confirm Vote'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl">
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
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 text-center mb-2">
              Cast Your Vote
            </h1>
            <p className="text-gray-600 text-center">
              Constituency #{constituencyNo}
            </p>
            {error && <p className="text-center text-red-500 mt-2">{error}</p>}
          </div>

          <div className="grid gap-4 mb-8">
            {candidates.map((candidate, index) => (
              <button
                key={candidate.id}
                onClick={() => handleCandidateSelect(candidate.id)}
                className={`w-full p-6 border-2 rounded-xl transition-all duration-300 ${selectedCandidate === candidate.id
                  ? 'border-blue-500 bg-blue-50 shadow-lg scale-105'
                  : 'bg-gray-50 border-gray-300 hover:bg-gray-100'
                  } hover:shadow-md hover:scale-102 transform`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-200 text-gray-700 font-bold text-lg">
                      {index + 1}
                    </div>
                    <div className="text-3xl">{getPartySymbol(candidate.party)}</div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-800 text-lg">{candidate.party}</h3>
                      <p className="text-sm text-gray-600">{candidate.name}</p>
                    </div>
                  </div>
                  {selectedCandidate === candidate.id && (
                    <CheckCircle className="w-6 h-6 text-blue-600" />
                  )}
                </div>
              </button>
            ))}
            {candidates.length === 0 && !loading && (
              <p className="text-center text-gray-500">No candidates found for this constituency.</p>
            )}
          </div>

          <div className="border-t pt-6">
            <button
              onClick={() => setShowConfirmation(true)}
              disabled={!selectedCandidate}
              className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-300 disabled:to-gray-400 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-300 disabled:cursor-not-allowed transform hover:scale-105 disabled:hover:scale-100"
            >
              {selectedCandidate ? 'Submit Vote' : 'Select a Party to Continue'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VotingPage;