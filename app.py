from flask import Flask, render_template, request, g
import pyodbc
from gtts import gTTS
import datetime
import logging
from azure.identity import InteractiveBrowserCredential

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database connection details
server = 'voiceserver.database.windows.net'
database = 'voicedb'
driver = '{ODBC Driver 17 for SQL Server}'

def get_db_connection():
    if 'cnxn' not in g:
        try:
            credential = InteractiveBrowserCredential()
            token = credential.get_token("https://database.windows.net/.default").token.encode('utf-16le')

            # Connect to Azure SQL DB
            conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};'
            g.cnxn = pyodbc.connect(conn_str, attrs_before={1256: token})  # SQL_COPT_SS_ACCESS_TOKEN
            logger.info("Connected to the database successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            g.cnxn = None
    return g.cnxn

@app.teardown_appcontext
def close_db_connection(exception):
    cnxn = g.pop('cnxn', None)
    if cnxn is not None:
        cnxn.close()

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

    cnxn = get_db_connection()
    if cnxn is None:
        return "Database connection error", 500

    try:
        cursor = cnxn.cursor()
        insert_query = "INSERT INTO users (full_name, purpose, number, gender, date, time) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (full_name, purpose, number, gender, current_date, current_time))
        cnxn.commit()
        logger.info("Inserted data into the database successfully.")
    except Exception as e:
        logger.error(f"Failed to insert data into the database: {e}")
        return "Database error", 500

    tts = gTTS(welcome_message)
    tts.save(f"static/{full_name}.mp3")

    return render_template('success.html', full_name=full_name, purpose=purpose, number=number, gender=gender, current_date=current_date, current_time=current_time)

@app.route('/database', methods=['GET'])
def database():
    cnxn = get_db_connection()
    if cnxn is None:
        return "Database connection error", 500

    try:
        cursor = cnxn.cursor()
        select_query = "SELECT * FROM users"
        cursor.execute(select_query)
        rows = cursor.fetchall()
        logger.info("Fetched data from the database successfully.")
    except Exception as e:
        logger.error(f"Failed to fetch data from the database: {e}")
        return "Database error", 500

    return render_template('database.html', rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
