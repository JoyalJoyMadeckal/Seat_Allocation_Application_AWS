from datetime import datetime
from flask import Flask, jsonify, render_template, request, session, redirect
import requests
import boto3


app = application = Flask(__name__)
app.secret_key = "abcd"

def login_or_logout():
    login = False
    if 'username' in session:
        login = True
    return login

@app.route('/')
def index():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect('/admin/seats')
        return redirect("/seatselect")
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'Logout' in request.form.keys():
            session.pop('username', None)
            return redirect('/')
        user_name = request.form['username']
        password = request.form['password']
        token = {'user_name':user_name, 'password':password}
        authenticated = requests.post("https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/loginvalidate", json=token) # should be rest API
        if authenticated.json()['validate']:
            session['username'] = user_name
            if authenticated.json()['admin']:
                session['role'] = 'admin'
                return redirect('/admin/seats')
            else:
                session['role'] = 'user'
                return redirect('/seatselect')
        else:
            return render_template('login.html', login_message='The user name or password does not exist', show=False)

    
    return render_template('login.html', show=False)

@app.route('/seatselect', methods=["GET", "POST"])
def seatselect():
    if 'username' in session:
        print('some')

        weatherdata = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=37.81&lon=144.96&appid=7672f07379b9b23c0a5c3a65aedd9b91")

        resp = requests.get("https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/fetchseatsallocated")

        if request.method == 'GET':
            return render_template("seatselect.html", seats_allocated = resp.json()['allocated_seats'], show=True,
            weather={'main': weatherdata.json()['weather'][0]['description'], 'temp': round(weatherdata.json()['main']['temp']-273.15)})
        
        seat_allocated  = request.form['seat'] if len(request.form.keys()) else None

        if not seat_allocated:
            return render_template("seatselect.html", message="You haven't selected your seat",
             seats_allocated = resp.json()['allocated_seats'], show=True, error=True)

        requests.post(f"https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/seatselect",
                    json={'user': session['username'], 'seat': seat_allocated})

        resp = requests.get("https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/fetchseatsallocated")

        return render_template("seatselect.html", message="The seat is allocated successfully.", show=True,
        seats_allocated = resp.json()['allocated_seats'], error=False, weather=weatherdata.json())
    return redirect('/login')


@app.route('/admin/seats', methods=["GET", "POST"])
def seatselectadmin():
    if 'username' in session:
        resp = requests.get("https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/fetchseatsallocated")

        if request.method == 'GET':
            return render_template("seatselectadmin.html", seats_allocated = resp.json()['allocated_seats'], show=True)

        seat_allocated  = request.form.keys() if len(request.form.keys()) else []

        if set(seat_allocated) != set(resp.json()['allocated_seats']):
            requests.post("https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/updateseatallocation", json={'new_seats': list(seat_allocated), 
                        'old_seats': resp.json()['allocated_seats'], 'users': resp.json()['users']})
        
        
        file = request.files['file']
        if file.filename:
            s3 = boto3.client('s3')
            s3.upload_fileobj(file, "bookmyseat", str(datetime.now()))

        print(set(seat_allocated), set(resp.json()['allocated_seats']))

        condition = ((set(seat_allocated) != set(resp.json()['allocated_seats'])) or file.filename )

        message = "File upload and Seat updation completed" if condition else "No updations done."
        error = True if condition else False

        resp = requests.get("https://syx55jaon7.execute-api.us-east-1.amazonaws.com/Dev/fetchseatsallocated")

        return render_template("seatselectadmin.html", message=message, show=True,
        seats_allocated = resp.json()['allocated_seats'], error=error)
    return redirect('/login')