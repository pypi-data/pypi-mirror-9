'''
.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.
'''
from __future__ import absolute_import, division, print_function

import collections
from itertools import chain, ifilter, imap, islice
import logging
import operator

from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.linear_model import LogisticRegression

from dossier.label import CorefValue, expand_labels
from dossier.web import engine_index_scan, streaming_sample


logger = logging.getLogger(__name__)

itget = operator.itemgetter


def similar(store, label_store):
    '''An active learning search engine that returns similar results.

    This satisfies the :class:`dossier.web.SearchEngine` interface.

    In addition to the standard query inputs of ``content_id``,
    ``filter_pred``, and ``limit``, this search engine has optional
    parameters ``canopy_limit`` and ``label_limit`` that restrict
    the number of candidates loaded for in-memory ranking and the
    number of labels used for model training, respectively.
    '''
    return create_search_engine(store, label_store, similar=True)


def dissimilar(store, label_store):
    '''An active learning search engine that returns dissimilar results.

    This satisfies the :class:`dossier.web.SearchEngine` interface.

    In addition to the standard query inputs of ``content_id``,
    ``filter_pred``, and ``limit``, this search engine has optional
    parameters ``canopy_limit`` and ``label_limit`` that restrict
    the number of candidates loaded for in-memory ranking and the
    number of labels used for model training, respectively.
    '''
    return create_search_engine(store, label_store, similar=False)


def create_search_engine(store, label_store, similar=True):
    # N.B. `limit` caps the final results returned by the ranker.
    # This is distinct from `canopy_limit` and `label_limit`, where
    # they are used to keep resource use in check.
    def _(content_id, filter_pred, limit,
          canopy_limit=100, label_limit=100):
        '''Creates an active learning search engine.

        This is a helper function meant to satisfy the interface of
        a search engine with a particular active learning model.
        '''
        # Are these maximums good enough? No idea. ---AG
        canopy_limit = str_to_max_int(canopy_limit, 1000)
        label_limit = str_to_max_int(label_limit, 1000)

        learner = PairwiseFeatureLearner(
            store, label_store, content_id,
            canopy_limit=canopy_limit, label_limit=label_limit)
        try:
            candidate_probs = sorted(
                learner.probabilities(), reverse=similar, key=itget(1))
        except InsufficientTrainingData:
            logger.info('Falling back to plain index scan...')
            index_scan = engine_index_scan(store)
            return index_scan(content_id, filter_pred, limit)

        ranked = ifilter(lambda t: filter_pred(t[0]), candidate_probs)
        results = imap(lambda ((cid, fc), p): (cid, fc, {'probability': p}),
                       ranked)
        return {
            'results': list(islice(results, limit)),
        }
    return _


class InsufficientTrainingData(Exception):
    pass


