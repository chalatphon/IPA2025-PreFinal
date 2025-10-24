#######################################################################################
# Yourname:
# Your student ID:
# Your GitHub Repo: 

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import time
import os
import restconf_final
import netmiko_final
import ansible_final
from dotenv import load_dotenv

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
load_dotenv()
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.environ.get("WEBEX_ROOM_ID")
api = ""
command = ""
while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    clist = ["create","delete","enable","disable","status","gigabit_status","showrun"]
    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith("/66070041"):

        # extract the command
        myinput = message.split(" ")
        check = len(myinput)
        if(check == 2):
            command = myinput[1]
            if(command == "restconf"):
                api = "restconf"
                responseMessage = "Ok: Restconf"
            elif(command == "netconf"):
                api = "netconf"
                responseMessage = "Ok: Netconf"
            elif(command in clist and api == ""):
                print(api)
                responseMessage = "Error: No method specified"
            elif(command in clist and api != ""):
                print("hello")
                responseMessage = "Error: No IP specified"
            elif(command not in clist and api != ""):
                responseMessage = "Error: No command found"
            else:
                responseMessage = "God help me"
        elif(check == 3 and api == "restconf"):
            deviceip = myinput[1]
            command = myinput[2]
            if command == "create":
                responseMessage = restconf_final.create(deviceip)
            elif command == "delete":
                responseMessage = restconf_final.delete(deviceip)
            elif command == "enable":
                responseMessage = restconf_final.enable(deviceip)
            elif command == "disable":
                responseMessage = restconf_final.disable(deviceip)
            elif command == "status":
                responseMessage = restconf_final.status(deviceip)
            elif command == "gigabit_status":
                responseMessage = netmiko_final.gigabit_status(deviceip)
            elif command == "showrun":
                response = ansible_final.showrun()
                responseMessage = response["msg"]
                print(responseMessage)
            else:
                responseMessage = "Error: No command or unknown command"
        else:
            responseMessage = "Opps you did something wrong"

        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if command == "showrun" and responseMessage == 'ok':
            filename = "./backups/show_run_66070041_CSR1kv.txt"
            fileobject = open(filename, "rb")
            filetype = "text/plain"
            postData = {
                "roomId": roomIdToGetMessages,
                "text": "show running config",
                "files": ("show_run_66070041_CSR1kv.txt", fileobject, filetype),
            }
            postData = MultipartEncoder(postData)
            HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}   

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data = postData ,
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
