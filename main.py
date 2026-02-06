import flet as ft
import csv
import os

def main(page: ft.Page):
    # --- CONFIGURAÇÃO VISUAL ---
    page.title = "Posto Controle"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1f1f1f"
    page.padding = 20
    page.scroll = "AUTO"

    # --- NOMES EXATOS (Confirmados pelo Diagnóstico) ---
    ARQUIVO_60K = "tabela_tanque(in).csv"
    ARQUIVO_15K = "tabela_15000L 1(in).csv" # Atenção ao espaço antes do 1
    ARQUIVO_30K = "tabela_30000L(in).csv"

    # Mapa de qual tanque usa qual arquivo
    CONFIG_TANQUES = {
        "T01 - Diesel S500": ARQUIVO_60K,
        "T02A - Diesel S10 (Lado A)": ARQUIVO_60K,
        "T02B - Diesel S10 (Lado B)": ARQUIVO_60K,
        "T04 - Gas. Aditivada": ARQUIVO_15K,
        "T05 - Gas. Comum": ARQUIVO_30K,
        "📊 SOMA TOTAL S10 (A+B)": ARQUIVO_60K
    }

    # Memória do app
    banco_dados = {}
    
    # Campo para avisos (caso algum arquivo falhe)
    txt_status = ft.Text("Sistema pronto.", color="grey", size=12)

    # --- 1. FUNÇÃO DE CARREGAMENTO (Executada DEPOIS da tela abrir) ---
    def carregar_arquivos_seguro():
        try:
            # Pega a pasta atual (confirmado pelo diagnóstico)
            pasta_assets = os.path.join(os.getcwd(), "assets")
            
            arquivos_encontrados = 0
            erros_leitura = []

            # Lista única de arquivos para carregar
            lista_arquivos = [ARQUIVO_60K, ARQUIVO_15K, ARQUIVO_30K]

            for nome_arquivo in lista_arquivos:
                caminho = os.path.join(pasta_assets, nome_arquivo)
                
                try:
                    dados_tanque = {}
                    # Tenta abrir (utf-8-sig para acentos)
                    if os.path.exists(caminho):
                        with open(caminho, mode='r', encoding='utf-8-sig') as f:
                            # Tenta ler com ponto e vírgula
                            leitor = csv.reader(f, delimiter=';')
                            next(leitor, None) # Pula cabeçalho
                            
                            for linha in leitor:
                                if len(linha) >= 2:
                                    try:
                                        cm = int(linha[0])
                                        # Trata 1.000 ou 1000,00
                                        litros = int(float(linha[1].replace('.', '').replace(',', '.')))
                                        dados_tanque[cm] = litros
                                    except: continue
                        
                        if dados_tanque:
                            banco_dados[nome_arquivo] = dados_tanque
                            arquivos_encontrados += 1
                        else:
                            erros_leitura.append(f"{nome_arquivo} (Vazio)")
                    else:
                        erros_leitura.append(f"{nome_arquivo} (Não achado)")

                except Exception as e:
                    erros_leitura.append(f"{nome_arquivo} (Erro: {str(e)})")

            # Atualiza o status na tela
            if erros_leitura:
                txt_status.value = f"Alerta: Problema em {', '.join(erros_leitura)}"
                txt_status.color = "orange"
            else:
                txt_status.value = f"Sucesso! {arquivos_encontrados} tabelas carregadas."
                txt_status.color = "green"
            
            page.update()

        except Exception as e:
            txt_status.value = f"Erro Geral: {str(e)}"
            txt_status.color = "red"
            page.update()

    # --- 2. LÓGICA DE CÁLCULO ---
    def mudar_dropdown(e):
        opcao = dropdown_tanques.value
        if "SOMA TOTAL" in opcao:
            container_soma.visible = True
            txt_regua_1.label = "Régua T02A (cm)"
            btn_calcular.text = "CALCULAR TOTAL SISTEMA"
        else:
            container_soma.visible = False
            txt_regua_1.label = "Régua (cm)"
            btn_calcular.text = "CONSULTAR VOLUME"
        
        card_resultado.visible = False
        page.update()

    def calcular(e):
        opcao = dropdown_tanques.value
        if not opcao: 
            txt_status.value = "Selecione um tanque primeiro"
            txt_status.color = "red"
            page.update()
            return

        arquivo_alvo = CONFIG_TANQUES.get(opcao)
        tabela = banco_dados.get(arquivo_alvo)

        if not tabela:
            lbl_total.value = "Erro Tabela"
            lbl_desc.value = f"Arquivo {arquivo_alvo} não carregou"
            lbl_total.color = "#ff4d4d" # Vermelho
            card_resultado.visible = True
            page.update()
            return

        try:
            if "SOMA TOTAL" in opcao:
                val_1 = txt_regua_1.value
                val_2 = txt_regua_2.value
                
                if not val_1 or not val_2:
                    lbl_total.value = "Digite as duas réguas"
                    lbl_total.size = 20
                    card_resultado.visible = True
                    page.update()
                    return

                cm_a = int(val_1)
                cm_b = int(val_2)
                
                vol_a = tabela.get(cm_a, 0)
                vol_b = tabela.get(cm_b, 0)
                total = vol_a + vol_b
                
                lbl_total.value = f"{total} Litros"
                lbl_total.size = 40
                lbl_desc.value = "Total Sistema (Físico + Contábil)"
                lbl_detalhe.value = f"Lado A: {vol_a} L  |  Lado B: {vol_b} L"
                lbl_total.color = "#007bff" # Azul

            else:
                if not txt_regua_1.value: return
                cm = int(txt_regua_1.value)
                vol = tabela.get(cm)
                
                if vol is not None:
                    lbl_total.value = f"{vol} Litros"
                    lbl_total.size = 40
                    lbl_desc.value = "Volume em Estoque"
                    lbl_detalhe.value = f"Tanque: {opcao.split(' - ')[0]}"
                    lbl_total.color = "#007bff"
                else:
                    lbl_total.value = "Não Tabelado"
                    lbl_total.size = 30
                    lbl_desc.value = "Medida fora da tabela"
                    lbl_detalhe.value = "Verifique a régua novamente"
                    lbl_total.color = "orange"

            card_resultado.visible = True

        except ValueError:
            lbl_total.value = "Erro numérico"
            lbl_desc.value = "Digite apenas números inteiros"
            lbl_total.size = 30
            lbl_total.color = "red"
            card_resultado.visible = True
        
        page.update()

    # --- 3. MONTAGEM DA TELA (Interface Bonita) ---
    
    # Cabeçalho
    header = ft.Container(
        content=ft.Column([
            ft.Text("Controle de Estoque", size=22, weight="bold", color="white"),
            txt_status # Mostra se carregou ou deu erro
        ]),
        margin=ft.margin.only(bottom=20)
    )

    # Entradas
    dropdown_tanques = ft.Dropdown(
        label="Selecione o Tanque",
        options=[ft.dropdown.Option(nome) for nome in CONFIG_TANQUES.keys()],
        on_change=mudar_dropdown,
        color="white", border_color="#007bff", bgcolor="#2d2d2d",
        text_size=16
    )

    txt_regua_1 = ft.TextField(
        label="Régua (cm)", keyboard_type=ft.KeyboardType.NUMBER, 
        color="white", border_color="white", text_align="center", text_size=18
    )

    # Campo extra para o Tanque B (Soma)
    txt_regua_2 = ft.TextField(
        label="Régua T02B (cm)", keyboard_type=ft.KeyboardType.NUMBER, 
        color="white", border_color="white", text_align="center", text_size=18
    )
    container_soma = ft.Container(content=txt_regua_2, visible=False)

    btn_calcular = ft.ElevatedButton(
        text="CONSULTAR", width=300, height=55, 
        bgcolor="#007bff", color="white", 
        on_click=calcular,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    # Resultado
    lbl_desc = ft.Text("Resultado", color="grey", size=14)
    lbl_total = ft.Text("-", size=40, weight="bold", color="#007bff")
    lbl_detalhe = ft.Text("-", color="white", size=14)

    card_resultado = ft.Container(
        content=ft.Column([
            lbl_desc,
            lbl_total,
            ft.Divider(color="grey"),
            lbl_detalhe
        ], horizontal_alignment="center"),
        bgcolor="#2d2d2d", padding=25, border_radius=15, visible=False, width=320,
        border=ft.border.all(1, "#444444")
    )

    # Adiciona tudo na tela PRIMEIRO
    page.add(
        ft.Column([
            header,
            dropdown_tanques,
            ft.Container(height=10),
            txt_regua_1,
            ft.Container(height=5),
            container_soma,
            ft.Container(height=20),
            btn_calcular,
            ft.Container(height=25),
            card_resultado
        ], horizontal_alignment="center")
    )

    # AGORA carrega os arquivos (com a tela já aberta)
    carregar_arquivos_seguro()

ft.app(target=main, assets_dir="assets")