class PairwiseFeatureLearner(object):
    '''A pairwise active learning model.

    This active learning model applies
    :class:`~sklearn.linear_model.LogisticRegression` on-the-fly
    as a user (or simulated user) interacts with content
    via the web services provided by :mod:`dossier.web`.

    This reads :class:`~dossier.label.Label` objects from
    :class:`~dossier.label.LabelStore` and provides predictions of
    pairwise equivalence, which can be used for coreference resolution,
    clustering, and ranking.

    .. automethod:: dossier.models.PairwiseFeatureLearner.__init__
    .. automethod:: dossier.models.PairwiseFeatureLearner.probabilities
    '''
    def __init__(self, store, label_store, content_id,
                 canopy_limit=None, label_limit=None):
        '''Build a new model.

        :param store: A store of feature collections.
        :type store: :class:`dossier.store.Store`
        :param label_store: A store of labels (ground truth data).
        :type label_store: :class:`dossier.label.LabelStore`
        :param str content_id: The query content id (which should correspond
                               to a feature collection in the ``store``).
                               If it doesn't, no results are returned.
        :param int canopy_limit: A limit on the number of results to return
                                 in the canopy (the initial index scan).
                                 This is meant to be a mechanism for resource
                                 control.
        :param int label_limit: A limit on the number of labels to use in
                                training. This is meant to be a mechanism for
                                resource control.
        '''
        self.store = store
        self.label_store = label_store
        self.query_content_id = content_id
        self.query_fc = None
        self.canopy_limit = canopy_limit
        self.label_limit = label_limit

    def probabilities(self):
        '''Trains a model and predicts recommendations.

        If the query feature collection could not be found or if there
        is insufficient training data, an empty list is returned.

        Otherwise, a list of content objects (tuples of content
        id and feature collection) and probabilities is returned.
        The probability is generated from the model, and reflects
        confidence of the model that the corresponding content object
        is related to the query based on the ground truth data.

        On a large database, random samples are used for training, so
        this function is not deterministic.

        :rtype: ``list`` of
          ((``content_id``, :class:`dossier.fc.FeatureCollection`),
          probability)
        '''
        self.query_fc = self.store.get(self.query_content_id)
        if self.query_fc is None:
            logger.warning('Could not find FC for %s', self.query_content_id)
            return []

        # Try the canopy query before training, because if the canopy query
        # gives us nothing, then there's no point in the additional work.
        #
        # Possible optimization: If the canopy query yields fewer than N
        # results, then can we just return all of them? ---AG
        #
        # N.B Doing the canopy query first will cause things to be slower
        # when there is insufficient training data.
        candidates = self.canopy(limit=self.canopy_limit)
        if len(candidates) == 0:
            logger.info(
                'Could not find any candidates in a canopy query by '
                'scanning the following indexes: %s',
                ', '.join(self.store.index_names()))
            return []

        # Get labels from the database and translate them to the form
        # `[{-1, 1}, i, j]` where `i, j` are indices into the list
        # `content_objs`, which has type `[(content_id, FeatureCollection)]`.
        logger.info('Fetching labels...')
        labels = list(self.labels_from_query(limit=self.label_limit))
        logger.info('Fetching FCs from labels...')
        content_objs = self.content_objs_from_labels(labels)
        indexed_labels = labels_to_indexed_coref_values(content_objs, labels)

        logger.info('Training...')
        model = self.train([fc for _, fc in content_objs], indexed_labels)
        if model is None:
            logger.info(
                'Could not train model: insufficient training data. '
                '(query content id: %s)', self.query_content_id)
            raise InsufficientTrainingData

        feature_names, classifier, transformer = model
        return zip(candidates, self.classify(
            feature_names, classifier, transformer, candidates))

    def train(self, fcs, idx_labels):
        '''Trains and returns a model using sklearn.

        If there are new labels to add, they can be added, returns an
        sklearn model which can be used for prediction and getting
        features.

        This method may return ``None`` if there is insufficient
        training data to produce a model.

        :param labels: Ground truth data.
        :type labels: list of ``({-1, 1}, index1, index2)``.
        '''
        # We have insufficient training data when there is only one or
        # fewer classes of labels.
        if len({lab[0] for lab in idx_labels}) <= 1:
            return None

        feature_names = vectorizable_features(fcs)
        dis = dissimilarities(feature_names, fcs)

        phi_dicts, labels = [], []  # lists are in correspondence
        for coref_value, i, j in idx_labels:
            # i, j are indices into the list `fcs`
            labels.append(coref_value)  # either -1 or 1
            phi_dicts.append({name: dis[name][i,j] for name in feature_names})

        vec = dict_vector()
        training_data = vec.fit_transform(phi_dicts)

        model = LogisticRegression(class_weight='auto', penalty='l1')
        model.fit(training_data, labels)
        return feature_names, model, vec

    def classify(self, feature_names, classifier, transformer, candidates):
        '''Returns ``[probability]`` in correspondence with
        ``candidates``.

        Where each ``probability`` corresponds to the probability that
        the corresponding candidate is classified with a positive label
        given the training data.

        The list returned is in correspondence with the list of
        candidates given.

        N.B. The contract of this method should be simplified by
        bundling ``feature_names``, ``classifier`` and ``transformer``
        into one thing known as "the model." ---AG
        '''
        dis = {}
        for name in feature_names:
            vec = dict_vector()
            query = vec.fit_transform([self.query_fc[name]])
            cans = vec.transform(fc[name] for _, fc in candidates)
            dis[name] = 1 - pairwise_distances(
                cans, query, metric='cosine', n_jobs=1)[:,0]

        # in correspondence with `candidates`
        phi_dicts = transformer.transform(
            [{name: dis[name][i] for name in feature_names}
             for i in xrange(len(candidates))])
        return classifier.predict_proba(phi_dicts)[:,1]

    def canopy(self, limit=None):
        ids = streaming_sample(self.canopy_ids(limit_hint=hard_limit(limit)),
                               limit, hard_limit(limit))
        # I don't think it ever makes sense to include the query
        # as part of the candidate set.
        return filter(lambda (_, fc): fc is not None, self.store.get_many(ids))

    def canopy_ids(self, limit_hint=None):
        limit_hint = limit_hint or 1000
        # TODO: It seems like this should pre-emptively discard content
        # ids that have already participated in a *direct* label with
        # the query. But I think this is a premature optimization since
        # the filtering functions will take care of it. (This optimization
        # would mean fewer kernel computations.)
        blacklist = {self.query_content_id}
        cids = set()

        # OK, so it turns out that a naive index scan is pretty inflexible and
        # arbitrary. The issue is that in a big enough data set, the first
        # index scan will probably exhaust all of our result set, which
        # means result sets will never see any variety.
        #
        # Instead, we'll try to sample from each index in small batch sizes.
        # This is a heuristic; not a principled approach. ---AG
        index_names = self.store.index_names()
        batch_size = limit_hint / 10
        progress = {}  # idx, name |--> last end
        # When `progress` is empty, the following loop will terminate.
        # An index is removed from `progress` when it no longer produces
        # results.
        for idx_name in index_names:
            for name in self.query_fc.get(idx_name, {}):
                progress[(idx_name, name)] = 0

        logger.info('starting index scan (query content id: %s)',
                    self.query_content_id)
        while len(progress) > 0:
            for idx_name in index_names:
                for name in self.query_fc.get(idx_name, {}):
                    key = (idx_name, name)
                    if key not in progress:
                        continue
                    logger.info('[StringCounter index: %s] scanning for "%s"',
                                idx_name, name)
                    scanner = self.store.index_scan(idx_name, name)
                    progressed = 0
                    for cid in islice(scanner, progress[key], None):
                        if progressed >= batch_size:
                            break
                        if cid not in cids and cid not in blacklist:
                            cids.add(cid)
                            progressed += 1
                            yield cid
                    if progressed == 0:
                        progress.pop(key)
                    else:
                        progress[key] += progressed

    def labels_from_query(self, limit=None):
        '''ContentId -> [Label]'''
        logger.info('Getting connected component')
        pos_component = self.label_store.connected_component(
            self.query_content_id)
        pos_component = streaming_sample(
            pos_component, limit, limit=hard_limit(limit))
        pos_expanded = expand_labels(pos_component)
        logger.info('Getting negative labels')

        # It turns out that inferring negative labels actually takes quite
        # a bit of time. I think this is because we are being a bit overeager
        # in how we're adding negative labels in the first place.
        # We should revisit this when negative labels are applied more
        # judiciously.
        # negatives = self.label_store.negative_inference(
            # self.query_content_id)
        negatives = ifilter(
            lambda l: l.value == CorefValue.Negative,
            self.label_store.directly_connected(self.query_content_id))

        # This tomfoolery makes sure that if there are positive and
        # negative labels, then we'll grab at least one of each.
        # (It doesn't matter if we return a little more than `limit` labels.)
        pos_sample = streaming_sample(
            chain(pos_component, pos_expanded),
            limit, limit=hard_limit(limit))
        neg_sample = streaming_sample(
            negatives, limit, limit=hard_limit(limit))
        return pos_sample + neg_sample

    def content_objs_from_labels(self, labels):
        '''[Label] -> [(content_id, FeatureCollection)]'''
        ids = set()
        for lab in labels:
            ids.add(lab.content_id1)
            ids.add(lab.content_id2)
        return list(ifilter(lambda (cid, fc): fc is not None,
                            self.store.get_many(ids)))


