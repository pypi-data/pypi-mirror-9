from __future__ import absolute_import
from __future__ import division
import uuid
import sys
import random
import string
import math


# Builds a doc of a certain size.
def build_doc(size):
    doc = {}
    n_attrs = 5

    for i in xrange(5):
        doc[uuid.uuid4()] = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in xrange(math.floor(size / n_attrs))
        )

    return doc
