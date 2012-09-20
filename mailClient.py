from __future__ import division
# -*- coding: utf-8 -*-

"""The user interface for our app"""

# Import the compiled UI module
#from windowUi import Ui_MainWindow
import windowUi
import os,sys
import imaplib, re
import time
import multiprocessing
import threading
import glob
import sys
#import winsound
import email
import shelve
import shutil

# Import Qt modules

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from multiprocessing import freeze_support
from IPython.config.application import Application
from testSpamFilter import StripTags
from learn import learn
import testSpamFilter

class mythread(QThread):
    def __init__(self,lock, server, username, password, statusBar,listWidgetInbox,listWidgetSpam, textBoxInbox, textBoxSpam, d): # d is the original class, i.e. the 
        super(mythread,self).__init__(d)
        self.lock = lock
        self.server = server
        self.username = username
        self.password = password
        self.statusBar = statusBar
        self.listWidgetInbox = listWidgetInbox
        self.listWidgetSpam = listWidgetSpam
        self.textBoxInbox = textBoxInbox
        self.textBoxSpam = textBoxSpam
        self.d=d
        self.user = "spamFilter/user/"
        self.spamDict = {}
        self.hamDict = {}
        self.k = 1
        self.n = 3 # Determines the weight of user database
        
    def run(self):
        pOfHamLearned, pOfSpamLearned, hamDictLearned, spamDictLearned, hamWordFreqLearned, spamWordFreqLearned = self.g("spamFilter/")
        pOfHamUser, pOfSpamUser, hamDictUser, spamDictUser, hamWordFreqUser, spamWordFreqUser = self.g("spamFilter/user/")
        
#        print "whatev"
#        print pOfHamLearned, pOfSpamLearned, len(hamDictLearned), len(spamDictLearned), hamWordFreqLearned, spamWordFreqLearned
#        print pOfHamUser, pOfSpamUser, len(hamDictUser), len(spamDictUser), hamWordFreqUser, spamWordFreqUser
        self.f(self.lock, self.server, self.username, self.password, self.statusBar, self.listWidgetInbox, self.listWidgetSpam, self.textBoxInbox, self.textBoxSpam,
                pOfHamLearned, pOfSpamLearned, hamDictLearned, spamDictLearned, hamWordFreqLearned, spamWordFreqLearned,
                pOfHamUser, pOfSpamUser, hamDictUser, spamDictUser, hamWordFreqUser, spamWordFreqUser, self.d)

    def isHam(self, message, pOfHam, pOfSpam, hamDict, spamDict, totalWordFrequencyOfHams, totalWordFrequencyOfSpams):
        self.pOfHam = pOfHam
        self.pOfSpam = pOfSpam
        self.hamDict = hamDict
        self.spamDict = spamDict
        self.totalWordFrequencyOfHams = totalWordFrequencyOfHams
        self.totalWordFrequencyOfSpams = totalWordFrequencyOfSpams

        messageDict = {}
        
        messageDict.clear()
        str1 = testSpamFilter.StripTags(message)
        
        # create a list of words separated at whitespaces
        wordList1 = re.findall(r'\w+',str1)
        wordList2 = []
        for word1 in wordList1:
            # last character of each word
            lastchar = word1[-1:]
            # use a list of punctuation marks
            if lastchar in [",", ".", "!", "?", ";","'"]:
                word2 = word1.rstrip(lastchar)
            else:
                word2 = word1
            # build a wordList of lower case modified words
            if len(word2) < 10:
                wordList2.append(word2.lower())
            
        # create a wordfrequency dictionary
        for word2 in wordList2:
            messageDict[word2] = messageDict.get(word2, 0) + 1
    
        pOfMessageGivenSpam = 1
        pOfMessageGivenHam = 1
        countX = 0  # For hams
        countY = 0  # For spams
        normalizer = 1
        if len(self.hamDict) == 0 or len(self.spamDict) == 0: return 0.5,0.5
        for key in messageDict.keys():
            if not self.hamDict.has_key(key): countX  = 0
            else: countX = int(self.hamDict[key])
            
            if not self.spamDict.has_key(key): countY = 0
            else: countY = int(self.spamDict[key])
            
            normalizer *= ((countY +self.k)*(self.totalWordFrequencyOfHams +self.k*len(self.hamDict)))/((countX+self.k)*(self.totalWordFrequencyOfSpams + self.k*len(self.spamDict)))
            #print countY, countX,totalWordFrequencyOfHams +k*len(hamDict) ,totalWordFrequencyOfSpams + k*len(spamDict), normalizer
        print len(self.hamDict), len(self.spamDict),self.totalWordFrequencyOfHams, self.totalWordFrequencyOfSpams
