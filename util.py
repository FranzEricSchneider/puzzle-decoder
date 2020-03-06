import numpy

def sample_exponential():
    """
    Generator to get exponential samples. Done in batches because the random
    generator is a lot faster per sample that way, compared to one call per
    sample.

    Values are scaled to be *mostly* from 0.0 to 1.0, and then ones over 1.0
    are remove so we get an approximate 1/x distribution, but capped at 1.0
    """
    while True:
        batch = numpy.random.exponential(scale=0.2, size=int(1e4))
        for value in batch:
            if value <= 1.0:
                yield value
