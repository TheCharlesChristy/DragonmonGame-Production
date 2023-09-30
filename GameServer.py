from flask import Flask, render_template, request, jsonify, json, redirect, Response, url_for
import json
import eventlet
from flask_assets import Bundle, Environment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from datetime import datetime
import GenerateToken
import random
import hashlib
import encryptionfunctions as pki
from flask_socketio import SocketIO, emit, send, disconnect
import ssl
import ast
import math

app = Flask(__name__)
#Create Flask server app
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'charleschristy325@gmail.com'
app.config['MAIL_PASSWORD'] = 'uwtuymqvfuzfkzke'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config["MAIL_DEFAULT_SENDER"] = 'charleschristy325@gmail.com'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
mail = Mail(app)
#Config db type and tell flask to not keep track of db updates
db = SQLAlchemy()
db.init_app(app)
#inititialize database

js = Bundle("Classes.js", "index.js", "Bag.js", "Team.js", output="main.js")
assets = Environment(app)
assets.register("main_js", js)
#Bundle together pieces of game javascript code and designate it as main.js

SysToken = {}
activepasswordreset = {}
Token_username = {}
Sys_pid = {}
LiveMoves = {}
LiveTeamexists = {}
f = open("static/Mapdata.txt", "r")
filedata = f.read()
mapdata = ast.literal_eval(filedata)
f.close()

socketio = SocketIO(app, cors_allowed_origins=["https://localhost:1111"], engineio_logger=True, logger=True)
#initialize socketio and allow cross origin requests from localhost:1111 and enable logs

class User(db.Model):
    username = db.Column(db.String(), primary_key=True)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String(), nullable=False)
    AuthedIp = db.Column(db.String(50))


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

#define database table User that contains user username, email, password


class Friends(db.Model):
    pkey = db.Column(db.Integer, primary_key = True)
    initiator = db.Column(db.String(30), db.ForeignKey(User.username))
    recipient = db.Column(db.String(30), db.ForeignKey(User.username))
    accepted = db.Column(db.Integer(), nullable = False)

    def __init__(self, initiator, recipient, accepted):
        self.initiator = initiator
        self.recipient = recipient
        self.accepted = accepted
    
    def __repr__(self):
        return '<Friends %r>' % self.initiator


class Player(db.Model):
    username = db.Column(db.String(30), db.ForeignKey(User.username))
    playerid = db.Column(db.String(150), primary_key = True)
    xpostion = db.Column(db.Integer())
    yposition = db.Column(db.Integer())
    currentmap = db.Column(db.Integer())
    Sockid = db.Column(db.String())
    BeatenNPCs = db.Column(db.String())
    wins = db.Column(db.Integer())

    def __init__(self, username, playerid, xpos, ypos, currentmap, wins):
        self.username = username
        self.playerid = playerid
        self.xpostion = xpos
        self.yposition = ypos
        self.currentmap = currentmap
        self.wins = wins


    def __repr__(self):
        return '<Player %r>' % self.username

class Characters(db.Model):
    characterid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), nullable = False)
    Hp = db.Column(db.Integer(), nullable = False)
    Attack = db.Column(db.Integer(), nullable = False)
    Defense = db.Column(db.Integer(), nullable = False)
    def __init__(self, name, Hp, Attack, Defense):
        self.name =  name
        self.Hp = Hp
        self.Attack = Attack
        self.Defense = Defense
    
    def __repr__(self):
        return '<characterid %r>' % self.characterid

class PlayerCharacter(db.Model):
    pkey = db.Column(db.Integer(), primary_key = True)
    playerid = db.Column(db.String(150), db.ForeignKey(Player.playerid), nullable = False)
    characterid  = db.Column(db.Integer(), db.ForeignKey(Characters.characterid),nullable = False)
    modifiers = db.Column(db.String(), nullable = False)
    active = db.Column(db.String(10), nullable = False)
    def __init__(self, playerid, characterid, modifiers, Active):
        self.playerid = playerid
        self.characterid = characterid
        self.modifiers = modifiers
        self.active = Active
    
    def __repr__(self):
        return '<PlayerCharacter %r>' % self.pkey
    
class NPC(db.Model):
    npcid = db.Column(db.Integer(), primary_key = True)
    map = db.Column(db.String())
    xpos = db.Column(db.Integer())
    ypos = db.Column(db.Integer())
    looking = db.Column(db.String())
    def __init__(self, map, xpos, ypos, looking):
        self.map = map
        self.xpos = xpos
        self.ypos = ypos
        self.looking = looking

    def __repr__(self):
        return '<NPC %r>' % self.npcid
    
class NPCTeam(db.Model):
    pkey = db.Column(db.Integer(), primary_key = True)
    npcid = db.Column(db.Integer(), db.ForeignKey(NPC.npcid))
    characterid  = db.Column(db.Integer(), db.ForeignKey(Characters.characterid), nullable = False)
    level = db.Column(db.Integer(), nullable = False)
    def __init__(self, npcid, characterid, level):
        self.npcid = npcid
        self.characterid = characterid
        self.level = level
    def __repr__(self):
        return '<NPCchar %r>' % self.npcid


class P2PMessages(db.Model):
    Timeofsent = db.Column(db.String(), primary_key = True)
    sender = db.Column(db.String(), db.ForeignKey(Player.username))
    recipient = db.Column(db.String(), db.ForeignKey(Player.username))
    message = db.Column(db.String(), nullable = False)
    def __init__(self, Timeofsent, sender, recipient, message):
        self.Timeofsent = Timeofsent
        self.sender =  sender
        self.recipient = recipient
        self.message = message
    
    def __repr__(self):
        return '<Timeofsent %r>' % self.Timeofsent

class GroupNames(db.Model):
    Groupid = db.Column(db.String(), primary_key = True)
    Groupname = db.Column(db.String(), nullable = False)
    def __init__(self, Groupid, Groupname):
        self.Groupid = Groupid
        self.Groupname = Groupname

    def __repr__(self):
        return '<Groupid %r>' % self.Groupid

class PlayerGroups(db.Model):
    pkey = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), db.ForeignKey(Player.username))
    Groupid = db.Column(db.String(), db.ForeignKey(GroupNames.Groupid))
    def __init__(self, username, Groupid):
        self.username =  username
        self.Groupid = Groupid
    
    def __repr__(self):
        return '<pkey %r>' % self.pkey
    
class GroupMessages(db.Model):
    Timeofsent = db.Column(db.String(), primary_key = True)
    Groupid = db.Column(db.String(), db.ForeignKey(GroupNames.Groupid))
    message = db.Column(db.String(), nullable = False)
    def __init__(self, Timeofsent, Groupid, message):
        self.Timeofsent = Timeofsent
        self.Groupid =  Groupid
        self.message = message
    
    def __repr__(self):
        return '<Timeofsent %r>' % self.Timeofsent
    
class PlayerItems(db.Model):
    pkey = db.Column(db.Integer, primary_key = True)
    playerid = db.Column(db.String(), db.ForeignKey(Player.playerid))
    itemid = db.Column(db.Integer())
    quantity = db.Column(db.Integer())
    def __init__(self, playerid, itemid, quantity):
        self.playerid =  playerid
        self.itemid = itemid
        self.quantity = quantity
    
    def __repr__(self):
        return '<pkey %r>' % self.pkey
    
