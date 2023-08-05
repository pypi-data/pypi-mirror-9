# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2014-2015 Regents of the University of California.
# Author: Jeff Thompson <jefft0@remap.ucla.edu>
# Author: Adeola Bannis <thecodemaiden@gmail.com>
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
BasicIdentityStorage extends IdentityStorage to implement a basic storage of
identity, public keys and certificates using SQLite.
"""

import os
import math
import sqlite3
from pyndn import Name, KeyLocator
from pyndn.util import Blob
from pyndn.security.security_exception import SecurityException
from pyndn.security.identity.identity_storage import IdentityStorage
from pyndn.security.certificate.identity_certificate import IdentityCertificate

INIT_ID_TABLE = ["""
CREATE TABLE IF NOT EXISTS
  Identity(
      identity_name     BLOB NOT NULL,
      default_identity  INTEGER DEFAULT 0,

      PRIMARY KEY (identity_name)
  );
""",
  "CREATE INDEX identity_index ON Identity(identity_name);"]

INIT_KEY_TABLE = ["""
CREATE TABLE IF NOT EXISTS
  Key(
      identity_name     BLOB NOT NULL,
      key_identifier    BLOB NOT NULL,
      key_type          INTEGER,
      public_key        BLOB,
      default_key       INTEGER DEFAULT 0,
      active            INTEGER DEFAULT 0,

      PRIMARY KEY (identity_name, key_identifier)
  );
""",
  "CREATE INDEX key_index ON Key(identity_name);"]

INIT_CERT_TABLE = ["""
CREATE TABLE IF NOT EXISTS
  Certificate(
      cert_name         BLOB NOT NULL,
      cert_issuer       BLOB NOT NULL,
      identity_name     BLOB NOT NULL,
      key_identifier    BLOB NOT NULL,
      not_before        TIMESTAMP,
      not_after         TIMESTAMP,
      certificate_data  BLOB NOT NULL,
      valid_flag        INTEGER DEFAULT 1,
      default_cert      INTEGER DEFAULT 0,

      PRIMARY KEY (cert_name)
  );
