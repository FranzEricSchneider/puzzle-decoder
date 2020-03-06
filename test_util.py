#!/usr/bin/python3

import collections
import glob
import json

import cv2
import numpy

import data
import util


def main():
    util.check_characters_with_image(data.CHARACTERS,
                                     data.ASSUMED,
                                     mapping=dict(data.SAMPLE_KEY))
    test_images()
    # test_exponential()
    test_check_key()
    test_map_characters()


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


def test_map_characters():
    words = ((1, 2, 3), (4, 5), (1, 2, 5, 6, 7, 8, 9, 10))

    assert util.map_characters(
        words=words,
        key=((3, "a"), (4, "b"), (8, "c"))
    ) == ((1, 2, "a"), ("b", 5), (1, 2, 5, 6, 7, "c", 9, 10))

    assert util.map_characters(
        words=words,
        key=((1, "y"), (5, "z"))
    ) == (("y", 2, 3), (4, "z"), ("y", 2, "z", 6, 7, 8, 9, 10))


def test_check_key():
    # thud
    checked_keys = {}
    words = ((33, 21, 4, 8), )
    key = ((33, "t"), (21, "h"), (4, "u"), (8, "d"))
    mapped, score = util.check_key(checked_keys, words, key)

    assert mapped == (("t", "h", "u", "d"), )
    assert isinstance(score, float)
    assert numpy.isclose(score, 1.0)
    assert checked_keys == {
        str(((33, "t"), (21, "h"), (4, "u"), (8, "d"))): 1.0,
    }
    json.dumps(checked_keys)

    # monstrous regiment
    words = ((33, 21, 4, 8, 15, 30, 21, 19, 8), (30, 2, 6, 13, 33, 2, 4, 15))
    key = ((33, "m"), (21, "o"), (4, "n"), (8, "s"), (15, "t"),
           (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))
    mapped, score = util.check_key(checked_keys, words, key)

    assert mapped == (("m", "o", "n", "s", "t", "r", "o", "u", "s"),
                      ("r", "e", "g", "i", "m", "e", "n", "t"))
    assert numpy.isclose(score, 1.0)
    assert checked_keys == {
        str(((33, "t"), (21, "h"), (4, "u"), (8, "d"))): 1.0,
        str(((33, "m"), (21, "o"), (4, "n"), (8, "s"), (15, "t"),
             (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))): 1.0,
    }
    json.dumps(checked_keys)

    # Same words, but taking out "o"
    key = ((33, "m"), (4, "n"), (8, "s"), (15, "t"),
           (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))
    mapped, score = util.check_key(checked_keys, words, key)

    assert mapped == (("m", 21, "n", "s", "t", "r", 21, "u", "s"),
                      ("r", "e", "g", "i", "m", "e", "n", "t"))
    assert numpy.isclose(score, 0.5)
    assert checked_keys == {
        str(((33, "t"), (21, "h"), (4, "u"), (8, "d"))): 1.0,
        str(((33, "m"), (21, "o"), (4, "n"), (8, "s"), (15, "t"),
             (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))): 1.0,
        str(((33, "m"), (4, "n"), (8, "s"), (15, "t"),
             (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))): 0.5,
    }
    json.dumps(checked_keys)

    # Same words, but taking out "t"
    # Also, wipe the checked_keys and assert it's not persistent
    checked_keys = {}
    key = ((33, "m"), (21, "o"), (4, "n"), (8, "s"),
           (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))
    mapped, score = util.check_key(checked_keys, words, key)

    assert mapped == (("m", "o", "n", "s", 15, "r", "o", "u", "s"),
                      ("r", "e", "g", "i", "m", "e", "n", 15))
    assert numpy.isclose(score, 0.0)
    assert checked_keys == {
        str(((33, "m"), (21, "o"), (4, "n"), (8, "s"),
             (30, "r"), (19, "u"), (2, "e"), (6, "g"), (13, "i"))): 0.0,
    }
    json.dumps(checked_keys)


if __name__ == '__main__':
    main()
