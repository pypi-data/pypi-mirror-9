
import numpy as np
import itertools
from pyannote.core.matrix import LabelMatrix


class Prior(object):

    def __init__(self, neighbourhood=60., resolution=0.1):
        super(Prior, self).__init__()
        self.neighbourhood = neighbourhood
        self.resolution = resolution

    def _incrementIndicatorFunc(self, segment, reference, _if):
        i = (segment.start - reference.start) / self.resolution
        j = (segment.end - reference.start) / self.resolution
        _if[i:j] += 1

    # indicator function
    def _indicatorFunc(self, annotation, reference):

        n = reference.duration / self.resolution
        _if = np.zeros(n, dtype=float)

        for segment, _ in annotation.itertracks():
            self._incrementIndicatorFunc(segment, reference, _if)

        return _if

    def _fit(self, annotation):

        # TODO: remove 'Unknown' labels

        numMatches = np.zeros((self.n_ + 1, ), dtype=float)
        numComparisons = np.zeros((self.n_ + 1, ), dtype=float)

        reference = annotation.get_timeline().extent()
        N = int(reference.duration / self.resolution)

        _IF = self._indicatorFunc(annotation, reference)

        for label in annotation.labels():

            _if = self._indicatorFunc(annotation.subset([label]),
                                      reference)

            numMatches[0] += np.sum(_if * _if)
            numComparisons[0] += np.sum(_if * _IF)
            for delta in range(1, N):
                d = delta if delta < self.n_ else self.n_
                numMatches[d] += np.sum(_if[:-delta] * _if[delta:])
                numComparisons[d] += np.sum(_if[:-delta] * _IF[delta:])

        return numMatches, numComparisons

    def fit(self, annotations):

        self.n_ = int(self.neighbourhood / self.resolution)
        numMatches = np.zeros((self.n_ + 1, ), dtype=float)
        numComparisons = np.zeros((self.n_ + 1, ), dtype=float)

        for annotation in annotations:
            m, c = self._fit(annotation)
            numMatches += m
            numComparisons += c

        self.probability_ = numMatches / numComparisons

        return self

    def _apply(self, segment1, segment2):

        if (segment1 ^ segment2).duration > self.neighbourhood:
            return self.probability_[-1]

        range1 = xrange(int(segment1.start / self.resolution),
                        int(segment1.end / self.resolution))

        range2 = xrange(int(segment2.start / self.resolution),
                        int(segment2.end / self.resolution))

        numDelta = np.zeros((self.n_ + 1, ), dtype=float)
        for t1, t2 in itertools.product(range1, range2):
            delta = abs(t1 - t2)
            delta = delta if delta < self.n_ else self.n_
            numDelta[delta] += 1

        return np.average(self.probability_, weights=numDelta)

    def apply(self, annotation):
        tracks = list(annotation.itertracks())
        P = LabelMatrix(data=None, dtype=np.float, rows=tracks, columns=tracks)
        for st in tracks:
            for st_ in tracks:
                P[st, st_] = self._apply(st[0], st_[0])
        return P

    def _repr_png_(self):
        from pyannote.core.notebook import plt, _render
        fig, ax = plt.subplots()
        ax.plot(np.arange(0, self.neighbourhood, self.resolution),
                self.probability_[:-1], 'b')
        ax.plot([self.neighbourhood, 1.5 * self.neighbourhood],
                [self.probability_[-1], self.probability_[-1]],
                'b--')
        ax.set_ylim(0, 1)
        ax.set_xlabel(r"$\Delta t$")
        ax.set_ylabel(r"prior$(\Delta t)$")
        ax.set_title('Prior probability')
        data = _render(fig)
        return data
