"""Tests de utils/validators.py (puro, sin red)."""

import unittest

from utils.validators import (
    TEXT,
    UNSUPPORTED_URL,
    YOUTUBE_PLAYLIST,
    YOUTUBE_VIDEO,
    classify,
    unsupported_message,
)


class ClassifyTest(unittest.TestCase):
    def test_texto(self):
        self.assertEqual(classify("un mamut chiquitito"), TEXT)
        self.assertEqual(classify(""), TEXT)
        self.assertEqual(classify("youtube.com sin https"), TEXT)

    def test_video(self):
        self.assertEqual(classify("https://www.youtube.com/watch?v=abc"), YOUTUBE_VIDEO)
        self.assertEqual(classify("https://youtu.be/abc"), YOUTUBE_VIDEO)
        self.assertEqual(classify("https://www.youtube.com/shorts/abc"), YOUTUBE_VIDEO)
        self.assertEqual(classify("https://music.youtube.com/watch?v=abc"), YOUTUBE_VIDEO)
        self.assertEqual(classify("https://m.youtube.com/watch?v=abc"), YOUTUBE_VIDEO)

    def test_playlist(self):
        self.assertEqual(classify("https://www.youtube.com/watch?v=abc&list=PLx"), YOUTUBE_PLAYLIST)
        self.assertEqual(classify("https://www.youtube.com/playlist?list=PLx"), YOUTUBE_PLAYLIST)
        self.assertEqual(classify("https://www.youtube.com/watch?v=abc&LIST=PLx"), YOUTUBE_PLAYLIST)

    def test_no_compatible(self):
        self.assertEqual(classify("https://www.instagram.com/reel/abc/"), UNSUPPORTED_URL)
        self.assertEqual(classify("https://www.tiktok.com/@x/video/1"), UNSUPPORTED_URL)
        self.assertEqual(classify("https://facebook.com/reel/1"), UNSUPPORTED_URL)
        self.assertEqual(classify("https://example.com/cancion"), UNSUPPORTED_URL)

    def test_mensaje(self):
        self.assertIn("YouTube", unsupported_message())


if __name__ == "__main__":
    unittest.main()
