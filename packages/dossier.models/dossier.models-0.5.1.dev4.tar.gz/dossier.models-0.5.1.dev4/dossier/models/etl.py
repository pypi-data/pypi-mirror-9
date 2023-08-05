from __future__ import absolute_import, division, print_function

import argparse
from collections import Counter, defaultdict
from itertools import chain, islice
import multiprocessing
import re
import sys
import time
import traceback
import urllib
import zlib

import cbor
from gensim import corpora, models
import happybase

from dossier.fc import FeatureCollection, FeatureCollectionChunk, StringCounter
from dossier.store import Store
from dossier.web import streaming_sample
import kvlayer
from streamcorpus_pipeline._clean_visible import cleanse, make_clean_visible
from streamcorpus_pipeline._clean_html import make_clean_html
import yakonfig

import dossier.models.features.sip as sip


def html_to_fc(html, url=None, timestamp=None, other_features=None):
    if isinstance(html, str):
        html = unicode(html, 'utf-8')
    timestamp = timestamp or int(time.time() * 1000)
    other_features = other_features or []
    url = url or u''

    clean_html = make_clean_html(html.encode('utf-8')).decode('utf-8')
    clean_vis = make_clean_visible(html.encode('utf-8')).decode('utf-8')

    fc = FeatureCollection()
    fc[u'meta_raw'] = html
    fc[u'meta_clean_html'] = clean_html
    fc[u'meta_clean_visible'] = clean_vis
    fc[u'meta_timestamp'] = unicode(timestamp)
    fc[u'meta_url'] = unicode(url, 'utf-8')
    for feat_name, feat_val in other_features.iteritems():
        fc[feat_name] = feat_val

    body = cleanse(fc[u'meta_clean_visible'])
    nps = sip.noun_phrases(body)
    fc[u'bowNP'] = StringCounter(nps)
    return fc


def add_sip_to_fc(fc, tfidf, limit=4):
    if 'bowNP' not in fc:
        return
    nouns = fc['bowNP'].keys()
    bow = tfidf[tfidf.id2word.doc2bow(nouns)]
    # convert to `word: count` from `index: count`.
    # BUT only take the most significant.
    bow = {tfidf.id2word[word]: count
           for word, count in Counter(dict(bow)).most_common(limit)}
    fc[u'bowNP_sip'] = StringCounter(bow)


def row_to_content_obj(key_row):
    '''Returns ``FeatureCollection`` given an HBase artifact row.

    Note that the FC returned has a Unicode feature ``artifact_id``
    set to the row's key.
    '''
    key, row = key_row
    cid = 'web|' + urllib.quote(key, safe='~').encode('utf-8')
    response = row.get('response', {})

    other_bows = defaultdict(StringCounter)
    for attr, val in row.get('indices', []):
        other_bows[attr][val] += 1
    try:
        artifact_id = key
        if isinstance(artifact_id, str):
            artifact_id = unicode(artifact_id, 'utf-8')
        fc = html_to_fc(
            response.get('body', ''),
            url=row.get('url'), timestamp=row.get('timestamp'),
            other_features=dict(other_bows, **{'artifact_id': artifact_id}))
    except:
        fc = None
        print('Could not create FC for %s:' % cid, file=sys.stderr)
        print(traceback.format_exc())
    return cid, fc


def get_artifact_rows(conn, limit=5):
    t = conn.table('artifact')
    for key, data in t.scan(limit=limit, batch_size=50):
        yield key, unpack_artifact_row(data)


def unpack_artifact_row(row):
    data = {
        'url': row['f:url'],
        'timestamp': int(row['f:timestamp']),
        'request': {
            'method': row['f:request.method'],
            'client': cbor.loads(zlib.decompress(row['f:request.client'])),
            'headers': cbor.loads(zlib.decompress(row['f:request.headers'])),
            'body': cbor.loads(zlib.decompress(row['f:request.body'])),
        },
        'response': {
            'status': row['f:response.status'],
            'server': {
                'hostname': row['f:response.server.hostname'],
                'address': row['f:response.server.address'],
            },
            'headers': cbor.loads(zlib.decompress(row['f:response.headers'])),
            'body': cbor.loads(zlib.decompress(row['f:response.body'])),
        },
        'indices': [],
    }
    for kk, vv in row.items():
        mm = re.match(r"^f:index\.(?P<key>.*)\.[0-9]+$", kk)
        if mm is not None:
            data['indices'].append((mm.group('key'), vv))
    return data


def unpack_noun_phrases(row):
    body = cbor.loads(zlib.decompress(row['f:response.body']))
    body = make_clean_visible(body.encode('utf-8')).decode('utf-8')
    body = cleanse(body)
    return sip.noun_phrases(body)


def generate_fcs(tfidf, conn, pool, add, limit=5, batch_size=100):
    rows = get_artifact_rows(conn, limit=limit)
    batch = []
    for i, (cid, fc) in enumerate(pool.imap(row_to_content_obj, rows), 1):
        if fc is None:
            continue
        add_sip_to_fc(fc, tfidf)
        batch.append((cid, fc))

        if len(batch) >= batch_size:
            add(batch)
            batch = []
        if i % 100 == 0:
            status('%d of %s done'
                   % (i, 'all' if limit is None else str(limit)))
    if len(batch) > 0:
        add(batch)


