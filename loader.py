import threading
import time
import random
from collections import defaultdict, deque
from enum import Enum

class Status(Enum):
    ATIVA = "ATIVA"
    ESPERANDO = "ESPERANDO"
    ABORTADA = "ABORTADA"
    FINALIZADA = "FINALIZADA"

class Recurso:
    def __init__(self, nome):
        self.nome = nome
        self.lock = threading.RLock()
        self.ocupado_por = None
        self.valor = random.randint(1, 100)

    def __str__(self):
        return f"{self.nome}(valor={self.valor}, ocupado_por={self.ocupado_por})"

class GerenciadorDeadlock:
    def __init__(self):
        self.grafo = defaultdict(set)
        self.lock = threading.RLock()

    def add_espera(self, t_espera, t_detentora):
        with self.lock:
            self.grafo[t_espera].add(t_detentora)

    def remove_espera(self, t_espera, t_detentora=None):
        with self.lock:
            if t_detentora:
                self.grafo[t_espera].discard(t_detentora)
            else:
                self.grafo[t_espera].clear()
                for origem in self.grafo:
                    self.grafo[origem].discard(t_espera)

    def detectar_deadlock(self):
        with self.lock:
            visitados = set()
            caminho = set()

            def dfs(n):
                if n in caminho: return True
                if n in visitados: return False
                visitados.add(n)
                caminho.add(n)
                for vizinho in self.grafo[n]:
                    if dfs(vizinho): return True
                caminho.remove(n)
                return False

            return any(dfs(no) for no in self.grafo if no not in visitados)

    def transacoes_em_deadlock(self):
        with self.lock:
            if not self.detectar_deadlock():
                return set()
            em_ciclo, visitados, caminho = set(), set(), []

            def dfs(n):
                if n in caminho:
                    em_ciclo.update(caminho[caminho.index(n):])
                    return
                if n in visitados: return
                visitados.add(n)
                caminho.append(n)
                for vizinho in self.grafo[n]:
                    dfs(vizinho)
                caminho.pop()

            for no in self.grafo:
                if no not in visitados:
                    dfs(no)
            return em_ciclo

class Sistema:
    def __init__(self):
        self.recursos = {r: Recurso(r) for r in ['X', 'Y']}
        self.transacoes = {}
        self.timestamp = 0
        self.lock = threading.RLock()
        self.gerenciador = GerenciadorDeadlock()
        self.evento_parar_detector = threading.Event()
        self.thread_detector = None

    def novo_timestamp(self):
        with self.lock:
            t = self.timestamp
            self.timestamp += 1
            return t

    def iniciar_detector(self):
        def detector():
            while not self.evento_parar_detector.wait(1):
                self.detectar_resolver_deadlock()
        self.thread_detector = threading.Thread(target=detector, daemon=True)
        self.thread_detector.start()

    def parar_detector(self):
        self.evento_parar_detector.set()
        if self.thread_detector:
            self.thread_detector.join()

    def detectar_resolver_deadlock(self):
        em_deadlock = self.gerenciador.transacoes_em_deadlock()
        if em_deadlock:
            print(f"\n🚨 DEADLOCK entre: {em_deadlock}")
            vitima = max((self.transacoes[n] for n in em_deadlock), key=lambda t: t.timestamp, default=None)
            if vitima:
                print(f"💀 Abortando {vitima.nome} (ts: {vitima.timestamp})")
                vitima.abortar()

