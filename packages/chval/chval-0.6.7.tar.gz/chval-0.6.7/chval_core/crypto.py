#!/usr/bin/env python

# Copyright 2010 Louis Paternault

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module related to encryption.
"""

# Third party modules
import base64
import getpass
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

# Cheval modules
from chval_core import error, write

class PasswordFailed(Exception):
    "Exception thrown when user fails three times to give password."

class Crypt:
    "Class performing encryption"
    def __init__(self, checksum):
        """
        checksum: default value for self.checksum
        """
        # Object use to hash strings
        self.hash = None
        # Object (of class RSA) used to encrypt strings (asymetric algorithm)
        self.rsa = RSA.generate(1024)
        # converted-to-base64 encrypted sha256 checksum of the valid password.
        # None if no password yet
        self.checksum = checksum

    def check_password(self, trial):
        """Check if 'trial' is the good password.

        Return True if so, False otherwise.
        """
        self.hash = SHA256.new(trial)
        if self.checksum is None:
            return True

        iv_checksum = base64.b64decode(self.checksum)
        iv = iv_checksum[0:AES.block_size]
        echecksum = iv_checksum[AES.block_size:]

        aes = AES.new(self.hash.digest(), AES.MODE_CFB, IV = iv)
        return (self.hash.digest() == aes.decrypt(echecksum))

    def has_main(self):
        "Return True iff there is a main password."
        return self.checksum != None

    def ask_password(self, prompt):
        """Ask password if not done yet

        Arguments:
        - prompt: string to display before asking for password
        """
        if self.hash == None:
            fail = 0
            while True:
                if (self.check_password(getpass.getpass(prompt))):
                    break
                fail += 1
                if (fail == 3):
                    raise PasswordFailed
            self.checksum = self.hash.digest()

    def set_password(self, prompt):
        """Set password

        Precondition:
            * self.has_main() == False
        """
        try:
            while True:
                password1 = getpass.getpass(prompt)
                password2 = getpass.getpass(prompt)
                if password1 == password2:
                    break
                write("Passwords do not match.\n")
        except KeyboardInterrupt:
            error("\nKilled by user.")
        self.check_password(password1)
        self.checksum = self.hash.digest()

    def encrypt(self, message):
        """Return the message, encrypted, and converted in base 64

        Arguments:
        - message: message to encrypt

        Preconditions:
        - main password is known (self.ask_password() has been successfully
          called)
        """
        iv = Random.new().read(AES.block_size)
        aes = AES.new(self.hash.digest(), AES.MODE_CFB, IV = iv)
        return base64.b64encode(iv + aes.encrypt(message))

    def decrypt(self, message64):
        """Return the original string

        Arguments:
        - message64: an encrypted string converted in base 64 (such as returned
          by method "self.encrypt".

        Preconditions:
        - main password is known (self.ask_password() has been successfully
          called)
        """
        iv_message = base64.b64decode(message64)
        iv = iv_message[0:AES.block_size]
        message = iv_message[AES.block_size:]
        aes = AES.new(self.hash.digest(), AES.MODE_CFB, IV = iv)
        return aes.decrypt(message)

def get_random():
    "Return 256 random bytes"
    return Random.get_random_bytes(256)

if __name__ == '__main__':
    error("This module is not meant to be run alone.")
