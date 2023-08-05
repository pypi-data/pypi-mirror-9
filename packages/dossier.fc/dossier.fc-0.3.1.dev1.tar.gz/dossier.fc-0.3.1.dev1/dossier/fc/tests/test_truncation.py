'''dossier.fc Feature Collections

.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.

'''
from __future__ import absolute_import, division, print_function
from collections import Counter
from operator import itemgetter

from dossier.fc.tests import counter_type  # noqa


def test_truncation(counter_type):  # noqa
    num = 100
    data = {str(x): x+1 for x in xrange(num)}

    counter = counter_type(data)
    assert len(counter) == num

    truncation_length = 10
    counter.truncate_most_common(truncation_length)
    assert len(counter) == truncation_length

    most_common = Counter(data).most_common(truncation_length)
    from_counter = map(itemgetter(1), counter.most_common(truncation_length))
    expected = map(itemgetter(1), most_common)
    from_counter = map(abs, from_counter)
    assert from_counter == expected

    assert set(counter_type(dict(most_common)).items()) == set(counter.items())

    should_be_counter = counter_type({str(x): x+1 for x in xrange(90, 100)})
    assert should_be_counter == counter