class Battles(db.Model):
    pkey = db.Column(db.Integer, primary_key = True)
    playerid = db.Column(db.String(), db.ForeignKey(Player.playerid))
    typeid = db.Column(db.Integer())
    opponentid = db.Column(db.String())

    def __init__(self, playerid, typeid, opponentid):
        self.playerid =  playerid
        self.typeid = typeid
        self.opponentid = opponentid

    def __repr__(self):
        return '<pkey %r>' %self.pkey

class Moves(db.Model):
    Moveid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    hpchange = db.Column(db.Integer)
    attackchange = db.Column(db.Integer)
    defensechange = db.Column(db.Integer)
    appliedeffect = db.Column(db.Integer)

    def __init__(self, name, dhp, dattack, ddefense, effect):
        self.name = name
        self.hpchange = dhp
        self.attackchange = dattack
        self.defensechange = ddefense
        self.appliedeffect = effect

    def __repr__(self):
        return '<Moveid %r>' %self.Moveid

class CharacterMoves(db.Model):
    pkey = db.Column(db.Integer, primary_key = True)
    characterid =db.Column(db.Integer(), db.ForeignKey(Characters.characterid))
    Moveid = db.Column(db.Integer(), db.ForeignKey(Moves.Moveid))

    def __init__(self, charid, moveid):
        self.characterid = charid
        self.Moveid = moveid

    def __repr__(self):
        return '<pkey %r>' %self.pkey
    
class LiveBattles(db.Model):
    battleid = db.Column(db.Integer, primary_key = True)
    senderid = db.Column(db.String(), db.ForeignKey(Player.playerid))
    recipientid = db.Column(db.String(), db.ForeignKey(Player.playerid))
    
    def __init__(self, sID, rID):
        self.senderid = sID
        self.recipientid = rID

    def __repr__(self):
        return '<battleid %r' %self.battleid

    
#define database table Player that contains users username, players unique id, players position and current map and active status
#active status will be used for authentication purposes
with app.app_context():
    db.create_all()

def createdbdata():
    with app.app_context():
        goku = Characters("Goku", 50, 30, 40)
        vegeta = Characters("Vegeta", 50, 40, 30)
        gohan = Characters("Gohan", 35, 50, 40)
        broly = Characters("Broly", 70, 50, 30)
        trunks = Characters("Trunks", 40, 40, 40)
        frieza = Characters("Frieza", 50, 30, 30)
        db.session.add(goku)
        db.session.add(vegeta)
        db.session.add(gohan)
        db.session.add(broly)
        db.session.add(trunks)
        db.session.add(frieza)
        NPC1 = NPC("map1", 20,26,"right")
        NPC2 = NPC("map1", 48,42,"up")
        NPC3 = NPC("map1", 42,38,"left")
        NPC4 = NPC("map1", 72,22,"down")
        db.session.add(NPC1)
        db.session.add(NPC2)
        db.session.add(NPC3)
        db.session.add(NPC4)
        NPC1Char1 = NPCTeam(1, 6, 5)
        NPC2Char1 = NPCTeam(2, 1, 15)
        NPC2Char2 = NPCTeam(2, 2, 15)
        NPC3Char1 = NPCTeam(3, 3, 40)
        NPC3Char2 = NPCTeam(3, 5, 40)
        NPC4Char1 = NPCTeam(4, 1, 80)
        NPC4Char2 = NPCTeam(4, 2, 80)
        NPC4Char3 = NPCTeam(4, 3, 80)
        NPC4Char4 = NPCTeam(4, 4, 80)
        NPC4Char5 = NPCTeam(4, 5, 80)
        NPC4Char6 = NPCTeam(4, 6, 80)
        db.session.add(NPC1Char1)
        db.session.add(NPC2Char1)
        db.session.add(NPC2Char2)
        db.session.add(NPC3Char1)
        db.session.add(NPC3Char2)
        db.session.add(NPC4Char1)
        db.session.add(NPC4Char2)
        db.session.add(NPC4Char3)
        db.session.add(NPC4Char4)
        db.session.add(NPC4Char5)
        db.session.add(NPC4Char6)
        Move1 = Moves("Punch", 10, 1, 0.75, 0)
        Move2 = Moves("Ki Blast", 15, 1, 1, 0)
        Move3 = Moves("Kamehameha", 50, 1, 1, 0)
        Move4 = Moves("Kaioken", 0, 2, 0.5, 0)
        Move5 = Moves("Big Bang Attack", 70, 0.75, 1, 0)
        Move6 = Moves("Pride", 0, 1.5, 0.75, 0)
        Move7 = Moves("Masenko", 40, 1, 1, 0)
        Move8 = Moves("Beast mode", 0, 3, 3, 0)
        Move9 = Moves("Saiyan of legends", 0, 3, 1, 0)
        Move10 = Moves("Adapt", 0, 1, 2, 0)
        Move11 = Moves("Sword slash", 70, 1, 1, 0)
        Move12 = Moves("Burning Blast", 30, 1, 1, 1)
        Move13 = Moves("Death Laser", 70, 1, 1, 0)
        Move14 = Moves("Bio-enhancement", 0, 1.5, 1.5, 0)
        db.session.add(Move1)
        db.session.add(Move2)
        db.session.add(Move3)
        db.session.add(Move4)
        db.session.add(Move5)
        db.session.add(Move6)
        db.session.add(Move7)
        db.session.add(Move8)
        db.session.add(Move9)
        db.session.add(Move10)
        db.session.add(Move11)
        db.session.add(Move12)
        db.session.add(Move13)
        db.session.add(Move14)
        db.session.commit()
        characters = Characters.query.filter(Characters.characterid>-1).all()
        for i in range(len(characters)):
            char = characters[i]
            punch = CharacterMoves(char.characterid, 1)
            Kiblast = CharacterMoves(char.characterid, 2)
            db.session.add(punch)
            db.session.add(Kiblast)
            for x in range(3,5):
                Mid = (i*2)+x
                relation = CharacterMoves(char.characterid, Mid)
                db.session.add(relation)
        db.session.commit()
with app.app_context():
    if len(Characters.query.filter(Characters.characterid>-1).all()) == 0:    
        createdbdata()
        print("Database created")
def addplayerchars():
    with app.app_context():
        plyr = Player.query.filter_by(username = "Charles").first()
        plyrchar = PlayerCharacter(plyr.playerid, 4, "10,1,0", "Inactive")
        item = PlayerItems(plyr.playerid, 2, 5)
        npc = NPC("map1", 13,12,"right")
        NPCteam = NPCTeam(1, 6, 5)
        db.session.add(npc)
        db.session.add(NPCteam)
        db.session.add(plyrchar)
        db.session.add(item)
        db.session.commit()
#addplayerchars()

#creating database
def generateandcheckPID():
    playerid = GenerateToken.Generate()
    if Player.query.filter_by(playerid=playerid).first() != None:
        playerid = generateandcheckPID()
    return playerid
def AddUser(username, email, password):
    with app.app_context():
        NewUser = User(username, email, password)
        PID = generateandcheckPID() 
        NewPlayer = Player(username, PID, 18, 14, "map1", 0)
        db.session.add(NewUser)
        db.session.add(NewPlayer)
        newcharacter = PlayerCharacter(PID, 1, "1,1,1", "Active")
        db.session.add(newcharacter)
        db.session.commit()
#function for adding a user to the database
def AuthIP(IP, username):
    account = User.query.filter_by(username=username).first()
    account.AuthedIp = IP
    db.session.commit()

