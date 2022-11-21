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

    sleep(sleep_time)
    return hi


if __name__ == "__main__":
    import argparse 
    parser = argparse.ArgumentParser(description='Hello World')
    parser.add_argument('--lang', type=str, default='en', help='Language')
    parser.add_argument('--sleep_time', type=float, default=0.1, help='Sleep time')
    args = parser.parse_args()
    print(hello_world(args.lang, args.sleep_time))
