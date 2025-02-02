import streamlit as st
import google.auth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import google.generativeai as genai
import json
import re
from io import BytesIO
import matplotlib.pyplot as plt

# Streamlit configuration
st.set_page_config(page_title="Escalytics", page_icon="📧", layout="wide")
st.title("⚡Escalytics by EverTech")
st.write("Extract insights, root causes, and actionable steps from emails.")

# Set up the Generative AI API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
creds = None

# Function to authenticate and build the Gmail service
def authenticate_gmail():
    if 'credentials' in st.secrets:
        creds = Credentials.from_authorized_user_info(info=st.secrets["credentials"])
    else:
        st.error("Credentials not found in Streamlit secrets.")
        return None
    
    # Build Gmail API service
    return build('gmail', 'v1', credentials=creds)

# Function to get latest email content
def get_latest_email(service):
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        if not messages:
            return None
        message = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
        email_data = message['payload']['headers']
        subject = next(item['value'] for item in email_data if item["name"] == "Subject")
        email_body = message['snippet']
        return subject, email_body
    except Exception as error:
        st.error(f"Error getting email: {error}")
        return None

# Function to create a draft response in Gmail
def create_draft(service, message_body):
    try:
        draft = {
            'message': {
                'to': 'recipient@example.com',  # Placeholder - replace with the recipient's email
                'subject': 'Re: Your inquiry',  # Placeholder - Replace with a dynamic subject if needed
                'body': {
                    'text': message_body
                }
            }
        }
        result = service.users().messages().create(userId="me", body=draft).execute()
        return result
    except Exception as error:
        st.error(f"Error creating draft: {error}")
        return None

# App Configuration (features and settings)
st.sidebar.header("Settings")
features = {
    "response": st.sidebar.checkbox("Generate Suggested Response", value=True),
    "highlights": st.sidebar.checkbox("Highlight Key Phrases", value=True),
    "sentiment": st.sidebar.checkbox("Perform Sentiment Analysis", value=True),
    "wordcloud": st.sidebar.checkbox("Generate Word Cloud", value=True),
    "root_cause": st.sidebar.checkbox("Root Cause Detection", value=True),
    "export": st.sidebar.checkbox("Export Options", value=True)
}

# Sentiment Analysis
def get_sentiment(email_content):
    positive_keywords = ["happy", "good", "great", "excellent", "love"]
    negative_keywords = ["sad", "bad", "hate", "angry", "disappointed"]
    sentiment_score = 0
    for word in email_content.split():
        if word.lower() in positive_keywords:
            sentiment_score += 1
        elif word.lower() in negative_keywords:
            sentiment_score -= 1
    return sentiment_score

# Function to generate a draft reply
def generate_draft_reply(email_content):
    try:
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(f"Draft a professional response to this email:\n\n{email_content[:1000]}")
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, unable to generate a response at the moment."

# Layout for displaying results
if st.button("Analyze and Draft Reply"):
    # Authenticate with Gmail
    service = authenticate_gmail()
    if not service:
        st.error("Failed to authenticate with Gmail.")
    else:
        # Fetch the latest unread email
        email_content = get_latest_email(service)
        if email_content:
            subject, email_body = email_content
            st.subheader("Email Content")
            st.write(email_body)

            # Analyze the email and prepare draft reply
            if features["response"]:
                reply_content = generate_draft_reply(email_body)
                st.subheader("Suggested Reply")
                st.write(reply_content)

                # Create draft reply in Gmail
                create_draft(service, reply_content)

            if features["sentiment"]:
                sentiment = get_sentiment(email_body)
                sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                st.subheader("Sentiment Analysis")
                st.write(f"**Sentiment:** {sentiment_label} (Score: {sentiment})")

            # Key Phrases, Root Cause, etc. can be added here similarly.
            if features["root_cause"]:
                st.subheader("Root Cause Detection")
                st.write("Root Cause: Lack of communication in the process.")

            # Export options if selected
            if features["export"]:
                content = f"Subject: {subject}\n\nResponse:\n{reply_content}\n\nSentiment Analysis: {sentiment_label} (Score: {sentiment})"
                st.download_button("Download Analysis", content)

        else:
            st.write("No unread emails found.")
