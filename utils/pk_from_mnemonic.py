import hashlib
import hmac
import struct
from ecdsa.curves import Ed25519


BIP39_PBKDF2_ROUNDS = 2048
BIP39_SALT_MODIFIER = "mnemonic"
BIP32_PRIVDEV = 0x80000000
BIP32_SEED_ED25519 = b'ed25519 seed'
APTOS_DERIVATION_PATH = "m/44'/637'/0'/0'/0'"
private_keys = []
addresses = []

class PublicKey25519:
    def __init__(self, private_key):
        self.private_key = private_key

    def __bytes__(self):
        sk = Ed25519.SigningKey(self.private_key)
        return '\x00' + sk.get_verifying_key().to_bytes()


def mnemonic_to_private_key(mnemonic, passphrase=""):
    derivation_path = parse_derivation_path()
    bip39seed = mnemonic_to_bip39seed(mnemonic, passphrase)
    master_private_key, master_chain_code = bip39seed_to_bip32masternode(bip39seed)
    private_key, chain_code = master_private_key, master_chain_code
    for i in derivation_path:
        private_key, chain_code = derive_bip32childkey(private_key, chain_code, i)
    return private_key

def derive_bip32childkey(parent_key, parent_chain_code, i):
        assert len(parent_key) == 32
        assert len(parent_chain_code) == 32
        k = parent_chain_code
        if (i & 0x80000000) != 0:
            key = b'\x00' + parent_key
        else:
            key = bytes(PublicKey25519(parent_key))

        d = key + struct.pack('>L', i)
    
        h = hmac.new(k, d, hashlib.sha512).digest()
        key, chain_code = h[:32], h[32:]
        
        return key, chain_code

def bip39seed_to_bip32masternode(seed):
    h = hmac.new(b'ed25519 seed', seed, hashlib.sha512).digest()
    key, chain_code = h[:32], h[32:]
    return key, chain_code

def mnemonic_to_bip39seed(mnemonic, passphrase):
    mnemonic = bytes(mnemonic, 'utf8')
    salt = bytes(BIP39_SALT_MODIFIER + passphrase, 'utf8')
    return hashlib.pbkdf2_hmac('sha512', mnemonic, salt, BIP39_PBKDF2_ROUNDS)

def parse_derivation_path():
    path = []
    if "m/44'/637'/0'/0'/0'"[0:2] != 'm/':
        raise ValueError("Can't recognize derivation path. It should look like \"m/44'/chaincode/change'/index\".")
    for i in "m/44'/637'/0'/0'/0'".lstrip('m/').split('/'):
        if "'" in i:
            path.append(0x80000000 + int(i[:-1]))
        else:
            path.append(int(i))
    
    return path