def CheckAuth(PID, IP):
    playeraccount = Player.query.filter_by(playerid = PID).first()
    username = playeraccount.username
    account = User.query.filter_by(username=username).first()
    if account.AuthedIp == IP:
        return True
    else:
        return False

def removeIp(PID):
    playeraccount = Player.query.filter_by(playerid = PID).first()
    username = playeraccount.username
    account = User.query.filter_by(username=username).first()
    account.AuthedIp = None
    db.session.commit()

def getPID(usern):
    PID = Player.query.filter_by(username = usern).first()
    return str(PID.playerid)
#function for getting a users id from their username

def getUsername(PID):
    player = Player.query.filter_by(playerid = PID).first()
    return player.username
#function for getting the username of a user from their email

def getactivecharacters(Playerid):
    playercharacters = PlayerCharacter.query.filter((PlayerCharacter.playerid == Playerid)&(PlayerCharacter.active == "Active")).order_by(PlayerCharacter.characterid.asc()).all()
    characters = []
    levels = []
    for i in range(len(playercharacters)):
        characterid = (playercharacters[i].characterid)
        character = Characters.query.filter_by(characterid = characterid).first()
        characters.append(character.name)
        levels.append(playercharacters[i].modifiers.split(",")[0])
    return {"names": characters, "levels": levels}
    
    

def changeMap(PID, map):
    pass



#function for changing what map a player is on

#end of database stuff!!!:)
#//////////////////////////
#//////////////////////////
#//////////////////////////
#start of flask stuff:((((

@app.route("/Game", methods =["GET","POST"])
def Game():
    data = request.args.get("data")
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']
    if CheckAuth(data, userIP) == False:
        return redirect("/")
    else:
        removeIp(data)
        return render_template("Game.html", username = getUsername(data))
#route for the game

@app.route("/Login", methods =["GET","POST"])
def Login():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = addSystem(SysId)
    return render_template("Login.html", Token = Token)

@app.route("/Login/Failed", methods = ["GET", "POST"])
def LoginFailed():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = addSystem(SysId)
    return render_template("Login.html", Token = Token, message = "Login Failed Please Try Again")

@app.route('/Createaccount', methods =["GET","POST"])
def CreateAccount():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = addSystem(SysId)
    return render_template("Createaccount.html", Token = Token, message = "")

@app.route('/Createaccount/accountexists', methods =["GET","POST"])
def AccountExists():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = addSystem(SysId)
    message = "Account exists please login"
    return render_template("Createaccount.html", Token = Token, message = message )

@app.route("/ForgotPassword", methods =["GET","POST"])
def ForgotPassword():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = addSystem(SysId)
    print(SysToken)
    return render_template("Forgotpassword.html", Token = Token)

@app.route("/ForgotPassword/Failed", methods =["GET","POST"])
def ForgotPasswordFailed():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = addSystem(SysId)
    return render_template("Forgotpassword.html", Token = Token, message = "Please enter an email of an existing account")

@app.route('/', methods =["GET","POST"])
def Home():
    return render_template("Home.html")

@app.route("/Verify", methods =["GET","POST"])
def Verify():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    print(SysToken)
    Token = SysToken[SysId]
    if Token == request.form.get("Token"):
        if request.form.get("reference") == "CreateAccount":
            removeSystem(SysId)
            username = request.form.get("username")
            email = request.form.get("email")
            password = bytes(request.form.get("password"), "utf-8")
            hashedemail = hashlib.sha256(email.encode()).hexdigest()
            encryptedpassword = pki.encryptdata(password, publickey)
            try:
                AddUser(username, hashedemail, encryptedpassword)
                return redirect("/")
            except:
                return redirect("/Createaccount/accountexists")
        elif request.form.get("reference") == "Login":
            removeSystem(SysId)
            if ("@" in request.form.get("username")):
                email = request.form.get("username")
                hashedemail = hashlib.sha256(email.encode()).hexdigest()
                try:
                    account = User.query.filter_by(email=hashedemail).first()
                    encryptedpassword = account.password
                    username = account.username
                except:
                    return redirect("/Login/Failed")
            else:
                username = request.form.get("username")
                try:
                    account = User.query.filter_by(username=username).first()
                    encryptedpassword = account.password
                except:
                    return redirect("/Login/Failed")
            inputpassword = bytes(request.form.get("password"), "utf-8")
            password = pki.decryptdata(encryptedpassword, privatekey)
            if password == inputpassword:
                if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                    userIP = request.environ['REMOTE_ADDR']
                else:
                    userIP = request.environ['HTTP_X_FORWARDED_FOR']
                AuthIP(userIP, username)
                PID = getPID(username)
                return redirect(url_for("Game", data=PID))
            else:
                return redirect("/Login/Failed") 
        elif request.form.get("reference") == "ForgotPassword":
            inputvalue = request.form.get("input")
            email = [inputvalue]
            msg = Message("Reset Password - DragonMon", recipients=email)
            hashedemail = hashlib.sha256(inputvalue.encode()).hexdigest()
            try:
                account = User.query.filter_by(email=hashedemail).first()
                encryptedpassword = account.password
                username = account.username
            except:
                return redirect("/ForgotPassword/Failed")
            activepasswordreset[Token] = username
            message = "<p>Dear "+ username + "</p>"
            msg.html = render_template("ResetPasswordemail.html", data = message, Token = Token)
            mail.send(msg)
            print("messagesent")
            return redirect("/")
        elif request.form.get("reference") == "Resetpassword":
            removeSystem(SysId)
            print("hiii")
            password = bytes(request.form.get("new_password"), "utf-8")
            encryptedpassword = pki.encryptdata(password, publickey)
            Token = request.form.get("Token")
            username = activepasswordreset[Token]
            user = User.query.filter_by(username=username).first()
            user.password = encryptedpassword
            db.session.commit()
            return redirect("/")
    else:
        print(request.form.get("reference"))
        print("NOOO")
        return redirect("/ForgotPassword")
    
@app.route("/ResetPassword", methods = ["GET","POST"])
def ResetPassword():
    Token = request.args.get("Token")
    print(SysToken)
    return render_template("ResetPassword.html", Token = Token)

@app.route("/Friends", methods = ["GET", "POST"])
def friends():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = request.args.get("token")
    if SysToken[Token] == SysId:
        SysToken.pop(Token)
        return render_template("Friends.html", token = Token)
    else:
        return redirect("/")

@app.route("/Messages", methods = ["GET", "POST"])
def messages():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Token = request.args.get("token")
    if SysToken[Token] == SysId:
        username = Token_username[Token]
        SysToken.pop(Token)
        return render_template("Messages.html", username = username)
    else:
        return redirect("/")
    
@app.route("/Battle", methods = ["GET", "POST"])
def Battle():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    pid = request.args.get("pid")
    if Sys_pid[pid] == SysId:
        player = Player.query.filter_by(playerid = pid).first()
        username = player.username
        Sys_pid.pop(pid)
        return render_template("Battle.html", username = username)
    else:
        return redirect("/")


#///End of Flask///#
#//////////////////#
#//////////////////#
#//////////////////#
#//// Socket io////#

@socketio.on("GoBack")
def Goback():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Sockid =  request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playerid = player.playerid
    username = player.username
    user = User.query.filter_by(username = username).first()
    user.AuthedIp = SysId
    db.session.commit()
    socketio.emit("ToGame", {"PID" : playerid}, to = Sockid)

