#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @file     crypto.py
# @author   kaka_ace <xiang.ace@gmail.com>
# @date     Mar 05 2015
# @breif     
# 


from Crypto.Hash import MD5


class CryptoUtils(object):
    """


    """
    @staticmethod
    def calculate_md5_value_from_string(s):
        """
        move from My https://github.com/kaka19ace/pycmd-tools/blob/master/md5sum.py
        """
        m = MD5.new(s)
        return m.hexdigest()

    @staticmethod
    def calculate_md5_value_from_filename(filename):
        """
        move from My https://github.com/kaka19ace/pycmd-tools/blob/master/md5sum.py
        """
        _READ_FILE_BUFFER = 10240
        m = MD5.new()
        with open(filename, "rb") as f:
            while True:
                buf = f.read(_READ_FILE_BUFFER)
                if buf == "":
                    break
                m.update(buf)

        return m.hexdigest()
