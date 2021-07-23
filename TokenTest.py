#
# TokenTest.py - basic Orchestrator helper class that includes functions to facilitate 
#                login, logout, and issue REST GET/POST/DELETE/PUT calls over a session
# 
# Your use of this Software is for training purposes only. There is NO warantee of any kind.
# 
# Last update: April 2021
# 

import requests

class OrchHelper:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.url_prefix = "https://" + url + "/gms/rest"
        self.session = requests.Session()
        self.headers = {}
        self.apiSrcId = "?source=menu_rest_apis_id"  #for API calls w/ just source as query param
        self.apiSrcId2 = "&source=menu_rest_apis_id" #for API calls w/ multiple query params
        self.supportedAuthModes = ["local","radius","tacacs"] #remote authentication modes supported via this helper module
        self.authMode = "local"   # change this to the desired auth mode before invoking login() function.
        requests.packages.urllib3.disable_warnings() #disable certificate warning messages 

    def login (self):
        # basic login function without multi-factor authentication
        # NOTE: if the userId is using RBAC, they must have R/O or R/W access to the REST API functionality to access the APIs
        # Returns True if login succeeds, False if exception raised or failure to login

        if self.authMode not in self.supportedAuthModes:
            print("{0}: authentication mode not supported".format(self.authMode))
            return False
        
        try:
            response = self.post("/authentication/login",
                                 {"user": self.user, "password": self.password, "loginType": self.supportedAuthModes.index(self.authMode)})
            if response.status_code == 200:
                print ("{0}: Orchestrator login success".format(self.url))
                # get and set X-XSRF-TOKEN
                # This allows scripts to work when the "Enforce CSRF Token Check" is checked on Orchestrator 8.10 and after.
                # It saves the token from the cookie.
                for cookie in response.cookies:
                    if cookie.name == "orchCsrfToken":
                        self.headers["X-XSRF-TOKEN"] = cookie.value
                return True
            else:
                print ("{0}: Orchestrator login failed: {1}".format(self.url, response.text))
                return False
        except:
            print("{0}: Exception - unable to connect to Orchestrator".format(self.ipaddress))
            return False

    def mfa_login (self, mfacode):
        # alternative login function for multi-factor authentication
        # mfacode is integer value that is provided by Orchestrator after providing initial userid and passwd
        # To use mfa_login, first request the mfacode using send_mfa(). An MFA code will be sent depending on how the user is configured.
        # Then call this function with the provided MFA code.
        #
        # NOTE: if the userId is using RBAC, they must have R/O or R/W access to the REST API functionality to access the APIs
        # Returns True if login succeeds, False if exception raised or failure to login
        
        try:
            response = self.post("/authentication/login", {"user": self.user, "password": self.password, "token": int(mfacode)})
            if response.status_code == 200:
                print ("{0}: Orchestrator MFA login success".format(self.url))
                # get and set X-XSRF-TOKEN
                for cookie in response.cookies:
                    if cookie.name == "orchCsrfToken":
                        self.headers["X-XSRF-TOKEN"] = cookie.value
                return True
            else:
                print ("{0}: Orchestrator MFA login failed: {1}".format(self.url, response.text))
                return False
        except:
            print("{0}: Exception - unable to connect to Orchestrator".format(self.ipaddress))
            return False
             
    def send_mfa(self):
        # send request to Orchestrator to issue MFA token to user
        # returns True on success, False on failure or exception
        try:
            response = self.post("/authentication/loginToken",{"user": self.user, "password": self.password, "TempCode": True})
        except:
            print("Exception - unable to submit token request")
            return False
        return True if response.status_code in [200,204] else False
        
    def logout(self):
        try:
            r = self.get("/authentication/logout")
            if r.status_code == 200:
                print ("{0}: Orchestrator logout success".format(self.url))
            else:
                print ("{0}: Orchestrator logout failed: {1}".format(self.url, r.text))
        except:
            print("{0}: Exception - unable to logout of Orchestrator".format(self.ipaddress))

    # These post, get, delete, and put commands supply the CSRF Token (in the headers) for each API call.
    def post(self, url, data):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.post(self.url_prefix + url + apiSrcStr, json=data, verify=False, timeout=120, headers=self.headers)

    def get(self, url):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.get(self.url_prefix + url + apiSrcStr, verify=False, timeout=120, headers=self.headers)

    def delete(self, url):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.delete(self.url_prefix + url + apiSrcStr, verify=False, timeout=120, headers=self.headers)

    def put(self, url, data):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.put(self.url_prefix + url + apiSrcStr, json=data, verify=False, timeout=120, headers=self.headers)

    # Here are functions used by this test program. 
    
    def get_appliances(self):
        # sample GET operation to retrieve list of appliances from the Orchestrator
        # JSON response is a list object
        r = self.get("/appliance")
        if r.status_code == 200:
            return r.json()
        else:
            print ("{0}: unable to get appliance list: {1}".format(self.url, r.text))
            return []

    def get_discovered(self):
        # Get the list of discovered appliances from the Orchestrator
        # JSON response is a list object
        r = self.get("/appliance/discovered")
        if r.status_code == 200:
            return r.json()
        else:
            print ("{0}: unable to get appliance list: {1}".format(self.url, r.text))
            return []

    def get_subnets(self,nePK):
        # Get the list subnets for a specific appliance
        r = self.get("/appliance/rest/{0}/subnets3/configured".format(nePK))
        if r.status_code == 200:
            return r.json()
        else:
            print ("{0}: unable to get subnets list: from {1}  error: {2}".format(self.url, nePK, r.text))
            return []

# sample test code - only applies if this module is run as main
# This tests:
#   - Instantiation of an OrchHelper class
#   - Basic login capability, using local authentication
#   - Retrieval of a list of managed appliances
#   - Retrieval of Discoverd appliances
#   - Retrieval of a list of subnets from a specific appliance
#   - Logout operation
#
# This code can be left in here when importing this class into other modules

if __name__ == "__main__":
    url = "192.168.1.22"
    user = "admin"
    pwd = "Speak-123"
	
    o = OrchHelper(url, user, pwd)

    o.authMode = "local"  #not required as local is the default
    o.login()
    
    # for MFA login:
    #    o.send_mfa()
    #    mfa = input("Enter MFA code: ")
    #    o.mfa_login(mfa)
    
    appliances = o.get_appliances()
    print("\nTotal appliances: ",len(appliances), "\n")
    
    discovered = o.get_discovered()
    for ec in discovered:
	    print("Discovered:{0}\r\r\r\r\r".format(ec))
		
    sub_list = o.get_subnets("0.NE")
    print("Subnets: ", sub_list, "\n")
    
    o.logout()
    