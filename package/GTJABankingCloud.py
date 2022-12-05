import os
from re import L, S
from package.BankingCloudBatch import BankingCloudBatch
import logging


class GTJABankingCloud(BankingCloudBatch):

	def __init__(self,cmd_path,config_file_path,script_path,ignore_error=False):
		self.lg = logging.getLogger(__name__)
		self.lg.info('GTJA Batch initisation')
		super().__init__(cmd_path,config_file_path,script_path,ignore_error=False)
		

	def do_nothing(self):
		pass
		