class Transacao(threading.Thread):
    def __init__(self, nome, sistema):
        super().__init__()
        self.sistema = sistema
        self.nome = nome
        self.timestamp = sistema.novo_timestamp()
        self.status = Status.ATIVA
        self.recursos = set()
        self.abort_event = threading.Event()
        self.tentativas = 0
        self.max_tentativas = 3

    def run(self):
        while self.tentativas < self.max_tentativas:
            self.tentativas += 1
            print(f"🚀 {self.nome} iniciando (tentativa {self.tentativas}, ts: {self.timestamp})")
            if self.executar():
                print(f"✅ {self.nome} finalizou com sucesso")
                self.status = Status.FINALIZADA
                break
            else:
                if self.tentativas < self.max_tentativas:
                    print(f"🔄 {self.nome} reiniciando...")
                    self.reiniciar()
                else:
                    print(f"❌ {self.nome} falhou após {self.max_tentativas} tentativas")
        with self.sistema.lock:
            self.sistema.transacoes.pop(self.nome, None)

    def executar(self):
        try:
            with self.sistema.lock:
                self.sistema.transacoes[self.nome] = self

            time.sleep(random.uniform(0.1, 0.5))
            if not self.lock('X'): return False
            self.ler('X')
            time.sleep(random.uniform(0.1, 0.3))
            if not self.lock('Y'):
                self.unlock_todos()
                return False
            self.ler('Y')
            time.sleep(random.uniform(0.1, 0.3))
            self.escrever('X')
            self.escrever('Y')
            self.unlock_todos()
            self.commit()
            return True
        except Exception as e:
            print(f"❌ Erro em {self.nome}: {e}")
            self.unlock_todos()
            return False

    def lock(self, recurso_nome):
        if self.abort_event.is_set():
            return False
        recurso = self.sistema.recursos[recurso_nome]
        print(f"🔒 {self.nome} tenta lock em {recurso_nome}")
        if recurso.lock.acquire(timeout=0.1):
            if recurso.ocupado_por is None:
                recurso.ocupado_por = self.nome
                self.recursos.add(recurso_nome)
                print(f"✅ {self.nome} obteve {recurso_nome}")
                return True
            else:
                detentora = self.sistema.transacoes.get(recurso.ocupado_por)
                recurso.lock.release()
                return self.wait_die(recurso_nome, detentora)
        else:
            detentora = self.sistema.transacoes.get(recurso.ocupado_por)
            return self.wait_die(recurso_nome, detentora) if detentora else False

    def wait_die(self, recurso_nome, detentora):
        if detentora and self.timestamp < detentora.timestamp:
            return self.esperar(recurso_nome, detentora)
        else:
            print(f"💀 {self.nome} (ts:{self.timestamp}) morre por {recurso_nome} de {detentora.nome if detentora else 'desconhecida'}")
            self.abortar()
            return False

    def esperar(self, recurso_nome, detentora):
        print(f"⏳ {self.nome} espera {recurso_nome} ocupado por {detentora.nome}")
        self.status = Status.ESPERANDO
        self.sistema.gerenciador.add_espera(self.nome, detentora.nome)
        sucesso = self.espera_ativa(recurso_nome)
        self.sistema.gerenciador.remove_espera(self.nome, detentora.nome)
        return sucesso

    def espera_ativa(self, recurso_nome):
        inicio = time.time()
        while time.time() - inicio < 3:
            if self.abort_event.is_set():
                return False
            if self.tenta_adquirir(recurso_nome):
                self.status = Status.ATIVA
                print(f"✅ {self.nome} obteve {recurso_nome} após esperar")
                return True
            time.sleep(0.1)
        print(f"⏰ {self.nome} timeout ao esperar {recurso_nome}")
        return False

    def tenta_adquirir(self, recurso_nome):
        recurso = self.sistema.recursos[recurso_nome]
        if recurso.lock.acquire(timeout=0.1):
            if recurso.ocupado_por is None:
                recurso.ocupado_por = self.nome
                self.recursos.add(recurso_nome)
                return True
            else:
                recurso.lock.release()
        return False

    def ler(self, recurso_nome):
        recurso = self.sistema.recursos[recurso_nome]
        print(f"📖 {self.nome} leu {recurso_nome} = {recurso.valor}")

    def escrever(self, recurso_nome):
        recurso = self.sistema.recursos[recurso_nome]
        novo_valor = random.randint(1, 100)
        recurso.valor = novo_valor
        print(f"✏️  {self.nome} escreveu {recurso_nome} = {novo_valor}")

    def unlock_todos(self):
        for r in list(self.recursos):
            self.unlock(r)

    def unlock(self, recurso_nome):
        if recurso_nome in self.recursos:
            recurso = self.sistema.recursos[recurso_nome]
            recurso.ocupado_por = None
            self.recursos.remove(recurso_nome)
            recurso.lock.release()
            print(f"🔓 {self.nome} liberou {recurso_nome}")

    def commit(self):
        print(f"💾 {self.nome} COMMIT")

    def abortar(self):
        self.status = Status.ABORTADA
        self.abort_event.set()
        self.sistema.gerenciador.remove_espera(self.nome)
        self.unlock_todos()
        print(f"💀 {self.nome} ABORTADA")

    def reiniciar(self):
        self.status = Status.ATIVA
        self.abort_event.clear()
        self.recursos.clear()
        self.timestamp = self.sistema.novo_timestamp()
        time.sleep(random.uniform(0.5, 1.5))

def main():
    print("🎯 Simulador Wait-Die iniciando\n")
    sistema = Sistema()
    sistema.iniciar_detector()

    try:
        transacoes = [Transacao(f"T{i+1}", sistema) for i in range(4)]
        print(f"🚀 Iniciando {len(transacoes)} transações...\n")
        for t in transacoes:
            t.start()
            time.sleep(random.uniform(0.1, 0.3))
        for t in transacoes:
            t.join()
        print("\n🏁 Simulação concluída!")
        for nome, recurso in sistema.recursos.items():
            print(f"  {recurso}")
    finally:
        sistema.parar_detector()

if __name__ == "__main__":
    main()
