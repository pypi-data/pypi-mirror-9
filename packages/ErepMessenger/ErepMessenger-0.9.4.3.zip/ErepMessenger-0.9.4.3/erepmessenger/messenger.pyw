from Tkinter import *
import tkMessageBox
import requests
from bs4 import BeautifulSoup
import ConfigParser
import time
import re
import os
import json

#------------------------------------------------------------------------------------------------

def showLogin():
    global mLogin
    if eToken is not None:
        if mmToken == "1":
            tkMessageBox.showinfo("Attention!", "You are already logged into Erepublik!")
    else:
        mLogin=Toplevel()
        mLogin.tk.call('wm', 'iconphoto', mLogin._w, icon)
        mLogin.title("Login to Erepublik")
        mLogin.geometry('225x125+600+400')
        mLogin.lift()
        Label(mLogin,text='Email:').grid(row=0,column=0,sticky=E)
        Label(mLogin,text='Password:').grid(row=1,column=0,sticky=E)
        Entry(mLogin,textvariable=eEmail).grid(row=0,column=1,sticky=W)
        Entry(mLogin,textvariable=ePassword).grid(row=1,column=1,sticky=W)
        Button(mLogin,text="Login to Erepublik",command=eLogin).grid(row=2,column=1,sticky=W)
        
#------------------------------------------------------------------------------------------------
        
def eLogin():
    global mLogin
    global eToken
    global eRep
    global mmToken
    formdata = {'citizen_email': eEmail.get(), 'citizen_password': ePassword.get(), "remember": '1', 'commit': 'Login'}
    erepLogin = eRep.post('http://www.erepublik.com/en/login',data=formdata,allow_redirects=False)
    if erepLogin.status_code==302:
        mLogin.destroy()
        r = eRep.get('http://www.erepublik.com/en')        
        soup = BeautifulSoup(r.text)
        scripts = soup.find_all("script")
        script = unicode.join(u'\n',map(unicode,scripts))
        regex = re.compile("csrfToken\s*:\s*\'([a-z0-9]+)\'")
        toke = regex.findall(script)
        eToken = toke[0]
        mmToken = "1"
    else:
        tkMessageBox.showerror("Attention!", "Login Failed!", parent=mLogin)
        return
        
#------------------------------------------------------------------------------------------------
        
def sendPM(citizen,subject,message):
    global eRep
    eHeaders = {
        'Referer': 'http://www.erepublik.com/en/main/messages-compose/'+citizen,
        'X-Requested-With': 'XMLHttpRequest'}

    sendmessage = {
        '_token': eToken,
        'citizen_name': citizen,
        'citizen_subject': subject,
        'citizen_message': message}
    
    erepMess = eRep.post('http://www.erepublik.com/en/main/messages-compose/'+citizen,data=sendmessage,headers=eHeaders,allow_redirects=False)
    return

#------------------------------------------------------------------------------------------------

def mmSend():
    global eMes
    global resultText
    global citizen
    error = 0
    if mmToken == "1":
        if len(idList.get(1.0,END)) == 0:
            tkMessageBox.showerror("Attention!", "Make sure all info is complete before trying to send your messages!", parent=mGui)
            error = 1
        if len(sub.get()) == 0:
            tkMessageBox.showerror("Attention!", "Make sure all info is complete before trying to send your messages!", parent=mGui)
            error = 1
        if len(mess.get(1.0,END)) == 0:
            tkMessageBox.showerror("Attention!", "Make sure all info is complete before trying to send your messages!", parent=mGui)
            error = 1
        if len(mess.get(1.0,END)) > 2000:
            tkMessageBox.showerror("Attention!", "Your message cannot be more than 2000 characters long! It is currently "+str(len(mess.get(1.0,END)))+" characters long.", parent=mGui)
            error = 1
        if error == 0:
            mResults=Toplevel()
            mResults.tk.call('wm', 'iconphoto', mResults._w, icon)
            mResults.title("MM Results")
            mResults.geometry('400x125+600+400')
            resultFrame = Frame(mResults)
            resultFrame.pack(side=LEFT)
            resultText = Text(resultFrame)
            resultText.pack(side=LEFT, fill=Y)
            resultScroll = Scrollbar(resultFrame)
            resultScroll.pack(side=RIGHT, fill=Y)
            resultScroll.config(command=resultText.yview)
            resultText.config(yscrollcommand=resultScroll.set)
            mResults.lift()
            if "," in idList.get(1.0,END):
                list = idList.get(1.0,END).split(',')
                print list
            else:
                list = idList.get(1.0,END).splitlines()
                print list
            
            for mId in list:
                citizen = mId.strip()
                message = mess.get(1.0,END)
                if message.find("[name]") != -1:
                    r = requests.get("https://www.kimonolabs.com/api/ondemand/6gm5u8b2?apikey=z2FM7xXXZhucmYhX0Ub4CsySLCV2U57e&kimpath4=" + citizen)
                    data = r.content
                    result = json.loads(data)
                    message = message.replace("[name]",result['results']['profile'][0]['name'])
                    sendPM(citizen,sub.get(),message)
                    time.sleep(1)
                    resultText.insert(END, "Message sent to "+citizen+"("+result['results']['profile'][0]['name']+")\n")
                else:
                    sendPM(citizen,sub.get(),message)
                    time.sleep(1)
                    resultText.insert(END, "Message sent to "+citizen+" ([name] not used)\n")
                resultText.see(END)
                resultText.update_idletasks()
    else:
        tkMessageBox.showerror("Attention!", "Press \"Start\" to login before using the messenger!", parent=mGui)

