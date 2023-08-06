# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-10-21
#  Copyright (c) 2011 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

"""
This package provides simple access to the Austrian RTR (Rundfunk und Telekom
Regulierungs-GmbH) "ECG list", the registry of persons and companies who do
not wish to receive promotional e-mail.

Typical usage looks like this::

    from ecglist import ECGList

    e = ECGList("/data/ecg-liste.hash")
    if email not in e:
        send_email(email)
    else:
        print "%s does not want to receive email" % email

Note that the data file is only loaded when the first address is verified,
i.e. the address verification might raise an Exception if the hash file has
vanished in the mean time.

To reread the on-disk hash file or to free up the in-memory hash
table, use the reread() method like so::

    e.reread()

"""

__version__ = '1.5'

import hashlib
import os
import threading

# ------------------------------------------------------------------------
class ECGList(object):
    """
    I am a simple wrapper class for accessing the austrian RTR GmbH
    do-not-email blacklist.
    """

    NOT_EMAIL_ADDRESS = 1
    DOMAIN_BLACKLISTED = 2
    ADDRESS_BLACKLISTED = 3

    status_str = {
        NOT_EMAIL_ADDRESS: "Not an email address",
        DOMAIN_BLACKLISTED: "Domain blacklisted",
        ADDRESS_BLACKLISTED: "Address blacklisted"
    }

    chunk_size = 20

    def __init__(self, filename="ecg-liste.hash"):
        self.read_lock = threading.Lock()
        self.reread(filename)

    def read(self):
        hash_values = set()
        with open(self.filename, "rb", buffering=self.chunk_size * 8192) as f:
            while True:
                chunk = f.read(self.chunk_size)
                if len(chunk) < self.chunk_size:
                    break
                hash_values.add(chunk)

        self.hash_values = hash_values

    def reread(self, filename=None):
        """
        Reset the internal state, throw away any cached hash values and
        optionally set a new file name. Use to free up memory after use

        """
        if filename is not None:
            self.filename = filename
        if self.filename is None:
            raise ValueError("ECGList needs a file name")
        if not os.path.isfile(self.filename):
            raise IOError("Path '%s' is not accessible" % self.filename)
        file_size = os.path.getsize(self.filename)
        if file_size == 0 or file_size % self.chunk_size != 0:
            raise ValueError("File '%s' is not a valid hash file" % self.filename)
        self.hash_values = None

    def _get_blacklist_status_code(self, email):
        """
        External use deprecated, use get_blacklist_status(..., numeric=True)
        """
        if self.hash_values is None:          # Not yet pulled in hash value from file?
            with self.read_lock:              # Only one thread may read file at any time
                if self.hash_values is None:  # Maybe some other thread already updated?
                    self.read()

        if '@' in email:
            email = email.lower()
            name, domain = email.split('@', 1)

            if hashlib.sha1(("@" + domain).encode('UTF-8')).digest() in self.hash_values:
                return self.DOMAIN_BLACKLISTED
            if hashlib.sha1(email.encode('UTF-8')).digest() in self.hash_values:
                return self.ADDRESS_BLACKLISTED
            return None

        return self.NOT_EMAIL_ADDRESS

    def get_blacklist_status(self, email, numeric=False):
        """
        Search an email address in the blacklist. Returns either
        None or a status. The status is either a string describing
        the type of listing or a numeric status code (if numeric=True)
        """
        status = self._get_blacklist_status_code(email)
        if numeric:
            return status
        return self.status_str[status] if status else None

    def __contains__(self, email):
        """
        Implement "in" operator. Return truthy if email is blacklisted,
        with the return value being the error code, falsy otherwise.
        """
        return self._get_blacklist_status_code(email)

    def __getitem__(self, email):
        """
        Implement indexing operator. Return result as of get_blacklist_status()
        """
        return self._get_blacklist_status_code(email)

# ------------------------------------------------------------------------
