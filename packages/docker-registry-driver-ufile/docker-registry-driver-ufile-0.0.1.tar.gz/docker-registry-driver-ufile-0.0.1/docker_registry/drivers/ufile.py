# -*- coding: utf-8 -*-
"""
docker_registry.drivers.ufile
~~~~~~~~~~~~~~~~~~~~~~~~~~

UFile is a distributed key/value storage provided by UCloud.
See http://docs.ucloud.cn/ufile/index.html for additional info.

"""

import functools
import logging
import os
import time

import requests

from docker_registry.core import driver
from docker_registry.core import exceptions as de
from docker_registry.core import lru
from ucloudauth import UFileAuth

# FIXME: tmp hack for ucloud minit bug
import mock

logger = logging.getLogger(__name__)


GET = "get"
POST = "post"
PUT = "put"
HEAD = "head"
DELETE = "delete"


def add_slash(path):
    if path == "" or path.endswith("/"):
        return path
    else:
        return path + "/"


def remove_slash(path):
    while path.endswith("/"):
        path = path[:-1]
    return path


def add_to_index(func):
    @functools.wraps(func)
    def add_key_to_index(obj, key, *args, **kwargs):
        key = remove_slash(key)
        dirname, basename = os.path.split(key)
        obj._mkdir(dirname)
        func(obj, key, *args, **kwargs)
        obj._update_index(dirname, adds=[basename])
    return add_key_to_index


