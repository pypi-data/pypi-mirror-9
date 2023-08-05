# -*- coding: utf-8 -*-
from imagine import Imagine
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error


"""
Class: Albuminer
Summary: Wraps the functionality of Albuminer.
Params: String filename (it should be already checked to exist)
"""


class Albuminer:
    def __init__(self, filename):
        self.filename = filename
        # Get all the tags needed to establish the query
        audio = ID3(self.filename)
        self.album = audio["TALB"].text[0]
        self.artist = audio["TPE1"].text[0]
        self.pref = "cover-1.jpg"  # prefered cover

    # Download 3 covers using Imagine
    def get_covers(self):
        imaginator = Imagine(self.artist + " " + self.album + " cover", 3)
        imaginator.execute()

        # Pick one
        pref = 0
        while 1 > int(pref) or 3 < int(pref):
            print("Check the three downloaded covers; which one do you like the best? (1-3): ", end='')
            pref = input()

        self.pref = "cover-" + pref + ".jpg"

    # Set the selected cover
    def set_cover(self):
        audio = MP3(self.filename, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=open(self.pref, 'rb').read()
            )
        )
        audio.save()

    # Wrapper for all the functionality
    def albumine(self):
        self.get_covers()
        self.set_cover()
