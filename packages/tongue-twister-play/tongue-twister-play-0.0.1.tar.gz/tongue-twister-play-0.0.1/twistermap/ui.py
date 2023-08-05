from random import choice
import os

from vlermv import Vlermv

from .network import build_network, query_network

RANDOM = 1

def q(thing = RANDOM, cache = {}):
    '''
    Query for tongue-twisters related to ``thing``,
    or do a ``RANDOM`` tongue-twister. Cache the network
    after the first run.
    '''
    if 'network' not in cache:
        v = Vlermv(os.path.expanduser('~/.tongue-twister-play'))
        if 'network' in v:
            cache['network'] = v['network']
        else:
            cache['network'] = v['network'] = build_network()
    if thing == RANDOM:
        thing = choice(list(cache['network'][1].keys()))
    return list(query_network(cache['network'], thing))

def play():
    tongue_twisters = q()
    tongue_twister = None
    prev_tongue_twister = None
    for i in range(1000):
        if len(tongue_twisters) < 2:
            break
        while prev_tongue_twister == tongue_twister:
            tongue_twister = choice(tongue_twisters)
        prev_tongue_twister = tongue_twister
        yield tongue_twister
        tongue_twisters = q(tongue_twister)
