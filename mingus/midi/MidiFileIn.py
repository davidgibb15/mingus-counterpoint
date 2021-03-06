#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

================================================================================

    mingus - Music theory Python package, MIDI File In
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

   MidiFileIn is a module that can read a MIDI file and convert it into
   mingus.containers objects.

================================================================================
"""

import mingus.containers.Note as Note
import mingus.containers.NoteContainer as NoteContainer
import mingus.containers.Bar as Bar
import mingus.containers.Track as Track
import mingus.containers.Composition as Composition
from mingus.containers.Instrument import MidiInstrument
import mingus.core.notes as notes
import mingus.core.intervals as intervals
import binascii


def MIDI_to_Composition(file):
    """Converts a MIDI file to a mingus.containers.Composition and returns it in a \
tuple with the last used tempo in beats per minute (this will change in the \
future). This function can raise all kinds of exceptions (IOError, \
HeaderError, TimeDivisionError, FormatError), so be sure to try and catch."""

    m = MidiFile()
    return m.MIDI_to_Composition(file)


class HeaderError(Exception):

    pass


class TimeDivisionError(Exception):

    pass


class FormatError(Exception):

    pass


class MidiFile:

    """This class parses a MIDI file."""

    bpm = 120
    meter = (4, 4)
    bytes_read = 0

    def MIDI_to_Composition(self, file):
        (header, track_data) = self.parse_midi_file(file)
        c = Composition()
        if header[2]['fps']:
            print "Don't know how to parse this yet"
            return c
        ticks_per_beat = header[2]['ticks_per_beat']

        for track in track_data:
            # this loop will gather data for all notes,
            # set up keys and time signatures for all bars
            # and set the tempo and instrument for the track.

            metronome = 1  # Tick once every quarter note
            thirtyseconds = 8  # 8 thirtyseconds in a quarter note
            step = 256.0 # WARNING: Assumes our smallest desired quantization step is a 256th note.

            meter = (4, 4)
            key = 'C'
            bar = 0
            beat = 0
            now = (bar, beat)
            b = None

            started_notes = {}
            finished_notes = {}
            b = Bar(key=key, meter=meter)
            bars = [b]

            bpm = None
            instrument = None
            track_name = None

            for deltatime, event in track:
                if deltatime != 0:
                    duration = (ticks_per_beat * 4.0) / float(deltatime)

                    dur_q = int(round(step/duration))
                    length_q = int(b.length * step)

                    o_bar = bar
                    c_beat = beat + dur_q
                    bar += int(c_beat / length_q)
                    beat = c_beat % length_q

                    while o_bar < bar:
                        o_bar += 1
                        o_key = b.key
                        b = Bar(key=key, meter=meter)
                        b.key = o_key
                        bars.append(b)

                    now = (bar, beat)

                if event['event'] == 8:
                # note off
                    channel = event['channel']
                    note_int = event['param1']
                    velocity = event['param2']
                    note_name = notes.int_to_note(note_int % 12)
                    octave = note_int / 12 - 1

                    note = Note(note_name, octave)
                    note.channel = channel
                    note.velocity = velocity

                    x = (channel, note_int)
                    start_time = started_notes[x]
                    del started_notes[x]
                    end_time = now

                    y = (start_time, end_time)
                    if y not in finished_notes:
                        finished_notes[y] = []

                    finished_notes[y].append(note)

                elif event['event'] == 9:
                # note on
                    channel = event['channel']
                    note_int = event['param1']
                    velocity = event['param2']
                    x = (channel, note_int)

                    # add the note to the current NoteContainer
                    started_notes[x] = now

                elif event['event'] == 10:
                # note aftertouch
                    pass

                elif event['event'] == 11:
                # controller select
                    pass

                elif event['event'] == 12:
                # program change
                # WARNING: only the last change in instrument will get saved.
                    i = MidiInstrument()
                    i.instrument_nr = event['param1']
                    instrument = i

                elif event['event'] == 0x0f:
                # meta event Text
                    if event['meta_event'] == 1:
                        pass

                    elif event['meta_event'] == 3:
                    # Track name
                        track_name = event['data']

                    elif event['meta_event'] == 6:
                    # Marker
                        pass

                    elif event['meta_event'] == 7:
                    # Cue Point
                        pass

                    elif event['meta_event'] == 47:
                    # End of Track
                        pass

                    elif event['meta_event'] == 81:
                    # Set tempo
                    # WARNING: Only the last change in bpm will get saved
                        mpqn = self.bytes_to_int(event['data'])
                        bpm_o = bpm
                        bpm = 60000000 / mpqn

                    elif event['meta_event'] == 88:
                    # Time Signature
                        d = event['data']
                        thirtyseconds = self.bytes_to_int(d[3])
                        metronome = self.bytes_to_int(d[2]) / 24.0
                        denom = 2 ** self.bytes_to_int(d[1])
                        numer = self.bytes_to_int(d[0])
                        meter = (numer, denom)
                        b.set_meter(meter)

                    elif event['meta_event'] == 89:
                    # Key Signature
                        d = event['data']
                        sharps = self.bytes_to_int(d[0])
                        minor = self.bytes_to_int(d[0])
                        if minor:
                            key = 'A'
                        else:
                            key = 'C'
                        for i in xrange(abs(sharps)):
                            if sharps < 0:
                                key = intervals.major_fourth(key)
                            else:
                                key = intervals.major_fifth(key)
                        b.key = Note(key)

                    else:
                        print 'Unsupported META event', event['meta_event']

                else:
                    print 'Unsupported MIDI event', event

            t = Track(instrument)
            t.name = track_name

            sorted_notes = {}

            # sort the notes (so they are added to the bars in order)
            # this loop will also split up notes that span more than one bar.
            for x in finished_notes:
                (start_bar, start_beat), (end_bar, end_beat) = x
                if end_beat == 0:
                    end_bar -= 1
                    end_beat = int(bars[end_bar].length * step)

                while start_bar <= end_bar:
                    nc = NoteContainer(finished_notes[x])
                    b = bars[start_bar]

                    if start_bar < end_bar:
                        # only executes when note spans more than one bar.
                        length_q = int(b.length * step)
                        dur = int(step/(length_q - start_beat))
                    else:
                        # always executes - add the final section of this note.
                        dur = int(step/(end_beat-start_beat))

                    if start_beat != 0:
                        at = float(start_beat)/step
                    else:
                        at = 0.0

                    if start_bar not in sorted_notes:
                        sorted_notes[start_bar] = {}
                    if at not in sorted_notes[start_bar]:
                        sorted_notes[start_bar][at] = (dur, nc)

                    # set our offsets for the next loop
                    start_beat = 0
                    start_bar += 1

            # add all notes to all bars in order.
            for start_bar in sorted(sorted_notes.keys()):
                for at in sorted(sorted_notes[start_bar].keys()):
                    dur, nc = sorted_notes[start_bar][at]
                    bars[start_bar].place_notes_at(nc, dur, at)

            # add the bars to the track, in order
            for b in bars:
                b.fill_with_rests()
                t + b

            # add the track to the composition
            c.tracks.append(t)

        return (c, bpm)

    def parse_midi_file_header(self, fp):
        """Reads the header of a MIDI file and returns a touple containing the \