#        print "normalizer"
#        print 1+normalizer,"   ", 1+1/normalizer
        
        pOfSpamGivenMessage = 1 / (1 + (1/normalizer)*self.pOfHam/self.pOfSpam)
        pOfHamGivenMessage = 1 / ( 1 + normalizer*self.pOfSpam/self.pOfHam)

        print "pOfHamGIvenMessage = {0}".format(pOfHamGivenMessage)
        print "pOfSpamGivenMessage = {0}".format(pOfSpamGivenMessage)

        return pOfHamGivenMessage, pOfSpamGivenMessage
            
    def g (self, root):
        spamDict = {}
        hamDict = {}
        
        if not os.path.exists(root + "spamDict"):
            if not os.path.exists(self.user):
                os.mkdir(self.user)
            if not os.path.exists(self.user + "ham/"):
                os.mkdir(self.user + "ham/")
            if not os.path.exists(self.user + "spam/"):
                os.mkdir(self.user + "spam/")
            for filename in os.listdir(self.user + "ham/"):
                os.remove(self.user + "ham/" + filename)
            for filename in os.listdir(self.user + "spam/"):
                os.remove(self.user + "spam/"+filename)
            from learn import learn
            self.statusBar.setText(r"Wait, I'm learning \.\.\.\.\.")
            learn(root)
            self.statusBar.setText("learned")
            
        for line in open(root + "spamDict","r+"):
            key, data = line.split()
            spamDict[key] = data
        
        for line in open(root + "hamDict","r+"):
            key, data = line.split()
            hamDict[key] = data
            
        self.k = 1   # For Laplacian smoothing
        temp = shelve.open(root + "db")
        print "db" , temp
        C = temp["pOfHam"]
#        lenHams = temp["lenHams"]
#        lenSpams = temp["lenSpams"]
#        total = lenHams + lenSpams
        temp.close()
        pOfHam = C #(C*total+self.k)/(total+self.k*2)
        pOfSpam = 1-C #((1-C)*total+self.k)/(total+self.k*2)
#        pOfSpam = (60+self.k)/(90+self.k*2)
#        pOfHam = (30+self.k)/(90+self.k*2)
        
        print "pOfHam, pOfSpam",pOfHam,pOfSpam
        sKeyList = spamDict.keys()
        sKeyList.sort()
        
        totalWordFrequencyOfSpams = 0
        for sKey in sKeyList:
            totalWordFrequencyOfSpams += int(spamDict[sKey])
        
        hKeyList = hamDict.keys()
        hKeyList.sort()
        
        totalWordFrequencyOfHams = 0
        for hKey in hKeyList:
            totalWordFrequencyOfHams += int(hamDict[hKey])
            
        return pOfHam, pOfSpam, hamDict, spamDict, totalWordFrequencyOfHams, totalWordFrequencyOfSpams
    
    def f (self,lock, server, username, password, statusBar, listWidgetInbox, listWidgetSpam, textBoxInbox, textBoxSpam, 
 pOfHamLearned, pOfSpamLearned, hamDictLearned, spamDictLearned, hamWordFreqLearned, spamWordFreqLearned,
 pOfHamUser, pOfSpamUser, hamDictUser, spamDictUser, hamWordFreqUser, spamWordFreqUser, d):
        print "f"  
        
        if not os.path.exists(self.user):
            os.makedirs(self.user)  
        
        if not os.path.exists(self.user + "ham"):
            os.makedirs(self.user + "ham")   
        
