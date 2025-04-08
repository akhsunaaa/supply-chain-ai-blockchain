# integration.py
from web3 import Web3
from datetime import datetime
import json
import hashlib
from typing import Dict, List, Optional
import logging
from .security import CryptographicSecurity
import base64
import threading

class SmartContract:
    """
    Simulated smart contract for supply chain operations.
    In production, this would interact with actual blockchain smart contracts.
    """
    def __init__(self):
        self.transactions = []
        self.events = []
        self.contract_address = "0x0000000000000000000000000000000000000000"  # Placeholder
        self.security = CryptographicSecurity()
        
    def emit_event(self, event_type: str, data: Dict) -> str:
        """Simulate blockchain event emission with cryptographic security"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'transaction_hash': self.security.hash_transaction(data),
            'signature': self.security.sign_data(data).hex(),
            'merkle_root': self.security.generate_merkle_root(self.transactions + [data])
        }
        self.events.append(event)
        return event['transaction_hash']

class BlockchainIntegration:
    def __init__(self, blockchain_url: Optional[str] = None):
        """Initialize blockchain integration with enhanced security"""
        self.logger = logging.getLogger('BlockchainIntegration')
        self.contract = SmartContract()
        self.security = CryptographicSecurity()
        
        # Initialize Web3 if URL is provided
        if blockchain_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(blockchain_url))
                if not self.web3.isConnected():
                    self.logger.warning("Failed to connect to blockchain network")
                    self.web3 = None
            except Exception as e:
                self.logger.error(f"Error connecting to blockchain: {str(e)}")
                self.web3 = None
        else:
            self.web3 = None

        # Enhanced caching with TTL
        self.transaction_cache = {}
        self.cache_ttl = 3600  # 1 hour TTL
        self.last_cache_cleanup = datetime.now()
        
        # Batch processing queue with retry mechanism
        self.transaction_queue = []
        self.failed_transactions = []
        self.batch_size = 10
        self.batch_timeout = 60  # seconds
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        self._setup_encryption()
        self._start_retry_worker()

    def _setup_encryption(self):
        """Setup encryption for sensitive data"""
        self.encryption_key = self.security.derive_key(
            "supply_chain_secret",  # In production, use secure key management
            self.security.generate_salt()
        )

    def _encrypt_sensitive_data(self, data: Dict) -> Dict:
        """Encrypt sensitive data in the transaction"""
        encrypted_data = {}
        for key, value in data.items():
            if isinstance(value, str) and any(sensitive in key.lower() for sensitive in ['password', 'key', 'secret', 'token']):
                ciphertext, iv = self.security.encrypt_data(value, self.encryption_key)
                encrypted_data[key] = {
                    'encrypted': True,
                    'ciphertext': base64.b64encode(ciphertext).decode(),
                    'iv': base64.b64encode(iv).decode()
                }
            else:
                encrypted_data[key] = value
        return encrypted_data

    def _decrypt_sensitive_data(self, data: Dict) -> Dict:
        """Decrypt sensitive data in the transaction"""
        decrypted_data = {}
        for key, value in data.items():
            if isinstance(value, dict) and value.get('encrypted'):
                ciphertext = base64.b64decode(value['ciphertext'])
                iv = base64.b64decode(value['iv'])
                decrypted_data[key] = self.security.decrypt_data(ciphertext, iv, self.encryption_key)
            else:
                decrypted_data[key] = value
        return decrypted_data

    def _cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        if (current_time - self.last_cache_cleanup).seconds > self.cache_ttl:
            expired_keys = [
                k for k, v in self.transaction_cache.items()
                if (current_time - v['timestamp']).seconds > self.cache_ttl
            ]
            for k in expired_keys:
                del self.transaction_cache[k]
            self.last_cache_cleanup = current_time

    def _start_retry_worker(self):
        """Start background thread for retrying failed transactions"""
        def retry_worker():
            while True:
                if self.failed_transactions:
                    retry_batch = self.failed_transactions[:self.batch_size]
                    self.failed_transactions = self.failed_transactions[self.batch_size:]
                    
                    for tx in retry_batch:
                        if tx['retries'] < self.max_retries:
                            try:
                                self._create_transaction(tx['data'])
                                self.logger.info(f"Successfully retried transaction: {tx['data'].get('transaction_hash')}")
                            except Exception as e:
                                self.logger.error(f"Retry failed for transaction: {str(e)}")
                                tx['retries'] += 1
                                self.failed_transactions.append(tx)
                        else:
                            self.logger.error(f"Transaction failed after {self.max_retries} retries: {tx['data'].get('transaction_hash')}")
                
                threading.Event().wait(self.retry_delay)
                
        thread = threading.Thread(target=retry_worker, daemon=True)
        thread.start()

    def _process_batch_transactions(self):
        """Process queued transactions in batch with improved error handling"""
        if not self.transaction_queue:
            return
            
        try:
            batch_data = self.transaction_queue[:self.batch_size]
            self.transaction_queue = self.transaction_queue[self.batch_size:]
            
            # Process batch
            for data in batch_data:
                try:
                    self._create_transaction(data)
                except Exception as e:
                    self.logger.error(f"Transaction failed: {str(e)}")
                    self.failed_transactions.append({
                        'data': data,
                        'retries': 0,
                        'last_error': str(e)
                    })
                
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            # Add failed transactions to retry queue
            for data in batch_data:
                self.failed_transactions.append({
                    'data': data,
                    'retries': 0,
                    'last_error': str(e)
                })

    def _create_transaction(self, data: Dict) -> str:
        """Create a blockchain transaction with cryptographic security and improved error handling"""
        try:
            # Generate transaction hash
            transaction_hash = self.security.hash_transaction(data)
            
            # Sign the transaction
            signature = self.security.sign_data(data)
            
            # Add cryptographic metadata
            data['transaction_hash'] = transaction_hash
            data['signature'] = signature.hex()
            data['merkle_root'] = self.security.generate_merkle_root(
                list(self.transaction_cache.values()) + [data]
            )

            if self.web3 and self.web3.isConnected():
                try:
                    # Here we would interact with the actual blockchain
                    self.contract.emit_event(data['type'], data)
                except Exception as e:
                    self.logger.error(f"Blockchain interaction failed: {str(e)}")
                    raise
            else:
                # Fallback to local storage with encryption
                self.transaction_cache[transaction_hash] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                # Clean up expired cache entries
                self._cleanup_expired_cache()

            self.logger.info(f"Created transaction: {transaction_hash}")
            return transaction_hash

        except Exception as e:
            self.logger.error(f"Transaction creation failed: {str(e)}")
            raise

    def get_transaction_status(self, transaction_hash: str) -> Dict:
        """Get detailed status of a transaction including retry attempts"""
        status = {
            'hash': transaction_hash,
            'status': 'unknown',
            'retries': 0,
            'last_error': None
        }
        
        # Check in transaction cache
        if transaction_hash in self.transaction_cache:
            status['status'] = 'completed'
            return status
            
        # Check in failed transactions
        for tx in self.failed_transactions:
            if tx['data'].get('transaction_hash') == transaction_hash:
                status['status'] = 'failed'
                status['retries'] = tx['retries']
                status['last_error'] = tx['last_error']
                return status
                
        # Check in current queue
        for tx in self.transaction_queue:
            if tx.get('transaction_hash') == transaction_hash:
                status['status'] = 'pending'
                return status
                
        return status

    def record_sensor_data(self, sensor_id: str, data: Dict) -> str:
        """Record sensor data on the blockchain with encryption"""
        try:
            transaction_data = {
                'type': 'sensor_reading',
                'sensor_id': sensor_id,
                'data': self._encrypt_sensitive_data(data),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to batch queue
            self.transaction_queue.append(transaction_data)
            
            # Process batch if size threshold reached
            if len(self.transaction_queue) >= self.batch_size:
                self._process_batch_transactions()
                
            return self.security.hash_transaction(transaction_data)
            
        except Exception as e:
            self.logger.error(f"Error recording sensor data: {str(e)}")
            raise

    def record_ripeness_analysis(self, crate_id: str, analysis_result: Dict) -> str:
        """Record fruit ripeness analysis results with encryption"""
        try:
            transaction_data = {
                'type': 'ripeness_analysis',
                'crate_id': crate_id,
                'analysis': self._encrypt_sensitive_data(analysis_result),
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error recording ripeness analysis: {str(e)}")
            raise

    def create_shipment_record(self, shipment_data: Dict) -> str:
        """Create a new shipment record with encryption"""
        try:
            transaction_data = {
                'type': 'shipment_creation',
                'shipment_data': self._encrypt_sensitive_data(shipment_data),
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error creating shipment record: {str(e)}")
            raise

    def update_shipment_status(self, 
                             shipment_id: str, 
                             status: str, 
                             location: Optional[Dict] = None) -> str:
        """Update shipment status with encryption"""
        try:
            transaction_data = {
                'type': 'shipment_update',
                'shipment_id': shipment_id,
                'status': status,
                'location': self._encrypt_sensitive_data(location) if location else None,
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error updating shipment status: {str(e)}")
            raise

    def record_quality_check(self, shipment_id: str, quality_data: Dict) -> str:
        """Record quality check results with encryption"""
        try:
            transaction_data = {
                'type': 'quality_check',
                'shipment_id': shipment_id,
                'quality_data': self._encrypt_sensitive_data(quality_data),
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error recording quality check: {str(e)}")
            raise

    def verify_transaction(self, transaction_hash: str) -> Dict:
        """Verify a transaction on the blockchain with cryptographic verification"""
        try:
            if transaction_hash in self.transaction_cache:
                transaction_data = self.transaction_cache[transaction_hash]
                decrypted_data = self._decrypt_sensitive_data(transaction_data)
                
                # Verify signature
                signature = bytes.fromhex(transaction_data['signature'])
                is_valid = self.security.verify_signature(decrypted_data, signature)
                
                # Verify Merkle root
                merkle_root_valid = (
                    transaction_data['merkle_root'] == 
                    self.security.generate_merkle_root(list(self.transaction_cache.values()))
                )
                
                return {
                    'verified': is_valid and merkle_root_valid,
                    'data': decrypted_data,
                    'signature_valid': is_valid,
                    'merkle_root_valid': merkle_root_valid
                }
            return {'verified': False}
        except Exception as e:
            self.logger.error(f"Transaction verification failed: {str(e)}")
            raise

    def get_shipment_history(self, shipment_id: str) -> List[Dict]:
        """Get complete history of a shipment with decryption"""
        try:
            history = []
            for tx_hash, tx_data in self.transaction_cache.items():
                data = tx_data
                if (('shipment_id' in data and data['shipment_id'] == shipment_id) or
                    ('shipment_data' in data and data['shipment_data'].get('shipment_id') == shipment_id)):
                    decrypted_data = self._decrypt_sensitive_data(data)
                    history.append({
                        'transaction_hash': tx_hash,
                        **decrypted_data
                    })
            
            return sorted(history, key=lambda x: x['timestamp'])
        except Exception as e:
            self.logger.error(f"Error retrieving shipment history: {str(e)}")
            raise

    def get_crate_history(self, crate_id: str) -> List[Dict]:
        """Get complete history of a crate with decryption"""
        try:
            history = []
            for tx_hash, tx_data in self.transaction_cache.items():
                data = tx_data
                if ('crate_id' in data and data['crate_id'] == crate_id):
                    decrypted_data = self._decrypt_sensitive_data(data)
                    history.append({
                        'transaction_hash': tx_hash,
                        **decrypted_data
                    })
            
            return sorted(history, key=lambda x: x['timestamp'])
        except Exception as e:
            self.logger.error(f"Error retrieving crate history: {str(e)}")
            raise

    def generate_supply_chain_report(self, 
                                   shipment_id: Optional[str] = None,
                                   crate_id: Optional[str] = None,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> Dict:
        """Generate a comprehensive supply chain report with decryption"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'transactions': []
            }

            for tx_hash, tx_data in self.transaction_cache.items():
                data = tx_data
                timestamp = data['timestamp']

                # Apply filters
                if start_date and timestamp < start_date:
                    continue
                if end_date and timestamp > end_date:
                    continue
                if shipment_id and not (
                    ('shipment_id' in data and data['shipment_id'] == shipment_id) or
                    ('shipment_data' in data and data['shipment_data'].get('shipment_id') == shipment_id)
                ):
                    continue
                if crate_id and ('crate_id' not in data or data['crate_id'] != crate_id):
                    continue

                decrypted_data = self._decrypt_sensitive_data(data)
                report['transactions'].append({
                    'transaction_hash': tx_hash,
                    **decrypted_data
                })

            report['transactions'].sort(key=lambda x: x['timestamp'])
            report['total_transactions'] = len(report['transactions'])
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating supply chain report: {str(e)}")
            raise

    def get_blockchain_status(self) -> Dict:
        """Get current blockchain connection status"""
        return {
            'connected': bool(self.web3 and self.web3.isConnected()),
            'contract_address': self.contract.contract_address,
            'total_transactions': len(self.transaction_cache),
            'total_events': len(self.contract.events),
            'public_key': self.security.export_public_key()
        }