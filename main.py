import flet as ft
import csv
import os

def main(page: ft.Page):
    page.title = "Conferencia"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    
    banco_dados = {}

    # --- 1. CARREGAR ARQUIVOS ---
    def carregar_dados():
        pasta_assets = "assets"
        if not os.path.exists(pasta_assets):
            os.makedirs(pasta_assets)
            return

        for arquivo in os.listdir(pasta_assets):
            if arquivo.lower().endswith(".csv"):
                caminho = os.path.join(pasta_assets, arquivo)
                try:
                    dados_tanque = {}
                    with open(caminho, mode='r', encoding='utf-8-sig') as f:
                        leitor = csv.reader(f, delimiter=';')
                        next(leitor, None)
                        for linha in leitor:
                            if len(linha) >= 2:
                                try:
                                    # Limpa pontos e converte
                                    val_cm = int(linha[0])
                                    val_litros = int(float(linha[1].replace('.', '').replace(',', '.')))
                                    dados_tanque[val_cm] = val_litros
                                except: continue
                    
                    if dados_tanque:
                        nome = arquivo.replace(".csv", "").upper()
                        banco_dados[nome] = dados_tanque
                except: pass
    carregar_dados()

    # --- 2. MENU ---
    opcoes_menu = []
    if banco_dados:
        for nome in banco_dados.keys():
            opcoes_menu.append(ft.dropdown.Option(nome))
    else:
        opcoes_menu.append(ft.dropdown.Option("Sem CSV na pasta assets"))

    # --- 3. LÓGICA ---
    def buscar_litros(e):
        nome_tanque = dropdown_tanques.value
        if not nome_tanque:
            lbl_resultado.value = "Selecione o tanque"
            lbl_resultado.color = "red" # Cor em texto simples
            page.update()
            return

        try:
            regua = int(txt_regua.value)
            # Busca segura no dicionário
            tabela = banco_dados.get(nome_tanque)
            
            if tabela:
                litros = tabela.get(regua)
                if litros is not None:
                    lbl_resultado.value = f"{litros} Litros"
                    lbl_resultado.color = "blue" # Cor em texto simples
                else:
                    lbl_resultado.value = "Nao encontrado"
                    lbl_resultado.color = "orange"
            else:
                lbl_resultado.value = "Erro na tabela"

        except:
            lbl_resultado.value = "Digite numeros"
            lbl_resultado.color = "red"
        
        page.update()

    # --- 4. TELA SIMPLIFICADA ---
    dropdown_tanques = ft.Dropdown(
        label="Tanque",
        options=opcoes_menu,
        width=300
    )

    txt_regua = ft.TextField(
        label="Regua (cm)", 
        width=300, 
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    # Botão no formato antigo (compatível com tudo)
    btn_calcular = ft.ElevatedButton(
        content=ft.Text("CONSULTAR"), 
        width=300, 
        height=50, 
        on_click=buscar_litros
    )
    
    lbl_resultado = ft.Text("---", size=40, weight=ft.FontWeight.BOLD)

    page.add(
        ft.Column([
            ft.Text("Controle de Estoque", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            dropdown_tanques,
            txt_regua,
            ft.Container(height=10),
            btn_calcular,
            ft.Divider(),
            lbl_resultado
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main, assets_dir="assets")