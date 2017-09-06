#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/trackingwebhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "parcel.tracking":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    track = parameters.get("track-number")

    destinations = {'12':'deliverd', '23':'In transition', '34':'In depot', '45':'At Toronto Airport', '56':'At Ottawa'}

    speech = "The parcel with track number : " + track + " latest status is : " + destinations[track]

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % (port))

    app.run(debug=True, port=port, host='0.0.0.0')
