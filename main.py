import flet as ft
import csv
import os

def main(page: ft.Page):
    # --- CONFIGURAÇÃO VISUAL ---
    page.title = "Posto Controle"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#1f1f1f"

    # Cores
    COR_FUNDO = "#1f1f1f"
    COR_CARD = "#2d2d2d"
    COR_DESTAQUE = "#007bff" # Azul
    COR_ERRO = "#ff4d4d"

    # --- MAPEAMENTO DOS TANQUES (A Lógica do Posto) ---
    # AJUSTADO CONFORME SUA FOTO DA PASTA ASSETS
    CONFIG_TANQUES = {
        "T01 - Diesel S500": "tabela_tanque(in).csv",
        "T02A - Diesel S10 (Lado A)": "tabela_tanque(in).csv",
        "T02B - Diesel S10 (Lado B)": "tabela_tanque(in).csv",
        "T04 - Gas. Aditivada": "tabela_15000L 1(in).csv",
        "T05 - Gas. Comum": "tabela_30000L(in).csv",
        "📊 SOMA TOTAL S10 (A+B)": "tabela_tanque(in).csv"
    }

    banco_dados = {}

    # --- 1. CARREGAR ARQUIVOS ---
    def carregar_dados():
        pasta_assets = "assets"
        if not os.path.exists(pasta_assets):
            return

        for arquivo in os.listdir(pasta_assets):
            # O sistema vai tentar ler qualquer CSV que encontrar
            if arquivo.lower().endswith(".csv"):
                caminho = os.path.join(pasta_assets, arquivo)
                try:
                    dados_tanque = {}
                    # Encoding utf-8-sig para ler acentos e símbolos corretamente
                    with open(caminho, mode='r', encoding='utf-8-sig') as f:
                        leitor = csv.reader(f, delimiter=';')
                        next(leitor, None) # Pula cabeçalho
                        for linha in leitor:
                            if len(linha) >= 2:
                                try:
                                    cm = int(linha[0])
                                    litros = int(float(linha[1].replace('.', '').replace(',', '.')))
                                    dados_tanque[cm] = litros
                                except: continue
                    if dados_tanque:
                        # Guarda no banco de dados com o nome EXATO do arquivo
                        banco_dados[arquivo] = dados_tanque
                        print(f"Carregado: {arquivo}")
                except: pass
    carregar_dados()

    # --- 2. LÓGICA DO SISTEMA ---
    
    def mudar_dropdown(e):
        opcao = dropdown_tanques.value
        # Se escolher a opção de SOMA, mostra o segundo campo
        if "SOMA TOTAL" in opcao:
            txt_regua_2.visible = True
            txt_regua_1.label = "Régua T02A (cm)"
            btn_calcular.text = "CALCULAR TOTAL"
        else:
            txt_regua_2.visible = False
            txt_regua_1.label = "Régua (cm)"
            btn_calcular.text = "CONSULTAR"
        
        # Limpa resultados antigos
        card_resultado.visible = False
        page.update()

    def calcular(e):
        opcao = dropdown_tanques.value
        if not opcao: return

        # Pega o nome do arquivo correspondente à escolha
        arquivo_csv = CONFIG_TANQUES.get(opcao)
        tabela = banco_dados.get(arquivo_csv)

        if not tabela:
            lbl_total.value = "Erro: Arquivo CSV não achado"
            lbl_detalhe.value = f"Procurando: {arquivo_csv}"
            card_resultado.visible = True
            page.update()
            return

        try:
            # Lógica Especial para Soma (T02A + T02B)
            if "SOMA TOTAL" in opcao:
                cm_a = int(txt_regua_1.value)
                cm_b = int(txt_regua_2.value)
                
                vol_a = tabela.get(cm_a, 0)
                vol_b = tabela.get(cm_b, 0)
                total = vol_a + vol_b

                lbl_detalhe.value = f"Lado A: {vol_a} L  |  Lado B: {vol_b} L"
                lbl_total.value = f"{total} Litros"
                lbl_desc.value = "Total Sistema S10"
            
            # Lógica Normal (Individual)
            else:
                cm = int(txt_regua_1.value)
                vol = tabela.get(cm)
                
                if vol is not None:
                    lbl_total.value = f"{vol} Litros"
                    lbl_detalhe.value = f"Tanque: {opcao.split(' - ')[0]}"
                    lbl_desc.value = "Volume em Estoque"
                else:
                    lbl_total.value = "Não Tabelado"
                    lbl_detalhe.value = "Verifique a régua"

            card_resultado.visible = True
            lbl_total.color = COR_DESTAQUE

        except ValueError:
            lbl_total.value = "Digite apenas números"
            lbl_total.color = COR_ERRO
            card_resultado.visible = True
        
        page.update()

    # --- 3. INTERFACE VISUAL ---
    
    titulo = ft.Text("Controle de Tanques", size=24, weight="bold", color="white")
    
    dropdown_tanques = ft.Dropdown(
        label="Selecione o Tanque",
        options=[ft.dropdown.Option(nome) for nome in CONFIG_TANQUES.keys()],
        on_change=mudar_dropdown,
        color="white",
        border_color="white",
        bgcolor=COR_CARD
    )

    txt_regua_1 = ft.TextField(
        label="Régua (cm)", 
        keyboard_type=ft.KeyboardType.NUMBER,
        color="white",
        border_color="white",
        text_align="center"
    )

    txt_regua_2 = ft.TextField(
        label="Régua T02B (cm)", 
        keyboard_type=ft.KeyboardType.NUMBER,
        visible=False, # Começa invisível
        color="white",
        border_color="white",
        text_align="center"
    )

    btn_calcular = ft.ElevatedButton(
        text="CONSULTAR",
        width=300,
        height=50,
        bgcolor=COR_DESTAQUE,
        color="white",
        on_click=calcular
    )

    # Card de Resultado
    lbl_desc = ft.Text("Resultado", color="grey")
    lbl_total = ft.Text("-", size=40, weight="bold", color=COR_DESTAQUE)
    lbl_detalhe = ft.Text("-", color="white")

    card_resultado = ft.Container(
        content=ft.Column([
            lbl_desc,
            lbl_total,
            ft.Divider(color="grey"),
            lbl_detalhe
        ], horizontal_alignment="center"),
        bgcolor=COR_CARD,
        padding=20,
        border_radius=15,
        visible=False,
        width=300
    )

    page.add(
        ft.Column([
            titulo,
            ft.Divider(color="grey"),
            ft.Container(height=10),
            dropdown_tanques,
            ft.Container(height=10),
            txt_regua_1,
            txt_regua_2,
            ft.Container(height=20),
            btn_calcular,
            ft.Container(height=20),
            card_resultado
        ], horizontal_alignment="center")
    )

ft.app(target=main, assets_dir="assets")