@socketio.on("getFriends")
def getFriends(Token):
    #generate dict of friends for specific user somehow need to store a relationship between sockid and username
    username = Token_username[Token]
    Sockid = request.sid
    player = Player.query.filter_by(username = username).first()
    player.Sockid = Sockid
    db.session.commit()
    #stored Sockid against user
    friends = getplayerfriends(username, 1)
    socketio.emit("RecieveFriends", friends, to = Sockid)
        
@socketio.on("removeFriend")
def removefriend(Token, Friendname):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()    
    username = player.username
    record = Friends.query.filter_by(initiator = username, recipient = Friendname).first()
    if record == None:
        record = Friends.query.filter_by(recipient = username, initiator = Friendname).first()
    db.session.delete(record)
    db.session.commit()
    SysToken[Token] = SysId
    socketio.emit("UpdateTable", to = Sockid)
    sender = Player.query.filter_by(username = Friendname).first()
    friends = getplayerfriends(Friendname, 1)
    socketio.emit("RecieveFriends", friends, to = sender.Sockid)

@socketio.on("Finalise")
def Finaliseconnection(data):
    print("CONNECTED")
    username = data
    sockid = request.sid
    player = Player.query.filter_by(username = username).first()
    player.Sockid = sockid
    db.session.commit()
    activechardata = getactivecharacters(player.playerid)
    characters = activechardata["names"]
    urls = generateUrls(characters)
    socketio.emit("Activecharacters", {"Characters":characters, "Urls":urls, "Levels": activechardata["levels"]}, to = sockid)
    #above is to send characters for table on left hand side of page
    mapname = player.currentmap
    data = mapdata[mapname]
    Map = data["data"]
    xpos = player.xpostion
    ypos = player.yposition
    fname1 = "static/Assets/%s.png"%mapname
    fname2 = "static/Assets/Top%s.png"%mapname
    fnames = [fname1, fname2]
    socketio.emit("mapdata", {"data":Map, "ypos":ypos, "xpos":xpos, "map":fnames}, to = sockid)
    #aboce sends data regarding collision tiles and player pos
    NPCs = []
    ids = []
    beatenstring = player.BeatenNPCs
    beatenids = []
    if beatenstring != None:
        beatenlist = beatenstring.split(",")
        for i in range(len(beatenlist)):
            beatenids.append(int(beatenlist[i]))
    xposs = []
    yposs = []
    lookings = []
    if mapname == "map1":
        NPCs = NPC.query.filter_by(map = mapname).all()
        for i in range(len(NPCs)):
            npc = NPCs[i]
            ids.append(npc.npcid)
            xposs.append(npc.xpos)
            yposs.append(npc.ypos)
            lookings.append(npc.looking)
    socketio.emit("NPCS", {"ids":ids,"xposs":xposs,"yposs":yposs,"lookings":lookings, "beaten":beatenids}, to = sockid)
    #sends npc data
    friendsdict = getplayerfriends(username, 1)
    friendnameslist = list(friendsdict.values())
    for i in range(len(friendnameslist)):
        friendname = friendnameslist[i]
        friend = Player.query.filter_by(username = friendname).first()
        socketio.emit("Friendpos", {"account":friend.username, "xpos":friend.xpostion, "ypos":friend.yposition}, to = sockid)
    #sends friend data
    btlreqnames = []
    btlreqs = LiveBattles.query.filter_by(recipientid = player.playerid).all()
    for i in range(len(btlreqs)):
        sID = btlreqs[i].senderid
        sender = Player.query.filter_by(playerid = sID).first()
        btlreqnames.append(sender.username)
    socketio.emit("battlerequestdata", {"names":btlreqnames}, to = sockid)



    
@socketio.on("Redirecting")
def Confirmredirect():
    Sockid = request.sid
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    newtoken = GenerateToken.Generate()
    SysToken[newtoken] = SysId
    Token_username[newtoken] = username
    socketio.emit("Redirectconfirmed", {"token" : newtoken}, to = Sockid)

@socketio.on("Requestfriendmessages")
def requestmessages(Targetname):
    Sockid = request.sid
    messages = GetP2Pmessages(Sockid, Targetname)
    socketio.emit("Recievemessages", messages, to = Sockid)

@socketio.on("ClearMessages")
def ClearMessages(Target):
    Sockid = request.sid
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    timeofsend = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    check = Player.query.filter_by(username = Target).first()
    print(check)
    if check == None:
        type = "Group"
    else:
        type = "Friend"
    if type == "Friend":
        messages = P2PMessages.query.filter(((P2PMessages.sender == username) & (P2PMessages.recipient == Target)) | ((P2PMessages.sender == Target) & (P2PMessages.recipient == username))).order_by(P2PMessages.Timeofsent.asc()).all()
        for i in range(len(messages)):
            message = messages[i]
            db.session.delete(message)
        #add message to conversation saying messages cleared
        msg = "System:    %s has cleared the conversation"%username
        bformattedmessage = bytes(msg, "utf-8")
        encryptedmessage = pki.encryptdata(bformattedmessage, publickey)
        newmessage = P2PMessages(timeofsend, username, Target, encryptedmessage)
        db.session.add(newmessage)
        db.session.commit()
        friend = Player.query.filter_by(username = Target).first()
        othersocket = friend.Sockid
        listoftargetsockets =[Sockid, othersocket]
        for i in range(len(listoftargetsockets)):
            socket = listoftargetsockets[i]
            socketio.emit("Recievemessages", messages, to = socket)
    elif type == "Group":
        print("Recieved Group")
        messages = GroupMessages.query.filter_by(Groupid = Target).order_by(GroupMessages.Timeofsent.asc()).all()
        for i in range(len(messages)):
            db.session.delete(messages[i])
        msg = "System:    %s has cleared the conversation"%username
        bformattedmessage = bytes(msg, "utf-8")
        encryptedmessage = pki.encryptdata(bformattedmessage, publickey)
        newmessage = GroupMessages(timeofsend, Target, encryptedmessage)
        db.session.add(newmessage)
        db.session.commit()
        listoftargetsockets =[]
        listofmemberentries = PlayerGroups.query.filter_by(Groupid = Target).all()
        for entry in listofmemberentries:
            player = Player.query.filter_by(username = entry.username).first()
            listoftargetsockets.append(player.Sockid)
        messages = GetGroupMessages(Target)
        for i in range(len(listoftargetsockets)):
            socket = listoftargetsockets[i]
            socketio.emit("Recievemessages", messages, to = socket)
        
        
def GetP2Pmessages(Sockid, Targetname):
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    objectrecords = P2PMessages.query.filter(((P2PMessages.sender == username) & (P2PMessages.recipient == Targetname)) | ((P2PMessages.sender == Targetname) & (P2PMessages.recipient == username))).order_by(P2PMessages.Timeofsent.asc()).all()
    messages = {}
    for i in range(len(objectrecords)):
        encryptedmessage = objectrecords[i].message
        rawmessage = pki.decryptdata(encryptedmessage, privatekey)
        message = rawmessage.decode("utf-8")
        messages[i] = message
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n")
    print(messages)
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n")
    return messages

@socketio.on("Requestconversations")
def requestconversations():
    Sockid = request.sid
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    friendsdict = getplayerfriends(username, 1)
    Groups = PlayerGroups.query.filter_by(username = username).all()
    print("\n\n\n\n\n\n\n")
    print(Groups)
    print("\n\n\n\n\n\n\n")
    Groupnamedict = {}
    Groupiddict = {}
    for i in range(len(Groups)):
        Groupid = Groups[i].Groupid
        Groupname = GroupNames.query.filter_by(Groupid = Groupid).first().Groupname
        Groupnamedict[i] = Groupname
        Groupiddict[i] = Groupid  
    print("\n\n\n\n\n\n\n")
    print((friendsdict, Groupnamedict, Groupiddict))
    print("\n\n\n\n\n\n\n")
    socketio.emit("Recieveconversations", data = (friendsdict, Groupnamedict, Groupiddict), to = Sockid)


