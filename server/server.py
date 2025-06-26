import socket
import threading
import random
import time
import json
from datetime import datetime

class Servidor21:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        
        # Estruturas de dados do jogo
        self.jogadores = {}  # {endereco: {'nome': str, 'cartas': [], 'pontuacao': int, 'parou': bool}}
        self.partida_ativa = False
        self.cartas_disponiveis = []
        self.log_partidas = []
        
        # Para keepalive
        self.ultimo_keepalive = {}
        
        print(f"Servidor iniciado em {self.host}:{self.port}")
        self.inicializar_baralho()
        
    def inicializar_baralho(self):
        """Inicializa um baralho completo de cartas"""
        naipes = ['♠', '♥', '♦', '♣']
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.cartas_disponiveis = []
        
        for naipe in naipes:
            for valor in valores:
                self.cartas_disponiveis.append(f"{valor}{naipe}")
        
        random.shuffle(self.cartas_disponiveis)
        
    def calcular_pontuacao(self, cartas):
        """Calcula a pontuação das cartas considerando Ás como 1 ou 11"""
        pontuacao = 0
        ases = 0
        
        for carta in cartas:
            valor = carta[:-1]  # Remove o naipe
            if valor in ['J', 'Q', 'K']:
                pontuacao += 10
            elif valor == 'A':
                ases += 1
                pontuacao += 11
            else:
                pontuacao += int(valor)
        
        # Ajusta os Ases se necessário
        while pontuacao > 21 and ases > 0:
            pontuacao -= 10
            ases -= 1
            
        return pontuacao
    
    def sortear_carta(self):
        """Sorteia uma carta do baralho"""
        if not self.cartas_disponiveis:
            self.inicializar_baralho()
        return self.cartas_disponiveis.pop()
    
    def enviar_mensagem(self, endereco, mensagem):
        """Envia uma mensagem para um cliente específico"""
        try:
            self.socket.sendto(mensagem.encode('utf-8'), endereco)
            self.log_evento(f"Enviado para {endereco}: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {endereco}: {e}")
    
    def broadcast_mensagem(self, mensagem, excluir=None):
        """Envia uma mensagem para todos os jogadores conectados"""
        for endereco in self.jogadores:
            if endereco != excluir:
                self.enviar_mensagem(endereco, mensagem)
    
    def log_evento(self, evento):
        """Registra eventos no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {evento}"
        print(log_entry)
        self.log_partidas.append(log_entry)
    
    def processar_entrada_jogador(self, endereco, nome):
        """Processa a entrada de um novo jogador"""
        if endereco in self.jogadores:
            self.enviar_mensagem(endereco, "MENSAGEM:Você já está no jogo!")
            return
        
        self.jogadores[endereco] = {
            'nome': nome,
            'cartas': [],
            'pontuacao': 0,
            'parou': False
        }
        
        self.ultimo_keepalive[endereco] = time.time()
        
        self.log_evento(f"Jogador {nome} ({endereco}) entrou no jogo")
        self.enviar_mensagem(endereco, f"MENSAGEM:Bem-vindo ao jogo, {nome}!")
        
        # Verifica se pode iniciar o jogo
        if len(self.jogadores) >= 2 and not self.partida_ativa:
            self.iniciar_partida()
    
    def iniciar_partida(self):
        """Inicia uma nova partida"""
        self.partida_ativa = True
        self.log_evento("Nova partida iniciada")
        
        # Distribui duas cartas iniciais para cada jogador
        for endereco in self.jogadores:
            jogador = self.jogadores[endereco]
            jogador['cartas'] = []
            jogador['pontuacao'] = 0
            jogador['parou'] = False
            
            # Primeira carta
            carta1 = self.sortear_carta()
            jogador['cartas'].append(carta1)
            
            # Segunda carta
            carta2 = self.sortear_carta()
            jogador['cartas'].append(carta2)
            
            jogador['pontuacao'] = self.calcular_pontuacao(jogador['cartas'])
            
            self.enviar_mensagem(endereco, f"CARTA:{carta1}")
            self.enviar_mensagem(endereco, f"CARTA:{carta2}")
            self.enviar_mensagem(endereco, f"MENSAGEM:Suas cartas: {', '.join(jogador['cartas'])} | Pontuação: {jogador['pontuacao']}")
            
            if jogador['pontuacao'] == 21:
                self.enviar_mensagem(endereco, "MENSAGEM:Blackjack! Você tem 21!")
                jogador['parou'] = True
        
        self.broadcast_mensagem("MENSAGEM:Partida iniciada! Digite 'PEDIR_CARTA' para pedir uma carta ou 'PARAR' para finalizar sua jogada.")
    
    def processar_pedir_carta(self, endereco):
        """Processa o pedido de carta de um jogador"""
        if endereco not in self.jogadores:
            self.enviar_mensagem(endereco, "MENSAGEM:Você não está no jogo!")
            return
        
        jogador = self.jogadores[endereco]
        
        if jogador['parou']:
            self.enviar_mensagem(endereco, "MENSAGEM:Você já parou!")
            return
        
        if jogador['pontuacao'] >= 21:
            self.enviar_mensagem(endereco, "MENSAGEM:Você já ultrapassou 21 ou tem 21!")
            return
        
        # Sorteia uma nova carta
        nova_carta = self.sortear_carta()
        jogador['cartas'].append(nova_carta)
        jogador['pontuacao'] = self.calcular_pontuacao(jogador['cartas'])
        
        self.enviar_mensagem(endereco, f"CARTA:{nova_carta}")
        self.enviar_mensagem(endereco, f"MENSAGEM:Suas cartas: {', '.join(jogador['cartas'])} | Pontuação: {jogador['pontuacao']}")
        
        if jogador['pontuacao'] > 21:
            self.enviar_mensagem(endereco, "MENSAGEM:Você estourou! Pontuação acima de 21.")
            jogador['parou'] = True
        elif jogador['pontuacao'] == 21:
            self.enviar_mensagem(endereco, "MENSAGEM:Você tem 21! Sua jogada foi finalizada automaticamente.")
            jogador['parou'] = True
        
        self.verificar_fim_partida()
    
    def processar_parar(self, endereco):
        """Processa quando um jogador decide parar"""
        if endereco not in self.jogadores:
            self.enviar_mensagem(endereco, "MENSAGEM:Você não está no jogo!")
            return
        
        jogador = self.jogadores[endereco]
        jogador['parou'] = True
        
        self.enviar_mensagem(endereco, f"MENSAGEM:Você parou com {jogador['pontuacao']} pontos.")
        self.log_evento(f"Jogador {jogador['nome']} parou com {jogador['pontuacao']} pontos")
        
        self.verificar_fim_partida()
    
    def verificar_fim_partida(self):
        """Verifica se a partida terminou e calcula os resultados"""
        if not self.partida_ativa:
            return
        
        # Verifica se todos os jogadores pararam ou estouraram
        todos_pararam = all(jogador['parou'] for jogador in self.jogadores.values())
        
        if todos_pararam:
            self.finalizar_partida()
    
    def finalizar_partida(self):
        """Finaliza a partida e envia os resultados"""
        self.partida_ativa = False
        self.log_evento("Partida finalizada")
        
        # Calcula os resultados
        jogadores_validos = []
        for endereco, jogador in self.jogadores.items():
            if jogador['pontuacao'] <= 21:
                jogadores_validos.append((endereco, jogador))
        
        if not jogadores_validos:
            # Todos estouraram
            self.broadcast_mensagem("RESULTADO:EMPATE")
            self.broadcast_mensagem("MENSAGEM:Todos os jogadores estouraram! Empate!")
        else:
            # Encontra a maior pontuação válida
            maior_pontuacao = max(jogador['pontuacao'] for _, jogador in jogadores_validos)
            vencedores = [(endereco, jogador) for endereco, jogador in jogadores_validos 
                         if jogador['pontuacao'] == maior_pontuacao]
            
            if len(vencedores) == 1:
                # Um vencedor
                endereco_vencedor, jogador_vencedor = vencedores[0]
                self.enviar_mensagem(endereco_vencedor, "RESULTADO:GANHOU")
                
                for endereco in self.jogadores:
                    if endereco != endereco_vencedor:
                        self.enviar_mensagem(endereco, "RESULTADO:PERDEU")
                
                self.broadcast_mensagem(f"MENSAGEM:Vencedor: {jogador_vencedor['nome']} com {maior_pontuacao} pontos!")
            else:
                # Empate
                for endereco, _ in vencedores:
                    self.enviar_mensagem(endereco, "RESULTADO:EMPATE")
                
                for endereco in self.jogadores:
                    if endereco not in [end for end, _ in vencedores]:
                        self.enviar_mensagem(endereco, "RESULTADO:PERDEU")
                
                nomes_vencedores = [jogador['nome'] for _, jogador in vencedores]
                self.broadcast_mensagem(f"MENSAGEM:Empate entre: {', '.join(nomes_vencedores)} com {maior_pontuacao} pontos!")
        
        # Limpa os jogadores para uma nova partida
        self.jogadores.clear()
        self.ultimo_keepalive.clear()
        self.inicializar_baralho()
    
    def processar_keepalive(self, endereco):
        """Processa mensagem de keepalive"""
        self.ultimo_keepalive[endereco] = time.time()
        self.enviar_mensagem(endereco, "KEEPALIVE_ACK")
    
    def verificar_conexoes(self):
        """Verifica conexões inativas (thread separada)"""
        while True:
            tempo_atual = time.time()
            enderecos_inativos = []
            
            for endereco in list(self.ultimo_keepalive.keys()):
                if tempo_atual - self.ultimo_keepalive[endereco] > 30:  # 30 segundos timeout
                    enderecos_inativos.append(endereco)
            
            for endereco in enderecos_inativos:
                if endereco in self.jogadores:
                    nome = self.jogadores[endereco]['nome']
                    self.log_evento(f"Jogador {nome} ({endereco}) desconectado por inatividade")
                    del self.jogadores[endereco]
                    del self.ultimo_keepalive[endereco]
                    
                    if len(self.jogadores) < 2 and self.partida_ativa:
                        self.broadcast_mensagem("MENSAGEM:Partida cancelada - jogadores insuficientes")
                        self.partida_ativa = False
                        self.jogadores.clear()
                        self.ultimo_keepalive.clear()
            
            time.sleep(10)  # Verifica a cada 10 segundos
    
    def executar(self):
        """Loop principal do servidor"""
        # Inicia thread para verificar conexões
        thread_keepalive = threading.Thread(target=self.verificar_conexoes, daemon=True)
        thread_keepalive.start()
        
        print("Servidor aguardando conexões...")
        
        while True:
            try:
                data, endereco = self.socket.recvfrom(1024)
                mensagem = data.decode('utf-8').strip()
                
                self.log_evento(f"Recebido de {endereco}: {mensagem}")
                
                if mensagem.startswith("ENTRAR:"):
                    nome = mensagem.split(":", 1)[1]
                    self.processar_entrada_jogador(endereco, nome)
                
                elif mensagem == "PEDIR_CARTA":
                    self.processar_pedir_carta(endereco)
                
                elif mensagem == "PARAR":
                    self.processar_parar(endereco)
                
                elif mensagem == "KEEPALIVE":
                    self.processar_keepalive(endereco)
                
                else:
                    self.enviar_mensagem(endereco, "MENSAGEM:Comando não reconhecido")
                    
            except Exception as e:
                print(f"Erro no servidor: {e}")

if __name__ == "__main__":
    servidor = Servidor21()
    try:
        servidor.executar()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        # Salva o log antes de sair
        with open("log_partidas.txt", "w", encoding="utf-8") as f:
            for entrada in servidor.log_partidas:
                f.write(entrada + "\n")
        print("Log salvo em log_partidas.txt")

