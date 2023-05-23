from __future__ import annotations
import re
from AutoSub import logger


class SubtitleLine:
    def __init__(self, subtitle_number, text, start_time, end_time):
        self.subtitle_number = subtitle_number
        self.text = text
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return str(self.subtitle_number) + '\n' + \
            Subtitles._convert_second(self.start_time) + " --> " + \
            Subtitles._convert_second(self.end_time) + "\n" + \
            self.text


class Subtitles:
    def __init__(self):
        self.lines = []

    @staticmethod
    def from_str(srt_string):
        s = Subtitles()
        s.lines = Subtitles.parse_srt(srt_string)
        return s

    @staticmethod
    def parse_srt(srt_string):
        subtitles = []

        # Split the SRT string into individual subtitle blocks
        subtitle_blocks = re.split(r'\n\s*\n', srt_string.strip())

        for block in subtitle_blocks:
            # Extract the subtitle number, times, and text using regex
            match = re.fullmatch(
                r'\s*(?P<number>\d+)\s*(?P<s_HH>\d{2}):(?P<s_MM>\d{2}):(?P<s_SS>\d{2}),(?P<s_ms>\d{3})\s*'
                r'-->\s*(?P<e_HH>\d{2}):(?P<e_MM>\d{2}):(?P<e_SS>\d{2}),(?P<e_ms>\d{3})\s*(?P<text>.+)\s*', block,
                re.DOTALL)
            if match:
                subtitle_number = int(match.group("number"))
                start_time = int(match.group('s_HH')) * 3600 + int(match.group('s_MM')) * 60 + int(
                    match.group('s_SS')) + int(match.group('s_ms')) / 1000
                end_time = int(match.group('e_HH')) * 3600 + int(match.group('e_MM')) * 60 + int(
                    match.group('e_SS')) + int(match.group('e_ms')) / 1000
                text = match.group('text').strip()

                # ignore empty line.
                if start_time == end_time:
                    continue

                # Check for overlapping times
                if subtitles:
                    last_line = subtitles[-1]
                    if last_line.end_time > start_time:
                        raise Exception("Overlapping times in SRT")
                    if last_line.subtitle_number + 1 != subtitle_number:
                        print(srt_string)
                        raise Exception("Incorrect subtitle number sequence")

                # Create the subtitle line and add it to the list
                line = SubtitleLine(subtitle_number, text, start_time, end_time)
                subtitles.append(line)
            else:
                # The block does not match the expected SRT format
                raise Exception("Invalid SRT format @ " + block)

        return subtitles

    def add_line(self, subtitle_number, text, start_time, end_time):
        line = SubtitleLine(subtitle_number, text, start_time, end_time)
        self.lines.append(line)

    def add_subline(self, subline):
        self.lines.append(subline)

    def resemble(self, other: Subtitles):
        if len(self.lines) != len(other.lines):
            logger.debug("sanity check 2 err msg : lines count not match, input srt have " + int(len(other.lines)) +
                         " while output have " + int(len(self.lines)))
            return False

        for line_self, line_other in zip(self.lines, other.lines):
            if line_self.start_time != line_other.start_time:
                logger.debug("sanity check 2 err msg : start time not match.")
                logger.debug("output line : " + str(line_self))
                logger.debug("input line : " + str(line_other))
                return False
            elif line_self.end_time != line_other.end_time:
                logger.debug("sanity check 2 err msg : end time not match.")
                logger.debug("output line : " + str(line_self))
                logger.debug("input line : " + str(line_other))
                return False
            elif line_self.subtitle_number != line_other.subtitle_number:
                logger.debug("sanity check 2 err msg : end time not match.")
                logger.debug("output line : " + str(line_self))
                logger.debug("input line : " + str(line_other))
                return False

        return True

    @staticmethod
    def _convert_second(seconds):
        assert seconds >= 0, "non-negative timestamp expected"
        milliseconds = round(seconds * 1000.0)

        hours = milliseconds // 3_600_000
        milliseconds -= hours * 3_600_000

        minutes = milliseconds // 60_000
        milliseconds -= minutes * 60_000

        seconds = milliseconds // 1_000
        milliseconds -= seconds * 1_000

        return (
            f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
        )

    def __str__(self):
        return ''.join(str(line) + "\n\n" for line in self.lines)

    def start_time(self, default):
        if len(self.lines) == 0:
            return default
        else:
            return self.lines[0].start_time

    def start_time_fmt(self):
        if len(self.lines) == 0:
            return ''
        else:
            return Subtitles._convert_second(self.lines[0].start_time)

    def end_time(self, default):
        if len(self.lines) == 0:
            return default
        else:
            return self.lines[-1].end_time

    def end_time_fmt(self):
        if len(self.lines) == 0:
            return ''
        else:
            return Subtitles._convert_second(self.lines[-1].end_time)