@socketio.on("SendMessage")
def addmessage(message, target):
    print(message, target)
    Sockid = request.sid
    timeofsend = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    formattedmessage = "%s:    "%username + message
    bformattedmessage = bytes(formattedmessage, "utf-8")
    encryptedmessage = pki.encryptdata(bformattedmessage, publickey)
    checktarget = Player.query.filter_by(username = target).first()
    if checktarget != None:
        newmessage = P2PMessages(timeofsend, username, target, encryptedmessage)
        targetrecord = Player.query.filter_by(username = target).first()
        targetsocket = targetrecord.Sockid
        db.session.add(newmessage)
        db.session.commit()
        messages = GetP2Pmessages(Sockid, target)
        socketio.emit("Recievemessages", messages, to=Sockid)
        socketio.emit("Recievemessages", messages, to=targetsocket)
    else:
        newmessage = GroupMessages(timeofsend, target, encryptedmessage)
        db.session.add(newmessage)
        db.session.commit()
        listofmembers = PlayerGroups.query.filter_by(Groupid = target).all()
        messages = GetGroupMessages(target)
        for i in range(len(listofmembers)):
            member = listofmembers[i].username
            socket = Player.query.filter_by(username = member).first().Sockid
            socketio.emit("Recievemessages", messages, to=socket)
            
@socketio.on("AddMember")
def AddGroupMember(target, Groupid):
    print(target)
    newmember = PlayerGroups(target, Groupid)
    db.session.add(newmember)
    timeofsend = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    rawmessage = bytes("System: %s was added to the group"%target, "utf-8")
    encryptedmessage = pki.encryptdata(rawmessage, publickey)
    sysmessage = GroupMessages(timeofsend, Groupid, encryptedmessage)
    db.session.add(sysmessage)
    db.session.commit()
    listofmembers = PlayerGroups.query.filter_by(Groupid = Groupid).all()
    messages = GetGroupMessages(target)
    print(listofmembers)
    for i in range(len(listofmembers)):
        member = listofmembers[i].username
        print(member)
        socket = Player.query.filter_by(username = member).first().Sockid
        print(socket)
        socketio.emit("refresh", messages, to=socket)

@socketio.on("RequestGroupconversation")
def Groupconversation(Groupid):
    Sockid = request.sid
    messages = GetGroupMessages(Groupid)
    socketio.emit("Recievemessages", messages, to=Sockid)

@socketio.on("disconnect")
def disconnectclient():
    print("Disconnected", str(request.sid))
    disconnect()

@socketio.on("currentmap")
def getcurrentmap(data):
    #changeMap()
    pass

@socketio.on("Friends")
def Friendsredirect():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    #generate token and emit this is in /Game
    Token = GenerateToken.Generate()
    SysToken[Token] = SysId
    #store relationship between Token and username by getting username from sockid
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    username = player.username
    Token_username[Token] = username
    socketio.emit("Friends", {"data" : Token}, to = Sockid)

@socketio.on("searchName")
def Searchforname(Targetname):
    Sockid = request.sid
    print("NAMENAMENAMENAME")
    print(Targetname)
    print("NAMENAMENAMENAME")
    Target = Player.query.filter_by(username = Targetname).first()
    if Target == None:
        socketio.emit("Nameresult", {"data":"None"}, to = Sockid)
    else:
        TargetName = Target.username
        socketio.emit("Nameresult", {"data": TargetName}, to = Sockid)

@socketio.on("SendFriendRequest")
def GenerateFriendRequest(TargetName):
    Sockid = request.sid
    sender = Player.query.filter_by(Sockid = Sockid).first()
    sendername = sender.username
    existingrecord = Friends.query.filter_by(initiator = sendername, recipient = TargetName).first()
    existingrecord2 = Friends.query.filter_by(initiator = TargetName, recipient = sendername).first()
    if existingrecord == None and existingrecord2 == None:
        print("\n\n\n\n\n\n REQUEST/FRIEND exists")
        newfriendship = Friends(sendername, TargetName, 0)
        db.session.add(newfriendship)
        db.session.commit()
    target = Player.query.filter_by(username = TargetName).first()
    requests = getplayerfriends(TargetName, 0)
    socketio.emit("Friendrequests", requests, to = target.Sockid)

@socketio.on("getRequests")
def GetfriendRequests():
    Sockid = request.sid
    recipient = Player.query.filter_by(Sockid = Sockid).first()
    recipientname = recipient.username
    requests = getplayerfriends(recipientname, 0)
    socketio.emit("Friendrequests", requests, to = Sockid)

@socketio.on("AcceptFriend")
def AcceptFriend(Token, Friendname):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playername = player.username
    record = Friends.query.filter_by(initiator = Friendname, recipient = playername).first()
    record.accepted = 1
    sender = Player.query.filter_by(username = Friendname).first()
    db.session.commit()
    SysToken[Token] = SysId
    sender = Player.query.filter_by(username = Friendname).first()
    friends = getplayerfriends(Friendname, 1)
    socketio.emit("RecieveFriends", friends, to = sender.Sockid)


@socketio.on("DeclineFriend")
def DeclineFriend(Token, TargetName):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playername = player.username
    record = Friends.query.filter_by(initiator = TargetName, recipient = playername).first()
    db.session.delete(record)
    db.session.commit()
    SysToken[Token] = SysId

@socketio.on("CreateGroup")
def CreateGroup(Members, Groupname):
    Sockid = request.sid
    if len(Members)<2:
        socketio.emit("Notenoughmembers", to = Sockid)
    else:
        initiatorname = Player.query.filter_by(Sockid = Sockid).first().username
        Groupid = Generate_check_group()
        NewGroupname = GroupNames(Groupid, Groupname)
        db.session.add(NewGroupname)
        for i in range(len(Members)):
            member = Members[i]
            memberaccount = Player.query.filter_by(username = member).first()
            membersocket = memberaccount.Sockid
            socketio.emit("refresh", to = membersocket)
            newmember = PlayerGroups(member, Groupid)
            db.session.add(newmember)
        addinitiator = PlayerGroups(initiatorname, Groupid)
        db.session.add(addinitiator)
        for i in range(len(Members)):
            member = Members[i]
            memberaccount = Player.query.filter_by(username = member).first()
            membersocket = memberaccount.Sockid
        db.session.commit()
        socketio.emit("refresh", Sockid)

@socketio.on("LeaveGroup")
def LeaveGroup(Groupid):
    Sockid = request.sid
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    record = PlayerGroups.query.filter_by(username = username, Groupid = Groupid).first()
    db.session.delete(record)
    db.session.commit()
    timeofsend = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    rawmessage = bytes("System: %s left the group"%username, "utf-8")
    encryptedmessage = pki.encryptdata(rawmessage, publickey)
    sysmessage = GroupMessages(timeofsend, Groupid, encryptedmessage)
    db.session.add(sysmessage)
    db.session.commit()
    listofmembers = PlayerGroups.query.filter_by(Groupid = Groupid).all()
    messages = GetGroupMessages(Groupid)
    for i in range(len(listofmembers)):
        member = listofmembers[i].username
        socket = Player.query.filter_by(username = member).first().Sockid
        socketio.emit("Recievemessages", messages, to=socket)
    socketio.emit("refresh", to = Sockid)

