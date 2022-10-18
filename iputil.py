#!/usr/bin/env python3 

import re
import shlex
import subprocess

def get_my_ip(device = "wlan0"):
    cp = subprocess.run(shlex.split(f"ip addr show dev {device}"), stdout=subprocess.PIPE)
    for line in cp.stdout.decode('utf-8').split("\n"):
        m = re.match(' +inet ([^/]+)/', line)
        if m:
            return m.group(1)
    return "unknown"
