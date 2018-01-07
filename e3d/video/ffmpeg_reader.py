"""
This module implements all the functions to read a video or a picture
using ffmpeg. It is quite ugly, as there are many pitfalls to avoid

Modified version, copied from
https://github.com/Zulko/moviepy/blob/master/moviepy/video/io/ffmpeg_reader.py
and
https://github.com/Zulko/moviepy/blob/master/moviepy/audio/io/readers.py
MIT license
"""

from __future__ import division

import subprocess as sp
from subprocess import DEVNULL
import re

import numpy as np
import warnings

import os
import datetime
import time


class FFMPEG_VideoReader:
    def __init__(self, filename, infos, bufsize=None, pix_fmt="rgb24", check_duration=True,
                 target_resolution=None, resize_algo='bicubic', fps_source='tbr', read1=False):

        self.filename = filename
        self.proc = None
        self.fps = infos['video_fps']
        self.size = infos['video_size']
        self.rotation = infos['video_rotation']

        if target_resolution:
            # revert the order, as ffmpeg used (width, height)
            target_resolution = target_resolution[1], target_resolution[0]

            if None in target_resolution:
                ratio = 1
                for idx, target in enumerate(target_resolution):
                    if target:
                        ratio = target / self.size[idx]
                self.size = (int(self.size[0] * ratio), int(self.size[1] * ratio))
            else:
                self.size = target_resolution
        self.resize_algo = resize_algo

        self.duration = infos['video_duration']
        self.ffmpeg_duration = infos['duration']
        self.nframes = infos['video_nframes']

        self.infos = infos

        self.pix_fmt = pix_fmt
        if 'rgba' or 'bgra'in pix_fmt:
            self.depth = 4
        else:
            self.depth = 3

        if bufsize is None:
            w, h = self.size
            bufsize = self.depth * w * h + 100

        self.bufsize = bufsize
        self.initialize()

        self.pos = 0
        if read1:
            self.lastread = self.read_frame()

    def initialize(self, starttime=0):
        """Opens the file, creates the pipe. """

        self.close()  # if any

        if starttime != 0:
            offset = min(1, starttime)
            i_arg = ['-ss', "%.06f" % (starttime - offset), '-hwaccel', 'vdpau', '-i', self.filename, '-ss', "%.06f" % offset]
        else:
            i_arg = ['-i', self.filename]

        # i_arg.extend('-hwaccel vdpau'.split())

        cmd = (['ffmpeg'] + i_arg + ['-loglevel', 'error', '-f', 'image2pipe', '-vf',
                                                         'scale=%d:%d' % tuple(self.size), '-sws_flags',
                                                         self.resize_algo, "-pix_fmt", self.pix_fmt, '-vcodec',
                                                         'rawvideo', '-'])
        popen_params = {"bufsize": self.bufsize, "stdout": sp.PIPE, "stderr": sp.PIPE, "stdin": DEVNULL}

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        self.proc = sp.Popen(cmd, **popen_params)

    def skip_frames(self, n=1):
        """Reads and throws away n frames """
        w, h = self.size
        # for i in range(n):
        self.proc.stdout.read(self.depth * w * h * n)
        # self.proc.stdout.flush()
        self.pos += n

    def read_frame(self):
        w, h = self.size
        nbytes = self.depth * w * h

        s = self.proc.stdout.read(nbytes)
        if len(s) != nbytes:

            warnings.warn("Warning: in file %s, " % (self.filename) + "%d bytes wanted but %d bytes read," % (
                nbytes, len(s)) + "at frame %d/%d, at time %.02f/%.02f sec. " % (
                              self.pos, self.nframes, 1.0 * self.pos / self.fps,
                              self.duration) + "Using the last valid frame instead.", UserWarning)

            if not hasattr(self, 'lastread'):
                raise IOError(("failed to read the first frame of "
                               "video file %s. That might mean that the file is "
                               "corrupted. That may also mean that you are using "
                               "a deprecated version of FFMPEG. On Ubuntu/Debian "
                               "for instance the version in the repos is deprecated. "
                               "Please update to a recent version from the website." +
                               '\n' + str(self.proc.stderr.read().decode())) % (self.filename))

            result = self.lastread

        else:
            self.pos += 1
            result = np.fromstring(s, dtype='uint8')
            # result.shape = (h, w, len(s) // (w * h))
            self.lastread = result

        return result

    def get_frame(self, t):
        """ Read a file video frame at time t.

        Note for coders: getting an arbitrary frame in the video with
        ffmpeg can be painfully slow if some decoding has to be done.
        This function tries to avoid fetching arbitrary frames
        whenever possible, by moving between adjacent frames.
        """

        # these definitely need to be rechecked sometime. Seems to work.

        # I use that horrible '+0.00001' hack because sometimes due to numerical
        # imprecisions a 3.0 can become a 2.99999999... which makes the int()
        # go to the previous integer. This makes the fetching more robust in the
        # case where you get the nth frame by writing get_frame(n/fps).

        pos = int(self.fps * t + 0.00001) + 1

        # Initialize proc if it is not open
        if not self.proc:
            self.initialize(t)
            self.pos = pos
            self.lastread = self.read_frame()

        if pos == self.pos:
            return self.lastread
        else:
            if (pos < self.pos) or (pos > self.pos + 100):
                self.initialize(t)
                self.pos = pos
            else:
                self.skip_frames(pos - self.pos - 1)
            result = self.read_frame()
            self.pos = pos
            return result

    def close(self):
        if self.proc:
            self.proc.terminate()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.proc.wait()
            self.proc = None
        if hasattr(self, 'lastread'):
            del self.lastread
            

