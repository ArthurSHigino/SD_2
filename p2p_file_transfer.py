#!/usr/bin/env python3
import socket
import threading
import json
import hashlib
import os
import time
import argparse
from typing import Dict, List, Set

class P2PPeer:
    def __init__(self, ip: str, port: int, neighbors: List[str]):
        self.ip = ip
        self.port = port
        self.neighbors = neighbors
        self.block_size = 1024
        self.files = {}  # filename -> {blocks: {block_id: data}, total_blocks: int, file_hash: str}
        self.peer_blocks = {}  # peer_address -> set of block_ids they have
        self.server_socket = None
        self.running = False
        
    def start_server(self):
        """Inicia o servidor para escutar conexões de outros peers"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Peer iniciado em {self.ip}:{self.port}")
        
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
            except:
                break
                
    def handle_client(self, client_socket, addr):
        """Processa requisições de outros peers"""
        try:
            data = client_socket.recv(4096).decode()
            request = json.loads(data)
            
            if request['type'] == 'get_block':
                filename = request['filename']
                block_id = request['block_id']
                
                if filename in self.files and block_id in self.files[filename]['blocks']:
                    response = {
                        'status': 'success',
                        'block_data': self.files[filename]['blocks'][block_id].hex()
                    }
                else:
                    response = {'status': 'not_found'}
                    
                client_socket.send(json.dumps(response).encode())
                
            elif request['type'] == 'get_file_info':
                filename = request['filename']
                if filename in self.files:
                    response = {
                        'status': 'success',
                        'total_blocks': self.files[filename]['total_blocks'],
                        'file_hash': self.files[filename]['file_hash'],
                        'available_blocks': list(self.files[filename]['blocks'].keys())
                    }
                else:
                    response = {'status': 'not_found'}
                    
                client_socket.send(json.dumps(response).encode())
                
        except Exception as e:
            print(f"Erro ao processar cliente {addr}: {e}")
        finally:
            client_socket.close()
            
    def load_file(self, filepath: str):
        """Carrega um arquivo e o fragmenta em blocos"""
        filename = os.path.basename(filepath)
        
        with open(filepath, 'rb') as f:
            file_data = f.read()
            
        file_hash = hashlib.sha256(file_data).hexdigest()
        total_blocks = (len(file_data) + self.block_size - 1) // self.block_size
        
        blocks = {}
        for i in range(total_blocks):
            start = i * self.block_size
            end = min(start + self.block_size, len(file_data))
            blocks[i] = file_data[start:end]
            
        self.files[filename] = {
            'blocks': blocks,
            'total_blocks': total_blocks,
            'file_hash': file_hash
        }
        
        print(f"Arquivo {filename} carregado: {total_blocks} blocos, hash: {file_hash[:16]}...")
        
    def request_block(self, peer_addr: str, filename: str, block_id: int) -> bytes:
        """Solicita um bloco específico de um peer"""
        try:
            ip, port = peer_addr.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, int(port)))
            
            request = {
                'type': 'get_block',
                'filename': filename,
                'block_id': block_id
            }
            
            sock.send(json.dumps(request).encode())
            response_data = sock.recv(4096).decode()
            response = json.loads(response_data)
            
            sock.close()
            
            if response['status'] == 'success':
                return bytes.fromhex(response['block_data'])
            return None
            
        except Exception as e:
            print(f"Erro ao solicitar bloco {block_id} de {peer_addr}: {e}")
            return None
            
    def get_file_info(self, peer_addr: str, filename: str) -> Dict:
        """Obtém informações sobre um arquivo de um peer"""
        try:
            ip, port = peer_addr.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, int(port)))
            
            request = {
                'type': 'get_file_info',
                'filename': filename
            }
            
            sock.send(json.dumps(request).encode())
            response_data = sock.recv(4096).decode()
            response = json.loads(response_data)
            
            sock.close()
            return response
            
        except Exception as e:
            print(f"Erro ao obter info do arquivo de {peer_addr}: {e}")
            return {'status': 'error'}
            
    def download_file(self, filename: str, output_path: str = None):
        """Baixa um arquivo dos peers vizinhos"""
        if output_path is None:
            output_path = filename
            
        # Descobre informações do arquivo nos peers
        file_info = None
        peer_blocks_map = {}
        
        for peer in self.neighbors:
            info = self.get_file_info(peer, filename)
            if info['status'] == 'success':
                if file_info is None:
                    file_info = info
                peer_blocks_map[peer] = set(info['available_blocks'])
                
        if file_info is None:
            print(f"Arquivo {filename} não encontrado nos peers")
            return False
            
        total_blocks = file_info['total_blocks']
        target_hash = file_info['file_hash']
        
        # Inicializa estrutura local do arquivo
        if filename not in self.files:
            self.files[filename] = {
                'blocks': {},
                'total_blocks': total_blocks,
                'file_hash': target_hash
            }
            
        # Baixa blocos faltantes
        missing_blocks = set(range(total_blocks)) - set(self.files[filename]['blocks'].keys())
        
        print(f"Baixando {len(missing_blocks)} blocos de {filename}...")
        
        for block_id in missing_blocks:
            # Encontra peer que tem o bloco
            for peer, available_blocks in peer_blocks_map.items():
                if block_id in available_blocks:
                    block_data = self.request_block(peer, filename, block_id)
                    if block_data:
                        self.files[filename]['blocks'][block_id] = block_data
                        print(f"Bloco {block_id} baixado de {peer}")
                        break
                        
        # Verifica se download está completo
        if len(self.files[filename]['blocks']) == total_blocks:
            self.save_file(filename, output_path)
            return True
        else:
            print(f"Download incompleto: {len(self.files[filename]['blocks'])}/{total_blocks} blocos")
            return False
            
    def save_file(self, filename: str, output_path: str):
        """Reconstrói e salva o arquivo completo"""
        if filename not in self.files:
            print(f"Arquivo {filename} não encontrado")
            return False
            
        file_info = self.files[filename]
        
        # Reconstrói o arquivo
        file_data = b''
        for i in range(file_info['total_blocks']):
            if i in file_info['blocks']:
                file_data += file_info['blocks'][i]
            else:
                print(f"Bloco {i} faltando")
                return False
                
        # Verifica integridade
        calculated_hash = hashlib.sha256(file_data).hexdigest()
        if calculated_hash != file_info['file_hash']:
            print(f"Erro de integridade: hash esperado {file_info['file_hash']}, calculado {calculated_hash}")
            return False
            
        # Salva arquivo
        with open(output_path, 'wb') as f:
            f.write(file_data)
            
        print(f"Arquivo {filename} salvo em {output_path} (hash verificado)")
        return True
        
    def stop(self):
        """Para o servidor"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

