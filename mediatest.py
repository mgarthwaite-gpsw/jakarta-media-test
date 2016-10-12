import os
from functools import partial
from multiprocessing import Pool
import time
import shutil
import sys
import argparse


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
            runLogLine = 0
            for i in range(runLogLine,len(text)):
                runLogLine += 1
                if suiteName in text[i]:
                    break
            while runLogLine < len(text):
                if breakString in text[runLogLine]:
                    runLogLine += 1
                    break
                elif "FAIL " in text[runLogLine]:
                    parsedLog.insert(line+1,"\t \t%s" % text[runLogLine])
                    parsedLog.insert(line+1,"\t \t%s" % text[runLogLine-1])
                    runLogLine += 1
                    lenParsedLog = len(parsedLog)
                else:
                    runLogLine +=1
        line += 1
    shortLog = open("ParsedLog%i.log" % iterationOfLoop, "w+")
    for line in parsedLog:
        shortLog.write(line)
    shortLog.write("=====================================-----END OF TEST RUN----=================================================\n\n")
    shortLog.seek(0)
    print shortLog.read()
    shortLog.seek(0)
    shortLog.close()


def runTest(server, pictureList, videoList, iterationOfLoop):

    executable = "./gpsdk_jakarta_unittest"
    dirPath = "%s/TestNum%i" % (os.getcwd(), iterationOfLoop)

    if os.path.exists(dirPath):
        shutil.rmtree(dirPath)
    mp4Path = dirPath + "/tmp.mp4"
    jpgPath = dirPath + "/tmp.jpg"
    os.makedirs(dirPath)


    if iterationOfLoop >= len(pictureList):
        shutil.copy2(pictureList[0], jpgPath)
        pictID = 0
    else:
        shutil.copy2(pictureList[iterationOfLoop], jpgPath)
        pictID = iterationOfLoop
    if iterationOfLoop >= len(videoList):
        shutil.copy2(videoList[0], mp4Path)
        videoID = 0
    else:
        shutil.copy2(videoList[iterationOfLoop], mp4Path)
        videoID = iterationOfLoop
    shutil.copy2(executable, dirPath)
    time.sleep(10)
    os.chdir(dirPath)
    time.sleep((((iterationOfLoop*2)/3)%10)+1)
    os.system(executable + " -v -s suite_media2_complete_direct_s3_upload -j %s -dcomp 511 -dlevel 555 > runLog%i.log 2>&1" % (server,iterationOfLoop))
    os.system("echo 'PID:%s TestNum%i completed using %s AND %s' >> runLog%i.log" % (os.getpid(), iterationOfLoop , videoList[videoID], pictureList[pictID], iterationOfLoop))
    os.remove("tmp.mp4")
    os.remove("tmp.jpg")
    parseLog(iterationOfLoop)
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

    def aggregateLogs(self, listCount):
        self.parsedLog = []
        for i in range(0,listCount):
            logPath = "TestNum%i/ParsedLog%i.log" % (i,i)
            with open(logPath,"r") as file:
                text = file.readlines()
                for line in range(0,len(text)):
                    self.parsedLog.append(text[line])
            file.close()
        completeLog = open("AggregatedLog.log","w+")
        for line in self.parsedLog:
            completeLog.write(line)


        count = 0
        failID = 0
        for line in completeLog:
            count += line.count("FAIL SUITE: ")


        if count == 0:
            print "NO FAILED TESTS. GREEN"
            completeLog.write("NO FAILED TESTS. GREEN")
            failID = 0
        elif count > 0 and count < listCount:
            print "SOME FAILED TESTS. YELLOW"
            completeLog.write("SOME FAILED TESTS. YELLOW")
            failID = 1
        else:
            print "ALL TESTS FAILED. RED."
            completeLog.write("ALL TESTS FAILED. RED.")
            failID = 2

        return completeLog, failID

    def test_runMediaTest(self,server):
        #local use
        #/Users/mgarthwaite/Dropbox/CAH_Recorded
        #/zoidberg/CI/CAH_Recorded

        pictureList, videoList = self.appendList("/zoidberg/CI/CAH_Recorded")

        if len(pictureList) > len(videoList):
             listCount = len(pictureList)
        else:
             listCount = len(videoList)

        func = partial(runTest, server, pictureList, videoList)
        pool = Pool(processes=8)
        pool.map(func,range(0,listCount))
        pool.close()
        pool.join()


        logFile,failID = self.aggregateLogs(listCount)


        if failID == 2:
            sys.exit(0)
        elif failID == 1:
            sys.exit(0)
        else:
            sys.exit(0)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s ","--server", required=True)
    args = parser.parse_args()
    return args.server

if (__name__ == "__main__"):
    testWrapper = JDKLibTest()
    testWrapper.test_runMediaTest(parseArgs())