#!/usr/bin/env python3

import subprocess
import tempfile
import json
import os, sys, pathlib


project_dir = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.append(project_dir)

from pubsub_client.run_in_shell import RunInShell


class DtccBuilder(RunInShell):
    def __init__(self, publish=False) -> None:
        RunInShell.__init__(self, 
            module='dtcc-module-dtcc-builder',
            tool="build-citymodel", 
            publish=publish,
            shell_command="ls"
        )

    # Suggested new interface

    def run_command(self, message:dict):
        pass

    def process_input(self):
        self.data_directory = "/"
        # Read point cloud from .las
        # Write point cloud to .pb

    def process_output(self):
        pass

    # Old interface

    def process_arguments_on_start(self, message:dict):
        self.message = message
        if message['tool'] == 'build-citymodel':
            return f'dtcc-generate-citymodel {self.data_directory}'
        elif message['tool'] == 'build-mesh':
            return f'dtcc-generate-mesh {self.data_directory}'

    def process_return_data(self):
        # if self.message['command_name'] == 'build-citymodel':
        #     data = 'CityModel.pb'
        # elif self.message['command_name'] == 'build-mesh':
        #     data = 'CitySurface.pb'
        return json.dumps({"data": ""})


class DtccBuilderCityModel(RunInShell):
    def __init__(self, publish=False) -> None:
        RunInShell.__init__(self, 
            module='dtcc-module-dtcc-builder',
            tool="build-citymodel", 
            publish=publish,
            shell_command=""
        )

    def process_arguments_on_start(self, message:dict):
        self.message = message
        return f'dtcc-generate-citymodel {self.data_directory}'
      
    def process_return_data(self):
        data = 'CityModel.pb'
        return json.dumps({"data": data})

if __name__ == "__main__":
    import importlib, inspect
    file_path = pathlib.Path(__file__).resolve().__str__() + '.py'
    for name, cls in inspect.getmembers(importlib.import_module(file_path), inspect.isclass):
        print(name)
    # DtccBuilderCityModel(publish=True).listen()
