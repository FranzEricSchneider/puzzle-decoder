import collections
import cv2
import glob
import numpy

import data


# TODO: Change this into a test file, maybe splitting into multiple

# The maximum size each individual character can be
SHAPE = (90, 70, 3)
# The height to allow for cv2.putText
TEXT_BUFFER = 40
# The height to allow for each row of character + text
LINE_BUFFER = TEXT_BUFFER + 10
# Tracks the current spot where we are inserting characters
Cursor = collections.namedtuple('Cursor', ['x', 'ymin', 'ymax'])


def main():
    check_images()
    check_character_number()
    check_words()
    check_characters_with_image()


def check_images():
    """Check that the images are within the size range."""
    for image_name in glob.glob("images/*.png"):
        image = cv2.imread(image_name)
        if image.shape[0] > SHAPE[0] or image.shape[1] > SHAPE[1]:
            raise ValueError(
                "Image {} too big: {} > {}".format(
                    image_name, image.shape, SHAPE
                )
            )
        if image.shape[2] != 3:
            raise ValueError(
                "Image {} is not in color image format".format(image_name)
            )


def check_character_number():
    """Assert that our unknown characters can be explained by the alphabet."""
    complete_set = set(data.CHARACTERS)
    known_set = set(data.ASSUMED.keys())
    unknown_set = complete_set - known_set
    # We need 26 or fewer unknowns
    assert len(unknown_set) <= 26
    # Assert that data.UNKNOWN was constructed the same way
    assert unknown_set == data.UNKNOWN


def check_words():
    # Check basic types
    assert isinstance(data.WORDS, tuple)
    for word in data.WORDS:
        assert isinstance(word, tuple)
        for character in word:
            assert isinstance(character, int)

    # Give some basic length and value constraints
    assert len(data.WORDS) > 100
    for word in data.WORDS:
        assert len(word) >= 1
        for character in word:
            assert character < 40
            assert character not in data.ASSUMED

    # Check some basic properties of the set
    assert isinstance(data.WORD_SET, set)
    for word in data.WORD_SET:
        assert isinstance(word, tuple)
        assert word in data.WORDS
    for word in data.WORDS:
        assert word in data.WORD_SET

    # Check the frequency dictionaries
    for freq in [data.CHARACTER_FREQ, data.SET_FREQ]:
        assert isinstance(freq, collections.Counter)
        for character in freq:
            assert character not in data.ASSUMED
            assert character in data.CHARACTERS
    assert sum(data.CHARACTER_FREQ.values()) > sum(data.SET_FREQ.values())


def check_characters_with_image(mapping=None):
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
    for character in data.CHARACTERS:

        # If we get a newline, update the cursor. If not, place a character
        if character in data.ASSUMED and data.ASSUMED[character] == "\n":
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
            if character in data.ASSUMED:
                text = data.ASSUMED[character]
            else:
                if mapping:
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


if __name__ == '__main__':
    main()
