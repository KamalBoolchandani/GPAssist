import os
import openai
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import subprocess

# OpenAI API key
openai.api_key = ""

# Google API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
          'https://www.googleapis.com/auth/documents.readonly']
current_directory = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(current_directory, 'gpassist-443008-f6377e3451cf.json')
creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=creds)
docs_service = build('docs', 'v1', credentials=creds)

# Constants for Google Sheet and Doc
spreadsheet_id = '1MHx3ce5yGhZDN5SCHiiK0Ny68p4_zT7H5fRdVppTWI4'
range_name='Sheet1!B2'  # Adjust as needed
FAQ_DOC_ID = "1FTW8R0Yqxqd2CqkE9pasj3-cftbuUvi_at-nv7_zx1c"

# Function to read Google Sheet data
def read_sheet_data():
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        print('No data found in the sheet.')
    else:
        return values


# Function to read FAQ Google Doc content
def read_faq_doc():
    doc = docs_service.documents().get(documentId=FAQ_DOC_ID).execute()
    content = ""
    for element in doc.get('body').get('content'):
        if 'paragraph' in element:
            for text_run in element['paragraph']['elements']:
                content += text_run.get('textRun', {}).get('content', "")
    return content

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

        print("S3 bucket provisioned successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during Terraform execution: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")

# OpenAI Chatbot logic
def chatbot_response(user_input):
    # Define intents
    if "leave balance" in user_input.lower():
        sheet_data = read_sheet_data()
        user = "John Doe"  # Example user
        leave_type = "sick"  # Example leave type
        return f"{user} has {sheet_data} sick leaves remaining."  # Adjust as needed
    elif "apply leave" in user_input.lower():
        sheet_data = read_sheet_data()
        return apply_leave("John Doe", "sick", 3, sheet_data)  # Example
    elif "faq" in user_input.lower():
        faq_content = read_faq_doc()
        return f"FAQs: \n{faq_content}"
    elif "provision" in user_input.lower():
        return provision_s3()
    else:
        return "Sorry, I didn't understand your request."

# # Main chatbot loop
# if __name__ == "__main__":
    
#     print("Chatbot is running. Type 'exit' to quit.")
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == "exit":
#             break
#         response = chatbot_response(user_input)
#         print(f"Bot: {response}")
