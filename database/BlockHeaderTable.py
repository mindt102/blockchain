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


@query_func
def get_max_height(db=None) -> int:
    res = db.fetchOne(f"SELECT MAX(height) FROM {__table_name}")
    __logger.debug(f"Max height: {res}")
    if res[0]:
        return res[0]
    return 0


@query_func
def get_header_by_maxheight(db=None) -> tuple[BlockHeader, int, int]:
    '''
    Get the header with the highest height
    Returns:
        tuple[int, BlockHeader]: (header_id, header)
    '''
    max_height = get_max_height(db=db)
    header_data = db.selectOne(table_name=__table_name, where="height",
                               field="*", params=(max_height,))
    if not header_data:
        return None, None, None
    return data_to_header(header_data)


@query_func
def insert_header(header: BlockHeader, height, db=None):
    values = (
        header.get_prev_block_hash(),
        header.get_hash(),
        header.get_merkle_root(),
        header.get_timestamp(),
        header.get_nonce(),
        header.get_bits(),
        height
    )
    return db.insert(__table_name, __table_col, values)


@query_func
def get_header_by_hash(header_hash: bytes, db: DatabaseController = None) -> tuple[BlockHeader, int, int]:
    header_data = db.selectOne(table_name=__table_name,
                               where="hash", field="*", params=(header_hash,))
    if not header_data:
        return None, None, None
    return data_to_header(header_data)


def data_to_header(data: tuple) -> tuple[BlockHeader, int, int]:
    '''
    Convert data from database to BlockHeader
    Returns:
        tuple[BlockHeader, int, int]: (header, header_id, height)
    '''
    header_id, prev_block_hash, _, merkle_root, timestamp, nonce, bits, height = data
    return BlockHeader(prev_block_hash, merkle_root, bits, nonce, timestamp), header_id, height
