from blockchain.BlockHeader import BlockHeader
from database.DatabaseController import DatabaseController, query_func
import utils

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
__logger = utils.get_logger(__name__)


def data_to_header(data: tuple) -> tuple[BlockHeader, int, int]:
    '''
    Convert data from database to BlockHeader
    Returns:
        tuple[BlockHeader, int, int]: (header, header_id, height)
    '''
    header_id, prev_block_hash, _, merkle_root, timestamp, nonce, bits, height = data
    header = BlockHeader(prev_block_hash, merkle_root, bits, nonce, timestamp)
    header.set_height(height)
    return header, header_id, height


@query_func
def get_max_height(db=None) -> int:
    res = db.fetchOne(f"SELECT MAX(height) FROM {__table_name}")
    if res[0]:
        return res[0]
    return 0


@query_func
def get_top_header(db=None) -> tuple[BlockHeader, int, int]:
    '''
    Get the header with the highest height
    Returns:
        tuple[BlockHeader, int, int]: (header, header_id, height)
    '''
    max_height = get_max_height(db=db)
    return get_header_by_height(max_height, max_height=max_height, db=db)


@query_func
def get_header_by_height(height: int, max_height=0, db=None) -> tuple[BlockHeader, int, int]:
    '''
    Get the header based on the height on the longest chain
    Returns:
        tuple[int, BlockHeader]: (header_id, header)
    '''
    header_data = db.selectAll(table_name=__table_name, where="height",
                               field="*", params=(height,))
    if len(header_data) == 0:
        return None, None, None
    elif len(header_data) == 1 or height == max_height:
        return data_to_header(header_data[0])
    else:
        if max_height == 0:
            max_height = get_max_height(db=db)
        next_header, _, _ = get_header_by_height(
            height + 1, max_height=max_height, db=db)
        if not next_header:
            raise Exception("Next header not found")
        for data in header_data:
            header, _, _ = data_to_header(data)
            if next_header.get_prev_block_hash() == header.get_hash():
                return data_to_header(data)


@query_func
def insert_header(header: BlockHeader, height, db=None):
    header.set_height(height)
    values = (
        header.get_prev_block_hash(),
        header.get_hash(),
        header.get_merkle_root(),
        header.get_timestamp(),
        header.get_nonce(),
        header.get_bits(),
        header.get_height()
    )
    return db.insert(__table_name, __table_col, values)


@query_func
def get_header_by_hash(header_hash: bytes, db: DatabaseController = None) -> tuple[BlockHeader, int, int]:
    '''
    Get the header based on the hash
    Returns:
        tuple[BlockHeader, int, int]: (header, header_id, height)
    '''
    header_data = db.selectOne(table_name=__table_name,
                               where="hash", field="*", params=(header_hash,))
    if not header_data:
        return None, None, None
    return data_to_header(header_data)


@query_func
def get_height_by_id(header_id: int, db: DatabaseController = None) -> int:
    '''
    Get the height of the header based on the id
    Returns:
        int: height
    '''
    res = db.fetchOne(
        f"SELECT height FROM {__table_name} WHERE id = ?", (header_id,))
    if res:
        return res[0]
    return None


@query_func
def get_bits_by_height(block_height, db=None):
    res = db.fetchOne(
        f"SELECT bits FROM {__table_name} WHERE height = ?", (block_height,))
    if res:
        return res[0]
    return None
