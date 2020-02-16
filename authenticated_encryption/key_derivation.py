#!/usr/bin/env python3

from Crypto.Hash import (SHA512, HMAC)
from Crypto.Protocol.KDF import PBKDF2
from authenticated_encryption.program_options import (ProgramOptions,)


class KeyDerivation(object):
    def __init__(self, options: ProgramOptions):
        password = options.password.encode('UTF-8')
        salt = "I.Hlc0<SF>dk+YV+arbuEE__]O:Lfzw%HP3oSfF99C)8BDfE<jPz`ZA-\"_ZHT\
VUi+9'Aub*C'Q3xP(%&".encode('UTF-8')
        prf = lambda secret, salt: HMAC.new(
            key=secret, msg=salt, digestmod=SHA512).digest()
        key = PBKDF2(password=password, salt=salt, dkLen=96,
                     count=options.key_derivation_iterations, prf=prf)
        self._encryption_key = key[0:32]
        self._hmac_key = key[32:96]

    @property
    def encryption_key(self) -> bytes:
        return self._encryption_key

    @property
    def hmac_key(self) -> bytes:
        return self._hmac_key
