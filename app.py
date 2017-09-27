#!/usr/bin/env python

import urllib
import urllib.request
import base64
import json
import os
from http import HTTPStatus
from flask import Flask
from flask import request
from flask import make_response
# this is new 
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
    pin = parameters.get("track-number")

    url = 'https://soa-gw.canadapost.ca/vis/track/pin/MJ107326680CA/detail'
    request = urllib.request.Request(url) # .format(pin))
    print('URL = ' + url)
    base64string = base64.encodestring(('%s:%s' % ('ee36457569d0beab', '60cd45fc6b41020bd66e2d')).encode()).decode().replace('\n', '')

    request.add_header("Authorization", "Basic %s" % base64string)

    try:
        rsp = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print ('--------->>not authorized')
            speech = "status : not authorized"
        elif e.code == 404:
            print('--------->>not found')
            speech = "status : not found"
        elif e.code == 503:
            print('--------->>service unavailable')
            speech = "status : service unavailable"
        else:
            print('--------->>Unknown error')
            speech = "status : Unknown"
    else:
        print('Succedd')
        print ('---------------------------------')
        data = rsp.read().decode('utf-8')
        root = ET.fromstring(data)
        # hack removes the namespace since ElementTree cannot process it cleanly
        new_data = data.replace('<tracking-detail xmlns="http://www.canadapost.ca/ws/track">','<tracking-detail>')

        print ('new_data: ' + new_data)
        root  = ET.fromstring(new_data)
        output = ""
        isDelivered = False

        occurrences = root.findall('./significant-events/occurrence')
        if occurrences:
            for oc in occurrences:
                d = oc.find('event-description')
                isDelivered = (d.text == "Delivered")  #check for delivery status
                print ( 'isDelivered: %r' , isDelivered)
                if isDelivered:
                    break

            occurrence = occurrences[0]  # gets latest status
            ev_description = occurrence.find('event-description')
            print (ev_description.text)
            ev_date = occurrence.find('event-date')
            ev_time = occurrence.find('event-time')
            ev_site = occurrence.find('event-site')
            ev_province = occurrence.find('event-province')



    speech = "status : " + ev_description.text

    print ( 'Response :')
    print(speech)
    return speech


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
