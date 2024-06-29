from flask import Flask, render_template, request
import pyodbc
from gtts import gTTS
import datetime
from azure.identity import DefaultAzureCredential

app = Flask(__name__)

# Database connection details
server = 'voiceserver.database.windows.net'
database = 'voicedb'
driver = '{ODBC Driver 17 for SQL Server}'

# Use DefaultAzureCredential to get a token for Azure SQL
credential = DefaultAzureCredential()
token = credential.get_token("https://database.windows.net/.default").token.encode('utf-16le')

# Connect to Azure SQL DB
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};'
cnxn = pyodbc.connect(conn_str, attrs_before={1256: token})  # SQL_COPT_SS_ACCESS_TOKEN

current_datetime = datetime.datetime.now()

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
    welcome_message = f"Welcome {full_name} This App is completely deployed on Azure Architecture by Maheboob"
    gender = request.form.get('gender')

    current_date = current_datetime.date()
    current_time = current_datetime.time().strftime('%H:%M:%S')

    cursor = cnxn.cursor()
    insert_query = "INSERT INTO users (full_name, purpose, number, gender, date, time) VALUES (?, ?, ?, ?, ?, ?)"
    cursor.execute(insert_query, (full_name, purpose, number, gender, current_date, current_time))
    cnxn.commit()

    tts = gTTS(welcome_message)
    tts.save(f"static/{full_name}.mp3")

    return render_template('success.html', full_name=full_name, purpose=purpose, number=number, gender=gender, current_date=current_date, current_time=current_time)

@app.route('/database', methods=['GET'])
def database():
    cursor = cnxn.cursor()
    select_query = "SELECT * FROM users"
    cursor.execute(select_query)
    rows = cursor.fetchall()

    return render_template('database.html', rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
