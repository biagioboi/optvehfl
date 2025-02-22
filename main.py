import numpy as np
import pandas as pd
import glob
from scipy.optimize import minimize

nodi_scelti = 0

class BS:
    def __init__(self, id, prezzo_iniziale):
        self.id = id
        self.price_per_tx_power = 5 # Pago 5 euro per ogni W di tx power
        self.prezzo = prezzo_iniziale # Prezzo che il ML Provider deve pagarmi per ciascun utente servito
        self.tx_min = 1
        self.tx_max = 20
        self.tx_power = 0

    def feasible_comb(self, nodi, curr_tx):
        amount_to_pay = curr_tx * self.price_per_tx_power
        return amount_to_pay <= nodi * self.prezzo

    def bs_satisfied(self, nodi, curr_tx):
        sinr = 4 * 10 ** 8 * np.log2(1 + curr_tx / 10 ** -17)
        throughput = sinr / nodi
        if throughput < 60:
            return False, 0
        while not self.feasible_comb(nodi, curr_tx):
            self.prezzo = self.prezzo + 0.05
        return True, throughput

    def scegli_prezzo(self, nodi):
        past_utility = nodi / 90 * nodi * self.prezzo
        feasible, throughput = self.bs_satisfied(nodi, 10)
        if past_utility >= (nodi / 90) * nodi * self.prezzo:
            self.prezzo = self.prezzo - 0.05
        print(f"Current gain {nodi / 90 * nodi * self.prezzo}")

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
        if self.accuracy > 0:
            current_best = {"accuracy": self.accuracy, "nodi": 0, "iterazioni": 0}
        else:
            current_best = {"accuracy": 0.00, "nodi": 0, "iterazioni": 0}
        for x in range(self.min_iterazioni, self.max_iter):
            for y in range(self.min_utenti, self.max_utenti):
                temp = self.df.loc[(df['num_nodes'] == y) & (df['round'] == x)]['accuracy'].iloc[0]
                if temp > current_best["accuracy"]:
                    if self.feasible_comb(bs, y, x):
                        current_best["accuracy"] = temp
                        current_best["nodi"] = y
                        current_best["iterazioni"] = x
        self.accuracy = current_best["accuracy"]
        return current_best


file_pattern = "*.csv"  # Cambia se i file sono in una cartella diversa
csv_files = glob.glob(file_pattern)
df_list = [pd.read_csv(file) for file in csv_files]
df = pd.concat(df_list, ignore_index=True)
bs_player = BS(1, 0.001)
ml_player = MLProvider(500, df)
max_round = 100
for i in range(1, max_round):
    current_best = ml_player.scegli_nodi_iterazioni(bs_player)
    ml_player.iterazioni = current_best["iterazioni"]
    ml_player.accuracy = current_best["accuracy"]
    print(f"The best is {ml_player.iterazioni} and {ml_player.accuracy} with { current_best['nodi']}\n")

    nodi_scelti = current_best["nodi"]
    bs_player.scegli_prezzo(nodi_scelti)
    print(f"The new price is {bs_player.prezzo}\n")
