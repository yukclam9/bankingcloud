import os
from package.ConfigurationReader import ConfigurationReader
from package.BankingCloudAPI import BankingCloudAPI
from package.BankingCloudUser import BankingCloudUser
from package.BankingCloudCmd import BankingCloudCmd
from package.GTJABankingCloud import GTJABankingCloud
from package.BankingCloudLog import BankingCloudLog
import logging
if __name__ == "__main__":

    configurations_path= r'C:\TEMP\moodys\bccl-202215.01.09-RELEASE\saas'
    configurations_file= r'configuration.properties'
    cmd_path= r'C:\TEMP\moodys\bccl-202215.01.09-RELEASE'
    config_file_path=os.path.join(configurations_path,configurations_file)
    script_path=r'C:\Users\LamC1\OneDrive - moodys.com\Precision\Task\GTJA\api\bankingcloud'
    os.chdir(cmd_path)

    BankingCloudLog()
    lg = logging.getLogger(__name__)

    batch = GTJABankingCloud(cmd_path,config_file_path,script_path)
    lg.info('Running Upload To S3')
    batch.upload_to_s3()
    batch.configure_batch(closing_date='20221028',company='GTJAI')
    lg.info('Running Autocatalog')
    batch.autocatalog()
    lg.info('Running Project')
    project_name = batch.run_project()
    project_name='api-py-202212051257'
    lg.info('Running Report Generation')
    batch.generate_report_zip(project_name)
    lg.info('Running Download Report')
    batch.download_report(project_name)
    lg.info('Batch Completed')
    

   
    

    

    

    
    

    
        
                        
                        
    
    

    


