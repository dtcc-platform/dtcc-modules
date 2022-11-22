#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json

from pubsub_client.run_in_shell import RunInShell
from dtcc_hello_world import hello_world


class DtccBuilder(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self, 'dtcc-module-dtcc-builder', publish)

    def process_arguments_on_start(self, message:dict):
        self.message = message
        if message['command_name'] == 'build-citymodel':
            # FIXME: Need path to data directory (and the actual data...)
            return f'dtcc-generate-citymodel <path_to_data_directory>'

    def process_return_data(self):
        if self.message['command_name'] == 'build-citymodel':
            # FIXME: Need to store the data on the file server
            data = 'CityModel.pb'
        return json.dumps({"data": data})

if __name__ == "__main__":
    DtccBuilder(publish=True).listen()
