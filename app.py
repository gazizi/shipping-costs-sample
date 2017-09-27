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

    #pin = '7023210361050105'
    url = 'https://stg30.soa-gw.canadapost.ca/track/json/package/{0}/info'
    request = urllib.request.Request(url.format(pin))

    #base64string = base64.encodestring('%s:%s' % ('CPO_TAP_APP', 'CPO_TAP-QA')).replace('\n', '')
    base64string = base64.encodestring(('%s:%s' % ('CPO_TAP_APP', 'CPO_TAP-QA')).encode()).decode().replace('\n', '')

    request.add_header("Authorization", "Basic %s" % base64string)

    try:
        rsp = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print ('not authorized')
            speech =  "The parcel with track number : " + pin  + " error: not authorized."
        elif e.code == 404:
            print ('not found')
            speech =  "The parcel with track number : " + pin  + " not found!, Please check your track number."
        elif e.code == 503:
            print ('service unavailable')
            speech =  "error - service unavailable."
        else:
            print ('unknown error: ')
            speech =  "unknown error."
    else:
        # everything is fine
        print ('success')
        new_t = string.replace(rsp.split("\n")[1],'<tracking-detail xmlns="http://www.canadapost.ca/ws/track">','<tracking-detail>')
        print new_t
        root  = ET.fromstring(new_t)
        output = ""
        isDelivered = False

        occurrences = root.findall('./significant-events/occurrence')
        if occurrences:
            for oc in occurrences:
                d = oc.find('event-description')
                isDelivered = (d.text == "Delivered")  #check for delivery status
                if isDelivered:
                    break

            occurrence = occurrences[0]  # gets latest status
            ev_description = occurrence.find('event-description')
            ev_date = occurrence.find('event-date')
            ev_time = occurrence.find('event-time')
            ev_site = occurrence.find('event-site')
            ev_province = occurrence.find('event-province')



        #json_data = json.load(rsp)
        #speech =  "The parcel with track number : " + pin  + " latest status is : " + json_data['status']
        speech =  "The parcel with track number : " + pin  + " latest status is : " + ev_description
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
