# dbman
"""
A collection of helper funcs to manage the db system
"""

import pandas as pd

def db_append(targetFile, newDF):
    """
    Append new data to an existing csv database file
    """
    assert type(newDF) == pd.DataFrame
    try:
        df = pd.read_csv("~/dump/{}".format(targetFile))
    except FileNotFoundError:
        print("no previous df found, initializing blank one")
        df = pd.DataFrame()
    df = df.append(newDF, sort=False, ignore_index=True)
    if True in df.duplicated():
        # this may not be terribly effective! no subset, as there is in dupcheck
        print("Alert: there are duplicate values in here!")
    df.to_csv("~/dump/{}".format(targetFile), index=False)

def db_dupcheck(targetFile, targetCols=["username"], overwrite=False):
    df = pd.read_csv("~/dump/{}".format(targetFile))
    theList = df.duplicated(subset=targetCols)
    print(theList)
    print("Columns of the df are", df.columns)
    if True in theList.tolist():
        print("There ARE duplicates in this db")
        if overwrite:
            # if we've selected the overwrite option, overwrite the OG file with a deduped version
            nonDups = [True if j == False else False for j in theList.tolist()]
            (df[nonDups]).to_csv("~/dump/{}".format(targetFile), index=False)
        return True
    else:
        print("There are NO duplicates in this db")
        return False

def db_clean(targetFile):
    """
    cleans a db from unused index columns that accumulate from .to_csv writes with index
    """
    df = pd.read_csv("~/dump/{}".format(targetFile))
    cols = [c for c in df.columns if "Unnamed" not in c]
    df = df[cols]
    df.to_csv("~/dump/{}".format(targetFile), index=False)