#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2015 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from pyannote.core import Unknown
from pyannote.core.matrix import LabelMatrix
from itertools import permutations
import numpy as np


def get_groundtruth_from_annotation(annotation):

    tracks = [(s, t) for (s, t) in annotation.itertracks()]
    data = np.zeros((len(tracks), len(tracks)), dtype=np.int)
    G = LabelMatrix(data=data, rows=tracks, columns=tracks)

    for ((s1, t1, l1), (s2, t2, l2)) in permutations(annotation.itertracks(label=True), 2):

        if isinstance(l1, Unknown) or isinstance(l2, Unknown):
            g = -1
        else:
            g = 1 if l1 == l2 else 0

        G[(s1, t1), (s2, t2)] = g

    return G
