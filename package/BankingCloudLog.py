import yaml
import logging
import logging.config
from singleton_decorator import singleton

@singleton
class BankingCloudLog():

	def __init__(self):
		with open(r'.\scripts' + r'\package\config.yaml', 'r') as f:
			config = yaml.safe_load(f.read())
			logging.config.dictConfig(config)
		self.lg = logging.getLogger(__name__)
		self.lg.info('Log Configurations initiated')

