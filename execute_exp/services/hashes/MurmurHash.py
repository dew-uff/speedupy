import mmh3
from execute_exp.services.hashes.Hash import Hash


class MurmurHash(Hash):
    def _hash(self, data: bytes) -> str:
        return hex(mmh3.hash128(data))[2:]
