#!/usr/bin/env python3

from random import shuffle
import netifaces
import os
import psycopg2
import requests
import sys
import logging
import yaml

if len(sys.argv) < 2:
    print('No DNS address given.', file=sys.stderr)
    exit(1)

dns = sys.argv[1]

public = os.environ.get('PUBLIC_IP', False)

if public:

    public_ip_urls = [
        'http://icanhazip.com',
        'http://myip.dnsomatic.com/'
    ]
    shuffle(public_ip_urls)

    for url in public_ip_urls:
        try:
            ip = requests.get(url).text.rstrip()
            break
        except Exception:
            continue

else:

    prefix_list = os.environ.get("INTERFACE_PREFIX", "en,eth,wl")
    prefixes = prefix_list.split(',')

    interface = os.environ.get("INTERFACE_NAME", None)

    if not interface:
        interfaces = []

        for prefix in prefixes:
            for i in netifaces.interfaces():
                if i.startswith(prefix):
                    interfaces.append(i)
                    break

        if len(interfaces) == 0:
            print('No interface found.', file=sys.stderr)
            exit(1)

        interface = interfaces[0]

    ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']


def main():

    try:
        db_config_file = open('/etc/pg-dns-register/db.yml')
        db_config = yaml.load(db_config_file, Loader=yaml.SafeLoader)
    except (FileNotFoundError, IOError):
        logging.exception('Error reading config file.')
        sys.exit(1)
    except yaml.YAMLError:
        logging.exception('Error parsing config file.')
        sys.exit(1)

    db_conn = psycopg2.connect(**db_config)
    cur = db_conn.cursor()

    try:
        cur.execute("""
            INSERT INTO records (type, name, data, ttl)
            VALUES ('A', %s, %s, 30)
            ON CONFLICT (type, name) DO UPDATE
              SET data = excluded.data,
                  ttl = excluded.ttl;
        """, (dns, ip))
        db_conn.commit()
    except Exception:
        logging.exception('Failed to update DNS table.')
        db_conn.rollback()
