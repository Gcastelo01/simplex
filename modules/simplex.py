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

        self.n_var = nVars
        self.n_rest = nRest
        self.cost_vector = costV
        self.rest_M = resM
        self.rest_results = np.zeros([nRest], dtype=np.float128)
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
- Número de variáveis: {self.n_var};\n
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
        self.__certificate = np.zeros(lp.n_rest, dtype=np.float128)
        self.__objValue = 0
        self.__baseVars = []
        self.__possibleResult = np.zeros(lp.n_var)
        self.__kind = 'otima'
        self.__isDual = False

    def __isOptimal__(self) -> bool:
        for i in self.__lp.cost_vector:
            if i > 0:
                return False
        else:
            return True

    def __checkIlimited__(self, indexToTest) -> bool:
        """
        Sempre que todos os coeficientes da coluna correspondente de uma variavel candidata forem não-positivos (ou sejam negativos ou zero), a PL é ilimitada.
        """
        toBeTested = self.__lp.rest_M[:, indexToTest]

        for i in toBeTested:
            if i > 0: 
                return False

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

        # Pivoteio a restrição (no caso, deixo o valor como 1.)
        self.__lp.rest_M[small_idx] /= small
        # Repetindo a operação no vetor de resultados
        self.__lp.rest_results[small_idx] /= small
        # Repetindo a operação no VERO
        self.__VERO[small_idx] /= small

        # Zerando Colunas acima e abaixo do valor Pivoteado, na matriz de Restrições.
        for i in range(self.__lp.n_rest):
            if i != small_idx:
                toBeNull = self.__lp.rest_M[i][iMax]
                self.__lp.rest_M[i] -= (toBeNull * self.__lp.rest_M[small_idx])
                self.__lp.rest_results[i] -= (toBeNull * self.__lp.rest_results[small_idx])
                self.__VERO[i] -= (toBeNull * self.__VERO[small_idx]) # Repetindo no VERO
                

        toBeNull = self.__lp.cost_vector[iMax]  # Pegando o valor do elemento do vetor de custos a ser anulado.

        self.__lp.cost_vector -= (toBeNull * self.__lp.rest_M[small_idx])  # Anulando o vetor de custos no ponto.

        self.__certificate -= (toBeNull * self.__VERO[small_idx])  # Repetindo as operações no VERO e no certificado;
    
        self.__objValue -= (self.__lp.rest_results[small_idx] * toBeNull)  # Atualizando valor

    def __startVero__(self) -> None:
        self.__VERO = np.zeros((self.__lp.n_rest, self.__lp.n_rest))

        for i in range(self.__lp.n_rest):
            self.__VERO[i][i] = 1

    def __getPossible__(self, idx: int) -> int:
        """
        @brief Verifica se um determinado valor arbitrário é parte de uma base de soluções viáveis
        """
        col = self.__lp.rest_M[:, idx]
        for idx, i in enumerate(col):
            if i == 1:
                return self.__lp.rest_results[idx]
        else:
            return 'none'

    def runSimplex(self) -> None:
        """
        @brief Roda o Algoritmo Simplex para a PL parâmetro. Esta chamada automaticamente determina a necessidade de gerar uma PL auxiliar, de rodar o simplex dual ou quaisquer outros ajustes.
        """
        
        # Começa a matriz de registro de operações.
        self.__startVero__()
        
        # Enquanto a matriz não for ótima, escolho um elemento e pivoteio.
        while not self.__isOptimal__():
            iMax = self.__findMaxCostIndex__()
            if self.__checkIlimited__(iMax):
                self.__kind = 'ilimitada'
                break
            self.__pivot__(iMax)
          
        # Invertendo o valor objetivo
        self.__objValue = self.__objValue * -1
        
        # Invertendo o valor do vetor certificado
        self.__certificate = self.__certificate * -1

        for i in self.__lp.rest_results:
          if i < 0:
            self.__isDual = True

        if self.__isDual: self.__runDual__()

        if self.__objValue < 0:
          self.__kind = 'inviavel'
          pass
        
        
        if self.__kind == 'otima':
          for i in range(self.__lp.n_var):
              if(self.__lp.cost_vector[i] == 0):
                  self.__possibleResult[i] = self.__getPossible__(i)
              else: 
                  self.__possibleResult[i] = 0
        
        # Se a PL for ilimitada, cria um vetor com um resultado possível.
        if self.__kind == 'ilimitada':
            self.__certificate = self.__certificate * -1
            for i in range(self.__lp.n_var):
                if(self.__lp.cost_vector[i] == 0):
                    self.__possibleResult[i] = self.__getPossible__(i)
                else: 
                    self.__possibleResult[i] = 0
    
    def __runDual__(self) -> None:
      
      
    def testCertificate(self):
      if self.__kind == 'otima':
        y = self.__certificate
        b = self.__lp.rest_results
        c = self.__lp.cost_vector
        z = self.__lp.rest_results
        print(f"Vetor de Custo: {c[self.__lp.n_var:].T}\n yTb: {y.T @ b}\n cTz: {c[self.__lp.n_var:].T @ z} \n z: {z}")
        
    def __str__(self) -> str:
        if self.__kind == 'otima':
            a = f"""
        1. {self.__kind}
        2. {self.__objValue}
        4. {self.__possibleResult}
        3. {self.__certificate}

        """

        elif self.__kind == 'ilimitada':
            a = f"""
        1. {self.__kind}
        2. {self.__possibleResult}
        3. {self.__certificate}

        """
        
        else:
          a = f"""
        1. {self.__kind}
        3. {self.__certificate}
          """

        return a
