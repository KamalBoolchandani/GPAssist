import os
import openai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import subprocess
import io
from googleapiclient.http import MediaIoBaseDownload
import csv
import re

# OpenAI API key
openai.api_key = ""

# Google API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
          'https://www.googleapis.com/auth/documents.readonly',
          'https://www.googleapis.com/auth/drive.readonly']
current_directory = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(current_directory, 'gpassist-443008-f6377e3451cf.json')
creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=creds)
docs_service = build('docs', 'v1', credentials=creds)
doc_service = build('drive', 'v3', credentials=creds)

# Constants for Google Sheet and Doc
spreadsheet_id = '1MHx3ce5yGhZDN5SCHiiK0Ny68p4_zT7H5fRdVppTWI4'
range_name='Sheet1!F2'  # Adjust as needed
FAQ_DOC_ID = "1FTW8R0Yqxqd2CqkE9pasj3-cftbuUvi_at-nv7_zx1c"

conversation_state = {}

# Function to read Google Sheet data
def read_sheet_data():
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values')
    if not values:
        print('No data found in the sheet.')
    else:
        return values
    
## url checker
def is_url(text):
    # Check if the text is a valid URL
    url_regex = re.compile(r'https?://[^\s]+')
    return url_regex.match(text)

# Function to read FAQ Google Doc content
def read_faq_doc(user_input):

    # File ID of the Google Sheet (found in its URL)
    FILE_ID = '1PIPER6IsgSJLzWRaF3Yvm0Wpc2OcRXOUOJ4VBdKj8SU'

# Specify the desired export MIME type for CSV
    MIME_TYPE = 'text/csv'

# Path to save the downloaded file
    output_file_path = 'output.csv'

# Request to export the file
    request = doc_service.files().export_media(fileId=FILE_ID, mimeType=MIME_TYPE)
    # Download the file
    with io.FileIO(output_file_path, 'wb') as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")

    print(f"File downloaded as {output_file_path}")

    # below code will help to know required data

    file_path = "output.csv"
    # id_name = input("inter your quesions: ")
    # Open and read the CSV file
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)  # Reads rows as dictionaries
        for row in csv_reader:
            #print(row)
            # Access specific data by column name
            if user_input in row["Questions"].lower():
                if is_url(row['Answers']):  # Condition to filter specific row
                    return f'<a href="{row["Answers"]}" target="_blank">{row["Answers"]}</a>'
                else:
                    return(f"{row['Answers']}")
                
        return(f"Sorry! I could not find any thing related to {user_input}  Can you please rephrase?")
   
# Function to apply leave
def apply_leave(user, leave_type, days, sheet_data):
    for row in sheet_data:
        if row[0].lower() == user.lower() and row[1].lower() == leave_type.lower():
            remaining = int(row[3])
            if remaining >= days:
                return f"Leave applied! {remaining - days} {leave_type} leaves remaining."
            else:
                return f"Insufficient {leave_type} leaves. Only {remaining} remaining."
    return f"No record found for {user} with leave type {leave_type}."

# Function to provision AWS resources
def provision_s3():
   
    try:
        # Set the directory where the Terraform file is located
        
        terraform_dir = os.path.dirname(os.path.abspath(__file__))  # Current directory
        
        # Step 1: Initialize Terraform
        print("Initializing Terraform...")
        subprocess.run(["terraform", "init"], cwd=terraform_dir, check=True)

        # Step 2: Apply Terraform configuration
        print("Applying Terraform configuration...")
        subprocess.run(
            ["terraform", "apply", "-auto-approve"], cwd=terraform_dir, check=True
        )

        return ("S3 bucket provisioned successfully!")
    except subprocess.CalledProcessError as e:
        return(f"Error during Terraform execution: {e}")
    except Exception as ex:
        return(f"Something went wromg please try again: {ex}")

# OpenAI Chatbot logic
        
def chatbot_response(user_input):
    global conversation_state

    # Handle "Apply Leave" intent
    if conversation_state.get("intent") == "apply_leaves" and conversation_state.get("step") == "ask_date":
        chosen_date = user_input.strip()
        if chosen_date.lower() == "cancel":
            conversation_state.clear()
            return "Leave application canceled."
        else:
            conversation_state.clear()
            return f"Leave for {chosen_date} has been applied successfully and it is awaiting your manager's approval"

    if "apply leave" in user_input.lower():
        conversation_state["intent"] = "apply_leaves"
        conversation_state["step"] = "ask_date"
        response= "Please provide the date for your leave in dd-mm-yyyy format (or type 'cancel' to exit)."
        return response

    # Handle "Provision Resources" intent
    elif conversation_state.get("intent") == "provision_resources":
        if conversation_state.get("step") == "ask_cloud":
            if user_input.lower() == "aws":
                conversation_state["cloud"] = "AWS"
                conversation_state["step"] = "ask_resource"
                return "Great! What resource would you like to provision? (S3 or EC2)"
            else:
                return "Currently, we support only AWS. Please type 'AWS' to proceed."
        elif conversation_state.get("step") == "ask_resource":
            if user_input.lower() in ["s3", "ec2"]:
                resource = user_input.upper()
                cloud = conversation_state.get("cloud")
                conversation_state.clear()
                return provision_s3()
                # return f"Starting provisioning of {resource} on {cloud}..."
            else:
                return "We support only S3 or EC2. Please choose one of these resources."

    elif "provision" in user_input.lower():
        conversation_state["intent"] = "provision_resources"
        conversation_state["step"] = "ask_cloud"
        return "Which cloud provider would you like to use? (Currently, we support only AWS)"
    
    elif "leave balance" in user_input.lower():
        sheet_data = read_sheet_data()
        user = "You"  # Example user
        leave_type = "Total"  # S
        return f"{user} have {sheet_data}  leaves remaining." 
    
    else: 
        faq_content = read_faq_doc(user_input.lower())
        return f"FAQs: \n{faq_content}"

# Main chatbot loop
if __name__ == "__main__":
    
    print("Chatbot is running. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = chatbot_response(user_input)
        print(f"Bot: {response}")
