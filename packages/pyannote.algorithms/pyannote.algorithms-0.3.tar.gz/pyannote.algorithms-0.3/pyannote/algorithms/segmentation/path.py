#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2012-2014 CNRS

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

from __future__ import unicode_literals


from ..classification.gmm import GMMUBMClassification

import numpy as np
from sklearn.mixture.gmm import log_multivariate_normal_density
from ..stats.llr import logsumexp

import networkx as nx


class OptimalPathSegmentation(object):

    def __init__(self,
                 alpha=1., min_duration=0, max_duration=np.inf,
                 n_components=8):

        super(OptimalPathSegmentation, self).__init__()
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.n_components = n_components
        self.alpha = alpha

    def _cohesion(self, segment, features):

        X = features.crop(segment)
        weights = self._gmmubm._adapt_ubm(X).weights_

        i0, n = features.sliding_window.segmentToRange(segment)
        lpr = self._lpr[i0:i0 + n, :]

        logprob = logsumexp(lpr + np.log(weights), axis=1)

        return np.sum(logprob)

    def _cohesion_matrix(self, features, input_segmentation):

        N = len(input_segmentation)
        cohesion = np.NaN * np.ones((N, N))

        for i, segment in enumerate(input_segmentation):
            print i, segment.start
            for j in range(i, N):
                segment = segment | input_segmentation[j]
                if segment.duration < self.min_duration or \
                   segment.duration > self.max_duration:
                    break
                cohesion[i, j] = self._cohesion(segment, features)

        return cohesion

    def _graph(self, cohesion, input_segmentation, features):

        g = nx.DiGraph()
        N = len(input_segmentation)
        n = len(features.data)
        for i, segment in enumerate(input_segmentation):
            for j in range(i, N):
                if np.isnan(cohesion[i, j]):
                    continue
                segment = segment | input_segmentation[j]
                weight = -cohesion[i, j] + self.alpha * np.log(n)
                g.add_edge(segment.start, segment.end, weight=weight)

        return g


    def apply(self, features, input_segmentation):

        for i, segment in enumerate(input_segmentation):
            pass


    def __call__(self, features, input_segmentation):

        X = features.data
        self._gmmubm = GMMUBMClassification(
            n_components=self.n_components,
            covariance_type='diag',
            sampling=1000, params='w')
        self._gmmubm._background = self._gmmubm._fit_background(X)

        self._lpr = log_multivariate_normal_density(
            X,
            self._gmmubm._background.means_,
            self._gmmubm._background.covars_,
            self._gmmubm._background.covariance_type)

        matrix = self._cohesion_matrix(features, input_segmentation)

        return matrix

