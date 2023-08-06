"""
Test dogpile protection by using two reader processes to try to process the
same image chain. Ensure that the image chain is only processed once.
"""

from unittest import TestCase
from threading import Thread
from six.moves import queue

from pyramid import testing

from ..images.chain import FilterChain
from ..images.filters import Filter
from ..images.view import process_image

from . import utils


q = queue.Queue()


class RecordingFilter(Filter):
    def filter(self, im):
        q.put(1)
        return im


def run_process(name, original_ext):

    chain = FilterChain(
        'test-dogpile',
        filters=[
            RecordingFilter(),
        ],
        extension='jpg', width=50, height=50,
    )
    with testing.testConfig():
        process_image(utils.default_settings,
                      name, original_ext, chain)


def setup():
    utils.load_images()


class TestImageDogpileProtection(TestCase):

    def test_create(self):
        args = [
            ('smiley-jpeg-rgb', 'jpg'),
            ('smiley-jpeg-rgb', 'jpg'),
            ('smiley-png24-alpha', 'png'),
            ('smiley-png24-alpha', 'png'),
            ('smiley-png24-alpha', 'png'),
        ]
        threads = []
        for arg in args:
            t = Thread(target=run_process, args=arg)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        # Make sure that the RecordingFilter was run exactly twice.
        self.assertEqual(q.qsize(), 2)
