import React, { useState, useEffect } from 'react';
import {
    Users,
    UserPlus,
    LogOut,
    Activity,
    BarChart3,
    Search,
    CheckCircle,
    XCircle,
    RefreshCw,
    Trophy,
    ChevronDown,
    ChevronUp,
    Vote
} from 'lucide-react';
import VoterRegistration from './VoterRegistration';
import { api } from '../../services/api';

interface Voter {
    voter_id: string;
    name: string;
    aadhaar_number: string;
    phone_number: string;
    constituency_no: number;
    has_voted: boolean;
    voted_at?: string;
}

interface ResultCandidate {
    candidate_id: number;
    candidate_name: string;
    party: string;
    votes: number;
    percentage: number;
}

interface ConstituencyResultData {
    constituency_no: number;
    constituency_name: string;
    total_votes: number;
    candidates: ResultCandidate[];
    winner?: ResultCandidate | null;
}

interface OverallResultsData {
    total_votes_cast: number;
    total_registered_voters: number;
    turnout_percentage: number;
    constituencies_reported: number;
    constituency_results: ConstituencyResultData[];
    top_candidates: ResultCandidate[];
}

interface AdminDashboardProps {
    onLogout: () => void;
}

type AdminView = 'stats' | 'register' | 'voters' | 'results';

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
    const [currentView, setCurrentView] = useState<AdminView>('stats');
    const [stats, setStats] = useState({
        total_voters: 0,
        voters_voted: 0,
        registration_complete: false
    });
    const [voters, setVoters] = useState<Voter[]>([]);
    const [votersLoading, setVotersLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [overallResults, setOverallResults] = useState<OverallResultsData | null>(null);
    const [resultsLoading, setResultsLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [expandedConstituency, setExpandedConstituency] = useState<number | null>(null);

    const username = localStorage.getItem('admin_username') || 'Admin';

    useEffect(() => {
        loadStats();
    }, []);

    useEffect(() => {
        if (currentView === 'voters') {
            loadVoters();
        } else if (currentView === 'results') {
            loadResults();
        }
    }, [currentView]);

    const loadStats = async () => {
        try {
            const data = await api.admin.getStats();
            setStats(data);
        } catch (err) {
            console.error('Failed to load stats');
        }
    };

    const loadVoters = async () => {
        setVotersLoading(true);
        try {
            const data = await api.admin.getVoters(undefined, searchQuery || undefined);
            setVoters(data.voters || []);
        } catch (err) {
            console.error('Failed to load voters');
        } finally {
            setVotersLoading(false);
        }
    };

    const loadResults = async () => {
        setResultsLoading(true);
        try {
            const data = await api.admin.getResults();
            const mapped: OverallResultsData = {
                total_votes_cast: data.total_votes_cast || 0,
                total_registered_voters: data.total_registered_voters || 0,
                turnout_percentage: data.turnout_percentage || 0,
                constituencies_reported: data.constituencies_reported || 0,
                top_candidates: (data.top_candidates || []).map((c: any) => ({
                    candidate_id: c.candidate_id,
                    candidate_name: c.candidate_name,
                    party: c.party,
                    votes: c.vote_count || 0,
                    percentage: c.percentage || 0
                })),
                constituency_results: (data.constituency_results || []).map((cr: any) => ({
                    constituency_no: cr.constituency_no,
                    constituency_name: cr.constituency_name,
                    total_votes: cr.total_votes,
                    winner: cr.winner ? {
                        candidate_id: cr.winner.candidate_id,
                        candidate_name: cr.winner.candidate_name,
                        party: cr.winner.party,
                        votes: cr.winner.vote_count || 0,
                        percentage: cr.winner.percentage || 0
                    } : null,
                    candidates: (cr.candidates || []).map((c: any) => ({
                        candidate_id: c.candidate_id,
                        candidate_name: c.candidate_name,
                        party: c.party,
                        votes: c.vote_count || 0,
                        percentage: c.percentage || 0
                    }))
                }))
            };
            setOverallResults(mapped);
        } catch (err) {
            console.error('Failed to load results');
        } finally {
            setResultsLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_username');
        onLogout();
    };

    const renderContent = () => {
        switch (currentView) {
            case 'register':
                return <VoterRegistration onCancel={() => setCurrentView('stats')} />;
            case 'voters':
                return (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-gray-800">Manage Voters</h2>
                            <button
                                onClick={loadVoters}
                                className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                            >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Refresh
                            </button>
                        </div>
                        <div className="mb-4">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search by name or Aadhaar..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && loadVoters()}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                        {votersLoading ? (
                            <div className="text-center py-8 text-gray-500">Loading voters...</div>
                        ) : voters.length === 0 ? (
                            <div className="text-center py-8 text-gray-500">No voters found</div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-200">
                                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Voter ID</th>
                                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Name</th>
                                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Aadhaar</th>
                                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Constituency</th>
                                            <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {voters.map((voter) => (
                                            <tr key={voter.voter_id} className="border-b border-gray-100 hover:bg-gray-50">
                                                <td className="py-3 px-4 text-sm text-gray-800">{voter.voter_id}</td>
                                                <td className="py-3 px-4 text-sm text-gray-800">{voter.name}</td>
                                                <td className="py-3 px-4 text-sm text-gray-600">
                                                    {voter.aadhaar_number.slice(0, 4)}...{voter.aadhaar_number.slice(-4)}
                                                </td>
                                                <td className="py-3 px-4 text-sm text-gray-600">{voter.constituency_no}</td>
                                                <td className="py-3 px-4">
                                                    {voter.has_voted ? (
                                                        <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                                                            <CheckCircle className="w-3 h-3 mr-1" />
                                                            Voted
                                                        </span>
                                                    ) : (
                                                        <span className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                                            <XCircle className="w-3 h-3 mr-1" />
                                                            Not Voted
                                                        </span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                );
            case 'results':
                return (
                    <div className="space-y-6">
                        {/* Summary Stats Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-gray-500 text-sm font-medium">Total Registered Voters</h3>
                                    <Users className="w-5 h-5 text-blue-500" />
                                </div>
                                <p className="text-3xl font-bold text-gray-800">
                                    {overallResults?.total_registered_voters ?? '—'}
                                </p>
                            </div>
                            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-gray-500 text-sm font-medium">Votes Polled</h3>
                                    <Vote className="w-5 h-5 text-green-500" />
                                </div>
                                <p className="text-3xl font-bold text-gray-800">
                                    {overallResults?.total_votes_cast ?? '—'}
                                </p>
                            </div>
                            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-gray-500 text-sm font-medium">Turnout</h3>
                                    <BarChart3 className="w-5 h-5 text-purple-500" />
                                </div>
                                <p className="text-3xl font-bold text-gray-800">
                                    {overallResults ? `${overallResults.turnout_percentage}%` : '—'}
                                </p>
                            </div>
                            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-gray-500 text-sm font-medium">Constituencies Reported</h3>
                                    <Activity className="w-5 h-5 text-orange-500" />
                                </div>
                                <p className="text-3xl font-bold text-gray-800">
                                    {overallResults?.constituencies_reported ?? '—'}
                                </p>
                            </div>
                        </div>

                        {/* Calculate Results Button */}
                        {!showResults && (
                            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
                                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                                <h3 className="text-lg font-semibold text-gray-800 mb-2">Election Results</h3>
                                <p className="text-gray-500 mb-6">Click below to calculate and display constituency-wise election results</p>
                                <button
                                    onClick={() => {
                                        setShowResults(true);
                                        loadResults();
                                    }}
                                    disabled={resultsLoading}
                                    className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-300"
                                >
                                    {resultsLoading ? 'Calculating...' : '📊 Calculate Results'}
                                </button>
                            </div>
                        )}

                        {/* Constituency-wise Results */}
                        {showResults && (
                            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h2 className="text-xl font-bold text-gray-800">Constituency-wise Results</h2>
                                    <button
                                        onClick={loadResults}
                                        className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                                    >
                                        <RefreshCw className="w-4 h-4 mr-2" />
                                        Refresh
                                    </button>
                                </div>
                                {resultsLoading ? (
                                    <div className="text-center py-8 text-gray-500">Calculating results...</div>
                                ) : !overallResults || overallResults.constituency_results.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                                        <p>No votes have been cast yet</p>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {overallResults.constituency_results.map((constituency) => (
                                            <div key={constituency.constituency_no} className="border border-gray-200 rounded-lg overflow-hidden">
                                                {/* Constituency Header (clickable) */}
                                                <button
                                                    onClick={() => setExpandedConstituency(
                                                        expandedConstituency === constituency.constituency_no ? null : constituency.constituency_no
                                                    )}
                                                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                                                >
                                                    <div className="flex items-center">
                                                        <span className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm mr-3">
                                                            {constituency.constituency_no}
                                                        </span>
                                                        <div className="text-left">
                                                            <p className="font-semibold text-gray-800">{constituency.constituency_name}</p>
                                                            <p className="text-sm text-gray-500">{constituency.total_votes} votes polled</p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center">
                                                        {constituency.winner && (
                                                            <span className="hidden sm:flex items-center px-3 py-1 bg-green-50 text-green-700 text-sm rounded-full mr-3">
                                                                <Trophy className="w-3 h-3 mr-1" />
                                                                {constituency.winner.candidate_name}
                                                            </span>
                                                        )}
                                                        {expandedConstituency === constituency.constituency_no
                                                            ? <ChevronUp className="w-5 h-5 text-gray-400" />
                                                            : <ChevronDown className="w-5 h-5 text-gray-400" />
                                                        }
                                                    </div>
                                                </button>

                                                {/* Expanded Candidate List */}
                                                {expandedConstituency === constituency.constituency_no && (
                                                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                                                        <div className="space-y-3">
                                                            {constituency.candidates.map((candidate, idx) => (
                                                                <div key={candidate.candidate_id} className="bg-white rounded-lg p-3 border border-gray-100">
                                                                    <div className="flex items-center justify-between mb-2">
                                                                        <div className="flex items-center">
                                                                            <span className={`w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold mr-3 ${idx === 0 ? 'bg-yellow-500' : idx === 1 ? 'bg-gray-400' : 'bg-gray-300'}`}>
                                                                                {idx + 1}
                                                                            </span>
                                                                            <div>
                                                                                <p className="font-medium text-gray-800 text-sm">{candidate.candidate_name}</p>
                                                                                <p className="text-xs text-gray-500">{candidate.party}</p>
                                                                            </div>
                                                                        </div>
                                                                        <div className="text-right">
                                                                            <p className="text-lg font-bold text-gray-800">{candidate.votes}</p>
                                                                            <p className="text-xs text-gray-500">{candidate.percentage.toFixed(1)}%</p>
                                                                        </div>
                                                                    </div>
                                                                    <div className="w-full bg-gray-100 rounded-full h-1.5">
                                                                        <div
                                                                            className={`h-1.5 rounded-full ${idx === 0 ? 'bg-green-500' : 'bg-blue-400'}`}
                                                                            style={{ width: `${candidate.percentage}%` }}
                                                                        ></div>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            case 'stats':
            default:
                return (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-gray-500 text-sm font-medium">Total Voters</h3>
                                <div className="p-2 bg-blue-50 rounded-lg">
                                    <Users className="w-5 h-5 text-blue-600" />
                                </div>
                            </div>
                            <p className="text-3xl font-bold text-gray-800">{stats.total_voters}</p>
                            <p className="text-green-500 text-sm mt-2 flex items-center">
                                <Activity className="w-3 h-3 mr-1" />
                                Updated just now
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-gray-500 text-sm font-medium">Votes Cast</h3>
                                <div className="p-2 bg-green-50 rounded-lg">
                                    <BarChart3 className="w-5 h-5 text-green-600" />
                                </div>
                            </div>
                            <p className="text-3xl font-bold text-gray-800">{stats.voters_voted}</p>
                            <p className="text-gray-400 text-sm mt-2">
                                Turnout: {stats.total_voters ? Math.round((stats.voters_voted / stats.total_voters) * 100) : 0}%
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-gray-50 transition-colors"
                            onClick={() => setCurrentView('register')}
                        >
                            <div className="p-4 bg-purple-50 rounded-full mb-3">
                                <UserPlus className="w-8 h-8 text-purple-600" />
                            </div>
                            <h3 className="font-semibold text-gray-800">Register New Voter</h3>
                            <p className="text-sm text-gray-500 mt-1">Add voter details & photos</p>
                        </div>
                    </div>
                );
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
                <div className="p-6 border-b border-gray-100">
                    <h1 className="text-xl font-bold text-gray-800 flex items-center">
                        <Users className="w-6 h-6 mr-2 text-blue-600" />
                        Admin Panel
                    </h1>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    <button
                        onClick={() => setCurrentView('stats')}
                        className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${currentView === 'stats'
                                ? 'bg-blue-50 text-blue-700'
                                : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <Activity className="w-5 h-5 mr-3" />
                        Dashboard
                    </button>

                    <button
                        onClick={() => setCurrentView('register')}
                        className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${currentView === 'register'
                                ? 'bg-blue-50 text-blue-700'
                                : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <UserPlus className="w-5 h-5 mr-3" />
                        Register Voter
                    </button>

                    <button
                        onClick={() => setCurrentView('voters')}
                        className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${currentView === 'voters'
                                ? 'bg-blue-50 text-blue-700'
                                : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <Search className="w-5 h-5 mr-3" />
                        Manage Voters
                    </button>

                    <button
                        onClick={() => setCurrentView('results')}
                        className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${currentView === 'results'
                                ? 'bg-blue-50 text-blue-700'
                                : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <BarChart3 className="w-5 h-5 mr-3" />
                        Results
                    </button>
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <div className="flex items-center mb-4 px-4">
                        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold">
                            {username[0]}
                        </div>
                        <div className="ml-3">
                            <p className="text-sm font-medium text-gray-700">{username}</p>
                            <p className="text-xs text-gray-500">Administrator</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                    >
                        <LogOut className="w-4 h-4 mr-2" />
                        Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-y-auto">
                <header className="flex items-center justify-between mb-8 md:hidden">
                    <h1 className="text-xl font-bold text-gray-800">Admin Dashboard</h1>
                    <button onClick={handleLogout} className="p-2 text-gray-600">
                        <LogOut className="w-5 h-5" />
                    </button>
                </header>

                {renderContent()}
            </main>
        </div>
    );
};

export default AdminDashboard;
