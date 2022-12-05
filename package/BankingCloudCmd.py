import subprocess
import os
import logging

'''
Run upload and download files
'''

class BankingCloudCmd:

    def __init__(self,cmdLinePath):
        self.cmdLinePath = cmdLinePath
        self.lg = logging.getLogger(__name__)

    def uploadData(self):
        result = []
        cmd = 'bccl saas upload-folder'
        self.lg.info('Start file upload via CMD ' + str(cmd))

        p = subprocess.Popen(cmd,
                             cwd=self.cmdLinePath,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE )
        for line in p.stdout:
            result.append(line.decode())
        errcode= p.returncode
        self.lg.info('Command Line Output') 
        if errcode is not None:
            self.lg.error('Hit Error in Uploading files.Check Logs')
            for  line in result:
                self.lg.error('Command Line Output with Error:' + str(line))
            raise Exception ('Upload Failed. See above for debugging')
        for line in result:
            self.lg.info('Command Line Output:' + str(line)) #put to debug later
        self.lg.info('Finished file upload via CMD')


    def downloadData(self,projectId):
        result = []
        cmd = 'bccl saas download-reports-zip --project-id=' + str(projectId)
        self.lg.info('Start Report File Download via CMD ' + str(cmd))
        p = subprocess.Popen(cmd,
                             cwd=self.cmdLinePath,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE )
        for line in p.stdout:
            result.append(line.decode())
        errcode= p.returncode
        self.lg.info('Command Line Output') 
        if errcode is not None:
            self.lg.error('Hit Error in Download files.Check Logs')
            for  line in result:
                self.lg.error('Command Line Output with Error:' + str(line))
            raise Exception ('Report Download Failed. See above for debugging')
        for line in result:
            self.lg.info('Command Line Output:' + str(line)) #put to debug later
        self.lg.info('Finished Report Download via CMD')
