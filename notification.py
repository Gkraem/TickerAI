import requests
import os
from twilio.rest import Client

# Email configuration
ADMIN_EMAIL = "gkraem@vt.edu"
# API key for web3forms.com
WEB3FORMS_ACCESS_KEY = "3a301349-3bdc-4a7f-afd5-afe06ef15287"

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

def send_admin_notification(user_data):
    """
    Send an email notification to the admin when a new user registers
    using web3forms.com API
    """
    try:
        # Prepare the payload for web3forms
        payload = {
            "access_key": WEB3FORMS_ACCESS_KEY,
            "from_name": f"Ticker AI Bot",
            "name": f"New User: {user_data['name']}",
            "email": user_data['email'],
            "to_email": ADMIN_EMAIL,  # Recipient email address
            "message": f"""
New Ticker AI User Registration:

Name: {user_data['name']}
Email: {user_data['email']}
Phone: {user_data['phone']}
Registration Time: {user_data['created_at']}
            """,
            "subject": "New Ticker AI User Registration"
        }
        
        # Send the POST request to web3forms API
        print(f"Sending email notification for new user: {user_data['name']}")
        response = requests.post(
            "https://api.web3forms.com/submit", 
            data=payload
        )
        
        # Print full response for debugging
        print(f"Web3Forms API Response: {response.text}")
        
        # Check if submission was successful
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"Notification sent successfully to {ADMIN_EMAIL}")
                return True
            else:
                print(f"Web3Forms API error: {result.get('message')}")
                return False
        else:
            print(f"Web3Forms API HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")
        return False

def send_sms_notification(phone_number, message):
    """
    Send SMS notification using Twilio
    
    Parameters:
    -----------
    phone_number : str
        Recipient's phone number (format: +1XXXXXXXXXX)
    message : str
        SMS message content
        
    Returns:
    --------
    dict
        Response with status and message
    """
    # Check if Twilio credentials are available
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return {
            "success": False,
            "message": "Twilio credentials not configured. Please set the TWILIO environment variables."
        }
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send the SMS
        twilio_message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        return {
            "success": True,
            "message": f"SMS sent successfully! SID: {twilio_message.sid}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send SMS: {str(e)}"
        }

def send_bulk_sms(users, message):
    """
    Send SMS notifications to multiple users
    
    Parameters:
    -----------
    users : list
        List of user dictionaries containing 'phone' key
    message : str
        SMS message content to send to all users
        
    Returns:
    --------
    dict
        Response with status, success count, and failure count
    """
    if not users:
        return {
            "success": False,
            "message": "No users provided"
        }
    
    results = {
        "total": len(users),
        "success": 0,
        "failed": 0,
        "failures": []
    }
    
    for user in users:
        phone = user.get('phone')
        if not phone:
            results["failed"] += 1
            results["failures"].append({
                "user": user.get('name', 'Unknown'),
                "reason": "No phone number provided"
            })
            continue
            
        # Format phone number if needed (ensure it has +1 prefix for US numbers)
        if not phone.startswith('+'):
            phone = f"+1{phone.replace('-', '').replace(' ', '')}"
            
        # Send SMS
        result = send_sms_notification(phone, message)
        
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
            results["failures"].append({
                "user": user.get('name', 'Unknown'),
                "reason": result["message"]
            })
    
    return results