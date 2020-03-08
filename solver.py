#!/usr/bin/python3

import argparse
from ast import literal_eval
import json

import data
import util


# TODO: Load and write this to a non-git place, and initialize it with an empty
# dict if it doesn't exist
CHECKED_FILE = "checked_keys_dictionary.json"


def main():
    parser = argparse.ArgumentParser(
        description="Make new keys and examine the solve state",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-e", "--examine-results",
                        help="Examine the top N results",
                        action="store_true")
    parser.add_argument("-i", "--ipdb",
                        help="Open ipdb at end of script",
                        action="store_true")
    parser.add_argument("-o", "--output-best-guess",
                        help="Write out image of best guess",
                        action="store_true")
    parser.add_argument("-p", "--polish-key",
                        help="Pass in a key and we'll try to improve it")
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

    elif args.output_best_guess:
        util.check_characters_with_image(data.CHARACTERS,
                                         data.ASSUMED,
                                         mapping=dict(data.PRESUMED_ANSWER))

    else:
        # Load the exponential RNG once
        RNG = util.sample_exponential()

        if args.polish_key:
            util.polish_known_key(RNG=RNG,
                                  checked_keys=checked_keys,
                                  words=data.WORD_SET,
                                  key=literal_eval(args.polish_key))

        else:
            # Try a number of times
            for _ in range(int(1e4)):
                key = util.generate_random_key(RNG, checked_keys, 26)

                # Scores the key and adds it to the dictionary checked_keys
                mapped, score = util.check_key(checked_keys, data.WORD_SET, key)

        # Always end key production by writing the updated dictionary
        with open(CHECKED_FILE, "w") as file:
            json.dump(checked_keys, file)

    if args.ipdb:
        import ipdb; ipdb.set_trace()


if __name__ == "__main__":
	main()
