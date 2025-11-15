#!/usr/bin/env python3
import hashlib
import os

def test_file_integrity():
    print("=== TESTE DE INTEGRIDADE ===")
    
    # Cria arquivo binário de teste
    test_data = b"P2P Test Data\n" * 100  # Dados binários
    with open("integrity_test.bin", "wb") as f:
        f.write(test_data)
    
    original_hash = hashlib.sha256(test_data).hexdigest()
    print(f"✓ Arquivo criado - Hash: {original_hash[:16]}...")
    
    # Testa fragmentação manual
    from p2p_file_transfer import P2PPeer
    
    peer = P2PPeer("127.0.0.1", 9999, [])
    peer.load_file("integrity_test.bin")
    
    # Verifica se foi fragmentado corretamente
    filename = "integrity_test.bin"
    if filename in peer.files:
        file_info = peer.files[filename]
        print(f"✓ Fragmentado em {file_info['total_blocks']} blocos")
        print(f"✓ Hash armazenado: {file_info['file_hash'][:16]}...")
        
        # Reconstrói arquivo
        reconstructed = b""
        for i in range(file_info['total_blocks']):
            reconstructed += file_info['blocks'][i]
        
        reconstructed_hash = hashlib.sha256(reconstructed).hexdigest()
        
        if original_hash == reconstructed_hash:
            print("✓ INTEGRIDADE VERIFICADA: Hash original == Hash reconstruído")
            return True
        else:
            print("✗ FALHA DE INTEGRIDADE")
            return False
    
    return False

if __name__ == "__main__":
    success = test_file_integrity()
    
    # Limpeza
    if os.path.exists("integrity_test.bin"):
        os.remove("integrity_test.bin")
    
    print(f"\nResultado: {'PASSOU' if success else 'FALHOU'}")
