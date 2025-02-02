import streamlit as st
import google.generativeai as genai
from io import BytesIO
import json
import matplotlib.pyplot as plt
import re
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Configure API Key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Gmail API setup (credentials from Streamlit secrets)
SERVICE_ACCOUNT_FILE = st.secrets["GMAIL_CREDENTIALS_JSON"]  # Path to your service account JSON
SCOPES = ['https://www.googleapis.com/auth/gmail.compose'] # Permission to create drafts

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

try:
    service = build('gmail', 'v1', credentials=credentials)
except Exception as e:
    st.error(f"Error initializing Gmail API: {e}")
    st.stop() # Stop execution if Gmail API fails


# App Configuration
st.set_page_config(page_title="Escalytics", page_icon="📧", layout="wide")
st.title("⚡Escalytics by EverTech")
st.write("Extract insights, root causes, and actionable steps from emails.")

# Sidebar for Features (All enabled by default)
st.sidebar.header("Settings")
features = {
    "sentiment": st.sidebar.checkbox("Perform Sentiment Analysis", value=True),
    "highlights": st.sidebar.checkbox("Highlight Key Phrases", value=True),
    "response": st.sidebar.checkbox("Generate Suggested Response", value=True),
    "wordcloud": st.sidebar.checkbox("Generate Word Cloud", value=True),
    "grammar_check": st.sidebar.checkbox("Grammar Check", value=True),
    "key_phrases": st.sidebar.checkbox("Extract Key Phrases", value=True),
    "actionable_items": st.sidebar.checkbox("Extract Actionable Items", value=True),
    "root_cause": st.sidebar.checkbox("Root Cause Detection", value=True),
    "culprit_identification": st.sidebar.checkbox("Culprit Identification", value=True),
    "trend_analysis": st.sidebar.checkbox("Trend Analysis", value=True),
    "risk_assessment": st.sidebar.checkbox("Risk Assessment", value=True),
    "severity_detection": st.sidebar.checkbox("Severity Detection", value=True),
    "critical_keywords": st.sidebar.checkbox("Critical Keyword Identification", value=True),
    "export": st.sidebar.checkbox("Export Options", value=True),  # Export enabled by default
}

# Input Email Section
email_content = st.text_area("Paste your email content here:", height=200)
MAX_EMAIL_LENGTH = 1000

# ... (Rest of the functions for analysis remain the same)

# Layout for displaying results
if email_content and st.button("Generate Insights"):
    try:
        # ... (All analysis functions are called as before)

        # Prepare content for export (including the draft email)
        export_content = (
            # ... (Existing export content)
            f"Suggested Response:\n{response}\n\n"  # Include the generated response
        )
        # Gmail Draft Creation
        if features["response"]: # Only create draft if response generation is enabled
            try:
                message = {
                    'message': {
                        'raw': create_message(email_content, response)
                    }
                }
                draft = service.users().drafts().create(userId='me', body=message).execute()
                st.success(f"Draft saved successfully! Draft ID: {draft['id']}")
            except Exception as e:
                st.error(f"Error saving draft: {e}")

        # Export options
        if features["export"]:
            # ... (Export options remain the same)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Paste email content and click 'Generate Insights' to start.")


def create_message(email_content, draft_content):
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Basic email structure (you'll likely need to customize this)
    message = MIMEMultipart()
    message['To'] = "recipient@example.com"  # Replace with actual recipient or leave blank for draft
    message['From'] = "your_email@example.com"  # Replace with your email
    message['Subject'] = "Re: " + email_content[:50] + "..." if len(email_content)>50 else email_content # Add a subject
    # Email body (using the generated draft content)
    msg = MIMEText(draft_content)
    message.attach(msg)
    raw_message = message.as_string()
    b64_encoded_message = base64.urlsafe_b64encode(raw_message.encode("UTF-8")).decode("ascii")
    return b64_encoded_message
