#!/usr/bin/python3

import json

import data
import util


CHECKED_FILE = "checked_keys_dictionary.json"


def main():
    # Always start by checking the saved keys
    checked_keys = json.load(open(CHECKED_FILE, "r"))
    # And loading the exponential RNG
    RNG = util.sample_exponential()

    # key = data.SAMPLE_KEY
    for _ in range(1000):
        key = util.generate_random_key(RNG, checked_keys, 26)

        # Scores the key and adds it to the dictionary checked_keys
        mapped, score = util.check_key(checked_keys, data.WORD_SET, key)

    # Always end by writing the updated list
    with open(CHECKED_FILE, "w") as file:
        json.dump(checked_keys, file)


if __name__ == "__main__":
	main()
