
#!/usr/bin/env python

import sys
import requests
import json
import csv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# import configparser
import configparser

config = configparser.ConfigParser()

configfile = 'voucherprint.cfg'

config.read(configfile)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


jar = requests.cookies.RequestsCookieJar()

s = requests.Session()

username=None
password=None
baseurl=None
site=None

def authconn():
    # Request
    # POST https://localhost:8443/api/login

    try:
        response = s.post(
            url="https://localhost:8443/api/login",
            cookies=jar,
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            verify = False,
            data=json.dumps({
                "username": username,
                "password": password
            })
        )
        if response.status_code != 200:
            print('Authentication failed')
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print('Authentication failed: ', e)


def createvoucher():
    # Create Vouchers
    # POST https://localhost:8443/api/s/default/cmd/hotspot

    count = input('How many vouchers to create? [4] ') or 4
    expire = input('How long until the vouchers expire (minutes)? [4 hours] ') or 240
    note = input('Note? ') or ''
    up = input('Bandwidth limit up: ') or 0
    down = input('Bandwidth limit down: ') or 0
    bytequota = input('Total usage limit in mb: ') or 0
    quota = input('Single use (1), Multiuse (0), or Limited Uses (# of uses): [1] ') or 1

    jparms = {}
    jparms['cmd'] = "create-voucher"
    jparms['expire'] = expire
    if note:
        jparms['note'] = note
    if up:
        jparms['up'] = up
    if down:
        jparms['down'] = down
    if bytequota:
        jparms['quota'] = bytequota

    try:
        response = s.post(
            url="https://localhost:8443/api/s/default/cmd/hotspot",
            cookies=jar,
            verify = False,
            params=jparms,
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        if response.status_code != 200:
            print('Voucher creation failed')
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print(response.text)
            sys.exit(1)
        rj = response.json()
        createtime = rj['data'][0]['create_time']
        return createtime
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def getvouchers(createtime):
    # Get Vouchers
    # POST https://localhost:8443/api/s/default/stat/voucher

    try:
        response = s.post(
            url="https://localhost:8443/api/s/default/stat/voucher",
            headers={
                # "Cookie": "unifises=TZnkv5Po9m7bSVfLNb3cWSax0mBbY36I; csrf_token=1wtP5r7HAaPaJIfmsw8IYCgUAg0MOdNF",
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "create_time": createtime
            })
        )
        if response.status_code != 200:
            print('Voucher retrieval failed')
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            sys.exit(1)
        vouchers = response.json()['data']
        return vouchers
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def csvvouchers(vouchers):
    fieldnames = list(vouchers[0].keys())
    with open('vouchers.csv', 'w') as csvfile:
        fieldnames = fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for voucher in vouchers:
            writer.writerow(voucher)

def setup():
    global username, password, baseurl, site, configfile
    try:
        if config:
            if 'Settings' in config:
                settings = config['Settings']
                username = settings['username']
    except:
        pass
    if username is None:
        username = input("What is your UniFi username? ")
        try:
            config['Settings']['username'] = username
        except:
            config['Settings'] = {}
            config['Settings']['username'] = username

    try:
        if config:
            if 'Settings' in config:
                settings = config['Settings']
                password = settings['password']
    except:
        pass
    if password is None:
        password = input("What is your UniFi password? ")

        while True:
            savep = input('Save password to file? [Y/n] ') or 'Y'
            if (savep is 'Y') or (savep is 'y') or (savep is 'n') or (savep is 'N'):
                break
        try:
            if savep is 'Y' or savep is 'y':
                config['Settings']['password'] = password
        except:
            config['Settings'] = {}
            config['Settings']['password'] = password

    try:
        if config:
            if 'Settings' in config:
                settings = config['Settings']
                baseurl = settings['baseurl']
    except:
        pass
    if baseurl is None:
        baseurl = input("What is your UniFi base url [https://localhost:8443]? ") or 'https://localhost:8443'
        try:
            config['Settings']['baseurl'] = baseurl
        except:
            config['Settings'] = {}
            config['Settings']['baseurl'] = baseurl

    try:
        if config:
            if 'Settings' in config:
                settings = config['Settings']
                site = settings['site']
    except:
        pass
    if site is None:
        site = input("What is your UniFi site [default]? ") or 'default'
        try:
            config['Settings']['site'] = site
        except:
            config['Settings'] = {}
            config['Settings']['site'] = site


    with open(configfile, 'w') as configfile:
        config.write(configfile)


def main(argv):

    setup()
    authconn()
    createtime = createvoucher()
    vouchers = getvouchers(createtime)
    csvvouchers(vouchers)
    pass

if __name__ == "__main__":
    main(sys.argv)




