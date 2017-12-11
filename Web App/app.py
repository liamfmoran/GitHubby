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
    data_json = request.json
    radio_entries = data_json['radio_entries']
    form_inputs = data_json['form']


    fname = ""
    lname = "" 
    age = ""

    for input in form_inputs:
        if input['name'] == "fname":
            fname = input['value']
        elif input['name'] == "lname":
            lname = input['value']
        elif input['name'] == "age-amount":
            age = input['value']

    gender = radio_entries[0][1]  
    preference = radio_entries[1][1]
    size = radio_entries[2][1]
    loyalty = radio_entries[3][1]
    attention = radio_entries[4][1]
    money = radio_entries[5][1]
    kids = radio_entries[6][1]
    privacy = radio_entries[7][1]

    data = {
        "name": fname,
        "matches": []
    }
    data["matches"] = KristenCode.getMatches(preference, age, size, loyalty, attention, money, kids, privacy)
    return json.dumps(data)

@app.route('/showDashboard', defaults = {'matches':[]}, methods=['POST','GET'])
@app.route('/showDashboard/<matches>', methods=['POST','GET'])
def showDashboard(matches):
    if matches:
        print("matches " + str(matches))
        data  = json.loads(matches)
        print(data)
        return render_template('dashboard.html', result=data)
    else:
        return render_template('dashboard.html', result=[])

if __name__ == '__main__':
    app.run()
