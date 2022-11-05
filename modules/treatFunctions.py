import numpy as np


def input_treat(file: str) -> tuple:
    """
    @brief Função para tratamento de input 

    @param file: O caminho para o arquivo a ser aberto

    @return Tupla com a matriz de restrições, o vetor de custo, o número de restrições e o número de variáveis
    """
    f = open(file)

    n_restricoes, n_var = f.readline().split(' ')
    n_restricoes, n_var = int(n_restricoes), int(n_var)

    cost_vector = np.array([int(i) for i in f.readline().split(' ')])
    
    matriz_rest = np.ndarray((n_restricoes, n_var + 1))
    
    for i in range(n_restricoes):
      matriz_rest[i] = f.readline().split(" ")

    return (matriz_rest, cost_vector, n_restricoes, n_var)

