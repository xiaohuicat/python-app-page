import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# 生成非对称加密的私钥和公钥
def rsa_generate_keys():
    # 生成RSA密钥对
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 从私钥导出公钥
    public_key = private_key.public_key()

    # 将私钥序列化为PEM格式
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 将公钥序列化为PEM格式
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

# 使用公钥进行非对称加密
def rsa_encrypt(public_pem:str, plaintext:str):
    # 从PEM格式的公钥加载公钥对象
    public_key = serialization.load_pem_public_key(public_pem.encode('utf-8'))

    # 使用公钥加密数据
    ciphertext = public_key.encrypt(
        plaintext.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(ciphertext).decode('ascii')

# 使用私钥进行非对称解密
def rsa_decrypt(private_pem:str, ciphertext:str):
    # 从PEM格式的私钥加载私钥对象
    private_key = serialization.load_pem_private_key(private_pem.encode('utf-8'), password=None)

    # 使用私钥解密数据
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return plaintext.decode('utf-8')