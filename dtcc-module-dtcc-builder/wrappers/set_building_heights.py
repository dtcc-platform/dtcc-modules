#!/usr/bin/env python3

import subprocess
import tempfile
import os, sys, pathlib
import json

# project_dir = str(pathlib.Path(__file__).resolve().parents[1])
# sys.path.append(project_dir)

from core.run_in_shell import RunInShell
from core.logger import getLogger
logger = getLogger("dtcc-module-dtcc-builder")

class DtccCalcBuildingHeights(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            module="dtcc-module-dtcc-builder",
            tool="set-building-heights",
            publish=publish
        )


    def run_command(self, parameters:dict) -> str:
        """
        Pass in arguments based on the recived parameters if needed
        Otherwise just return the default shell command
        """
        data_dir = parameters.get("data_dir", None)
        if data_dir is None or not os.path.isdir(data_dir):
            raise Exception(f"Missing data directory: {data_dir}")
        logger.info(f"Running {self.tool} on data_dir: {data_dir}")
  
        shell_command = f"/dtcc-builder/bin/dtcc-build  --citymodel-only {data_dir}"
 
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
        data_dir = parameters.get("data_dir", None)
        if data_dir is None or not os.path.isdir(data_dir):
            return json.dumps({"data_url": "ERROR"})
        citymodel = os.path.join(data_dir, "CityModel.pb")
        if not os.path.isfile(citymodel):
            return json.dumps({"data_url": "ERROR"})
        return json.dumps({"data_url": citymodel})




if __name__ == "__main__":
    logger.info("Starting dtcc-module-hello-world")
    DtccCalcBuildingHeights(publish=True).listen()