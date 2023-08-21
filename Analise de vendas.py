# IMPORTANDO DADOS DO SISTEMA DA LOJA

import requests
import pandas as pd
from pandas import json_normalize
import json

BLING_SECRET_KEY = "{chave api}"


def list_products(page=1):
    url = f'https://bling.com.br/Api/v2/pedidos/page={page}/json/'
    payload = {'apikey': BLING_SECRET_KEY, }
    all_products = {'retorno': {'pedidos': []}}

    for i in range(150):
        page = i+1
        url = f'https://bling.com.br/Api/v2/pedidos/page={page}/json/'
        pedidos = requests.get(url, params=payload)
        try:
            pagina = pedidos.json()['retorno']['pedidos']
            for item in pagina:
                all_products['retorno']['pedidos'].append(item)
        except KeyError:

            break

    df = json_normalize(all_products, meta=['pedidos'])
    return df


pedidos = list_products()
df = pd.json_normalize(pedidos.explode('retorno.pedidos')['retorno.pedidos'])
df = df.explode("pedido.itens")
df.to_excel("pedidos expandido.xlsx", index = False)

# Expandindo itens
df1 = pd.json_normalize(df['pedido.itens'])
df1.to_excel("itens expandidos.xlsx", index = False)

# Unindo tabelas
df = pd.read_excel("pedidos expandido.xlsx")
df1 = pd.read_excel("itens expandidos.xlsx")
df2 = df.merge(df1, on="juntar")
df2.rename(columns={"item.codigo": "codigo"}, inplace=True)
df2.to_excel("pedidos itens.xlsx")

# IMPORTANDO PRODUTOS DO SISTEMA DA LOJA

BLING_SECRET_KEY = "{chave api}"


def list_products(page=1):
    url = f'https://bling.com.br/Api/v2/produtos/page={page}/json/'
    payload = {'apikey': BLING_SECRET_KEY, }
    all_products = {'retorno': {'produtos': []}}

    for i in range(150):
        page = i+1
        url = f'https://bling.com.br/Api/v2/produtos/page={page}/json/'
        produtos = requests.get(url, params=payload)
        try:
            pagina = produtos.json()['retorno']['produtos']
            for item in pagina:
                all_products['retorno']['produtos'].append(item)
        except KeyError:

            break

    df = json_normalize(all_products, meta=['produtos'])
    return df


produtos = list_products()
df = pd.json_normalize(produtos.explode('retorno.produtos')['retorno.produtos'])
#df = df.explode("produtos.itens")

df.to_excel("produtos.xlsx", index=False)

# UNINDO TABELAS
df2 = pd.read_excel("pedidos itens.xlsx")
df2 = df2[["pedido.data", "pedido.loja", "pedido.cliente.nome", "pedido.cliente.fone", "codigo", "item.descricao", "item.quantidade", "item.valorunidade","pedido.cliente.celular", "pedido.situacao"]]
df3 = pd.read_excel("produtos.xlsx")
df3 = df3[["produto.codigo", "produto.marca", "produto.categoria.descricao"]]
df3 = df3.dropna()
df3.rename(columns = {"produto.codigo":"codigo"}, inplace = True)
df4 = df2.merge(df3, how = "left", on = "codigo")

# filtrando situaçao
df4 = df4[df4["pedido.situacao"] == "Atendido"]

# tipo data
df4["pedido.data"] = pd.to_datetime(df4["pedido.data"])

# nome das lojas
# for i, item in enumerate(df4["pedido.loja"]):
#     if (item == 204208096) or (item == float(204208096)):
#             df4.loc[i, "pedido.loja"] = "VR"
#     elif (item == 203906560) or (item == float(203906560)):
#             df4.loc[i, "pedido.loja"] = "BM"
#     elif (item == 203553616) or (item == float(203553616)):
#             df4.loc[i, "pedido.loja"] = "SITE"
df4 = df4.dropna(subset=["pedido.data"])
df4.to_excel("pedidos itens completos.xlsx", index = False)

# ANALISE POR CATERGORIA
categoria = input("Qual categoria?")

df_cat = df4[df4["pedido.data"]>pd.Timestamp(2023,1,1)] # INFORME A DATA

df_cat = df_cat[df_cat["produto.categoria.descricao"] == categoria]
df_cat = df_cat.groupby(["pedido.cliente.nome", "pedido.cliente.fone", "produto.marca"]).sum()
df_cat = df_cat.drop("item.valorunidade", axis = 1)
display(df_cat)

marca = input("Qual marca?")

df_marca = df4[df4["pedido.data"]>pd.Timestamp(2023,1,1)] #INFORME A DATA

df_marca = df_marca[df_marca["produto.marca"] == marca]
df_marca = df_marca.groupby(["pedido.cliente.nome", "pedido.cliente.fone", "produto.categoria.descricao"]).sum()
df_marca = df_marca.drop("item.valorunidade", axis = 1)
display(df_marca)