format type, number of tracks and parsed time division information"""

        # Check header

        try:
            if fp.read(4) != 'MThd':
                raise HeaderError, 'Not a valid MIDI file header. Byte %d.'\
                     % self.bytes_read
            self.bytes_read += 4
        except:
            raise IOError, "Couldn't read from file."

        # Parse chunk size

        try:
            chunk_size = self.bytes_to_int(fp.read(4))
            self.bytes_read += 4
        except:
            raise IOError, "Couldn't read chunk size from file. Byte %d."\
                 % self.bytes_read

        # Expect chunk size to be at least 6

        if chunk_size < 6:
            return False
        try:
            format_type = self.bytes_to_int(fp.read(2))
            self.bytes_read += 2
            if format_type not in [0, 1, 2]:
                raise FormatError, '%d is not a valid MIDI format.'\
                     % format_type
        except:
            raise IOError, "Couldn't read format type from file."
        try:
            number_of_tracks = self.bytes_to_int(fp.read(2))
            time_division = self.parse_time_division(fp.read(2))
            self.bytes_read += 4
        except:
            raise IOError, \
                "Couldn't read number of tracks and/or time division from tracks."

        chunk_size -= 6
        if chunk_size % 2 == 1:
            raise FormatError, "Won't parse this."
        fp.read(chunk_size / 2)
        self.bytes_read += chunk_size / 2
        return (format_type, number_of_tracks, time_division)

    def bytes_to_int(self, bytes):
        return int(binascii.b2a_hex(bytes), 16)

    def parse_time_division(self, bytes):
        """Parses the time division found in the header of a MIDI file and returns \
a dictionairy with the boolean fps set to indicate whether to use frames \
per second or ticks per beat. If fps is True, the values SMPTE_frames \
and clock_ticks will also be set. If fps is False, ticks_per_beat will \
hold the value."""

        # If highest bit is set, time division is set in frames per second
        # otherwise in ticks_per_beat

        value = self.bytes_to_int(bytes)
        if not value & 0x8000:
            return {'fps': False, 'ticks_per_beat': value & 0x7FFF}
        else:
            SMPTE_frames = (value & 0x7F00) >> 2
            if SMPTE_frames not in [24, 25, 29, 30]:
                raise TimeDivisionError, \
                    "'%d' is not a valid value for the number of SMPTE frames"\
                     % SMPTE_frames
            clock_ticks = (value & 0x00FF) >> 2
            return {'fps': True, 'SMPTE_frames': SMPTE_frames,
                    'clock_ticks': clock_ticks}

    def parse_track(self, fp):
        """Parses a MIDI track from its header to its events. And returns a list of \