""",
  "CREATE INDEX cert_index ON Certificate(cert_name);",
  "CREATE INDEX subject ON Certificate(identity_name);"]

class BasicIdentityStorage(IdentityStorage):
    """
    Create a new BasicIdentityStorage to work with an SQLite file.

    :param str databaseFilePath: (optional) The path of the SQLite file. If
      omitted, use the default location.
    """
    def __init__(self, databaseFilePath = None):
        super(BasicIdentityStorage, self).__init__()

        if databaseFilePath == None or databaseFilePath == "":
            if not "HOME" in os.environ:
                # Don't expect this to happen
                home = "."
            else:
                home = os.environ["HOME"]

            identityDirectory = os.path.join(home, ".ndn")
            if not os.path.exists(identityDirectory):
                os.makedirs(identityDirectory)

            databaseFilePath = os.path.join(identityDirectory, "ndnsec-public-info.db")
            
        self._database = sqlite3.connect(databaseFilePath)

        # Check if the ID table exists.
        cursor = self._database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' And name='Identity'")
        if cursor.fetchone() == None:
            for command in INIT_ID_TABLE:
                self._database.execute(command)
        cursor.close()

        # Check if the Key table exists.
        cursor = self._database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' And name='Key'")
        if cursor.fetchone() == None:
            for command in INIT_KEY_TABLE:
                self._database.execute(command)
        cursor.close()

        # Check if the Certificate table exists.
        cursor = self._database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' And name='Certificate'")
        if cursor.fetchone() == None:
            for command in INIT_CERT_TABLE:
                self._database.execute(command)
        cursor.close()

        self._database.commit()

    def doesIdentityExist(self, identityName):
        """
        Check if the specified identity already exists.

        :param Name identityName: The identity name.
        :return: True if the identity exists, otherwise False.
        :rtype: bool
        """
        result = False

        cursor = self._database.cursor()
        cursor.execute(
          "SELECT count(*) FROM Identity WHERE identity_name=?",
          (identityName.toUri(),))
        (count,) = cursor.fetchone()
        if count > 0:
            result = True

        cursor.close()
        return result

    def addIdentity(self, identityName):
        """
        Add a new identity. Do nothing if the identity already exists.

        :param Name identityName: The identity name.
        """
        identityUri = identityName.toUri()
        if self.doesIdentityExist(identityName):
            return

        cursor = self._database.cursor()
        cursor.execute("INSERT INTO Identity (identity_name) VALUES(?)",
            (identityUri,))
        self._database.commit()
        cursor.close()

    def revokeIdentity(self):
        """
        Revoke the identity.

        :return: True if the identity was revoked, False if not.
        :rtype: bool
        """
        return False

    def doesKeyExist(self, keyName):
        """
        Check if the specified key already exists.

        :param Name keyName: The name of the key.
        :return: True if the key exists, otherwise False.
        :rtype: bool
        """
        keyId = keyName[-1].toEscapedString()
        identityName = keyName[:-1]

        cursor = self._database.cursor()
        cursor.execute(
          "SELECT count(*) FROM Key WHERE identity_name=? AND key_identifier=?",
          (identityName.toUri(), keyId))
        keyIdExists = False
        (count,) = cursor.fetchone()
        if count > 0:
            keyIdExists = True

        cursor.close()
        return keyIdExists

    def addKey(self, keyName, keyType, publicKeyDer):
        """
        Add a public key to the identity storage. Also call addIdentity to ensure
        that the identityName for the key exists.

        :param Name keyName: The name of the public key to be added.
        :param keyType: Type of the public key to be added.
        :type keyType: int from KeyType
        :param Blob publicKeyDer: A blob of the public key DER to be added.
        """
        if keyName.size() == 0:
            return

        if self.doesKeyExist(keyName):
            raise SecurityException("A key with the same name already exists!")

        identityName = keyName[:-1]
        identityUri = identityName.toUri()

        self.addIdentity(identityName)

        keyId = keyName[-1].toEscapedString()
        keyBuffer = sqlite3.Binary(bytearray(publicKeyDer.buf()))

        cursor = self._database.cursor()
        cursor.execute(
          "INSERT INTO Key (identity_name, key_identifier, key_type, public_key) VALUES(?,?,?,?)",
          (identityUri, keyId, keyType, keyBuffer))
        self._database.commit()
        cursor.close()

    def getKey(self, keyName):
        """
        Get the public key DER blob from the identity storage.

        :param Name keyName: The name of the requested public key.
        :return: The DER Blob. If not found, return a isNull() Blob.
        :rtype: Blob
        """
        if not self.doesKeyExist(keyName):
            return Blob()

        identityUri = keyName[:-1].toUri()
        keyId = keyName[-1].toEscapedString()

        cursor = self._database.cursor()
        cursor.execute("SELECT public_key FROM Key WHERE identity_name=? AND key_identifier=?",
            (identityUri, keyId))
        (keyData, ) = cursor.fetchone()
        cursor.close()
        return Blob(bytearray(keyData))

    def activateKey(self, keyName):
        """
        Activate a key. If a key is marked as inactive, its private part will
        not be used in packet signing.

        :param Name keyName: The name of the key.
        """
        raise RuntimeError("activateKey is not implemented")

    def deactivateKey(self, keyName):
        """
        Deactivate a key. If a key is marked as inactive, its private part will
        not be used in packet signing.

        :param Name keyName: The name of the key.
        """
        raise RuntimeError("deactivateKey is not implemented")

    def deletePublicKeyInfo(self, keyName):
        """
        Remove the key and all certificates associated with it.

        :param Name keyName: The name of the key.
        """
        if keyName.size() == 0:
            return

        keyId = keyName[-1].toEscapedString()
        identityName = keyName[:-1]
        cursor = self._database.cursor()
        cursor.execute("DELETE FROM Certificate WHERE identity_name=? AND key_identifier=?",
            (identityName.toUri(), keyId))

        cursor.execute("DELETE FROM Key WHERE identity_name=? and key_identifier=?",
            (identityName.toUri(), keyId))

        self._database.commit()
        cursor.close()

    def doesCertificateExist(self, certificateName):
        """
        Check if the specified certificate already exists.

        :param Name certificateName: The name of the certificate.
        :return: True if the certificate exists, otherwise False.
        :rtype: bool
        """
        cursor = self._database.cursor()
        cursor.execute(
          "SELECT count(*) FROM Certificate WHERE cert_name=?",
          (certificateName.toUri(),))
        certExists = False
        (count,) = cursor.fetchone()
        if count > 0:
            certExists = True

        cursor.close()
        return certExists

    def addCertificate(self, certificate):
        """
        Add a certificate to the identity storage.

        :param IdentityCertificate certificate: The certificate to be added.
          This makes a copy of the certificate.
        """
        certificateName = certificate.getName()
        keyName = certificate.getPublicKeyName()

        if not self.doesKeyExist(keyName):
            raise SecurityException("No corresponding Key record for certificate! " +
              keyName.toUri() + " " + certificateName.toUri())

        # Check if the certificate already exists.
        if self.doesCertificateExist(certificateName):
            raise SecurityException("Certificate has already been installed!")

        keyId = keyName.get(-1).toEscapedString()
        identity = keyName[:-1]

        # Check if the public key of the certificate is the same as the key record.
        keyBlob = self.getKey(keyName)
        if (keyBlob.isNull() or
            not keyBlob.equals(certificate.getPublicKeyInfo().getKeyDer())):
            raise SecurityException("Certificate does not match public key")

        # Insert the certificate.

        signature = certificate.getSignature()
        signerName = KeyLocator.getFromSignature(signature).getKeyName()
        # Convert from milliseconds to seconds since 1/1/1970.
        notBefore = int(math.floor(certificate.getNotBefore() / 1000.0))
        notAfter = int(math.floor(certificate.getNotAfter() / 1000.0))
        encodedCert = sqlite3.Binary(bytearray(certificate.wireEncode().buf()))

        cursor = self._database.cursor()
        cursor.execute(
          "INSERT INTO Certificate (cert_name, cert_issuer, identity_name, key_identifier, not_before, not_after, certificate_data) " +
          "VALUES (?,?,?,?,?,?,?)",
          (certificateName.toUri(), signerName.toUri(), identity.toUri(), keyId,
                notBefore, notAfter, encodedCert))
        self._database.commit()
        cursor.close()

    def getCertificate(self, certificateName, allowAny = False):
        """
        Get a certificate from the identity storage.

        :param Name certificateName: The name of the requested certificate.
        :param bool allowAny: (optional) If False, only a valid certificate will
          be returned, otherwise validity is disregarded.  If omitted,
          allowAny is False.
        :return: The requested certificate. If not found, return None.
        :rtype: IdentityCertificate
        """
        if not self.doesCertificateExist(certificateName):
            return None
        
        if not allowAny:
            raise RuntimeError(
              "BasicIdentityStorage.getCertificate for not allowAny is not implemented")

        cursor = self._database.cursor()
        cursor.execute("SELECT certificate_data FROM Certificate WHERE cert_name=?",
            (certificateName.toUri()))
        (certData, ) = cursor.fetchone()
        cursor.close()

        certificate = IdentityCertificate()
        certificate.wireDecode(bytearray(certData))
        return certificate

    def deleteCertificateInfo(self, certificateName):
        """
        Remove a certificate from associated keys.

        :param Name keyName: The name of the key.
        """
        if certificateName.size() == 0:
            return

        cursor = self._database.cursor()
        cursor.execute("DELETE FROM Certificate WHERE cert_name=?",
            (certificateName.toUri(),))
        self._database.commit()
        cursor.close()

    def deleteIdentityInfo(self, identityName):
        """
        Delete an identity and related public keys and certificates.

        :param Name identity: The identity name.
        """
        identity = identityName.toUri()

        cursor = self._database.cursor()
        cursor.execute("DELETE FROM Certificate WHERE identity_name=?",
            (identity,))

        cursor.execute("DELETE FROM Key WHERE identity_name=?",
            (identity,))

        cursor.execute("DELETE FROM Identity WHERE identity_name=?",
            (identity,))

        self._database.commit()
        cursor.close()

    #
    # Get/Set Default
    #

    def getDefaultIdentity(self):
        """
        Get the default identity.

        :return: The name of default identity.
        :rtype: Name
        :raises SecurityException: if the default identity is not set.
        """
        cursor = self._database.cursor()
        cursor.execute(
          "SELECT identity_name FROM Identity WHERE default_identity=1")
        row = cursor.fetchone()

        if row != None:
            (identity,) = row
            cursor.close()
            return Name(identity)
        else:
            cursor.close()
            raise SecurityException(
              "BasicIdentityStorage::getDefaultIdentity: The default identity is not defined")

    def getDefaultKeyNameForIdentity(self, identityName):
        """
        Get the default key name for the specified identity.

        :param Name identityName: The identity name.
        :return: The default key name.
        :rtype: Name
        :raises SecurityException: if the default key name for the identity is
          not set.
        """
        cursor = self._database.cursor()
        cursor.execute(
          "SELECT key_identifier FROM Key WHERE identity_name=? AND default_key=1",
          (identityName.toUri(),))
        row = cursor.fetchone()

        if row != None:
            (keyName,) = row
            cursor.close()
            return Name(identityName).append(keyName)
        else:
            cursor.close()
            raise SecurityException(
              "BasicIdentityStorage::getDefaultKeyNameForIdentity: The default key for the identity is not defined")

    def getDefaultCertificateNameForKey(self, keyName):
        """
        Get the default certificate name for the specified key.

        :param Name keyName: The key name.
        :return: The default certificate name.
        :rtype: Name
        :raises SecurityException: if the default certificate name for the key
          name is not set.
        """
        keyId = keyName[-1].toEscapedString()
        identityName = keyName[:-1]

        cursor = self._database.cursor()
        cursor.execute(
          "SELECT cert_name FROM Certificate WHERE identity_name=? AND key_identifier=? AND default_cert=1",
          (identityName.toUri(), keyId))
        row = cursor.fetchone()

        if row != None:
            (certName,) = row
            cursor.close()
            return Name(certName)
        else:
            cursor.close()
            raise SecurityException(
              "BasicIdentityStorage::getDefaultCertificateNameForKey: The default certificate for the key name is not defined")

    def getAllKeyNamesOfIdentity(self, identityName, nameList, isDefault):
        """
        Append all the key names of a particular identity to the nameList.

        :param Name identityName: The identity name to search for.
        :param Array<Name> nameList: Append result names to nameList.
        :param bool isDefault: If true, add only the default key name. If false,
          add only the non-default key names.
        """
        if isDefault:
            query = "SELECT key_identifier FROM Key WHERE default_key=1 and identity_name=?"
        else:
            query = "SELECT key_identifier FROM Key WHERE default_key=0 and identity_name=?"

        cursor = self._database.cursor()
        cursor.execute(query, (identityName.toUri(), ))
        keyIds = cursor.fetchall()
        for (keyId, ) in keyIds:
            nameList.append(Name(identityName).append(keyId))
        cursor.close()

    def setDefaultIdentity(self, identityName):
        """
        Set the default identity. If the identityName does not exist, then clear
        the default identity so that getDefaultIdentity() raises an exception.

        :param Name identityName: The default identity name.
        """
        # Reset previous default identity.
        cursor = self._database.cursor()
        cursor.execute(
          "UPDATE Identity SET default_identity=0 WHERE default_identity=1")

        # Set current default identity.
        cursor.execute(
          "UPDATE Identity SET default_identity=1 WHERE identity_name=?",
          (identityName.toUri(), ))
        self._database.commit()
        cursor.close()

    def setDefaultKeyNameForIdentity(self, keyName, identityNameCheck = None):
        """
        Set the default key name for the specified identity.


        :param Name keyName: The key name.
        :param Name identityNameCheck: (optional) The identity name to check the
          keyName.
        """
        keyId = keyName[-1].toEscapedString()
        identityName = keyName[:-1]

        if (not (identityNameCheck is None) and
             identityNameCheck.size() != 0 and
             not identityNameCheck.equals(identityName)):
            raise SecurityException(
              "Specified identity name does not match the key name")

        # Reset previous default key.
        identityUri = identityName.toUri()
        cursor = self._database.cursor()
        cursor.execute(
          "UPDATE Key SET default_key=0 WHERE default_key=1 and identity_name=?",
          (identityUri, ))

        # Set current default Key.
        cursor.execute(
          "UPDATE Key SET default_key=1 WHERE identity_name=? AND key_identifier=?",
          (identityUri, keyId))

        self._database.commit()
        cursor.close()

    def setDefaultCertificateNameForKey(self, keyName, certificateName):
        """
        Set the default key name for the specified identity.

        :param Name keyName: The key name.
        :param Name certificateName: The certificate name.
        """
        keyId = keyName[-1].toEscapedString()
        identityName = keyName[:-1]

        # Reset previous default certificate.
        identityUri = identityName.toUri()
        cursor = self._database.cursor()
        cursor.execute(
          "UPDATE Certificate SET default_cert=0 WHERE default_cert=1 AND identity_name=? AND key_identifier=?",
          (identityUri, keyId))

        # Set the current default Certificate.
        cursor.execute(
          "UPDATE Certificate SET default_cert=1 WHERE identity_name=? AND key_identifier=? AND cert_name=?",
            (identityUri, keyId, certificateName.toUri()))

        self._database.commit()
        cursor.close()
