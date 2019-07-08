import fprint_lib2

while True:
    print("------Menu-------")
    print("i) register fingerprint")
    print("o) identify fingerprint")
    print("p) delete fingerprint")
    print("----------------")
    q = input("> ")

    if q == 'i':
        fprint_lib2.register_fingerprint()
    if q == 'o':
        fprint_lib2.identify_fingerprint()
    if q == 'p':
        fprint_lib2.delete_fingerprint()