#        files = glob.glob(self.user + "user_inbox" + '/*')
#        for f in files:
#            os.remove(f)
    
        if not os.path.exists(self.user + "spam"):
            os.makedirs(self.user+"spam")
        
#        files = glob.glob(self.user+"user_spam" + '/*')
#        for f in files:
#            os.remove(f)
    
        conn = imaplib.IMAP4_SSL(server, 993)
        conn.login(username, password)
        
        statusBar.setText("Connected")
        print "Connected"
        unreadCount = re.search("UNSEEN (\d+)", conn.status("INBOX", "(UNSEEN)")[1][0]).group(1)
        
        conn.select()
        typ, data = conn.search(None, 'ALL')
        i = 0
        learn(self.user)
        if os.path.exists("spamFilter/user/"):
            if os.path.exists(self.user + "spam/"):
                for filename in os.listdir(self.user + "spam/"):
                    self.listWidgetSpam.addItem(str(filename))
                    i = max(int(filename),i)
            if os.path.exists(self.user + "ham/"):
                for filename in os.listdir(self.user + "ham/"):
                    self.listWidgetInbox.addItem(str(filename))
                    i = max(int(filename),i)
                      
        for num in data[0].split()[i:]:
            if d.disconnectFlag == True:
                self.statusBar.setText("Disconnected")
                print "Disconnected"
                break
            typ, data = conn.fetch(num, '(RFC822)')
            print num
            time.sleep(10)
            message = ""
            message = data[0][1]
            try:
                lock.lockForWrite()
                h1, s1 = self.isHam(message, pOfHamLearned, pOfSpamLearned, hamDictLearned, spamDictLearned, hamWordFreqLearned, spamWordFreqLearned)
                h2, s2 = self.isHam(message, pOfHamUser, pOfSpamUser, hamDictUser, spamDictUser, hamWordFreqUser, spamWordFreqUser)
                hBar = (h1 + (self.n-1)*h2)/self.n
                sBar = (s1 + (self.n-1)*s2)/self.n
                print "hBar,sBar",hBar, sBar
                if (hBar-sBar > 0) :
                    listWidgetInbox.addItem(str(num))
                    f = open(self.user + "ham/" + str(num),"w")
                    f.write(message)
                    f.close()
                else:
                    listWidgetSpam.addItem(str(num))
                    f = open(self.user + "spam/" + str(num),"w")
                    f.write(message)
                    f.close()
            finally:
                lock.unlock()
        conn.close()
        conn.logout()
        
class threadhandler(QThread):
    def __init__(self,d):
        super(threadhandler,self).__init__(d)
        self.d=d
    def run(self):
        self.h(self.d)
    def h(self,d):
        running=0
        run=0
        while d.ps!=len(d.inlinks):
            if d.stop==True:
                return
            for i in d.inlinks:
                if d.threads[d.inlinks.index(i)].isRunning()==True:
                    running=running+1
            if running!=d.concurrency and run<len(d.inlinks):
                d.threads[run].start()
                run=run+1
                
            running=0
            time.sleep(0.1)
        if d.stop==False:
            self.emit(SIGNAL("fin()"))
            
