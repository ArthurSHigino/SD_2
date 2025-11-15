# Sistema P2P de Transferência de Arquivos

## Visão Geral
Sistema elementar de transferência de arquivos usando modelo Peer-to-Peer (P2P) onde cada peer atua simultaneamente como cliente e servidor.

## Características Implementadas

### Arquitetura P2P Simétrica
- Cada peer escuta em uma porta específica (servidor)
- Cada peer pode solicitar blocos de outros peers (cliente)
- Suporte a múltiplos peers simultâneos

### Fragmentação de Arquivos
- Arquivos divididos em blocos de 1024 bytes
- Registro local dos blocos possuídos
- Verificação de integridade com SHA-256

### Protocolo de Comunicação
- Comunicação via sockets TCP
- Serialização JSON para mensagens
- Suporte a concorrência com threads

## Instalação e Execução

### Pré-requisitos
- Python 3.6+
- Rede local ou localhost para testes

### Execução Básica

#### Peer Seeder (tem o arquivo):
```bash
python3 p2p_file_transfer.py --port 8080
```

#### Peer Leecher (quer baixar):
```bash
python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080
```

### Parâmetros de Linha de Comando
- `--ip`: IP do peer (padrão: 127.0.0.1)
- `--port`: Porta do peer (obrigatório)
- `--neighbors`: Lista de peers vizinhos (formato: ip:porta,ip:porta)

## Comandos Interativos

### `load <arquivo>`
Carrega um arquivo local e o fragmenta para compartilhamento.
```
> load exemplo.txt
Arquivo exemplo.txt carregado: 15 blocos, hash: a1b2c3d4...
```

### `download <nome_arquivo> [arquivo_saida]`
Baixa um arquivo dos peers vizinhos.
```
> download exemplo.txt minha_copia.txt
Baixando 15 blocos de exemplo.txt...
Bloco 0 baixado de 127.0.0.1:8080
...
Arquivo exemplo.txt salvo em minha_copia.txt (hash verificado)
```

### `status`
Mostra status dos arquivos locais.
```
> status
exemplo.txt: 15/15 blocos
outro_arquivo.pdf: 8/20 blocos
```

### `quit`
Finaliza o peer.

## Casos de Teste

### Teste 1: Transferência Básica (2 peers)
```bash
# Terminal 1 - Seeder
python3 p2p_file_transfer.py --port 8080
> load test_file.txt

# Terminal 2 - Leecher  
python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080
> download test_file.txt
```

### Teste 2: Rede com 4 Peers
```bash
# Terminal 1
python3 p2p_file_transfer.py --port 8080

# Terminal 2
python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080

# Terminal 3
python3 p2p_file_transfer.py --port 8082 --neighbors 127.0.0.1:8080,127.0.0.1:8081

# Terminal 4
python3 p2p_file_transfer.py --port 8083 --neighbors 127.0.0.1:8080,127.0.0.1:8081,127.0.0.1:8082
```

### Criação de Arquivos de Teste
```bash
# Arquivo pequeno (10KB)
python3 -c "with open('small.txt', 'wb') as f: f.write(b'A' * 10240)"

# Arquivo médio (1MB)
python3 -c "with open('medium.txt', 'wb') as f: f.write(b'B' * 1048576)"

# Arquivo grande (10MB)
python3 -c "with open('large.txt', 'wb') as f: f.write(b'C' * 10485760)"
```

## Protocolo de Comunicação

### Mensagens Suportadas

#### Solicitar Bloco
```json
{
    "type": "get_block",
    "filename": "exemplo.txt",
    "block_id": 5
}
```

#### Resposta de Bloco
```json
{
    "status": "success",
    "block_data": "41414141..." // dados em hexadecimal
}
```

#### Solicitar Informações do Arquivo
```json
{
    "type": "get_file_info", 
    "filename": "exemplo.txt"
}
```

#### Resposta de Informações
```json
{
    "status": "success",
    "total_blocks": 15,
    "file_hash": "a1b2c3d4...",
    "available_blocks": [0, 1, 2, 5, 8, 12]
}
```

## Características de Segurança

### Verificação de Integridade
- Hash SHA-256 calculado para arquivo completo
- Verificação automática após download completo

### Timeouts de Rede
- Timeout de 5 segundos para conexões
- Prevenção de conexões pendentes

### Portas Seguras
- Uso de portas não privilegiadas (>1024)
- Configuração para localhost por padrão

## Limitações Conhecidas

1. **Descoberta de Peers**: Configuração estática de vizinhos
2. **Tolerância a Falhas**: Sem recuperação automática de conexões
3. **Otimização**: Sem algoritmo de seleção inteligente de peers
4. **Persistência**: Estado não é salvo entre execuções

## Arquitetura do Código

### Classe Principal: `P2PPeer`
- `start_server()`: Inicia servidor TCP
- `handle_client()`: Processa requisições
- `load_file()`: Fragmenta e carrega arquivo
- `download_file()`: Coordena download de peers
- `request_block()`: Solicita bloco específico
- `save_file()`: Reconstrói arquivo completo

### Estruturas de Dados
- `files`: Dicionário com arquivos e blocos locais
- `peer_blocks`: Mapeamento de blocos por peer
- `neighbors`: Lista de peers vizinhos configurados

## Exemplo de Execução Completa

```bash
# Preparação
echo "Conteúdo de teste para o sistema P2P" > arquivo_teste.txt

# Peer 1 (Seeder)
python3 p2p_file_transfer.py --port 8080
> load arquivo_teste.txt
Arquivo arquivo_teste.txt carregado: 1 blocos, hash: 7f8a9b2c...
> status
arquivo_teste.txt: 1/1 blocos

# Peer 2 (Leecher) - em outro terminal
python3 p2p_file_transfer.py --port 8081 --neighbors 127.0.0.1:8080
> download arquivo_teste.txt copia_arquivo.txt
Baixando 1 blocos de arquivo_teste.txt...
Bloco 0 baixado de 127.0.0.1:8080
Arquivo arquivo_teste.txt salvo em copia_arquivo.txt (hash verificado)
> status
arquivo_teste.txt: 1/1 blocos
```

## Troubleshooting

### Erro "Address already in use"
- Aguarde alguns segundos e tente novamente
- Use porta diferente com `--port`

### Erro "Connection refused"
- Verifique se o peer de destino está executando
- Confirme IP e porta na lista de neighbors

### Download incompleto
- Verifique se o peer seeder tem o arquivo completo
- Use comando `status` para verificar blocos disponíveis
