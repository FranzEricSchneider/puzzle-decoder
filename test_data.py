#!/usr/bin/python3

import collections

import data


def main():
    test_english()
    test_character_number()
    test_words()
    test_keys()


def test_english():
    for word in ["she", "strode", "defiantly", "into", "the", "sky"]:
        assert data.is_english(word)

    for not_word in ["esmerylda", "waz", "mohst", "upzet", "whith", "nanogg"]:
        assert not data.is_english(not_word)

    for bad_word in data.BLACKLIST:
        assert not data.is_english(bad_word)


def test_character_number():
    """Assert that our unknown characters can be explained by the alphabet."""
    complete_set = set(data.CHARACTERS)
    known_set = set(data.ASSUMED.keys())
    unknown_set = complete_set - known_set
    # We need 26 or fewer unknowns
    assert len(unknown_set) <= 26
    # Assert that data.UNKNOWN was constructed the same way
    assert unknown_set == data.UNKNOWN


def test_words():
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

    # Assert that the frequency lists are sorted so that the largest frequency
    # items come first
    for freq, freq_list in [(data.CHARACTER_FREQ, data.CHARACTER_FREQ_LIST),
                            (data.SET_FREQ, data.SET_FREQ_LIST)]:
        for i in range(len(freq_list) - 1):
            assert freq[freq_list[i]] >= freq[freq_list[i + 1]]
    # Check the sorted dictionary list


def test_keys():
    mapping = dict(data.SAMPLE_KEY)
    assert len(mapping) == 6
    assert 2 in mapping



if __name__ == '__main__':
    main()
