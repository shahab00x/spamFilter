from __future__ import division
from testSpamFilter import StripTags, testFilter
import os
import re
import shelve

def learn(root="spamFilter/user/"):
    # PROCESS SPAMS
    spams = []
    for filename in os.listdir(root + "spam/"):
        f = open(root+"spam/" + filename,"r+")
        spams.append(f.read())
        f.close()
    
    # Find out spams word frequency
    # start with an empty dictionary
    freqSpamWords = {}
    
    for m in spams :
        str1 = StripTags(m)
        
        #print "Original string:"
        #print str1
         
        #print
         
        # create a list of words separated at whitespaces
        wordList1 = re.findall(r'\w+',str1)
         
        # strip any punctuation marks and build modified word list
        # start with an empty list
        wordList2 = []
        for word1 in wordList1:
            # last character of each word
            lastchar = word1[-1:]
            # use a list of punctuation marks
            if lastchar in [",", ".", "!", "?", ";","'"]:
                word2 = word1.rstrip(lastchar)
            else:
                word2 = word1
            #word2 = re.findall(r'\w+',word1)
            # build a wordList of lower case modified words
            if len(word2) < 10:
                wordList2.append(word2.lower())
            
            # create a wordfrequency dictionary
        for word2 in wordList2:
            freqSpamWords[word2] = freqSpamWords.get(word2, 0) + 1
     
    #PROCESS HAMS
    hams = []
    for filename in os.listdir(root+"ham"):
        f2 = open(root+"ham/" + filename,"r+")
        hams.append(f2.read())
        f2.close()
        
    # Find out hams word frequency
    # start with an empty dictionary
    freqHamWords = {}
    
    for m in hams :
        str1 = StripTags(m)
        
        # create a list of words separated at whitespaces
        wordList1 = re.findall(r'\w+',str1)
         
        # strip any punctuation marks and build modified word list
        # start with an empty list
        wordList2 = []
        for word1 in wordList1:
            # last character of each word
            lastchar = word1[-1:]
            # use a list of punctuation marks
            if lastchar in [",", ".", "!", "?", ";","'"]:
                word2 = word1.rstrip(lastchar)
            else:
                word2 = word1
            #word2 = re.findall(r'\w+',word1)
            # build a wordList of lower case modified words
            if len(word2) < 10:
                wordList2.append(word2.lower())
            
            # create a wordfrequency dictionary
        for word2 in wordList2:
            freqHamWords[word2] = freqHamWords.get(word2, 0) + 1
    
    # create a list of keys and sort the list
    # all words are lower case already
    
    keyList1 = freqSpamWords.keys()
    keyList1.sort()
    
    keyList2 = freqHamWords.keys()
    keyList2.sort()
        
    total1 = 0
    total2 = 0
    
    myFile1 = open(root+"spamDict","w")
    myFile2 = open(root+"hamDict","w")
    
    for key1 in keyList1:
        myFile1.write( "%-10s %d" % (key1, freqSpamWords[key1]) + "\n")
        total1+= freqSpamWords[key1] 
    myFile1.close()
    
    for key2 in keyList2:
        myFile2.write( "%-10s %d" % (key2, freqHamWords[key2]) + "\n")
        total2+= freqHamWords[key2] 
    myFile2.close()
    
#    print "dictionary size for spam is {0}".format(len(freqSpamWords))
#    print "total spams are {0} and \"you\" is {1}".format(total1,freqSpamWords["you"])
#    print "the probability of the word \"you\" being a spam {0}".format(freqSpamWords["you"]/total1)
#    
#    print "dictionary size for ham is {0}".format(len(freqHamWords))
#    print "total hams are {0} and \"you\" is {1}".format(total2,freqHamWords["you"])
#    print "the probability of the word \"you\" being a ham {0}".format(freqHamWords["you"]/total2)
#    
    constant = (len(hams)+1)/(len(hams)+len(spams)+2)
    f  = shelve.open(root+"/db")
    f["pOfHam"] = constant
    f["lenHams"] = len(hams)
    f["lenSpams"] = len(spams)
    f.close()
    return constant
