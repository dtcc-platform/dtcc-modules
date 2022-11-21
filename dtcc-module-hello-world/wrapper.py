import subprocess

from dtcc_hello_world import hello_world


def start(command, data = {}, config = {}):
    if command == "hello-world":
        lang = config['lang']
        sleep_time = config['sleep_time']
        hi = hello_world(lang, sleep_time)
        return {"hello_world": hi}
    if command == "hello-world-cli":
        lang = config['lang']
        sleep_time = config['sleep_time']
        hi = subprocess.check_output(["dtcc-hello-world", "--lang", lang, "--sleep_time", str(sleep_time)])
        return {"hello_world": hi}

    else:
        return {"error": "Command not found"}