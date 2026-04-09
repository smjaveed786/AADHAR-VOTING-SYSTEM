/**
 * API Service for Voting System
 * Handles communication with the FastAPI backend
 */

const API_BASE = 'http://localhost:5001/api';

// Types
export interface LoginResponse {
    access_token: string;
    token_type: string;
    username: string;
}

export interface VoterRegistrationData {
    name: string;
    aadhaar_number: string;
    phone_number: string;
    constituency_no: number;
    photos: File[];
}

// Helpers
const getHeaders = (isMultipart = false) => {
    const token = localStorage.getItem('admin_token');
    const headers: HeadersInit = {
        'Authorization': token ? `Bearer ${token}` : '',
    };

    if (!isMultipart) {
        headers['Content-Type'] = 'application/json';
    }

    return headers;
};

export const api = {
    auth: {
        login: async (username: string, password: string): Promise<LoginResponse> => {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            // Note: The FastAPI OAuth2PasswordRequestForm expects form data
            // But our custom auth endpoint expects JSON
            // Let's check api/routes/auth.py -> it expects JSON {username, password}

            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            return response.json();
        },

        verify: async (): Promise<boolean> => {
            try {
                const response = await fetch(`${API_BASE}/auth/verify`, {
                    headers: getHeaders(),
                });
                return response.ok;
            } catch {
                return false;
            }
        },

        sendOTP: async (aadhaar: string) => {
            const response = await fetch(`${API_BASE}/auth/send-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ aadhaar }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to send OTP');
            }

            return response.json();
        },

        verifyOTP: async (aadhaar: string, otp: string) => {
            const response = await fetch(`${API_BASE}/auth/verify-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ aadhaar, otp }),
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to verify OTP');
            }

            return data;
        }
    },

    admin: {
        registerVoter: async (data: VoterRegistrationData) => {
            const formData = new FormData();
            formData.append('name', data.name);
            formData.append('aadhaar_number', data.aadhaar_number);
            formData.append('phone_number', data.phone_number);
            formData.append('constituency_no', data.constituency_no.toString());

            data.photos.forEach((photo) => {
                formData.append('photos', photo);
            });

            const response = await fetch(`${API_BASE}/admin/register-voter`, {
                method: 'POST',
                headers: getHeaders(true), // Multipart
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Registration failed');
            }

            return response.json();
        },

        getStats: async () => {
            const response = await fetch(`${API_BASE}/admin/stats`, {
                headers: getHeaders(),
            });
            return response.json();
        },

        getVoters: async (constituency?: number, search?: string) => {
            let url = `${API_BASE}/admin/voters?`;
            if (constituency) url += `constituency=${constituency}&`;
            if (search) url += `search=${encodeURIComponent(search)}`;
            const response = await fetch(url, {
                headers: getHeaders(),
            });
            return response.json();
        },

        getResults: async (constituencyNo?: number) => {
            let url = `${API_BASE}/results/overall`;
            if (constituencyNo) url = `${API_BASE}/results/constituency/${constituencyNo}`;
            const response = await fetch(url, {
                headers: getHeaders(),
            });
            return response.json();
        }
    },

    vote: {
        getCandidates: async (constituencyNo: number) => {
            const response = await fetch(`${API_BASE}/vote/candidates/${constituencyNo}`);
            return response.json();
        },

        submitVote: async (token: string, voterId: string, candidateId: number) => {
            const response = await fetch(`${API_BASE}/vote/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token,
                    voter_id: voterId,
                    candidate_id: candidateId,
                }),
            });
            return response.json();
        }
    },

    verification: {
        complete: async (aadhaar: string, frames: string[]) => {
            const response = await fetch(`${API_BASE}/verify/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    aadhaar_number: aadhaar,
                    frames
                }),
            });
            return response.json();
        }
    }
};
