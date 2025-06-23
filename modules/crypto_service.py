"""
Kriptografi Servisi
AES şifreleme, HMAC doğrulama ve anahtar türetme işlemlerini yönetir
"""

from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import pickle

class CryptoService:
    """Kriptografi işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def derive_keys(password: str, salt: bytes):
        """PBKDF2 ile anahtar türetme"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32 * 2,  # 32 bytes AES, 32 bytes HMAC
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key[:32], key[32:]  # AES key, HMAC key

    @staticmethod
    def encrypt_and_authenticate(data: bytes, aes_key: bytes, hmac_key: bytes):
        """Veriyi şifrele ve HMAC ile doğrula"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Padding (AES block = 16 byte)
        pad_len = 16 - (len(data) % 16)
        data += bytes([pad_len]) * pad_len

        ciphertext = encryptor.update(data) + encryptor.finalize()

        # HMAC hesapla
        h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
        h.update(iv + ciphertext)
        tag = h.finalize()

        return iv + ciphertext + tag

    @staticmethod
    def decrypt_and_verify(encrypted_data: bytes, aes_key: bytes, hmac_key: bytes):
        """Şifrelenmiş veriyi çöz ve doğrula"""
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:-32]
        tag = encrypted_data[-32:]

        # HMAC doğrulama
        h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=default_backend())
        h.update(iv + ciphertext)
        h.verify(tag)  # Doğrulama başarısızsa hata verir

        # AES çözme
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Padding çıkar
        pad_len = padded_data[-1]
        return padded_data[:-pad_len]

    @staticmethod
    def verify_password(password: str) -> bool:
        """Saklanan parola hash'i ile girilen parolayı doğrular"""
        try:
            with open("password_hash.bin", "rb") as f:
                data = f.read()
                salt = data[:16]
                stored_hash = data[16:]
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                    backend=default_backend()
                )
                password_hash = kdf.derive(password.encode())
                
                return password_hash == stored_hash
        except FileNotFoundError:
            return True  # Eğer parola dosyası yoksa, varsayılan olarak doğru kabul et

    @staticmethod
    def encrypt_share_data(share_data: dict, password: str) -> bytes:
        """Pay verisini şifrele"""
        salt = os.urandom(16)
        aes_key, hmac_key = CryptoService.derive_keys(password, salt)
        
        raw = pickle.dumps(share_data)
        encrypted = CryptoService.encrypt_and_authenticate(raw, aes_key, hmac_key)
        
        return salt + encrypted

    @staticmethod
    def decrypt_share_data(encrypted_data: bytes, password: str) -> dict:
        """Şifrelenmiş pay verisini çöz"""
        salt = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        
        aes_key, hmac_key = CryptoService.derive_keys(password, salt)
        raw = CryptoService.decrypt_and_verify(encrypted, aes_key, hmac_key)
        
        return pickle.loads(raw) 