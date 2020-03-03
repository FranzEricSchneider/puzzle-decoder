import cv2
import glob

import data

SHAPE = (90, 70, 3)


def main():
    check_images()
    check_character_number()
    # TODO: Write this one we have the images
    # show_output_image()


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


if __name__ == '__main__':
    main()
