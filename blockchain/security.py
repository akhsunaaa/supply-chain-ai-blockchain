from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Tuple, Dict, Optional
import json
import hashlib
from datetime import datetime, timedelta
import threading
from functools import lru_cache

class CryptographicSecurity:
    def __init__(self):
        self.backend = default_backend()
        self._generate_key_pair()
        self.key_rotation_interval = timedelta(days=7)  # Rotate keys weekly
        self.last_key_rotation = datetime.now()
        self._key_rotation_lock = threading.Lock()
        
        # Initialize key rotation thread
        self._start_key_rotation_thread()
        
    def _start_key_rotation_thread(self):
        """Start background thread for key rotation"""
        def rotation_worker():
            while True:
                with self._key_rotation_lock:
                    if datetime.now() - self.last_key_rotation > self.key_rotation_interval:
                        self._rotate_keys()
                threading.Event().wait(3600)  # Check every hour
                
        thread = threading.Thread(target=rotation_worker, daemon=True)
        thread.start()
        
    def _rotate_keys(self):
        """Rotate cryptographic keys"""
        old_public_key = self.public_key
        self._generate_key_pair()
        self.last_key_rotation = datetime.now()
        return old_public_key
        
    def _generate_key_pair(self) -> None:
        """Generate RSA key pair for digital signatures with improved key size"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,  # Increased from 2048 for better security
            backend=self.backend
        )
        self.public_key = self.private_key.public_key()
        
    @lru_cache(maxsize=1000)
    def generate_salt(self) -> bytes:
        """Generate a cryptographically secure salt with caching"""
        return os.urandom(32)  # Increased from 16 for better security
        
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive a key from password using PBKDF2 with improved parameters"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),  # Upgraded from SHA256
            length=64,  # Increased from 32
            salt=salt,
            iterations=310000,  # Increased from 100000
            backend=self.backend
        )
        return kdf.derive(password.encode())
        
    def encrypt_data(self, data: str, key: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data using AES-256-GCM with improved security"""
        iv = os.urandom(16)  # Increased from 12
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag_length=16),  # Explicit tag length
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        return ciphertext, iv
        
    def decrypt_data(self, ciphertext: bytes, iv: bytes, key: bytes) -> str:
        """Decrypt data using AES-256-GCM with improved security"""
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag_length=16),  # Explicit tag length
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()
        
    @lru_cache(maxsize=1000)
    def sign_data(self, data: Dict) -> bytes:
        """Sign data using RSA-PSS with improved parameters"""
        data_string = json.dumps(data, sort_keys=True)
        signature = self.private_key.sign(
            data_string.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),  # Upgraded from SHA256
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()  # Upgraded from SHA256
        )
        return signature
        
    def verify_signature(self, data: Dict, signature: bytes) -> bool:
        """Verify RSA-PSS signature with improved parameters"""
        try:
            data_string = json.dumps(data, sort_keys=True)
            self.public_key.verify(
                signature,
                data_string.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),  # Upgraded from SHA256
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()  # Upgraded from SHA256
            )
            return True
        except:
            return False
            
    @lru_cache(maxsize=1000)
    def generate_merkle_root(self, transactions: tuple) -> str:
        """Generate Merkle root from list of transactions with caching"""
        if not transactions:
            return ""
            
        # Convert transactions to hashes using SHA-3
        hashes = [hashlib.sha3_512(json.dumps(tx, sort_keys=True).encode()).hexdigest() 
                 for tx in transactions]
        
        # Build Merkle tree with improved hashing
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha3_512(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            hashes = new_hashes
            
        return hashes[0]
        
    @lru_cache(maxsize=1000)
    def hash_transaction(self, transaction: Dict) -> str:
        """Generate SHA-3 hash of transaction with caching"""
        return hashlib.sha3_512(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()
        
    def export_public_key(self) -> str:
        """Export public key in PEM format"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
    def import_public_key(self, key_pem: str) -> None:
        """Import public key from PEM format"""
        self.public_key = serialization.load_pem_public_key(
            key_pem.encode(),
            backend=self.backend
        ) 