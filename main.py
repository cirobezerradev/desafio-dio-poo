from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self._contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._cpf = cpf
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf

    @property
    def data_nascimento(self):
        return self._data_nascimento

    def __str__(self):
        contas_fmt = "\n\t".join(str(conta.numero) for conta in self._contas)\
            or "(sem contas)"
        return \
            f"Nome: {self.nome}\nCPF: {self.cpf}\n"\
            f"Data de Nascimento: {self.data_nascimento}\n"\
            f"Endereço: {self._endereco}\n"\
            f"Contas: \n\t{contas_fmt}"


class Conta:

    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, numero: int, cliente: Cliente):
        return cls(numero, cliente)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor: float) -> bool:
        saldo = self._saldo
        saldo_insuficiente = valor > saldo

        if saldo_insuficiente:
            print("\n Transação falhou! Saldo insuficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso!")
            return True

        else:
            print("Transação Falhou! O Valor informado é inválido.")

        return False

    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self._saldo += valor
            print(" Depósito realizado com sucesso")
            return True

        else:
            print("Transação Falhou! O Valor informado é inválido.")

        return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500.0, limite_saque=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saque

    def sacar(self, valor):
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self._limite
        excedeu_saque = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("Transação Falhou! O valor de saque excedeu o limite.")
        elif excedeu_saque:
            print("Transação Falhou! Excedeu o limte de saques diário.")
        elif valor > 0:
            return super().sacar(valor)
        else:
            print("Transação Falhou! O Valor informado é inválido.")

        return False

    def __str__(self):
        return f"""\
            \nAgência: {self.agencia}
            C\\C: {self.numero}
            Titular: {self.cliente.nome}
            """


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(conta: Conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        sucesso = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_trasacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        sucesso = conta.depositar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao: Transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )


def cadastrar_usuario(clientes: list[Cliente]):

    print("\n================ CRIAR USUÁRIO ================\n\n")
    nome = input("Digite o nome do usuário: ")
    data_nascimento = input("Digite a data de nascimento dd/mm/yyyy: ")
    cpf = input("Digite o CPF: ")
    if any(cliente.cpf == cpf for cliente in clientes):
        print(
            "\nNão foi possível realizar o cadastro!\n"
            "Esse usuário já foi cadastrado anteriormente."
        )
        return
    endereco = input("Digite o endereço: ")

    return clientes.append(PessoaFisica(nome, cpf, data_nascimento, endereco))


def listar_usuarios(clientes: list[Cliente]):
    print(8*"=", " USUÁRIOS CADASTRADOS ", 8*"=")

    if not clientes:
        print("Nenhum usuário cadastrado")
        print(37 * "=")
        return

    for i, cliente in enumerate(clientes, start=1):
        print(f"Usuário: {i}")
        print(cliente)
        print(37 * "=")


def criar_conta(clientes: list[Cliente], contas: list[Conta]):
    print("\n================ CRIAR CONTA ================\n\n")
    # Numero da conta é definido autoincrementando
    numero = str(len(contas) + 1)
    cpf = input("Digite um CPF de usuário cadastrado: ")

    if any(cliente.cpf == cpf for cliente in clientes):
        cliente = [cliente for cliente in clientes if cliente.cpf == cpf]
        conta = ContaCorrente.nova_conta(numero, cliente[0])
        contas.append(conta)
        cliente[0].adicionar_conta(conta)

        print(
            f"\nConta número: {numero} de {cliente[0].nome} - "
            f"CPF: {cliente[0].cpf} cadastrada com sucesso!"
        )
    else:
        print(
            f"\nNão foi possível criar a conta. "
            f"Não existe usuário cadastrado com o CPF - {cpf} informado."
        )


def listar_contas(contas: list[Conta]):
    print(8*"=" + " Lista Contas Cadastradas " + 8*"=")

    if not contas:
        print("Nenhuma conta criada!")

    for conta in contas:
        print(conta)
        print(42*"-")

    print(42*"=")


def menu():
    opcoes = """
[1] Cadastrar Usuário
[2] Listar Usuários Cadastrados
[3] Criar Conta
[4] Listar Contas
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """
    opcao = input(opcoes)

    return opcao


def main():
    clientes = []
    contas = []

    while True:

        opcao = menu().lower()

        if opcao == "1":
            cadastrar_usuario(clientes)

        elif opcao == "2":
            listar_usuarios(clientes)

        elif opcao == "3":
            criar_conta(clientes, contas)

        elif opcao == "4":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print(
                "Operação inválida, por favor selecione "
                "novamente a operação desejada."
            )


if __name__ == "__main__":
    main()
