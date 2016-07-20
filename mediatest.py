import os
from functools import partial
from multiprocessing import Pool
import time
import shutil
import sys

##smurtlogging
##find the suite that failed
##look in the log following the suite name
##for ever FAIL, pull FAIL line and the line previous to it.
##repeat for all suites, all iterations

def parseLog(iterationOfLoop):
    breakString = " tests -"
    parsedLog = []
    with open("runLog%i.log" % (iterationOfLoop), "r") as file:
        text = file.readlines()
        for line in range(len(text) - 1, -1, -1):
            if (text[line][0:6] == "Total:"):
                for appLine in range(line, len(text)):
                    parsedLog.append(text[appLine])
    lenParsedLog = len(parsedLog)
    line = 0
    while line < lenParsedLog:
        if "FAIL SUITE: suite_" in parsedLog[line]:
            stringList = parsedLog[line].split()
            suiteName = stringList[len(stringList)-1]
            print suiteName
            runLogLine = 0
            for i in range(runLogLine,len(text)):
                runLogLine += 1
                if suiteName in text[i]:
                    break
            while runLogLine < len(text):
                if breakString in text[runLogLine]:
                    runLogLine += 1
                    break
                elif "FAIL test_" in text[runLogLine]:
                    parsedLog.insert(line+1,"\t \t%s" % text[runLogLine])
                    parsedLog.insert(line+1,"\t \t%s" % text[runLogLine-1])
                    runLogLine += 1
                    lenParsedLog = len(parsedLog)
                else:
                    runLogLine +=1
        line += 1
    completeLog = open("ParsedLog%i.log" % iterationOfLoop, "w+")
    for line in parsedLog:
        completeLog.write(line)


def runWinTest(pictureList,videoList,iterationOfLoop):
    if os.path.exists("TestNum%i" % iterationOfLoop):
        shutil.copy2("gpsdk_jakarta_unittest.exe", "TestNum%i" % iterationOfLoop)
    else:
        os.makedirs("TestNum%i" % iterationOfLoop)
        shutil.copy2("gpsdk_jakarta_unittest.exe", "TestNum%i" % iterationOfLoop)

    if iterationOfLoop >= len(pictureList):
        shutil.copy(pictureList[0], "TestNum%i\\tmp.jpg" % iterationOfLoop)
        pictID = 0
    else:
        shutil.copy(pictureList[iterationOfLoop], "TestNum%i\\tmp.jpg" % iterationOfLoop)
        pictID = iterationOfLoop
    if iterationOfLoop >= len(videoList):
        shutil.copy(videoList[0], "TestNum%i\\tmp.mp4" % iterationOfLoop)
        videoID = 0
    else:
        shutil.copy(videoList[iterationOfLoop], "TestNum%i\\tmp.mp4" % iterationOfLoop)
        videoID = iterationOfLoop
    time.sleep(10)
    os.chdir("TestNum%i" % iterationOfLoop)
    time.sleep((((iterationOfLoop*2)/3)%10)+1)
    os.system("gpsdk_jakarta_unittest.exe -v -j qa -dcomp 511 -dlevel 555 > runLog%i.log 2>&1" % (iterationOfLoop))
    os.system("echo 'PID:%s TestNum%i completed using %s AND %s' >> runLog%i.log" % (os.getpid(), iterationOfLoop , videoList[videoID], pictureList[pictID], iterationOfLoop))
    parseLog(iterationOfLoop)
    os.chdir("..")
    return None


def runPosixTest(pictureList, videoList, iterationOfLoop):
    if os.path.exists("./TestNum%i" % iterationOfLoop):
        shutil.copy2("gpsdk_jakarta_unittest.exe", "TestNum%i" % iterationOfLoop)
    else:
        os.makedirs("TestNum%i" % iterationOfLoop)
        shutil.copy2("gpsdk_jakarta_unittest", "TestNum%i" % iterationOfLoop)

    if iterationOfLoop >= len(pictureList):
        shutil.copy(pictureList[0], "./TestNum%i/tmp.jpg" % iterationOfLoop)
        pictID = 0
    else:
        shutil.copy(pictureList[iterationOfLoop], "./TestNum%i/tmp.jpg" % iterationOfLoop)
        pictID = iterationOfLoop
    if iterationOfLoop >= len(videoList):
        shutil.copy(videoList[0], "./TestNum%i/tmp.mp4" % iterationOfLoop)
        videoID = 0
    else:
        shutil.copy(videoList[iterationOfLoop], "./TestNum%i/tmp.mp4" % iterationOfLoop)
        videoID = iterationOfLoop
    time.sleep(10)
    os.chdir("TestNum%i/" % iterationOfLoop)
    time.sleep((((iterationOfLoop*2)/3)%10)+1)
    os.system("./gpsdk_jakarta_unittest -v -j qa -dcomp 511 -dlevel 555 > runLog%i.log 2>&1" % (iterationOfLoop))
    os.system("echo 'PID:%s TestNum%i completed using %s AND %s' >> runLog%i.log" % (os.getpid(), iterationOfLoop , videoList[videoID], pictureList[pictID], iterationOfLoop))
    os.chdir("..")
    return None

class JDKLibTest():

    def appendList(self,pathtoMedia):
        pictureList = []
        videoList = []
        for root,dirs,files in os.walk(pathtoMedia):
            for file in files:
                if file.endswith(".MP4") or file.endswith(".TRV"):
                    videoList.append(os.path.join(root, file))
                if file.endswith(".JPG"):
                    pictureList.append(os.path.join(root, file))
        return pictureList, videoList

    def aggregatePosixLogs(self, listCount):
        self.parsedLog = []
        for i in range(0,listCount):
            with open("./TestNum%i/ParsedLog%i.log" % (i,i),"r") as file:
                text = file.readlines()
                for line in range(0,len(text)):
                    self.parsedLog.append(text[line])
            file.close()
        completeLog = open("AggregatedLog.log","w+")
        for line in self.parsedLog:
            completeLog.write(line)
        return completeLog

    def aggregateWinLogs(self, listCount):
        self.parsedLog = []
        for i in range(0,listCount):
            with open("TestNum%i\\ParsedLog%i.log" % (i,i),"r") as file:
                text = file.readlines()
                for line in range(0,len(text)):
                    self.parsedLog.append(text[line])
            file.close()
        completeLog = open("AggregatedLog.log","w+")
        for line in self.parsedLog:
            completeLog.write(line)
        return completeLog


    def test_runMediaTest(self):

        if (os.name == "posix"):
            pictureList, videoList = self.appendList("/zoidberg/CI/CAH_Recorded")
        else:
            pictureList, videoList = self.appendList("C:\Jenkins\workspace\CAH_Recorded")


        if len(pictureList) > len(videoList):
             listCount = len(pictureList)
        else:
             listCount = len(videoList)
        if(os.name == "posix"):
            func = partial(runPosixTest, pictureList, videoList)
        else:
            func = partial(runWinTest, pictureList, videoList)
        pool = Pool(processes=8)
        pool.map(func,range(0,listCount))
        pool.close()
        pool.join()
        if(os.name == "posix"):
            logFile = self.aggregatePosixLogs(listCount)
        else:
            logFile = self.aggregateWinLogs(listCount)
        logFile.seek(0)
        print logFile.read()
        logFile.seek(0)
        if "FAIL" in logFile.read():
            sys.exit(1)
        else:
            sys.exit(0)

if (__name__ == "__main__"):
    testWrapper = JDKLibTest()
    testWrapper.test_runMediaTest()