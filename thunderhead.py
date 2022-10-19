from hashlib import new
from pydexcom import Dexcom
import sqlite3
import pandas as pd
import time
import http.client, urllib

class ThunderHead: 
    # username = dexcom username
    # password = dexcom password
    # change = the threshold for change between concurrent blood glucose levels that you want to prompt an alert
    # low = the low threshold below which you want to be alerted
    def __init__(self, username: str, password: str, change, low):
        self.username = username
        self.password = password
        self.conn = None
        self.dexcom = None
        self.bgvs = []
        self.change = change
        self.low = low
        # Create new dexcom object
        self.create_dexcom()

    # Uses the pydexcom package to create a new dexcom object
    def create_dexcom(self):
        new_dexcom = Dexcom(self.username, self.password)
        self.dexcom = new_dexcom
        #self.set_up_database()

    # Uses the current dexcom object to get the current blood glucose
    def get_current_blood_sugar(self):
        bg = self.dexcom.get_current_glucose_reading()
        print(bg.value)

    # Uses the Pushover API to send a message
    def send_message(self, message = "DEFAULT MESSAGE"):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": "a7hxahk94ajn8tyt5y13wnq4dwia1t",
            "user": "u39yretpf7kpu775jm8djwey42t8jh",
            "message": f"{message}",
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

    # Gets a blood sugar reading every 5 minutes and checks to see if an alert is warranted
    def watch(self):
        print("Starting watch...")
        # reset stored blood glucose levels 
        self.bgvs = []
        # get the initial blood sugar reading
        initial_bg = self.dexcom.get_current_glucose_reading().value
        # add the initial value to stored values
        self.bgvs.append(initial_bg)
        # wait 5 minutes
        time.sleep(300)
        while True:
            # get next blood glucose
            next_bg = self.dexcom.get_current_glucose_reading().value
            # add next blood glucose to stored values
            self.bgvs.append(next_bg)
            # check if an alert is warranted
            self.send_update()
            # wait 5 minutes
            time.sleep(300)

    # checks if a change or low warrants an alert
    def check(self, bg, change):
        if bg <= self.low:
            return True
        if change <= self.change:
            return True
        return False
            
    # gets the current bg and old blood glucose to calculate change in order to potentially send an alert
    def send_update(self):
        bg_len = len(self.bgvs)
        # current bg
        new_bg = self.bgvs[bg_len - 1]
        # old bg
        old_bg = self.bgvs[bg_len - 2]
        # Sets sign="+" if the change is positive and "-" if negative
        # if sign="#" then something has happened that I did not anticipate
        sign = "#"
        if new_bg >= old_bg:
            sign = "+"
        else:
            sign = "-"
        change = abs(new_bg - old_bg)
        # checks to see if the change or current bg warrant an alert
        # the else statement is just to debug so you get an alert everytime regardless
        if self.check(new_bg, change):
            message = f"Current Glucose : {new_bg}\nChange : {sign}{change}"
            self.send_message(message)
        else:
            message = f" DEBUG (NOT AN ALERT)\nCurrent Glucose : {new_bg}\nChange : {sign}{change}"
            self.send_message(message)
        


    # Not working yet
    # Potential plan is to create a database to get a summary notification each day
    # Talk to mom about how best to set up the database
    def set_up_database(self):
        #FIXME
        conn = sqlite3.connect('dexcom_database') 
        self.conn = conn
        c = self.conn.cursor()
        #FIXME
        # The below command needs to be changed to create the proper database
        c.execute('''
          CREATE TABLE IF NOT EXISTS dexcom
          ([product_id] INTEGER PRIMARY KEY, [product_name] TEXT)
          ''')
        #c.execute(''' DROP TABLE bgv''')
        