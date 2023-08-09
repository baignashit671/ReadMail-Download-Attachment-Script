import credentials
import msal
import json
import requests

# Function to generate access token
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

data_received = '2023-07-25'
mail_subject = 'NNIP_GLIMPSE2_20230724'
mail_sender = 'jorryt.peperkamp@nnip.com'
mail_user = 'nashit.baig@fintechglobal.center'

# API call URL with unread email filter
url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages?$filter=startswith(from/emailAddress/address, '{mail_sender}') and subject eq '{mail_subject}' and receivedDateTime ge '{data_received}' and isRead eq false"

headers = {
    "Authorization": f"Bearer {token}",
    "ContentType": "application/json"
}

# Print the email address used for login
print("Logged in as:", mail_user)

# Send the API request
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# Function to grab attachment
def get_email_attachment(message_id):
    url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{message_id}/attachments"
    response = requests.get(url, headers=headers)
    return response.json()

# Function to store the file in the current working directory
def save_attachment(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)

# Check if there are messages in the response
if "value" not in data:
    print("No unread emails found matching the filter criteria.")
    exit()


# Loop through each response
for d in data["value"]:
    mes_id = d['id']  # Message id

    # Get attachments now
    attachments = get_email_attachment(mes_id)
    for attachment in attachments['value']:
        attachment_name = attachment['name']
        attachment_id = attachment['id']

        # Download url request or API call
        download_attachment_endpoint = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{mes_id}/attachments/{attachment_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "ContentType": "application/octet-stream"
        }

        response = requests.get(download_attachment_endpoint, headers=headers)
        response.raise_for_status()

        # Save the attachment to the current working directory
        save_attachment(attachment_name, response.content)

    # Mark the email as read
    mark_as_read_endpoint = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{mes_id}"
    payload = {
        "isRead": True
    }
    
    mark_as_read_response = requests.patch(mark_as_read_endpoint, headers=headers, json=payload)
    mark_as_read_response.raise_for_status()
    
    # Get the email message subject
    message_subject = d['subject']
    # Print a message indicating the attachment has been downloaded
    print(f"Downloaded: {attachment_name} from email with subject: {message_subject}")
