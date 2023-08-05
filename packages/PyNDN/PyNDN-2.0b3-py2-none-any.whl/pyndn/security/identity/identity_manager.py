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
This module defines the IdentityManager class which is the interface of
operations related to identity, keys, and certificates.
"""

import sys
from Crypto.Hash import SHA256
from pyndn.name import Name
from pyndn.data import Data
from pyndn.util.common import Common
from pyndn.util.blob import Blob
from pyndn.encoding import WireFormat
from pyndn.sha256_with_rsa_signature import Sha256WithRsaSignature
from pyndn.key_locator import KeyLocatorType
from pyndn.digest_sha256_signature import DigestSha256Signature
from pyndn.security.identity.basic_identity_storage import BasicIdentityStorage
from pyndn.security.identity.file_private_key_storage import FilePrivateKeyStorage
from pyndn.security.identity.osx_private_key_storage import OSXPrivateKeyStorage
from pyndn.security.security_exception import SecurityException
from pyndn.security.security_types import KeyType, DigestAlgorithm
from pyndn.security.key_params import RsaKeyParams
from pyndn.security.certificate import IdentityCertificate
from pyndn.security.certificate import PublicKey, CertificateSubjectDescription

class IdentityManager(object):
    """
    Create a new IdentityManager to use the optional identityStorage and
    privateKeyStorage.

    :param IdentityStorage identityStorage: (optional) An object of a subclass
      of IdentityStorage. If omitted, use BasicIdentityStorage.
    :param PrivateKeyStorage privateKeyStorage: (optional) An object of a
      subclass of PrivateKeyStorage. If omitted, use the default
      PrivateKeyStorage for your system, which is OSXPrivateKeyStorage for OS X,
      otherwise FilePrivateKeyStorage.
    """
    def __init__(self, identityStorage = None, privateKeyStorage = None):
        if identityStorage == None:
            identityStorage = BasicIdentityStorage()
        if privateKeyStorage == None:
            if sys.platform == 'darwin':
                # Use the OS X Keychain
                privateKeyStorage = OSXPrivateKeyStorage()
            else:
                privateKeyStorage = FilePrivateKeyStorage()

        self._identityStorage = identityStorage
        self._privateKeyStorage = privateKeyStorage

    def createIdentity(self, identityName, params):
        """
        Create an identity by creating a pair of Key-Signing-Key (KSK) for this
        identity and a self-signed certificate of the KSK.

        :param Name identityName: The name of the identity.
        :return: The key name of the auto-generated KSK of the identity.
        :rtype: Name
        """
        self._identityStorage.addIdentity(identityName)
        keyName = self._generateKeyPair(identityName, True, params)
        self._identityStorage.setDefaultKeyNameForIdentity(keyName, identityName)
        newCert = self.selfSign(keyName)
        self.addCertificateAsDefault(newCert)

        return keyName

    def deleteIdentity(self, identityName):
        """
        Delete the identity from the public and private key storage. If the
        identity to be deleted is current default system default, the method
        will not delete the identity and will return immediately.
        :param Name identityName: The name of the identity to delete.
        """
        try:
            if (self._identityStorage.getDefaultIdentity() == identityName):
                return # don't delete the default identity!
        except SecurityException:
            # There is no default identity to check.
            pass
        
        keysToDelete = []
        self._identityStorage.getAllKeyNamesOfIdentity(identityName, keysToDelete, True)
        self._identityStorage.getAllKeyNamesOfIdentity(identityName, keysToDelete, False)

        self._identityStorage.deleteIdentityInfo(identityName)

        for keyName in keysToDelete:
            self._privateKeyStorage.deleteKeyPair(keyName)

    def setDefaultIdentity(self, identityName):
        """
        Set the default identity. If the identityName does not exist, then clear
        the default identity so that getDefaultIdentity() raises an exception.

        :param Name identityName: The default identity name.
        """
        self._identityStorage.setDefaultIdentity(identityName)

    def getDefaultIdentity(self):
        """
        Get the default identity.

        :return: The name of default identity.
        :rtype: Name
        :raises SecurityException: if the default identity is not set.
        """
        return self._identityStorage.getDefaultIdentity()

    def generateRSAKeyPair(self, identityName, isKsk = False, keySize = 2048):
        """
        Generate a pair of RSA keys for the specified identity.

        :param Name identityName: The name of the identity.
        :param bool isKsk: (optional) true for generating a Key-Signing-Key
          (KSK), false for a Data-Signing-Key (DSK). If omitted, generate a
          Data-Signing-Key.
        :param int keySize: (optional) The size of the key. If omitted, use a
          default secure key size.
        :return: The generated key name.
        :rtype: Name
        """
        keyName = self._generateKeyPair(identityName, isKsk, RsaKeyParams(keySize))
        return keyName

    def setDefaultKeyForIdentity(self, keyName, identityName = None):
        """
        Set a key as the default key of an identity.

        :param Name keyName: The name of the key.
        :param Name identityName: (optional) the name of the identity. If not
          specified, the identity name is inferred from the keyName.
        """
        if identityName == None:
            identityName = Name()
        self._identityStorage.setDefaultKeyNameForIdentity(keyName, identityName)

    def getDefaultKeyNameForIdentity(self,identityName = None):
        """
        Get the default key for an identity.

        :param Name identityName: The name of the identity.
        :raises SecurityException: if the default key name for the identity is
          not set.
        """
        return self._identityStorage.getDefaultKeyNameForIdentity(identityName)

    def generateRSAKeyPairAsDefault(
          self, identityName, isKsk = False, keySize = 2048):
        """
        Generate a pair of RSA keys for the specified identity and set it as
        default key for the identity.

        :param NameidentityName: The name of the identity.
        :param bool isKsk: (optional) true for generating a Key-Signing-Key
          (KSK), false for a Data-Signing-Key (DSK). If omitted, generate a
          Data-Signing-Key.
        :param int keySize: (optional) The size of the key. If omitted, use a
          default secure key size.
        :return: The generated key name.
        :rtype: Name
        """
        newKeyName = self.generateRSAKeyPair(identityName, isKsk, keySize)
        self._identityStorage.setDefaultKeyNameForIdentity(newKeyName, identityName)
        return newKeyName

    def getPublicKey(self, keyName):
        """
        Get the public key with the specified name.

        :param Name keyName: The name of the key.
        :return: The public key.
        :rtype: PublicKey
        """
        return PublicKey(self._identityStorage.getKey(keyName))

    # TODO: Add two versions of createIdentityCertificate.

    def addCertificate(self, certificate):
        """
        Add a certificate into the public key identity storage.

        :param IdentityCertificate certificate: The certificate to to added.
          This makes a copy of the certificate.
        """
        self._identityStorage.addCertificate(certificate)

    def setDefaultCertificateForKey(self, certificate):
        """
        Set the certificate as the default for its corresponding key.

        :param IdentityCertificate certificate: The certificate.
        """
        keyName = certificate.getPublicKeyName()

        if not self._identityStorage.doesKeyExist(keyName):
            raise SecurityException("No corresponding Key record for certificate!")

        self._identityStorage.setDefaultCertificateNameForKey(
          keyName, certificate.getName())

    def addCertificateAsIdentityDefault(self, certificate):
        """
        Add a certificate into the public key identity storage and set the
        certificate as the default for its corresponding identity.

        :param IdentityCertificate certificate: The certificate to to added.
          This makes a copy of the certificate.
        """
        self._identityStorage.addCertificate(certificate)
        keyName = certificate.getPublicKeyName()
        self.setDefaultKeyForIdentity(keyName)
        self.setDefaultCertificateForKey(certificate)

    def addCertificateAsDefault(self, certificate):
        """
        Add a certificate into the public key identity storage and set the
        certificate as the default of its corresponding key.

        :param IdentityCertificate certificate: The certificate to to added.
          This makes a copy of the certificate.
        """
        self._identityStorage.addCertificate(certificate)
        self.setDefaultCertificateForKey(certificate)

    def getCertificate(self, certificateName):
        """
        Get a certificate with the specified name.

        :param Name certificateName: The name of the requested certificate.
        :return: The requested certificate which is valid.
        :rtype: IdentityCertificate
        """
        return self._identityStorage.getCertificate(certificateName, False)

    def getAnyCertificate(self, certificateName):
        """
        Get a certificate even if the certificate is not valid anymore.

        :param Name certificateName: The name of the requested certificate.
        :return: The requested certificate.
        :rtype: IdentityCertificate
        """
        return self._identityStorage.getCertificate(certificateName, True)

    def getDefaultCertificateNameForIdentity(self, identityName):
        """
        Get the default certificate name for the specified identity, which will
        be used when signing is performed based on identity.

        :param Name identityName: The name of the specified identity.
        :return: The requested certificate name.
        :rtype: Name
        :raises SecurityException: if the default key name for the identity is
          not set or the default certificate name for the key name is not set.
        """
        return self._identityStorage.getDefaultCertificateNameForIdentity(
          identityName)

    def getDefaultCertificateName(self):
        """
        Get the default certificate name of the default identity.

        :return: The requested certificate name.
        :rtype: Name
        :raises SecurityException: if the default identity is not set or the
          default key name for the identity is not set or the default
          certificate name for the key name is not set.
        """
        return self._identityStorage.getDefaultCertificateNameForIdentity(
          self.getDefaultIdentity())

    def signByCertificate(self, target, certificateName, wireFormat = None):
        """
        Sign the target based on the certificateName. If it is a Data object,
        set its signature. If it is an array, return a signature object.

        :param target: If this is a Data object, wire encode for signing,
          update its signature and key locator field and wireEncoding. If it is
          an array, sign it and return a Signature object.
        :param Name certificateName: The Name identifying the certificate which
          identifies the signing key.
        :param wireFormat: (optional) The WireFormat for calling encodeData, or
          WireFormat.getDefaultWireFormat() if omitted.
        :type wireFormat: A subclass of WireFormat
        :return: The Signature object (only if the target is an array).
        :rtype: An object of a subclass of Signature
        """
        if wireFormat == None:
            # Don't use a default argument since getDefaultWireFormat can change.
            wireFormat = WireFormat.getDefaultWireFormat()

        if isinstance(target, Data):
            data = target
            digestAlgorithm = [0]
            signature = self._makeSignatureByCertificate(
              certificateName, digestAlgorithm)

            data.setSignature(signature)
            # Encode once to get the signed portion.
            encoding = data.wireEncode(wireFormat)

            data.getSignature().setSignature(self._privateKeyStorage.sign
              (encoding.toSignedBuffer(),
               self.certificateNameToPublicKeyName(certificateName),
               digestAlgorithm[0]))

            # Encode again to include the signature.
            data.wireEncode(wireFormat)
        else:
            digestAlgorithm = [0]
            signature = self._makeSignatureByCertificate(
              certificateName, digestAlgorithm)

            signature.setSignature(
              self._privateKeyStorage.sign(
                target, self.certificateNameToPublicKeyName(certificateName),
                digestAlgorithm[0]))

            return signature

    def signInterestByCertificate(self, interest, certificateName, wireFormat = None):
        """
        Append a SignatureInfo to the Interest name, sign the name components
        and append a final name component with the signature bits.

        :param Interest interest: The Interest object to be signed. This appends
          name components of SignatureInfo and the signature bits.
        :param Name certificateName: The certificate name of the key to use for
          signing.
        :param wireFormat: (optional) A WireFormat object used to encode the
           input. If omitted, use WireFormat.getDefaultWireFormat().
        :type wireFormat: A subclass of WireFormat
        """
        if wireFormat == None:
            # Don't use a default argument since getDefaultWireFormat can change.
            wireFormat = WireFormat.getDefaultWireFormat()

        digestAlgorithm = [0]
        signature = self._makeSignatureByCertificate(
          certificateName, digestAlgorithm)

        # Append the encoded SignatureInfo.
        interest.getName().append(wireFormat.encodeSignatureInfo(signature))

        # Append an empty signature so that the "signedPortion" is correct.
        interest.getName().append(Name.Component())
        # Encode once to get the signed portion, and sign.
        encoding = interest.wireEncode(wireFormat)
        signature.setSignature(self._privateKeyStorage.sign
          (encoding.toSignedBuffer(),
           self.certificateNameToPublicKeyName(certificateName),
           digestAlgorithm[0]))

        # Remove the empty signature and append the real one.
        interest.setName(interest.getName().getPrefix(-1).append(
          wireFormat.encodeSignatureValue(signature)))

    def signWithSha256(self, data, wireFormat = None):
        """
        Wire encode the Data object, digest it and set its SignatureInfo to a
        DigestSha256.

        :param Data data: The Data object to be signed. This updates its
          signature and wireEncoding.
        :param wireFormat: (optional) A WireFormat object used to encode the
           input. If omitted, use WireFormat.getDefaultWireFormat().
        :type wireFormat: A subclass of WireFormat
        """
        if wireFormat == None:
            # Don't use a default argument since getDefaultWireFormat can change.
            wireFormat = WireFormat.getDefaultWireFormat()

        data.setSignature(DigestSha256Signature())
        # Encode once to get the signed portion.
        encoding = data.wireEncode(wireFormat)

        # Get the bytes to sign.
        signedPortion = encoding.toSignedBuffer()
        if sys.version_info[0] == 2:
            # In Python 2.x, we need a str.  Use Blob to convert signedPortion.
            signedPortion = Blob(signedPortion, False).toRawStr()

        # Digest and set the signature.
        data.getSignature().setSignature(Blob(SHA256.new(signedPortion).digest()))

        # Encode again to include the signature.
        data.wireEncode(wireFormat)

    def signInterestWithSha256(self, interest, wireFormat = None):
        """
        Append a SignatureInfo for DigestSha256 to the Interest name, digest the
        name components and append a final name component with the signature
        bits (which is the digest).

        :param Interest interest: The Interest object to be signed. This appends
          name components of SignatureInfo and the signature bits.
        :param wireFormat: (optional) A WireFormat object used to encode the
           input. If omitted, use WireFormat.getDefaultWireFormat().
        :type wireFormat: A subclass of WireFormat
        """
        if wireFormat == None:
            # Don't use a default argument since getDefaultWireFormat can change.
            wireFormat = WireFormat.getDefaultWireFormat()

        signature = DigestSha256Signature()
        # Append the encoded SignatureInfo.
        interest.getName().append(wireFormat.encodeSignatureInfo(signature))

        # Append an empty signature so that the "signedPortion" is correct.
        interest.getName().append(Name.Component())
        # Encode once to get the signed portion.
        encoding = interest.wireEncode(wireFormat)

        # Get the bytes to sign.
        signedPortion = encoding.toSignedBuffer()
        if sys.version_info[0] == 2:
            # In Python 2.x, we need a str.  Use Blob to convert signedPortion.
            signedPortion = Blob(signedPortion, False).toRawStr()

        # Digest and set the signature.
        signature.setSignature(Blob(SHA256.new(signedPortion).digest()))

        # Remove the empty signature and append the real one.
        interest.setName(interest.getName().getPrefix(-1).append(
          wireFormat.encodeSignatureValue(signature)))

    def selfSign(self, keyName):
        """
        Generate a self-signed certificate for a public key.

        :param Name keyName: The name of the public key.
        :return: The generated certificate.
        :rtype: IdentityCertificate
        """
        certificate = self._generateCertificateForKey(keyName)
        self.signByCertificate(certificate, certificate.getName())

        return certificate

    # TODO: Move this to IdentityCertificate
    @staticmethod
    def certificateNameToPublicKeyName(certificateName):
        """
        Get the public key name from the full certificate name.

        :param Name certificateName: The full certificate name.
        :return: The related public key name.
        :rtype: Name
        """
        i = certificateName.size() - 1
        idString = "ID-CERT"
        while i >= 0:
            if certificateName[i].toEscapedString() == idString:
                break
            i -= 1

        tmpName = certificateName.getSubName(0, i)
        keyString = "KEY"
        i = 0
        while i < tmpName.size():
            if tmpName[i].toEscapedString() == keyString:
                break
            i += 1

        return tmpName.getSubName(0, i).append(tmpName.getSubName(
                 i + 1, tmpName.size() - i - 1))

    def _generateCertificateForKey(self, keyName):
        # Let any raised SecurityExceptions bubble up.
        publicKeyBits = self._identityStorage.getKey(keyName)

        publicKey = PublicKey(publicKeyBits)

        timestamp = Common.getNowMilliseconds()

        # TODO: Specify where the 'KEY' component is inserted
        # to delegate responsibility for cert delivery.
        # cf: http://redmine.named-data.net/issues/1659
        certificateName = keyName.getPrefix(-1).append('KEY').append(keyName.get(-1))
        certificateName.append("ID-CERT").append(
          Name.Component.fromNumber(int(timestamp)))

        certificate = IdentityCertificate(certificateName)

        certificate.setNotBefore(timestamp)
        certificate.setNotAfter((timestamp + 2*365*24*3600*1000)) # about 2 years.

        certificate.setPublicKeyInfo(publicKey)

        # ndnsec likes to put the key name in a subject description.
        sd = CertificateSubjectDescription("2.5.4.41", keyName.toUri())
        certificate.addSubjectDescription(sd)

        certificate.encode()

        return certificate

    def _makeSignatureByCertificate(self, certificateName, digestAlgorithm):
        """
        Return a new Signature object based on the signature algorithm of the
        public key with keyName (derived from certificateName).

        :param Name certificateName: The full certificate name.
        :param Array digestAlgorithm: Set digestAlgorithm[0] to the signature
          algorithm's digest algorithm, e.g. DigestAlgorithm.SHA256 .
        :return: The related public key name.
        :rtype: Signature
        """
        keyName = self.certificateNameToPublicKeyName(certificateName)
        publicKey = self._privateKeyStorage.getPublicKey(keyName)
        keyType = publicKey.getKeyType()

        if keyType == KeyType.RSA:
            signature = Sha256WithRsaSignature()
            digestAlgorithm[0] = DigestAlgorithm.SHA256

            signature.getKeyLocator().setType(KeyLocatorType.KEYNAME)
            signature.getKeyLocator().setKeyName(certificateName.getPrefix(-1))

            return signature
        else:
            raise SecurityException("Key type is not recognized")

    def _generateKeyPair(self, identityName, isKsk, params):
        """
        Generate a pair of keys for the specified identity.

        :param Name identityName: The name of the identity.
        :param bool isKsk: (optional) true for generating a Key-Signing-Key
          (KSK), false for a Data-Signing-Key (DSK). If omitted, generate a
          Data-Signing-Key.
        :param KeyParams params: The parameters of the key.
        :return: The generated key name.
        :rtype: Name
        """
        keyName = self._identityStorage.getNewKeyName(identityName, isKsk)
        self._privateKeyStorage.generateKeyPair(keyName, params)
        publicKeyBits = self._privateKeyStorage.getPublicKey(keyName).getKeyDer()
        self._identityStorage.addKey(keyName, params.getKeyType(), publicKeyBits)

        return keyName
