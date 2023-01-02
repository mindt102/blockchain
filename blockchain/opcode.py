from utils import hash256, hash160

from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PublicKey
from ellipticcurve.signature import Signature


def op_dup(stack):
    if len(stack) < 1:
        return False
    stack.append(stack[-1])
    return True


def op_hash256(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    stack.append(hash256(element))
    return True


def op_hash160(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    h160 = hash160(element)
    stack.append(h160)
    return True


def op_equal(stack):
    if len(stack) < 2:
        return False
    element1 = stack.pop()
    element2 = stack.pop()
    if element1 == element2:
        stack.append(b'\x01')
    else:
        stack.append(b'\x00')
    return True


def op_verify(stack):
    if len(stack) < 1:
        return False
    element = stack.pop()
    if element == b'\x00':
        return False
    return True


def op_equalverify(stack):
    if not op_equal(stack):
        return False
    return op_verify(stack)


def op_checksig(stack, z):
    if len(stack) < 2:
        return False
    sec_pubkey = stack.pop()
    der_signature = stack.pop()[:-1]
    try:
        pubkey = PublicKey.fromDer(sec_pubkey)
        signature = Signature.fromDer(der_signature)
    except (ValueError, SyntaxError) as e:
        return False
    if Ecdsa.verify(z, signature, pubkey):
        stack.append(b'\x01')
    else:
        stack.append(b'\x00')
    return True


OP_CODE_FUNCTIONS = {
    b'\x76': op_dup,
    b'\xac': op_checksig,
    b'\xa9': op_hash160,
    b'\xac': op_hash256,
    b'\x88': op_equalverify,
}

# OP_CODE_NAMES = {
#     118: "op_dup",
#     170: "op_hash256"
# }
