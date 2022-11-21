from dtcc_hello_world import hello_world

def start(data = {}, config = {}):
    lang = config['lang']
    sleep_time = config['sleep_time']
    hi = hello_world(lang, sleep_time)
    return {"hello_world": hi}
