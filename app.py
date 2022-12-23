from datetime import datetime
from json import JSONDecoder
import json
import time
from xml.dom import NOT_FOUND_ERR
from flask import Flask, flash, render_template, request, session, redirect, url_for
import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth, firestore
from flask_session import Session
from python_helper.helper import checkIp, getAllUsers, getLevelUpRequirement, getLevelsForAdmin, getReferalsForAdmin, getTurnaments, getTurnamentsForAdmin, getUser, getWithdrawlsForAdmin, levelUp
import collections


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

firebaseConfig = {
    'apiKey': "AIzaSyCSB9x_WJxAeJXcyuVXJXQ2umL1-Vv_HyU",
    'authDomain': "game-arn.firebaseapp.com",
    'projectId': "game-arn",
    'storageBucket': "game-arn.appspot.com",
    'messagingSenderId': "662773918950",
    'appId': "1:662773918950:web:d63514dd35e386903ddf27",
    'measurementId': "G-H25T9QWD2C",
    'databaseURL': "",

}

firebase = pyrebase.initialize_app(firebaseConfig)
admin = 'QJOT6GCrTdWmiuE9ZncFPz5KdBM2'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aasfwhbedhRRSGDDYT*^&^%&(3435453GHXTYVUIHG54&^%'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def landingPage():
    loggedIn = False

    return render_template('index.html', loggedIn=firebase.auth().current_user != None)


@app.route("/dashboard")
def dashboad():
    user = None
    data = None
    turnaments = None
    if session.get('user') != None:
        user = getUser(session.get('user'))
        print(user)
        data = getLevelUpRequirement(user['level'])
        turnaments = getTurnaments(session.get('user'))
        levelUp(user['score'], user['level'], user['id'])

        user['levelup'] = data
        user['turnaments'] = turnaments
        print(user)

    if user != None:
        if user['id'] == admin:
            allusers = getAllUsers()
            return render_template('admin_users_tables.html', LoggedIn=session.get('user') != None, user_data=user, allUsers=allusers)
        else:
            return render_template('dashboard.html', LoggedIn=session.get('user') != None, user_data=user)
    else:
        return redirect("/login")


@app.route("/login", methods=['POST', 'GET'],)
def login():
    print(session.get('user') != None)
    email = request.form.get('email')
    password = request.form.get('password')
    if request.method == 'POST':
        if len(password) < 6:
            flash('Password must be at least 6 characters', category='error')
        else:
            try:
                _auth = firebase.auth().sign_in_with_email_and_password(
                    email=email, password=password)
                print(_auth)
                session['user'] = _auth['localId']
                flash('Login successful', category='Success')
            except:
                flash('Login unsuccessful', category='error')

    return render_template('login.html', LoggedIn=session.get('user') != None)


@app.route("/signup", methods=['POST', 'GET'],)
def signup():

    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirmpassword')
    name = request.form.get('name')

    if request.method == 'POST':
        ipaddress = request.args.get('ip')
        if ipaddress != None:
            checks = checkIp(ipaddress)
            print(checks)
            if checks == False:
                if password != confirm:
                    flash('Password Not Matched', category='error')
                elif len(password) < 6:
                    flash('Password must be at least 6 characters',
                          category='error')
                else:

                    _auth = auth.create_user(email=email, password=password)

                    if _auth.uid != None:
                        firestore.client().collection('Users').document(_auth.uid).set({
                            'email': email,
                            'name': name,
                            'id': _auth.uid,
                            'level': 0,
                            'score': 0,
                            'referals': [],
                            'earning': 0,
                            'withdrawl': 0,

                        })
                        session['user'] = _auth.uid
                        referalCode = request.args.get('referal_code')

                        print(referalCode)
                        if referalCode != None:
                            firestore.client().collection('ReferalsRequest').add({
                                'date': str(datetime.now().strftime("%Y:%m:%d")),
                                'inviter': referalCode,
                                'new': True,
                                'new_user':  _auth.uid,
                                'reward': 1,
                                'status': False,
                            })
                        firestore.client().collection('Ip Address').document(
                            str('Ip Address')).update({'Ip': firestore.ArrayUnion([ipaddress])})
                        flash('Account created Succesfully', category='Success')

                    else:
                        if checkIp(ipaddress):
                            flash('One Device can have only one account !',
                                  category='error')
                        else:
                            flash('Account Not Created', category='error')
            else:
                flash('One Device can have only one account !', category='error')

    return render_template('signup.html', LoggedIn=session.get('user') != None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/pingpong", methods=['GET', 'POST'])
def pingpong():
    id = session.get('user')
    high_score = getTurnaments(session.get('user'))
    user = getUser(id)
    if request.method == 'POST':
        data = request.json['score']
        data = int(data)
        print(high_score)
        firestore.client().collection('Users').document(
            id).update({'score': user['score'] + data})
        if data > high_score['participants_score']:
            firestore.client().collection('turnaments').document(str(datetime.now().strftime("%Y:%m:%d"))
                                                                 ).update({'participants': firestore.ArrayUnion([{'user': id, 'score': data}])})
            if 'participant_array_id' in high_score:
                firestore.client().collection('turnaments').document(str(datetime.now().strftime("%Y:%m:%d"))
                                                                     ).update({'participants': firestore.ArrayRemove([high_score['participant_array_id']])})

    return render_template('pingpong.html', LoggedIn=session.get('user') != None, high_score=high_score['highest_score'],testmode= False)


@app.route("/createturnament", methods=['POST'])
def createturnament():
    id = '2022:08:20'
    if admin:
        # cu = getTurnaments(id)
        # print(cu)
        # user = getUser(cu['leaderboard'][0]['id'])
        while 1 == 1:
            # firestore.client().collection('Users').document(
            #     id).update({'earning': user['earning'] + cu['prize']})
            firestore.client().collection('turnaments').document(str(datetime.now().strftime("%Y:%m:%d"))).set({
                'participants': [],
                'prize': 10,
                'reset_time': datetime.now().strftime("%Y:%m:%d"),
                'start_time': datetime.now().strftime("%Y:%m:%d"),
            })
            id = str(datetime.now().strftime("%Y:%m:%d"))
            time.sleep(86400)

    return 'working'


@app.route("/turnaments")
def turnaments():
    user = None

    turnaments = None
    if session.get('user') != None:
        user = getUser(session.get('user'))
        print(user)
        turnaments = getTurnamentsForAdmin()
        levelUp(user['score'], user['level'], user['id'])

        user['turnaments'] = turnaments
        print(turnaments)

    if user != None:
        if user['id'] == admin:

            return render_template('turnaments.html', LoggedIn=session.get('user') != None, user_data=user,)
        else:
            return render_template('404.html')
    else:
        return redirect("/login")


@app.route("/levels")
def levels():
    user = None

    if session.get('user') != None:
        user = getUser(session.get('user'))
        user['levels'] = getLevelsForAdmin()
        print(user)

    if user != None:
        if user['id'] == admin:

            return render_template('levels.html', LoggedIn=session.get('user') != None, user_data=user)
        else:
            return render_template('404.html')
    else:
        return redirect("/login")


@app.route("/withdrawls")
def withdrawls():
    user = None

    if session.get('user') != None:
        user = getUser(session.get('user'))
        user['withdrawls'] = getWithdrawlsForAdmin()

    if user != None:
        if user['id'] == admin:

            return render_template('withdrawls.html', LoggedIn=session.get('user') != None, user_data=user)
        else:
            return render_template('404.html')
    else:
        return redirect("/login")


@app.route("/referals")
def referals():
    user = None

    if session.get('user') != None:
        user = getUser(session.get('user'))
        user['referals'] = getReferalsForAdmin()

    if user != None:
        if user['id'] == admin:

            return render_template('referals.html', LoggedIn=session.get('user') != None, user_data=user)
        else:
            return render_template('404.html')
    else:
        return redirect("/login")


@app.route("/makepayment/<string:id>", methods=['Post'])
def makepayment(id):

    firestore.client().collection('withdrawls').document(id).update({
        'status': True
    })
    return 'Done'


@app.route("/approveRef/<string:id>/<string:status>", methods=['Post'])
def approveRef(id, status):
    ref = getReferalsForAdmin()
    print(ref)
    for r in ref:
        if r['id'] == id:
            user = getUser(r['inviter'])
            print(user)
            firestore.client().collection('Users').document(str(r['inviter'])).update({'referals': firestore.ArrayUnion(
                [{'id': r['new_user'], 'prize':r['reward']}]), 'earning': user['earning'] + r['reward']})
            firestore.client().collection('ReferalsRequest').document(
                id).update({'status': True, 'new': False})
    return 'Done'


@app.route("/unapproveRef/<string:id>/<string:status>", methods=['Post'])
def unapproveRef(id, status):
    ref = getReferalsForAdmin()
    for r in ref:
        if r['id'] == id:
            firestore.client().collection('ReferalsRequest').document(
                id).update({'status': False, 'new': False})
    return 'Done'


@app.route("/requestWithdrawl/<string:medium>/<int:cost>/<string:number>", methods=['Post'])
def requestWithdrawl(medium, cost, number):
    user = getUser(session.get('user'))
    if user['earning'] >= cost:
        firestore.client().collection('withdrawls').add({
            'amount': cost,
            'date': str(datetime.now().strftime("%Y:%m:%d")),
            'expected_delivery_date': str(datetime.now().strftime("%Y:%m:%d")),
            'medium': medium,
            'status': False,
            'number': number
        })

        firestore.client().collection('Users').document(
            user['id']).update({'earning': user['earning'] - cost})

    return 'Done'


@app.route("/privacypolicy")
def privacypolicy():

    return render_template('privacypolecy.html')

@app.route("/testpingpong")
def testpingpong():

    return render_template('pingpong.html', LoggedIn=session.get('user') != None, high_score=5000,testmode= True)


@app.route("/termsandconditions")
def Terms():

    return render_template('termsandconditions.html')


@app.route("/about")
def about():

    return render_template('aboutus.html')


if __name__ == "__main__":
    app.run(debug=True)
