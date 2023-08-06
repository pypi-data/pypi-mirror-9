
from __future__ import generators

from abc import abstractmethod

#TODO: circular dependencies?
from libextract.coretools import histogram, argmax
from libextract.html import get_etree, get_pairs, get_final_text
from libextract.strategies import ARTICLE_TEXT

## PHASES
## parse
## predict
## extract

class PipelineError(ValueError):
    pass

class Pipeline():
    """There are three branches of logic that will kick off when
    you initialize a Pipeline:

    Note: in all cases, an HT/XML document (*data*) and a single
    or multiple functions are expected. Certain keyword arguments
    (**kwargs) will execute certain branches of logic.


    Case 1.
        ARTICLE_TEXT = (func1, func2,.., funcN)
        Pipeline(data, ARTICLE_TEXT)
        # or
        Pipeline(data, func1, func2,.., funcN)
    Expln.
        Supplying an HT/XML document (*data*), and a list (loosely
        speaking) of functions (fn).

        These fn's are pipelined (ie. "data" is fed to the first fn
        in *args; the output is fed into second fn in *args, etc.)

        The fn's may be in a single list, or provided as positional
        arguments (*args).
    Case 2.
        Pipeline(data, strategy=ARTICLE_TEXT)
    Expln.
        Supplying an HT/XML document (*data*) and a "strategy".

        The *strategy* argument must be provided as a keyword argument.

    Case 3.
        # A)
        # ARTICLE_TEXT = (parse_html,
        #                 ..,
        #                 get_text)

        Pipeline(data, get_text=custom, strategy=ARTICLE_TEXT
        # B)
        Pipeline(data, custom, strategy=ARTICLE_TEXT
    Expln A.
        Supplying an HT/XML document (*data*), a function (w/ keyword
        param *get_text*), and a *strategy* (also keyword arg) will
        execute a branch of logic that will save the *strategy* to
        use, and the *get_text* keyword arg will be used as an
        indicator to replace *strategy*'s original "get_text" function
        with the provided one.

        Case 3. Subcases:

    """
    def __init__(self, *args, **kwargs):
        #args -- tuple of anonymous arguments
        #kwargs -- dictionary of named arguments
        #self._parse = kwargs.get('parse_html', get_etree)


        self._funcs = args
        self._strat = kwargs.get('strategy', ARTICLE_TEXT)



    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    def get_iterator(self):
        return self.__iter__()
