import numpy as np
from time import sleep

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
        self.n_rest = nRest
        self.cost_vector = costV
        self.rest_M = resM
        self.rest_results = np.zeros([nRest])
        self.is_dual = False
        self.__fpiMade = False

    def makeFPI(self) -> None:
        """
        @function makeFPI

        @brief Transforma a PL recebida originalmente na Forma Padrão de igualdade. Com a FPI, fica mais fácil executar o algoritmo simplex.
        """
        # Criando variáveis de relaxação para transformar PL em igualdades
        if not self.__fpiMade:
            self.__fpiMade = True

            newCosts = np.zeros(self.n_rest)
            self.cost_vector = np.concatenate(
                (self.cost_vector, newCosts), axis=None)

            # Adicionando novas variáveis à matriz de restrições
            newRests = np.zeros((self.n_rest, self.n_rest))

            for i in range(self.n_rest):
                newRests[i][i] = 1

            self.rest_results = np.array(self.rest_M[:, -1])
            self.rest_M = np.delete(self.rest_M, -1, 1)
            self.rest_M = np.concatenate((self.rest_M, newRests), axis=1)

    def __str__(self) -> str:
        return (f"""
---------------------------------------------
| INFORMAÇÕES DA PROGRAMAÇÃO LINEAR| \n
- Número de variáveis: {self.__n_var};\n
- Número de Restrições: {self.n_rest} \n
- Vetor de Custos: {self.cost_vector} \n
- Vetor de Resultados: {self.rest_results}\n
- Matriz de Restrições: \n {self.rest_M} \n
----------------------------------------------
        """)


class Simplex:
    """
    @brief Para modos de praticidade, o algoritmo simplex será representado como uma classe dentro do programa. Ele recebe uma PL já em FPI, verifica qual método deverá ser seguido para calcular o ótimo e executa o algoritmo.

    @param lp: A PL a ser trabalhada
    """
    def __init__(self, lp: LinearProgram) -> None:
        self.__lp = lp
        self.__VERO = None
        self.__certificate = np.zeros(lp.n_rest)
        self.__objValue = 0
        self.__baseVars = []

    def __isOptimal__(self) -> bool:
        for i in self.__lp.cost_vector:
            if i > 0:
                return False
        else:
            return True

    def __findMaxCostIndex__(self) -> int:
        maxItem = np.amax(self.__lp.cost_vector)
        indexMax = np.where(self.__lp.cost_vector == maxItem)[0][0]
        return indexMax

    def __findMinFormCol__(self, column: np.ndarray) -> int:
      small = -1
      small_idx = 0

      for idx, element in enumerate(column):
          if element > 0:
              if column[idx] < small or small < 0:
                  small = column[idx]
                  small_idx = idx

      return (small, small_idx)

    def __pivot__(self, iMax: int) -> None:

        # Pego a coluna referente às restrições
        ColumnCopy = self.__lp.rest_M[:, iMax]

        # Descubro qual restrição deverá ser pivoteada
        small, small_idx = self.__findMinFormCol__(ColumnCopy)

        # Pivoteio a resrtição (no caso, deixo o valor como 1.)
        self.__lp.rest_M[small_idx] = self.__lp.rest_M[small_idx] / small
        self.__lp.rest_results[small_idx] = self.__lp.rest_results[small_idx] / small

        self.__VERO[small_idx] = self.__VERO[small_idx] / \
            small  # Espelhando as operações no VERO


        # Zerando Colunas acima e abaixo do valor Pivoteado, na matriz de Restrições.
        for i in range(self.__lp.n_rest):
            if i != small_idx:
                toBeNull = self.__lp.rest_M[i][iMax]

                self.__lp.rest_M[i] = self.__lp.rest_M[i] + \
                    (-1 * toBeNull * self.__lp.rest_M[i])
                self.__lp.rest_results[i] = self.__lp.rest_results[i] + \
                    (-1 * toBeNull * self.__lp.rest_results[i])
                self.__VERO[i] = self.__VERO[i] + \
                    (-1 * toBeNull * self.__VERO[i])



        toBeNull = self.__lp.cost_vector[iMax]  # Pegando o valor do elemento do vetor de custos a ser anulado.

        self.__lp.cost_vector = self.__lp.cost_vector + \
            (-1 * toBeNull * self.__lp.rest_M[iMax])  # Anulando o vetor de custos no ponto.


        self.__certificate = self.__certificate - (toBeNull * self.__VERO[iMax])  # Repetindo as operações no VERO e no certificado;
    
        self.__objValue = self.__objValue - (self.__lp.rest_results[iMax] * toBeNull)


    def __startVero__(self) -> None:
        self.__VERO = np.zeros((self.__lp.n_rest, self.__lp.n_rest))

        for i in range(self.__lp.n_rest):
            self.__VERO[i][i] = 1


    def runSimplex(self) -> None:
        self.__startVero__()

        while not self.__isOptimal__():
            iMax = self.__findMaxCostIndex__()
            self.__pivot__(iMax)

        self.__certificate = self.__certificate * -1
        self.__objValue = self.__objValue * -1

        for i in range(self.__lp.n_rest):
            if(self.__lp.cost_vector[i]) == 0:
                self.__baseVars.append(i+1)

    def dualSimplex(self):
        pass

    def __str__(self) -> str:
        a = f"""
        ---------- | SIMPLEX RESULTS | ----------
          -> Valor Objetivo: {self.__objValue}
          -> Certificado: {self.__certificate}
          -> Variáveis Básicas: {self.__baseVars}

        1. Otima
        2. {self.__objValue}
        3. {self.__certificate}

        """

        return a
