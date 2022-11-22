#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json

from pubsub_client.run_in_shell import RunInShell


class DtccBuilder(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self, 'dtcc-module-dtcc-builder', publish)

    # Suggested new interface

    def run_command(self, message:dict):
        pass

    def process_input(self):
        pass

    def process_output(self):
        pass

    def process_arguments_on_start(self, message:dict):
        self.message = message
        # FIXME: Need path to data directory (and the actual data...)
        if message['command_name'] == 'build-citymodel':
            return f'dtcc-generate-citymodel <path_to_data_directory>'
        elif message['command_name'] == 'build-mesh':
            return f'dtcc-generate-mesh <path_to_data_directory>'

    def process_return_data(self):
        # FIXME: Need to store the data on the file server
        if self.message['command_name'] == 'build-citymodel':
            data = 'CityModel.pb'
        elif self.message['command_name'] == 'build-mesh':
            data = 'CitySurface.pb'
        return json.dumps({"data": data})

if __name__ == "__main__":
    DtccBuilder(publish=True).listen()
