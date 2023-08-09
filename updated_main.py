import credentials
import msal
import json
import requests
from datetime import datetime

# Function to generate access token using MSAL (Microsoft Authentication Library)
def get_access_token():
    tenantID = credentials.tenantid_
    authority = 'https://login.microsoftonline.com/' + tenantID
    clientID = credentials.appclientid
    clientSecret = credentials.appsec
    scope = ['https://graph.microsoft.com/.default']  # Wrap the scopes in square brackets
    app = msal.ConfidentialClientApplication(clientID, authority=authority, client_credential=clientSecret)
    access_token = app.acquire_token_for_client(scopes=scope)
    return access_token


access_token = get_access_token()
token = access_token['access_token']

data_received = '2023-07-28'
mail_subject = 'BTCA Excel Report'
# mail_sender = 'jorryt.peperkamp@nnip.com'
mail_sender = 'fbergling@bloomberg.net'
mail_user = 'nashit.baig@fintechglobal.center'

# API call URL with unread email filter
# url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages?$filter=startswith(from/emailAddress/address, '{mail_sender}') and subject eq '{mail_subject}' and receivedDateTime ge {data_received} and isRead eq false"
url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages?$filter=startswith(from/emailAddress/address, '{mail_sender}') and subject eq '{mail_subject}' and receivedDateTime ge {data_received} and isRead eq false"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Print the email address used for login
print("Logged in as:", mail_user)

# Send the API request
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful
except requests.exceptions.RequestException as e:
    print("An error occurred while making the API request:", e)
    exit()

data = json.loads(response.text)

# Check if there are messages in the response
if "value" not in data:
    print("No messages found in the response.")
    exit()


# Function to grab attachment
def get_email_attachment(message_id):
    url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{message_id}/attachments"
    response = requests.get(url, headers=headers)
    return response.json()


# Function to store the file in the current working directory
def save_attachment(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)


# Loop through each response
for d in data["value"]:
    mes_id = d['id']  # Message id

    # Check if the email is unread
    if not d['isRead']:
        # Mark the email as read
        mark_as_read_endpoint = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{mes_id}"
        payload = {
            "isRead": True
        }

        mark_as_read_response = requests.patch(mark_as_read_endpoint, headers=headers, json=payload)
        mark_as_read_response.raise_for_status()

        # Get attachments now
        attachments = get_email_attachment(mes_id)
        for attachment in attachments['value']:
            attachment_name = attachment['name']
            attachment_id = attachment['id']

            # Download url request or API call
            download_attachment_endpoint = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{mes_id}/attachments/{attachment_id}/$value"

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream",
                "Prefer": "id=me"
            }

            response = requests.get(download_attachment_endpoint, headers=headers)
            response.raise_for_status()

            # Save the attachment to the current working directory
            save_attachment(attachment_name, response.content)

            # Open text files with encoding
            if attachment_name.endswith('.txt'):
                with open(attachment_name, encoding='utf-8') as f:
                    data = f.read()

            # Get the email message subject
            message_subject = d['subject']
            # Print a message indicating the attachment has been downloaded
            print(f"Downloaded: {attachment_name} from email with subject: {message_subject}")
    else:
        print("Email is already marked as read, skipping attachment download.")
