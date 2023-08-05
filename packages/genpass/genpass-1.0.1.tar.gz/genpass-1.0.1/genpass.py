#!/usr/bin/env python
# Copyright 2015 Steven Dee. See COPYING for details.
"""
Generates random memorable passphrases.

This script builds a set of unique suitable words from a dictionary file, then
produces one or more passphrases chosen at random form that set. It also
optionally prints estimates of the entropy (i.e. difficulty to guess) of the
produced passphrases based on the number of items in the set and the number of
words per phrase.

Caveat emptor: if you generate passphrases without a separator, or with a
separator that is a lower-case letter, the entropy estimate may be wrong.
"""
from __future__ import print_function

import argparse
import itertools
import math
import random
import re
import sys


__version__ = '1.0.1'

def gen_words(min_word, max_word, filename):
    """Returns a list of unique words from a dictionary file.

    Opens filename, reads words from it line by line, normalizes the words read
    to lowercase non-possessive (strictly speaking, taking only the portion
    before the first "'"), and adds the ones between min_word and max_word
    characters that contain only letters (no numbers, no symbols) to the set of
    words returned.
    """
    words = set()
    with open(filename, 'r') as words_file:
        for line in words_file:
            word = line.rstrip().lower().split("'")[0]
            if (len(word) >= min_word and len(word) <= max_word and
                    re.search('^[a-z]*$', word)):
                words.add(word)
    return words

def get_passphrase(words, n_words, sep, gen):
    """Get a random n-word passphrase from the word set."""
    passwords = gen.sample(words, n_words)
    return sep.join(passwords)

def entropy_estimate(n_items, items_per_guy, n_guys):
    """Returns an estimate of entropy per word and per passphrase."""
    def log2(n):
        return math.log(n) / math.log(2)
    bits_per_item = log2(n_items)
    bits_per_guy = bits_per_item * items_per_guy
    bits_overall = bits_per_guy - log2(n_guys)
    return bits_per_item, bits_overall

def stats_str(n_words, words_per_phrase, n_phrases):
    """Returns a string describing an entropy estimate."""
    bits_per_word, bits_overall = entropy_estimate(n_words, words_per_phrase,
                                                   n_phrases)
    stats = ['{:.2f} bits/word'.format(bits_per_word)]
    if n_phrases > 1:
        stats.append('{} phrases'.format(n_phrases))
    paren_str = ', '.join(stats)
    base_str = '{:.2f} bits estimated entropy'.format(bits_overall)
    return '{} ({})'.format(base_str, paren_str)

def some_examples(items):
    """Returns the first few items in a collection."""
    return ('  ' + x for x in itertools.islice(items, 6))


def parse_args(argv):
    """Returns Namespace from passed command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        version=__version__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print extra info')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="don't print stats")
    parser.add_argument('--words', dest='n_words', type=int, default=4,
                        help='number of words in result passphrase')
    parser.add_argument('--phrases', dest='n_phrases', type=int, default=1,
                        help='number of passphrases to produce')
    parser.add_argument('--min-word', metavar='LEN', type=int, default=3,
                        help='minimum length of an individual word')
    parser.add_argument('--max-word', metavar='LEN', type=int, default=10,
                        help='maximum length of an individual word')
    parser.add_argument('--sep', default='-',
                        help='separator between words')
    parser.add_argument('--no-sep', action='store_const', const='', dest='sep')
    parser.add_argument('--dict', dest='filename',
                        default='/usr/share/dict/words',
                        help='dictionary file to use')
    return parser.parse_args(argv)

# pylint: disable=too-many-arguments
# Justification: with explicitly spelled out arguments, we're warned if we
# aren't using any, and we get an error if we pass any extra. Thus this (with
# the call to main(**args) in run_ below) serves as a check that our argument
# parser contains all and only arguments that have actual effect on the
# program.
#
def main(min_word, max_word, n_words, n_phrases, sep, debug, quiet, filename):
    """Builds a set of unique words and prints passphrases from it."""
    words = gen_words(min_word, max_word, filename)
    gen = random.SystemRandom()

    if not quiet:
        print(stats_str(len(words), n_words, n_phrases), file=sys.stderr)
    if debug:
        print('{} words such as'.format(len(words)), *some_examples(words),
              sep='\n', file=sys.stderr)

    for _ in range(n_phrases):
        print(get_passphrase(words, n_words, sep, gen))

def run_():
    "Runs from command-line args."
    args = parse_args(sys.argv[1:])
    main(**vars(args))


if __name__ == '__main__':
    run_()
