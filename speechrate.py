# -*- coding: utf-8 -*-

# speechrate.py - determines the speech rate of data from the Buckeye corpus.
#
# Copyright 2019, Gero Kunter (gero.kunter@uni-siegen.de)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# The following list of labels is used to deliminate the context windows for
# determining the speech rate:
BREAK_LABELS = ("<SIL>", "<LAUGH>", "<IVER>", "<UNKNOWN>", "<VOCNOISE>",
                "<NOISE>",
                "{B_TRANS}", "{E_TRANS}")

# Labels are described in Table 4 of the Buckeye Manual
# https://buckeyecorpus.osu.edu/BuckeyeCorpusmanual.pdf
#
# <SIL>         pause
# <LAUGH>       laughter without producing a word
# <IVER>        interviewer's turn
# <VOCNOISE>    non-speech vocalizations
# <UNKNOWN>     audible but unintelligible speech
# <NOISE>       environmental noise
#
# {B_TRANS}     beginning of transcript
# {E_TRANS}     end of transcript
#
# You can add more labels to BREAK_LABELS. For example, if you want to end the
# context window also if the speaker produces a word hesitantly, you'd add
# "<HES-" (with quotation marks, with only an opening '<' but no closing one)
# to the variable.


def get_context(lines, ref_pos, span):
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

    # Skip the header information from the Buckeye .words files if it is
    # included in the list of lines:
    if "#" in lines:
        header_pos = lines.index("#")
        lines = lines[(header_pos + 1):]
    elif "#\n" in lines:
        header_pos = lines.index("#\n")
        lines = lines[(header_pos + 1):]
    else:
        header_pos = 0

    ref_pos = ref_pos - header_pos - 1

    # Determine the extent of the left and the right context windows around the
    # reference token. Each window will contain up to 'span' tokens, but can
    # contain fewer if the start or end of the recording is included.
    #
    # In order to correctly calculate the start and end times of the tokens,
    # the left context window will include one additional token, and the right
    # context window will include the reference token.
    #
    l_start = max(0, ref_pos - span - 2)
    r_end = min(len(lines), ref_pos + span + 1)

    # l_dist and r_dist will contain the temporal distance of the tokens in the
    # left and right context window from the reference token.
    l_dist = []
    r_dist = []

    # obtain left context window (which may be empty):
    l_win = [s.strip().split(" ", 1) for s in lines[l_start:ref_pos]]
    if l_win:
        # for each token in the left window, create a list entry that contains
        # the end time and the word string:
        l_dat = [{"t": float(time), "word": trans.split(" ", 2)[1]}
                 for time, trans in l_win]

        # the start time of the reference token equates the end time of the
        # last token in the left window:
        start_time = l_dat[-1]["t"]

        # go through the tokens left context window in reverse order, excluding
        # the very first context token (this token is only included so that the
        # start_time can always be determined correctly):
        for token in l_dat[1:][::-1]:
            # calculate the temporal distance between the context token and the
            # current token, and add the distance to a list:
            l_dist.append(start_time - token["t"])

            # stop if the context token matches one of the break labels:
            if token["word"].upper().startswith(BREAK_LABELS):
                break

    # obtain right context window, including the reference token as the first
    # element:
    r_win = [s.strip().split(" ", 1) for s in lines[ref_pos:r_end]]

    # for each token in the right window, create a list entry that contains
    # the end time and the word string:
    r_dat = [{"t": float(time.strip()), "word": trans.split(" ", 2)[1]}
             for time, trans in r_win]

    # the end time of the reference token is stored in the first element of
    # the right context window:
    end_time = r_dat[0]["t"]

    # go through the tokens in the right window (excluding the reference token)
    for token in r_dat[1:]:
        # stop if the context token matches one of the break labels:
        if token["word"].upper().startswith(BREAK_LABELS):
            break

        # calculate the temporal distance between the context token and the
        # current token, and add the distance to a list:
        r_dist.append(token["t"] - end_time)

    return (l_dist[1:], r_dist)


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
    if l_dist and r_dist:
        return (max(l_dist) + max(r_dist)) / (len(l_dist) + len(r_dist))
    elif r_dist and not l_dist:
        return max(r_dist) / len(r_dist)
    elif l_dist:
        return max(l_dist) / len(l_dist)
    else:
        return None
