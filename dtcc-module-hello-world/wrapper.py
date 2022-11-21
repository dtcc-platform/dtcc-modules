#!/usr/bin/env python3

import subprocess
import tempfile
import os

from pubsub_client.run_in_shell import RunInShell
from dtcc_hello_world import hello_world


class DtccHelloWorld(RunInShell):
    def __init__(self, publish=True) -> None:
        RunInShell.__init__(self,
            task_name="run_dtcc_hello_world",
            publish=publish,
            shell_command="python3 dtcc_hello_world.py"
        )
        self.output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)

    def process_arguments_on_start(self, message:dict):
        lang = message['lang']
        sleep_time = message['sleep_time']
        return f"{self.shell_command} --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"

    def process_return_data(self):
        with open(self.output_file.name, 'r') as src:
            return_data = src.read()
        os.remove(self.output_file.name)
        return return_data

if __name__ == "__main__":
    dtcc_hello_world = DtccHelloWorld(publish=True)
    dtcc_hello_world.start()