def labels_to_indexed_coref_values(content_objs, labels):
    '''[(content_id, FeatureCollection)] -> [Label] -> [({-1,1}, i, j)]

    where 0 <= i, j < len(content_objs).
    '''
    cids_to_idx = {}
    for i, (content_id, _) in enumerate(content_objs):
        cids_to_idx[content_id] = i
    idx = lambda cid: cids_to_idx[cid]
    labs = []
    for lab in labels:
        if lab.content_id1 in cids_to_idx and lab.content_id2 in cids_to_idx:
            labs.append((lab.value.value, idx(lab.content_id1), idx(lab.content_id2)))
    return labs


def vectorizable_features(fcs):
    '''Discovers the ordered set of vectorizable features in ``fcs``.

    Returns a list of feature names, sorted lexicographically.
    Feature names are only included if the corresponding
    features are vectorizable (i.e., they are an instance of
    :class:`collections.Mapping`).
    '''
    is_mapping = lambda obj: isinstance(obj, collections.Mapping)
    return sorted({name for fc in fcs for name in fc if is_mapping(fc[name])})


def dissimilarities(feature_names, fcs):
    '''Computes the pairwise dissimilarity matrices.

    This returns a dictionary mapping each name in ``feature_names``
    to a pairwise dissimilarities matrix. The dissimilaritiy scores
    correspond to ``1 - kernel`` between each feature of each
    pair of feature collections in ``fcs``.

    (The kernel used is currently fixed to ``cosine`` distance.)
    '''
    dis = {}
    for count, name in enumerate(feature_names, 1):
        logger.info('computing pairwise dissimilarity matrix '
                    'for %d of %d features (current feature: %s)',
                    count, len(feature_names), name)
        ## opportunity to use joblib is buried down inside call to
        ## pairwise_distances...
        # And it's fixed to `n_jobs=1` because running multiprocessing
        # inside py.test causes weird problems. It also doesn't seem like a
        # good idea to do it inside a web server either. ---AG
        dis[name] = 1 - pairwise_distances(
            dict_vector().fit_transform(fc[name] for fc in fcs),
            metric='cosine', n_jobs=1)
    return dis


def dict_vector():
    return DictVectorizer(sparse=False)


def hard_limit(limit):
    return limit if limit is None else (limit * 10)


def str_to_max_int(s, maximum):
    try:
        return min(maximum, int(s))
    except (ValueError, TypeError):
        return maximum
