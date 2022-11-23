#!/usr/bin/env python3

import subprocess
import tempfile
import os
import json

from pubsub_client.run_in_shell import RunInShell
from dtcc_hello_world import hello_world


class DtccHelloWorld(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            module="dtcc-module-hello-world",
            command="hello-world",
            publish=publish,
            shell_command=""
        )
        self.message = {}
        self.output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)

    def process_arguments_on_start(self, message:dict):
        self.message = message
        tool = message['tool']
        lang = message['lang']
        sleep_time = message['sleep_time']
        if tool == "hello-world":
            return f"python3 dtcc_hello_world.py --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"
        elif tool == "hello-world-2":
            return f"python3 dtcc_hello_world.py --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"

    def process_return_data(self):
        with open(self.output_file.name, 'r') as src:
            return_data = src.read()
        if self.message['tool'] == "hello-world-2":
            return_data += "from hello-world-2"
        os.remove(self.output_file.name)
        return json.dumps({"hello_world": return_data})


if __name__ == "__main__":
    DtccHelloWorld(publish=True).listen()
