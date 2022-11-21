from time import sleep

def hello_world(lang = 'en', sleep_time = 0.1):
    if lang == 'en':
        hi = "Hello World!"
    elif lang == 'fr':
        hi = "Bonjour le monde!"
    elif lang == 'se':
        hi = "Hej världen!"
    else:
       hi = "Hello World!"

    time.sleep(sleep_time)
    return hi


