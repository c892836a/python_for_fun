import random
import os

random_range = 999
random_number = 1001


def start_random():
    count = 0
    for _i in range(random_number):
        if random.randint(0, random_range) > int(random_range / 2):
            count += 1

    print(count)
    if count < (random_number / 2) + 1:
        print("Go to shower")
    else:
        print("Please start your show!")



if __name__ == "__main__":
    start_random()
    os.system("pause")
