from flask import Flask, jsonify, request, url_for, redirect , session , render_template, g 
import sqlite3

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'This secret' #no sensitive info in session cookies !

def connect_db():
	sql = sqlite3.connect('/home/vagrant/src/Flask Projects/app01/data.db') #filepath is relative to Virtual Env
	sql.row_factory = sqlite3.Row  #dictionaries instead of tuples
	return sql

def get_db():           # to check if db already loaded
	if not hasattr(g, 'sqlite3'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext  # to auto close db
def clos_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close() # so not left vulnerable


@app.route('/')
def index():
	session.pop('name', None)
	return '<h1>Hello, All!</h1>'


@app.route('/home', methods=['POST','GET'], defaults={'name' : 'Default'})

@app.route('/home/<string:name>', methods=['POST','GET'])
def home(name):
	session['name'] = name
	db =get_db()
	cur = db.execute('select id, name, location from users')
	results = cur.fetchall()

	return render_template('home.html', name=name , display=True, \
	   myList=['one','two','three','four'], dictList=[{'name' : 'Zach'}, {'name' : 'Zoe'}], results=results)


@app.route('/json')
def json():
	if 'name' in session:

		name = session['name']
	else:
	   	name = 'NotInSession'
	return jsonify({'key' : 'value', 'listkey' : [1,2,3,], 'name' : name})

@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hiya{}! You are from {}. This is your query page</h1>'.format(name,location)

                     #alt , methods=['GET', 'POST']
@app.route('/theform', methods=['GET','POST'])#default 'GET' 
def theform():
    if request.method == 'GET':
	    return render_template('form.html')
    else: 
	    name = request.form["name"]
	    location = request.form['location']


	    db = get_db()
	    db.execute('insert into users (name, location) values (?, ?)', [name, location])
	    db.commit() #because sqlite is transactional
	    
	    
	    return redirect(url_for('home', name=name, location=location))


@app.route('/theform', methods=['POST'])
def process():
    name = request.form['name']
    location = request.form['location']
    return '<h2>Hey {} from {}. Your form was submitted.</h2>'.format(name, location)
	


@app.route('/processjson', methods=['POST'])
def processjson():

    data = request.get_json()
    
    name = data["name"]
    location = data["location"]

    randomList = data["randomList"]

    return jsonify({'result' : 'Success', 'name' : name, 'location' : location, 'randomkeyinlist' : randomList[1]})

@app.route('/viewresults')
def viewresults():
	db = get_db()
	cur = db.execute('select id, name, location from users')
	results = cur.fetchall()
	return '<h1>The ID is {}. The name is {}. The location is {}.</h1>'.format(results[3]['id'], results[3]['name'], results[3]['location'])

if __name__ == '__main__':
	app.run(host ='0.0.0.0')