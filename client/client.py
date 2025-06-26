import socket
import threading
import time

class Cliente21:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conectado = False
        self.nome = ""
        self.cartas = []
        self.pontuacao = 0
        self.jogo_ativo = False
        
    def conectar(self, nome):
        """Conecta ao servidor com o nome do jogador"""
        self.nome = nome
        try:
            mensagem = f"ENTRAR:{nome}"
            self.socket.sendto(mensagem.encode('utf-8'), (self.host, self.port))
            self.conectado = True
            print(f"Conectando como {nome}...")
            
            # Inicia thread para receber mensagens
            thread_receber = threading.Thread(target=self.receber_mensagens, daemon=True)
            thread_receber.start()
            
            # Inicia thread para keepalive
            thread_keepalive = threading.Thread(target=self.enviar_keepalive, daemon=True)
            thread_keepalive.start()
            
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def receber_mensagens(self):
        """Thread para receber mensagens do servidor"""
        while self.conectado:
            try:
                data, _ = self.socket.recvfrom(1024)
                mensagem = data.decode('utf-8').strip()
                
                if mensagem.startswith("CARTA:"):
                    carta = mensagem.split(":", 1)[1]
                    self.cartas.append(carta)
                    print(f"\n🃏 Nova carta recebida: {carta}")
                    
                elif mensagem.startswith("RESULTADO:"):
                    resultado = mensagem.split(":", 1)[1]
                    self.processar_resultado(resultado)
                    
                elif mensagem.startswith("MENSAGEM:"):
                    texto = mensagem.split(":", 1)[1]
                    print(f"\n📢 {texto}")
                    
                elif mensagem == "KEEPALIVE_ACK":
                    # Resposta do keepalive, não precisa fazer nada
                    pass
                    
                else:
                    print(f"\n📨 Mensagem do servidor: {mensagem}")
                    
            except Exception as e:
                if self.conectado:
                    print(f"Erro ao receber mensagem: {e}")
                break
    
    def processar_resultado(self, resultado):
        """Processa o resultado final da partida"""
        print("\n" + "="*50)
        print("🎯 RESULTADO FINAL DA PARTIDA")
        print("="*50)
        
        if resultado == "GANHOU":
            print("🎉 PARABÉNS! VOCÊ GANHOU! 🎉")
        elif resultado == "PERDEU":
            print("😞 Você perdeu desta vez...")
        elif resultado == "EMPATE":
            print("🤝 Empate!")
        
        print("="*50)
        self.jogo_ativo = False
        self.cartas = []
        self.pontuacao = 0
    
    def enviar_keepalive(self):
        """Thread para enviar mensagens de keepalive"""
        while self.conectado:
            try:
                self.socket.sendto("KEEPALIVE".encode('utf-8'), (self.host, self.port))
                time.sleep(15)  # Envia keepalive a cada 15 segundos
            except Exception as e:
                if self.conectado:
                    print(f"Erro ao enviar keepalive: {e}")
                break
    
    def pedir_carta(self):
        """Solicita uma nova carta ao servidor"""
        try:
            self.socket.sendto("PEDIR_CARTA".encode('utf-8'), (self.host, self.port))
        except Exception as e:
            print(f"Erro ao pedir carta: {e}")
    
    def parar(self):
        """Informa ao servidor que o jogador quer parar"""
        try:
            self.socket.sendto("PARAR".encode('utf-8'), (self.host, self.port))
        except Exception as e:
            print(f"Erro ao parar: {e}")
    
    def mostrar_status(self):
        """Mostra o status atual do jogador"""
        if self.cartas:
            print(f"\n🃏 Suas cartas: {', '.join(self.cartas)}")
            print(f"📊 Pontuação atual: {self.pontuacao}")
    
    def executar(self):
        """Loop principal do cliente"""
        print("🎮 Bem-vindo ao Jogo 21 (Blackjack)!")
        print("="*40)
        
        # Solicita o nome do jogador
        while True:
            nome = input("Digite seu nome: ").strip()
            if nome:
                break
            print("Por favor, digite um nome válido.")
        
        # Conecta ao servidor
        if not self.conectar(nome):
            print("Não foi possível conectar ao servidor.")
            return
        
        print("\n📋 Comandos disponíveis:")
        print("  1 - Pedir carta")
        print("  2 - Parar")
        print("  3 - Ver status")
        print("  4 - Sair")
        print("\nAguarde o início da partida...")
        
        # Loop principal de interação
        while self.conectado:
            try:
                print("\n" + "-"*30)
                comando = input("Digite o comando (1-4): ").strip()
                
                if comando == "1":
                    self.pedir_carta()
                    
                elif comando == "2":
                    self.parar()
                    
                elif comando == "3":
                    self.mostrar_status()
                    
                elif comando == "4":
                    print("Saindo do jogo...")
                    self.conectado = False
                    break
                    
                else:
                    print("Comando inválido. Use 1, 2, 3 ou 4.")
                    
            except KeyboardInterrupt:
                print("\nSaindo do jogo...")
                self.conectado = False
                break
            except Exception as e:
                print(f"Erro: {e}")
        
        self.socket.close()
        print("Desconectado do servidor.")

if __name__ == "__main__":
    # Permite configurar o endereço do servidor
    print("🎮 Cliente do Jogo 21")
    print("="*25)
    
    host = input("Digite o IP do servidor (Enter para localhost): ").strip()
    if not host:
        host = "localhost"
    
    try:
        port = input("Digite a porta do servidor (Enter para 12345): ").strip()
        if not port:
            port = 12345
        else:
            port = int(port)
    except ValueError:
        print("Porta inválida, usando 12345")
        port = 12345
    
    cliente = Cliente21(host, port)
    cliente.executar()

