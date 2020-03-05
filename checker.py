from collections import namedtuple
import cv2
import glob
import numpy

import data

# The maximum size each individual character can be
SHAPE = (90, 70, 3)
# The height to allow for cv2.putText
TEXT_BUFFER = 40
# The height to allow for each row of character + text
LINE_BUFFER = TEXT_BUFFER + 10
# Tracks the current spot where we are inserting characters
Cursor = namedtuple('Cursor', ['x', 'ymin', 'ymax'])


def main():
    check_images()
    check_character_number()
    check_characters_with_image()


def check_images():
    """Check that the images are within the size range for x and y"""
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
    assert unknown_set == data.UNKNOWN


def check_characters_with_image(mapping=None):
    """TODO: Explain."""

    # Note that in image space it goes (y, x), a.k.a. (vertical, horizontal)
    image = numpy.ones((70 * (SHAPE[0] + LINE_BUFFER), 30 * SHAPE[1], 3)) * 255
    cursor = Cursor(x=0, ymin=0, ymax=SHAPE[0])

    for character in data.CHARACTERS:

        # If we get a newline, update the cursor. If not, place a character
        if character in data.ASSUMED and data.ASSUMED[character] == "\n":
            # Zero the x position and bump the height down
            cursor = Cursor(x=0,
                            ymin=cursor.ymax + LINE_BUFFER,
                            ymax=cursor.ymax + LINE_BUFFER + SHAPE[0])

        else:
            # TODO: Explain
            character_image = cv2.imread(
                "images/image_{}.png".format(character)
            )

            # TODO: Explain
            character_y_edge = calculate_y_edge(cursor, character_image.shape)

            # Set the character image into the greater image
            # Note that images are (y, x), where y and x are in the human
            # expected frame
            image[character_y_edge:character_y_edge + character_image.shape[0],
                  cursor.x:cursor.x + character_image.shape[1],
                  :] = character_image

            # TODO: Explain
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
                # WTF - why is putText location now in (horizontal, vertical)?
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
