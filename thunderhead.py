# _,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,_

# ThunderHead Backend
# Current Version: 3.0.2
# Author: Jimmy Wengler
# Last Updated: Jan 28

# _,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'-.,_

from pydexcom import Dexcom
import time
import http.client, urllib
from datetime import datetime

# This is the actual 'algorithm' part of the app. It's not a true backend as it doesn't accept API calls
# The flask 'frontend' creates an instance of this class to provide the necessary visual information
# Flask interacts with this class in two ways.
#   1. Initiates the class then calls create_dexcom() with the necessary information
#   2. Calls get_update() to get information to display to the user. The order that the functions get called are get_update() -> calc_slopes() -> check()
# TODO: Instead of providing preformatted text, return [HIGH, LOW, STABLE] and predicted glucose value at 5, 10, 15mins 

# FIXME: REMOVE TURBOFLASK AND MAKE IT SO THE USER JUST REFRESHES THE PAGE EVERY 5 MINUTES TO GET THE NEW TREND. THEN WE CAN MOVE TO JAVASCRIPT

class ThunderHead: 

    # change = the threshold for change between concurrent blood glucose levels that you want to prompt an alert
    # low = the low threshold below which you want to be alerted
    # high = the high threshold above which you want to be alerted
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

    # Uses the pydexcom package to create a new dexcom object and store it as a member of the class
    # Some variables are cast to numeric values becase the flask form provides text as the default type
    # TODO: Change flask form to automatically provide numeric data to reduce casting
    def create_dexcom(self, username, password, low, high, fw, sw, tw):
        new_dexcom = Dexcom(username, password)
        self.dexcom = new_dexcom
        self.bgvs = []
        self.low = int(low)
        self.high = int(high)
        self.fw = float(fw)
        self.sw = float(sw)
        self.tw = float(tw)

    # Checks to see if a dexcom object has been created in the class
    # RETURN: bool 
    def check_dexcom(self):
        if self.dexcom is None:
            return False
        else:
            return True

    # Provides the update text that flask displays on the web page
    # Flask calls this function every 5 minutes
    # RETURN: text to be displayed by frontend
    def get_update(self):
        if self.dexcom == None:
            return ["NA", "NA", "NO DEXCOM OBJECT"]
        bgvs = self.dexcom.get_glucose_readings(minutes=60, max_count= 4)
        try:
            temp = self.dexcom.get_current_glucose_reading()
            if temp == None:
                return ["NA", "NA", "DEXCOM COULD NOT FIND A CURRENT BLOOD GLUCOSE"]
        except:
            return["NA", "NA", "DEXCOM COULD NOT FIND A CURRENT BLOOD GLUCOSE"]

        # FIXME: USE ABOVE DATA TO MAKE TREND AUTOMATICALLY SO NO UPDATE
        if len(bgvs) < 4:
            cur = self.dexcom.get_current_glucose_reading()
            if cur == None:
                return ["NA", "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]
            else: 
                return [cur.value, "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]
        else:
            can_check = True
            for bg in bgvs:
                if bg == None:
                    can_check = False

            if can_check:
                #self.print_bgvs(bgvs)
                data_1 = bgvs[3].value
                data_2 = bgvs[2].value
                data_3 = bgvs[1].value
                data_4 = bgvs[0].value

                first_slope = data_2 - data_1
                second_slope = data_3 - data_2 
                third_slope = data_4 - data_3
                average_slope = (first_slope * self.fw) + (second_slope * self.sw) + (third_slope * self.tw)
                cur_bg = data_4
                # FIXME: change function below to return list of things for html
                return self.check(cur_bg, average_slope)
            else:
                cur = self.dexcom.get_current_glucose_reading()
                if cur == None:
                    return ["NA", "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]
                else: 
                    return [cur.value, "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]

        # Get the current blood sugar
        bg = self.dexcom.get_current_glucose_reading()

        # Check if sensor is reading, -99 means no blood sugar value is available
        if bg is None:
            bg = -99
        else:
            bg = bg.value

        # Append the new glucose value
        self.bgvs.append(bg)

        # Once current glucose has been added, we can run the predictive algorithm and get the appropiate status message
        message = self.calc_slopes()

        # Appends the current time to the end of the status message. Useful for ensuring the frontend is updating every 5 mins
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        time_message = f"{message}\nLast Updated: {current_time}"

        # Return completed message
        return time_message

    
    # This functions takes a current blood sugar and slope (calculated in calc_slopes()) and predicts what the blood sugar will be in 15 mins
    # Based off the prediction the function returns a STABLE, LOW, or HIGH message with the appropiate information
    # RETURN: Text with information to be displayed by frontend
    def check(self, current_bg, slope):
        predicted_bg = current_bg + (slope * 3)
        #past_bg = self.bgvs[len(self.bgvs) - 2]
        if predicted_bg <= self.low:
            message = f"LOW PREDICTED - Average Fall: {slope}"
            return [current_bg, predicted_bg, message]
            #self.send_message(message=message, title= "LOW PREDICTED")
        elif predicted_bg >= self.high:
            message = f"Status: HIGH PREDICTED - Average Rise: {slope}"
            return [current_bg, predicted_bg, message]
            #self.send_message(message=message, title= "HIGH PREDICTED")
        else:
            message = f"Status: Stable blood sugar\nCurrent Glucose: {current_bg}\nPredicted to be stable({self.low}-{self.high})"
            return [current_bg, predicted_bg, ""]


    # Uses the 4 previous data points to generate a prediction of what the blood sugar will be at in 15 mins
    # RETURN text message to be displayed by frontend
    def calc_slopes(self):
        # Check how many glucose values we have. If less than 4 return error message
        bg_len = len(self.bgvs)
        if bg_len < 4:
            message = "Status: ALGORITHM ERROR\nInsufficient data to run algorithm"
            return message

        # Calculate the 3 changes in blood glucose values over the last 4 data points
        # Uses check() to predict blood sugar and check if alert is warranted
        else:
            data_1 = self.bgvs[bg_len - 4]
            data_2 = self.bgvs[bg_len - 3]
            data_3 = self.bgvs[bg_len - 2]
            data_4 = self.bgvs[bg_len - 1]
            
            # If one of the past 4 data points is -99 then we don't have the necessary data to run algorithm
            # Return error message
            if data_1 == -99 or data_2 == -99 or data_3 == -99 or data_4 == -99:
                message = f"Status: ALGORITHM ERROR\nCould not run predictive algorithm. One of these values ({data_1}, {data_2}, {data_3}, {data_4}) was -99"
                return message

            # Calculate the 3 slopes then find their weighted average, pass the weighted average and current blood sugar to check() to craft final message
            else:
                first_slope = data_2 - data_1
                second_slope = data_3 - data_2 
                third_slope = data_4 - data_3
                average_slope = (first_slope * self.fw) + (second_slope * self.sw) + (third_slope * self.tw)
                cur_bg = data_4
                message = self.check(cur_bg, average_slope)
                # Return message
                return message
