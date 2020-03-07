#!/usr/bin/python3

import collections
import cv2
import numpy

import data


# The maximum size each individual character can be
SHAPE = (90, 70, 3)
# The height to allow for cv2.putText
TEXT_BUFFER = 40
# The height to allow for each row of character + text
LINE_BUFFER = TEXT_BUFFER + 10
# Tracks the current spot where we are inserting characters
Cursor = collections.namedtuple('Cursor', ['x', 'ymin', 'ymax'])


def check_characters_with_image(characters, assumed, mapping=None):
    """
    Writes image of stored characters for visual checking. Each line of text is
    represented as
        1) A line of the cipher text
        2) Underneath it, our mapping of cipher to ascii (? by default)

    Arguments:
        mapping: None (in which case all non-assumed characters become "?") or
            a dictionary of {unknown character (int): ascii}, where the unknown
            characters are all stored as integers in CHARACTERS. Items in the
            mapping will be displayed as such under the sipher text.

    Returns nothing
    """

    # Note that in image space it goes (y, x), a.k.a. (vertical, horizontal)

    # First make a blank canvas to insert images into
    image = numpy.ones((70 * (SHAPE[0] + LINE_BUFFER), 30 * SHAPE[1], 3)) * 255
    # Make a cursor tracking the next position to add a character
    cursor = Cursor(x=0, ymin=0, ymax=SHAPE[0])

    # Add each character to the image
    for character in characters:

        # If we get a newline, update the cursor. If not, place a character
        if character in assumed and assumed[character] == "\n":
            # Zero the x position and bump the height down
            cursor = Cursor(x=0,
                            ymin=cursor.ymax + LINE_BUFFER,
                            ymax=cursor.ymax + LINE_BUFFER + SHAPE[0])

        else:
            # Load the image for this character. This is probably inefficient,
            # but since this function is meant for human inspection anyway the
            # possible lengths won't matter to a computer
            character_image = cv2.imread(
                "images/image_{}.png".format(character)
            )

            # Calculate where the image should be placed vertically so that it
            # will be centered on the cursor. The character images have
            # variable heights depending on the character shape
            character_y_edge = calculate_y_edge(cursor, character_image.shape)

            # Set the character image into the greater image
            # Note that images are (y, x), where x and y are in the human
            # expected frame
            image[character_y_edge:character_y_edge + character_image.shape[0],
                  cursor.x:cursor.x + character_image.shape[1],
                  :] = character_image

            # Figure out what we want to map cipher text to, this display it
            # underneath the cipher representation
            if character in assumed:
                text = assumed[character]
            else:
                if mapping and character in mapping:
                    text = mapping[character]
                else:
                    text = "?"
            cv2.putText(
                img=image,
                text=text,
                # WTF - why is putText location in (horizontal, vertical)?
                org=(cursor.x + character_image.shape[1] // 4,
                     cursor.ymax + TEXT_BUFFER),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.5,
                color=(0, 0, 0),
                thickness=2,
            )

            # Update the cursor
            cursor = Cursor(x=cursor.x + character_image.shape[1],
                            ymin=cursor.ymin,
                            ymax=cursor.ymax)

    # Figure out where we start hitting blank whitespace, and clip the image
    where = numpy.argwhere(image != (255, 255, 255))
    y_edge = max(where[:, 0]) + 20
    x_edge = max(where[:, 1]) + 20
    image = image[0:y_edge, 0:x_edge]

    # Write out the image
    cv2.imwrite("check_text_image.png", image)


def calculate_y_edge(cursor, shape):
    # Get the range and subtract the character size
    empty = (cursor.ymax - cursor.ymin) - shape[0]
    return cursor.ymin + int(empty / 2)


def sample_exponential():
    """
    Generator to get exponential samples. Done in batches because the random
    generator is a lot faster per sample that way, compared to one call per
    sample.

    Samples are scaled to be *mostly* from 0.0-1.0, and then samples over 1.0
    are remove so we get an approximate 1/x distribution, but capped at 1.0
    """
    while True:
        batch = numpy.random.exponential(scale=0.2, size=int(1e4))
        for value in batch:
            if value <= 1.0:
                yield value


