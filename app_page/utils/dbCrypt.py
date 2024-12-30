import time
from utils.crypt import aes_crypt
from utils.crypt import rsa_crypt
from nanoid import generate
# 双重加密
def dbCrypt(plaintext:str, public_pem:str, key_length=32, timeVerify=None):
  aes_key = generate(size=key_length)                                        # 随机生成32位AES对称加密密钥
  verify = f'{aes_key}{int(time.time()*1000)}' if timeVerify else aes_key
  rsa_aes_key = rsa_crypt.rsa_encrypt(public_pem, verify)                # 给对称加密密钥进行
  ret = aes_crypt.aes_encrypt(plaintext, aes_key)
  return ret, rsa_aes_key