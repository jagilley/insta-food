import jgapi
from time import sleep
import random

if __name__=="__main__":
    sleep(random.uniform(5.0, 40.0))
    for i in range(20):
        jgapi.follow_someone()
    sleep(7)
    jgapi.unfollow_someone(datedelta=5)
    sleep(random.uniform(5.0, 20.0))
    rndint = random.randrange(0,77)
    if rndint == 7:
        jgapi.post_something()
