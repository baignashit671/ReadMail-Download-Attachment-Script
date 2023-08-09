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
    scope = ['https://graph.microsoft.com/.default']
    app = msal.ConfidentialClientApplication(clientID, authority=authority, client_credential=clientSecret)
    access_token = app.acquire_token_for_client(scopes=scope)
    return access_token

access_token = get_access_token()
token = access_token['access_token']

data_received = '2023-07-20'
mail_subject = 'PYTHON SCRIPT TO DOWN EMAIL ATTACHMENTS'
mail_sender = 'baignashit@gmail.com'
mail_user = 'nashit.baig@fintechglobal.center.onmicrosoft.com'

# API call URL
url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages?$filter=startswith(from/emailAddress/address, '{mail_sender}') and subject eq '{mail_subject}' and receivedDateTime ge {data_received}"

headers = {
    "Authorization": f"Bearer {token}",
    "ContentType": "application/json"
}

# Send the API request
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# Function to grab attachment
def get_email_attachment(message_id):
    url = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{message_id}/attachments"
    response = requests.get(url, headers=headers)
    return response.json()

# Loop through each response
for d in data["value"]:
    print(d['id'])
    mes_id = d['id']  # message id

    # Get attachments now
    attachments = get_email_attachment(mes_id)
    for attachment in attachments['value']:
        attachment_name = attachment['name']
        attachment_id = attachment['id']

        # Download URL request or API call
        download_attachment_endpoint = f"https://graph.microsoft.com/v1.0/users/{mail_user}/messages/{mes_id}/attachments/{attachment_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "ContentType": "application/octet-stream"
        }

        response = requests.get(download_attachment_endpoint, headers=headers)
        response.raise_for_status()

        # Logic to store the file in the current working directory
        with open(attachment_name, 'wb') as f:
            f.write(response.content)
