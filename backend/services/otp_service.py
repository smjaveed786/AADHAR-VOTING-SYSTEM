"""
Twilio OTP Service

Handles sending and verifying OTP codes via SMS using Twilio.
"""

import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
from twilio.rest import Client
from settings import get_settings


class OTPService:
    """Service for managing OTP generation and verification via Twilio."""
    
    def __init__(self):
        """Initialize Twilio client with credentials from settings."""
        settings = get_settings()
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_phone_number
        self.otp_storage_file = settings.base_dir.parent / "data" / "otp_storage.json"
        self.otp_expiry_minutes = 5
        
        # Ensure storage file exists
        self.otp_storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.otp_storage_file.exists():
            self._save_storage({})
    
    def _load_storage(self) -> Dict:
        """Load OTP storage from file."""
        try:
            with open(self.otp_storage_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_storage(self, data: Dict):
        """Save OTP storage to file."""
        with open(self.otp_storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_otp(self) -> str:
        """Generate a 6-digit OTP code."""
        return str(random.randint(100000, 999999))
    
    def _cleanup_expired_otps(self, storage: Dict):
        """Remove expired OTPs from storage."""
        now = datetime.now()
        expired_keys = []
        
        for key, data in storage.items():
            expiry = datetime.fromisoformat(data['expiry'])
            if now > expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            del storage[key]
    
    def send_otp(self, phone_number: str, aadhaar: str) -> Dict:
        """
        Send OTP to the given phone number.
        
        Args:
            phone_number: Phone number in E.164 format (e.g., +919876543210)
            aadhaar: Aadhaar number for tracking
            
        Returns:
            Dict with success status and message
        """
        try:
            # Generate OTP
            otp_code = self._generate_otp()
            
            # Send SMS via Twilio
            message = self.client.messages.create(
                body=f"Your OTP for Election Voting is: {otp_code}. Valid for {self.otp_expiry_minutes} minutes. Do not share with anyone. - Election Commission",
                from_=self.from_number,
                to=phone_number
            )
            
            # Store OTP with expiry
            storage = self._load_storage()
            self._cleanup_expired_otps(storage)
            
            storage[aadhaar] = {
                'otp': otp_code,
                'phone': phone_number,
                'expiry': (datetime.now() + timedelta(minutes=self.otp_expiry_minutes)).isoformat(),
                'attempts': 0,
                'sent_at': datetime.now().isoformat()
            }
            
            self._save_storage(storage)
            
            print(f"✅ OTP sent to {phone_number}: {otp_code} (SID: {message.sid})")
            
            return {
                'success': True,
                'message': 'OTP sent successfully',
                'expires_in': self.otp_expiry_minutes * 60
            }
            
        except Exception as e:
            print(f"❌ Error sending OTP: {e}")
            return {
                'success': False,
                'message': f'Failed to send OTP: {str(e)}'
            }
    
    def verify_otp(self, aadhaar: str, otp_code: str) -> Dict:
        """
        Verify the OTP code for the given Aadhaar.
        
        Args:
            aadhaar: Aadhaar number
            otp_code: OTP code to verify
            
        Returns:
            Dict with success status and message
        """
        storage = self._load_storage()
        self._cleanup_expired_otps(storage)
        
        if aadhaar not in storage:
            return {
                'success': False,
                'message': 'No OTP found. Please request a new OTP.'
            }
        
        otp_data = storage[aadhaar]
        
        # Check expiry
        expiry = datetime.fromisoformat(otp_data['expiry'])
        if datetime.now() > expiry:
            del storage[aadhaar]
            self._save_storage(storage)
            return {
                'success': False,
                'message': 'OTP has expired. Please request a new OTP.'
            }
        
        # Check attempts
        if otp_data['attempts'] >= 3:
            del storage[aadhaar]
            self._save_storage(storage)
            return {
                'success': False,
                'message': 'Too many failed attempts. Please request a new OTP.'
            }
        
        # Verify OTP
        if otp_data['otp'] == otp_code:
            # Success - remove OTP from storage
            del storage[aadhaar]
            self._save_storage(storage)
            print(f"✅ OTP verified successfully for Aadhaar: {aadhaar}")
            return {
                'success': True,
                'message': 'OTP verified successfully'
            }
        else:
            # Increment attempts
            otp_data['attempts'] += 1
            storage[aadhaar] = otp_data
            self._save_storage(storage)
            
            remaining = 3 - otp_data['attempts']
            return {
                'success': False,
                'message': f'Invalid OTP. {remaining} attempts remaining.'
            }


# Singleton instance
_otp_service: Optional[OTPService] = None


def get_otp_service() -> OTPService:
    """Get or create the OTP service singleton."""
    global _otp_service
    if _otp_service is None:
        _otp_service = OTPService()
    return _otp_service
