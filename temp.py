import xxhash
import random
from entities.BTree import DiskBTree

# Generate a sample B-tree and populate it
def generate_xxh128_key(data: str) -> str:
    return xxhash.xxh128(data.encode()).hexdigest()

def main():
    tree = DiskBTree('btree.dat', 'btree.values')

    # Sample data insertion
    print("Inserting key-value pairs...")
    for i in range(4):
        key = generate_xxh128_key(f"sample-{i}")
        value = {"index": i, "data": f"this is value {i}"}
        tree.insert(key, value)
        print(f"Inserted key: {key}")

    # Retrieve a value
    test_key = generate_xxh128_key("sample-5")
    result = tree.search(test_key)
    print(f"\nRetrieved for key {test_key}: {result}")

    # Traverse the tree
    print("\nTraversing all key-value pairs:")
    for k, v in tree.traverse():
        print(f"Key: {k} => Value: {v}")

    tree.close()

if __name__ == "__main__":
    main()