def ffmpeg_parse_infos(filename, print_infos=False, check_duration=True, fps_source='tbr'):
    """Get file infos using ffmpeg.

    Returns a dictionnary with the fields:
    "video_found", "video_fps", "duration", "video_nframes",
    "video_duration", "audio_found", "audio_fps"

    "video_duration" is slightly smaller than "duration" to avoid
    fetching the uncomplete frames at the end, which raises an error.

    """

    # open the file in a pipe, provoke an error, read output
    cmd = ['ffmpeg', "-i", filename]

    popen_params = {"bufsize": 10 ** 5, "stdout": sp.PIPE, "stderr": sp.PIPE, "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)

    proc.stdout.readline()
    proc.terminate()
    infos = proc.stderr.read().decode('utf8')
    del proc

    if print_infos:
        # print the whole info text returned by FFMPEG
        print(infos)

    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError(("the file %s could not be found!\n"
                       "Please check that you entered the correct "
                       "path.") % filename)

    result = dict()

    # get duration (in seconds)
    result['duration'] = None

    if check_duration:
        try:
            keyword = 'Duration: '
            # for large GIFS the "full" duration is presented as the last element in the list.
            index = 0
            line = [l for l in lines if keyword in l][index]
            match = re.findall("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])", line)[0]
            result['duration'] = convertTime(match)
        except Exception as Ex:
            raise IOError((str(Ex) + " failed to read the duration of file %s.\n"
                           "Here are the file infos returned by ffmpeg:\n\n%s") % (filename, infos))

    # get the output line that speaks about video
    lines_video = [l for l in lines if ' Video: ' in l and re.search('\d+x\d+', l)]

    result['video_found'] = (lines_video != [])

    if result['video_found']:
        try:
            line = lines_video[0]

            # get the size, of the form 460x320 (w x h)
            match = re.search(" [0-9]*x[0-9]*(,| )", line)
            s = list(map(int, line[match.start():match.end() - 1].split('x')))
            result['video_size'] = s
        except Exception:
            raise IOError(("failed to read video dimensions in file %s.\n"
                           "Here are the file infos returned by ffmpeg:\n\n%s") % (filename, infos))

        # Get the frame rate. Sometimes it's 'tbr', sometimes 'fps', sometimes
        # tbc, and sometimes tbc/2...
        # Current policy: Trust tbr first, then fps unless fps_source is
        # specified as 'fps' in which case try fps then tbr

        # If result is near from x*1000/1001 where x is 23,24,25,50,
        # replace by x*1000/1001 (very common case for the fps).

        def get_tbr():
            match = re.search("( [0-9]*.| )[0-9]* tbr", line)

            # Sometimes comes as e.g. 12k. We need to replace that with 12000.
            s_tbr = line[match.start():match.end()].split(' ')[1]
            if "k" in s_tbr:
                tbr = float(s_tbr.replace("k", "")) * 1000
            else:
                tbr = float(s_tbr)
            return tbr

        def get_fps():
            match = re.search("( [0-9]*.| )[0-9]* fps", line)
            fps = float(line[match.start():match.end()].split(' ')[1])
            return fps

        if fps_source == 'tbr':
            try:
                result['video_fps'] = get_tbr()
            except:
                result['video_fps'] = get_fps()

        elif fps_source == 'fps':
            try:
                result['video_fps'] = get_fps()
            except:
                result['video_fps'] = get_tbr()

        # It is known that a fps of 24 is often written as 24000/1001
        # but then ffmpeg nicely rounds it to 23.98, which we hate.
        coef = 1000.0 / 1001.0
        fps = result['video_fps']
        for x in [23, 24, 25, 30, 50]:
            if (fps != x) and abs(fps - x * coef) < .01:
                result['video_fps'] = x * coef

        if check_duration:
            result['video_nframes'] = int(result['duration'] * result['video_fps']) + 1
            result['video_duration'] = result['duration']
        else:
            result['video_nframes'] = 1
            result['video_duration'] = None
        # We could have also recomputed the duration from the number
        # of frames, as follows:
        # >>> result['video_duration'] = result['video_nframes'] / result['video_fps']

        # get the video rotation info.
        try:
            rotation_lines = [l for l in lines if 'rotate          :' in l and re.search('\d+$', l)]
            if len(rotation_lines):
                rotation_line = rotation_lines[0]
                match = re.search('\d+$', rotation_line)
                result['video_rotation'] = int(rotation_line[match.start(): match.end()])
            else:
                result['video_rotation'] = 0
        except Exception:
            raise IOError(("failed to read video rotation in file %s.\n"
                           "Here are the file infos returned by ffmpeg:\n\n%s") % (filename, infos))

    lines_audio = [l for l in lines if ' Audio: ' in l]

    result['audio_found'] = lines_audio != []

    if result['audio_found']:
        line = lines_audio[0]
        try:
            match = re.search(" [0-9]* Hz", line)
            result['audio_fps'] = int(line[match.start() + 1:match.end()])
        except Exception:
            result['audio_fps'] = 'unknown'

    return result


class FFMPEG_AudioReader:
    """
    A class to read the audio in either video files or audio files
    using ffmpeg. ffmpeg will read any audio and transform them into
    raw data.

    Parameters
    ------------

    filename
      Name of any video or audio file, like ``video.mp4`` or
      ``sound.wav`` etc.

    buffersize
      The size of the buffer to use. Should be bigger than the buffer
      used by ``to_audiofile``

    print_infos
      Print the ffmpeg infos on the file being read (for debugging)

    fps
      Desired frames per second in the decoded signal that will be
      received from ffmpeg

    nbytes
      Desired number of bytes (1,2,4) in the signal that will be
      received from ffmpeg

    """

    def __init__(self, filename, buffersize, print_infos=False, fps=44100, nbytes=2, nchannels=2):

        self.filename = filename
        self.nbytes = nbytes
        self.fps = fps
        self.f = 's%dle' % (8 * nbytes)
        self.acodec = 'pcm_s%dle' % (8 * nbytes)
        self.nchannels = nchannels
        infos = ffmpeg_parse_infos(filename)
        self.duration = infos['duration']
        if 'video_duration' in infos:
            self.duration = infos['video_duration']
        else:
            self.duration = infos['duration']
        self.infos = infos
        self.proc = None
        self.pos = 0
        self.nframes = int(self.fps * self.duration)
        self.buffersize = min(self.nframes + 1, buffersize)
        self.buffer = None
        self.buffer_startframe = 1
        self.initialize()
        self.buffer_around(1)
        if print_infos:
            print(self.proc.stderr.read())

    def initialize(self, starttime=0):
        """ Opens the file, creates the pipe. """

        self.close_proc()  # if any

        if starttime != 0:
            offset = min(1, starttime)
            i_arg = ["-ss", "%.05f" % (starttime - offset), '-i', self.filename, '-vn', "-ss", "%.05f" % offset]
        else:
            i_arg = ['-i', self.filename, '-vn']

        cmd = (
        ['ffmpeg'] + i_arg + ['-loglevel', 'error', '-f', self.f, '-acodec', self.acodec, '-ar',
                                                  "%d" % self.fps, '-ac', '%d' % self.nchannels, '-'])

        popen_params = {"bufsize": self.buffersize, "stdout": sp.PIPE, "stderr": sp.PIPE, "stdin": DEVNULL}

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        self.proc = sp.Popen(cmd, **popen_params)

        self.pos = np.round(self.fps * starttime)

    def skip_chunk(self, chunksize):
        s = self.proc.stdout.read(self.nchannels * chunksize * self.nbytes)
        self.proc.stdout.flush()
        self.pos = self.pos + chunksize

    def read_chunk(self, chunksize):
        # chunksize is not being autoconverted from float to int
        chunksize = int(round(chunksize))
        L = self.nchannels * chunksize * self.nbytes
        s = self.proc.stdout.read(L)
        # dt = {1: 'uint8', 2: 'int16', 4: 'int32'}[self.nbytes]
        # result = np.fromstring(s, dtype=dt)
        # result = (1.0 * result / 2 ** (8 * self.nbytes - 1)). \
        #         reshape((int(len(result) / self.nchannels), self.nchannels))
        # # self.proc.stdout.flush()
        self.pos = self.pos + chunksize
        return s

    def seek(self, pos):
        """
        Reads a frame at time t. Note for coders: getting an arbitrary
        frame in the video with ffmpeg can be painfully slow if some
        decoding has to be done. This function tries to avoid fectching
        arbitrary frames whenever possible, by moving between adjacent
        frames.
        """
        if (pos < self.pos) or (pos > (self.pos + 1000000)):
            t = 1.0 * pos / self.fps
            self.initialize(t)
        elif pos > self.pos:
            # print pos
            self.skip_chunk(pos - self.pos)
        # last case standing: pos = current pos
        self.pos = pos

    def close_proc(self):
        if hasattr(self, 'proc') and self.proc is not None:
            self.proc.terminate()
            for std in [self.proc.stdout, self.proc.stderr]:
                std.close()
            self.proc = None

    def get_frame(self, tt):

        buffersize = self.buffersize
        if isinstance(tt, np.ndarray):
            # lazy implementation, but should not cause problems in
            # 99.99 %  of the cases


            # elements of t that are actually in the range of the
            # audio file.
            in_time = (tt >= 0) & (tt < self.duration)

            # Check that the requested time is in the valid range
            if not in_time.any():
                raise IOError("Error in file %s, " % (self.filename) + "Accessing time t=%.02f-%.02f seconds, " % (
                tt[0], tt[-1]) + "with clip duration=%d seconds, " % self.duration)

            # The np.round in the next line is super-important.
            # Removing it results in artifacts in the noise.
            frames = np.round((self.fps * tt)).astype(int)[in_time]
            fr_min, fr_max = frames.min(), frames.max()

            if not (0 <= (fr_min - self.buffer_startframe) < len(self.buffer)):
                self.buffer_around(fr_min)
            elif not (0 <= (fr_max - self.buffer_startframe) < len(self.buffer)):
                self.buffer_around(fr_max)

            try:
                result = np.zeros((len(tt), self.nchannels))
                indices = frames - self.buffer_startframe
                if len(self.buffer) < self.buffersize // 2:
                    indices = indices - (self.buffersize // 2 - len(self.buffer) + 1)
                result[in_time] = self.buffer[indices]
                return result

            except IndexError as error:
                warnings.warn("Error in file %s, " % (self.filename) + "At time t=%.02f-%.02f seconds, " % (
                tt[0], tt[-1]) + "indices wanted: %d-%d, " % (indices.min(), indices.max()) + "but len(buffer)=%d\n" % (
                              len(self.buffer)) + str(error), UserWarning)

                # repeat the last frame instead
                indices[indices >= len(self.buffer)] = len(self.buffer) - 1
                result[in_time] = self.buffer[indices]
                return result

        else:

            ind = int(self.fps * tt)
            if ind < 0 or ind > self.nframes:  # out of time: return 0
                return np.zeros(self.nchannels)

            if not (0 <= (ind - self.buffer_startframe) < len(self.buffer)):
                # out of the buffer: recenter the buffer
                self.buffer_around(ind)

            # read the frame in the buffer
            return self.buffer[ind - self.buffer_startframe]

    def buffer_around(self, framenumber):
        """
        Fills the buffer with frames, centered on ``framenumber``
        if possible
        """

        # start-frame for the buffer
        new_bufferstart = max(0, framenumber - self.buffersize // 2)

        if self.buffer is not None:
            current_f_end = self.buffer_startframe + self.buffersize
            if new_bufferstart < current_f_end < new_bufferstart + self.buffersize:
                # We already have one bit of what must be read
                conserved = current_f_end - new_bufferstart + 1
                chunksize = self.buffersize - conserved
                array = self.read_chunk(chunksize)
                self.buffer = np.vstack([self.buffer[-conserved:], array])
            else:
                self.seek(new_bufferstart)
                self.buffer = self.read_chunk(self.buffersize)
        else:
            self.seek(new_bufferstart)
            self.buffer = self.read_chunk(self.buffersize)

        self.buffer_startframe = new_bufferstart

    def __del__(self):
        # If the garbage collector comes, make sure the subprocess is terminated.
        self.close_proc()


def convertTime(timeStr):
    # https://stackoverflow.com/a/10663851
    main, remain = timeStr.split('.')
    x = time.strptime(main, '%H:%M:%S')
    res = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    return res + float('.' + remain)
