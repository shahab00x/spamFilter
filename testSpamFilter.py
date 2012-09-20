from __future__ import division
import os
import re
from addSignature import addSignature,test

#This function strips the html tags
def StripTags(text): 
    finished = 0 
    while not finished: 
        finished = 1 
        start = text.find("<") 
        if start >= 0: 
            stop = text[start:].find(">") 
            if stop >= 0: 
                text = text[:start] + text[start+stop+1:] 
                finished = 0 
    return text 

def testFilter(constant, root):
    spamDict = {}
    
    for line in open(root + "spamDict","r+"):
        key, data = line.split()
        spamDict[key] = data
    
    hamDict = {}
    
    for line in open(root + "hamDict","r+"):
        key, data = line.split()
        hamDict[key] = data
        
    k = 60   # For Laplacian smoothing
    totalMessages = addSignature()
    
    pOfSpam = ((1-constant)*totalMessages+k)/(totalMessages+k*2)
    pOfHam = (constant*totalMessages+k)/(totalMessages+k*2)
    print "pOfSpam = {0}".format(pOfSpam) , "pOfHam = {0}".format(pOfHam)
    pOfMessageGivenSpam = 0
    pOfMessageGivenHam = 0
    pOfSpamGivenMessage = 0
    pOfHamGivenMessage = 0
    
    numberOfActualSpams = 0
    numberOfSpamsGotRight = 0           # True Negative
    numberOfSpamsClassifiedAsHam = 0    # False Positive
    
    
    numberOfActualHams = 0              
    numberOfHamsGotRight = 0            # True Positive
    numberOfHamsClassifiedAsSpam = 0    # False Negative
    
    messageDict = {}
    
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
    
    messages = []
    for filename in os.listdir(test):
        f = open(test + filename,"r+")
        messages.append(f.read())
        f.close()
    
#    print "length of messages array {0}".format(len(messages))
    message =""
    for message in messages:
        messageDict.clear()
        str1 = StripTags(message)
        
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
        for key in messageDict.keys():
            if not hamDict.has_key(key): countX  = 0
            else: countX = int(hamDict[key])
            
            if not spamDict.has_key(key): countY = 0
            else: countY = int(spamDict[key])
            
            normalizer *= ((countY +k)*(totalWordFrequencyOfHams +k*len(hamDict)))/((countX+k)*(totalWordFrequencyOfSpams + k*len(spamDict)))
            #print countY, countX,totalWordFrequencyOfHams +k*len(hamDict) ,totalWordFrequencyOfSpams + k*len(spamDict), normalizer
        
#        print "normalizer", normalizer
#        print 1+normalizer,"   ", 1+1/normalizer
        
#        pOfSpamGivenMessage = 1 / (1 + (1/normalizer)*pOfSpam/pOfHam)
#        pOfHamGivenMessage = 1 / ( 1 + normalizer*pOfHam/pOfSpam)
        
        pOfSpamGivenMessage = 1 / (1 + (1/normalizer)*(pOfHam/pOfSpam))
        pOfHamGivenMessage = 1 / ( 1 + (normalizer*pOfSpam)/pOfHam)
        
#        print pOfSpamGivenMessage, "   " , pOfHamGivenMessage
        #print str1
        if pOfSpamGivenMessage > pOfHamGivenMessage :
            #print "[SPAM MESSAGE] " + message
            if "XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X" in message :
                numberOfActualSpams += 1
                numberOfSpamsGotRight += 1
                #print "right spam"
            else: 
                numberOfActualHams += 1
                numberOfHamsClassifiedAsSpam += 1
                #print "wrong spam"
        elif pOfSpamGivenMessage < pOfHamGivenMessage :
            if "XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X" in message :
                numberOfActualSpams += 1
                numberOfSpamsClassifiedAsHam += 1
                #print "wrong ham"
            else: 
    #            print "[HAM MESSAGE] " + message
                numberOfActualHams += 1
                numberOfHamsGotRight += 1
                #print "right ham"
        f.close()
    
#    print "Number of total actual spams {0}".format(numberOfActualSpams) # 
#    print "Number of total actual hams {0}".format(numberOfActualHams)   # 
#    print "Number of spams gotten right {0} , classified as ham {1}".format(numberOfSpamsGotRight,numberOfSpamsClassifiedAsHam)
#    print "Number of hams gotten right {0} , classified as spam {1}".format(numberOfHamsGotRight,numberOfHamsClassifiedAsSpam)
#    print "Percentage of spams gotten right {0} ".format(((numberOfSpamsGotRight+1) / (numberOfActualSpams +1))*100)
#    print "Percentage of hams gotten right {0}".format(((numberOfHamsGotRight+1) / (numberOfActualHams+1))*100)
    """ return (True positive, false positive, true negative, false negative)"""
    return (numberOfHamsGotRight, numberOfSpamsClassifiedAsHam, numberOfSpamsGotRight, numberOfHamsClassifiedAsSpam)
