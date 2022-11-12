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
        self.__is_dual = False
        self.__fpiMade = False

    def makeFPI(self) -> None:
        """
        @function makeFPI

        @brief Transforma a PL recebida originalmente na Forma Padrão de igualdade. Com a FPI, fica mais fácil executar o algoritmo simplex.
        """
        # Criando variáveis de relaxação para transformar PL em igualdades
        if not self.__fpiMade:
            self.__fpiMade = True

            newCosts = np.zeros(self.__n_rest)
            self.__cost_vector = np.concatenate(
                (self.__cost_vector, newCosts), axis=None)

            # Adicionando novas variáveis à matriz de restrições
            newRests = np.zeros((self.__n_rest, self.__n_rest))

            for i in range(self.__n_rest):
                newRests[i][i] = 1

            self.__rest_results = np.array([self.__rest_M[:, -1]])
            self.__rest_M = np.delete(self.__rest_M, -1, 1)
            self.__rest_M = np.concatenate((self.__rest_M, newRests), axis=1)


    def getSimplexMode(self) -> bool:
        self.__isDual__()
        return self.__is_dual

    def __isDual__(self):
        tableauHead = self.__cost_vector.dot(-1)
        negVars = False

        for i in self.__rest_results[0]:
            if i < 0:
                negVars = True
                break

        if negVars:
            for i in tableauHead:
                if i < 0:
                    self.__is_dual = False
                    break
            else:
                self.__is_dual = True



    def __str__(self) -> str:
        return (f"""
---------------------------------------------
| INFORMAÇÕES DA PROGRAMAÇÃO LINEAR| \n
- Número de variáveis: {self.__n_var};\n
- Número de Restrições: {self.__n_rest} \n
- Vetor de Custos: {self.__cost_vector} \n
- Vetor de Resultados: {self.__rest_results}\n
- Usar Simplex Dual? {self.getSimplexMode()} \n
- Matriz de Restrições: \n {self.__rest_M} \n
----------------------------------------------
        """)



class Simplex:
    """
    @brief Para modos de praticidade, o algoritmo simplex será representado como uma classe dentro do programa. Ele recebe uma PL já em FPI, verifica qual método deverá ser seguido para calcular o ótimo e executa o algoritmo.

    @param lp: A PL a ser trabalhada
    """
    def __init__(self, lp: LinearProgram) -> None:
        self.__lp = lp

    def runSimplex(self):
        pass

    def primalSimplex(self):
        pass

    def dualSimplex(self):
        pass

    def auxLinearProgram(self):
        pass
