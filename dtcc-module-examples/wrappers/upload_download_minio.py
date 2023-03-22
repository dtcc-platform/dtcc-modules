#!/usr/bin/env python3

import subprocess
import tempfile
import os, sys, pathlib
import json

from core.run_in_shell import RunInShell
from core.pub_sub_base import PubSubBase
from core.logger import getLogger
from core.minio_service import MinioFileHandler
logger = getLogger("dtcc-module-dtcc-builder")

class DtccMinioExample(RunInShell,PubSubBase):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            module="dtcc-module-examples",
            tool="upload-download-minio",
            publish=publish
        )


    def run_command(self, parameters:dict) -> str:
        """
        Pass in arguments based on the recived parameters if needed
        Otherwise just return the default shell command
        """
        bucket_name = parameters.get("bucket_name", None)
        prefix = parameters.get("prefix", None)
        file_name = parameters.get("file_name", None)

        local_data_dir = self.local_file_handler.get_data_dir()
        os.makedirs(local_data_dir,exist_ok=True)

        if local_data_dir is None or not os.path.isdir(local_data_dir):
            raise Exception(f"Missing data directory: {local_data_dir}")

        file_info_objects = self.download_object(
            local_storage_path=local_data_dir,
            prefix=prefix,
            file_name=file_name,
            bucket_name=bucket_name
        )

        
  
        shell_command = f"touch {local_data_dir}/sample.txt"
 
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

        local_data_dir = self.local_file_handler.get_data_dir()

        data_file = os.path.join(local_data_dir, "sample.txt")
        if not os.path.isfile(data_file):
            return self.create_output(status="Error: File not available!")
        
        file_info = self.upload_file(file_path=data_file,prefix=prefix,bucket_name=bucket_name)

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
    DtccMinioExample(publish=True).listen()