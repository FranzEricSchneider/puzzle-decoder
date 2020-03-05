import string

import checker
import data


def main():
	mapping = dict(zip(list(data.UNKNOWN), string.ascii_lowercase))
	checker.check_characters_with_image(mapping)

if __name__ == '__main__':
	main()
