#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
================================================================================

    Music theory Python package, intervals module.
    Copyright (C) 2008-2009, Bart Spaans

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


================================================================================

    The intervals module can be used to create intervals from notes.
    When you are working in a key (for instance 'F'), you can use the
    functions second ('G'), third ('A'), fourth ('Bb'), fifth ('C'),
    sixth ('D') and seventh ('E') to get to the respective natural
    intervals of that note.
    When you want to get the absolute intervals you can use the
    minor and major functions. For example: minor_third(\"F\") returns
    'Ab' while major_third(\"F\") returns 'A'.

    This modules also contains other useful helper functions like
    measure, determine, invert, is_consonant and is_dissonant.

================================================================================"""

import notes
import diatonic


def unison(note, key=None):
    """One of the most useless methods ever written, which returns the unison of \
note. The key is not at all important, but is here for consistency reasons \
only.
    Example:
{{{
>>> unison(\"C\")
'C'
}}}"""

    return note


def second(note, key):
    """Take the diatonic second of note in key.
    Examples:
{{{
>>>    second(\"E\", \"C\")
'F'
>>> second(\"E\", \"D\")
'F#'
}}}
    Raises a !KeyError if the `note` is not found in the `key`."""

    return diatonic.interval(key, note, 1)


def third(note, key):
    """Take the diatonic third of note in key.
    Examples:
{{{
>>>    third(\"E\", \"C\")
'G'
>>>    third(\"E\", \"E\")
'G#'
}}}
    Raises a !KeyError if note is not found in key."""

    return diatonic.interval(key, note, 2)


def fourth(note, key):
    """Take the diatonic fourth of note in key.
    Examples:
{{{
>>>    fourth(\"E\", \"C\")
'A'
>>>    fourth(\"E\", \"B\")
'A#'
}}}
    Raises a !KeyError if note is not found in key."""

    return diatonic.interval(key, note, 3)


def fifth(note, key):
    """Take the diatonic fifth of note in key.
    Examples:
{{{
>>>    fifth(\"E\", \"C\")
'B'
>>>    fifth(\"E\", \"F\")
'Bb'
}}}
    Raises a !KeyError if note is not found in key."""

    return diatonic.interval(key, note, 4)


def sixth(note, key):
    """Take the diatonic sixth of note in key.
    Examples:
{{{
>>>    sixth(\"E\", \"C\")
'C'
>>> sixth(\"E\", \"B\")
'C#'
}}}
    Raises a !KeyError if note is not found in key."""

    return diatonic.interval(key, note, 5)


def seventh(note, key):
    """Take the diatonic seventh of note in key.
    Examples:
{{{
>>> seventh(\"E\", \"C\")
'D'
>>> seventh(\"E\", \"B\")
'D#'
}}}
    Raises a !KeyError if note is not found in key."""

    return diatonic.interval(key, note, 6)


def minor_unison(note):
    return notes.diminish(note)


def major_unison(note):
    return note


def augmented_unison(note):
    return notes.augment(note)


def minor_second(note):
    sec = second(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, sec, 1)


def major_second(note):
    sec = second(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, sec, 2)


def minor_third(note):
    trd = third(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, trd, 3)


def major_third(note):
    trd = third(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, trd, 4)


def minor_fourth(note):
    frt = fourth(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, frt, 4)


def major_fourth(note):
    frt = fourth(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, frt, 5)


def perfect_fourth(note):
    return major_fourth(note)


def minor_fifth(note):
    fif = fifth(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, fif, 6)


def major_fifth(note):
    fif = fifth(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, fif, 7)


def perfect_fifth(note):
    return major_fifth(note)


def minor_sixth(note):
    sth = sixth(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, sth, 8)


def major_sixth(note):
    sth = sixth(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, sth, 9)


def minor_seventh(note):
    sth = seventh(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, sth, 10)


def major_seventh(note):
    sth = seventh(note[0], 'C')
    return augment_or_diminish_until_the_interval_is_right(note, sth, 11)


def get_interval(note, interval, key='C'):
    """Gets the note an interval (in half notes) away from the given note. This \
will produce mostly theoretical sound results, but you should use the minor \
and major functions to work around the corner cases."""

    intervals = map(lambda x: (notes.note_to_int(key) + x) % 12, [
        0,
        2,
        4,
        5,
        7,
        9,
        11,
        ])
    key_notes = diatonic.get_notes(key)
    for x in key_notes:
        if x[0] == note[0]:
            result = (intervals[key_notes.index(x)] + interval) % 12
    if result in intervals:
        return key_notes[intervals.index(result)] + note[1:]
    else:
        return notes.diminish(key_notes[intervals.index((result + 1) % 12)]
                               + note[1:])


def measure(note1, note2):
    """Returns an integer in the range of 0-11, determining the half note steps \
between note1 and note2.
    Examples:
{{{
>>>    measure(\"C\", \"D\")
2
>>>    measure(\"D\", \"C\")
10
}}}"""

    res = notes.note_to_int(note2) - notes.note_to_int(note1)
    if res < 0:
        return 12 - res * -1
    else:
        return res


def augment_or_diminish_until_the_interval_is_right(note1, note2, interval):
    """A helper function for the minor and major functions. You should probably not \
use this directly."""

    cur = measure(note1, note2)
    while cur != interval:
        if cur > interval:
            note2 = notes.diminish(note2)
        elif cur < interval:
            note2 = notes.augment(note2)
        cur = measure(note1, note2)

    # We are practically done right now, but we need to be able to create the
    # minor seventh of Cb and get Bbb instead of B######### as the result

    val = 0
    for token in note2[1:]:
        if token == '#':
            val += 1
        elif token == 'b':
            val -= 1

    # These are some checks to see if we have generated too much #'s or too much
    # b's. In these cases we need to convert #'s to b's and vice versa.

    if val > 6:
        val = val % 12
        val = -12 + val
    elif val < -6:
        val = val % -12
        val = 12 + val

    # Rebuild the note

    result = note2[0]
    while val > 0:
        result = notes.augment(result)
        val -= 1
    while val < 0:
        result = notes.diminish(result)
        val += 1
    return result


def invert(interval):
    """Invert an interval represented as `[note1, note2]`.
    For example:
{{{
>>> invert[\"C\", \"E\"]
[\"E\", \"C\"]
}}}"""

    interval.reverse()
    res = list(interval)
    interval.reverse()
    return res

def semitones_from_shorthand(shorthand):
    basic = {
        '1': 0,
        '2': 2,
        '3': 4,
        '4': 5,
        '5': 7,
        '6': 9,
        '7': 11
    }
    base = basic[shorthand[-1]]
    for x in shorthand:
        if x == '#':
            base += 1
        elif x == 'b':
            base -= 1
    return base

def determine(note1, note2, shorthand=False):
    """Names the interval between note1 and note2.
    Example:
{{{
>>>    determine(\"C\", \"E\")
'major third'
>>> determine(\"C\", \"Eb\")
'minor third'
>>> determine(\"C\", \"E#\")
'augmented third'
>>> determine(\"C\", \"Ebb\")
'diminished third'
}}}

    This works for all intervals. Note that there are corner cases for \
'major' fifths and fourths:
{{{
>>> determine(\"C\", \"G\")
'perfect fifth'
>>> determine(\"C\", \"F\")
'perfect fourth'
}}}"""

    if hasattr(note1, 'octave') and hasattr(note2, 'octave'):
        if int(note1) > int(note2):
            note3 = note2
            note2 = note1
            note1 = note3
            del note3

    if hasattr(note1, 'name'):
        note1 = note1.name
    if hasattr(note2, 'name'):
        note2 = note2.name

    # Corner case for unisons ('A' and 'Ab', for instance)

    if note1[0] == note2[0]:

        def get_val(note):
            """Private function to count the value of accidentals"""

            r = 0
            for x in note[1:]:
                if x == 'b':
                    r -= 1
                elif x == '#':
                    r += 1
            return r

        x = get_val(note1)
        y = get_val(note2)
        if x == y:
            if not shorthand:
                return 'major unison'
            return '1'
        elif x < y:
            if not shorthand:
                return 'augmented unison'
            return '#1'
        elif x - y == 1:
            if not shorthand:
                return 'minor unison'
            return 'b1'
        else:
            if not shorthand:
                return 'diminished unison'
            return 'bb1'

    # Other intervals

    n1 = notes.fifths.index(note1[0])
    n2 = notes.fifths.index(note2[0])
    number_of_fifth_steps = n2 - n1
    if n2 < n1:
        number_of_fifth_steps = len(notes.fifths) - n1 + n2

    # [name, shorthand_name, half notes for major version of this interval]

    fifth_steps = [
        ['unison', '1', 0],
        ['fifth', '5', 7],
        ['second', '2', 2],
        ['sixth', '6', 9],
        ['third', '3', 4],
        ['seventh', '7', 11],
        ['fourth', '4', 5],
        ]

    # Count half steps between note1 and note2

    half_notes = measure(note1, note2)

    # Get the proper list from the number of fifth steps

    current = fifth_steps[number_of_fifth_steps]

    # maj = number of major steps for this interval

    maj = current[2]

    # if maj is equal to the half steps between note1 and note2 the interval is
    # major or perfect

    if maj == half_notes:

        # Corner cases for perfect fifths and fourths

        if current[0] == 'fifth':
            if not shorthand:
                return 'perfect fifth'
        elif current[0] == 'fourth':
            if not shorthand:
                return 'perfect fourth'
        if not shorthand:
            return 'major ' + current[0]
        return current[1]
    elif maj + 1 <= half_notes:

    # if maj + 1 is equal to half_notes, the interval is augmented.

        if not shorthand:
            return 'augmented ' + current[0]
        return '#' * (half_notes - maj) + current[1]
    elif maj - 1 == half_notes:

    # etc.

        if not shorthand:
            return 'minor ' + current[0]
        return 'b' + current[1]
    elif maj - 2 >= half_notes:
        if not shorthand:
            return 'diminished ' + current[0]
        return 'b' * (maj - half_notes) + current[1]


def from_shorthand(note, interval, up=True):
    """Returns the note on interval up or down.
    Example:
{{{
>>> from_shorthand(\"A\", \"b3\")
'C'
>>> from_shorthand(\"D\", \"2\")
'E'
>>> from_shorthand(\"E\", \"2\", False)
'D'
}}}"""

    # warning should be a valid note.

    if not notes.is_valid_note(note):
        return False

    # [shorthand, interval function up, interval function down]

    shorthand_lookup = [
        ['1', major_unison, major_unison],
        ['2', major_second, minor_seventh],
        ['3', major_third, minor_sixth],
        ['4', major_fourth, major_fifth],
        ['5', major_fifth, major_fourth],
        ['6', major_sixth, minor_third],
        ['7', major_seventh, minor_second],
        ]

    # Looking up last character in interval in shorthand_lookup and calling that
    # function.

    val = False
    for shorthand in shorthand_lookup:
        if shorthand[0] == interval[-1]:
            if up:
                val = shorthand[1](note)
            else:
                val = shorthand[2](note)

    # warning Last character in interval should be 1-7

    if val == False:
        return False

    # Collect accidentals

    for x in interval:
        if x == '#':
            if up:
                val = notes.augment(val)
            else:
                val = notes.diminish(val)
        elif x == 'b':
            if up:
                val = notes.diminish(val)
            else:
                val = notes.augment(val)
        else:
            return val


def is_consonant(note1, note2, include_fourths=True):
    """A consonance is a harmony, chord, or interval considered stable, as opposed \
to a dissonance (see `is_dissonant`). This function tests whether the given \
interval is consonant. This basically means that it checks whether the \
interval is (or sounds like) a unison, third, sixth, perfect fourth or \
perfect fifth. In classical music the fourth is considered dissonant when \
used contrapuntal, which is why you can choose to exclude it."""

    return is_perfect_consonant(note1, note2, include_fourths)\
         or is_imperfect_consonant(note1, note2)


def is_perfect_consonant(note1, note2, include_fourths=True):
    """Perfect consonances are either unisons, perfect fourths or fifths, or \
octaves (which is the same as a unison in this model; see the \
`container.Note` class for more). Perfect fourths are usually included as \
well, but are considered dissonant when used contrapuntal, which is why you \
can exclude them."""

    dhalf = measure(note1, note2)
    return dhalf in [0, 7] or include_fourths and dhalf == 5


def is_imperfect_consonant(note1, note2):
    """Imperfect consonances are either minor or major thirds or minor or major \
sixths."""

    return measure(note1, note2) in [3, 4, 8, 9]


def is_dissonant(note1, note2, include_fourths=False):
    """Tests whether an interval is considered unstable, dissonant. In the default \
case perfect fourths are considered consonant, but this can be changed with \
the `exclude_fourths` flag."""

    return not is_consonant(note1, note2, not include_fourths)


