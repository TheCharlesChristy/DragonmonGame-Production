import os
import shutil

def del_certs():
    dir_name = r"C:\Users\Charles\Desktop\Projects\DragonmonGame"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".cer") or item.endswith(".pem"):
            os.remove(os.path.join(dir_name, item))

def createInitpems():
    from keys import CreateKeys

def copy_certs():
    dir_name = r"C:\Users\Charles\Desktop\Projects\DragonmonGame"
    test = os.listdir(dir_name)
    for item in test:
        if item == "ca-public-key.pem":
            shutil.copy(os.path.join(dir_name, item), r"C:\Users\Charles\Desktop\Projects\DragonmonGame\CA-Cert.cer")
        if item == "server-public-key.pem":
            shutil.copy(os.path.join(dir_name, item), r"C:\Users\Charles\Desktop\Projects\DragonmonGame\Server-Cert.cer")

def refresh_certs():
    del_certs()
    createInitpems()
    copy_certs()
    print("\n\nCertificates Refreshed Successfully\nPlease follow procedure to install the CA-Cert.cer file on your device.\n\n")

refresh_certs()