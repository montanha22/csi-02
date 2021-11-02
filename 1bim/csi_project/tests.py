from plots import get_df_acidentes, get_df_vendas

FAIL = '\033[91m'
OKGREEN = '\033[92m'
ENDC = '\033[0m'

def print_error(msg):
    print(f"\t{FAIL}{msg}{ENDC}")

def print_success(msg):
    print(f"\t{OKGREEN}{msg}{ENDC}")

def test_get_acidentes():
    df_acidentes = None
    try:
        df_acidentes = get_df_acidentes(2021, 1, 2021, 5)
        print_success(f"Dataset de acidentes adquirido com sucesso. {len(df_acidentes)} linhas encontradas")
    except Exception as e:
        print_error(f"erro ao adquirir o dataset de acidentes: {e}")

def test_get_vendas():
    df_vendas = None
    try:
        df_vendas = get_df_vendas(2021, 1, 2021, 5)
        print_success(f"Dataset de vendas adquirido com sucesso. {len(df_vendas)} linhas encontradas")
    except Exception as e:
        print_error(f"erro ao adquirir o dataset de acidentes: {e}")

if __name__ == "__main__":
    print("\n\n\nIniciando testes")
    test_get_acidentes()
    test_get_vendas()
    print("Fim dos testes\n\n\n\n")