class Storage(driver.Base):
    root_index = "ufile-root-index"
    index_header = {"content-type": "application/ufile-index"}
    default_retries = 3
    default_retry_interval = 1
    default_timeout = 60
    chunk_size = 10 * 1024 * 1024  # 10MB

    def __init__(self, path=None, config=None):
        # turn on streaming support
        self.supports_bytes_range = True

        # config check
        for key in ("ufile_baseurl", "ufile_public_key", "ufile_private_key"):
            val = getattr(config, key)
            if not val:
                raise ValueError("storage config {0}={1} is not valid".format(
                    key, val
                ))

        session = requests.session()
        session.auth = UFileAuth(
            config.ufile_public_key,
            config.ufile_private_key
        )
        self._session = session
        self._baseurl = config.ufile_baseurl
        self._retries = config.ufile_retries or self.default_retries
        self._interval = (
            config.ufile_retry_interval or self.default_retry_interval
        )
        self._timeout = (config.ufile_timeout or self.default_timeout)

    def exists(self, path):
        """check if key exists

        :param key: key path
        """
        logger.info("check for <{0}>".format(path))
        dirname, basename = os.path.split(path)

        dirname = dirname or self.root_index

        if not basename:
            # key is dir
            # "HEAD" the index file so we don't download the whole conetnt
            try:
                self._request(HEAD, dirname)
                return True
            except de.FileNotFoundError:
                logger.error("dir not found: <{0}>".format(dirname))
                return False

        # key is file
        # look for it in the index file
        try:
            res = self._request(GET, dirname)
        except de.FileNotFoundError:
            logger.error("index not found: <{0}>".format(dirname))
            return False

        s_basename = basename.encode("utf8")
        for line in res.iter_lines():
            if line == s_basename:
                return True
        logger.debug("<{0}> not found".format(basename))
        return False

    def get_size(self, path):
        # FIXME: ucloud bug, head will not return correct content-length
        # res = self._request(HEAD, path)
        res = self._request(GET, path)
        return int(res.headers["content-length"])

    @lru.get
    def get_content(self, path):
        res = self._request(GET, path)
        return res.content

    @lru.set
    @add_to_index
    def put_content(self, path, content):
        key = remove_slash(path)
        logger.info("simple upload <{0}>".format(key))
        self._request(PUT, key, data=content)
        return path

    @lru.remove
    def remove(self, path):
        # we put final delete in the public function, so we only do it once
        if self._is_dir(path):
            self._rmtree(path)
            # delete dir in parent-dir index
            parent, dir_path = os.path.split(remove_slash(path))
            self._update_index(parent, deletes=[dir_path])
        else:
            self._rm(path)
            index, to_delete = os.path.split(path)
            self._update_index(index, deletes=[to_delete])

    def stream_read(self, path, bytes_range=None):
        headers = dict()
        if bytes_range:
            header_range = "bytes={0}-{1}".format(*bytes_range)
            logger.info("bytes range = {0}".format(header_range))
            headers["range"] = header_range
        res = self._request(GET, path, headers=headers, stream=True)
        for data in res.iter_content(self.chunk_size):
            yield data

    @add_to_index
    def stream_write(self, path, fp):
        """ufile multipart upload

        :param key: upload file path
        :param fp: file-object like data
        """
        key = remove_slash(path)
        logger.info("multipart upload begin <{0}>".format(key))
        upload_id, block_size = self._init_multipart_upload(key)
        data = fp.read(block_size)
        etags = []
        try:
            while data:
                etag = self._multipart_upload(key, upload_id, len(etags), data)
                etags.append(etag)
                data = fp.read(block_size)
        except BaseException:
            self._abort_multipart_upload(key, upload_id)
        else:
            self._finish_multipart_upload(key, upload_id, ",".join(etags))

    def list_directory(self, path=None):
        """list_directory
        returns a list of file names (including dir names, with heading slash)

        :param dir_path: dir path to ls
        """
        for fname in self._lsdir(path):
            yield remove_slash(fname)

    def _lsdir(self, path):
        dir_path = remove_slash(path or "")
        logger.info("list dir for {0}".format(dir_path))
        res = self._request(GET, dir_path)

        for key, val in self.index_header.items():
            if res.headers.get(key) != val:
                raise de.FileNotFoundError("{0} is not there".format(dir_path))

        return [
            os.path.join(dir_path, fname)
            for fname in res.text.splitlines()
            if fname
        ]

    def _request(self, method, key, **options):
        """send an http request to ufile
        do some basic check
        if it's ok, return `response` object like normal requests do
        if it's 404, raise FileNotFound
        otherwise, raise http error

        :param method: http verb (lowercase)
        :param **options: options will direct pass to requests
        """
        if key.startswith("/"):
            key = key[1:]
        logger.info("request {0} {1}".format(method, key))

        req = getattr(self._session, method)
        url = "{0}/{1}".format(self._baseurl, key)
        options.setdefault("timeout", self._timeout)

        for __ in range(self._retries):
            try:
                res = req(url, **options)
            except BaseException as exc:
                logger.info(
                    "http {0} {1} error {2}".format(method, url, exc),
                    exc_info=True
                )
                time.sleep(self._interval)
                continue
            if res.ok:
                # everything ok, break retry loop
                return res
            elif res.status_code == 404:
                # not found, break retry loop
                raise de.FileNotFoundError("{0} is not there".format(key))
            logger.info("http {0} {1} failed: {2}\n{3}\nretry in {4}s".format(
                method, url, res, res.text, self._interval
            ))
            time.sleep(self._interval)
        else:
            # something went wrong we tried our best, raise error
            res.raise_for_status()

    def _is_dir(self, path):
        is_dir = path.endswith("/")
        logger.info("test dir <{0}> {1}".format(path, is_dir))
        return is_dir

    def _rmtree(self, dir_path):
        """remove dir recursively

        :param dir_path: dir path to remove
        """
        # remove all file in the index
        logger.info("remove dir {0}".format(dir_path))
        for key in self._lsdir(dir_path):
            if self._is_dir(key):
                key = remove_slash(key)
                logger.info("going to delete dir {0}".format(key))
                self._rmtree(key)
            else:
                logger.info("going to delete key {0}".format(key))
                self._rm(key)
        # remove index
        logger.info("going to delete index {0}".format(dir_path))
        self._rm(dir_path)

    def _rm(self, key):
        """remove file

        :param key: file to delete
        """
        logger.info("remove {0}".format(key))
        self._request(DELETE, key)

    def _mkdir(self, dir_path):
        """mkdir and update dir index recursively

        :param dir_path: dir path
        """
        logger.info("mkdir {0}".format(dir_path))
        dir_path = remove_slash(dir_path)
        if not dir_path:
            logger.info("skip mkdir the root dir")
            return

        parent, dirname = os.path.split(dir_path)
        dirname = add_slash(dirname)
        self._update_index(parent, adds=[dirname])

        if parent:
            # not root, make parent dir
            logger.info(
                "continue to make <{0}>'s parent dir <{1}>".format(
                    dir_path, parent
                )
            )
            return self._mkdir(parent)

    # FIXME: date in string_to_sign must be "", ucloud bug
    @mock.patch("time.strftime")
    def _init_multipart_upload(self, key, mock_time):
        """initiative a multipart upload
        returns a tuple (upload_id, block_size)

        :param key: upload file path
        """
        mock_time.return_value = ""

        logger.info("init multipart upload for <{0}>".format(key))
        res = self._request(POST, "{0}?uploads".format(key))
        upload_id, block_size = res.json()["UploadId"], res.json()["BlkSize"]
        logger.info(
            "<{0}> multipart upload inited: block={1}, upload_id={2}".format(
                key, block_size, block_size
            )
        )
        return upload_id, block_size

    # FIXME: date in string_to_sign must be "", ucloud bug
    @mock.patch("time.strftime")
    def _multipart_upload(self, key, upload_id, part_number, data, mock_t):
        """multipart upload, upload part of file

        :param key: upload file path
        :param upload_id: multipart upload id
        :param part_number: part number of the whole file, 0 based
        :param data: part of file to upload
        """
        mock_t.return_value = ""

        logger.info(
            "multipart upload part {0} for <{1})>, upload_id={2}".format(
                part_number, key, upload_id
            )
        )
        res = self._request(
            PUT, key,
            params=dict(uploadId=upload_id, partNumber=part_number),
            data=data
        )
        etag = res.headers["etag"]
        logger.debug(
            "{0} part {1}'s etag is {2}".format(key, part_number, etag)
        )
        return etag

    # FIXME: date in string_to_sign must be "", ucloud bug
    @mock.patch("time.strftime")
    def _abort_multipart_upload(self, key, upload_id, mock_t):
        """abort multipart upload procedure

        :param key: upload file path
        :param upload_id: multipart upload_id
        """
        mock_t.return_value = ""

        logger.info(
            "abort multipart upload for <{0})>, upload_id={1}".format(
                key, upload_id,
            )
        )
        self._request(DELETE, key, params=dict(uploadId=upload_id))

    # FIXME: date in string_to_sign must be "", ucloud bug
    @mock.patch("time.strftime")
    def _finish_multipart_upload(self, key, upload_id, etags, mock_t):
        """finish multipart upload

        :param key: upload file path
        :param upload_id: multipart upload_id
        :params etags: parts etags joined with ","
        """
        mock_t.return_value = ""

        logger.info(
            "finsish multipart upload for <{0})>, upload_id={1}".format(
                key, upload_id,
            )
        )
        self._request(POST, key, params=dict(uploadId=upload_id), data=etags)

    def _update_index(self, index, adds=None, deletes=None):
        if index == "":
            index = self.root_index
        logger.info(
            "index: {0} has changed, add: {1}, delete: {2}".format(
                index, adds, deletes
            )
        )
        try:
            res = self._request(GET, index)
            current = set(res.text.splitlines())
        except de.FileNotFoundError:
            # dir not exists
            current = set()

        current.update(adds or {})
        current -= set(deletes or {})
        self._request(
            PUT, index,
            data="\n".join(current) + "\n",
            headers=self.index_header
        )
