from flask import Flask, render_template, redirect, url_for, json, request, Response
import random, subprocess
import datetime
import KristenCode

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def main():
    return render_template('login.html')

@app.route('/showSignUp', methods=['POST','GET'])
def showSignUp():
    return render_template('signup.html')

@app.route('/showDashboardAfterSubmission', methods=['POST','GET'])
def showDashboardAfterSubmission():
    #unimportant
    fname = request.form["fname"]
    lname = request.form["lname"]  
    email = request.form["email"]
    password = request.form["pass"]
    cpass = request.form["cpass"]
    gender = request.form["gender"]  
    preference = request.form["preference"]

    #used for query
    age = request.form["age-amount"]
    size = request.form["size"]
    loyalty = request.form["loyalty"]
    attention = request.form["attention"]
    money = request.form["money"]
    kids = request.form["kids"]
    privacy = request.form["privacy"]

    matches = KristenCode.getMatches(preference, age, size, loyalty, attention, money, kids, privacy)
    print(json.dumps(matches))
    return json.dumps(matches)

@app.route('/showDashboard', defaults = {'matches':[]}, methods=['POST','GET'])
@app.route('/showDashboard/<matches>', methods=['POST','GET'])
def showDashboard(matches):
    if matches:
        print("matches " + str(matches))
        data  = json.loads(matches)
        print(data)
        return render_template('dashboard.html', result=data)
    else:
        print("yuh")
        return render_template('dashboard.html', result=[])

if __name__ == '__main__':
    app.run()
