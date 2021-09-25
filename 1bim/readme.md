# Projeto CSI-02

## O que é o projeto?

A versão atual do projeto consiste em um site/aplicação capaz de buscar informações sobre vendas de veículos e sobre acidentes de trânsitos em 2 diferentes fontes: aplicação SOAP do banco central e API rest do site de dados abertos de Porto Alegre.

## Como rodar o projeto? - Windows

Na pasta 1bim, seguir o passo a passo:

1. Configurar um ambiente virtual para a instalação dos módulos python.

```{cmd}
py -m venv venv
```

2. Ativar o venv

```{cmd}
.\venv\Scripts\activate
```

3. Instalar módulos necessários

```{cmd}
py -m pip install -r requirements.txt
```

4. Configurar variável de ambiente para o Flask

```{cmd}
$env:FLASK_APP = "runserver.py"
```

5. Rodar o script de inicialização

```{cmd}
py .\runserver.py
```

## Qual é a estrutura do projeto?

A maior parte do código está na pasta [csi_project](./csi_project).

Nela temos o script [\_\_init\_\_.py](./csi_project/__init__.py) que possui a função responsável por criar a instância da aplicação. A aplicação raiz é composta por aplicações modulares chamadas blueprints. Como o projeto ainda é pequeno, só existe uma única blueprint no momento, a main_app.

A main_app é a aplicação responsável pelas páginas de boas vindas e a página de visualizações. Dentro do script [main_app.py](./csi_project/main_app.py) temos as definições das rotas da aplicação principal, além de rotas para aquisição dos gráficos.

Por fim, os templates html ficam na pasta de templates e os arquivos de estilização e outros arquivos estáticos ficam na pasta static.