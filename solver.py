#!/usr/bin/python3

import string

import data
import util


def main():
	mapping = dict(zip(list(data.UNKNOWN), string.ascii_lowercase))
	util.check_characters_with_image(data.CHARACTERS,
                                     data.ASSUMED,
                                     mapping)


if __name__ == '__main__':
	main()