def status(*args, **kwargs):
    kwargs['end'] = ''
    args = list(args)
    args[0] = '\033[2K\r' + args[0]
    print(*args, **kwargs)
    sys.stdout.flush()


def batch_iter(n, iterable):
    iterable = iter(iterable)
    while True:
        yield chain([next(iterable)], islice(iterable, n-1))


class App(yakonfig.cmd.ArgParseCmd):
    def __init__(self, *args, **kwargs):
        yakonfig.cmd.ArgParseCmd.__init__(self, *args, **kwargs)
        self._store = None

    @property
    def store(self):
        if self._store is None:
            feature_indexes = None
            try:
                conf = yakonfig.get_global_config('dossier.store')
                feature_indexes = conf['feature_indexes']
            except KeyError:
                pass
            self._store = Store(kvlayer.client(),
                                feature_indexes=feature_indexes)
        return self._store

    def args_convert(self, p):
        p.add_argument('--host', default='localhost')
        p.add_argument('--port', default=9090, type=int)
        p.add_argument('--table-prefix', default='')
        p.add_argument('--limit', default=5, type=int)
        p.add_argument('--batch-size', default=1000, type=int)
        p.add_argument('-p', '--processes',
                       default=multiprocessing.cpu_count(), type=int)
        p.add_argument('-o', '--output', default=None)
        p.add_argument('tfidf_model_path',
                       help='This is required and can be generated '
                            'with the `dossier.etl tfidf` script.')

    def do_convert(self, args):
        tfidf = models.TfidfModel.load(args.tfidf_model_path)
        conn = happybase.Connection(host=args.host, port=args.port,
                                    table_prefix=args.table_prefix)
        pool = multiprocessing.Pool(processes=args.processes)
        limit = None if args.limit == 0 else args.limit

        chunk = None
        if args.output is None:
            def add(cids_and_fcs):
                self.store.put(cids_and_fcs)
        else:
            chunk = FeatureCollectionChunk(path=args.output, mode='wb')
            def add(cids_and_fcs):
                for _, fc in cids_and_fcs:
                    chunk.add(fc)
        generate_fcs(tfidf, conn, pool, add,
                     limit=limit, batch_size=args.batch_size)
        if chunk is not None:
            chunk.flush()

    def args_tfidf(self, p):
        p.add_argument('--host', default='localhost')
        p.add_argument('--port', default=9090, type=int)
        p.add_argument('--table-prefix', default='')
        p.add_argument('--limit', default=100, type=int)
        p.add_argument('--batch-size', default=1000, type=int)
        p.add_argument('-p', '--processes',
                       default=multiprocessing.cpu_count(), type=int)
        p.add_argument('ids', metavar='INPUT_ROW_KEY_SAMPLE_FILE',
                       help='A file containing row keys to use for a sample.')
        p.add_argument('out', metavar='OUTPUT_TFIDF_MODEL_FILE',
                       help='The file path to write the tfidf model to.')

    def do_tfidf(self, args):
        conn = happybase.Connection(host=args.host, port=args.port,
                                    table_prefix=args.table_prefix)
        t = conn.table('artifact')
        corpus = []
        print('Extracting random sample...')
        sample = streaming_sample(open(args.ids), args.limit)

        print('Building corpus...')
        batches = batch_iter(args.batch_size, (s.strip() for s in sample))
        pool = multiprocessing.Pool(processes=args.processes)
        for i, batch in enumerate(batches, 1):
            rows = (row for _, row in t.rows(list(batch)))
            for noun_phrases in pool.imap(unpack_noun_phrases, rows):
                corpus.append(noun_phrases)
            status('%d of %d batches done' % (i, args.limit / args.batch_size))

        print('Computing model...')
        dictionary = corpora.Dictionary(corpus)
        bows = [dictionary.doc2bow(tokens) for tokens in corpus]
        tfidf = models.TfidfModel(bows, id2word=dictionary)
        tfidf.save(args.out)

    def args_ids(self, p):
        p.add_argument('--host', default='localhost')
        p.add_argument('--port', default=9090, type=int)
        p.add_argument('--table-prefix', default='')
        p.add_argument('--limit', default=100, type=int)

    def do_ids(self, args):
        conn = happybase.Connection(host=args.host, port=args.port,
                                    table_prefix=args.table_prefix)
        t = conn.table('artifact')
        hbase_filter = 'FirstKeyOnlyFilter() AND KeyOnlyFilter()'
        ids = islice(enumerate(t.scan(filter=hbase_filter)), args.limit)
        for i, (key, data) in ids:
            print(key)
            if i % 100000 == 0:
                print('%d keys received' % i, file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description='Utilities for generating FCs from artifacts.')
    app = App()
    app.add_arguments(p)
    args = yakonfig.parse_args(p, [kvlayer, yakonfig])
    app.main(args)


if __name__ == '__main__':
    main()
