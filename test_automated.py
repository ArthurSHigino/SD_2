#!/usr/bin/env python3
import subprocess
import time
import os
import signal

def test_p2p_system():
    print("=== TESTE AUTOMATIZADO DO SISTEMA P2P ===")
    
    # Cria arquivo de teste
    test_content = "Teste automatizado do sistema P2P\n" * 50  # ~1.5KB
    with open("auto_test.txt", "w") as f:
        f.write(test_content)
    print("✓ Arquivo de teste criado")
    
    # Inicia peer seeder
    peer1 = subprocess.Popen([
        "python3", "p2p_file_transfer.py", "--port", "9080"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    time.sleep(2)  # Aguarda inicialização
    
    # Carrega arquivo no peer1
    peer1.stdin.write("load auto_test.txt\n")
    peer1.stdin.flush()
    time.sleep(1)
    
    # Inicia peer leecher
    peer2 = subprocess.Popen([
        "python3", "p2p_file_transfer.py", "--port", "9081", "--neighbors", "127.0.0.1:9080"
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    time.sleep(2)
    
    # Baixa arquivo no peer2
    peer2.stdin.write("download auto_test.txt downloaded_auto_test.txt\n")
    peer2.stdin.flush()
    time.sleep(3)
    
    # Finaliza peers
    peer1.stdin.write("quit\n")
    peer2.stdin.write("quit\n")
    peer1.stdin.flush()
    peer2.stdin.flush()
    
    time.sleep(2)
    
    # Mata processos se ainda estiverem rodando
    try:
        peer1.terminate()
        peer2.terminate()
    except:
        pass
    
    # Verifica se arquivo foi transferido corretamente
    if os.path.exists("downloaded_auto_test.txt"):
        with open("auto_test.txt", "r") as f1, open("downloaded_auto_test.txt", "r") as f2:
            original = f1.read()
            downloaded = f2.read()
            
        if original == downloaded:
            print("✓ TESTE PASSOU: Arquivo transferido corretamente!")
            print(f"✓ Tamanho original: {len(original)} bytes")
            print(f"✓ Tamanho baixado: {len(downloaded)} bytes")
            return True
        else:
            print("✗ TESTE FALHOU: Conteúdo diferente")
            return False
    else:
        print("✗ TESTE FALHOU: Arquivo não foi baixado")
        return False

if __name__ == "__main__":
    success = test_p2p_system()
    
    # Limpeza
    for f in ["auto_test.txt", "downloaded_auto_test.txt"]:
        if os.path.exists(f):
            os.remove(f)
    
    exit(0 if success else 1)
