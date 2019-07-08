"""
Requirement: pip3 install adafruit-circuitpython-lis3dh 
Check USB port: ls /dev/tty*
"""
import time
import fprint_lib
import serial

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
finger = fprint_lib.Fingerprint_Lib(uart)

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

def register_finger(location):
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
    else:
        if i == fprint_lib.BADLOCATION:
            print("Bad storage location")
        elif i == fprint_lib.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True

def get_num():
    #Use input() to get a valid number from 1 to 127. Retry till success!
    i = 0
    while (i > 63) or (i < 1):
        try:
            i = int(input("Enter User ID from 1-63: "))
        except ValueError:
            pass
    return i 

#######################################################################

def register_fingerprint():
    print("Input password: ")
    j = input("> ")
    if j == 'fourfang':
        if fprint.read_templates() != fprint_lib2.fprint_lib.OK:
            raise RuntimeError('Failed to read templates')
        print("Fingerprint templates occupied:", finger.templates)
        k = get_num()
        register_finger(k)
        print("Repeat again")
        time.sleep(0.5)
        register_finger(k + 63)
    else:
        raise RuntimeError('Incorrect password!')

def identify_fingerprint():
    if get_fingerprint():
        if finger.confidence >= 100:
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            raise RuntimeError('Low confidence!')
    else:
        print("Finger not found")

def delete_fingerprint():
    l = get_num()
    get_fingerprint()
    print(finger.finger_id)
    if finger.finger_id == l or finger.finger_id == (l+63):
        finger.delete_model(l)
        finger.delete_model(l + 63)
        print("Deleted!")
    else:
        print("Failed to delete")