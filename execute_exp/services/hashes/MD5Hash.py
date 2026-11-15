import hashlib
from execute_exp.services.hashes.Hash import Hash


class MD5Hash(Hash):
    def _hash(self, data: bytes) -> str:
        return hashlib.md5(data).hexdigest()
