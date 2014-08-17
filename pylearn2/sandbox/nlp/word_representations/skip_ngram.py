#! /usr/env/bin python
# -*- coding: utf-8 -*-
"""
A module to generate cbow and skip-gram vectors from a dataset

"""
__author__ = 'trunghuynh'
__copyright__ = "(c) 2010, Universite de Montreal"
__license__ = "3-clause BSD license"
__contact__ = "trunghlt@gmail.com"

import os.path
import subprocess
from tempfile import NamedTemporaryFile
from pylearn2.sandbox.nlp.word_representations import WordVectorSpace
from gensim.models.word2vec import LineSentence, Word2Vec
from pylearn2.utils.web import unzip
from pylearn2.utils.string_utils import preprocess


def dict2str(params):
    result = ""
    for k, v in params.iteritems():
        result += "-" + k + "_" + str(v)
    return result


class WikipediaFirstBillionWords(WordVectorSpace):
    URL = "http://mattmahoney.net/dc/enwik9.zip"
    PYLEARN2_DATA_PATH = preprocess('${PYLEARN2_DATA_PATH}')
    DATA_PATH = os.path.join(PYLEARN2_DATA_PATH, "WikipediaFirstBillionWords")
    ORIGINAL_DATA_FILE_NAME = "enwiki9"
    TEXT_PROCESS_PERL = """
        #!/usr/bin/perl

        # Program to filter Wikipedia XML dumps to "clean" text consisting only of lowercase
        # letters (a-z, converted from A-Z), and spaces (never consecutive).
        # All other characters are converted to spaces.  Only text which normally appears
        # in the web browser is displayed.  Tables are removed.  Image captions are
        # preserved.  Links are converted to normal text.  Digits are spelled out.

        # Written by Matt Mahoney, June 10, 2006.  This program is released to the public domain.

        $/=">";                     # input record separator
        while (<>) {
          if (/<text /) {$text=1;}  # remove all but between <text> ... </text>
          if (/#redirect/i) {$text=0;}  # remove #REDIRECT
          if ($text) {

            # Remove any text not normally visible
            if (/<\/text>/) {$text=0;}
            s/<.*>//;               # remove xml tags
            s/&amp;/&/g;            # decode URL encoded chars
            s/&lt;/</g;
            s/&gt;/>/g;
            s/<ref[^<]*<\/ref>//g;  # remove references <ref...> ... </ref>
            s/<[^>]*>//g;           # remove xhtml tags
            s/\[http:[^] ]*/[/g;    # remove normal url, preserve visible text
            s/\|thumb//ig;          # remove images links, preserve caption
            s/\|left//ig;
            s/\|right//ig;
            s/\|\d+px//ig;
            s/\[\[image:[^\[\]]*\|//ig;
            s/\[\[category:([^|\]]*)[^]]*\]\]/[[$1]]/ig;  # show categories without markup
            s/\[\[[a-z\-]*:[^\]]*\]\]//g;  # remove links to other languages
            s/\[\[[^\|\]]*\|/[[/g;  # remove wiki url, preserve visible text
            s/{{[^}]*}}//g;         # remove {{icons}} and {tables}
            s/{[^}]*}//g;
            s/\[//g;                # remove [ and ]
            s/\]//g;
            s/&[^;]*;/ /g;          # remove URL encoded chars

            # convert to lowercase letters and spaces, spell digits
            $_=" $_ ";
            chop;
            print $_;
          }
        }
    """

    def __init__(self):
        model = self._get_model()
        super(self, WikipediaFirstBillionWords).__init__(model.index2word,
                                                         model.syn0)

    def _get_model(self, size=100, window=5, min_count=5, workers=4):
        params = dict(size=size, window=window, min_count=min_count,
                      workers=workers)
        fname = 'skip_ngram-' + dict2str(params) + ".bin"
        if not os.path.exists(os.path.join(self.DATA_PATH, fname)):
            original_fname = os.path.join(self.DATA_PATH,
                                          self.ORIGINAL_DATA_FILE_NAME)
            if not os.path.exists(original_fname):
                unzip(self.URL, self.DATA_PATH)
            with NamedTemporaryFile(delete=True) as f:
                f.write(self.TEXT_PROCESS_PERL)
                f.close()
                with NamedTemporaryFile(delete=True) as pf:
                    proc = subprocess.call(["perl", f.name, original_fname],
                                           stdout=pf)
                    pf.flush()
                    sentences = LineSentence(pf.name)
                    model = Word2Vec(sentences, **params)
                    model.save(os.path.join(self.DATA_PATH, fname))
        else:
            model = Word2Vec.load(os.path.join(self.DATA_PATH, fname))
        return model