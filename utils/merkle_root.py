from utils.hashing import hash256


def merkle_parent(arg0, arg1):
    hash0 = bytes.fromhex(arg0)
    hash1 = bytes.fromhex(arg1)
    parent = hash256(hash0+hash1)
    return parent


def compute_merkle_root(transactions) -> bytes:
    # Compute the merkle root of a list of transactions
    # Args:
    #    transactions (list[Transaction]): list of transactions
    # Returns:
    #    bytes: merkle root
    if len(transactions) == 1:
        merkle_root = hash256(transactions[0].serialize())
    else:
        hex_hashes = []
        for _ in range(len(transactions)):
            hash_transac = transactions[_].get_hash()
            hex_hashes.append(hash_transac.hex())
        while len(hex_hashes) > 1:
            if len(hex_hashes) % 2 == 1:
                hex_hashes.append(hex_hashes[-1])
            hex_hashes = [merkle_parent(a, b) for (a, b) in zip(
                hex_hashes[0::2], hex_hashes[1::2])]
        merkle_root = hex_hashes[0]
    return merkle_root
