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

            self.rest_results = np.array([self.rest_M[:, -1]])
            self.rest_M = np.delete(self.rest_M, -1, 1)
            self.rest_M = np.concatenate((self.rest_M, newRests), axis=1)

    def getSimplexMode(self) -> bool:
        self.__isDual__()
        return self.is_dual

    def __isDual__(self):
        tableauHead = self.cost_vector.dot(-1)
        negVars = False

        for i in self.rest_results[0]:
            if i < 0:
                negVars = True
                break

        if negVars:
            for i in tableauHead:
                if i < 0:
                    self.is_dual = False
                    break
            else:
                self.is_dual = True

    def __str__(self) -> str:
        return (f"""
---------------------------------------------
| INFORMAÇÕES DA PROGRAMAÇÃO LINEAR| \n
- Número de variáveis: {self.__n_var};\n
- Número de Restrições: {self.n_rest} \n
- Vetor de Custos: {self.cost_vector} \n
- Vetor de Resultados: {self.rest_results}\n
- Usar Simplex Dual? {self.getSimplexMode()} \n
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

    def __isOptimal__(self) -> bool:
        for i in self.__lp.cost_vector:
            if i >= 0:
                return False
        else:
            return True

    def __findMaxCostIndex__(self) -> int:
        maxItem = np.amax(self.__lp.cost_vector)
        indexMax = np.where(self.__lp.cost_vector == maxItem)[0][0]
        return indexMax

    def __findMinFormCol__(self, column: np.ndarray) -> int:
        result = column / self.__lp.rest_results
        small = result[0]
        small_idx = 0

        for idx, element in enumerate(self.__lp.rest_results):
            if element > 0:
                if result[idx] < small:
                    small = result[idx]
                    small_idx = idx

        return (small, small_idx)

    def __pivot__(self, iMax: int) -> None:
        '''
        @TODO Encontrar indice do maior elemento do vetor de custos; ok
        @TODO Encontrar, na coluna do maior elemento b que minimiza: b/A_jk, A_jk > 0. ok
        @TODO Divide aquela linha toda pelo valor do elemento b; ok

        @TODO zerar a coluna:(fazer copia da linha de b, somar a linha do outro elemento com -1 * valor do elemento da coluna de b); ok
        '''

        # Pego a coluna referente às restrições
        ColumnCopy = self.__lp.rest_M[:, iMax]
        
        # Descubro qual restrição deverá ser pivoteada
        small, small_idx = self.__findMinFormCol__(ColumnCopy)

        # Pivoteio a resrtição (no caso, deixo o valor como 1.)
        self.__lp.rest_M[small_idx] = self.__lp.rest_M[small_idx] / small
        
        self.__VERO[small_idx] = self.__VERO[small_idx] / small  # Espelhando as operações no VERO

        for i in range(self.__lp.n_rest):
            if i != small_idx:
                toBeNull = self.__lp.rest_M[i][iMax]
                
                self.__lp.rest_M[i] = self.__lp.rest_M[i] + (-1 * toBeNull * self.__lp.rest_M[i])
                self.__lp.rest_results[i] = self.__lp.rest_results[i] + (-1 * toBeNull * self.__lp.rest_results[i])
                self.__VERO[i] = self.__VERO[i] + (-1 * toBeNull * self.__VERO[i])
                self.__lp.rest_results
                print(self.__lp)
                input('Pressione Qualquer tecla para continuar...')

        toBeNull = self.__lp.cost_vector[iMax]
        self.__lp.cost_vector[iMax] = self.__lp.cost_vector[iMax] + (-1 * toBeNull * self.__lp.cost_vector[iMax])


    def __startVero__(self) -> None:
        self.__VERO = np.zeros((self.__lp.n_rest, self.__lp.n_rest))

        for i in range(self.__lp.n_rest):
            self.__VERO[i][i] = 1

    def runSimplex(self) -> None:
        self.__startVero__()

        while not self.__isOptimal__():
            iMax = self.__findMaxCostIndex__()
            self.__pivot__(iMax)

    def dualSimplex(self):
        pass
