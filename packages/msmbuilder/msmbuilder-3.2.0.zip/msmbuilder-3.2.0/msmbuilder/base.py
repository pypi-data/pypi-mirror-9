from __future__ import print_function, absolute_import, division

from sklearn.base import BaseEstimator as SklearnBaseEstimator


class BaseEstimator(SklearnBaseEstimator):
    # http://msmbuilder-mixtape.s3-website-us-west-1.amazonaws.com/latest/apipatterns.html

    def summarize(self):
        """Return some diagnostic summary statistics about this Markov model"""
        return 'NotImplemented'