def map_characters(characters, key):
    """
    Takes a tuple of characters and returns the same, but with swapped values,
    according to the given mapping AND to the assumed mapping in data.ASSUMED
    using whitespace, punctuation, and numbers

    Arguments:
        characters: tuple of ciphertext characters (integers)
        key: tuple of tuple pairs containing (cipher character, ascii). Does
            not need to map all 26 letters

    Returns:
        same structure as characters, but some or all of the cipher characters
        have been swapped for the ascii characters via key and data.ASSUMED
    """
    mapping = dict(key)
    new_characters = []
    for character in characters:
        if character in data.ASSUMED:
            new_characters.append(data.ASSUMED[character])
        elif character in mapping:
            new_characters.append(mapping[character])
        else:
            new_characters.append(character)
    return tuple(new_characters)


def map_words(words, key):
    """
    Takes a tuple of tuples and returns the same, but with swapped values,
    according to the given mapping

    Arguments:
        words: tuple of tuple of ciphertext characters (integers)
        key: tuple of tuple pairs containing (cipher character, ascii). Does
            not need to map all 26 letters

    Returns:
        same structure as words, but some or all of the cipher characters have
        been swapped for the ascii characters via key
    """
    mapping = dict(key)
    new_words = []
    for word in words:
        new_words.append(
            tuple([mapping[character] if character in mapping else character
                   for character in word])
        )
    return tuple(new_words)


def check_key(checked_keys, words, key):
    """
    Scores a given key by ranking the fraction of English in words created
    by the key, then stores that mapping in checked_keys.

    Arguments:
        checked_keys: dict, contains {tuple key: float score}
        words: see map_words
        key: see map_words

    Returns:
        mapped: see map_words return value
        score: float

    Note that the dictionary checked_keys is modified
    """

    # Switch characters we know we want to map
    mapped = map_words(words, key)

    # Calculate the score by the number of English words
    count = 0
    for word in mapped:
        try:
            string_word = "".join(word)
            if data.is_english(string_word):
                count += 1
        except TypeError:
            pass
    score = count / len(words)

    # Record the checked key and its score. Note that we have to set the keys
    # to be strings so we can jsonify them
    checked_keys[str(key)] = score

    return mapped, score


def display_key(key, include_characters=False):
    """Render a key onto the whole dataset."""
    mapped = list(map_characters(data.CHARACTERS, key))
    for idx in range(len(mapped)):
        if not isinstance(mapped[idx], str):
            removed = mapped.pop(idx)
            if include_characters:
                mapped.insert(idx, ".{}.".format(removed))
            else:
                mapped.insert(idx, "?")

    # Do some visual formatting in the include_characters case
    joined = "".join(mapped)
    if include_characters:
        joined = joined.replace("..", ".")
        joined = joined.replace(" .", " ").replace(". ", " ")
        joined = joined.replace(" ", "   ")

    return "{}\n".format(key) + joined


RankedKey = collections.namedtuple('RankedKey', ['key', 'score'])


def get_ranked_keys(checked_keys, number=1):
    """
    Get the top N ranked keys from a dictionary.

    Arguments:
        checked_keys: a dictionary of keys and scores, as from
            checked_keys_dictionary.json
        number: number of ranked scores we want to extract

    Returns:
        A tuple of (list of ranked keys, list of corresponding scores)
    """
    assert number >= 1
    ranked_keys = [RankedKey(key=None, score=0.0)] * number

    for key, score in checked_keys.items():
        # If the current score is greater than the least score in the ranked
        # list, then replace that least score and then resort the list.
        if score > ranked_keys[-1].score:
            ranked_keys[-1] = RankedKey(key, score)
            ranked_keys = sorted(ranked_keys,
                                 key=lambda x: x.score,
                                 reverse=True)

    return ([key.key for key in ranked_keys],
            [key.score for key in ranked_keys])
