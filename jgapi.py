# jgapi
"""
An API wrapper for our use cases for the Instagram API
"""

#from InstagramAPI import InstagramAPI
from gram import InstagramAPI
import pandas as pd
import traceback
from dbman import db_append, db_dupcheck
import datetime
import os
import dateutil
import subprocess
from time import sleep
import random

with open("creds.txt", 'r') as f:
    creds = f.read()

api = InstagramAPI("nyc.eats.today", creds)
api.login()
our_user_id = api.username_id

def jg_followers():
    """
    Return info about who's following us
    """
    global api, our_user_id
    followers = api.getTotalFollowers(our_user_id)
    print('Number of followers:', len(followers))
    return followers

def following_dump(dump=False):
    """
    Collect info about who we're following, and dump it to a file (namely, data/following.csv)
    """
    global api, our_user_id
    following = []
    next_max_id = True
    while next_max_id:
        if next_max_id is True:
            next_max_id = ''
        _ = api.getUserFollowings(our_user_id, maxid=next_max_id)
        following.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
    #print(len(following))
    followingDF = pd.DataFrame(following)
    if dump:
        followingDF.to_csv("~/dump/following.csv", index=False)
    return followingDF["username"].tolist()

def getFollowCandidates(uid, dump=True):
    """
    Given the UID of a user whose followers we'd like to poach, return/dump info about their followers
    """
    global api, our_user_id
    """
    followingDF = pd.read_csv("~/dump/following.csv")
    followingUsernames = followingDF["username"].tolist()
    followingIDs = followingDF["pk"].tolist()
    """
    fl = api.getTotalFollowers(uid)
    if dump:
        pd.DataFrame(fl).to_csv("~/dump/{}.csv".format(uid), index=False)
    return pd.DataFrame(fl)

def jg_follow(uid):
    global api, our_user_id
    df = pd.DataFrame({"uid": [uid], "followed-at": [datetime.datetime.now()]})
    db_append("followed.csv", df)
    return api.follow(uid)

def jg_unfollow(uid):
    global api, our_user_id
    df = pd.DataFrame({"uid": [uid], "followed-at": [datetime.datetime.now()]})
    return api.unfollow(uid)

def follow_someone():
    """
    follow someone at random
    """
    candidates = pd.read_csv("~/dump/candidate_db.csv")
    # note: int wrapper is important because Pandas uses int64 datatype, which is incompatible with JSON
    jg_follow(int(candidates.at[random.randint(0, len(candidates.index.values)), "pk"]))

def unfollow_someone(datedelta=7):
    global api
    """
    Look at the csv of people we've followed, and if any were followed more than a week ago, unfollow them
    """
    followed = pd.read_csv("~/dump/followed.csv")
    followed["followed-at"] = followed["followed-at"].apply(dateutil.parser.parse)
    unfollow_eligible = followed[(datetime.datetime.now() - followed["followed-at"]) > datetime.timedelta(datedelta)]
    unfollow_eligible = unfollow_eligible.reset_index(drop=True)
    print("unfollow eligible is:")
    print(unfollow_eligible)
    if len(unfollow_eligible.index.values) > 0:
        randomIndex = random.randint(0, len(unfollow_eligible.index.values))
        myGuy = unfollow_eligible.at[randomIndex, "uid"]
        for unfol_user in unfollow_eligible["uid"].tolist()[:50]:
            print("unfollowing", unfol_user)
            api.unfollow(int(unfol_user))
            sleep(8)
        followed.loc[followed["uid"] == myGuy, "followed-at"] = (datetime.datetime.today() + datetime.timedelta(36500))
        print(followed.loc[followed["uid"] == myGuy])
        followed.to_csv("~/dump/followed.csv", index=False)
        db_dupcheck("followed.csv", targetCols=["uid"], overwrite=True)
    else:
        print("Nobody old enough to unfollow")

def post_something(blank=False):
    global api
    with open("/home/ec2-user/nyc.eats.today/stockquotes.txt", 'r') as f:
        stockquotes = (f.read()).split("\n")
    with open("/home/ec2-user/nyc.eats.today/hashtags.txt", 'r') as f:
        hashtags = (f.read()).split("\n")

    thisCaption = random.choice(stockquotes) + "\n.\n.\n." + random.choice(hashtags)
    
    inventoryDir = "/home/ec2-user/inventory"
    listOfPhotos = []
    for file in os.listdir(inventoryDir):
        if file.endswith(".jpg"):
            mypath = os.path.join(inventoryDir, file)
            listOfPhotos.append(mypath)
            print(mypath)
    myPhoto = random.choice(listOfPhotos)
    print("posting", myPhoto)
    myCap = random.choice(stockquotes) + "\n\n...Credit to @{}".format(str(myPhoto).split('-')[0])
    if not blank:
        api.uploadPhoto(myPhoto, caption=myCap)
        subprocess.call(["rm", myPhoto])

if __name__=="__main__":
    print("You've ran the file! It's a better idea to call an exposed method from another file.")
    """
    uids = ["702254", "8480313014"]
    for i in uids:
        db_append("candidate_db.csv", getFollowCandidates(i, dump=False))
    """
