from hashlib import new
from pydexcom import Dexcom
import sqlite3
import pandas as pd
import time
import http.client, urllib
import flask
from flask import render_template
from datetime import datetime

FIRSTWEIGHT = .25
SECONDWEIGHT = .25
THIRDWEIGHT = .50

class ThunderHead: 
    # username = dexcom username
    # password = dexcom password
    # change = the threshold for change between concurrent blood glucose levels that you want to prompt an alert
    # low = the low threshold below which you want to be alerted
    def __init__(self, change, low, high):
        self.conn = None
        self.dexcom = None
        self.bgvs = []
        self.slopes = []
        self.change = change
        self.low = low
        self.high = high
        self.time_passed = 0
        self.fw = .25
        self.sw = .25
        self.tw = .50
        # Create new dexcom object
        #self.create_dexcom()

    # Uses the pydexcom package to create a new dexcom object
    def create_dexcom(self, username, password, low, high, fw, sw, tw):
        new_dexcom = Dexcom(username, password)
        self.dexcom = new_dexcom
        self.bgvs = []
        self.low = int(low)
        self.high = int(high)
        self.fw = float(fw)
        self.sw = float(sw)
        self.tw = float(tw)

    def check_dexcom(self):
        if self.dexcom is None:
            return False
        else:
            return True

    def get_update(self):
        bg = self.dexcom.get_current_glucose_reading()
        if bg is None:
            bg = -99
        else:
            bg = bg.value

        self.bgvs.append(bg)
        message = self.calc_slopes()
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        time_message = f"{message}\nLast Updated: {current_time}"
        return time_message
        




    # Uses the current dexcom object to get the current blood glucose
    def get_current_blood_sugar(self):
        bg = self.dexcom.get_current_glucose_reading()
        print(bg.value)

    # Uses the Pushover API to send a message
    def send_message(self, message = "DEFAULT MESSAGE", title = "Test"):
        print(message)
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": "a7hxahk94ajn8tyt5y13wnq4dwia1t",
            "user": "u39yretpf7kpu775jm8djwey42t8jh",
            "title": title,
            "message": f"{message}",
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

    # Gets a blood sugar reading every 5 minutes and checks to see if an alert is warranted
    def watch(self):
        
        self.send_message(message = "Starting (test) watch...", title = "ThunderHead Test")
        # reset stored blood glucose levels 
        self.bgvs = []
        # get the initial blood sugar reading
        initial_bg = self.dexcom.get_current_glucose_reading()
        if initial_bg is None:
            self.send_message("No Blood Glucose Value")
            self.bgvs.append(-99)
        else:
            initial_bg = initial_bg.value
            self.bgvs.append(initial_bg)
        # add the initial value to stored values
        ##self.bgvs.append(initial_bg)
        # wait 5 minutes
        time.sleep(300)
        while True:
            # get next blood glucose
            next_bg = self.dexcom.get_current_glucose_reading()
            if next_bg is None:
                self.send_message("No Blood Glucose Value")
                self.bgvs.append(-99)
                #self.calc_slopes()
                #time.sleep(300)
            else:
                next_bg = next_bg.value
                self.bgvs.append(next_bg)
                self.calc_slopes()
            # add next blood glucose to stored values
            ##self.bgvs.append(next_bg)
            #print(next_bg)
            # check if an alert is warranted
            ##self.send_update()
            # wait 5 minutes
            time.sleep(300)

    # checks if a change or low warrants an alert
    # this is where the heart of the dynamic monitoring will occur
    # I need to whiteboard the situations in which I want the alerts to happen
    # the goal is to have code that can monitor blood sugar and dynamically alter it's threshold 
    # def check(self, bg, change):
    #     if bg <= self.low or change <= self.change:
    #         return True
    #     if change > -10 and change < 0:
    #         estimated_change = change * 3
    #         estimated_bg = bg + estimated_change
    #         if estimated_bg <= self.low:
    #             return True
    #         else:
    #             return False 
    #     if change < -10:
    #         estimated_change = change * 4
    #         estimated_bg = bg + estimated_change
    #         if estimated_bg <= self.low:
    #             return True
    #         else:
    #             return False
    #     return False
            
    # def make_message(self):
    #     bg_len = len(self.bgvs)
    #     slope_len = len(self.slopes)
    #     cur_slope = self.slopes[slope_len - 1]
    #     old_slope = self.slopes[slope_len - 2]
    #     # new bg
    #     cur_bg = self.bgvs[bg_len - 1]
    #     # old bg
    #     old_bg = self.bgvs[bg_len - 2]
    #     estimated_bg = cur_bg + cur_slope
    #     old_estimation = old_bg + old_slope
    #     change_in_slope = cur_slope - old_slope
    #     message = f"Blood Glucose: {cur_bg} (estimated to be {estimated_bg} in 5 minutes)\nCurrent Change: {cur_slope} \n Slope Trend: {change_in_slope} \n Current sugar ({cur_bg}) was estimated to be {old_estimation}"
    #     return message
        
    def check(self, current_bg, slope):
        predicted_bg = current_bg + (slope * 3)
        past_bg = self.bgvs[len(self.bgvs) - 2]
        if predicted_bg <= self.low:
            message = f"Status: LOW PREDICTED\nCurrent Glucose: {current_bg} \nPredicted Glucose (15mins): {predicted_bg}\nAverage Drop: {slope}\nPrevious Glucose Value: {past_bg}"
            return message
            #self.send_message(message=message, title= "LOW PREDICTED")
        elif predicted_bg >= self.high:
            message = f"Status: HIGH PREDICTED\nCurrent Glucose: {current_bg} \nPredicted Glucose (15mins): {predicted_bg}\nAverage Drop: {slope}\nPrevious Glucose Value: {past_bg}"
            return message
            #self.send_message(message=message, title= "HIGH PREDICTED")
        else:
            # FIXME: add default message
            message = f"Status: Stable blood sugar\nCurrent Glucose: {current_bg}\nPredicted to be stable({self.low}-{self.high})"
            return message


    # gets the current bg and old blood glucose to calculate change in order to potentially send an alert
    def calc_slopes(self):
        bg_len = len(self.bgvs)
        if bg_len < 4:
            message = "Status: ALGORITHM ERROR\nInsufficient data to run algorithm"
            return message
            #self.send_message("Insufficient data to run algorithm", title = "ALGORITHM ERROR")
        else:
            data_1 = self.bgvs[bg_len - 4]
            data_2 = self.bgvs[bg_len - 3]
            data_3 = self.bgvs[bg_len - 2]
            data_4 = self.bgvs[bg_len - 1]
            if data_1 == -99 or data_2 == -99 or data_3 == -99 or data_4 == -99:
                message = f"Status: ALGORITHM ERROR\nCould not run predictive algorithm. One of these values ({data_1}, {data_2}, {data_3}, {data_4}) was -99"
                return message
                #self.send_message(message = message, title = "ALGORITHM ERROR")
            else:
                first_slope = data_2 - data_1
                second_slope = data_3 - data_2 
                third_slope = data_4 - data_3
                average_slope = (first_slope * self.fw) + (second_slope * self.sw) + (third_slope * self.tw)
                cur_bg = data_4
                message = self.check(cur_bg, average_slope)
                return message

# Example bgvs = 120 (1), 115 (2), 117(3), 105(4)
        
        
# TODO
# Add -99 as bgv when no value is read
# Handle above when checking 