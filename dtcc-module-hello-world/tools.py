#!/usr/bin/env python3

import subprocess
import tempfile
import os, sys, pathlib
import json

# project_dir = str(pathlib.Path(__file__).resolve().parents[1])
# sys.path.append(project_dir)

from pubsub_client.run_in_shell import RunInShell
from pubsub_client.logger import getLogger
logger = getLogger("dtcc-module-hello-world")

from dtcc_hello_world import hello_world


class DtccHelloWorld(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            module="dtcc-module-hello-world",
            tool="hello-world",
            publish=publish,
        )


    def run_command(self, parameters:dict) -> str:
        """
        Pass in arguments based on the recived parameters if needed
        Otherwise just return the original shell command
        """
        self.output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.tool = parameters.get('tool', 'hello-world')
        lang = parameters.get('lang', 'en')
        sleep_time = parameters.get('sleep_time', 0.1)
        logger.info(f"Running {self.tool} with lang={lang} and sleep_time={sleep_time}")
  
        shell_command = f"python3 dtcc_hello_world.py --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"
 
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
        parameters
        data_directory = self.local_file_handler.get_data_dir()
        # Read point cloud from .las
        # ....
        # Write point cloud to .pb
        # .....
        temp = tempfile.NamedTemporaryFile(suffix='.pb')
        temp.write("test content .....")

        ## copy to local / shared  storage
        input_file_path = self.local_file_handler.copy_to_shared_folder(source_file_path=temp.name)
        parameters['input_file_path'] = input_file_path

        temp.close()

        
   
    def process_output(self, parameters:dict) -> str:
        # Return path to the result extracted from stdout or parameters
        ## example: output = ",".join(self.stdout_storage[-3:])
        with open(self.output_file.name, 'r') as src:
            return_data = src.read()

        # print(parameters['input_file_path'])
 
        os.remove(self.output_file.name)
        return json.dumps({"hello_world": return_data})



class DtccHelloWorld2(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            module="dtcc-module-hello-world",
            tool="hello-world-2",
            publish=publish,
            shell_command=""
        )

    def run_command(self, parameters:dict) -> str:
        """
        Pass in arguments based on the recived parameters if needed
        Otherwise just return the original shell command
        """
        self.output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.parameters = parameters
        self.tool = parameters.get('tool', 'hello-world')
        lang = parameters.get('lang', 'en')
        sleep_time = parameters.get('sleep_time', 0.1)
        logger.info(f"Running {self.tool} with lang={lang} and sleep_time={sleep_time}")
        shell_command = f"python3 dtcc_hello_world.py --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"

        return shell_command
 
    def parse_stdout(self, line:str) :
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
    
    def process_input(self, parameters:dict) -> str:
        data_directory = self.local_file_handler.get_data_dir()
        # Read point cloud from .las
        # ....
        # Write point cloud to .pb
        # .....
        temp = tempfile.NamedTemporaryFile(suffix='.pb')
        temp.write("test content .....")

        ## copy to local / shared  storage
        input_file_path = self.local_file_handler.copy_to_shared_folder(source_file_path=temp.name)

        temp.close()

        return input_file_path
        
   
    def process_output(self, parameters:dict) -> str:
        # Return path to the result extracted from stdout or parameters
        ## example: output = ",".join(self.stdout_storage[-3:])
        with open(self.output_file.name, 'r') as src:
            return_data = src.read()

        return_data += "from hello-world-2"
        os.remove(self.output_file.name)
        return json.dumps({"hello_world": return_data})



if __name__ == "__main__":
    logger.info("Starting dtcc-module-hello-world")
    DtccHelloWorld(publish=True).listen()
