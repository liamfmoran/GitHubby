from flask import Flask, render_template, json, request, Response
import random, subprocess
import datetime

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def main():
    return render_template('login.html')

@app.route('/showSignUp', methods=['POST','GET'])
def showSignUp():
    return render_template('signup.html')

@app.route('/showDashboard', methods=['POST','GET'])
def showDashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
	app.run()
