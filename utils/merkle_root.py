from utils.hashing import hash256


# def merkle_parent(arg0, arg1):
#     hash0 = bytes.fromhex(arg0)
#     hash1 = bytes.fromhex(arg1)
#     parent = hash256(hash0+hash1)
#     return parent


def compute_merkle_root(transactions) -> bytes:
    # Compute the merkle root of a list of transactions
    # Args:
    #    transactions (list[Transaction]): list of transactions
    # Returns:
    #    bytes: merkle root
    if len(transactions) == 1:
        merkle_root = hash256(transactions[0].serialize())
    else:
        hashes = []
        for tx in transactions:
            hashes.append(tx.get_hash())
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [hash256(a + b) for (a, b) in zip(
                hashes[0::2], hashes[1::2])]
        merkle_root = hashes[0]
    return merkle_root
