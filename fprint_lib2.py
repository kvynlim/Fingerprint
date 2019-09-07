"""
Requirement: pip3 install adafruit-circuitpython-lis3dh 
Check USB port: ls /dev/tty*
"""
import time
import fprint_lib
import serial
import csv
import pandas as pd
import time

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
finger = fprint_lib.Fingerprint_Lib(uart)
df = pd.read_csv('finger_file.csv', index_col='Names')
username_col = df.iloc[:,0]
template_1_col = df.iloc[:,1]
template_2_col = df.iloc[:,2]
attempt = 0

print(df)

def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != fprint_lib.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != fprint_lib.OK:
        return False
    print("Searching...")
    if finger.finger_fast_search() != fprint_lib.OK:
        return False
    return True

def register_finger(location, username, mode):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
        else:
            print("Place same finger again...", end="", flush=True)

        while True:
            i = finger.get_image()
            if i == fprint_lib.OK:
                print("Image taken")
                break
            elif i == fprint_lib.NOFINGER:
                print(".", end="", flush=True)
            elif i == fprint_lib.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == fprint_lib.OK:
            print("Templated")
        else:
            if i == fprint_lib.IMAGEMESS:
                print("Image too messy")
            elif i == fprint_lib.FEATUREFAIL:
                print("Could not identify features")
            elif i == fprint_lib.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != fprint_lib.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == fprint_lib.OK:
        print("Created")
    else:
        if i == fprint_lib.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="", flush=True)
    i = finger.store_model(location)
    if i == fprint_lib.OK:
        print("Stored")
        #WRITE_NAME@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if mode == 1:
            with open ('finger_file.csv', mode='a') as append_file:
                new_user = [username, username, location, location + 63]
                append = csv.writer(append_file)
                append.writerow(new_user)
                attempt = 1
        else:
            pass
    else:
        if i == fprint_lib.BADLOCATION:
            print("Bad storage location")
        elif i == fprint_lib.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True

def register_get_num():
    i = 1
    j = 0
    k = len(template_1_col)
    while i <= k:
        if i == template_1_col[j]:
            i +=1
            j +=1
        else:
            break
    print("Your USER ID: ", i)
    return i

def delete_get_num():
    #Use input() to get a valid number from 1 to 63. Retry till success!
    i = 0
    while (i > 63) or (i < 1):
        try:
            i = int(input("Enter User ID from 1-63: "))
        except ValueError:
            pass
    return i 

def read_name(username):
    i = 0
    while template_1_col[i] != username:
        i +=1
    print(f'Welcome {username_col[i]}')
        
def delete_name(username):
    i = 0
    while template_1_col[i] != username:
        i +=1
    df.drop([username_col[i]], axis=0, inplace=True)
    df.to_csv('finger_file.csv')

#######################################################################

def register_fingerprint():
    i = 0
    password = input("Input password: ")
    if password == 'ff':
        if finger.read_templates() != fprint_lib.OK:
            raise RuntimeError('Failed to read templates')
        print("Fingerprint templates occupied:", finger.templates)
        template_id = register_get_num()
        username = input("Input your name: ")
        register_finger(template_id, username, 1)
        print("Repeat again")
        time.sleep(0.5)
        if attempt == 1:
            register_finger(template_id + 63, username, 0)
        else:
            pass
    else:
        print("Wrong password!")

def identify_fingerprint():
    if get_fingerprint():
        if finger.confidence >= 100:
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
            if finger.finger_id > 63:
                read_name(finger.finger_id - 63)
            else:
                read_name(finger.finger_id)
        else:
            print('Low confidence!')
    else:
        print("Finger not found")

def delete_fingerprint():
    i = delete_get_num()
    get_fingerprint()
    print(finger.finger_id)
    if finger.finger_id == i:
        delete_name(i)
        finger.delete_model(i)
        finger.delete_model(i + 63)
        print("Deleted!")
    else:
        print("Failed to delete")

def force_delete_fingerprint():
    i = delete_get_num()
    #delete_name(i)
    finger.delete_model(i)
    #finger.delete_model(i + 63)
