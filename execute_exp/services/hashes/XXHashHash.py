import xxhash
from execute_exp.services.hashes.Hash import Hash


class XXHashHash(Hash):
    def hash(self, data: bytes) -> str:
        return xxhash.xxh128_hexdigest(data)
