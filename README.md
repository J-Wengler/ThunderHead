# ThunderHead
Dexcom API development for use in customizable CGM alerts and monitoring. This specific version uses flask to spin up a web app on a local host.

Usage:
1. Clone repo
2. Run the following commands in the directory 

```
python3 -m venv thunderhead
pip install -r requirements.txt
python3 main.py
```
3. Navigate to http://127.0.0.1:4999/

***Details: ThunderHead uses the weighed average of the last 3 changes in blood glucose to predict where the blood sugar is trending, you can manually change the weights in the web app to experiment with different values to see what works best for you.***

Relevant Documentation:

[Flask](https://flask.palletsprojects.com/en/2.2.x/)

[TurboFlask](https://turbo-flask.readthedocs.io/en/latest/)

[PyDexcom](https://github.com/gagebenne/pydexcom)

**Next Step: Move flask app to Google Cloud (custom domain: sugarwatch.net)**

