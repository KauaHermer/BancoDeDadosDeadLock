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

T1 iniciando (tentativa 1, ts: 0)
T1 tenta lock em X
T1 obteve lock em X
T1 leu X = 25
T1 tenta lock em Y
T1 obteve lock em Y
T1 leu Y = 48
T1 escreveu X = 35
T1 escreveu Y = 15
T1 liberou Y
T1 liberou X
T1 COMMIT realizado
T1 finalizou com sucesso

Simulação concluída.

---

Desenvolvido por [Kaua Hermer](https://github.com/KauaHermer)