@socketio.on("GetMembers")
def GetGroupMembers(Groupid):
    Sockid = request.sid
    user = Player.query.filter_by(Sockid = Sockid).first()
    username = user.username
    groupmembers = PlayerGroups.query.filter_by(Groupid = Groupid).all()
    groupmembernames = []
    for i in range(len(groupmembers)):
        groupmembernames.append(groupmembers[i].username)
    groupmembernames.remove(username)
    Membersdict = {}
    for i in range(len(groupmembernames)):
        Membersdict[i] = groupmembernames[i]
    socketio.emit("GroupMembers", Membersdict, to = Sockid)

@socketio.on("Bag")
def Bag():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playerid = player.playerid
    records = PlayerItems.query.filter_by(playerid = playerid).all()
    items = {}
    quantities = {}
    for i in range(len(records)):
        items[i] = records[i].itemid
        quantities[i] = records[i].quantity
    socketio.emit("Items", data = items, to = Sockid)
    socketio.emit("Quantities", data = quantities, to = Sockid)

@socketio.on("Team")
def Team():
    Sockid = request.sid
    playerid = Player.query.filter_by(Sockid = Sockid).first().playerid
    records = PlayerCharacter.query.filter_by(playerid = playerid).all()
    Names = {}
    Ids = []
    Levels = {}
    CurrentHp = {}
    FullHp = {}
    Urls = {}
    States = {}
    print(records)
    for i in range(len(records)):
        currentrecord = records[i]
        modifiers = currentrecord.modifiers.split(",")
        level = int(modifiers[0])
        Levels[i] = int(level)
        Hppercent = float(modifiers[1])
        Character = Characters.query.filter_by(characterid = currentrecord.characterid).first()
        Names[i] = Character.name
        Ids.append(currentrecord.pkey)
        FullHealth = Character.Hp * level
        print(type(FullHealth), type(Hppercent))
        Hp = FullHealth * Hppercent
        CurrentHp[i] = Hp
        FullHp[i] = FullHealth
        url = "static/Assets/%s.png"%Character.name
        Urls[i]= url
        state = currentrecord.active
        States[i] = state
    socketio.emit("Namesandids", {"Names":Names,"ids":Ids}, to = Sockid)
    socketio.emit("Levels", Levels, to = Sockid)
    socketio.emit("CurrentHps", CurrentHp, to = Sockid)
    socketio.emit("FullHp", FullHp, to = Sockid)
    socketio.emit("Urls", Urls, to = Sockid)
    socketio.emit("States", States, to = Sockid)

@socketio.on("RemoveTeamMember")
def removeteammember(pkey):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playerid = player.playerid
    playercharacter = PlayerCharacter.query.filter_by(pkey = pkey).first()
    currentteam = PlayerCharacter.query.filter_by(playerid = playerid, active = "Active").all()
    if len(currentteam)>1:
        playercharacter.active = "Inactive"
        db.session.commit()
        activedata = getactivecharacters(player.playerid)
        characters = activedata["names"]
        levels = activedata["levels"]
        urls = generateUrls(characters)
        socketio.emit("Activecharacters", {"Characters":characters, "Urls":urls, "Levels":levels}, to = Sockid)
        States = {}
        allcharacters = PlayerCharacter.query.filter_by(playerid = playerid).all()
        for i in range(len(allcharacters)):
            currentrecord = allcharacters[i]
            state = currentrecord.active
            States[i] = state
        socketio.emit("States", States, to = Sockid)

@socketio.on("AddTeamMember")
def addteammember(pkey):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playerid = player.playerid
    playercharacter = PlayerCharacter.query.filter_by(pkey = pkey).first()
    currentteam = PlayerCharacter.query.filter_by(playerid = playerid, active = "Active").all()
    if len(currentteam)<6:
        playercharacter.active = "Active"
        db.session.commit()
        activedata = getactivecharacters(player.playerid)
        characters = activedata["names"]
        levels = activedata["levels"]
        urls = generateUrls(characters)
        socketio.emit("Activecharacters", {"Characters":characters, "Urls":urls, "Levels":levels}, to = Sockid)
        States = {}
        allcharacters = PlayerCharacter.query.filter_by(playerid = playerid).all()
        for i in range(len(allcharacters)):
            currentrecord = allcharacters[i]
            state = currentrecord.active
            States[i] = state
        socketio.emit("States", States, to = Sockid)


@socketio.on("MovePlayer")
def Changeplayerpos(data):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid=Sockid).first()
    direction = data
    print(direction)
    if direction==1:
        player.yposition -=1
        emitnextmove = 1
    elif direction==2:
        player.xpostion -=1
        emitnextmove = 2
    elif direction==3:
        player.yposition +=1
        emitnextmove = 3
    elif direction==4:
        player.xpostion +=1
        emitnextmove = 4
    db.session.commit()
    sockets = getSockets(player)
    for i in range(len(sockets)):
        socketio.emit("UpdateFriendpos", {"account":player.username, "nextmove":emitnextmove}, to = sockets[i])

        
@socketio.on("AIbattle")
def doAIbattle(NPCid):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playerid = player.playerid
    battles = Battles.query.filter_by(playerid = player.playerid).all()
    for i in range(len(battles)):
        db.session.delete(battles[i])
    opponentid = NPCid
    btl = Battles(playerid, 1, opponentid)
    db.session.add(btl)
    db.session.commit()
    Sys_pid[playerid] = SysId
    socketio.emit("battle", {"pid":playerid}, to = Sockid)

@socketio.on("Grassbattle")
def dorandomencounter():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    playerid = player.playerid
    battles = Battles.query.filter_by(playerid = player.playerid).all()
    for i in range(len(battles)):
        db.session.delete(battles[i])
    opponentid = random.randint(1,6)
    btl = Battles(playerid, 0, opponentid)
    db.session.add(btl)
    db.session.commit()
    Sys_pid[playerid] = SysId
    socketio.emit("battle", {"pid":playerid}, to = Sockid)

@socketio.on("offlinelose")
def offlinelose():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    player.wins -= 1
    if player.wins<=-1:
        player.wins = 0
    player.xpostion = 15
    player.yposition = 15
    db.session.delete(battle)
    db.session.commit()

@socketio.on("onlinelose")
def onlinelose():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    player.wins -= 1
    if player.wins<=-1:
        player.wins = 0
    db.session.delete(battle)
    db.session.commit()

@socketio.on("offlinewin")
def offlinewin():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    print(battle)
    db.session.delete(battle)
    db.session.commit()
    if battle.typeid == 1:
        print(player.BeatenNPCs)
        if player.BeatenNPCs!=None:
            player.BeatenNPCs = player.BeatenNPCs + "," + str(battle.opponentid)
        else:
            player.BeatenNPCs = str(battle.opponentid)
    player.wins += 1
    characters = PlayerCharacter.query.filter((PlayerCharacter.playerid == player.playerid)&(PlayerCharacter.active == "Active")).all()
    for i in range (len(characters)):
        character = characters[i]
        mods = character.modifiers.split(",")
        print(mods)
        level = int(mods[0])
        xppercent = float(mods[2])
        xppercent += 8/(level+17.5)
        if xppercent>=1:
            delta = math.floor(xppercent)
            xppercent -= delta
            level += delta
        character.modifiers = str(level)+",1,"+str(xppercent)
    newitemid = random.randint(1,10)
    existingrecord = PlayerItems.query.filter((PlayerItems.playerid == player.playerid)&(PlayerItems.itemid==newitemid)).first()
    if existingrecord==None:
        newrecord = PlayerItems(player.playerid, newitemid, 1)
        db.session.add(newrecord)
    else:
        existingrecord.quantity += 1
    db.session.commit()

