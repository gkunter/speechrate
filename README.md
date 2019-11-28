# speechrate.py
Obtain the speech rate from .words files in the Buckeye corpus

Copyright 2019, Gero Kunter (gero.kunter@uni-siegen.de)

This module contains two functions, `get_context()` and `get_speechrate()`. It can be 
used to determine the speech rate (in number of words per second) for tokens from the 
Buckeye Speech Corpus (https://buckeyecorpus.osu.edu/). 

```
get_context(lines, ref_pos, span)
    """
    Create two lists representing the left and the right context window,
    respectively. Each list represents the temporal distance of the tokens in
    the context window from the reference token.

    The context windows will include up to `span` tokens, but can contain fewer
    tokens if the start or the end of the recording is reached, or if a token
    is encountered that may be considered a disfluency. These tokens are
    specified by the labels defined in the global variable BREAK_LABELS.

    Arguments
    ---------
    lines : list of strings
        The content of a Buckeye .words file, either with or without the
        header information.

    ref_pos : int
        The index of the reference token in the list `lines`.

    span : int
        The maximum size of the left and the right context window.

    Returns
    -------
    l_dist, r_dist : lists of float
        The temporal distance between the reference token and the tokens in the
        left and the right context window, respectively.

        If a context window doesn't contain a valid token (e.g. because the
        reference token occurs at the start or the end of the recording, or
        because it is preceded or followed by a pause), the respective list can
        be empty. Otherwise, it will contain up to `span` values (the length of
        the two lists can differ).
    """

def get_speechrate(l_dist, r_dist):
    """
    Calculate the speech rate based on the temporal distances of the tokens in
    the provided context windows.

    The speech D rate is calculated as the overall length of the left and the
    right context window, divided by the sum of the number of tokens in the two

    windows.

    If one of the two windows is empty, only the other list is taken into
    account.

    If both lists are empty, the function returns None.

    Note that as the two lists represent temporal distances, the maximum of
    each list represents the duration of the respective context window.

    Arguments
    ---------
    l_dist, r_dist : list of floats
        The temporal distance between the reference token and the tokens in the
        left and the right context window, respectively.

        These lists are typically produced by the `get_context()` function.

    Returns
    -------
    D : float
        The speech rate based on the two context windows. If both context
        windows are empty, D is defined as None.
    """
```

