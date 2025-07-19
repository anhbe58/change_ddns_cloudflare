import requests, time, json, configparser, logging, datetime
import smtplib
import os
from mail import send_email


script_path = os.path.dirname(os.path.abspath(__file__))
config_file = "cfauth.ini"
log_file = "ipchanges.log"
config_path = os.path.join(script_path, config_file)
log_path = os.path.join(script_path, log_file)

# Reading the keys from the cfauth.ini file
config = configparser.ConfigParser()
config.read(config_path)

zone_id = config.get('tokens', 'zone_id')
bearer_token = config.get('tokens', 'bearer_token')
record_id = config.get('tokens', 'record_id')

current_set_ip = None

# Get the time of the IP change
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Setting up the logger (a file where it records all IP changes)
logging.basicConfig(level=logging.INFO, filename=log_path, format='%(levelname)s :: %(message)s')

# The headers we want to use
headers = {
    "Authorization": f"Bearer {bearer_token}", 
    "content-type": "application/json"
    }

# Getting the initial data of your A Record
a_record = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}", headers=headers)

if a_record.status_code == 200:
    arecordjson = a_record.json()
    # This is the current IP that your chosen A record has been set to on Cloudflare
    current_set_ip = arecordjson['result']['content']   
else:
    logging.error("{} An exception occurred when getting A_Record {}".format(now, a_record.status_code))

# This gets your current live external IP (whether that is the same as the A record or not)
currentip = requests.get("https://api.ipify.org?format=json")

# Status code should be 200, otherwise the API is probably down (this can happen quite a bit)
ipcheck_status = currentip.status_code

# Handling any API errors (otherwise we'd be trying to change the IP to some random HTML)

currentactualip = currentip.json()['ip']

# This loop checks your live IP every 5 minutes to make sure that it's the same one as set in your DNS record
if (current_set_ip is not None) and (currentactualip != current_set_ip):
    # If your live IP is NOT the same as the A Record's IP
    # The "Payload" is what we want to change in the DNS record JSON (in this case, it's our IP)
    payload = {"content": currentactualip}

    # Change the IP using a PATCH request
    request_st = requests.patch(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}", headers=headers, data=json.dumps(payload))

    if request_st.status_code == 200:
        # LOG THE CHANGE
        logging.info(f"{now} - IP change from {current_set_ip} to {currentactualip}")
        send_email(currentactualip)
else:
    send_email(currentactualip)
    pass