@socketio.on("onlinewin")
def onlinewin():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    db.session.delete(battle)
    if battle.typeid == 1:
        print(player.BeatenNPCs)
        if player.BeatenNPCs!=None:
            player.BeatenNPCs = player.BeatenNPCs + "," + str(battle.opponentid)
        else:
            player.BeatenNPCs = str(battle.opponentid)
    player.wins += 1
    characters = PlayerCharacter.query.filter((PlayerCharacter.playerid == player.playerid)&(PlayerCharacter.active == "Active")).all()
    for i in range (len(characters)):
        character = characters[i]
        mods = character.modifiers.split(",")
        print(mods)
        level = int(mods[0])
        xppercent = float(mods[2])
        xppercent += 10/(level+17.5)
        if xppercent>=1:
            delta = math.floor(xppercent)
            xppercent -= delta
            level += delta
        character.modifiers = str(level)+",1,"+str(xppercent)
    db.session.commit()

@socketio.on("Getbattledata")
def Getbattledata():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    teamrecords = PlayerCharacter.query.filter((PlayerCharacter.playerid == player.playerid)&(PlayerCharacter.active == "Active")).all()
    team = []
    for i in range(len(teamrecords)):
        characterdata = {}
        record = teamrecords[i]
        mods = record.modifiers.split(",")
        hpmod = float(mods[1])
        level = float(mods[0])
        character = Characters.query.filter_by(characterid = record.characterid).first()
        characterdata["name"] = character.name
        characterdata["Fullhp"] = character.Hp*level
        characterdata["hp"] = character.Hp*level*hpmod
        characterdata["Attack"] = character.Attack*level
        characterdata["Defense"] = character.Defense*level
        characterdata["level"] = level
        moves = []
        charmoveids = CharacterMoves.query.filter_by(characterid = record.characterid).all()
        print(record.characterid)
        print(charmoveids)
        for x in range(len(charmoveids)):
            move = Moves.query.filter_by(Moveid = charmoveids[x].Moveid).first()
            movedata = {}
            movedata["name"] = move.name
            movedata["hpchange"] = move.hpchange
            movedata["attackchange"] = move.attackchange
            movedata["defensechange"] = move.defensechange
            movedata["effect"] = move.appliedeffect
            moves.append(movedata)
        characterdata["moves"] = moves
        team.append(characterdata)
    socketio.emit("Playerbattledata", {"data":team}, to = Sockid)
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponentid = battle.opponentid
    oppteam = []
    if battle.typeid==0:
        character = Characters.query.filter_by(characterid = opponentid).first()
        characterdata = {}
        level = math.floor(math.log(1+player.wins, 2)+1)
        print("\n\n\n\n\n\n\n\n\n")
        print(level)
        print("\n\n\n\n\n\n\n\n\n")
        characterdata["name"] = character.name
        characterdata["Fullhp"] = character.Hp*level
        characterdata["hp"] = character.Hp*level
        characterdata["Attack"] = character.Attack*level
        characterdata["Defense"] = character.Defense*level
        characterdata["level"] = level
        moves = []
        charmoveids = CharacterMoves.query.filter_by(characterid = character.characterid).all()
        for x in range(len(charmoveids)):
            move = Moves.query.filter_by(Moveid = charmoveids[x].Moveid).first()
            movedata = {}
            movedata["name"] = move.name
            movedata["hpchange"] = move.hpchange
            movedata["attackchange"] = move.attackchange
            movedata["defensechange"] = move.defensechange
            movedata["effect"] = move.appliedeffect
            moves.append(movedata)
        characterdata["moves"] = moves
        oppteam.append(characterdata)
    elif battle.typeid == 1:
        npc = NPC.query.filter_by(npcid = opponentid).first()
        npcteam = NPCTeam.query.filter_by(npcid = npc.npcid).all()
        for i in range(len(npcteam)):
            record = npcteam[i]
            level = record.level
            characterid = record.characterid
            characterdata = {}
            character = Characters.query.filter_by(characterid = characterid).first()
            characterdata["name"] = character.name
            characterdata["Fullhp"] = character.Hp*level
            characterdata["hp"] = character.Hp*level
            characterdata["Attack"] = character.Attack*level
            characterdata["Defense"] = character.Defense*level
            characterdata["level"] = level
            moves = []
            charmoveids = CharacterMoves.query.filter_by(characterid = character.characterid).all()
            for x in range(len(charmoveids)):
                move = Moves.query.filter_by(Moveid = charmoveids[x].Moveid).first()
                movedata = {}
                movedata["name"] = move.name
                movedata["hpchange"] = move.hpchange
                movedata["attackchange"] = move.attackchange
                movedata["defensechange"] = move.defensechange
                movedata["effect"] = move.appliedeffect
                moves.append(movedata)
            characterdata["moves"] = moves
            oppteam.append(characterdata)
    else:
        opponentteamrecords = PlayerCharacter.query.filter((PlayerCharacter.playerid == opponentid)&(PlayerCharacter.active == "Active")).all()
        for i in range(len(opponentteamrecords)):
            characterdata = {}
            record = opponentteamrecords[i]
            mods = record.modifiers.split(",")
            level = int(mods[0])
            characterid = record.characterid
            character = Characters.query.filter_by(characterid = characterid).first()
            characterdata["name"] = character.name
            characterdata["Fullhp"] = character.Hp*level
            characterdata["hp"] = character.Hp*level
            characterdata["Attack"] = character.Attack*level
            characterdata["Defense"] = character.Defense*level
            characterdata["level"] = level
            moves = []
            charmoveids = CharacterMoves.query.filter_by(characterid = character.characterid).all()
            for x in range(len(charmoveids)):
                move = Moves.query.filter_by(Moveid = charmoveids[x].Moveid).first()
                movedata = {}
                movedata["name"] = move.name
                movedata["hpchange"] = move.hpchange
                movedata["attackchange"] = move.attackchange
                movedata["defensechange"] = move.defensechange
                movedata["effect"] = move.appliedeffect
                moves.append(movedata)
            characterdata["moves"] = moves
            print(characterdata)
            oppteam.append(characterdata)
    socketio.emit("Opponentbattledata", {"data":oppteam, "type":battle.typeid}, to = Sockid)
    LiveMoves[Sockid] = None
    LiveTeamexists[Sockid] = True

        

@socketio.on("sendbattlerequest")    
def sendbtlreq(targetname):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    target = Player.query.filter_by(username = targetname).first()
    newbattle = LiveBattles(player.playerid, target.playerid)
    db.session.add(newbattle)
    db.session.commit()
    btlreqnames = []
    btlreqs = LiveBattles.query.filter_by(recipientid = target.playerid).all()
    for i in range(len(btlreqs)):
        sID = btlreqs[i].senderid
        sender = Player.query.filter_by(playerid = sID).first()
        btlreqnames.append(sender.username)
    socketio.emit("battlerequestdata", {"names":btlreqnames}, to = target.Sockid)

