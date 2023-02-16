# _,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,_

# ThunderHead Flask App
# Current Version: 3.0.2
# Author: Jimmy Wengler
# Last Updated: Jan 28

# _,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,_

from flask import Flask, render_template
from flask import request
from flask import redirect, url_for
from turbo_flask import Turbo
import random
from thunderhead import ThunderHead
from datetime import datetime


# This is the flask 'frontend.' It doesn't connect to the backend via API calls, but rather creates an instance of the ThunderHead class
# In all honesty, I'm a little hazy on how this works. Since we want part of the webpage to update automatically, we use the TurboFlask 
# extension to do that. I'll do my best to explain the flow, but specific details are best found in the Flask/TurboFlask documentation

# Declare Flask, TurboFlask, and Thunderhead objects
app = Flask(__name__)
thunder = ThunderHead(change = -30, low = 65, high = 250)


# The base webpage directs to a login page where the user can enter the necessary information
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        dex_username = request.form["name"]
        dex_pass = request.form["email"]
        dex_low = request.form["low"]
        dex_high = request.form["high"]
        dex_fw = request.form["fw"]
        dex_sw = request.form["sw"]
        dex_tw = request.form["tw"]
        thunder.create_dexcom(username = dex_username, password=dex_pass, low = dex_low, high = dex_high, fw = dex_fw, sw = dex_sw, tw = dex_tw)
        return redirect(url_for('index'))

    return render_template("login.html")

# After the login page button is hit, the user is directed to the main page where the information is stored
@app.route('/main')
def index():
    return_list = thunder.get_update()
    cur = return_list[0]
    pred = return_list[1]
    alr = return_list[2]
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    return render_template('index.html', cur_bg = cur, predicted_bg = pred, alert = alr, time = current_time)


# Fairly hazy on this function. From my understanding these are the specific steps that are called by turboflask when it replaces the data
# the stat variable is the status message pulled from the ThunderHead object

# Used to run script from command line
# Port 4999 instead of the more traditional 5000 because 5000 is reserved for the airplay task on macs
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4999, debug=True)