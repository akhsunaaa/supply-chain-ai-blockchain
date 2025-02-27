# integration.py
from web3 import Web3
from datetime import datetime
import json
from typing import Dict, List
import hashlib

class SupplyChainContract:
    """
    Smart contract interface for the supply chain management system.
    This is a placeholder for the actual smart contract implementation.
    """
    def __init__(self):
        self.events = []
        self.transactions = []

    def create_shipment(self, data: Dict) -> str:
        """Create a new shipment record on the blockchain"""
        # This would interact with the actual smart contract
        transaction_hash = self._generate_hash(data)
        return transaction_hash

    def update_shipment_status(self, shipment_id: str, status: str) -> str:
        """Update the status of an existing shipment"""
        # This would interact with the actual smart contract
        transaction_hash = self._generate_hash({
            'shipment_id': shipment_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        return transaction_hash

    def _generate_hash(self, data: Dict) -> str:
        """Generate a hash for the transaction data"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()

class BlockchainIntegration:
    def __init__(self, blockchain_url: str = None):
        """
        Initialize blockchain integration
        :param blockchain_url: URL of the blockchain network
        """
        self.contract = SupplyChainContract()
        if blockchain_url:
            self.web3 = Web3(Web3.HTTPProvider(blockchain_url))
        else:
            self.web3 = None
        self.transaction_cache = {}

    def record_sensor_data(self, 
                          sensor_id: str, 
                          data: Dict,
                          timestamp: str = None) -> str:
        """
        Record sensor data on the blockchain
        """
        if not timestamp:
            timestamp = datetime.now().isoformat()

        transaction_data = {
            'sensor_id': sensor_id,
            'data': data,
            'timestamp': timestamp,
            'type': 'sensor_reading'
        }

        return self._create_transaction(transaction_data)

    def record_ripeness_analysis(self, 
                               crate_id: str,
                               analysis_result: Dict) -> str:
        """
        Record fruit ripeness analysis results on the blockchain
        """
        transaction_data = {
            'crate_id': crate_id,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat(),
            'type': 'ripeness_analysis'
        }

        return self._create_transaction(transaction_data)

    def create_shipment_record(self, 
                             shipment_data: Dict) -> str:
        """
        Create a new shipment record on the blockchain
        """
        transaction_data = {
            **shipment_data,
            'timestamp': datetime.now().isoformat(),
            'type': 'shipment_creation'
        }

        return self._create_transaction(transaction_data)

    def update_shipment_status(self, 
                             shipment_id: str,
                             status: str,
                             location: Dict = None) -> str:
        """
        Update the status of a shipment on the blockchain
        """
        transaction_data = {
            'shipment_id': shipment_id,
            'status': status,
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'type': 'shipment_update'
        }

        return self._create_transaction(transaction_data)

    def record_quality_check(self, 
                           shipment_id: str,
                           quality_data: Dict) -> str:
        """
        Record quality check results on the blockchain
        """
        transaction_data = {
            'shipment_id': shipment_id,
            'quality_data': quality_data,
            'timestamp': datetime.now().isoformat(),
            'type': 'quality_check'
        }

        return self._create_transaction(transaction_data)

    def _create_transaction(self, data: Dict) -> str:
        """
        Create a transaction on the blockchain
        """
        try:
            if self.web3 and self.web3.isConnected():
                # Here we would interact with the actual blockchain
                transaction_hash = self.contract.create_shipment(data)
            else:
                # Fallback to local hash generation for demonstration
                transaction_hash = self.contract._generate_hash(data)

            # Cache the transaction data
            self.transaction_cache[transaction_hash] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

            return transaction_hash

        except Exception as e:
            raise Exception(f"Failed to create blockchain transaction: {str(e)}")

    def verify_transaction(self, transaction_hash: str) -> Dict:
        """
        Verify a transaction on the blockchain
        """
        if transaction_hash in self.transaction_cache:
            return {
                'verified': True,
                'data': self.transaction_cache[transaction_hash]
            }
        return {'verified': False}

    def get_shipment_history(self, shipment_id: str) -> List[Dict]:
        """
        Get the complete history of a shipment from the blockchain
        """
        history = []
        for tx_hash, tx_data in self.transaction_cache.items():
            data = tx_data['data']
            if ('shipment_id' in data and data['shipment_id'] == shipment_id):
                history.append({
                    'transaction_hash': tx_hash,
                    **tx_data
                })
        
        return sorted(history, key=lambda x: x['timestamp'])

    def get_crate_history(self, crate_id: str) -> List[Dict]:
        """
        Get the complete history of a crate from the blockchain
        """
        history = []
        for tx_hash, tx_data in self.transaction_cache.items():
            data = tx_data['data']
            if ('crate_id' in data and data['crate_id'] == crate_id):
                history.append({
                    'transaction_hash': tx_hash,
                    **tx_data
                })
        
        return sorted(history, key=lambda x: x['timestamp'])

    def generate_supply_chain_report(self, 
                                   shipment_id: str = None,
                                   crate_id: str = None,
                                   start_date: str = None,
                                   end_date: str = None) -> Dict:
        """
        Generate a comprehensive supply chain report
        """
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
            if shipment_id and ('shipment_id' not in data or data['shipment_id'] != shipment_id):
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
