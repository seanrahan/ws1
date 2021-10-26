#!/usr/local/bin/python3
"""
Author: Sean Hanrahan
shanrahan@vmware.com
script will grab macOS FileVault recovery key from device with supplied UDID
usage: python3 get-recovery-key.py <UDID>
"""
# import libraries
import requests
import json
import sys
from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient



############ START CONFIGURATION SECTION ################
############ ENTER YOUR ENV INFORMATION HERE ############
# OAuth 2.0 used for Authorization - need to configure an OAuth Client in UEM and put shared secret / id here
clientId = ''
sharedSecret = ''

# OAuth Client Token URL for UEM. For SaaS, look here: https://docs.vmware.com/en/VMware-Workspace-ONE-UEM/services/UEM_ConsoleBasics/GUID-BF20C949-5065-4DCF-889D-1E0151016B5A.html
tokenUrl = 'https://uat.uemauth.vmwservices.com/connect/token'

# tenant information for reference
apiHost = 'as135.awmdm.com'
############ END CONFIGURATION SECTION ##################



# Check for appropriate number of args, exit if not
if (len(sys.argv) != 2):
    print("usage: python3 get-recovery-key.py <UDID>")
    exit(1)

# Initial Internal Variables, URLs, etc.
udid = sys.argv[1]
uuid = ''
enrolled = False
searchUrl = "https://" + apiHost + "/api/mdm/devices?searchBy=udid&id=" + udid # API to find device by UDID
headers = {
   'Accept': 'application/json;version=1',
}

### SETUP DONE ###

#initialize session to WS1 UEM, get Access token
client = BackendApplicationClient(client_id=clientId)
session = OAuth2Session(client=client)
token = session.fetch_token(token_url=tokenUrl,client_id=id,client_secret=sharedSecret)

# Logic:
# call API to map UDID to UUID
# call recovery key API for appropriate UUID

try:
    deviceReq = session.get(searchUrl, headers=headers)
    deviceReq.raise_for_status()

    # print(deviceReq.text)

    # parse json response
    device = deviceReq.json()

    # extract UUID, Print device information for reference
    uuid = device['Uuid']
    
    print("Found Device!")
    print("UUID:" + uuid)
    print("Hostname: " + device['HostName'])
    if (device['EnrollmentStatus'] == 'Unenrolled'):
        print("Device Unenrolled, Last Seen on: " + device['LastSeen'])
    else:
        print("Device Currently Enrolled, Last Seen on: " + device['LastSeen'])
        enrolled = True
    print("--------------------")

    #define recovery URL, make API call
    recoveryUrl = "https://" + apiHost + "/api/mdm/devices/" + uuid + "/security/recovery-key"
    keyReq = session.get(recoveryUrl, headers=headers)
    keyReq.raise_for_status()

    #parse json respomnse
    keys = keyReq.json()

    # report out
    print("Found Recovery Key:")
    print(keys["recovery_key"])
    if (enrolled): print("NOTE: Device is currently ENROLLED, recovery key will rotate in the next 15 minutes")

# error handling
except HTTPError as http_err:
    print(f'HTTP Error: {http_err}')
except Exception as err:
    print(f'Other error: {err}')
