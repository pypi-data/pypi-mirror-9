# codplayer - test (parts of) the audio module
#
# Copyright 2013 Peter Liljenberg <peter.liljenberg@gmail.com>
#
# Distributed under an MIT license, please see LICENSE in the top dir.

import unittest

from .. import audio, model
from .. import toc

class DummyDisc:
    audio_format = model.PCM

class TestAudioPacket(unittest.TestCase):

    def test_no_pregap_or_index(self):

        t = model.DbTrack()
        t.file_offset = 5000
        t.length = 50000

        p = audio.AudioPacket(DummyDisc, t, 7, 2000, 1000)

        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 7)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, 2000)
        self.assertEqual(p.rel_pos, 2000)
        self.assertEqual(p.length, 1000)
        self.assertEqual(p.file_pos, 5000 + 2000)
        self.assertEqual(p.flags, 0)

        
    def test_pregap_and_index(self):

        t = model.DbTrack()
        t.file_offset = 5000
        t.length = 50000
        t.pregap_offset = 3000
        t.index = [8000, 15000]

        # In pregap
        p = audio.AudioPacket(DummyDisc, t, 0, 2000, 1000)

        self.assertEqual(p.index, 0)
        self.assertEqual(p.abs_pos, 2000)
        self.assertEqual(p.rel_pos, -1000)
        self.assertEqual(p.file_pos, 5000 + 2000)

        # Index 1, normal part of track
        p = audio.AudioPacket(DummyDisc, t, 0, 4000, 1000)

        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, 4000)
        self.assertEqual(p.rel_pos, 1000)
        self.assertEqual(p.file_pos, 5000 + 4000)
        
        # Index 2
        p = audio.AudioPacket(DummyDisc, t, 0, 10000, 1000)

        self.assertEqual(p.index, 2)
        self.assertEqual(p.abs_pos, 10000)
        self.assertEqual(p.rel_pos, 7000)
        self.assertEqual(p.file_pos, 5000 + 10000)

        # Index 3
        p = audio.AudioPacket(DummyDisc, t, 0, 15000, 1000)

        self.assertEqual(p.index, 3)
        self.assertEqual(p.abs_pos, 15000)
        self.assertEqual(p.rel_pos, 12000)
        self.assertEqual(p.file_pos, 5000 + 15000)
        
        
    def test_silent_pregap(self):

        t = model.DbTrack()
        t.file_offset = 5000
        t.length = 50000
        t.pregap_offset = 3000
        t.pregap_silence = 2000

        # In silent part of pregap
        p = audio.AudioPacket(DummyDisc, t, 0, 1000, 1000)

        self.assertEqual(p.index, 0)
        self.assertEqual(p.abs_pos, 1000)
        self.assertEqual(p.rel_pos, -2000)
        self.assertEqual(p.file_pos, None)
        
        # In disc part of pregap
        p = audio.AudioPacket(DummyDisc, t, 0, 2500, 500)

        self.assertEqual(p.index, 0)
        self.assertEqual(p.abs_pos, 2500)
        self.assertEqual(p.rel_pos, -500)
        self.assertEqual(p.file_pos, 5000 + 500)
        

