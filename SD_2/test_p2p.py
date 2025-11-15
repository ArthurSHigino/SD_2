#!/usr/bin/env python3
import os
import time
import subprocess
import threading

def create_test_file(filename, size_kb):
    """Cria arquivo de teste com tamanho específico"""
    with open(filename, 'wb') as f:
        data = b'A' * (size_kb * 1024)
        f.write(data)
    print(f"Arquivo de teste {filename} criado ({size_kb}KB)")

def run_peer(port, neighbors="", commands=[]):
    """Executa um peer em processo separado"""
    cmd = ['python3', 'p2p_file_transfer.py', '--port', str(port)]
    if neighbors:
        cmd.extend(['--neighbors', neighbors])
    
    print(f"Iniciando peer na porta {port}")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, text=True)
    
    # Envia comandos se fornecidos
    if commands:
        time.sleep(2)  # Aguarda inicialização
        for command in commands:
            process.stdin.write(command + '\n')
            process.stdin.flush()
            time.sleep(1)
    
    return process

def test_basic_transfer():
    """Teste básico com 2 peers"""
    print("=== TESTE BÁSICO: 2 PEERS ===")
    
    # Cria arquivo de teste
    create_test_file('test_file.txt', 10)  # 10KB
    
    # Peer 1 (seeder) - porta 8080
    peer1_commands = [
        'load test_file.txt',
        'status'
    ]
    
    # Peer 2 (leecher) - porta 8081
    peer2_commands = [
        'download test_file.txt downloaded_file.txt',
        'status'
    ]
    
    print("\nIniciando peers...")
    print("Peer 1 (seeder) na porta 8080")
    print("Peer 2 (leecher) na porta 8081")
    print("\nPara testar manualmente:")
    print("Terminal 1: python3 p2p_file_transfer.py --port 8080")
    print("Terminal 2: python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080")
    print("\nNo Terminal 1: load test_file.txt")
    print("No Terminal 2: download test_file.txt")

def test_multiple_peers():
    """Teste com 4 peers"""
    print("\n=== TESTE AVANÇADO: 4 PEERS ===")
    
    create_test_file('large_file.txt', 100)  # 100KB
    
    print("Configuração de 4 peers:")
    print("Peer 1 (porta 8080) - seeder inicial")
    print("Peer 2 (porta 8081) - conecta ao peer 1")
    print("Peer 3 (porta 8082) - conecta aos peers 1 e 2") 
    print("Peer 4 (porta 8083) - conecta a todos")
    
    print("\nComandos para teste manual:")
    print("Terminal 1: python3 p2p_file_transfer.py --port 8080")
    print("Terminal 2: python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080")
    print("Terminal 3: python3 p2p_file_transfer.py --port 8082 --neighbors 127.0.0.1:8080,127.0.0.1:8081")
    print("Terminal 4: python3 p2p_file_transfer.py --port 8083 --neighbors 127.0.0.1:8080,127.0.0.1:8081,127.0.0.1:8082")

if __name__ == '__main__':
    print("SISTEMA P2P DE TRANSFERÊNCIA DE ARQUIVOS - TESTES")
    print("=" * 50)
    
    test_basic_transfer()
    test_multiple_peers()
    
    print("\n" + "=" * 50)
    print("INSTRUÇÕES DE USO:")
    print("1. Execute cada peer em um terminal separado")
    print("2. No peer que tem o arquivo: 'load nome_arquivo'")
    print("3. Nos outros peers: 'download nome_arquivo'")
    print("4. Use 'status' para verificar progresso")
    print("5. Use 'quit' para sair")
