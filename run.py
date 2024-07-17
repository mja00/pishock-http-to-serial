import os
from flask import Flask, request, jsonify
from pishock import SerialAPI
import time

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "CHANGEME")

# All we need is a shocker ID for the serial api
SHOCKER_ID = int(os.environ.get('SHOCKER_ID', 13117))
SHOCK_API = SerialAPI(port=None)

# At startup send a beep to the shocker
start_shocker = SHOCK_API.shocker(SHOCKER_ID)
#start_shocker.beep(1)


@app.route("/api/apioperate", methods=['POST'])
def index():
    # Get the body
    body = request.get_json()
    # We only care about Op, Duration, and Intensity
    op = int(body.get('Op', 2))
    duration = float(body.get('Duration', 1))
    intensity = int(body.get('Intensity', 1))
    # If we have all the required fields
    if op and duration and intensity:
        # Send the command to the serial API
        try:
            shocker = SHOCK_API.shocker(SHOCKER_ID)
        except TimeoutError:
            # Wait a second and try again
            time.sleep(0.25)
            try:
                shocker = SHOCK_API.shocker(SHOCKER_ID)
            except TimeoutError:
                return 'Timeout Error, check the connection.'
        # Switch on op
        if op == 0:
            # Shock
            print(f'Sending shock at {intensity}% for {duration} seconds')
            shocker.shock(duration=duration, intensity=intensity)
        elif op == 1:
            # Vibrate
            print(f'Sending vibrate at {intensity}% for {duration} seconds')
            shocker.vibrate(duration=duration, intensity=intensity)
        elif op == 2:
            # Beep
            print(f'Sending beep for {duration} seconds')
            shocker.beep(duration=duration)
        else:
            # Unknown
            print(f'Unknown operation {op}')
            return 'Unknown Op, use 0 for shock, 1 for vibrate and 2 for beep.'
        return 'Operation Succeeded.'
    else:
        return 'Missing required fields, Op, Duration, and Intensity.'


if __name__ == '__main__':
    app.run(debug=True)