import collections
import cv2
import numpy


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
