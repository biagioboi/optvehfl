import numpy as np
import pandas as pd
import glob


class BS:
    def __init__(self, id, prezzo_iniziale):
        self.id = id
        self.price_per_tx_power = 5  # Costo per ogni W di potenza trasmessa
        self.prezzo = prezzo_iniziale  # Prezzo per utente servito
        self.tx_min = 1
        self.tx_max = 20
        self.tx_power = 10  # Partiamo con un valore iniziale ragionevole
        self.no_demand_rounds = 0  # Conta i round senza domanda

    def calcola_sinr(self, curr_tx):
        return 4 * 10 ** 8 * np.log2(1 + curr_tx / 10 ** -17)

    def calcola_throughput(self, nodi, curr_tx):
        sinr = self.calcola_sinr(curr_tx)
        return sinr / nodi if nodi > 0 else 0

    def bs_satisfied(self, nodi, curr_tx):
        throughput = self.calcola_throughput(nodi, curr_tx)
        return throughput >= 60

    def scegli_prezzo(self, nodi, ml_budget):
        if nodi == 0:
            self.no_demand_rounds += 1
            if self.no_demand_rounds > 2:
                self.prezzo = max(self.prezzo - 2, 0.001)  # Riduzione più aggressiva dopo 2 round senza domanda
            else:
                self.prezzo = max(self.prezzo - 4, 0.001)  # Riduzione standard
        else:
            self.no_demand_rounds = 0  # Resetta il contatore se c'è domanda
            max_prezzo_possibile = ml_budget / nodi
            self.prezzo = min(self.prezzo + 1, max_prezzo_possibile)  # Aumento più lento per evitare oscillazioni

        return self.prezzo


class MLProvider:
    def __init__(self, budget, df):
        self.budget = budget
        self.price_per_iter = 10
        self.iterazioni = 0
        self.accuracy = 0
        self.min_utenti = 10
        self.max_utenti = 89
        self.min_iterazioni = 10
        self.max_iter = 100
        self.df = df

    def feasible_comb(self, bs, utenti, iterazioni):
        return self.budget >= (utenti * bs.prezzo + iterazioni * self.price_per_iter)

    def scegli_nodi_iterazioni(self, bs):
        best_option = {"accuracy": 0.00, "nodi": 0, "iterazioni": 0}

        for x in range(self.min_iterazioni, self.max_iter):
            for y in range(self.min_utenti, self.max_utenti):
                df_filter = self.df.loc[(self.df['num_nodes'] == y) & (self.df['round'] == x)]
                if df_filter.empty:
                    continue  # Evita errori se il dataframe non ha dati

                temp_accuracy = df_filter['accuracy'].iloc[0]
                if temp_accuracy > best_option["accuracy"] and self.feasible_comb(bs, y, x):
                    best_option.update({"accuracy": temp_accuracy, "nodi": y, "iterazioni": x})

        self.accuracy = best_option["accuracy"]
        return best_option


# Lettura dei dati da file CSV
file_pattern = "data/*.csv"
csv_files = glob.glob(file_pattern)
df_list = [pd.read_csv(file) for file in csv_files]
df = pd.concat(df_list, ignore_index=True)

# Inizializzazione dei giocatori
bs_player = BS(1, 0.001)
ml_player = MLProvider(500, df)

max_round = 100
for i in range(1, max_round):
    current_best = ml_player.scegli_nodi_iterazioni(bs_player)
    ml_player.iterazioni = current_best["iterazioni"]
    ml_player.accuracy = current_best["accuracy"]
    nodi_scelti = current_best["nodi"]

    print(
        f"Round {i}: ML provider sceglie {ml_player.iterazioni} iterazioni, {nodi_scelti} nodi, accuracy {ml_player.accuracy:.4f}")

    bs_player.scegli_prezzo(nodi_scelti, ml_player.budget)
    print(f"Round {i}: BS aggiorna il prezzo a {bs_player.prezzo:.4f}\n")
