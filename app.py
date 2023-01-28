import random
import re
import sys
from flask import Flask, render_template
from flask import request
from flask import redirect, url_for
from turbo_flask import Turbo
import threading
import time
from thunderhead import ThunderHead

app = Flask(__name__)
turbo = Turbo(app)
thunder = ThunderHead(change = -30, low = 65, high = 250)


def update_load():
    with app.app_context():
        while True:
            time.sleep(300)
            turbo.push(turbo.replace(render_template('loadavg.html'), 'load'))


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()

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

@app.route('/main')
def index():
    return render_template('index.html')

@app.context_processor
def inject_load():
    if thunder.check_dexcom() == False:
        stat = "No dexcom object available"
    else:
        stat = thunder.get_update()
    
    return {'stat': stat}