events and the number of bytes that were read."""

        events = []
        chunk_size = self.parse_track_header(fp)
        bytes = chunk_size
        while chunk_size > 0:
            (delta_time, chunk_delta) = self.parse_varbyte_as_int(fp)
            chunk_size -= chunk_delta
            (event, chunk_delta) = self.parse_midi_event(fp)
            chunk_size -= chunk_delta
            events.append([delta_time, event])
        if chunk_size < 0:
            print 'yikes.', self.bytes_read, chunk_size
        return events

    def parse_midi_event(self, fp):
        """Parses a MIDI event. Returns a dictionary and a the number of bytes \
read."""

        chunk_size = 0
        try:
            ec = self.bytes_to_int(fp.read(1))
            chunk_size += 1
            self.bytes_read += 1
        except:
            raise IOError, \
                "Couldn't read event type and channel data from file."

        # Get the nibbles

        event_type = (ec & 0xf0) >> 4
        channel = ec & 0x0f

        # I don't know what these events are supposed to do, but I keep finding
        # them. The parser ignores them.

        if event_type < 8:
            raise FormatError, 'Unknown event type %d. Byte %d.' % (event_type,
                    self.bytes_read)

        # Meta events can have strings of variable length

        if event_type == 0x0f:
            try:
                meta_event = self.bytes_to_int(fp.read(1))
                (length, chunk_delta) = self.parse_varbyte_as_int(fp)
                data = fp.read(length)
                chunk_size += 1 + chunk_delta + length
                self.bytes_read += 1 + length
            except:
                raise IOError, "Couldn't read meta event from file."
            return ({'event': event_type, 'meta_event': meta_event, 'data'
                    : data}, chunk_size)
        elif event_type in [12, 13]:

        # Program change and Channel aftertouch events only have one parameter

            try:
                param1 = fp.read(1)
                chunk_size += 1
                self.bytes_read += 1
            except:
                raise IOError, "Couldn't read MIDI event parameters from file."
            param1 = self.bytes_to_int(param1)
            return ({'event': event_type, 'channel': channel, 'param1'
                    : param1}, chunk_size)
        else:
            try:
                param1 = fp.read(1)
                param2 = fp.read(1)
                chunk_size += 2
                self.bytes_read += 2
            except:
                raise IOError, "Couldn't read MIDI event parameters from file."
            param1 = self.bytes_to_int(param1)
            param2 = self.bytes_to_int(param2)
            return ({
                'event': event_type,
                'channel': channel,
                'param1': param1,
                'param2': param2,
                }, chunk_size)

    def parse_track_header(self, fp):
        """Returns the size of the track chunk."""

        # Check the header

        try:
            h = fp.read(4)
            self.bytes_read += 4
        except:
            raise IOError, "Couldn't read track header from file. Byte %d."\
                 % self.bytes_read
        if h != 'MTrk':
            raise HeaderError, 'Not a valid Track header. Byte %d.'\
                 % self.bytes_read

        # Parse the size of the header

        try:
            chunk_size = fp.read(4)
            self.bytes_read += 4
        except:
            raise IOError, "Couldn't read track chunk size from file."
        chunk_size = self.bytes_to_int(chunk_size)
        return chunk_size

    def parse_midi_file(self, file):
        """Parses a MIDI file. Returns the header -as a tuple containing \
respectively the MIDI format, the number of tracks and the time \
division-, the parsed track data and the number of bytes read"""

        try:
            f = open(file, 'r')
        except:
            raise IOError, 'File not found'
        self.bytes_read = 0
        header = self.parse_midi_file_header(f)
        tracks = header[1]
        result = []
        while tracks > 0:
            events = self.parse_track(f)
            result.append(events)
            tracks -= 1
        f.close()
        return (header, result)

    def parse_varbyte_as_int(self, fp, return_bytes_read=True):
        """Reads a variable length byte from the file and returns the corresponding \
integer."""

        result = 0
        bytes_read = 0
        r = 0x80
        while r & 0x80:
            try:
                r = self.bytes_to_int(fp.read(1))
                self.bytes_read += 1
            except:
                (IOError, "Couldn't read variable length byte from file.")
            if r & 0x80:
                result = (result << 7) + (r & 0x7F)
            else:
                result = (result << 7) + r
            bytes_read += 1
        if not return_bytes_read:
            return result
        else:
            return (result, bytes_read)


if __name__ == '__main__':
    from sys import argv
    import fluidsynth
    import MidiFileOut
    fluidsynth.init()
    (m, bpm) = MIDI_to_Composition(argv[1])
    MidiFileOut.write_Composition('test.mid', m, bpm)

