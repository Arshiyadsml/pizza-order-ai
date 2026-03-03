"""
SMS Service - Handles Twilio integration
Interview Learning: How to handle third-party services safely
"""

from twilio.rest import Client
import logging

# Setup logging - always log in production!
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        """
        Initialize Twilio SMS service.
        
        Interview Note: Always validate credentials early
        """
        self.client = Client(account_sid, auth_token)
        self.phone_number = phone_number
    
    def send_confirmation(self, to_phone: str, message: str) -> bool:
        """
        Send SMS confirmation.
        
        Interview Learning: Error handling patterns for external APIs
        """
        try:
            response = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully. SID: {response.sid}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
