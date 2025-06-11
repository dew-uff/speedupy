import os
import struct
import pickle

# Constants
ORDER = 4  # B-Tree order (max children per node)
KEY_SIZE = 32  # 32-character hex string
KEY_FORMAT = f'{KEY_SIZE}s'
PTR_FORMAT = 'Q'  # 8-byte unsigned long long

MAX_KEYS = ORDER - 1

NODE_FORMAT = (
    f'{KEY_FORMAT * MAX_KEYS}'    # 3 keys
    f'{PTR_FORMAT * MAX_KEYS}'    # 3 value offsets
    f'{PTR_FORMAT * ORDER}'       # 4 children
    f'?Q'                         # is_leaf, self_offset
)
NODE_SIZE = struct.calcsize(NODE_FORMAT)

# XXX: IMPLEMENTAR + TESTAR
class BTreeNode:
    def __init__(self, keys=None, value_offsets=None, children=None, is_leaf=True, self_offset=0):
        self.keys = keys or []
        self.value_offsets = value_offsets or []
        self.children = children or [0] * ORDER
        self.is_leaf = is_leaf
        self.self_offset = self_offset

    def serialize(self) -> bytes:
        keys = [k.encode('utf-8').ljust(KEY_SIZE, b'\x00') for k in self.keys]
        keys += [b'\x00' * KEY_SIZE] * (MAX_KEYS - len(keys))

        offsets = self.value_offsets + [0] * (MAX_KEYS - len(self.value_offsets))

        packed = struct.pack(
            NODE_FORMAT,
            *keys,
            *offsets,
            *self.children,
            self.is_leaf,
            self.self_offset
        )
        return packed

    @staticmethod
    def deserialize(data: bytes) -> 'BTreeNode':
        unpacked = struct.unpack(NODE_FORMAT, data)

        key_bytes = unpacked[:MAX_KEYS]
        offsets = list(unpacked[MAX_KEYS:2 * MAX_KEYS])

        keys = [k.decode('utf-8').rstrip('\x00') for k in key_bytes]
        key_offset_pairs = [(k, off) for k, off in zip(keys, offsets) if k]
        keys, value_offsets = zip(*key_offset_pairs) if key_offset_pairs else ([], [])

        children = list(unpacked[2 * MAX_KEYS:2 * MAX_KEYS + ORDER])
        is_leaf = unpacked[-2]
        self_offset = unpacked[-1]

        return BTreeNode(list(keys), list(value_offsets), children, is_leaf, self_offset)


# XXX: IMPLEMENTAR + TESTAR
class DiskBTree:
    def __init__(self, filename='btree.dat', value_filename='btree.values'):
        self.filename = filename
        self.value_filename = value_filename

        self.file = open(self.filename, 'rb+') if os.path.exists(filename) else open(self.filename, 'wb+')
        self.value_file = open(self.value_filename, 'ab+')
        self.value_file.seek(0, os.SEEK_END)

        if os.path.getsize(filename) == 0:
            self.root = self._new_node(is_leaf=True)
            self._write_node(self.root)
        else:
            self.root = self._read_node(0)

    def _new_node(self, is_leaf=True) -> BTreeNode:
        self.file.seek(0, os.SEEK_END)
        offset = self.file.tell()
        return BTreeNode([], [], [0] * ORDER, is_leaf, offset)

    def _write_node(self, node: BTreeNode):
        self.file.seek(node.self_offset)
        self.file.write(node.serialize())
        # self.file.flush()

    def _read_node(self, offset: int) -> BTreeNode:
        self.file.seek(offset)
        data = self.file.read(NODE_SIZE)
        return BTreeNode.deserialize(data)

    def _write_value(self, obj) -> int:
        data = pickle.dumps(obj)
        offset = self.value_file.tell()
        self.value_file.write(data)
        # self.value_file.flush()
        return offset

    def _read_value(self, offset: int):
        self.value_file.seek(offset)
        return pickle.load(self.value_file)

    def search(self, key: str, node: BTreeNode = None):
        node = node or self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return self._read_value(node.value_offsets[i])
        if node.is_leaf:
            return None
        child = self._read_node(node.children[i])
        return self.search(key, child)

    def insert(self, key: str, value):
        value_offset = self._write_value(value)
        root = self.root
        if len(root.keys) == MAX_KEYS:
            new_root = self._new_node(is_leaf=False)
            new_root.children[0] = root.self_offset
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_nonfull(new_root, key, value_offset)
            self._write_node(new_root)
        else:
            self._insert_nonfull(root, key, value_offset)
            self._write_node(root)

    def _insert_nonfull(self, node: BTreeNode, key: str, value_offset: int):
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append("")
            node.value_offsets.append(0)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.value_offsets[i + 1] = node.value_offsets[i]
                i -= 1
            node.keys[i + 1] = key
            node.value_offsets[i + 1] = value_offset
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
            self._insert_nonfull(child, key, value_offset)

    def _split_child(self, parent: BTreeNode, i: int):
        y = self._read_node(parent.children[i])
        z = self._new_node(is_leaf=y.is_leaf)

        mid = MAX_KEYS // 2

        parent.keys.insert(i, y.keys[mid])
        parent.value_offsets.insert(i, y.value_offsets[mid])

        y.keys = y.keys[:mid]
        y.value_offsets = y.value_offsets[:mid]
        z.keys = y.keys[mid + 1:]
        z.value_offsets = y.value_offsets[mid + 1:]

        if not y.is_leaf:
            y.children = y.children[:mid + 1]
            z.children = y.children[mid + 1:]

        parent.children.insert(i + 1, z.self_offset)
        parent.children = parent.children[:ORDER]

        self._write_node(y)
        self._write_node(z)
        self._write_node(parent)

    def traverse(self, node: BTreeNode = None):
        node = node or self.root
        result = []

        for i in range(len(node.keys)):
            if not node.is_leaf:
                child = self._read_node(node.children[i])
                result.extend(self.traverse(child))
            result.append((node.keys[i], self._read_value(node.value_offsets[i])))

        if not node.is_leaf:
            child = self._read_node(node.children[len(node.keys)])
            result.extend(self.traverse(child))

        return result

    def close(self):
        self.file.close()
        self.value_file.close()
