from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from replit import db #replit database
import os #for env variable passwords
import pdf_parser
import txt_ai_analyze
import email_parser

app = Flask(__name__)
auth = HTTPBasicAuth()
# username and password environment variables 
my_secret_usr = os.environ['username']
my_secret_psswd = os.environ['password']

users = {
    my_secret_usr : my_secret_psswd,
}

# init database variables as NULL
db['pdfDL_url']  = ""
db['report_Num'] = ""
db['landingURL'] = ""
    
@auth.get_password
def get_password(username):
    if username in users:
        return users.get(username)
    return None

@auth.error_handler
def unauthorized():
    return "Unauthorized access", 401

@app.route('/', methods=['POST'])
@auth.login_required
def handle_webhook():
    data = request.get_json()
    #extract email data and fetch pdf dl url
    #print(data['email_body'])
    email_body = str(data['email_body'])
    #print(email_body)
    extracted = email_parser.extract_msg_data(email_body)
    #write extracted to database
    db['pdfDL_url']  = extracted[0]['downloadURL']
    db['report_Num'] = extracted[0]['reportNum']
    db['landingURL'] = extracted[0]['pageURL']
    
    return "Webhook received successfully", 200

@app.route('/', methods=['GET'])
@auth.login_required
def return_boolean():
    #load values from database 
    pdfDL_url = db['pdfDL_url'] 
    report_Num = db['report_Num']  
    landing_URL = db['landingURL']  
  
    #Get extracted pdf text from url save to var
    pdf_txt = pdf_parser.extract_pdf_txt(pdfDL_url)
    #Search and retrieve locations in extracted pdf text
    pdf_loc = txt_ai_analyze.ai_location_search(pdf_txt)
    #Return dictionary with extracted pdf data to zapier
    pdf_data = {"pdfText" : pdf_txt , "pdfLocations" : pdf_loc,
                "reportNum" : report_Num, "pageURL" : landing_URL,
                "pdfDL_url" : pdfDL_url
               }
    return pdf_data
# If this script is executed directly (not imported as a module), start the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0")
