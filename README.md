# Simulador de Controle de Concorrência com Detecção e Resolução de Deadlock (Wait-Die)

Este projeto simula um sistema de transações concorrentes que acessam recursos compartilhados (X e Y), aplicando o algoritmo Wait-Die para controlar deadlocks. Ele foi desenvolvido como atividade prática para a disciplina de Banco de Dados II - UNIVALI.

---

## Objetivo

- Simular concorrência entre transações usando threads.
- Aplicar locks binários para controlar o acesso a dois recursos.
- Detectar deadlocks em tempo real usando grafos de espera.
- Resolver deadlocks com o algoritmo Wait-Die, forçando a reinicialização de transações mais novas.
- Exibir, no terminal, todas as ações das transações de forma clara e educativa.

---

## Tecnologias Utilizadas

- Python 3.10+
- `threading` (concorrência)
- `random`, `time` (simulação de acesso aleatório)
- `collections.defaultdict`, `deque` (para o grafo de espera)

---

## Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/KauaHermer/BancoDeDadosDeadLock.git
   cd BancoDeDadosDeadLock
   ```

2. Execute o simulador:
   ```bash
   python simulador.py
   ```

---

## Exemplo de Saída

T3 iniciando (tentativa 1, timestamp: 2)  
T3 tentando lock em X  
T3 (ts:2) morre esperando X de T2  
T3 ABORTADA  
T3 reiniciando com novo timestamp...  
T3 iniciando (tentativa 2, timestamp: 4)  
T3 tentando lock em X  
T3 obteve lock em X  
T3 tentando lock em Y  
T3 obteve lock em Y  
T3 leu Y = 33  
T3 escreveu X = 92  
T3 escreveu Y = 1  
T3 liberou X  
T3 liberou Y  
T3 COMMIT realizado  
T3 finalizou com sucesso.

---

Desenvolvido por [Kaua Hermer](https://github.com/KauaHermer)