#------------------------------------------------------------------------------------------------

global eToken
global mmToken
global eRep
global eMes
global idList
global sub
global mess
global icon
eRep = requests.Session()
eMes = requests.Session()
defHeaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36'}
eRep.headers=defHeaders
mesHeaders = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive', 'User-Agent': 'eMes/MO'}
eMes.headers=mesHeaders
mGui = Tk()
eToken = None
eEmail = StringVar()
ePassword = StringVar()
mmToken = '0'
mmID = StringVar()
mmPass = StringVar()
config = ConfigParser.ConfigParser()
scriptDirectory = os.path.dirname(os.path.realpath(__file__))
settingsFilePath = os.path.join(scriptDirectory, "config.cfg")
config.readfp(open(settingsFilePath))
eEmail.set(config.get('User','erepEmail'))
ePassword.set(config.get('User','erepPass'))

menubar = Menu(mGui)
menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=menu)
menu.add_command(label="Start", command=showLogin)
menu.add_command(label="Exit", command=mGui.quit)
mGui.config(menu=menubar)
leftFrame = Frame(mGui)
leftFrame.grid(row=0, column=0)
rightFrame = Frame(mGui)
rightFrame.grid(row=0, column=1)
#ID List box
Label(leftFrame, text="Citizen IDs:").pack(side="top")
scrollid = Scrollbar(leftFrame)
scrollid.pack(side="right", fill="y", expand=False)
idList = Text(leftFrame, height=28, width=15, wrap=WORD, yscrollcommand=scrollid.set)
idList.pack(side="left", fill="both", expand=True)
scrollid.config(command=idList.yview)
#Subject box
Label(rightFrame, text="Subject:").grid(row=0,column=0, sticky=W)
sub = Entry(rightFrame, width=39)
sub.grid(row=1,column=0)
#Message box
Label(rightFrame, text="Message:").grid(row=2,column=0, sticky=W)
scrollMes = Scrollbar(rightFrame)
scrollMes.grid(row=3,column=1,sticky="N,S,W")
mess = Text(rightFrame, height=23,width=44, wrap=WORD, yscrollcommand=scrollMes.set)
mess.grid(row=3,column=0, sticky=W)
scrollMes.config(command=mess.yview)
#Send button
Button(rightFrame, text="Send",command=mmSend).grid(row=4,column=0, sticky=E)

mGui.geometry('525x500+200+100')
mGui.minsize(525,500)
mGui.title("Erepublik Messenger")
iconPath = os.path.join(scriptDirectory, "messenger.gif")
icon = PhotoImage(file=iconPath)
mGui.tk.call('wm', 'iconphoto', mGui._w, icon)
currversion = "0.9.4.3"
vercheck = eRep.get('https://pypi.python.org/pypi/ErepMessenger')        
versoup = BeautifulSoup(vercheck.text)
newversion = versoup.find('title')
if newversion.renderContents() != "ErepMessenger "+currversion+" : Python Package Index":
    mUpdate=Toplevel()
    mUpdate.tk.call('wm', 'iconphoto', mUpdate._w, icon)
    mUpdate.title("New Version Available")
    mUpdate.geometry('400x125+600+400')
    updateText = Text(mUpdate)
    updateText.pack(side=LEFT, fill=Y)
    updateText.insert(END, "Go to:\nhttps://pypi.python.org/pypi/ErepMessenger\nand update ASAP!")
    mUpdate.lift(aboveThis=mGui)
mGui.mainloop()