# Create a class for our main window
class Main(QMainWindow, windowUi.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # This is always the same
        self.setupUi(self)
        self.lock = QReadWriteLock()
        self.pushButtonDisconnect.setDisabled(True)
        self.connect(self.listWidgetInbox,SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"), self.listWidgetInbox_itemChanged)
        self.connect(self.listWidgetSpam,SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"), self.listWidgetSpam_itemChanged)
        self.disconnectFlag = True
        self.listWidgetSpam.setSortingEnabled(True)
        self.listWidgetInbox.setSortingEnabled(True)
                         
    @pyqtSlot()
    def listWidgetSpam_itemChanged(self, prev, current):
        #winsound.Beep(2000,100)
        i = self.listWidgetSpam.currentItem()
        if i == None: return
        i = i.text()
        f = open('spamFilter/user/spam/' + i, 'r') 
        rawString = f.read()
        message = email.message_from_string(rawString)
        myMessage = rawString
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                myMessage = part.get_payload()
                break
            
        f.close()
        self.textBoxSpam.setHtml(myMessage)
     
    @pyqtSlot()    
    def listWidgetInbox_itemChanged(self, prev, current):
        #winsound.Beep(2200,100)
        i = self.listWidgetInbox.currentItem()
        if i == None: return
        i = i.text()
        f =  open('spamFilter/user/ham/' + i,'r')
        rawString = f.read()
        message = email.message_from_string(rawString)
        myMessage = rawString
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                myMessage = part.get_payload()
                break
            
        f.close()
        self.textBoxInbox.setHtml(myMessage)
        
    @pyqtSignature("")
    def on_pushButtonCon_clicked(self):
        #winsound.Beep(2000,100)
        
        sys.stdout.flush()
        self.pushButtonCon.setDisabled(True)
        self.pushButtonDisconnect.setEnabled(True)
        self.disconnectFlag = False
        
        self.statusBar.setText("Connecting...")
        self.repaint()
        
        server = str(self.lineEditServer.text())
        username = str(self.lineEditUsername.text())
        password = str(self.lineEditPassword.text())
        
        self.textBoxInbox.setHtml("")
        print "th=mythread"
        self.th = mythread(self.lock, server, username, password, self.statusBar, self.listWidgetInbox, self.listWidgetSpam, self.textBoxInbox, self.textBoxSpam, self)
        print "th.start()"
        self.th.start()
        print "after th.start()"       
    
#"""

    @pyqtSignature("")
    def on_pushButtonDisconnect_clicked(self):
        self.disconnectFlag = True
        self.pushButtonCon.setEnabled(True)
        self.pushButtonDisconnect.setDisabled(True)
        self.th.terminate()
        while self.th.isRunning():
            pass
        #winsound.Beep(1800,100)
        self.statusBar.setText("Disconnected")
        
    @pyqtSignature("")
    def on_pushButtonPrevSpam_clicked(self):
        i = self.listWidgetSpam.currentRow()
        print i
        self.listWidgetSpam.setCurrentItem(self.listWidgetSpam.item(i-1))
        if self.listWidgetSpam.currentItem() == None : 
            self.pushButtonPrevSpam.setDisabled(True)
    @pyqtSignature("")
    def on_pushButtonNextSpam_clicked(self):
        i = self.listWidgetSpam.currentRow()
        print i
        self.listWidgetSpam.setCurrentItem(self.listWidgetSpam.item(i+1))
        if self.listWidgetSpam.currentItem() == None : 
            self.on_pushButtonNextSpam_clicked()
        self.pushButtonNextSpam.setEnabled(True)
    
    @pyqtSignature("")
    def on_pushButtonPrevHam_clicked(self):
        i = self.listWidgetInbox.currentRow()
        print i
        self.listWidgetInbox.setCurrentItem(self.listWidgetInbox.item(i-1))
        if self.listWidgetInbox.currentItem() == None :
            self.pushButtonPrevHam.setDisabled(True)
    @pyqtSignature("")
    def on_pushButtonNextHam_clicked(self):
        i = self.listWidgetInbox.currentRow()
        print i
        self.listWidgetInbox.setCurrentItem(self.listWidgetInbox.item(i+1))
        if self.listWidgetInbox.currentItem() == None : 
            self.on_pushButtonNextHam_clicked()
        self.pushButtonPrevHam.setEnabled(True)
    @pyqtSignature("")
    def on_pushButtonMarkAsSpam_clicked(self):
        i = self.listWidgetInbox.takeItem(self.listWidgetInbox.currentRow())
        text = i.text()
        shutil.move("spamFilter/user/ham/"+text,"spamFilter/user/spam/"+text)
        self.listWidgetSpam.addItem(i)
        learn("spamFilter/user/")
    @pyqtSignature("")
    def on_pushButtonNotSpam_clicked(self):
        i = self.listWidgetSpam.takeItem(self.listWidgetSpam.currentRow())
        text = i.text()
        shutil.move("spamFilter/user/spam/"+text, "spamFilter/user/ham/"+text)
        self.listWidgetInbox.addItem(i)
        learn("spamFilter/user/")
def main():
    # Again, this is boilerplate, it's going to be the same on
    # almost every app you write
    app = QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()




