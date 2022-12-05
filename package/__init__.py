from .ConfigurationReader import ConfigurationReader
import os

if __name__ == "__main__":
    
    configurationsPath="C:\software\bccl-202215.01.09-RELEASE\saas"
    configurationsFile="configuration.properties"

    reader = ConfigurationReader(os.path.join(configurationsPath,configurationsFile))
    reader.parseConfiguration()
    print(reader.returnKey("wso2.url"))



    


