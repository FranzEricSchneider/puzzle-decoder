import cv2
import glob

import data

SHAPE = (40, 40)


def main():
    check_images()
    check_character_number()
    # TODO: Write this one we have the images
    # show_output_image()


def check_images():
    """Check that the images are the right size"""
    for image_name in glob.glob("images/*.png"):
        image = cv2.imread(image_name)
        if image.shape != SHAPE:
            raise ValueError(
                "Image {} doesn't match desired shape {}".format(
                    image_name, SHAPE
                )
            )


def check_character_number():
    """Assert that our unknown characters can be explained by the alphabet."""
    complete_set = set(data.CHARACTERS)
    known_set = set(data.ASSUMED.keys())
    unknown_set = complete_set - known_set
    # We need 26 or fewer unknowns
    assert len(unknown_set) <= 26


if __name__ == '__main__':
    main()
