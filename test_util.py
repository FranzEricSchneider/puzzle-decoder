import collections
import cv2
import glob

import data
import util


def main():
    util.check_characters_with_image(data.CHARACTERS, data.ASSUMED)
    test_images()
    test_exponential()


def test_images():
    """Check that the images are within the size range."""
    for image_name in glob.glob("images/*.png"):
        image = cv2.imread(image_name)
        if image.shape[0] > util.SHAPE[0] or image.shape[1] > util.SHAPE[1]:
            raise ValueError(
                "Image {} too big: {} > {}".format(
                    image_name, image.shape, util.SHAPE
                )
            )
        if image.shape[2] != 3:
            raise ValueError(
                "Image {} is not in color image format".format(image_name)
            )


def test_exponential():
    # Check that if we take enough samples we get the structure we want
    samples = []
    for _, sample in zip(range(int(1e4)), util.sample_exponential()):
        samples.append(int(round(sample * 5.0)))

    # Check that we have all of (and only) the expected values
    for key in [0, 1, 2, 3, 4, 5]:
        assert key in samples
    assert len(set(samples)) == 6

    # Check the order
    counted = collections.Counter(samples)
    for key in [0, 1, 2, 3, 4, 5]:
        count = counted[key]
        del counted[key]
        for lesser_count in counted.values():
            assert count > lesser_count


if __name__ == '__main__':
    main()
