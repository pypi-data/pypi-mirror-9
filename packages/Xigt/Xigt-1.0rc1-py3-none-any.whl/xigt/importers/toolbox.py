#!/usr/bin/env python3

from collections import OrderedDict
import logging
import warnings
from itertools import chain, zip_longest

from xigt import (XigtCorpus, Igt, Tier, Item, Metadata, Meta)
from xigt.codecs import xigtxml

try:
    import toolbox
except ImportError:
    import sys
    print('Could not import Toolbox module. Get it from here:\n'
          '  https://github.com/goodmami/toolbox\n',
          file=sys.stderr)

default_tier_types = {
    '\\t': 'words',
    '\\m': 'morphemes',
    '\\g': 'glosses',
    '\\p': 'pos',
    '\\f': 'translations'
}

default_alignments = {
    '\\m': '\\t',
    '\\g': '\\m',
    '\\p': '\\m'
}

default_record_markers = [
    '\\id',
    '\\ref'
]

default_attribute_map = {
    '\\id': 'corpus-id'
}

class XigtImportError(Exception):
    pass


def xigt_import(in_fh, out_fh, options=None):
    if options is None:
        options = {}
    options.setdefault('tier_types', default_tier_types)
    options.setdefault('alignments', default_alignments)
    options.setdefault('record_markers', default_record_markers)
    options.setdefault('attribute_map', default_attribute_map)

    tb = toolbox.read_toolbox_file(in_fh)
    igts = toolbox_igts(tb, options)
    xc = XigtCorpus(igts=igts, mode='transient')
    xigtxml.dump(out_fh, xc)


def toolbox_igts(tb, options):
    record_markers = options['record_markers']
    assert len(record_markers) > 0
    mkrPriKey = record_markers[-1]
    for context, data in toolbox.records(tb, record_markers):
        data = list(data)  # run the generator
        if context.get(mkrPriKey) is None:
            continue  # header info
        igt = make_igt(
            context[mkrPriKey],
            data,
            context=context,
            tier_types=options['tier_types'],
            alignments=options['alignments'],
            attribute_map=options['attribute_map']
        )
        if igt is not None:
            yield igt

def make_igt(key, data, context=None,
             tier_types=default_tier_types,
             alignments=default_alignments,
             attribute_map=default_attribute_map):
    if context is None:
        context = {}
    attrs = {}
    for (mkr, val) in chain(data, context.items()):
        if mkr in attribute_map:
            attrs[attribute_map[mkr]] = val
    metadata = None

    w = None
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')

        try:
            tiers = make_all_tiers(data, tier_types, alignments)
            igt = Igt(
                id=key,
                attributes=attrs,
                metadata=metadata,
                tiers=tiers
            )
        except (toolbox.ToolboxError, XigtImportError) as ex:
            logging.error('Error during import of item {}:\n  {}'
                          .format(key, str(ex)))
            igt = None
        if len(ws) > 0:
            w = ws[0]

    if w is not None:
        if issubclass(w.category, toolbox.ToolboxWarning):
            warnings.warn('{}: {}'.format(key, w.message), w.category)
        else:
            warnings.warn_explicit(w.message, w.category, w.filename, w.lineno)

    return igt


def make_all_tiers(item_data, tier_types, alignments):
    aligned_tiers = set(alignments.keys()).union(alignments.values())
    # use strip=False because we want same-length strings
    tier_data = toolbox.normalize_record(item_data, aligned_tiers, strip=False)
    prev = {}
    aligned_fields = toolbox.align_fields(
        tier_data, alignments, errors='ratio'
    )
    for mkr, aligned_tokens in aligned_fields:
        tier_type = tier_types.get(mkr)
        tier_id = mkr.lstrip('\\')
        algn_tier = prev.get(alignments.get(mkr))  # could be None
        try:
            tier = make_tier(tier_type, tier_id, aligned_tokens, algn_tier)
        except (AttributeError, AssertionError):
            raise XigtImportError('Error making {} tier (marker: {}).'
                                  .format(tier_type, mkr))
        prev[mkr] = tier
        yield tier

def make_tier(tier_type, tier_id, aligned_tokens, algn_tier):
    attrs = OrderedDict()
    items = list()
    i = 1  # start indices at 1
    if aligned_tokens == [(None, None)]:
        pass  # nothing to do
    elif algn_tier is not None:
        attrs['alignment'] = algn_tier.id
        algn_data = zip_longest(algn_tier.items, aligned_tokens)
        for tgt_item, src_data in algn_data:
            tgt_tok, src_toks = src_data
            assert tgt_tok == tgt_item.text  # FIXME is this necessary?
            for s in src_toks:
                items.append(
                    Item(id='{}{}'.format(tier_id, i),
                         text=s,
                         attributes={'alignment':tgt_item.id})
                )
                i += 1
    else:
        for tgt, src in aligned_tokens:
            for s in src:
                items.append(Item(id='{}{}'.format(tier_id, i), text=s))
                i += 1
    return Tier(id=tier_id, type=tier_type, items=items, attributes=attrs)