from blockchain.BlockHeader import BlockHeader
from database.DatabaseController import DatabaseController, query_func

__table_name = "block_headers"
__table_col = [
    "prev_hash",
    "hash",
    "merkel_root",
    "timestamp",
    "nonce",
    "bits",
    "height"
]


@query_func
def get_max_height(db=None):
    res = db.fetchOne(f"SELECT MAX(height) FROM {__table_name}")
    if res[0]:
        return res[0]
    return 0


@query_func
def insert_header(header: BlockHeader, db=None):
    values = header_to_data(header)
    return db.insert(__table_name, __table_col, values)


@query_func
def get_header_by_hash(header_hash: bytes, db: DatabaseController = None) -> tuple[int, BlockHeader]:
    header_data = db.selectOne(table_name=__table_name,
                               where="hash", field="*", params=(header_hash,))
    if not header_data:
        return None, None
    return header_data[0], data_to_header(header_data)


def header_to_data(header: BlockHeader):
    return (
        header.get_prev_block_hash(),
        header.get_hash(),
        header.get_merkle_root(),
        header.get_timestamp(),
        header.get_nonce(),
        header.get_bits(),
        get_max_height() + 1
    )


def data_to_header(data: tuple) -> BlockHeader:
    _, prev_block_hash, _, merkle_root, timestamp, nonce, bits, _ = data
    return BlockHeader(prev_block_hash, merkle_root, bits, nonce, timestamp)
