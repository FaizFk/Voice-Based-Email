from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from playsound import playsound
from gtts import gTTS
from CONSTANTS import LANGUAGE
import speech_recognition as sr
from email.mime.text import MIMEText
import base64
import re

# Define the required scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

CHOICE = {
    1: ["1", "one", "number 1"],
    2: ["2", "two", "tu", "number 2"],
    3: ["3", "three", "number 3"],
    4: ["4", "four", "for", "number 4"],
    5: ["5", "five", "number 5"],
    6: ["6", "six", "number 6"],
    7: ["7", "seven", "number 7"]
}

MAPPINGS = {
    "at the rate character": "@",
    "hashtag character": "#",
    "dollar character": "$",
    "percent character": "%",
    "ampersand character": "&",
    "star character": "*",
    "dot character": ".",
}

# Helper functions
def authenticate_gmail():
    creds = None
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def build_gmail_service():
    creds = authenticate_gmail()
    return build('gmail', 'v1', credentials=creds)

def modify_email(content, max_length=200):
    """
    Cleans the email content by removing special characters and truncating if it's too long.

    Args:
        content (str): The email content to clean.
        max_length (int): The maximum length for the content.

    Returns:
        str: The cleaned and shortened content.
    """
    # Remove special characters
    content = re.sub(r'[^\w\s.,?!]', '', content)
    # Truncate if longer than max_length
    if len(content) > max_length:
        content = content[:max_length]
    return content

def get_emails(service, user_id='me', max_results=3):
    # Fetch messages list
    results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        SpeakText("No messages found.")
        return []

    SpeakText(f"Fetching the {len(messages)} most recent emails.")
    email_data = []

    # Iterate through the messages and fetch details
    for i, message in enumerate(messages):
        msg = service.users().messages().get(userId=user_id, id=message['id']).execute()
        snippet = msg.get('snippet', 'No snippet available')
        email_data.append("Email {}:\n{}\n{}".format(i + 1, snippet, '-' * 40))

    return email_data

def send_email(service, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw}
    
    try:
        service.users().messages().send(userId="me", body=message_body).execute()
        SpeakText("Email sent successfully.")
    except Exception as error:
        SpeakText(f"An error occurred: {error}")


def search_emails(service, query, max_results=3):
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            SpeakText("No emails found matching the query.")
            return []

        email_data = []
        for i, message in enumerate(messages):
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            snippet = msg.get('snippet', 'No snippet available')
            email_data.append("Email {}:\n{}\n{}".format(i + 1, snippet, '-' * 40))

        return email_data
    except Exception as error:
        SpeakText(f"An error occurred during the search: {error}")
        return []

def compose_email(service):
    SpeakText("To whom do you want to send an email? Please say the recipient's email address letter by letter.")
    to = speech_to_text()
    to = to.replace(" ", "")
    SpeakText("You said {}. Say YES to confirm".format(to))
    res = speech_to_text()
    if res.lower() != "yes":
        SpeakText("Cancelling")
        return

    SpeakText("What should the subject of the email be?")
    subject = speech_to_text()
    SpeakText("You said {}. Say YES to confirm".format(subject))
    res = speech_to_text()
    if res.lower() != "yes":
        SpeakText("Cancelling")
        return

    SpeakText("Please dictate the body of the email.")
    body = speech_to_text()
    SpeakText("You said {}. Say YES to confirm".format(body))
    res = speech_to_text()
    if res.lower() != "yes":
        SpeakText("Cancelling")
        return

    send_email(service, to, subject, body)

def SpeakText(command, langinp=LANGUAGE):
    """
    Text to Speech using GTTS

    Args:
        command (str): Text to speak
        langinp (str, optional): Output language. Defaults to "en".
    """
    if langinp == "": langinp = "en"
    tts = gTTS(text=command, lang=langinp)
    tts.save("~tempfile01.mp3")
    playsound("~tempfile01.mp3")
    print(command)
    os.remove("~tempfile01.mp3")

def speech_to_text():
    """
    Speech to text

    Returns:
        str: Returns transcribed text
    """
    r = sr.Recognizer()
    text = None

    # Reading Microphone as source
    with sr.Microphone() as source:
        SpeakText("Beeep")
        audio_text = r.listen(source)

        try:
            text = r.recognize_google(audio_text)
            for word, symbol in MAPPINGS.items():
                text = text.replace(word, symbol)
            print(text)
        except:
            SpeakText("Sorry, I did not get that")

    return text        

# Main updated functions
def get_latest_mails(service):
    emails = get_emails(service)
    if emails:
        for email in emails:
            email = modify_email(email)
            SpeakText(email)
    else:
        SpeakText("No recent emails to display.")

def main():
    service = build_gmail_service()
    SpeakText("Always speak after the word Beeep")
    SpeakText("Choose the task you want to perform. Say 1 to get the last 3 mails. Say 2 to compose an email. Say 3 to search emails.")
    choice = speech_to_text()

    if choice.lower() in CHOICE[1]:
        get_latest_mails(service)
    elif choice.lower() in CHOICE[2]:
        compose_email(service)
    elif choice.lower() in CHOICE[3]:
        SpeakText("What should I search for?")
        query = speech_to_text()
        emails = search_emails(service, query)
        for email in emails:
            email = modify_email(email)
            SpeakText(email)
    else:
        SpeakText("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