def main():
    parser = argparse.ArgumentParser(description='Sistema P2P de Transferência de Arquivos')
    parser.add_argument('--ip', default='127.0.0.1', help='IP do peer')
    parser.add_argument('--port', type=int, required=True, help='Porta do peer')
    parser.add_argument('--neighbors', default='', help='Lista de peers vizinhos (ip:porta,ip:porta)')
    
    args = parser.parse_args()
    
    neighbors = []
    if args.neighbors:
        neighbors = args.neighbors.split(',')
        
    peer = P2PPeer(args.ip, args.port, neighbors)
    
    # Inicia servidor em thread separada
    server_thread = threading.Thread(target=peer.start_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("\nComandos disponíveis:")
    print("load <arquivo> - Carrega arquivo para compartilhar")
    print("download <nome_arquivo> [saida] - Baixa arquivo dos peers")
    print("status - Mostra status dos arquivos")
    print("quit - Sair")
    
    try:
        while True:
            cmd = input("\n> ").strip().split()
            
            if not cmd:
                continue
                
            if cmd[0] == 'load' and len(cmd) > 1:
                peer.load_file(cmd[1])
                
            elif cmd[0] == 'download' and len(cmd) > 1:
                output = cmd[2] if len(cmd) > 2 else None
                peer.download_file(cmd[1], output)
                
            elif cmd[0] == 'status':
                for filename, info in peer.files.items():
                    blocks_count = len(info['blocks'])
                    total = info['total_blocks']
                    print(f"{filename}: {blocks_count}/{total} blocos")
                    
            elif cmd[0] == 'quit':
                break
                
            else:
                print("Comando inválido")
                
    except KeyboardInterrupt:
        pass
    finally:
        peer.stop()
        print("\nPeer finalizado")

if __name__ == '__main__':
    main()
