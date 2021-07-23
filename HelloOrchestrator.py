#!/usr/bin/python
#*******************************************************************************
#
# Name:         HelloOrchestrator
#
# Description:  Simple application to use REST API calls to the Orchestrator
#
# Inputs:       None

# Outputs:      1. Return Value (of a REST GET request)
#               2. Response Code
#               3. JSON Object
#               4. JSON Object for use with Python
#               5. The "hostname" value
#
# Notes:        This is an example script. It is provided WITHOUT any warranty.
#               Use at your own risk.
#
# Suggestions:  Here are some things you could add...
#               - Test the Response Code to verify the GET/POST worked
#
#********************************************************************************

import sys, time, json
from OrchMiniHelp import OrchMiniHelper 

class Main:
    def __init__(self, argv):
        self.orchIP = "dazn-orch-euc1.silverpeak.cloud"
        self.url = "dazn-orch-euc1.silverpeak.cloud"
        self.orchUser = ""
        self.orchPassword = ""
        
    def run(self):
        # Create an object
        orch = OrchMiniHelper(self.orchIP, self.orchUser, self.orchPassword)
        
        # Login, get the "briefInfo", then logout
        orch.login()
        response = orch.get("/gmsserver/briefInfo")  #Note: Alternatively use "/gmsserver/info"
        appliances = orch.get("/appliance")
        
        orch.logout()

        # Display the "response" object in various formats
        #print("1. The return value:    {0}".format(response))             
        #print("2. Response Code:       {0}".format(response.status_code)) 
        #print("3. JSON object:\n{0}".format(response.text))
        #print("1. BriefInfo:\n{0}".format(response.json()))
        #print("5. The \"hostname\":      {0}".format(response.json()["hostname"]))

        print('Appliances')
        print('----------')
        for EC in appliances.json():
            print(EC['hostName'])
            print(EC['platform'])
            print(EC['serial'])
            print(EC['ip'],end = '\n\n')

        
        
if __name__ == "__main__":
    main_obj = Main(sys.argv[1:])
    main_obj.run()
