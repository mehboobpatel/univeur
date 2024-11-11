from azure.identity import DefaultAzureCredential
from flask import Flask, render_template, request
import pyodbc
from azure.keyvault.secrets import SecretClient

from gtts import gTTS
import datetime
import os

current_datetime = datetime.datetime.now()

app = Flask(__name__)


credential = DefaultAzureCredential()

username = 'voiceadmin'
password = 'Voice@1234'


#Below we will pulling the Vault url from App service settings in Azure

# VAULT_URL = os.getenv("KEY_VAULT")

# client = SecretClient(vault_url=VAULT_URL, credential=credential)

# Retrieve secrets from Key Vault
# username = client.get_secret('DBUSERNAME').value
# password = client.get_secret('DBPASSWORD').value

# Connect to Azure SQL DB
server = 'reception.database.windows.net'
database = 'reception'

driver = '{ODBC Driver 17 for SQL Server}'
# Use Azure AD authentication
credential = DefaultAzureCredential()
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')

# cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};Authentication=ActiveDirectoryPassword;UID=VoiceDB@masterpatel786yahoo.onmicrosoft.com;PWD={password}')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return submit()
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    full_name = request.form.get('full_name')
    purpose = request.form.get('purpose')
    number = request.form.get('number')
    welcome_message = f"Welcome {full_name} This App is completely deployed on Azure Architecture by Mehboob Patel"
    gender = request.form.get('gender') 

    visit_date = current_datetime.date()
    visit_time = current_datetime.time().strftime('%H:%M:%S')

    # Insert user details into boomlet table
    cursor = cnxn.cursor()
    insert_query = f"INSERT INTO users (full_name, purpose, number, gender, date, time) VALUES ('{full_name}', '{purpose}', '{number}', '{gender}', '{visit_date}', '{visit_time}')"
    cursor.execute(insert_query)
    cnxn.commit()

    # Generate audio file using gTTS
    tts = gTTS(welcome_message)
    static_dir = 'static'
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    tts.save(f"static/{full_name}.mp3")

    return render_template('success.html', full_name=full_name, purpose=purpose, number=number, gender=gender, current_date=visit_date, current_time=visit_time)

@app.route('/database', methods=['GET'])
def database():
    # Select all records from boomlet table
    cursor = cnxn.cursor()
    select_query = "SELECT * FROM users"
    cursor.execute(select_query)
    rows = cursor.fetchall()

    return render_template('database.html', rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

    