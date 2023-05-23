import unittest
from AutoSub.srt_tools import Subtitles, SubtitleLine

class TestSubtitles(unittest.TestCase):
    def test_resemble(self):
        srt_string1 = """
        1
        00:00:01,000 --> 00:00:05,000
        Hello!

        2
        00:00:06,000 --> 00:00:10,000
        World!
        """

        srt_string2 = """
        1
        00:00:01,000 --> 00:00:05,000
        你好！

        2
        00:00:06,000 --> 00:00:10,000
        世界！
        """

        srt_string3 = """
        1
        00:00:01,000 --> 00:00:05,000
        Hello!

        2
        00:00:08,000 --> 00:00:10,000
        World!
        """

        subtitles1 = Subtitles.from_str(srt_string1)
        subtitles2 = Subtitles.from_str(srt_string2)
        subtitles3 = Subtitles.from_str(srt_string3)

        self.assertTrue(subtitles1.resemble(subtitles2))
        self.assertFalse(subtitles1.resemble(subtitles3))

    def test_resemble2(self):
        input_str = ''
        with open("test_input1.srt", encoding='utf-8') as file:
            input_str = input_str.join(file.read())

        output_str = ''
        with open("test_input2.srt", encoding='utf-8') as file:
            output_str = output_str.join(file.read())

        subtitles1 = Subtitles.from_str(input_str)
        subtitles2 = Subtitles.from_str(output_str)

        self.assertTrue(subtitles1.resemble(subtitles2))



    def test_str(self):
        # Create Subtitles object
        subtitles = Subtitles()

        # Add some subtitle lines
        subtitles.add_line(1, "Hello!", 1, 71)
        subtitles.add_line(2, "World!", 121, 3600)

        # Define expected string representation
        expected_str = "1\n00:00:01,000 --> 00:01:11,000\nHello!\n2\n00:02:01,000 --> 01:00:00,000\nWorld!\n"

        # Assert the actual string representation matches the expected value
        self.assertEqual(str(subtitles), expected_str)

if __name__ == '__main__':
    unittest.main()
