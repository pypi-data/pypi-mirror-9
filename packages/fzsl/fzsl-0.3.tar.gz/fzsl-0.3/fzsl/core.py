import functools
import heapq
import multiprocessing
import re
import signal

class MatchInfo(object):
    def __init__(self, start=0, end=0, score=0, round_ejected=0):
        """
        Information about how a patch matches against the given search

        @attr start         - index in path where match starts
        @attr end           - index in path where match ends
        @attr score         - match score
        @attr round_ejected - the round (length of search string) that this path
                              was removed as a possible match
        """
        self.start = start
        self.end = end
        self.score = score
        self.round_ejected = round_ejected

    def update(self, start=None, end=None, score=None, round_ejected=None):
        """
        Update the MatchInfo attributes

        @param start         - index in path where match starts
        @param end           - index in path where match ends
        @param score         - match score
        @param round_ejected - the round (length of search string) that this path
        """
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if score is not None:
            self.score = score
        if round_ejected is not None:
            self.round_ejected = round_ejected

def default_scorer(path, c_round, regex):
    """
    Score how well a path is matched by the given regex.  Note
    that this function will be passed to a multiprocessing pool
    and needs to return enough context such that the results can
    be correctly collated back at the source.

    @param path     - path to score
    @param c_round  - length of the current search query.  This is
                      used to support deletion of characters in the
                      query.  If a character is deleted, then all
                      results that were ejected in the previous round
                      will be re-evaluated
    @param regex    - regular expression to use for matching
    @return         - This is a little complex in order to support
                      multiprocessing.  The return is a tuple where
                      the first item is the path that was passed into
                      this function.  The second item is another tuple
                      consisting of MatchInfo attributes: start, end,
                      score, round_ejected.  That is:
                      (path, (start, end, score, round_ejected))
    """
    matches = [m for m in regex.finditer(path)]
    if matches:
        def score(match):
            return 1.0 / (len(path) - match.start(1))

        ranked = [(score(m), m) for m in matches]
        score, best = max(ranked)

        return path, (best.start(1), best.end(1) - 1, score, 0)
    else:
        return path, (0, 0, 0.0, c_round)

class FuzzyMatch(object):
    def __init__(self, files=None, scorer=default_scorer):
        """
        Create a FuzzyMatcher which is responsible for handling the
        state as paths are added to the library being searched by an
        updating query.

        @param files    - initial library of paths to rank
        @param scorer   - scoring function.  This function must match
                          the signature and return values of the
                          default_scorer.  See it for more information.
        """
        if files is not None:
            self._library = {path:MatchInfo() for path in files}
        else:
            self._library = {}

        self._scorer = scorer
        self._search = ''

        def pool_init():
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        self._pool = multiprocessing.Pool(initializer=pool_init)

    @property
    def n_matches(self):
        """
        Number of paths which are candidates given the current query
        """
        return len([info for info in self._library.values() if info.round_ejected == 0])

    @property
    def n_files(self):
        """
        Total number of paths in the library being searched
        """
        return len(self._library)

    def add_files(self, files):
        """
        Add files to the library being searched.  This does not automatically
        score the new files.  Use update_scores() to do so if necessary.

        @param files    - list of files to add.
        """
        self._library.update({path:MatchInfo() for path in files})

    def reset_files(self, files):
        """
        Reset the library of possible files to match.  This does not
        automatically score the new files.  Use update_scores() to do
        so if necessary.

        @param files    - new files to use as a library
        """
        self._library = {path:MatchInfo() for path in files}

    def update_scores(self, search):
        """
        Update the scores for every path in the library that was not
        previously ejected.  If the search term is smaller than the
        previous one, paths that were ejected in the last round will
        be re-scored and possibly retained.

        @param search   - query to fuzzy match against the library
        """
        s_len = len(search)

        if s_len < len(self._search):
            _ = [self._library[path].update(round_ejected=0)
                    for path, info in self._library.items()
                    if info.round_ejected == s_len + 1]

        self._search = search

        if s_len == 0:
            return
        elif s_len == 1:
            # In the single character search case, it's far faster to use the
            # string index function over regex.  This is important as we want
            # to slim down the potential matches as quickly as possible.
            #
            # > def f(): 'aoacoeaemaoceaimfoaijhaohfeiahfoefhoeia'.index(j)
            # > def f2(): re.search('j', 'aoacoeaemaoceaimfoaijhaohfeiahfoefhoeia')
            # > timeit.timeit('f()', 'from __main__ import f')
            # 0.5705671310424805
            # > timeit.timeit('f()', 'from __main__ import f2 as f')
            # 2.7029879093170166
            def quick_score(path, info):
                index = path.find(search)
                if index != -1:
                    info.update(start=index, end=index, score=1.0)
                else:
                    info.update(round_ejected=1)

            _ = [quick_score(path, info) for path, info in self._library.items()]
            return

        pattern = '(?=(' + '.*?'.join(re.escape(c) for c in search) + '))'
        regex = re.compile(pattern, re.IGNORECASE)

        scorer = functools.partial(self._scorer, c_round=s_len, regex=regex)
        candidates = [path for path, info
                in self._library.items()
                if info.round_ejected == 0]

        _ = [self._library[path].update(*update)
                for path, update in self._pool.map(scorer, candidates)]

    def score(self, path):
        """
        @param path - path to lookup
        @return     - score of the given path
        """
        return self._library[path].score

    def start(self, path):
        """
        @param path - path to lookup
        @return     - index of the start of the match of the current query in the path
        """
        return self._library[path].start

    def end(self, path):
        """
        @param path - path to lookup
        @return     - index of the end of the match of the current query in the path
        """
        return self._library[path].end

    def top_matches(self, depth=10):
        """
        Get the best matching paths in the library.  Note that only paths
        which have not been ejected and have a positive score will be returned.
        Therefore, the length of the returned list may be less than the
        specified depth.

        @param depth    - maximum number of paths to return
        @return         - sorted list of the top scoring paths in the library
        """
        if len(self._search) > 0:
            valid = [path
                    for path, info in self._library.items()
                    if info.score > 0 and info.round_ejected == 0]
        else:
            valid = self._library.keys()

        ret = heapq.nlargest(depth, valid, key=lambda x: self._library[x].score)
        return ret

