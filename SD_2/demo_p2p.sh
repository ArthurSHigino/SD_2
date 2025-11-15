#!/bin/bash

echo "=== DEMONSTRAÇÃO SISTEMA P2P ==="
echo "Criando arquivo de demonstração..."

# Cria arquivo de teste
echo "Conteúdo de demonstração do sistema P2P de transferência de arquivos. Este texto será fragmentado em blocos e transferido entre peers." > demo_file.txt

echo "Arquivo demo_file.txt criado."
echo ""
echo "Para testar o sistema P2P:"
echo ""
echo "1. TERMINAL 1 (Peer Seeder):"
echo "   python3 p2p_file_transfer.py --port 8080"
echo "   > load demo_file.txt"
echo ""
echo "2. TERMINAL 2 (Peer Leecher):"
echo "   python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080"
echo "   > download demo_file.txt downloaded_demo.txt"
echo ""
echo "3. Verificar resultado:"
echo "   diff demo_file.txt downloaded_demo.txt"
echo ""
echo "ATENÇÃO: Execute em localhost (127.0.0.1) para segurança!"
