import shutil
import os
import io,sys
#class flushfile(io.TextIOWrapper):
#    def __init__(self, f):
#        self.f = f
#    def write(self, x):
#        self.f.write(x)
#        self.f.flush()
#sys.stdout = flushfile(sys.stdout)

test = "spamFilter/test/"
testSpams = "spamFilter/testSpams/"
testHams = "spamFilter/testHams/"

def addSignature():    
    count = 0    
    if os.path.exists(test):
        for filename in os.listdir(test):
            os.remove(test+filename)
        os.removedirs(test)
    
    os.mkdir(test)
    
    for filename in os.listdir(testSpams):
        f = open(testSpams + filename,"r")
        g = open(test+filename,"w")
        g.write(f.read()+"\n XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X")
        g.close()
        f.close()
        count += 1
    
    for filename in os.listdir(testHams):
        shutil.copyfile(testHams+filename, test+filename)
        count += 1
    return count