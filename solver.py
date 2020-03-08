#!/usr/bin/python3

import argparse
import json

import data
import util


CHECKED_FILE = "checked_keys_dictionary.json"


def main():
    parser = argparse.ArgumentParser(
        description="Make new keys and examine the solve state",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-e", "--examine-results",
                        help="Examine the top N results",
                        action="store_true")
    parser.add_argument("-n", "--number-to-examine",
                        help="Number of results to examine",
                        type=int,
                        default=3)
    parser.add_argument("-w", "--show-words-only",
                        help="When examining results, show only the full words"
                             " that made up the score",
                        action="store_true")
    args = parser.parse_args()

    # Always start by checking the saved keys
    checked_keys = json.load(open(CHECKED_FILE, "r"))

    if args.examine_results:
        # Get the top N results
        ranked_keys, scores = \
            util.get_ranked_keys(checked_keys, number=args.number_to_examine)

        # And display them in a number of ways
        for key, score in zip(ranked_keys, scores):
            if args.show_words_only:
                print(util.get_english_words(key))
            else:
                print(util.display_key(key, score=score))
            print("")

    else:
        # Load the exponential RNG once
        RNG = util.sample_exponential()

        # Try a number of times
        for _ in range(int(1e6)):
            key = util.generate_random_key(RNG, checked_keys, 26)

            # Scores the key and adds it to the dictionary checked_keys
            mapped, score = util.check_key(checked_keys, data.WORD_SET, key)

        # Always end key production by writing the updated dictionary
        with open(CHECKED_FILE, "w") as file:
            json.dump(checked_keys, file)


if __name__ == "__main__":
	main()
