import subprocess
from threading import Timer
import time
import pexpect
import socket

# Start an interactive bash shell


password = "passwordPlaceholder"
email = "webmaster@voltagehosting.net"
ip = "192.168.1.25"
key = "keyPlaceholder"

domainsList = []
textCodeList = []

# Function to read output with a timeout ## In all honesty chatgpt wrote this function lol, but its for debug only.... mostly
# def read_output(timeout,proc):
#     output_lines = []
#     timer = Timer(timeout, proc.kill)
#     try:
#         timer.start()
#         for line in proc.stdout:
#             output_lines.append(line.strip())
#     finally:
#         timer.cancel()
#     return output_lines

# Now you can interact with the shell
# while True:
#     command = input("$ ")
#     process.stdin.write(command + '\n') #command plus enter key
#     process.stdin.flush()
#     output = read_output(timeout=1)  # Set timeout to 1 second
#     # Print the output
#     print('\n'.join(output))

def findLine(tx):
    la = []
    for l in range(len(tx.splitlines())):
        for i in tx.splitlines()[l]:
            if i == ":":
                la.append(l)
    return(la)

def addDomain(dom):
    fi = open("domains.txt","a")
    fi.write(","+dom)
    fi.close()

def deleteAll():
    global domainsList, textCodeList, email, password, key
    for i in range(len(domainsList)):
        pexpect.run(f'curl -X POST https://mail.voltagehosting.net/admin/dns/custom/{domainsList[i]}/txt -H "Content-Type: text/plain" --data-raw "{textCodeList[i]}" -H "Authorization: Basic {key}"')

def sendRecord(do,tv):
    global email, password, key
    pexpect.run(f'curl -X POST https://mail.voltagehosting.net/admin/dns/custom/{do}/txt -H "Content-Type: text/plain" --data-raw "{tv}" -H "Authorization: Basic {key}"')

def renewDomains():
    global password, domainsList, textCodeList
    print("Starting")
    doms = open("domains.txt","r")
    domsList = doms.read().split(",")
    addString = ""
    domainTotal = 0
    for i in domsList:
        addString+=f"-d {i} "
    renewString = "sudo certbot certonly --manual --preferred-challenges dns "+addString
    #print(renewString)
    process = pexpect.spawn(renewString, timeout=4)
    while True:
        index = process.expect([pexpect.TIMEOUT, "password for it:", pexpect.EOF])
        if index == 1:
            process.sendline(password)
        else:
            break
    time.sleep(1)
    while True:
        index = process.expect([pexpect.TIMEOUT, r"\(E\)xpand/\(C\)ancel:", pexpect.EOF])
        if index == 1:
            process.sendline("E")
        else:
            break
    print("Registering Names")
    while True:
        index = process.expect([pexpect.TIMEOUT, "Press Enter to Continue", pexpect.EOF])
        if index == 1:
            if domainTotal == 0:
                domain = process.before.decode().splitlines()[6].replace(".voltagehosting.net.",".voltagehosting.net")
                textCode = process.before.decode().splitlines()[10]
            else:
                domain = process.before.decode().splitlines()[5].replace(".voltagehosting.net.",".voltagehosting.net")
                textCode = process.before.decode().splitlines()[9]
            domainsList.append(domain)
            textCodeList.append(textCode)
            sendRecord(domain,textCode)
            domainTotal += 1
            print("Do "+domain,"Tx "+textCode)
            time.sleep(5)
            process.sendline("")
        else:
            break
    # print(process.before.decode())
    hostN = socket.gethostname()
    hostNEW = hostN.split(".")
    deleteAll()
    pexpect.run("sudo systemctl restart nginx")
    ### TODO ANOTHER TIME ###pexpect.run(f'echo "Hello Web Admins, {hostNEW} has just had its certificate renewed for the following domains:\n{doms.read().replace(",",", ")}\nThe next renewal will take place in 2 months, a month from the expiry date. Thanks!" | mail -s "{hostNEW} Cert Renewal" {email}')
    #process.expect(pexpect.EOF)
    #print(process.after.decode())
    # process.stdin.write(password+"\n")
    # process.stdin.flush()
    # print(read_output(1,process))
    #process.terminate()

renewDomains()



#print(findLine("Hi\nThis: is\n a: test of\n Lines!"))
