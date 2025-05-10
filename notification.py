import requests

# Email configuration
ADMIN_EMAIL = "gkraem@vt.edu"
WEB3FORMS_ACCESS_KEY = "3a301349-3bdc-4a7f-afd5-afe06ef15287"

def send_admin_notification(user_data):
    """
    Send an email notification to the admin when a new user registers
    using web3forms.com API
    """
    try:
        # Prepare the payload for web3forms
        payload = {
            "access_key": WEB3FORMS_ACCESS_KEY,
            "name": f"New User: {user_data['name']}",
            "email": user_data['email'],
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
        response = requests.post(
            "https://api.web3forms.com/submit", 
            data=payload
        )
        
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