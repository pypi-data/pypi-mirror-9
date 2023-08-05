# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2014-2015 Regents of the University of California.
# Author: Jeff Thompson <jefft0@remap.ucla.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# A copy of the GNU Lesser General Public License is in the file COPYING.

"""
This module defines the FilePrivateKeyStorage class which extends
PrivateKeyStorage to implement private key storage using files.
"""

import os
import sys
import stat
import base64
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from pyndn.util import Blob
from pyndn.security.security_types import DigestAlgorithm
from pyndn.security.security_types import KeyClass
from pyndn.security.security_types import KeyType
from pyndn.security.security_exception import SecurityException
from pyndn.security.certificate.public_key import PublicKey
from pyndn.security.identity.private_key_storage import PrivateKeyStorage

class FilePrivateKeyStorage(PrivateKeyStorage):
    """
    Create a new FilePrivateKeyStorage to connect to the default directory.
    """
    def __init__(self):
        super(FilePrivateKeyStorage, self).__init__()

        if not "HOME" in os.environ:
            # Don't expect this to happen
            home = "."
        else:
            home = os.environ["HOME"]

        self._keyStorePath = os.path.join(home, ".ndn", "ndnsec-tpm-file")
        if not os.path.exists(self._keyStorePath):
            os.makedirs(self._keyStorePath)

    def generateKeyPair(self, keyName, params):
        """
        Generate a pair of asymmetric keys.

        :param Name keyName: The name of the key pair.
        :param KeyParams params: The parameters of the key.
        """
        if self.doesKeyExist(keyName, KeyClass.PUBLIC):
            raise SecurityException("Public key already exists")
        if self.doesKeyExist(keyName, KeyClass.PRIVATE):
            raise SecurityException("Private key already exists")

        publicKeyDer = None
        privateKeyDer = None

        if params.getKeyType() == KeyType.RSA:
            key = RSA.generate(params.getKeySize())
            publicKeyDer = key.publickey().exportKey(format = 'DER')
            privateKeyDer = key.exportKey(format = 'DER', pkcs = 8)
        else:
            raise SecurityException("Unsupported key type")

        keyUri = keyName.toUri()
        publicKeyFilePath = self.nameTransform(keyUri, ".pub")
        privateKeyFilePath = self.nameTransform(keyUri, ".pri")

        with open(publicKeyFilePath, 'w') as keyFile:
            keyFile.write(Blob(base64.b64encode(publicKeyDer), False).toRawStr())
        with open(privateKeyFilePath, 'w') as keyFile:
            keyFile.write(Blob(base64.b64encode(privateKeyDer), False).toRawStr())

        os.chmod(publicKeyFilePath,  stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        os.chmod(privateKeyFilePath, stat.S_IRUSR)

    def deleteKeyPair(self, keyName):
        """
        Delete a pair of asymmetric keys. If the key doesn't exist, do nothing.

        :param Name keyName: The name of the key pair.
        """
        keyUri = keyName.toUri()

        if self.doesKeyExist(keyName, KeyClass.PUBLIC):
            os.remove(self.nameTransform(keyUri, ".pub"))
        if self.doesKeyExist(keyName, KeyClass.PRIVATE):
            os.remove(self.nameTransform(keyUri, ".pri"))
        
    def getPublicKey(self, keyName):
        """
        Get the public key with the keyName.

        :param Name keyName: The name of public key.
        :return: The public key.
        :rtype: PublicKey
        """
        keyURI = keyName.toUri()

        if not self.doesKeyExist(keyName, KeyClass.PUBLIC):
            raise SecurityException(
              "Public key doesn't exist")

        base64Content = None
        with open(self.nameTransform(keyURI, ".pub")) as keyFile:
            base64Content = keyFile.read()
        der = base64.b64decode(base64Content)

        return PublicKey(Blob(der, False))

    def sign(self, data, keyName, digestAlgorithm = DigestAlgorithm.SHA256):
        """
        Fetch the private key for keyName and sign the data, returning a
        signature Blob.

        :param data: Pointer the input byte buffer to sign.
        :type data: An array type with int elements
        :param Name keyName: The name of the signing key.
        :param digestAlgorithm: (optional) the digest algorithm. If omitted,
          use DigestAlgorithm.SHA256.
        :type digestAlgorithm: int from DigestAlgorithm
        :return: The signature Blob.
        :rtype: Blob
        """
        keyURI = keyName.toUri()

        if not self.doesKeyExist(keyName, KeyClass.PRIVATE):
            raise SecurityException(
              "FilePrivateKeyStorage.sign: private key doesn't exist")

        if digestAlgorithm != DigestAlgorithm.SHA256:
            raise SecurityException(
              "FilePrivateKeyStorage.sign: Unsupported digest algorithm")

        # Read the private key.
        base64Content = None
        with open(self.nameTransform(keyURI, ".pri")) as keyFile:
            base64Content = keyFile.read()
        der = base64.b64decode(base64Content)
        if not type(der) is str:
            der = "".join(map(chr, der))

        privateKey = RSA.importKey(der)

        # Sign the hash of the data.
        if sys.version_info[0] == 2:
            # In Python 2.x, we need a str.  Use Blob to convert data.
            data = Blob(data, False).toRawStr()
        signature = PKCS1_v1_5.new(privateKey).sign(SHA256.new(data))
        # Convert the string to a Blob.
        return Blob(bytearray(signature), False)

    def decrypt(self, keyName, data, isSymmetric = False):
        """
        Decrypt data.

        :param Name keyName: The name of the decrypting key.
        :param data: The byte buffer to be decrypted.
        :type data: An array type with int elements
        :param bool isSymmetric: (optional) If True symmetric encryption is
          used, otherwise asymmetric encryption is used. If omitted, use
          asymmetric encryption.
        :return: The decrypted data.
        :rtype: Blob
        """
        raise RuntimeError("decrypt is not implemented")

    def encrypt(self, keyName, data, isSymmetric = False):
        """
        Encrypt data.

        :param Name keyName: The name of the encrypting key.
        :param data: The byte buffer to be encrypted.
        :type data: An array type with int elements
        :param bool isSymmetric: (optional) If True symmetric encryption is
          used, otherwise asymmetric encryption is used. If omitted, use
          asymmetric encryption.
        :return: The encrypted data.
        :rtype: Blob
        """
        raise RuntimeError("encrypt is not implemented")

    def generateKey(self, keyName, params):
        """
        Generate a symmetric key.

        :param Name keyName: The name of the key.
        :param KeyParams params: The parameters of the key.
        :param int keySize: (optional) The size of the key. If omitted, use 256.
        """
        raise RuntimeError("generateKey is not implemented")

    def doesKeyExist(self, keyName, keyClass):
        """
        Check if a particular key exists.

        :param Name keyName: The name of the key.
        :param keyClass: The class of the key, e.g. KeyClass.PUBLIC,
           KeyClass.PRIVATE, or KeyClass.SYMMETRIC.
        :type keyClass: int from KeyClass
        :return: True if the key exists, otherwise false.
        :rtype: bool
        """
        keyURI = keyName.toUri()
        if keyClass == KeyClass.PUBLIC:
            return os.path.isfile(self.nameTransform(keyURI, ".pub"))
        elif keyClass == KeyClass.PRIVATE:
            return os.path.isfile(self.nameTransform(keyURI, ".pri"))
        elif keyClass == KeyClass.SYMMETRIC:
            return os.path.isfile(self.nameTransform(keyURI, ".key").c_str())
        else:
            return False

    def nameTransform(self, keyName, extension):
        """
        Create a file path from keyName and the extension

        :param str keyName: The key name URI.
        :param str extension: The desired file name extension, e.g. ".pri".
        :return: The file path.
        :rtype: str
        """
        hashInput = keyName
        if sys.version_info[0] > 2:
            # In Python 2.x, hash uses a str. Otherwise use Blob to convert.
            hashInput = Blob(keyName, False).toBuffer()
        hash = SHA256.new(hashInput).digest()

        digest = base64.b64encode(hash)
        if type(digest) != str:
            # In Python 3, this is bytes, so convert to a str.
            digest = "".join(map(chr, digest))
        digest = digest.strip()
        digest = digest.replace('/', '%')

        return os.path.join(self._keyStorePath, digest + extension)