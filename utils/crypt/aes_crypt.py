from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode

# 加密
def aes_encrypt(plaintext:str, key:str):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    padded_plaintext = pad(plaintext.encode(), AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    return b64encode(ciphertext).decode()


# 解密
def aes_decrypt(ciphertext:str, key:str):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    ciphertext = b64decode(ciphertext)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size).decode()