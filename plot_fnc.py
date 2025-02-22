import numpy as np
import matplotlib.pyplot as plt

# Definizione delle funzioni di utilità
def utilita_bs(nodi, prezzo, cost_per_servizio=10):
    """Calcola l'utilità della Base Station"""
    return max(0, (nodi * (prezzo - cost_per_servizio)) - (50 / nodi) if nodi < 50 else 0)

def calcola_accuracy(nodi, iterazioni, max_nodi=50, max_iter=150):
    """Calcola l'accuratezza in base ai nodi e alle iterazioni"""
    return  (iterazioni * nodi) / (max_nodi * max_iter)

def utilita_ml_provider(nodi, iterazioni, prezzo_bs, costo_iter=20):
    """Funzione di utilità del ML Provider (minimizzazione del costo)"""
    accuracy = calcola_accuracy(nodi, iterazioni)
    penalita_iterazioni = (100 / (nodi + 1)) ** 2
    costo = (nodi * prezzo_bs) + (iterazioni * costo_iter) + penalita_iterazioni
    return accuracy - costo  # Maggiore accuratezza e minori costi = migliore utilità

# Impostiamo il range di nodi e iterazioni
nodi_range = np.linspace(1, 100, 50)  # Da 1 a 100 nodi
iterazioni_range = np.linspace(1, 150, 50)  # Da 1 a 150 iterazioni

# Prezzo iniziale della BS
prezzo_bs = 22

# Calcoliamo le utilità
utilita_bs_values = [utilita_bs(n, prezzo_bs) for n in nodi_range]
utilita_ml_values = [utilita_ml_provider(n, 100, prezzo_bs) for n in nodi_range]  # Fissiamo iterazioni=100 per il plot

# Creazione del grafico
plt.figure(figsize=(10, 5))

plt.plot(nodi_range, utilita_bs_values, label="Utilità Base Station", color='blue', linestyle='-')
plt.plot(nodi_range, utilita_ml_values, label="Utilità ML Provider", color='red', linestyle='--')

plt.xlabel("Numero di Nodi Serviti")
plt.ylabel("Utilità")
plt.title("Confronto della Funzione di Utilità della BS e del ML Provider")
plt.legend()
plt.grid(True)

# Mostra il plot
plt.show()
