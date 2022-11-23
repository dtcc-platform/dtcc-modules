#!/usr/bin/env python3

import subprocess
import tempfile
import os, sys, pathlib
import json

project_dir = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.append(project_dir)

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
            shell_command=""
        )
        self.message = {}
        
    def process_arguments_on_start(self, message:dict):
        self.output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.message = message
        self.tool = message.get('tool', 'hello-world')
        lang = message.get('lang', 'en')
        sleep_time = message.get('sleep_time', 0.1)
        logger.info(f"Running {self.tool} with lang={lang} and sleep_time={sleep_time}")
        if self.tool == "hello-world":
            return f"python3 dtcc_hello_world.py --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"
        elif self.tool == "hello-world-2":
            return f"python3 dtcc_hello_world.py --lang={lang} --sleep_time={sleep_time} --output-file={self.output_file.name}"

    def process_return_data(self):
        with open(self.output_file.name, 'r') as src:
            return_data = src.read()
        if self.tool == "hello-world-2":
            return_data += "from hello-world-2"
        os.remove(self.output_file.name)
        return json.dumps({"hello_world": return_data})


if __name__ == "__main__":
    logger.info("Starting dtcc-module-hello-world")
    DtccHelloWorld(publish=True).listen()