@socketio.on("Declinebattle")
def declinebtl(sendername):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    sender = Player.query.filter_by(username = sendername).first()
    record = LiveBattles.query.filter((LiveBattles.senderid == sender.playerid) & (LiveBattles.recipientid == player.playerid)).first()
    db.session.delete(record)
    db.session.commit()

@socketio.on("Acceptbattle")
def acceptbtl(sendername):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    sender = Player.query.filter_by(username = sendername).first()
    record = LiveBattles.query.filter((LiveBattles.senderid == sender.playerid) & (LiveBattles.recipientid == player.playerid)).first()
    socketio.emit("Confirmbattle", {"battleid":record.battleid}, to = sender.Sockid)
    
@socketio.on("Dolivebattle")
def dolivebattle(battleid):
    Sockid = request.sid 
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        SysId = request.environ['REMOTE_ADDR']
    else:
        SysId = request.environ['HTTP_X_FORWARDED_FOR']
    record = LiveBattles.query.filter_by(battleid = battleid).first()
    recipient = Player.query.filter_by(playerid = record.recipientid).first() 
    sender = Player.query.filter_by(Sockid = Sockid).first() 
    Sys_pid[sender.playerid] = SysId
    Sys_pid[record.senderid] = SysId
    battles = Battles.query.filter_by(playerid = sender.playerid).all()
    for i in range(len(battles)):
        db.session.delete(battles[i])
    battles = Battles.query.filter_by(playerid = recipient.playerid).all()
    for i in range(len(battles)):
        db.session.delete(battles[i])
    newbattle1 = Battles(sender.playerid, 2, recipient.playerid)
    newbattle2 = Battles(recipient.playerid, 2, sender.playerid)
    db.session.delete(record)
    db.session.add(newbattle1)
    db.session.add(newbattle2)
    db.session.commit()
    socketio.emit("battle" , {"pid":sender.playerid}, to = Sockid)
    socketio.emit("battle" , {"pid":recipient.playerid}, to = recipient.Sockid)

@socketio.on("MoveChosen")
def MoveChosen(Move):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    LiveMoves[Sockid] = Move
    if LiveMoves[Sockid] != None and LiveMoves[opponent.Sockid] != None:
        socketio.emit("DoMoves", {"Playermove":LiveMoves[Sockid],"Oppmove":LiveMoves[opponent.Sockid]}, to = Sockid)
        socketio.emit("DoMoves", {"Playermove":LiveMoves[opponent.Sockid],"Oppmove":LiveMoves[Sockid]}, to = opponent.Sockid)
        LiveMoves[Sockid] = None
        LiveMoves[opponent.Sockid] = None

@socketio.on("SwitchCharacters")
def switchchars(pointer):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    socketio.emit("SwitchChars", pointer, to = opponent.Sockid)

@socketio.on("Characterdied")
def Characterdied():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    socketio.emit("skipmove", to = opponent.Sockid)
    socketio.emit("oppchardied")

@socketio.on("healused")
def useheal(healamount):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    socketio.emit("healuser", {"amount":healamount}, to = Sockid)
    socketio.emit("healopp", {"amount":healamount}, to = opponent.Sockid)

@socketio.on("runaway")
def runaway():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    socketio.emit("win", to = opponent.Sockid)

@socketio.on("Resetplayer")
def resetplayer():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    player.xpostion = 15
    player.yposition = 15
    db.session.commit()

@socketio.on("caughtopp")
def catchopponent():
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    newchar = PlayerCharacter(player.playerid, battle.opponentid, "5,1,0", "Inactive")
    db.session.add(newchar)
    db.session.commit()

@socketio.on("itemused")
def useitem(itemid):
    Sockid = request.sid
    player = Player.query.filter_by(Sockid = Sockid).first()
    record = PlayerItems.query.filter((PlayerItems.playerid==player.playerid)&(PlayerItems.itemid==itemid)).first()
    record.quantity-=1
    if record.quantity <= 0:
        db.session.delete(record)
    if record.itemid > 5:
        battle = Battles.query.filter_by(playerid = player.playerid).first()
        if battle.typeid==2:
            opponent = Player.query.filter_by(playerid = battle.opponentid).first()
            socketio.emit("oppitemused", itemid, to = opponent.Sockid)
    db.session.commit()

@socketio.on("teamleft")
def teamisleft():
    Sockid = request.sid
    LiveTeamexists[Sockid] = True
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    if (LiveTeamexists[opponent.Sockid]==False):
        socketio.emit("win", to = Sockid)
        socketio.emit("lose", to = opponent.Sockid)
    else:
        socketio.emit("ResetButtons", to=Sockid)

    

@socketio.on("noteamleft")
def noteamisleft():
    Sockid = request.sid
    LiveTeamexists[Sockid] = False
    player = Player.query.filter_by(Sockid = Sockid).first()
    battle = Battles.query.filter_by(playerid = player.playerid).first()
    opponent = Player.query.filter_by(playerid = battle.opponentid).first()
    if (LiveTeamexists[opponent.Sockid]==False):
        socketio.emit("draw", to = Sockid)
        socketio.emit("draw", to = opponent.Sockid)
    else:
        socketio.emit("lose", to = Sockid)
        socketio.emit("win", to = opponent.Sockid)


def getSockets(player):
    friendsdict = getplayerfriends(player.username, 1)
    friends = list(friendsdict.values())
    Sockets = []
    for i in range(len(friends)):
        friendname = friends[i]
        friendacc = Player.query.filter_by(username = friendname).first()
        Sockets.append(friendacc.Sockid)
    return Sockets

    





    

def Generate_check_group():
    Groupid = GenerateToken.Generate()
    check = GroupNames.query.filter_by(Groupid = Groupid).first()
    if check == None:
        return Groupid
    else:
       Generate_check_group() 


def GetGroupMessages(Groupid):
    Grouprecords = GroupMessages.query.filter_by(Groupid = Groupid).order_by(GroupMessages.Timeofsent.asc()).all()
    messages = {}
    for i in range(len(Grouprecords)):
        encryptedmessage = Grouprecords[i].message
        binarymessage = pki.decryptdata(encryptedmessage, privatekey)
        message = binarymessage.decode("utf-8")
        messages[i] = message
    print(messages)
    return messages

def addSystem(SysId):
    SysToken[SysId] = GenerateToken.Generate()
    return SysToken[SysId]

def getplayerfriends(username, accepted):
    friendslist = []
    friendsdict = {}
    if accepted == 1:
        Friends1 = Friends.query.filter_by(initiator = username, accepted = accepted).all()
        for i in range(len(Friends1)):
            record = Friends1[i]
            friendslist.append(record.recipient)
    Friends2 = Friends.query.filter_by(recipient = username, accepted = accepted).all()
    for i in range(len(Friends2)):
        record = Friends2[i]
        friendslist.append(record.initiator)
    for i in range(len(friendslist)):
        keyvalue = "Friend%s"%str(i+1)
        friendsdict[keyvalue] = friendslist[i]
    return friendsdict

def removeSystem(SysId):
    SysToken.pop(SysId)

def generateUrls(characters):
    urls = []
    for i in range(len(characters)):
        Url = "static/Assets/%s.png" %characters[i]
        urls.append(Url)
    return urls
if __name__ == "__main__":
    privatekey, publickey = pki.loadkeys()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("server-public-key.pem", "server-private-key.pem")
    eventlet.wsgi.server(
        eventlet.wrap_ssl(eventlet.listen(("0.0.0.0", 1111)),
                          certfile="server-public-key.pem",
                          keyfile="server-private-key.pem",
                          server_side=True), app)
