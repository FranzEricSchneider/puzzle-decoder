#!/usr/bin/python3

import json

import data
import util


CHECKED_FILE = "checked_keys_dictionary.json"


def main():
    # Always start by checking the saved keys
    checked_keys = json.loads(CHECKED_FILE)

    # Always end by writing the updated list
    with open(CHECKED_FILE, 'w') as file:
        json.dump(checked_keys, file)

if __name__ == '__main__':
	main()
