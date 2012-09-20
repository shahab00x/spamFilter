from __future__ import division
from learn import learn
from testSpamFilter import testFilter
from time import clock

def l(f,*args):
    t0 = clock()
    r = f(*args)
    print clock() - t0
    return r
    
constant = l(learn,"spamFilter/")
tp,fp,tn,fn = l(testFilter, constant, "spamFilter/")
# true positive rate (tpr)
tpr = tp/(tp+fn)
# false positive rate (fpr)
fpr = fp/(fp+tn)

print "True Positive = {0} \nFalse Negative = {1} \nTrue Negative = {2} \nFalse Positive = {3}\n".format(tp,fn,tn,fp)
print "accuracy = ", (tp+tn)/(tp+tn + fp+fn)
print "learn complete\n\n\n"
