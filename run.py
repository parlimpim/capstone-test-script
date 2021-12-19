#! python3 
import os
import time
import pandas as pd
import json
import requests
import numpy

# Brief info found at
# https://netbeez.net/blog/http-transaction-timing-breakdown-with-curl/
#
# lookup: The time, in seconds, it took from the start until the name resolving was completed.
# connect: The time, in seconds, it took from the start until the TCP connect to the remote host (or proxy) was completed.
# appconnect: The time, in seconds, it took from the start until the SSL/SSH/etc connect/handshake to the remote host was completed. (Added in 7.19.0)
# pretransfer: The time, in seconds, it took from the start until the file transfer was just about to begin. This includes all pre-transfer commands and negotiations that are specific to the particular protocol(s) involved.
# redirect: The time, in seconds, it took for all redirection steps include name lookup, connect, pretransfer and transfer before the final transaction was started. time_redirect shows the complete execution time for multiple redirections. (Added in 7.12.3)
# starttransfer: The time, in seconds, it took from the start until the first byte was just about to be transferred. This includes time_pretransfer and also the time the server needed to calculate the result.
# total: The total time, in seconds, that the full operation lasted. The time will be displayed with millisecond resolution.

MAX_ITER = 10

URLS = {
    'gzip-static': 'https://us.taa.computer/sl-min-original.js',
    'prod': 'https://elastic.snaplogic.com/sl/js/designer/sl-min.js',
    'uat': 'https://uat.elastic.snaplogic.com/sl/js/designer/sl-min.js', 
    'gzip-nostatic': 'https://us.taa.computer/sl-min-original-nostaic.js',
    'no-gzip': 'https://us2.taa.computer/sl-min-original.js',
}

columns = [
    "time_namelookup", "time_connect", "time_appconnect",
    "time_pretransfer", "time_redirect", "time_total",
    "size_download", "remote_ip"
]

def process(filename, _method):
    df = pd.read_csv(filename, names=columns)
    df['location'] = os.getenv('location')
    df['provider'] = os.getenv('provider')
    df['method'] = _method
    return df

def send_data(df,method):
    requests.post(url=f"http://meme.peem.in/capstone/store-json/{os.getenv('provider')}_{os.getenv('location')}_{method}",data=df.to_json())
    print(method)
    print("Request Sent!")

def experiment(_method, url): 
    out_name = 'curl_' + _method + '.csv'
    try:
        os.system('curl --no-keepalive '+ url + r' -H "Cache-Control: no-cache, no-store, must-revalidate" '+
            r'-H "Accept-Encoding: gzip,deflate" -H "Keep-Alive: timeout=0, max=1" -H "Connection: close" '
            r'-H "Pragma: no-cache" -H "Expires: 0" -w "@curl-format.txt" ' +
            r'-o /dev/null -s >> ' + out_name
        )
    except KeyboardInterrupt: 
        exit(1)

try: 
    print("provider: {} location: {}".format(os.getenv('provider'),os.getenv('location')))
    for i in range(MAX_ITER):
        for key, target in URLS.items():
            experiment(key, target)
            print(f'[{i}] {key}')
        print(f" [{i}] Backing off from keep alive ... ")
        time.sleep(300)

    for file in URLS.keys():
        filename = 'curl_' + file + '.csv'
        result = process(filename, file)
        send_data(result,file)
except KeyboardInterrupt: 
    exit(0)

