#!/usr/bin/env python3

import os, sys, pathlib, json, time

from core.run_in_shell import RunInShell
from core.pub_sub_base import PubSubBase
from core.logger import getLogger
from core.minio_service import MinioFileHandler
logger = getLogger("dtcc-module-dtcc-builder")

class DtccCitySolarIrradiance(RunInShell,PubSubBase):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            module="dtcc-module-citysolar",
            tool="irradiance",
            publish=publish
        )
        self.local_data_dir = self.local_file_handler.get_data_dir()
        self.output_file_name = os.path.join(self.local_data_dir, "results.txt")
        os.makedirs(self.local_data_dir,exist_ok=True)

    def run_command(self, parameters:dict) -> str:
        """
        Pass in arguments based on the recived parameters if needed
        Otherwise just return the default shell command
        """
        bucket_name = parameters.get("bucket_name", None)
        prefix = parameters.get("prefix", None)
        file_name = parameters.get("file_name", None)

        if self.local_data_dir is None or not os.path.isdir(self.local_data_dir):
            raise Exception(f"Missing data directory: {self.local_data_dir}")

        file_info_objects = self.download_object(
            local_storage_path=self.local_data_dir,
            prefix=prefix,
            file_name=file_name,
            bucket_name=bucket_name
        )
        inputfile_path = os.path.join(self.local_data_dir, file_name)
        latitude = parameters.get("latitude", None)
        longitude = parameters.get("longitude", None)
        date = parameters.get("date", None)

        ## Optional: --latitude {latitude} --longitude {longitude} --one_date {date}

        shell_command = f"python3 -m citysolar.run_solar --display False --inputfile '{inputfile_path}' --exportpath '{self.output_file_name}' " 

        return shell_command
 
    def parse_stdout(self, line:str):
        """
        Parse to the stdout line to extract 
        1) progress percentage
        2) log level
        3) clean message
        """
        percent = 10
        loglevel = "info"
        message = line
        return percent, loglevel, message
    
    def process_input(self, parameters:dict) -> None:
        pass

        
    def process_output(self, parameters:dict) -> str:
        bucket_name = parameters.get("bucket_name", None)
        prefix = parameters.get("prefix", None)
        file_name = parameters.get("file_name", None)
        
        wait_for_file = 5
        for n in range(wait_for_file):
            if not os.path.isfile(self.output_file_name):
                if n == wait_for_file-1:
                    return self.create_output(status="Error: File not available!")
            else:
                break
            time.sleep(10)
        
        file_info = self.upload_file(file_path=self.output_file_name,prefix=prefix,bucket_name=bucket_name)

        return self.create_output(status="Success: File available", bucket_name=bucket_name, prefix=prefix, file_name=file_info.file_name )


    def create_output(self,status:str, bucket_name="", prefix="", file_name=""):
        return json.dumps({
            "status": status,
            "bucket_name":bucket_name,
            "prefix":prefix,
            "file_name": file_name
        })



if __name__ == "__main__":
    logger.info("Starting dtcc-module-exmaples")
    DtccCitySolarIrradiance(publish=True).listen()