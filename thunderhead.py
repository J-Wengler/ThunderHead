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



class ThunderHead: 

    # change = the threshold for change between concurrent blood glucose levels that you want to prompt an alert
    # low = the low threshold below which you want to be alerted
    # high = the high threshold above which you want to be alerted
    # 
    def __init__(self, change, low, high):
        self.conn = None
        self.dexcom = None
        self.change = change
        self.low = low
        self.high = high
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

    # Provides the update text that flask displays on the web page
    # Flask calls this function every 5 minutes
    # RETURN: text to be displayed by frontend
    def get_update(self):
        # Check if the dexcom object has been initiliazed
        if self.dexcom == None:
            return ["NA", "NA", "NO DEXCOM OBJECT"]
        
        bgvs = self.dexcom.get_glucose_readings(minutes=60, max_count= 4)
        # Try to pull the current blood glucose, if you can't or it's null then return the 'Missing' string
        try:
            temp = self.dexcom.get_current_glucose_reading()
            if temp == None:
                return ["NA", "NA", "DEXCOM COULD NOT FIND A CURRENT BLOOD GLUCOSE"]
        except:
            return["NA", "NA", "DEXCOM COULD NOT FIND A CURRENT BLOOD GLUCOSE"]

        # Check if you have the necessary data to make a prediction
        if len(bgvs) < 4:
            cur = self.dexcom.get_current_glucose_reading()

            # If you have a current bg then return it with the error message. If not, return NA as the current bg with the error message
            if cur == None:
                return ["NA", "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]
            else: 
                return [cur.value, "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]
        else:
            # Check to make sure that each value exists
            can_check = True
            for bg in bgvs:
                if bg == None:
                    can_check = False
            
            # Calculate the sloesp and pass to the check function.
            if can_check:
                data_1 = bgvs[3].value
                data_2 = bgvs[2].value
                data_3 = bgvs[1].value
                data_4 = bgvs[0].value

                first_slope = data_2 - data_1
                second_slope = data_3 - data_2 
                third_slope = data_4 - data_3
                # Calculate the weighted average of the three slopes
                average_slope = (first_slope * self.fw) + (second_slope * self.sw) + (third_slope * self.tw)
                cur_bg = data_4
                # FIXME: change function below to return list of things for html
                return self.check(cur_bg, average_slope)
            else:
                # Check again to make sure we can return the right bg
                cur = self.dexcom.get_current_glucose_reading()
                if cur == None:
                    return ["NA", "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]
                else: 
                    return [cur.value, "NA", "DEXCOM DID NOT RETURN CONTINOUS DATA FOR THE LAST 20 MINUTES"]


    
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
