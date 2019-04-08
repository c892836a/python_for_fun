import random
import os
# import time

RANDOM_RANGE = 3571
RANDOM_NUMBER = 1001
# RANDOM_FACTOR = int(str(time.time()).replace(".", ""))

def start_random():
    count = 0
    for _i in range(RANDOM_NUMBER):
        result = (random.randint(1, RANDOM_RANGE) * random.randint(1, RANDOM_RANGE)) % RANDOM_RANGE
        if result >= int(RANDOM_RANGE / 2):
            count += 1

    print(count)
    if count < (int(RANDOM_NUMBER / 2) + 1):
        print("Go to shower")
    else:
        print("Please start your show!")



if __name__ == "__main__":
    start_random()
    os.system("pause")
