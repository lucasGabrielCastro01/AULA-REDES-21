# Jogo 21 (Blackjack) - Implementação UDP

Projeto do jogo "21" (Blackjack) usando comunicação UDP entre cliente e servidor, desenvolvido para a disciplina de Redes de Computadores.

## Descrição

O sistema tem três partes:
- Servidor UDP: controla o jogo, distribui cartas, calcula pontos e decide o vencedor.
- Cliente UDP: terminal para o jogador interagir.
- Interface Web: interface gráfica opcional para demonstração.

## Funcionalidades

- Servidor gerencia múltiplos jogadores via UDP.
- Sorteio de cartas, controle de pontuação.
- Avaliação de vitória, derrota e empate.
- Comandos: PEDIR_CARTA, PARAR.
- Registro em log das partidas.
- Verificação de conexão (keepAlive).
- Interface Web simples (bônus).

## Tecnologias

- Python 3.x
- UDP
- HTML, CSS, JavaScript
- Bibliotecas: socket, threading, random, time, json, datetime

## Estrutura do projeto

```
projeto_21/
├── server/
│   └── server.py
├── client/
│   └── client.py
├── web_interface/
│   └── index.html
├── README.md
└── log_partidas.txt
```

## Como executar

1. Rodar servidor:

```bash
cd server
python3 server.py
```

2. Rodar cliente:

```bash
cd client
python3 client.py
```

- Informe IP do servidor (Enter para localhost)
- Informe porta (Enter para 12345)
- Digite seu nome
- Comandos:
  1 - Pedir carta
  2 - Parar
  3 - Ver status
  4 - Sair

3. Abrir `web_interface/index.html` no navegador para interface web.

## Protocolo de comunicação

- Cliente → Servidor:
  - ENTRAR:<nome>
  - PEDIR_CARTA
  - PARAR
  - KEEPALIVE

- Servidor → Cliente:
  - CARTA:<valor>
  - RESULTADO:<GANHOU|PERDEU|EMPATE>
  - MENSAGEM:<texto>
  - KEEPALIVE_ACK

## Regras do jogo

- Cada jogador começa com 2 cartas.
- Objetivo: chegar próximo de 21 sem passar.
- Valores: Números valem seu número; J, Q, K valem 10; Ás vale 1 ou 11.
- Pode pedir cartas ou parar.
- Passar de 21 = perde.
- Ganha quem tiver maior pontuação até 21.

## Testes realizados

- Partidas com 2 ou mais jogadores.
- Execução simultânea de vários clientes.
- Verificação de desconexão via keepAlive.

## Autores

Lucas Castro, Rodrigo Goulart e Samuel Faleiro.
