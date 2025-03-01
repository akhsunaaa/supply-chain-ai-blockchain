# integration.py
from web3 import Web3
from datetime import datetime
import json
import hashlib
from typing import Dict, List, Optional
import logging

class SmartContract:
    """
    Simulated smart contract for supply chain operations.
    In production, this would interact with actual blockchain smart contracts.
    """
    def __init__(self):
        self.transactions = []
        self.events = []
        self.contract_address = "0x0000000000000000000000000000000000000000"  # Placeholder
        
    def emit_event(self, event_type: str, data: Dict) -> str:
        """Simulate blockchain event emission"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'transaction_hash': self._generate_hash(data)
        }
        self.events.append(event)
        return event['transaction_hash']

    def _generate_hash(self, data: Dict) -> str:
        """Generate a hash for transaction data"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

class BlockchainIntegration:
    def __init__(self, blockchain_url: Optional[str] = None):
        """Initialize blockchain integration"""
        self.logger = logging.getLogger('BlockchainIntegration')
        self.contract = SmartContract()
        
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

        # Cache for transaction data
        self.transaction_cache = {}

    def record_sensor_data(self, sensor_id: str, data: Dict) -> str:
        """Record sensor data on the blockchain"""
        try:
            transaction_data = {
                'type': 'sensor_reading',
                'sensor_id': sensor_id,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error recording sensor data: {str(e)}")
            raise

    def record_ripeness_analysis(self, crate_id: str, analysis_result: Dict) -> str:
        """Record fruit ripeness analysis results"""
        try:
            transaction_data = {
                'type': 'ripeness_analysis',
                'crate_id': crate_id,
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error recording ripeness analysis: {str(e)}")
            raise

    def create_shipment_record(self, shipment_data: Dict) -> str:
        """Create a new shipment record"""
        try:
            transaction_data = {
                'type': 'shipment_creation',
                'shipment_data': shipment_data,
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
        """Update shipment status"""
        try:
            transaction_data = {
                'type': 'shipment_update',
                'shipment_id': shipment_id,
                'status': status,
                'location': location,
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error updating shipment status: {str(e)}")
            raise

    def record_quality_check(self, shipment_id: str, quality_data: Dict) -> str:
        """Record quality check results"""
        try:
            transaction_data = {
                'type': 'quality_check',
                'shipment_id': shipment_id,
                'quality_data': quality_data,
                'timestamp': datetime.now().isoformat()
            }
            return self._create_transaction(transaction_data)
        except Exception as e:
            self.logger.error(f"Error recording quality check: {str(e)}")
            raise

    def _create_transaction(self, data: Dict) -> str:
        """Create a blockchain transaction"""
        try:
            if self.web3 and self.web3.isConnected():
                # Here we would interact with the actual blockchain
                transaction_hash = self.contract.emit_event(data['type'], data)
            else:
                # Fallback to local hash generation for demonstration
                transaction_hash = self.contract._generate_hash(data)

            # Cache the transaction data
            self.transaction_cache[transaction_hash] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

            self.logger.info(f"Created transaction: {transaction_hash}")
            return transaction_hash

        except Exception as e:
            self.logger.error(f"Transaction creation failed: {str(e)}")
            raise

    def verify_transaction(self, transaction_hash: str) -> Dict:
        """Verify a transaction on the blockchain"""
        try:
            if transaction_hash in self.transaction_cache:
                return {
                    'verified': True,
                    'data': self.transaction_cache[transaction_hash]
                }
            return {'verified': False}
        except Exception as e:
            self.logger.error(f"Transaction verification failed: {str(e)}")
            raise

    def get_shipment_history(self, shipment_id: str) -> List[Dict]:
        """Get complete history of a shipment"""
        try:
            history = []
            for tx_hash, tx_data in self.transaction_cache.items():
                data = tx_data['data']
                if (('shipment_id' in data and data['shipment_id'] == shipment_id) or
                    ('shipment_data' in data and data['shipment_data'].get('shipment_id') == shipment_id)):
                    history.append({
                        'transaction_hash': tx_hash,
                        **tx_data
                    })
            
            return sorted(history, key=lambda x: x['timestamp'])
        except Exception as e:
            self.logger.error(f"Error retrieving shipment history: {str(e)}")
            raise

    def get_crate_history(self, crate_id: str) -> List[Dict]:
        """Get complete history of a crate"""
        try:
            history = []
            for tx_hash, tx_data in self.transaction_cache.items():
                data = tx_data['data']
                if ('crate_id' in data and data['crate_id'] == crate_id):
                    history.append({
                        'transaction_hash': tx_hash,
                        **tx_data
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
        """Generate a comprehensive supply chain report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'transactions': []
            }

            for tx_hash, tx_data in self.transaction_cache.items():
                data = tx_data['data']
                timestamp = tx_data['timestamp']

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

                report['transactions'].append({
                    'transaction_hash': tx_hash,
                    **tx_data
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
            'total_events': len(self.contract.events)
        }
