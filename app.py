from flask import Flask , jsonify , json , make_response , render_template , send_from_directory ,session ,abort ,redirect

from flask import request
import os, pymongo ,time, datetime
import pywaves as pw

app = Flask(__name__)

DB_URL = os.environ['DB_URL']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.environ['DB_NAME']
NODE_URL = os.environ['NODE_URL']
FAUCET_TIME = os.environ['FAUCET_TIME']
FAUCET_VALUE = os.environ['FAUCET_VALUE']
FLASK_ENV = os.environ['FLASK_ENV']
FLASK_RUN_PORT = os.environ['FLASK_RUN_PORT']
FLASK_RUN_HOST = os.environ['FLASK_RUN_HOST']
PVKEY = os.environ['PVKEY']
FAUCET_USDN_VALUE = os.environ['FAUCET_USDN_VALUE']
USDN_ASSET_ID= os.environ["USDN_ASSET_ID"]

pw.setNode(NODE_URL, "custom", "R")


client = pymongo.MongoClient("mongodb://"+str(DB_USERNAME)+":"+str(DB_PASSWORD)+"@"+str(DB_URL)+":"+str(DB_PORT)+"/")

db = client[DB_NAME]
users = db["users"]
ips = db["ips"]


myAddress = pw.Address(privateKey=str(PVKEY))
print("Connectetd to MY account")



@app.route('/')
def index():
    return render_template('index.html')

def send_waves(address):
    otherAddress = pw.Address(str(address))
    myAddress.sendWaves(otherAddress, int(FAUCET_VALUE)*(10**8))


def send_udsn(address):
    otherAddress = pw.Address(str(address))
    myToken = pw.Asset(str(USDN_ASSET_ID))
    myAddress.sendAsset(asset=myToken,amount=int(FAUCET_USDN_VALUE)*(10**6),recipient=otherAddress)

def checklastTime(userData):

    pastTime = time.time()-userData["lasttime"]
    if int(FAUCET_TIME) > pastTime:
        c = datetime.timedelta(seconds=int(FAUCET_TIME)-pastTime)
        minutes = divmod(c.seconds, 60)
        return False
    else:
        return True


def calculateLastTime(userData):
    pastTime = time.time()-userData["lasttime"]
    if int(FAUCET_TIME) > pastTime:
        c = datetime.timedelta(seconds=int(FAUCET_TIME)-pastTime)
        minutes = divmod(c.seconds, 60)
        return minutes



@app.route("/sendWaves",methods = ['POST'])
def sendWaves():

    address = str(request.form['address'])
    realIp=request.headers.get('X-Forwarded-For')

    if address == None or address == "":
        return "Invalid address",400
    
    if pw.validateAddress(address)==False:
        return "Invalid address",400

    userDataForAddress = users.find_one({"address":str(address),"asset":"waves"})
    userDataForIps = ips.find_one({"ip":str(realIp),"asset":"waves"})

    if userDataForAddress == None and userDataForIps ==None:
        users.insert_one({
            "address":str(address),
            "lasttime":int(time.time()),
            "asset":"waves"
        })
        ips.insert_one({
            "ip":realIp,
            "lasttime":int(time.time()),
            "asset":"waves"
            
        })

        send_waves(address)
        return "Send "+str(FAUCET_VALUE)+" token to "+str(address),200
        

    if userDataForAddress !=None and checklastTime(userDataForAddress) ==False:
        minutes=calculateLastTime(userDataForAddress)
        return "Failed, you must wait for "+str(minutes[0])+"Min "+str(minutes[1])+"Sec",400

    if userDataForIps !=None and checklastTime(userDataForIps) ==False:
        minutes=calculateLastTime(userDataForIps)
        return "Failed, you must wait for "+str(minutes[0])+"Min "+str(minutes[1])+"Sec",400
    
    if userDataForAddress==None:
        users.insert_one({
            "address":str(address),
            "lasttime":int(time.time()),
            "asset":"waves"
        })
    else:
        users.update_one({ "address": address,"asset":"waves"}, { "$set": { "lasttime": int(time.time()) }})

    if userDataForIps==None:
        ips.insert_one({
            "ip":realIp,
            "lasttime":int(time.time()),
            "asset":"waves"
        })
    else:
        ips.update_one({ "ip": realIp,"asset":"waves" }, { "$set": { "lasttime": int(time.time()) }})
  
    send_waves(address)
    return "Send "+str(FAUCET_VALUE)+" token to "+str(address),200




@app.route("/sendUsdn",methods = ['POST'])
def sendUsdn():

    address = str(request.form['address'])
    realIp=request.headers.get('X-Forwarded-For')

    if address == None or address == "":
        return "Invalid address",400
    
    if pw.validateAddress(address)==False:
        return "Invalid address",400

    userDataForAddress = users.find_one({"address":str(address),"asset":"usdn"})
    userDataForIps = ips.find_one({"ip":str(realIp),"asset":"usdn"})

    if userDataForAddress == None and userDataForIps ==None:
        users.insert_one({
            "address":str(address),
            "lasttime":int(time.time()),
            "asset":"usdn"
        })
        ips.insert_one({
            "ip":realIp,
            "lasttime":int(time.time()),
            "asset":"usdn"
            
        })

        send_udsn(address)
        return "Send "+str(FAUCET_VALUE)+" token to "+str(address),200
        

    if userDataForAddress !=None and checklastTime(userDataForAddress) ==False:
        minutes=calculateLastTime(userDataForAddress)
        return "Failed, you must wait for "+str(minutes[0])+"Min "+str(minutes[1])+"Sec",400

    if userDataForIps !=None and checklastTime(userDataForIps) ==False:
        minutes=calculateLastTime(userDataForIps)
        return "Failed, you must wait for "+str(minutes[0])+"Min "+str(minutes[1])+"Sec",400
    
    if userDataForAddress==None:
        users.insert_one({
            "address":str(address),
            "lasttime":int(time.time()),
            "asset":"usdn"
        })
    else:
        users.update_one({ "address": address,"asset":"usdn" }, { "$set": { "lasttime": int(time.time()) }})

    if userDataForIps==None:
        ips.insert_one({
            "ip":realIp,
            "lasttime":int(time.time()),
            "asset":"usdn"
        })
    else:
        ips.update_one({ "ip": realIp,"asset":"usdn" }, { "$set": { "lasttime": int(time.time()) }})
  
    
    send_udsn(address)

    return "Send "+str(FAUCET_VALUE)+" token to "+str(address),200



@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('templates/css/', path)


if __name__ == '__main__':
        app.run(debug=True,port=int(os.getenv("FLASK_RUN_PORT")),host=os.getenv("FLASK_RUN_HOST"))
