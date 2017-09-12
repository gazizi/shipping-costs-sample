#!/usr/bin/env python

import urllib
import urllib.request
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

    res = makeURLResult(req) #  makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

    return r

def makeURLResult(req):
    if req.get("result").get("action") != "parcel.tracking":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    track = parameters.get("track-number")

    pin = '7023210361050105'

    request = urllib.Request("https://stg30.soa-gw.canadapost.ca/track/json/package/{0}/info".format(pin))

    base64string = base64.encodestring('%s:%s' % ('CPO_TAP_APP', 'CPO_TAP-QA')).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    rsp = urllib.urlopen(request)

    json_data = json.load(rsp)



    destinations = {'12':'deliverd', '23':'In transition', '34':'In depot', '45':'At Toronto Airport', '56':'At Ottawa'}

    speech =  json_data # "The parcel with track number : " + track + " latest status is : " + destinations[track]

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }

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
