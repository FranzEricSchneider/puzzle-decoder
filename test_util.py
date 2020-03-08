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
    test_map_words()
    # test_display_key()
    test_get_ranked_keys()
    test_generate_random_key()


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
    # 40, 41, and 42 have assumed values
    characters = (1, 2, 3, 4, 22, 40, 41, 42)
    # Note that the key cannot map over ASSUMED characters
    assert util.map_words(
        characters=characters,
        key=((3, "a"), (4, "b"), (41, "c"))
    ) == (1, 2, "a", "b", "9", " ", ":", ",")


def test_map_words():
    words = ((1, 2, 3), (4, 5), (1, 2, 5, 6, 7, 8, 9, 10))

    assert util.map_words(
        words=words,
        key=((3, "a"), (4, "b"), (8, "c"))
    ) == ((1, 2, "a"), ("b", 5), (1, 2, 5, 6, 7, "c", 9, 10))

    assert util.map_words(
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


def test_display_key():
    print(util.display_key(data.SAMPLE_KEY, include_characters=True))
    print("\n==================\n")
    print(util.display_key(data.SAMPLE_KEY, include_characters=False))
    print("\n==================\n")
    print(util.display_key(data.SAMPLE_KEY, include_characters=False, score=1))


def test_get_ranked_keys():
    # Pretty simple, make sure we get a sorted list of the right length
    # Note that we want to call str() on a tuple (instead of writing a string)
    # because it will stringify things in the pythonic way (such as using ''
    # for internal strings) which I messed up once
    checked_keys = {
        str(((3, 'a'), (6, 'z'))): 0.15,
        str(((2, 'a'), (4, 'z'))): 0.5,
        str(((1, 'a'), (5, 'z'))): 0.75,
        str(((4, 'a'), (9, 'z'))): 0.0,
    }
    ranked_keys, scores = util.get_ranked_keys(checked_keys)
    assert ranked_keys == [str(((1, 'a'), (5, 'z')))]
    assert scores == [0.75]

    ranked_keys, scores = util.get_ranked_keys(checked_keys, number=3)
    assert ranked_keys == [str(((1, 'a'), (5, 'z'))),
                           str(((2, 'a'), (4, 'z'))),
                           str(((3, 'a'), (6, 'z')))]
    assert scores == [0.75, 0.5, 0.15]


def test_generate_random_key():
    RNG = util.sample_exponential()

    # Test that we get keys of the right length
    for length in range(5, 15):
        key = util.generate_random_key(RNG, {}, length)
        assert len(key) == length
        for pair in key:
            assert len(pair) == 2
            assert len(pair[1]) == 1
            assert isinstance(pair[0], int)
            assert isinstance(pair[1], str)

    # Assert that we (probably) have the most common letters
    key = util.generate_random_key(RNG, {}, 15)
    values = [pair[1] for pair in key]
    assert "e" in values
    assert "t" in values

    # Make a really common key and make sure we don't hit it
    checked_keys = {str(((4, 'e'), (16, 't'))): 0.5}
    for _ in range(int(1e3)):
        key = util.generate_random_key(RNG, checked_keys, 2)
        assert key != ((4, 'e'), (16, 't'))

    # Check a longer-than possible length
    key = util.generate_random_key(RNG, {}, 30)
    assert len(key) == len(data.UNKNOWN)


if __name__ == '__main__':
    main()
