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
    for i in range(20):
        key = generate_xxh128_key(f"sample-{i}")
        value = {"index": i, "data": f"this is value {i}"}
        
        print(f"Inserted key: {key} - i: {i}")
        
        tree.insert(key, value)

        print('\n\n')
        # tree.root.print_node()
        tree.traverse_pretty()
        print('\n\n')

    tree.traverse_pretty()

    # Retrieve a value
    for i in range(20):
        test_key = generate_xxh128_key(f"sample-{i}")
        result = tree.search(test_key)
        print(f"\nRetrieved for key {test_key}: {result}")

    # # Traverse the tree
    # print("\nTraversing all key-value pairs:")
    # for k, v in tree.traverse():
    #     print(f"Key: {k} => Value: {v}")

    # print(tree.traverse_pretty())

    tree.close()

if __name__ == "__main__":
    main()
