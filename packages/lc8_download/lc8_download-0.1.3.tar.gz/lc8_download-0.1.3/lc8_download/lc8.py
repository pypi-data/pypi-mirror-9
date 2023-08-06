# -*- coding: utf-8 -*-
from __future__ import print_function
import requests
from homura import download as fetch

from os.path import join, expanduser, exists, getsize
from os import makedirs


class WrongSceneNameError(Exception):
    pass


class RemoteFileDoesntExist(Exception):
    pass


class InvalidBandError(Exception):
    pass


def check_create_folder(folder_path):
    """Check whether a folder exists, if not the folder is created.
    Always return folder_path.
    """

    if not exists(folder_path):
        makedirs(folder_path)

    return folder_path


class Downloader(object):
    """Download Landsat 8 imagery from Amazon servers."""

    def __init__(self, scene):
        self.s3url = 'http://landsat-pds.s3.amazonaws.com/L8/'
        self.scene = scene
        self.path = scene[3:6]
        self.row = scene[6:9]
        self.baseurl = join(self.s3url, self.path, self.row, self.scene)
        self.validate_scene()
        self.download_dir = join(expanduser('~'), 'landsat')

    def download(self, bands, download_dir=None, metadata=False):
        self.bands = bands
        self.validate_bands()
        if download_dir is None:
            download_dir = self.download_dir

        dest_dir = check_create_folder(join(download_dir, self.scene))

        for band in self.bands:
            if band == 'BQA':
                filename = '%s_%s.TIF' % (self.scene, band)
            else:
                filename = '%s_B%s.TIF' % (self.scene, band)

            band_url = join(self.baseurl, filename)
            self.fetch(band_url, dest_dir, filename)

        if metadata:
            filename = '%s_MTL.txt' % (self.scene)
            url = join(self.baseurl, filename)
            self.fetch(url, dest_dir, filename)

    def fetch(self, url, path, filename):
        """Verify if the file is already downloaded and complete. If they don't
        exists or if are not complete, use homura download function to fetch
        files.
        """

        print(('Downloading: %s' % filename))

        if exists(join(path, filename)):
            size = getsize(join(path, filename))
            if size == self.get_remote_file_size(url):
                print(('%s already exists on your system' % filename))
                return False

        fetch(url, path)
        print(('stored at %s' % path))

        return True

    def validate_scene(self):
        """Validate scene name and verify if it's available on Amazon servers."""

        if len(self.scene) == 16:
            self.scene += 'LGN00'

        if self.scene.startswith('LC8') and self.scene.endswith('LGN00') and \
            len(self.scene) == 21:
            pass
        else:
            raise WrongSceneNameError(self.scene)

        index = join(self.baseurl, 'index.html')

        if not self.remote_file_exists(index):
            raise RemoteFileDoesntExist(
                '%s is not available on Amazon Storage' % self.scene
            )

    def validate_bands(self):
        """Validate bands parameter."""

        valid_bands = list(range(1, 12)) + ['BQA']
        for band in self.bands:
            if band not in valid_bands:
                raise InvalidBandError('%s is not a valid band' % band)

    def remote_file_exists(self, url):
        """Verify if the file is available on server."""
        status = requests.head(url).status_code

        if status == 200:
            return True
        else:
            return False

    def get_remote_file_size(self, url):
        """ Gets the filesize of a remote file """

        headers = requests.head(url).headers
        return int(headers['content-length'])