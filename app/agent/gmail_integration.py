from dotenv import load_dotenv
load_dotenv()

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes needed
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive.file'
]

def get_google_credentials():
    """Get or refresh Google credentials"""
    creds = None
    
    # Token file stores user credentials after first login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file(
            'token.json', SCOPES
        )
    
    # If no valid credentials — login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def send_email(recipient: str, subject: str, body: str, attachment_path: str = None):
    """Send email via Gmail API with optional attachment"""
    from datetime import datetime
    
    creds = get_google_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEMultipart()
    message['to'] = recipient
    message['subject'] = subject
    
    # HTML email body with date
    html_body = f"""
    <html><body>
    <h2>Daily Supply Chain Risk Report</h2>
    <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
    <hr>
    <h3>Key Highlights:</h3>
    <pre>{body}</pre>
    <hr>
    <p>Full report attached as markdown file.</p>
    </body></html>
    """
    
    message.attach(MIMEText(html_body, 'html'))
    
    # Attach file if provided
    if attachment_path and os.path.exists(attachment_path):
        from email.mime.base import MIMEBase
        from email import encoders
        
        with open(attachment_path, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )
            message.attach(attachment)
        print(f"Attached: {attachment_path}")
    
    # Encode and send
    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()
    
    service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
    
    print(f"Email sent to {recipient} ✅")

def save_to_drive(filename: str, content: str):
    """Save report to Google Drive"""
    from googleapiclient.http import MediaInMemoryUpload
    
    creds = get_google_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    # File metadata
    file_metadata = {
        'name': filename,
        'mimeType': 'text/plain'
    }
    
    # File content
    media = MediaInMemoryUpload(
        content.encode(),
        mimetype='text/plain'
    )
    
    # Upload
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name'
    ).execute()
    
    print(f"Saved to Drive: {file['name']} ✅")
    return file['id']

if __name__ == "__main__":
    # Test
    send_email(
        "maazulhasan@usf.edu",
        "Test Supply Chain Alert",
        "This is a test email from your Supply Chain Agent"
    )