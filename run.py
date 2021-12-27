import os
import time
import requests
import pandas as pd
import datetime

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

MAX_ITER = 2
# targets = {'dns': 'https://dns.taa.computer'}
targets = {'dns': 'https://dns.taa.computer', 'anycast': 'https://anycast.taa.computer', 'traditional': 'https://us.taa.computer', 'elastic': 'https://elastic.snaplogic.com/sl/js/designer/sl-min.js'}
# targets = {'budgy': 'https://budgy.elastic.snaplogicdev.com/sl/js/designer/sl-min.js','elastic': 'https://elastic.snaplogic.com/sl/js/designer/sl-min.js','uat': 'https://uat.elastic.snaplogic.com/sl/js/designer/sl-min.js''https://uat.elastic.snaplogic.com/sl/js/designer/sl-min.js'}
files  = ['sl-min-original-nostaic.js','sl-min-original.js']

columns = [
    "time_namelookup", "time_connect", "time_appconnect",
    "time_pretransfer", "time_redirect", "time_total"
]

def process(filename, _method, filename_list, server_location_list, datetime_list, backoff_list):
    export_filename = '/home/azureuser/' + filename
    df = pd.read_csv(filename, names=columns)
    df['location'] = os.getenv('location')
    df['provider'] = os.getenv('provider')
    df['method'] = _method
    df['filename'] = filename_list
    df['server_location'] = server_location_list
    df['datetime'] = datetime_list
    df['backoff'] = backoff_list
    df.to_csv(export_filename,index=False)
    return df

def send_data(df,method,filename):
    requests.post(url=f"http://meme.peem.in/capstone/store-json/{os.getenv('provider')}_{os.getenv('location')}_{method}_{filename}",data=df.to_json())
    print("Request Sent!")

def experiment(_method, filename, datetime_list, server_location_list): 
    out_name = _method + '_' + filename.replace('.', '-') + '.csv'
    if _method != 'elastic': url = targets[_method] + '/' + filename
    os.system('curl '+ url + r' -H "Cache-Control: no-cache, no-store, must-revalidate" '+
        r'-H "Pragma: no-cache" -H "Expires: 0" -w "@curl-format.txt" ' +
        r'-o /dev/null -s >> ' + out_name
    )
    datetime_list[_method][filename].append(datetime.datetime.now())
    if _method != 'elastic': server_location_list[_method][filename].append(requests.get(targets[_method] + '/' + 'location.txt').text.strip())

backoff_list = ['1.1 secs' for i in range(MAX_ITER)]
filename_list = {'sl-min-original-nostaic.js': ['sl-min-original-nostaic.js' for i in range(MAX_ITER)], 'sl-min-original.js': ['sl-min-original.js' for i in range(MAX_ITER)] }
datetime_list = {'dns':{'sl-min-original-nostaic.js': [],'sl-min-original.js': []}, 'anycast':{'sl-min-original-nostaic.js': [],'sl-min-original.js': []},'traditional':{'sl-min-original-nostaic.js': [],'sl-min-original.js': []},'elastic':[]}
server_location_list  = {'dns':{'sl-min-original-nostaic.js': [],'sl-min-original.js': []}, 'anycast':{'sl-min-original-nostaic.js': [],'sl-min-original.js': []},'traditional':{'sl-min-original-nostaic.js': [],'sl-min-original.js': []},'elastic':['oregon' for i in range(MAX_ITER)]}
for i in range(MAX_ITER):
        for key in targets.keys():
            for filename in files:
                experiment(key, filename, datetime_list, server_location_list)
                print(f'[{i}] {key} {filename}')
        print(f" [{i}] Backing off from keep alive ... ")
        time.sleep(1.1)

for key in targets.keys():
    for file in files:
        if key == 'elastic' & file == 'sl-min-original.js': continue
        filename = key + '_' + file.replace('.', '-') + '.csv'
        result = process(filename, key, filename_list[file], server_location_list[key][file], datetime_list[key][file], backoff_list)
        print(result)
        # send_data(result,key,filename)