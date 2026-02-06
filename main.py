import flet as ft
import os

def main(page: ft.Page):
    page.title = "Modo Diagnóstico"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.scroll = "AUTO"

    # Área de texto para mostrar o que o sistema encontrar
    txt_log = ft.Text("Aguardando comando...", color="green", font_family="Consolas")

    # 1. Botão para descobrir onde estamos
    def onde_estou(e):
        try:
            cwd = os.getcwd()
            txt_log.value = f"PASTA ATUAL: {cwd}\n\n"
            
            # Tenta listar arquivos na pasta atual
            lista = os.listdir(cwd)
            txt_log.value += f"ARQUIVOS AQUI:\n{lista}\n\n"
            
            # Tenta achar a pasta assets
            if "assets" in lista:
                txt_log.value += "PASTA 'ASSETS' ENCONTRADA!\n"
                lista_assets = os.listdir(os.path.join(cwd, "assets"))
                txt_log.value += f"CONTEÚDO DE ASSETS:\n{lista_assets}"
            else:
                txt_log.value += "❌ PASTA 'ASSETS' NÃO ESTÁ AQUI.\n"
                # Tenta olhar na pasta do script
                script_dir = os.path.dirname(__file__)
                txt_log.value += f"\nTENTANDO PASTA DO SCRIPT: {script_dir}\n"
                try:
                    lista_script = os.listdir(script_dir)
                    txt_log.value += f"ARQUIVOS NO SCRIPT:\n{lista_script}"
                except:
                    txt_log.value += "Erro ao ler pasta do script."

        except Exception as erro:
            txt_log.value = f"ERRO CRÍTICO: {erro}"
        page.update()

    # Botões de Ação
    btn_raio_x = ft.ElevatedButton("ONDE ESTÃO OS ARQUIVOS?", on_click=onde_estou, bgcolor="blue", color="white")

    page.add(
        ft.Text("DIAGNÓSTICO DO SISTEMA", size=20, weight="bold", color="red"),
        ft.Text("Se esta tela apareceu, o app NÃO travou.", color="grey"),
        ft.Divider(),
        btn_raio_x,
        ft.Divider(),
        ft.Container(content=txt_log, bgcolor="#111111", padding=10, border_radius=5)
    )

ft.app(target=main, assets_dir="assets")
