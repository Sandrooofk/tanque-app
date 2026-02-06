import flet as ft
import csv
import os

def main(page: ft.Page):
    # --- 1. CONFIGURAÇÃO INICIAL (Leve para não travar) ---
    page.title = "Posto Controle"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1f1f1f"
    page.padding = 20
    page.scroll = "AUTO"

    # Variáveis globais
    banco_dados = {}
    CONFIG_TANQUES = {
        "T01 - Diesel S500": "tabela_tanque(in).csv",
        "T02A - Diesel S10 (Lado A)": "tabela_tanque(in).csv",
        "T02B - Diesel S10 (Lado B)": "tabela_tanque(in).csv",
        "T04 - Gas. Aditivada": "tabela_15000L 1(in).csv",
        "T05 - Gas. Comum": "tabela_30000L(in).csv",
        "📊 SOMA TOTAL S10 (A+B)": "tabela_tanque(in).csv"
    }

    # --- 2. FUNÇÃO QUE CARREGA TUDO (Só roda quando clicar) ---
    def abrir_sistema(e):
        btn_entrar.text = "Carregando tabelas..."
        btn_entrar.disabled = True
        page.update()

        # Limpa a tela inicial
        page.clean()
        
        # Reconstrói a interface completa
        montar_interface_principal()
        
        # Carrega os dados
        carregar_dados_agora()

    # --- 3. LÓGICA DE CARREGAMENTO (Blindada) ---
    def carregar_dados_agora():
        try:
            # Pega o caminho confirmado pelo diagnóstico
            pasta_assets = os.path.join(os.getcwd(), "assets")
            if not os.path.exists(pasta_assets):
                # Tenta plano B
                pasta_assets = "assets"

            arquivos_lidos = 0
            
            # Lista exata dos seus arquivos
            lista_arquivos = [
                "tabela_tanque(in).csv",
                "tabela_15000L 1(in).csv",
                "tabela_30000L(in).csv"
            ]

            for nome in lista_arquivos:
                caminho = os.path.join(pasta_assets, nome)
                try:
                    dados_tanque = {}
                    if os.path.exists(caminho):
                        with open(caminho, mode='r', encoding='utf-8-sig') as f:
                            leitor = csv.reader(f, delimiter=';')
                            next(leitor, None)
                            for linha in leitor:
                                if len(linha) >= 2:
                                    try:
                                        c = int(linha[0])
                                        v = int(float(linha[1].replace('.', '').replace(',', '.')))
                                        dados_tanque[c] = v
                                    except: continue
                        if dados_tanque:
                            banco_dados[nome] = dados_tanque
                            arquivos_lidos += 1
                except: pass
            
            # Atualiza status na nova tela
            if arquivos_lidos > 0:
                txt_status.value = f"Sistema Online ({arquivos_lidos} tabelas)"
                txt_status.color = "green"
            else:
                txt_status.value = "Erro: Nenhuma tabela carregada"
                txt_status.color = "red"
            page.update()

        except Exception as ex:
            txt_status.value = f"Erro Geral: {str(ex)}"
            page.update()

    # --- 4. INTERFACE PRINCIPAL ---
    def montar_interface_principal():
        # Cabeçalho
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Controle de Estoque", size=22, weight="bold", color="white"),
                    txt_status
                ]),
                margin=ft.margin.only(bottom=10)
            )
        )
        
        # Adiciona os controles
        page.add(dropdown_tanques)
        page.add(ft.Container(height=10))
        page.add(txt_regua_1)
        page.add(container_soma) # Invisível por padrão
        page.add(ft.Container(height=20))
        page.add(btn_calcular)
        page.add(ft.Container(height=20))
        page.add(card_resultado)

    # --- 5. COMPONENTES (Definidos aqui para usar depois) ---
    txt_status = ft.Text("Carregando...", color="grey", size=12)

    def mudar_dropdown(e):
        op = dropdown_tanques.value
        if "SOMA" in op:
            container_soma.visible = True
            txt_regua_1.label = "Régua T02A (cm)"
            btn_calcular.text = "CALCULAR TOTAL"
        else:
            container_soma.visible = False
            txt_regua_1.label = "Régua (cm)"
            btn_calcular.text = "CONSULTAR"
        card_resultado.visible = False
        page.update()

    def calcular(e):
        op = dropdown_tanques.value
        if not op: return
        
        nome_arq = CONFIG_TANQUES.get(op)
        tab = banco_dados.get(nome_arq)
        
        if not tab:
            lbl_total.value = "Erro Tabela"
            card_resultado.visible = True
            page.update()
            return

        try:
            if "SOMA" in op:
                if not txt_regua_1.value or not txt_regua_2.value: return
                r1 = int(txt_regua_1.value)
                r2 = int(txt_regua_2.value)
                total = tab.get(r1, 0) + tab.get(r2, 0)
                lbl_total.value = f"{total} Litros"
                lbl_detalhe.value = f"A: {tab.get(r1,0)} | B: {tab.get(r2,0)}"
            else:
                if not txt_regua_1.value: return
                r1 = int(txt_regua_1.value)
                vol = tab.get(r1)
                if vol is not None:
                    lbl_total.value = f"{vol} Litros"
                    lbl_detalhe.value = "Estoque Físico"
                else:
                    lbl_total.value = "Não Tabelado"
                    lbl_detalhe.value = "-"
            
            card_resultado.visible = True
            page.update()
        except:
            lbl_total.value = "Erro Números"
            card_resultado.visible = True
            page.update()

    # Componentes Visuais
    dropdown_tanques = ft.Dropdown(
        label="Tanque", 
        options=[ft.dropdown.Option(x) for x in CONFIG_TANQUES.keys()],
        on_change=mudar_dropdown, color="white", bgcolor="#2d2d2d"
    )
    txt_regua_1 = ft.TextField(label="Régua (cm)", keyboard_type="NUMBER", color="white", text_align="center")
    txt_regua_2 = ft.TextField(label="Régua T02B (cm)", keyboard_type="NUMBER", color="white", text_align="center")
    container_soma = ft.Container(content=txt_regua_2, visible=False)
    
    btn_calcular = ft.ElevatedButton("CONSULTAR", bgcolor="blue", color="white", width=300, height=50, on_click=calcular)
    
    lbl_total = ft.Text("-", size=35, weight="bold", color="blue")
    lbl_detalhe = ft.Text("-", color="white")
    card_resultado = ft.Container(
        content=ft.Column([lbl_total, lbl_detalhe], horizontal_alignment="center"),
        bgcolor="#333333", padding=20, border_radius=10, visible=False
    )

    # --- TELA INICIAL (IGUAL AO DIAGNÓSTICO QUE FUNCIONOU) ---
    btn_entrar = ft.ElevatedButton(
        "ABRIR SISTEMA", 
        bgcolor="green", 
        color="white", 
        width=250, 
        height=60,
        on_click=abrir_sistema
    )

    page.add(
        ft.Column([
            ft.Icon(ft.icons.LOCAL_GAS_STATION, size=60, color="blue"),
            ft.Text("Posto Gestão", size=25, weight="bold", color="white"),
            ft.Container(height=30),
            btn_entrar,
            ft.Text("\nToque para iniciar", color="grey")
        ], horizontal_alignment="center", alignment="center")
    )

ft.app(target=main, assets_dir="assets")
