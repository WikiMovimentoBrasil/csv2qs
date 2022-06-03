# -*- coding: utf-8 -*-
import pandas as pd
import re
import urllib.parse
import requests


def tipo_dado(declaracoes):
    """ (lis) -> dict
    Recebe uma lista com as declarações que serão usadas e retorna um dicionário com o tipo de valor
    aceito para cada declaração

    :param list declaracoes: Lista com as declarações que serão usadas
    :return dict dicionario: Dicionário com os valores aceitos pelas declarações
    """

    dicionario = {}
    for statement in declaracoes:

        # retorna o tipo de valor da declaração
        if re.match(r'P\d+|qal\d+|S\d+|s\d+', statement):
            statement = re.sub(r'qal|S|s', 'P', statement)
            statement = re.sub(r'\..*', '', statement)

            if statement not in dicionario:
                print(f'Verificando {statement}')
                S = requests.Session()
                URL = "https://wikidata.org/w/api.php?"
                PARAMS = {
                    "action": "wbgetentities",
                    "ids": statement,
                    "format": "json"
                }
                R = S.get(url=URL, params=PARAMS)
                DATA = R.json()
                tipo = DATA["entities"][statement]["datatype"]
                dicionario[statement] = tipo

        elif statement == 'qid':
            dicionario[statement] = 'wikibase-item'

        elif re.match(r'L|D|A|S.*', statement):
            dicionario[statement] = 'string'

        else:
            print(f'O valor indicado "{statement}" não é uma declaração válida!')

    return dicionario


def create(qid, statement, value, datatype):
    """(str, str, str, dict) -> str
    Verifica se o valor fornecido é válido e constroi o QS

    :param str qid: QID fornecido
    :param str statement: Declaração fornecida
    :param str value: Valor fornecido
    :param dict datatype: Dicionário com os tipos de valores para as declarações
    :return str result: QS
    """
    source = False
    if re.match(r'S\d+|s\d+', statement):
        source = True

    qualifier = False
    if re.match(r'qal\d+', statement):
        qualifier = True

    if re.match(r'qal\d+|S\d+|s\d+', statement):
        statement = re.sub(r'qal|S|s', 'P', statement)

    # tipo de dado
    tipo = datatype[statement]
    
    if tipo == 'wikibase-item' or tipo == 'time':
        result = value

    elif tipo == 'monolingualtext':
        result = re.sub(r':(.*)', ':"\\1"', value)

    else:
        result = f'"{value}"'
    
    if source:
        statement = re.sub(r'P', 'S', statement)
        return f'|{statement}|{result}'

    elif qualifier:
        return f'|{statement}|{result}'

    else:
        return f'{qid}|{statement}|{result}'


def main():
    """() -> None
    Executa o script
    :return: None
    """
    
    # Cria dataframe
    df = pd.read_csv('data.csv')
    colunas = df.columns
    data_type = tipo_dado(colunas)

    # Escreve o QS
    QS = ''
    for linha in range(0, len(df.index)):

        # Define se irá criar ou editar um item no Wikidata com base na coluna qid
        QID = df.loc[linha, 'qid']
        if pd.notna(QID):
            if re.match(r'Q\d+', QID):
                QID = f'||{QID}'
            else:
                print(f'QID inválido: {QID}')
        else:
            QS += '||CREATE'
            QID = '||LAST'

        # obtém o valor em cada coluna da linha
        for i in range(0, len(colunas)):
            declaracao = colunas[i]

            # Ignora a coluna qid e verifica as outras colunas
            if declaracao != 'qid':
                declaracao = re.sub(r'\..*', '', declaracao)
                valor = df.iloc[linha, i]

                # se não é um valor nan o comando é criado
                if pd.notna(valor):
                    valor = str(valor)
                    payload = create(QID, declaracao, valor, data_type)
                    QS += payload

    # Encode url
    toolforge = 'https://quickstatements.toolforge.org/#/v1='
    encode = urllib.parse.quote(QS, safe='')
    print(f'{toolforge}{encode}')
    print("\n")
    print(QS)


if __name__ == "__main__":
    main()
