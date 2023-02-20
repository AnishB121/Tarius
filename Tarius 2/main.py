import os
import requests
from flask import Flask,render_template,redirect, url_for, request,session
import sqlite3
import googlemaps
import json
import time
from flask_login import LoginManager, login_user, current_user, login_required, logout_user,UserMixin #login_form
from getLocations import getLocationsMain
from flask_session import Session
namelist = []
placeidlist = []
location = []
user_loc_list=[]
address=""
phonenumber=""
website=""

connection = sqlite3.connect("volunteeringOP.db")
crsr = connection.cursor()
command="""CREATE TABLE IF NOT EXISTS vol_data (
  id INTEGER PRIMARY KEY ,
  name TEXT NOT NULL,
  hours REAL NOT NULL,
  descrption TEXT NOT NULL,
  areacode REAL NOT NULL,
  creator INTEGER KEY,
  pictureurl TEXT NOT NULL
)
"""
crsr.execute(command)
connection.commit()
connection.close()
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             username TEXT, password TEXT)''')
conn.commit()
conn.close()
conn = sqlite3.connect('volunteer.db')
c = conn.cursor()
c.execute('''
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            hours REAL NOT NULL
        )
    ''')
conn.commit()
conn.close()
def get_loc(ip):
	key=""
	url = f'https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={key}&outputFormat=JSON&ip={ip}'
	response = requests.get(url)
	data = response.json()
	if 'city' in data:
		city = data['city']
		return city

#users={}#make database L


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ryanisverycool'
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return User(result[0], result[1], result[2])
    else:
        return None
@app.route('/',methods=['GET','POST'])
def index():
	return render_template('index.html')
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (request.form['username'],))
        result = c.fetchone()
        if result:
            conn.close()
            return redirect(url_for('index'))
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (request.form['username'], request.form['password']))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (request.form['username'],))
    result = c.fetchone()
    if not result:	
      conn.close()
      return render_template('index.html')
    if request.form['password'] != result[2]:
      conn.close()
      return render_template('index.html')
    user = User(result[0], result[1], result[2])
    login_user(user)
    conn.close()
    user_loc_list.append(request.form["location"])
    return redirect(url_for('home'))

  return render_template('login.html')
'''
@app.route('/vol',methods=['GET','POST'])
def vol():
	if request.method == "POST":
		nhours = request.form['hours']
		conn = sqlite3.connect('volunteer.db')
		c = conn.cursor()
		if 'username' in session:
		 c.execute("UPDATE volunteers SET hours=hours+? WHERE username=?", (nhours, session["username"]))
		 conn.commit()
		 conn.close()
	if 'username' in session:
		hours = getvol(session["username"])
		return render_template('volunteer.html',hours=hours)
	else:
		print("fail")
		return render_template('volunteer.html')
'''
@app.route('/home',methods=['GET','POST'])
def home():
  # user_ip = request.remote_addr
  # location = get_loc(user_ip)
  location = user_loc_list[0]
  unpack = getLocationsMain(location)
  namelist = unpack[0]
  # print("kafa", namelist)
  photolist = unpack[1]
  names = []
  nimgs = []
  for i in range(8):
    # print("kblaaahaghaga", namelist[i])
    names.append(namelist[i])
    for i in range(8):
        # print("ajfdsfabaha", photolist[i])
        if photolist[i]:
            addtothing = photolist[i][0].get("photo_reference")
            finallink = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=" + str(addtothing) + "&key=" + os.environ["apikeysecret"]
            nimgs.append(finallink)
  return render_template('home.html', data1=names[0], data2=names[1], data3=names[2], data4=names[3], data5=names[4], data6=names[5], data7=names[6], data8=names[7], pic1=nimgs[0], pic2=nimgs[1], pic3=nimgs[2], pic4=nimgs[3], pic5=nimgs[4], pic6=nimgs[5], pic7=nimgs[6], pic8=nimgs[7])

def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/opp/<name>',methods=['GET','POST'])
def opp(name):
  print("kokokokokokokokokokok")
  address = ""
  phonenumber = ""
  website = ""
  description = ""
  image = ""
  print(user_loc_list)
  unpack = getLocationsMain(user_loc_list[0])
  namelist = unpack[0]
  placeidlist = unpack[2]
  for i in range(8):
    print(name)
    if namelist[i] == name:
      url = "https://maps.googleapis.com/maps/api/place/details/json?fields=name%2Cformatted_address%2Cinternational_phone_number%2Cwebsite%2Ceditorial_summary%2Cphoto&place_id=" + placeidlist[i] + "&key=" + os.environ['apikeysecret']
      payload = {}
      headers = {}
      response = requests.request("GET", url, headers=headers, data=payload)
      jdata = json.loads(response.text)
      print("bah", jdata, type(jdata))
      address = jdata.get('result').get('formatted_address')
      phonenumber = jdata.get('result').get('international_phone_number')
      website = jdata.get('result').get('website')
      description = jdata.get('result').get('editorial_summary')
      if jdata.get('result').get('photos'):
          image = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=" + str(jdata.get('result').get('photos')[0].get('photo_reference')) + "&key=" + os.environ["apikeysecret"]
      else:
          image = "/static/bullnotfound.png"
      if description != None and description != "None":
        description = description.get('overview')
      else:
        description = "Local charity/volunteer organization that can provide high school volunteer hours."
      print(address, phonenumber, website, description, image)
  return render_template('view.html', name=name, loc=address, contact=phonenumber, desc=description, website=website,img=image)


connection = sqlite3.connect('newops.db')
crsr = connection.cursor()
passion_command = """CREATE TABLE IF NOT EXISTS new_op (
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  description TEXT NOT NULL
)"""
crsr.execute(passion_command)
connection.commit()
connection.close()
@app.route('/create', methods = ['GET','POST'])
def create():
	if request.method=="GET":
		return render_template('create.html')
	if request.method == "POST":
		connection = sqlite3.connect('newops.db')
		crsr = connection.cursor()
		passion_project_query= """INSERT INTO new_op (name, email,description) VALUES (?, ?, ?)"""
		crsr.execute(passion_project_query,(request.form['name'],request.form['email'],request.form['description']))
		return render_template('index.html')
app.run(host='0.0.0.0', port=81)
