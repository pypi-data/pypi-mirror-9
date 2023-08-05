# -*- coding: utf-8 -*-
from tornado.httpclient import AsyncHTTPClient
import json
import xml.etree.ElementTree as ET


http_client = AsyncHTTPClient()
url = ''
response = ''
args = []
link = 'http://api.worldweatheronline.com/free/v2/weather.ashx?key='
api = ''
result = {}


def forecast(key, **kwargs):
    '''forecast(your_api_key, q=q, optional_arguments)
    q = US Zipcode, UK Postcode, Canada Postcode, IP, Lat/Long, city name;
    optional args https://developer.worldweatheronline.com/page/explorer-free:
    format=[json, xml, csv, tab]; extra=[localObsTime, isDayTime, utcDateTime];
    num_of_days=int; date=ISO Date; fx=[yes, no]; cc=[yes, no]; mca=[yes, no];
    fx24=[yes, no]; includelocation=[yes, no]; show_comments=[yes, no];
    tp=[3, 6, 12, 24]; showlocaltime=[yes, no];
    lang=[ar,bn,bg,zh,zh_tw,cs,nl,fi,fr,de,el,
         hi,hu,it,ja,jv,ko,zh_cmn,mr,pl,pt,pa,ro,ru,sr,si,
         sk,es,sv,ta,te,tr,uk,ur,vi,zh_wuu,zh_hsn,zh_yue,zu]
    '''
    global api
    if len(key) != 29:
        print 'invalid key'
    else:
        for i, j in kwargs.iteritems():
            args.append('&{0}={1}'.format(i, j))
        a = ''.join(set(args))
        api = link + key + a.replace(' ', '+')

        def handle_request(resp):
            global response
            if resp.error:
                print "Error:", resp.error
            else:
                response = resp.body

        http_client.fetch(api, handle_request)


def get_result():
    global result
    if response.startswith('{'):
        # the result is JSON, use wwo.result to see it
        result = json.loads(response)

    elif response.startswith('<'):
        # the result is XML, parse the wwo.result to work on the nodes
        # or, use wwo.response to see the raw result
        result = ET.fromstring(response)

    elif response.startswith('#The CSV'):
        # the result is CSV, check wwo.result to see it
        result = response

    elif response.startswith('#The TAB'):
        # the result is in TAB format
        result = response

    else:
        print 'Sorry, no valid response!'
