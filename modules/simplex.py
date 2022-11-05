import numpy as np


class LinearProgram:
    """
    @brief: Representação de uma Programação Linear no programa. A PL orginal é da forma:

      max c.T @ X
      sujeito a: A@x <= b
                  x >= 0

    @param: nVars - Número de Variáveis originais
    @param: nRest - Número de Restrições
    @param: costV - Vetor de Custos da PL
    @param: resM - Matriz de Restrições
    """

    def __init__(self, nVars: int, nRest: int, costV: np.ndarray, resM: np.ndarray) -> None:

        self.__n_var = nVars
        self.__n_rest = nRest
        self.__cost_vector = costV
        self.__rest_M = resM

        self.__rest_results = np.zeros([nRest])


    def makeFPI(self) -> None:
        """
        @function makeFPI

        @brief Transforma a PL recebida originalmente na Forma Padrão de igualdade. Com a FPI, fica mais fácil executar o algoritmo simplex.
        """
        # Criando variáveis de relaxação para transformar PL em igualdades
        newCosts = np.zeros(self.__n_rest)
        self.__cost_vector = np.concatenate(
              (self.__cost_vector, newCosts), axis=None)

        # Adicionando novas variáveis à matriz de restrições
        newRests = np.zeros((self.__n_rest, self.__n_rest))

        for i in range(self.__n_rest):
              newRests[i][i] = 1

        self.__rest_results = np.array([self.__rest_M[:, -1]])

        self.__rest_M = np.delete(self.__rest_M, -1, 1)

        self.__rest_M = np.concatenate((self.__rest_M, newRests, self.__rest_results.T), axis=1)


    def __str__(self) -> str:
        return (f"""
---------------------------------------------
| INFORMAÇÕES DA PROGRAMAÇÃO LINEAR| \n
- Número de variáveis: {self.__n_var};\n
- Número de Restrições: {self.__n_rest} \n
- Vetor de Custos: {self.__cost_vector} \n
- Matriz de Restrições: \n {self.__rest_M} \n
----------------------------------------------
        """)


class Simplex:
    def __init__(self, lp: LinearProgram) -> None:
        self.__lp = lp
