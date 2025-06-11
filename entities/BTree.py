import os
import struct

# Constants
ORDER = 4  # B-Tree order (max children per node)
PTR_FORMAT = 'Q'  # 8-byte unsigned long long (offsets)
KEY_SIZE = 32  # 32-character hex string
KEY_FORMAT = f'{KEY_SIZE}s'

MAX_KEYS = ORDER - 1
VALUE_SIZE = 256  # or whatever max value size you want
VALUE_FORMAT = f'{VALUE_SIZE}s'
NODE_FORMAT = f'{MAX_KEYS}{KEY_FORMAT}{MAX_KEYS}{VALUE_FORMAT}{ORDER}{PTR_FORMAT}?Q'
NODE_SIZE = struct.calcsize(NODE_FORMAT)


# XXX: VERIFICAR IMPLEMENTAÇÃO
class BTreeNode:
    def __init__(self, keys=None, values=None, children=None, is_leaf=True, self_offset=0):
        self.keys = keys or []
        self.values = values or []
        self.children = children or [0] * ORDER
        self.is_leaf = is_leaf
        self.self_offset = self_offset

    def serialize(self) -> bytes:
        keys = [k.encode('utf-8').ljust(KEY_SIZE, b'\x00') for k in self.keys]
        keys += [b'\x00' * KEY_SIZE] * (MAX_KEYS - len(keys))

        values = [v.encode('utf-8').ljust(VALUE_SIZE, b'\x00') for v in self.values]
        values += [b'\x00' * VALUE_SIZE] * (MAX_KEYS - len(values))

        packed = struct.pack(
            NODE_FORMAT,
            *keys,
            *values,
            *self.children,
            self.is_leaf,
            self.self_offset
        )
        return packed

    @staticmethod
    def deserialize(data: bytes) -> 'BTreeNode':
        unpacked = struct.unpack(NODE_FORMAT, data)

        key_bytes = unpacked[:MAX_KEYS]
        value_bytes = unpacked[MAX_KEYS:2 * MAX_KEYS]

        keys = [k.decode('utf-8').rstrip('\x00') for k in key_bytes]
        values = [v.decode('utf-8').rstrip('\x00') for v in value_bytes]

        # filter out empty entries
        key_value_pairs = [(k, v) for k, v in zip(keys, values) if k]

        keys, values = zip(*key_value_pairs) if key_value_pairs else ([], [])

        children = list(unpacked[2 * MAX_KEYS : 2 * MAX_KEYS + ORDER])
        is_leaf = unpacked[-2]
        self_offset = unpacked[-1]

        return BTreeNode(list(keys), list(values), children, is_leaf, self_offset)

    def traverse(self, node: BTreeNode = None):
        node = node or self.root
        result = []

        for i in range(len(node.keys)):
            if not node.is_leaf:
                child = self._read_node(node.children[i])
                result.extend(self.traverse(child))

            result.append((node.keys[i], node.values[i]))

        if not node.is_leaf:
            child = self._read_node(node.children[len(node.keys)])
            result.extend(self.traverse(child))

        return result


class DiskBTree:
    def __init__(self, filename='btree.dat'):
        self.filename = filename
        if not os.path.exists(filename):
            self.file = open(filename, 'wb+')
            self.root = self._new_node(is_leaf=True)
            self._write_node(self.root)
        else:
            self.file = open(filename, 'rb+')
            self.root = self._read_node(0)

    def _new_node(self, is_leaf=True) -> BTreeNode:
        self.file.seek(0, os.SEEK_END)
        offset = self.file.tell()
        return BTreeNode([], [0] * ORDER, is_leaf, offset)

    def _write_node(self, node: BTreeNode):
        self.file.seek(node.self_offset)
        self.file.write(node.serialize())
        self.file.flush()

    def _read_node(self, offset: int) -> BTreeNode:
        self.file.seek(offset)
        data = self.file.read(NODE_SIZE)
        return BTreeNode.deserialize(data)

    def search(self, key: int, node: BTreeNode = None):
        node = node or self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node, i
        if node.is_leaf:
            return None
        child = self._read_node(node.children[i])
        return self.search(key, child)

    def insert(self, key: int):
        root = self.root
        if len(root.keys) == MAX_KEYS:
            new_root = self._new_node(is_leaf=False)
            new_root.children[0] = root.self_offset
            self.root = new_root
            self._split_child(new_root, 0)
            self._insert_nonfull(new_root, key)
            self._write_node(new_root)
        else:
            self._insert_nonfull(root, key)
            self._write_node(root)

    def _insert_nonfull(self, node: BTreeNode, key: int):
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(0)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            self._write_node(node)
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            child = self._read_node(node.children[i])
            if len(child.keys) == MAX_KEYS:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
                child = self._read_node(node.children[i])
            self._insert_nonfull(child, key)

    def _split_child(self, parent: BTreeNode, i: int):
        y = self._read_node(parent.children[i])
        z = self._new_node(is_leaf=y.is_leaf)

        mid = MAX_KEYS // 2
        z.keys = y.keys[mid + 1:]
        y.keys = y.keys[:mid]

        if not y.is_leaf:
            z.children = y.children[mid + 1:]
            y.children = y.children[:mid + 1]

        parent.keys.insert(i, y.keys.pop())
        self._write_node(y)
        self._write_node(z)

        parent.children.insert(i + 1, z.self_offset)
        parent.children = parent.children[:ORDER]
        self._write_node(parent)

    def close(self):
        self.file.close()
