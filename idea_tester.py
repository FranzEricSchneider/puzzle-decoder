#!/usr/bin/python3

import json
import time

import numpy


# I don't know if this is exactly the data structure we'll end up with, but
# it's approximately right
def populate(number):
    values = []
    for i in range(int(number)):
        values.append(
            tuple(tuple(A)
                  for A in numpy.random.randint(low=0, high=100, size=(26, 2)))
        )
    return values


# Is it fastest to check if A in B for a list, set, or dict? The items will
# be tuple pairs up to 26 long and there could be a lot

# RESULTS:
# Structure list took 0.55261 seconds to search A in B over 1500 times where
#   each key is of shape (26, 2) and the structure is of length 10000
# Structure dict took 0.00043 seconds to search A in B over 1500 times where
#   each key is of shape (26, 2) and the structure is of length 10000
# Structure set took 0.00044 seconds to search A in B over 1500 times where
#   each key is of shape (26, 2) and the structure is of length 10000

# ANSWER:
# Use a dict or a set, dict may be more functional to store an associated score
def test_if_a_in_b():

    value_list = populate(1e4)
    value_dict = {value: numpy.random.random() for value in value_list}
    value_set = set(value_list)

    # Get a set of test values that's got some breadth but isn't huge. Include
    # some that are in there
    test_values = list(populate(10)) + value_list[100:105]
    repeat = 100

    for structure, values in (("list", value_list),
                              ("dict", value_dict),
                              ("set", value_set),
                              ):
        start = time.time()
        for i in range(repeat):
            for test_value in test_values:
                if test_value in values:
                    pass
        end = time.time()
        print("Structure {} took {:.5f} seconds to search A in B over {} times"
              " where each key is of shape {} and the structure is of"
              " length {}".format(structure,
                                  end - start,
                                  repeat * len(test_values),
                                  numpy.array(test_values[0]).shape,
                                  len(values)
                                  ))


# Can you json.dumps a set or dict?

# RESULTS
# Cannot dumps set
# {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}

# ANSWER
# Worked for dictionary, not set. Weird! I would have thought they'd both work
# since they're both hashable structures. The keys of a dictionary feel a lot
# like a set
def test_json_dumps():
    try:
        print(json.dumps(set([1, 2, 3, 4, 5])))
    except TypeError:
        print("Cannot dumps set")
    try:
        print(json.dumps(dict({1:1, 2:2, 3:3, 4:4, 5:5})))
    except TypeError:
        print("Cannot dumps dict")


def main():
    # TODO: Add an argparse disabling or enabling tests?
    # test_if_a_in_b()
    # test_json_dumps()
    pass


if __name__ == '__main__':
    main()
