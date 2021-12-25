import os
import json
import requests
import pandas as pd

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

MAX_ITER = 100
targets = {'dns': 'https://dns.taa.computer', 'anycast': 'https://anycast.taa.computer', 'traditional': 'https://us.taa.computer'}
files  = ['sl-min-original-nostaic.js']

columns = [
    "time_namelookup", "time_connect", "time_appconnect",
    "time_pretransfer", "time_redirect", "time_total"
]

def process(filename, _method, testedfile, server_location):
    df = pd.read_csv(filename, names=columns)
    df['location'] = os.getenv('location')
    df['provider'] = os.getenv('provider')
    df['method'] = _method
    df['filename'] = testedfile
    df['server_location'] = server_location.strip()
    return df

def send_data(df,method,filename):
    requests.post(url=f"http://meme.peem.in/capstone/store-json/{os.getenv('provider')}_{os.getenv('location')}_{method}_{filename}",data=df.to_json())
    print("Request Sent!")

def experiment(_method, filename): 
    out_name = _method + '_' + filename.replace('.', '-') + '.csv'
    url = targets[_method] + '/' + filename
    for i in range(MAX_ITER):
        os.system('curl '+ url + r' -H "Cache-Control: no-cache, no-store, must-revalidate" '+
            r'-H "Pragma: no-cache" -H "Expires: 0" -w "@curl-format.txt" ' +
            r'-o /dev/null -s >> ' + out_name
        )
    server_location = requests.get(targets[_method] + '/' + 'location.txt')
    result = process(out_name, _method, filename, server_location.text)
    send_data(result,_method,filename)

for target in targets.keys(): 
        print("location:", os.getenv('location'))
        print("provider:", os.getenv('provider'))
        for fname in files:
            print("location:", os.getenv('location'))
            print("provider:", os.getenv('provider'))
            print(target,fname)
            experiment(target, fname)
