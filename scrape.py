# scrape
"""
Scraper
"""

#from InstagramAPI import InstagramAPI
from gram import InstagramAPI
import pandas as pd
import os
from time import sleep
import traceback
from dbman import db_append, db_dupcheck
import datetime
import dateutil
import random
import subprocess
import jgapi
import json

#flwng = jgapi.following_dump()
#print(flwng)

with open("/home/ec2-user/nyc.eats.today/sources.txt", 'r') as f:
    hardList = (f.read()).split("\n")

random.shuffle(hardList)

for flw in hardList:
    subprocess.call(["/home/ec2-user/venv/bin/python3", "/home/ec2-user/inventory/instagram-profilecrawl/crawl_profile.py", flw])
    thisJsonPath = '/home/ec2-user/inventory/instagram-profilecrawl/profiles/{}.json'.format(flw)
    with open(thisJsonPath, 'r') as json_file:
        # open the json file we just created
        data = json.load(json_file)
        if len(data["posts"]) == 0:
            print("ATTN: No post data in JSON file!!")
        for itc, imgUrl in enumerate(data["posts"]):
            try:
                imgUrl2 = imgUrl["imgs"][0]
                imgdesc = imgUrl["imgdesc"][0]
            except IndexError:
                print("No imgs found, continuing")
                continue
            """
            if os.path.isdir("/home/ec2-user/inventory/{}".format(flw)):
                print("already scraped")
                break
            """
            if "food" in imgdesc:
                print("Food photo found! Saving")
                subprocess.call(["mkdir", "/home/ec2-user/inventory/{}".format(flw)])
                subprocess.call(["wget", imgUrl2, "-P", "/home/ec2-user/inventory/{}".format(flw)])
                subprocess.call(["mv", "/home/ec2-user/inventory/{}/{}".format(flw, imgUrl2.split("/")[-1]), "/home/ec2-user/inventory/{}-{}.jpg".format(flw, itc)])
            else:
                print("Photo not of food - desc is {}".format(imgdesc))
            sleep(random.uniform(1.1, 2.2))