class TestAudioSplitter(unittest.TestCase):

    def test_unedited_disc(self):

        toc_data = '''
// First track have pregap silence (which will be ignored anyway)
TRACK AUDIO
TWO_CHANNEL_AUDIO
SILENCE 00:00:40
FILE "data.cdr" 0 00:01:00
START 00:00:40


// Second track have pregap from file
TRACK AUDIO
NO COPY
NO PRE_EMPHASIS
TWO_CHANNEL_AUDIO
FILE "data.cdr" 00:01:00 00:01:00
START 00:00:30


// Third track have no pregap
TRACK AUDIO
NO COPY
NO PRE_EMPHASIS
TWO_CHANNEL_AUDIO
FILE "data.cdr" 00:02:00 00:00:17
'''
        
        disc = toc.parse_toc(toc_data, 'testId')

        # Work with three packets per second, i.e. 25 frames per
        # packet, to make the test case reasonably easy to write
        splitter = audio.AudioPacket.iterate(disc, 0, 3)
        
        def ftos(frames): return frames * model.PCM.audio_frames_per_cd_frame


        # First track will result in three audio packets (1 second of
        # sound)
        t = disc.tracks[0]

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 0)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, ftos(40))
        self.assertEqual(p.rel_pos, 0)
        self.assertEqual(p.length, ftos(25))
        self.assertEqual(p.file_pos, 0)
        self.assertEqual(p.flags, 0)

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 0)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, ftos(40 + 25))
        self.assertEqual(p.rel_pos, ftos(25))
        self.assertEqual(p.length, ftos(25))
        self.assertEqual(p.file_pos, ftos(25))
        self.assertEqual(p.flags, 0)

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 0)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, ftos(40 + 50))
        self.assertEqual(p.rel_pos, ftos(50))
        self.assertEqual(p.length, ftos(25))
        self.assertEqual(p.file_pos, ftos(50))
        self.assertEqual(p.flags, 0)


        # Second track will result in 25+5 frames pregap packet and
        # 25+20 frames main packets

        t = disc.tracks[1]

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 1)
        self.assertEqual(p.index, 0)
        self.assertEqual(p.abs_pos, 0)
        self.assertEqual(p.rel_pos, ftos(-30))
        self.assertEqual(p.length, ftos(25))
        self.assertEqual(p.file_pos, ftos(75))
        self.assertEqual(p.flags, 0)

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 1)
        self.assertEqual(p.index, 0)
        self.assertEqual(p.abs_pos, ftos(25))
        self.assertEqual(p.rel_pos, ftos(-5))
        self.assertEqual(p.length, ftos(5))
        self.assertEqual(p.file_pos, ftos(75 + 25))
        self.assertEqual(p.flags, 0)

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 1)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, ftos(30))
        self.assertEqual(p.rel_pos, 0)
        self.assertEqual(p.length, ftos(25))
        self.assertEqual(p.file_pos, ftos(75 + 30))
        self.assertEqual(p.flags, 0)

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 1)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, ftos(55))
        self.assertEqual(p.rel_pos, ftos(25))
        self.assertEqual(p.length, ftos(20))
        self.assertEqual(p.file_pos, ftos(75 + 55))
        self.assertEqual(p.flags, 0)


        # Third track will just be a 17 frame packet
        t = disc.tracks[2]

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t)
        self.assertEqual(p.track_number, 2)
        self.assertEqual(p.index, 1)
        self.assertEqual(p.abs_pos, 0)
        self.assertEqual(p.rel_pos, 0)
        self.assertEqual(p.length, ftos(17))
        self.assertEqual(p.file_pos, ftos(150))
        self.assertEqual(p.flags, 0)

        # Reached end of disc
        with self.assertRaises(StopIteration):
            splitter.next()


    def test_pause_after_track(self):
        # Simple disc with two tracks, pause after first
        disc = model.DbDisc()
        disc.audio_format = model.PCM

        t1 = model.DbTrack()
        t1.number = 1
        t1.length = t1.file_length = model.PCM.rate * 2
        t1.pause_after = True
        disc.tracks.append(t1)

        t2 = model.DbTrack()
        t2.number = 2
        t2.length = t2.file_length = model.PCM.rate
        t2.pause_after = True
        disc.tracks.append(t2)

        # Run 1s per packet
        splitter = audio.AudioPacket.iterate(disc, 0, 1)

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t1)
        self.assertEqual(p.abs_pos, 0)
        self.assertEqual(p.length, model.PCM.rate)
        self.assertEqual(p.flags, 0,
                         'should not pause in middle of track')

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t1)
        self.assertEqual(p.abs_pos, model.PCM.rate)
        self.assertEqual(p.length, model.PCM.rate)
        self.assertEqual(p.flags, p.PAUSE_AFTER,
                         'should pause after first track')

        p = splitter.next()
        self.assertIsNotNone(p)
        self.assertIs(p.track, t2)
        self.assertEqual(p.abs_pos, 0)
        self.assertEqual(p.length, model.PCM.rate)
        self.assertEqual(p.flags, 0,
                         'should not pause after last track')

        # Reached end of disc
        with self.assertRaises(StopIteration):
            splitter.next()

