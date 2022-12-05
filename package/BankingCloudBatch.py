from ast import Try
import os
from re import L, S
from package.ConfigurationReader import ConfigurationReader
from package.BankingCloudAPI import BankingCloudAPI
from package.BankingCloudUser import BankingCloudUser
from package.BankingCloudCmd import BankingCloudCmd
from datetime import datetime
import time
import logging

class BankingCloudBatch:

	def __init__(self,cmd_path,config_file_path,script_path,ignore_error=False):
		self.lg = logging.getLogger(__name__)
		self.cmd_path = cmd_path
		self.config_file_path = config_file_path
		self.bc_config = self.read_config()
		self.bc_api = self.init_bc()
		self.bc_cmd = self.init_cmd()
		self.closing_date = None
		self.company = None
		self.ignore_error = ignore_error


	def extractUserInfo(self):
		userInfo = {'client_id': self.bc_config['wso2.id'] , \
                'username': self.bc_config['wso2.username'], \
                'password': self.bc_config['wso2.password'], \
                'secret': self.bc_config['wso2.secret'], \
                'grantType': self.bc_config['wso2.grantType'] }
		self.lg.debug('Obtained User Informat ion' + str(userInfo))
		return userInfo

	def read_config(self):
		config = ConfigurationReader(self.config_file_path).allConfigurations
		self.lg.info('BCCL Configurations read')
		return config

	def init_bc(self):
		bc_user = BankingCloudUser(self.extractUserInfo())
		bc_api = BankingCloudAPI(bc_user)
		return bc_api

	def init_cmd(self):
		bc_cmd = BankingCloudCmd(self.cmd_path)
		return bc_cmd

	def upload_to_s3(self):
		self.lg.info('Start Upload files to Banking Cloud Data Lake')
		self.bc_cmd.uploadData()
		self.lg.info('Completion of Upload files to Banking Cloud Data Lake')

	def configure_batch(self,closing_date, company):
		self.closing_date = closing_date
		self.company = company

	def autocatalog(self):
		dataFilesDir = self.bc_config['s3.source'] + r'\\' + self.company + r'\\' + self.closing_date
		self.lg.debug('The target S3 Source folder is ' + str(dataFilesDir))
		bcDir= r'/' + self.company + r'/' + self.closing_date
		filesList = [bcDir + r'/' + f for f in os.listdir(dataFilesDir)]
		autocatalog_param= {'data_source':'input-datasource',
                 'files':filesList}
		self.lg.info('Start AutoCatalog')
		self.lg.debug('Running AutoCatalog with params ' + str(filesList))
		#result = self.bc_api.post(BankingCloudAPI.autoCatalog,postParams)
		result = self.bc_api.request(BankingCloudAPI.autoCatalog,autocatalog_param)
		self.lg.info(f'Completion of AutoCatalog with status Code result["status"]')
		self.lg.debug('The request return ' + str(result))
		catalogResults = result['body']['catalogedFiles']
		errorFiles = result['body']['errorFiles']
		for file in catalogResults:
			self.lg.info('Successfully catalog files ' + file['file'] + ',' + file['schema'] + ',' + file['company'] + ',' + file['closingDate'])
		if  errorFiles:
			self.lg.error('One or more file(s) failed autocatalog process. Check logs')
			for file in errorFiles:
				self.lg.error('Failed to catalog following files ' + file['file'] )
			if not self.ignore_error:
				raise Exception('Error in catalogging files. One more moe files failed')
		if  result['status'] != 200:
			self.lg.error('Error in  catalog files ' + file['file'] )
			raise Exception('Error in catalogging files due to invalidate status code')

	def monitor_project(self,project_name):
		status_param = {'project' : project_name}
		#result = self.bc_api.get(BankingCloudAPI.getProjectStatus,status_param)
		result = self.bc_api.request(BankingCloudAPI.getProjectStatus,status_param)
		if result['status'] == 200:
			self.lg.info('Monitor Project return Succesfully!')
		else:
			self.lg.error(f'Error in requesting for Project Status for project {project_name}')
			raise Exception('Failed to obtain project status for project {project_name}')
		project_status = result['body'][0] # its a list so we get [0]
		self.lg.debug('Project ' + str(project_name) + ' with Status : ' + str(project_status))
		self.lg.info('Project ' + str(project_name) + ' with Status : ' + project_status['status'])

		if not project_status['choices']:
			self.lg.info('Still Running. No further action available')
		else:
			choices =  project_status['choices']
			for options in choices:
				self.lg.info(f'Project Completion! {project_name}+  with available Action as {options["action"]}')
		return project_status

	def start_project(self):
		t = datetime.now() 
		t = t.strftime('%Y%m%d%H%M')
		closing_date_str = datetime.strptime(self.closing_date, '%Y%m%d').strftime('%Y-%m-%d')
		project_name='api-py-' + t #projectName ='api-py-202211160137'
		self.lg.info('Starting project ' + project_name + ' with company ' + str(self.company) + ' and closing date ' + str(self.closing_date))
		projectSetting={ 'project_name': project_name, \
		            'closing_date': closing_date_str, \
                'company': self.company, \
                'collection_name': r'[2022.35.1] SACCR BCBS GTJA mapping', \
				'project_scope': 'CALCULATION'
        }
		#result = self.bc_api.post(BankingCloudAPI.startProject,projectSetting)
		result = self.bc_api.request(BankingCloudAPI.startProject,projectSetting)
		if result['status'] == 200:
			self.lg.info('Project Launched Succesfully!')
		else:
			self.lg.error('Project Launched on Failure!')
		self.lg.info('Proceed to Project Monitoring for '  + str(project_name))
		# only return a project if valid status is returned
		time.sleep(60*3)
		project_status = self.monitor_project(project_name)
		return project_name
	
	def while_running(self,project_name,sleep_interval):
		trials = 1
		while True:
			project_status = self.monitor_project(project_name)
			self.lg.info(f'Enter into Project Waiting Phase for project {project_name}')
			trials += 1
			if project_status['status'] in ['PENDING','FAILED']:
				self.lg.info(f'Project Completion for project {project_name}. Exiting loop')
				break
			self.lg.info('Sleeping for a while. Project still running')
			time.sleep(sleep_interval)
			if trials >= 15: #avoid infinite loop
				project_status = self.monitor_project(project_name)
				if project_status['status'] in ['PREPARING','PROCESSING']:
					self.lg.error(f'Waiting loop for break anyway! Stop the Batch process. Adjust your sleep interval to fit a loop of 15')
					raise Exception('Inadequate Sleep interval configuration. Process still running after sleep loop completes')
				break
		return project_status['status']

	def run_project(self,sleep_interval=60*15):
		project_name = self.start_project()
		project_status = self.monitor_project(project_name)
		running = project_status['status'] in ['PREPARING','PROCESSING']
		trials =0
		cal_status = self.while_running(project_name,sleep_interval)
		if cal_status != 'PENDING':
			self.lg.debug('{project_name} failed with full status as ' + str(project_status))
			self.lg.error(f'{project_name} failed! Logon and check the project status')
			raise Exception(f'Failed Project execution for {project_name}  with company {self.company} and closing date {self.closing_date}')
		else:
			self.lg.info('Project {project_name} finished successfully ! ')

	def generate_report_zip(self,project_name):
		project_status = self.monitor_project(project_name)
		closing_date_str = datetime.strptime(self.closing_date, '%Y%m%d').strftime('%Y-%m-%d')
		if any(d['action'] == 'GENERATE_ZIP_REPORT' for d in project_status['choices']):
			genZipParams = {'project_name': project_name, \
						  'company': self.company, \
						  'closing_date': closing_date_str, \
						  'parameters':
						  {'reportZipFileFormat': 'xlsx-and-csv'}
				   }
			self.lg.info(f'Report Generation for project {project_name}')
			#genCall  = self.bc_api.put(BankingCloudAPI.generateZip,genZipParams)
			result = self.bc_api.request(BankingCloudAPI.generateZip,genZipParams)
			time.sleep(60*3)
			rep_status = self.while_running(project_name,60*15)
			if rep_status != 'PENDING':
				self.lg.debug('{project_name} report generation failed with full status as ' + str(project_status))
				self.lg.error(f'{project_name} report generation failed! Logon and check the project status')
				raise Exception(f'Failed Report Generaation for {project_name}  with company {self.company} and closing date {self.closing_date}')
			else:
				self.lg.info('Project {project_name} report generation finished successfully ! ')
	
	def download_report(self,project_name):
		project_status = self.monitor_project(project_name)
		project_id = project_status['project']['project_id']
		if project_status['statusDetails']=='REPORT_ZIP_GENERATION':
			self.lg.info(f'Downloading file to local directory')
			self.bc_cmd.downloadData(project_id)
			self.lg.info(f'Completed Downloading file to local directory')