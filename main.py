import flet as ft
import csv
import os
import traceback # Para mostrar o erro na tela se houver

def main(page: ft.Page):
    # --- CONFIGURAÇÃO VISUAL ---
    page.title = "Posto Controle"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.bgcolor = "#1f1f1f"
    page.scroll = "AUTO" # Permite rolar a tela se tiver erro grande

    # Lista MANUAL dos arquivos (Mais seguro para Android)
    ARQUIVOS_CONHECIDOS = [
        "tabela_tanque(in).csv",
        "tabela_15000L 1(in).csv",
        "tabela_30000L(in).csv"
    ]

    # Configuração dos Tanques
    CONFIG_TANQUES = {
        "T01 - Diesel S500": "tabela_tanque(in).csv",
        "T02A - Diesel S10 (Lado A)": "tabela_tanque(in).csv",
        "T02B - Diesel S10 (Lado B)": "tabela_tanque(in).csv",
        "T04 - Gas. Aditivada": "tabela_15000L 1(in).csv",
        "T05 - Gas. Comum": "tabela_30000L(in).csv",
        "📊 SOMA TOTAL S10 (A+B)": "tabela_tanque(in).csv"
    }

    banco_dados = {}
    
    # Área de texto para mostrar mensagens de debug/erro
    txt_debug = ft.Text("", color="red", size=14)

    # --- 1. CARREGAR ARQUIVOS (MÉTODO SEGURO) ---
    def carregar_dados():
        try:
            # Tenta descobrir onde o script está rodando
            caminho_base = os.path.dirname(__file__)
            pasta_assets = os.path.join(caminho_base, "assets")
            
            # Se não achar do jeito normal, tenta direto na pasta local
            if not os.path.exists(pasta_assets):
                pasta_assets = "assets"

            arquivos_carregados = 0

            for nome_arquivo in ARQUIVOS_CONHECIDOS:
                caminho = os.path.join(pasta_assets, nome_arquivo)
                
                try:
                    dados_tanque = {}
                    # Encoding utf-8-sig para ler acentos e símbolos
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
                        banco_dados[nome_arquivo] = dados_tanque
                        arquivos_carregados += 1
                except Exception as e_file:
                    print(f"Erro ao ler {nome_arquivo}: {e_file}")
            
            if arquivos_carregados == 0:
                txt_debug.value = f"ALERTA: Nenhum arquivo carregado. Pasta buscada: {pasta_assets}"
                
        except Exception as e:
            txt_debug.value = f"ERRO GERAL: {traceback.format_exc()}"
            page.update()

    # Tenta carregar e mostra erro se falhar
    carregar_dados()

    # --- 2. LÓGICA DO SISTEMA ---
    def mudar_dropdown(e):
        opcao = dropdown_tanques.value
        if "SOMA TOTAL" in opcao:
            txt_regua_2.visible = True
            txt_regua_1.label = "Régua T02A (cm)"
            btn_calcular.text = "CALCULAR TOTAL"
        else:
            txt_regua_2.visible = False
            txt_regua_1.label = "Régua (cm)"
            btn_calcular.text = "CONSULTAR"
        card_resultado.visible = False
        page.update()

    def calcular(e):
        opcao = dropdown_tanques.value
        if not opcao: return

        arquivo_csv = CONFIG_TANQUES.get(opcao)
        tabela = banco_dados.get(arquivo_csv)

        if not tabela:
            lbl_total.value = "Erro: Tabela não carregada"
            lbl_detalhe.value = f"Arquivo {arquivo_csv} falhou"
            card_resultado.visible = True
            page.update()
            return

        try:
            if "SOMA TOTAL" in opcao:
                cm_a = int(txt_regua_1.value)
                cm_b = int(txt_regua_2.value)
                vol_a = tabela.get(cm_a, 0)
                vol_b = tabela.get(cm_b, 0)
                total = vol_a + vol_b
                lbl_detalhe.value = f"A: {vol_a} L | B: {vol_b} L"
                lbl_total.value = f"{total} L"
                lbl_desc.value = "Total Sistema"
            else:
                cm = int(txt_regua_1.value)
                vol = tabela.get(cm)
                if vol is not None:
                    lbl_total.value = f"{vol} L"
                    lbl_detalhe.value = "Estoque Físico"
                    lbl_desc.value = "Volume"
                else:
                    lbl_total.value = "Não Tabelado"
                    lbl_detalhe.value = "Verifique a régua"

            card_resultado.visible = True
            lbl_total.color = "#007bff"

        except ValueError:
            lbl_total.value = "Use apenas números"
            lbl_total.color = "#ff4d4d"
            card_resultado.visible = True
        
        page.update()

    # --- 3. INTERFACE VISUAL ---
    dropdown_tanques = ft.Dropdown(
        label="Selecione o Tanque",
        options=[ft.dropdown.Option(nome) for nome in CONFIG_TANQUES.keys()],
        on_change=mudar_dropdown,
        color="white", border_color="white", bgcolor="#2d2d2d"
    )

    txt_regua_1 = ft.TextField(label="Régua (cm)", keyboard_type=ft.KeyboardType.NUMBER, color="white", border_color="white", text_align="center")
    txt_regua_2 = ft.TextField(label="Régua T02B (cm)", keyboard_type=ft.KeyboardType.NUMBER, visible=False, color="white", border_color="white", text_align="center")

    btn_calcular = ft.ElevatedButton(text="CONSULTAR", width=300, height=50, bgcolor="#007bff", color="white", on_click=calcular)

    lbl_desc = ft.Text("Resultado", color="grey")
    lbl_total = ft.Text("-", size=40, weight="bold", color="#007bff")
    lbl_detalhe = ft.Text("-", color="white")

    card_resultado = ft.Container(
        content=ft.Column([lbl_desc, lbl_total, ft.Divider(color="grey"), lbl_detalhe], horizontal_alignment="center"),
        bgcolor="#2d2d2d", padding=20, border_radius=15, visible=False, width=300
    )

    page.add(
        ft.Column([
            ft.Text("Controle de Tanques", size=24, weight="bold", color="white"),
            txt_debug, # <--- SE TIVER ERRO, VAI APARECER AQUI
            ft.Divider(color="grey"),
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
