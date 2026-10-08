
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.ticker import MultipleLocator
import matplotlib.patheffects as pe
import time
import ctypes  # An included library with Python install.   
import math
from pathlib import Path
import re
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


# =============================================================================
# IDENTIDADE VISUAL DA APLICAÇÃO
# =============================================================================
# Nome oficial da ferramenta e localização da logo. A imagem é procurada
# primeiro na mesma pasta do script, facilitando transportar os dois arquivos
# juntos para outro computador.
APP_TITLE = "EESC-USP Formula SAE: Drivetrain Analysis"
LOGO_FILENAME = "EESCUSPFSAE_logo.png"
LOGO_PATH = Path(__file__).resolve().parent / LOGO_FILENAME
_LOGO_MPL_CACHE = None


# =============================================================================
# VISÃO GERAL DO PROGRAMA
# =============================================================================
#
# O PlotterPowertrain transforma dados de um veículo e de uma curva de motor
# em estudos de powertrain para um carro de Fórmula SAE. A aplicação possui
# três fontes de dados independentes:
#
#   1) carro.csv
#      Contém as informações/configurações do veículo (relações de marcha,
#      relação primária/secundária e raio da roda).
#
#   2) CSV de RPM x Torque
#      Contém os pontos da curva do motor. Este arquivo é selecionado
#      separadamente para que seja possível testar diferentes mapas de motor
#      sem precisar editar o carro.csv.
#
#   3) CSV de Batch Run do OptimumLap
#      Contém várias simulações (runs). Cada linha possui um nome no primeiro
#      campo, seguido pelos valores de cada run. O programa procura os dados
#      pelo texto da primeira coluna, em vez de depender de posições fixas.
#      Isso torna a leitura mais resistente a alterações na ordem das linhas.
#
# Fluxo principal na GUI:
#
#   arquivos -> parsers -> objeto Carro/BatchRun -> estudos -> tabela/gráfico
#                                  -> resultados em memória -> exportação CSV
#
# O arquivo também mantém a interface de terminal histórica. A classe Carro
# concentra os cálculos físicos; as interfaces apenas selecionam entradas,
# chamam os cálculos e apresentam/exportam os resultados.
# =============================================================================
# FORMATOS DE ENTRADA
# =============================================================================
#
# carro.csv (formato atual):
#     nome;Teste
#     relacoes_marcha;C:\caminho\para\GearRatios.csv
#     relacao_primaria;2.6667
#     relacao_secundaria;2.9090
#     raio_roda;0.194
#     peso;240
#     Cat_pneu;2.204
#
# Parâmetros físicos opcionais aceitos no mesmo arquivo:
#     drivetrain_efficiency;0.96
#     drag_coefficient;1.34
#     downforce_coefficient;3.54
#     frontal_area;1.14
#     air_density;1.16
#     tire_rolling_drag;0.01
#     rev_limit;10931
#     longitudinal_friction;2.204
#     lateral_friction;2.285
#     rear_weight_distribution;0.55
#     rear_downforce_distribution;0.60
#     cg_height;0.25
#     wheelbase;1.55
#
# Quando esses campos não existem no carro.csv, o programa pode obtê-los do
# Batch Run carregado (quando o OptimumLap fornece a variável).
#
# Os nomes dos parâmetros são interpretados pelo programa, portanto a ordem
# das linhas não é importante. O parâmetro ``relacoes_marcha`` pode apontar
# para um arquivo externo de relações de marcha, como no exemplo, ou conter
# diretamente vários valores numéricos separados por ``;``.
#
# ``peso`` e ``Cat_pneu`` agora fazem parte do arquivo do carro e, portanto,
# deixam de ser valores fixos escondidos dentro da classe Carro.
#
# Por compatibilidade, a versão antiga do carro.csv com 5 linhas posicionais
# também é aceita. Nessa versão a primeira linha, que antes apontava para a
# curva RPM x Torque, deixou de ser necessária porque o mapa do motor agora é
# selecionado independentemente pela GUI.
#
# CSV RPM x Torque:
#     RPM<TAB>Torque
#     3500<TAB>19,10
#     3750<TAB>20,00
#
# CSV Batch Run do OptimumLap:
#     Final Drive Ratio [-];6.5;6.65;6.8;...
#     Lap time [s];45.09;45.08;45.07;...
#     Gear Shifts [-];60;62;62;...
#
# O parser do Batch Run não usa a posição da linha: ele procura o nome no
# primeiro campo e devolve todos os valores numéricos seguintes daquela linha.
# =============================================================================

rc_isdef = False
dpi = 0

def setMatplotParameters():
    global rc_isdef
    dpi = 130
    rc_params = {
        # Fonte e títulos
        #'font.family': 'serif',            # Fonte geral
        'axes.titlesize': 28,               # Título do gráfico
        'axes.titleweight': 'bold',         # Peso do título
        'axes.titlecolor': '#000000',       # Cor do título
        'axes.labelsize': 20,               # Texto dos eixos
        'axes.labelcolor': '#000000',       # Cor dos rótulos

        # Ticks (eixos)
        'xtick.labelsize': 12,              # Tamanho dos ticks X
        'ytick.labelsize': 12,              # Tamanho dos ticks Y
        'xtick.color': '#333333',           # Cor dos ticks X
        'ytick.color': '#333333',           # Cor dos ticks Y
        'xtick.direction': 'out',           # Direção dos ticks X
        'ytick.direction': 'out',           # Direção dos ticks Y
        'xtick.minor.visible': True,        # Ticks menores visíveis X
        'ytick.minor.visible': True,        # Ticks menores visíveis Y

        # Paleta de cores distintas e sóbrias
        'axes.prop_cycle': plt.cycler(color=[
            '#2E86AB',  # Azul
            '#F6C85F',  # Amarelo
            '#6B5B95',  # Roxo
            '#FF6F61',  # Coral
            '#88B04B',  # Verde
            '#955251'   # Vinho
        ]),

        # Tamanho e resolução
        'figure.figsize': (18, 9),          # Tamanho do gráfico
        'figure.dpi': dpi,                  # Resolução

        # Fundo e borda
        'figure.facecolor': '#FFFFFF',      # Fundo da figura
        'axes.facecolor': '#FFFFFF00',      # Fundo do gráfico (transparente)
        'axes.edgecolor': '#000000',        # Cor da borda
        'axes.linewidth': 1,                  # Espessura da borda0


        # Grid principal (major)
        'axes.grid': True,                  # Ativa grid
        'grid.color': '#B0B0B0',          # Cor da grade
        'grid.linestyle': '-',              # Estilo do traço
        'grid.linewidth': 0.8,              # Espessura da linha
        'axes.axisbelow': True,             # Grid abaixo dos dados

        # Grid secundário (minor)
        'grid.alpha': 0.25,                 # Transparência da grade

        # Curvas e marcadores
        'lines.linewidth': 2,               # Espessura da curva
        'lines.markersize': 6,              # Tamanho dos marcadores

        # Legenda
        'legend.handlelength': 1.5,    # Comprimento do ícone (linha/quadrado)
        'legend.handleheight': 2,    # Altura do ícone (mais perceptível em markers)
        'legend.labelspacing': 2,    # Espaço vertical entre os itens
        'legend.loc': 'best',          # Posição padrão da legenda
        'legend.borderpad': 0.5,       # Padding interno da legenda
        'legend.fontsize': 16,              # Texto da legenda
        'legend.title_fontsize': 16,        # Título da legenda
        'legend.frameon': True,             # Borda ativa
        'legend.facecolor': "#ffffffcc",    # Cor de fundo (semi-transparente)
        'legend.edgecolor': '#444444',      # Cor da borda
        'legend.framealpha': 0.9,           # Opacidade
        'legend.markerscale': 1,    # escala para pontos/marcadores

        # BBox da legenda
        'legend.handletextpad': 0.8,        # Espaço ícone-texto
        'legend.borderaxespad': 1.0,        # Espaço legenda-graf
        'legend.columnspacing': 1.0,        # Espaço entre colunas

        # Margens
        'axes.autolimit_mode': 'data',      # Ajuste pelos dados
        #'axes.xmargin': 40/dpi,              # Margem X
        #'axes.ymargin': 50/dpi                # Margem Y
    }
    plt.rcParams.update(rc_params)
    rc_isdef = True


def _get_logo_mpl():
    """Carrega e armazena em cache a logo para uso nos gráficos."""
    global _LOGO_MPL_CACHE
    if _LOGO_MPL_CACHE is not None:
        return _LOGO_MPL_CACHE

    try:
        if LOGO_PATH.exists():
            _LOGO_MPL_CACHE = mpimg.imread(str(LOGO_PATH))
        else:
            print(f"Aviso: logo não encontrada em: {LOGO_PATH}")
            _LOGO_MPL_CACHE = False
    except Exception as exc:
        print(f"Aviso: não foi possível carregar a logo: {exc}")
        _LOGO_MPL_CACHE = False
    return _LOGO_MPL_CACHE


def _add_logo_watermark(ax, alpha=0.05, zoom=0.50):
    """Adiciona a logo no fundo do gráfico.

    ``alpha=0.05`` equivale a 5% de opacidade, isto é, 95% de transparência,
    conforme solicitado. A posição usa coordenadas relativas aos eixos, então
    a marca d'água não altera os limites numéricos do gráfico.
    """
    logo = _get_logo_mpl()
    if logo is False:
        return None

    try:
        image = OffsetImage(logo, zoom=zoom)
        image.set_alpha(alpha)
        artist = AnnotationBbox(
            image,
            (0.50, 0.50),
            xycoords="axes fraction",
            frameon=False,
            box_alignment=(0.5, 0.5),
            zorder=0.5,
        )
        ax.add_artist(artist)
        return artist
    except Exception as exc:
        print(f"Aviso: não foi possível adicionar watermark da logo: {exc}")
        return None

def interp_1d(x_new, x, y):
    """Realiza interpolação linear 1D (substituindo np.interp)."""
    result = []
    for xi in x_new:
        if xi <= x[0]:
            result.append(y[0])
        elif xi >= x[-1]:
            result.append(y[-1])
        else:
            for k in range(len(x) - 1):
                if x[k] <= xi <= x[k + 1]:
                    slope = (y[k + 1] - y[k]) / (x[k + 1] - x[k])
                    result.append(y[k] + slope * (xi - x[k]))
                    break
    return result

def linspace_pure(start, stop, num):
    """Gera uma lista de números igualmente espaçados dentro de um intervalo.

    Substitui a função np.linspace do NumPy.
    """
    if num <= 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]

def plotterPrint(text):
    print("PlotterPowertrain: " + text)

def _detectar_delimitador_csv(filename):
    """Tenta identificar o separador do arquivo de dados.

    Os arquivos usados pelo projeto não têm todos o mesmo separador: a curva
    RPM x Torque de exemplo usa TAB, enquanto os exports do OptimumLap usam ';'.
    """
    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        amostra = file.read(4096)
    # TAB é característico do mapa RPM x Torque/relacionamento de marchas.
    if "	" in amostra:
        return "	"
    if ";" in amostra:
        return ";"
    return ","


def getRPMxTorquePoints(filename) -> list:
    """Lê uma curva de motor e devolve [[RPM, torque], ...].

    Formato aceito:
        RPM<TAB>Torque
        3500	19,10
        3750	20,00

    Tanto ponto quanto vírgula decimal são aceitos. Linhas vazias são ignoradas.
    """
    start_effectiveruntime = time.time()
    mapa = []
    delimiter = _detectar_delimitador_csv(filename)

    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=delimiter)
        for numero_linha, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) < 2:
                raise ValueError(f"Curva RPM x Torque: linha {numero_linha} tem menos de 2 colunas.")
            try:
                rpm = float(row[0].strip().replace(",", "."))
                torque = float(row[1].strip().replace(",", "."))
            except ValueError as exc:
                # Permite um cabeçalho textual eventual apenas na primeira linha.
                if numero_linha == 1:
                    continue
                raise ValueError(
                    f"Curva RPM x Torque: valores inválidos na linha {numero_linha}: {row[:2]}"
                ) from exc
            mapa.append([rpm, torque])

    if len(mapa) < 2:
        raise ValueError("O arquivo RPM x Torque precisa conter pelo menos dois pontos válidos.")

    mapa.sort(key=lambda ponto: ponto[0])  # ordem crescente em RPM
    print(f"{time.time() - start_effectiveruntime:.4f} segundos para adquirir dados RPMxTorque")
    return mapa


def getGearRatios(filename) -> list:
    """Lê as relações de marcha exportadas/copiadas do OptimumLap.

    Formato esperado por linha: ``<identificador da marcha>\t<relação>``.
    As relações são ordenadas da maior para a menor, correspondendo à 1ª
    para a última marcha.
    """
    start_effectiveruntime = time.time()
    mapa = []
    delimiter = _detectar_delimitador_csv(filename)

    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=delimiter)
        for numero_linha, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) < 2:
                raise ValueError(f"Relações de marcha: linha {numero_linha} inválida.")
            valor = _primeiro_valor_numerico(row[1])
            if valor is None:
                if numero_linha == 1:
                    continue
                raise ValueError(f"Relação de marcha inválida na linha {numero_linha}: {row[:2]}")
            mapa.append(valor)

    if not mapa:
        raise ValueError("Nenhuma relação de marcha válida foi encontrada.")
    mapa.sort(reverse=True)
    print(f"{time.time() - start_effectiveruntime:.4f} segundos para adquirir escalonamento de marchas")
    return mapa


def _normalizar_rotulo(rotulo):
    """Normaliza um rótulo para comparações tolerantes a maiúsculas/acentos."""
    import unicodedata
    texto = str(rotulo).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return " ".join(texto.split())


def _primeiro_valor_numerico(texto):
    """Converte um campo em float, retornando None quando ele não é numérico."""
    if texto is None:
        return None
    try:
        return float(str(texto).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def _extrair_series_numericas(row):
    """Extrai todos os números presentes depois do primeiro termo da linha."""
    valores = []
    for cell in row[1:]:
        if str(cell).strip() == "":
            continue
        numero = _primeiro_valor_numerico(cell)
        if numero is not None:
            valores.append(numero)
    return valores


def _buscar_linha_por_rotulo(dados, rotulo, aliases=()):
    """Busca uma série do Batch Run pelo primeiro campo da linha.

    A comparação primeiro tenta o texto exato e depois uma forma normalizada
    (sem acentos e sem diferença entre maiúsculas/minúsculas).
    """
    data = dados.get("data", {})
    if rotulo in data:
        return data[rotulo]

    procurados = {_normalizar_rotulo(rotulo)}
    procurados.update(_normalizar_rotulo(a) for a in aliases)
    for chave, valores in data.items():
        if _normalizar_rotulo(chave) in procurados:
            return valores

    disponiveis = ", ".join(data.keys())
    raise KeyError(f"Linha '{rotulo}' não encontrada no Batch Run. Dados disponíveis: {disponiveis}")


def getBatchVehicleParameters(batch):
    """Extrai parâmetros físicos constantes disponibilizados pelo OptimumLap.

    O Batch Run pode ser usado como fonte secundária para parâmetros que não
    estejam presentes no carro.csv. Isso é útil porque o CSV de configuração
    atual contém os parâmetros básicos do veículo, enquanto o export do
    OptimumLap também informa aerodinâmica, eficiência do drivetrain, Crr e
    limite de rotação.

    Apenas parâmetros que aparecem no Batch são retornados. FDR não é copiado
    para o modelo base porque cada coluna do Batch representa uma configuração
    diferente de FDR.
    """
    mapping = {
        "Drivetrain Efficiency [%]": ("drivetrain_efficiency", 0.01),
        "Drag Coefficient [-]": ("drag_coefficient", 1.0),
        "Downforce Coefficient [-]": ("downforce_coefficient", 1.0),
        "Frontal Area [m^2]": ("frontal_area", 1.0),
        "Air Density [kg/m^3]": ("air_density", 1.0),
        "Tire Rolling Drag [-]": ("tire_rolling_drag", 1.0),
        "Rev Limit [rpm]": ("rev_limit", 1.0),
        "Longitudinal Friction [-]": ("longitudinal_friction", 1.0),
        "Lateral Friction [-]": ("lateral_friction", 1.0),
        "Tire Rolling Radius [m]": ("wheel_radius", 1.0),
    }
    resultado = {}
    for rotulo, (nome, escala) in mapping.items():
        try:
            serie = _buscar_linha_por_rotulo(batch, rotulo)
        except KeyError:
            continue
        if not serie:
            continue
        resultado[nome] = float(serie[0]) * escala
    return resultado


def getBatchRun(filename, show_data_index=0) -> dict:
    """Lê um Batch Run do OptimumLap procurando os dados pelo primeiro termo.

    O retorno tem a forma:

        {
            "profile": {"Track": "...", "Vehicle": "...", ...},
            "data": {"Lap time [s]": [..], "Final Drive Ratio [-]": [..], ...},
            "sections": {...}
        }

    Isso elimina a dependência de índices como ``batch[37]``. Por exemplo,
    a série de FDR é obtida pesquisando diretamente ``Final Drive Ratio [-]``.
    """
    start_effectiveruntime = time.time()
    perfil = {}
    dados = {}
    secoes = {}
    secao_atual = ""

    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        for numero_linha, row in enumerate(reader, start=1):
            if not row:
                continue

            # O primeiro campo define a seção ou o nome do dado.
            rotulo = row[0].strip()
            if not rotulo:
                continue

            if rotulo.startswith("[") and rotulo.endswith("]"):
                secao_atual = rotulo
                secoes.setdefault(secao_atual, {})
                continue

            valores_textuais = [cell.strip() for cell in row[1:]]

            # As informações antes de [KPI Values] são metadados do resultado.
            if secao_atual in ("", "[Result Details]"):
                perfil[rotulo] = valores_textuais[0] if valores_textuais else ""
                secoes.setdefault(secao_atual or "[Result Details]", {})[rotulo] = perfil[rotulo]
                continue

            # Para as tabelas de KPIs/parâmetros, guardamos somente os valores
            # numéricos. A ordem da linha deixa de importar para o programa.
            serie = _extrair_series_numericas(row)
            if serie:
                dados[rotulo] = serie
                secoes.setdefault(secao_atual, {})[rotulo] = serie

    if not dados:
        raise ValueError("Nenhum dado numérico foi encontrado no Batch Run.")

    resultado = {"profile": perfil, "data": dados, "sections": secoes, "filename": str(filename)}

    if show_data_index:
        print("\n--- Índice textual dos dados do Batch Run ---")
        for indice, rotulo in enumerate(dados.keys()):
            print(f"{indice:3d}: {rotulo}")

    print(f"{time.time() - start_effectiveruntime:.4f} segundos para adquirir dados da Batch Run")
    return resultado


def plotBatchLaptimesFDRShift(batch, shift_time, ax=None):
    """Plota FDR x laptime considerando um tempo adicional por troca."""
    fdr_range = _buscar_linha_por_rotulo(batch, "Final Drive Ratio [-]")
    laptimes = _buscar_linha_por_rotulo(batch, "Lap time [s]", aliases=("Laptime [s]",))
    num_shifts = _buscar_linha_por_rotulo(batch, "Gear Shifts [-]", aliases=("Number of gearshifts",))

    laptimes_with_shifts = [t + (gs * shift_time) for t, gs in zip(laptimes, num_shifts)]

    # Quando chamado pelo terminal, criamos a figura. Na GUI, recebemos o eixo
    # já embutido na janela e evitamos abrir uma segunda janela do Matplotlib.
    if ax is None:
        if not rc_isdef:
            setMatplotParameters()
        fig, ax = plt.subplots()
        mostrar = True
    else:
        fig = ax.figure
        mostrar = False

    ax.set_xlabel(f"Final Drive Ratio [{min(fdr_range):g}; {max(fdr_range):g}]")
    ax.set_ylabel("Laptime [s]")
    ax.plot(fdr_range, laptimes, label="Laptimes sem tempo de troca")
    ax.plot(fdr_range, laptimes_with_shifts, label=f"Laptimes + {shift_time:g}s por troca")
    indice_min = laptimes_with_shifts.index(min(laptimes_with_shifts))
    ax.scatter(
        fdr_range[indice_min], laptimes_with_shifts[indice_min], s=50,
        label=f"Melhor com trocas: {laptimes_with_shifts[indice_min]:.2f} s | FDR: {fdr_range[indice_min]:.3f}"
    )
    ax.set_title("Laptime para Batch Runs de FDR com tempo de troca")
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(True, which="major")
    ax.grid(False, which="minor")
    ax.legend(loc="best")

    if mostrar:
        fig.tight_layout()
        _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
        plt.show()
    return [fdr_range, laptimes_with_shifts]


def plotBatchLaptimeFDR(batch, ax=None):
    """Plota FDR x laptime de cada run do Batch Run."""
    fdr_range = _buscar_linha_por_rotulo(batch, "Final Drive Ratio [-]")
    laptimes = _buscar_linha_por_rotulo(batch, "Lap time [s]", aliases=("Laptime [s]",))

    if ax is None:
        if not rc_isdef:
            setMatplotParameters()
        fig, ax = plt.subplots()
        mostrar = True
    else:
        fig = ax.figure
        mostrar = False

    ax.set_xlabel(f"Final Drive Ratio [{min(fdr_range):g}; {max(fdr_range):g}]")
    ax.set_ylabel("Laptime [s]")
    ax.plot(fdr_range, laptimes, label="Laptime")
    indice_min = laptimes.index(min(laptimes))
    ax.scatter(
        fdr_range[indice_min], laptimes[indice_min], s=50,
        label=f"Melhor laptime: {laptimes[indice_min]:.2f} s | FDR: {fdr_range[indice_min]:.3f}"
    )
    ax.set_title("Laptime para Batch Runs de FDR")
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(True, which="major")
    ax.grid(False, which="minor")
    ax.legend(loc="best")

    if mostrar:
        fig.tight_layout()
        _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
        plt.show()
    return [fdr_range, laptimes]


def getCarroCSV(filename):
    """Lê o carro.csv no formato de duas colunas ``Parâmetro;Valor``.

    A função continua retornando a segunda coluna para manter compatibilidade
    com a interface de terminal antiga. Para a nova arquitetura, use
    ``getCarroConfig`` abaixo, que também interpreta o nome do parâmetro.
    """
    dados = []
    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            dados.append(row[1].strip() if len(row) > 1 else "")
    return dados


def _caminho_eh_absoluto(caminho):
    """Reconhece caminhos absolutos tanto no Windows quanto no sistema atual.

    O carro.csv é frequentemente montado em um computador Windows e pode
    guardar valores como ``C:\\pasta\\GearRatios.csv``. Quando o arquivo é
    analisado em outro sistema, ``Path`` local pode não reconhecer esse texto
    como absoluto. Esta função evita transformar um caminho Windows em um
    caminho relativo ao diretório do carro.csv.
    """
    texto = str(caminho).strip()
    return Path(texto).is_absolute() or bool(re.match(r"^[A-Za-z]:[\\/]", texto))


def getCarroConfig(filename):
    """Lê e interpreta o arquivo de configuração ``carro.csv``.

    O formato atualmente utilizado pela equipe é uma tabela simples em que
    cada linha possui:

        nome_do_parametro;valor

    Exemplo:

        nome;Teste
        relacoes_marcha;C:\\...\\GearRatios.csv
        relacao_primaria;2.6667
        relacao_secundaria;2.9090
        raio_roda;0.194
        peso;240
        Cat_pneu;2.204

    A leitura é feita pelo *nome* do parâmetro e não pela posição da linha.
    Assim, novas linhas podem ser acrescentadas sem quebrar o parser.

    ``relacoes_marcha`` pode ter duas formas:
      1. caminho para um arquivo de relações de marcha, que será lido por
         :func:`getGearRatios`;
      2. vários números na própria linha, por exemplo
         ``relacoes_marcha;3.0;2.1;1.6;1.3;1.1;0.9``.

    O mapa RPM x Torque NÃO pertence mais ao carro.csv: ele é selecionado
    separadamente pela interface.

    Retorna um dicionário padronizado usado pela interface e pelo objeto
    :class:`Carro`.
    """
    entries = []
    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            if not row or not any(str(cell).strip() for cell in row):
                continue

            label = str(row[0]).strip()
            values = [str(cell).strip() for cell in row[1:] if str(cell).strip()]
            entries.append((label, values))

    if not entries:
        raise ValueError("O carro.csv está vazio.")

    # Mantemos todas as linhas em um dicionário normalizado para que
    # "relacao_primaria", "Relação primária" e "RELACAO PRIMARIA" possam ser
    # tratados como o mesmo parâmetro.
    normalized = {_normalizar_rotulo(label): values for label, values in entries}

    def find_values(*labels):
        """Procura um parâmetro por um conjunto de nomes/aliases."""
        for label in labels:
            chave = _normalizar_rotulo(label)
            if chave in normalized:
                return normalized[chave]

        # Segundo nível: permite diferenças pequenas, como '_' vs espaço,
        # plural/singular ou textos um pouco mais longos.
        wanted = [_normalizar_rotulo(label) for label in labels]
        for key, vals in normalized.items():
            if any(w in key or key in w for w in wanted):
                return vals
        return None

    config = {}

    # ------------------------------------------------------------------
    # 1) Identificação do carro
    # ------------------------------------------------------------------
    nome = find_values("nome", "name", "vehicle name", "car name")
    if nome:
        config["name"] = nome[0]

    # ------------------------------------------------------------------
    # 2) Relações de marcha
    # ------------------------------------------------------------------
    # No formato atual o nome usado é "relacoes_marcha". Mantemos os aliases
    # antigos para que arquivos anteriores continuem funcionando.
    gear_values = find_values(
        "relacoes_marcha",
        "relacoes marcha",
        "Gear Ratio Data [-]",
        "Gear Ratios",
        "Relações de marcha",
        "Escalonamento de marchas",
        "Gear Ratio",
    )

    if gear_values:
        # Tenta interpretar todos os campos da linha como números.
        numeric_gears = [_primeiro_valor_numerico(v) for v in gear_values]
        numeric_gears = [v for v in numeric_gears if v is not None]

        if len(numeric_gears) >= 2:
            # O restante do programa considera a 1ª marcha como a maior
            # relação, por isso armazenamos em ordem decrescente.
            config["gear_ratios"] = sorted(numeric_gears, reverse=True)
        else:
            # Se não forem números, o valor é interpretado como caminho para
            # o arquivo externo de escalonamento de marchas.
            config["gear_ratio_file"] = gear_values[0]

    # ------------------------------------------------------------------
    # 3) Relação primária e secundária
    # ------------------------------------------------------------------
    primary = find_values(
        "relacao_primaria",
        "relacao primaria",
        "Primary Drive Ratio",
        "Primary Ratio",
        "Relação primária",
        "Relacao primaria",
    )
    secondary = find_values(
        "relacao_secundaria",
        "relacao secundaria",
        "Secondary Drive Ratio",
        "Secondary Ratio",
        "Relação secundária",
        "Relacao secundaria",
    )
    fdr = find_values(
        "Final Drive Ratio [-]",
        "Final Drive Ratio",
        "FDR",
        "final_drive",
    )

    if primary:
        config["primary_ratio"] = _primeiro_valor_numerico(primary[0])
    if secondary:
        config["secondary_ratio"] = _primeiro_valor_numerico(secondary[0])
    if fdr and _primeiro_valor_numerico(fdr[0]) is not None:
        config["final_drive"] = _primeiro_valor_numerico(fdr[0])

    # ------------------------------------------------------------------
    # 4) Geometria e parâmetros de aderência
    # ------------------------------------------------------------------
    radius = find_values(
        "raio_roda",
        "raio roda",
        "Tire Rolling Radius [m]",
        "Wheel Radius [m]",
        "Wheel Radius",
        "Raio da roda",
        "Raio da roda [m]",
    )
    peso = find_values(
        "peso",
        "massa",
        "weight",
        "vehicle weight",
        "Vehicle Weight [kg]",
    )
    cat_pneu = find_values(
        "Cat_pneu",
        "cat pneu",
        "coeficiente pneu",
        "tire coefficient",
        "tire friction coefficient",
    )

    if radius:
        config["wheel_radius"] = _primeiro_valor_numerico(radius[0])
    if peso:
        config["weight"] = _primeiro_valor_numerico(peso[0])
    if cat_pneu:
        config["tire_coefficient"] = _primeiro_valor_numerico(cat_pneu[0])

    # ------------------------------------------------------------------
    # 4b) Parâmetros físicos opcionais
    # ------------------------------------------------------------------
    # Eles não são obrigatórios no carro.csv atual. Quando estiverem ausentes,
    # podem ser preenchidos a partir do Batch Run carregado ou pelos padrões
    # históricos do modelo.
    opcionais_fisicos = {
        "drivetrain_efficiency": (
            "Drivetrain Efficiency [%]", "drivetrain efficiency", "eficiencia drivetrain"
        ),
        "drag_coefficient": (
            "Drag Coefficient [-]", "drag coefficient", "cd"
        ),
        "downforce_coefficient": (
            "Downforce Coefficient [-]", "downforce coefficient", "cl"
        ),
        "frontal_area": (
            "Frontal Area [m^2]", "frontal area", "area frontal"
        ),
        "air_density": (
            "Air Density [kg/m^3]", "air density", "densidade do ar"
        ),
        "tire_rolling_drag": (
            "Tire Rolling Drag [-]", "tire rolling drag", "resistencia ao rolamento", "crr"
        ),
        "rev_limit": (
            "Rev Limit [rpm]", "rev limit", "limite de rpm"
        ),
        "longitudinal_friction": (
            "Longitudinal Friction [-]", "longitudinal friction", "atrito longitudinal"
        ),
        "lateral_friction": (
            "Lateral Friction [-]", "lateral friction", "atrito lateral"
        ),
        "rear_weight_distribution": (
            "Rear Weight Distribution [-]", "rear weight distribution", "distribuicao traseira"
        ),
        "rear_downforce_distribution": (
            "Rear Downforce Distribution [-]", "rear downforce distribution", "distribuicao downforce traseira"
        ),
        "cg_height": ("CG Height [m]", "cg height", "altura cg"),
        "wheelbase": ("Wheelbase [m]", "wheelbase", "entre-eixos"),
    }
    for chave, aliases in opcionais_fisicos.items():
        vals = find_values(*aliases)
        if vals:
            numero = _primeiro_valor_numerico(vals[0])
            if numero is not None:
                config[chave] = numero

    # ------------------------------------------------------------------
    # 5) Compatibilidade com formatos anteriores
    # ------------------------------------------------------------------
    # Caso o usuário ainda tenha um carro.csv antigo e algum parâmetro não
    # tenha sido identificado pelo nome, tentamos recuperar por posição.
    valores_legacy = [values[0] if values else "" for _, values in entries]

    # Formato antigo com 5 linhas: [RPMxTorque, marchas, primária,
    # secundária, raio]. Formato compacto: [marchas, primária, secundária,
    # raio]. O mapa RPMxTorque não é mais usado pelo carro.csv.
    offset = 1 if len(valores_legacy) >= 5 else 0

    if "gear_ratio_file" not in config and "gear_ratios" not in config and len(valores_legacy) >= offset + 1:
        config["gear_ratio_file"] = valores_legacy[offset]
    if "primary_ratio" not in config and len(valores_legacy) >= offset + 2:
        config["primary_ratio"] = _primeiro_valor_numerico(valores_legacy[offset + 1])
    if "secondary_ratio" not in config and len(valores_legacy) >= offset + 3:
        config["secondary_ratio"] = _primeiro_valor_numerico(valores_legacy[offset + 2])
    if "wheel_radius" not in config and len(valores_legacy) >= offset + 4:
        config["wheel_radius"] = _primeiro_valor_numerico(valores_legacy[offset + 3])

    # Valores históricos padrão: usados somente quando o arquivo realmente
    # não contém peso/coeficiente. No novo formato, estes campos vêm do CSV.
    if config.get("weight") is None:
        config["weight"] = 240.0
    if config.get("tire_coefficient") is None:
        config["tire_coefficient"] = 2.204

    # Se o carro.csv especificar apenas FDR, ainda podemos representá-lo como
    # primária = 1 e secundária = FDR, preservando o modelo matemático atual.
    if config.get("secondary_ratio") is None and config.get("final_drive") is not None:
        config["primary_ratio"] = 1.0
        config["secondary_ratio"] = config["final_drive"]

    obrigatorios = ["primary_ratio", "secondary_ratio", "wheel_radius"]
    faltantes = [chave for chave in obrigatorios if config.get(chave) is None]
    if "gear_ratio_file" not in config and "gear_ratios" not in config:
        faltantes.append("gear_ratio_file/gear_ratios")

    if faltantes:
        raise ValueError(
            "Não foi possível encontrar no carro.csv: " + ", ".join(faltantes)
        )

    # O caminho do arquivo de relações pode ser relativo ao próprio carro.csv.
    # Isso torna o conjunto de arquivos portátil: podemos manter carro.csv e
    # GearRatios.csv na mesma pasta sem registrar um caminho absoluto.
    if config.get("gear_ratio_file"):
        caminho_texto = str(config["gear_ratio_file"]).strip()
        if _caminho_eh_absoluto(caminho_texto):
            caminho_absoluto = Path(caminho_texto)
            if caminho_absoluto.exists():
                config["gear_ratio_file"] = caminho_absoluto
            else:
                # Arquivos de configuração normalmente carregam caminhos Windows.
                # Se o caminho original não existir neste computador, tentamos a
                # mesma referência pelo nome do arquivo na pasta do carro.csv.
                candidato_local = Path(filename).resolve().parent / Path(caminho_texto.replace("\\", "/")).name
                if candidato_local.exists():
                    config["gear_ratio_file"] = candidato_local
                else:
                    # Mantemos o caminho original para que o erro posterior informe
                    # exatamente qual dependência está faltando.
                    config["gear_ratio_file"] = caminho_absoluto
        else:
            # Caminho relativo é resolvido a partir da pasta do carro.csv.
            config["gear_ratio_file"] = Path(filename).resolve().parent / Path(caminho_texto)

    # Validação final dos parâmetros numéricos.
    for chave in ("primary_ratio", "secondary_ratio", "wheel_radius", "weight", "tire_coefficient"):
        if config.get(chave) is None:
            raise ValueError(f"O parâmetro '{chave}' não possui um valor numérico válido.")

    if config["wheel_radius"] <= 0:
        raise ValueError("'raio_roda' deve ser maior que zero.")
    if config["weight"] <= 0:
        raise ValueError("'peso' deve ser maior que zero.")
    if config["tire_coefficient"] <= 0:
        raise ValueError("'Cat_pneu' deve ser maior que zero.")

    config["filename"] = str(filename)
    return config


class Carro:
    """Modelo simplificado do powertrain utilizado pelos estudos.

    O objeto recebe três conjuntos de informações já processados:
      * mapa do motor: RPM x torque;
      * relações de cada marcha;
      * relação final e raio efetivo do pneu.

    A partir disso calcula potência do motor e, nos métodos de estudo, converte
    RPM em velocidade do veículo e torque em torque/força na roda. O FDR usado
    em uma análise pode ser diferente do FDR cadastrado: quando um método recebe
    ``fdr=...``, esse valor substitui a relação final somente naquele cálculo.
    """

    def __init__(
        self,
        mapa_torque_rpm,
        relacoes_marcha,
        relacao_primaria,
        relacao_secundaria,
        raio_roda_m,
        peso=240.0,
        Cat_pneu=2.204,
        drivetrain_efficiency=0.96,
        drag_coefficient=1.34,
        downforce_coefficient=3.54,
        frontal_area=1.14,
        air_density=1.16,
        tire_rolling_drag=0.01,
        rev_limit=None,
        longitudinal_friction=None,
        lateral_friction=None,
        rear_weight_distribution=0.55,
        rear_downforce_distribution=0.60,
        cg_height=None,
        wheelbase=None,
    ):
        """Inicializa o modelo de powertrain e seus parâmetros físicos.

        Os primeiros parâmetros vêm diretamente do carro.csv e do mapa de
        motor. Os demais são parâmetros físicos opcionais: podem vir do
        carro.csv, de um Batch Run ou dos valores históricos de compatibilidade.
        
        Importante: o modelo não inventa torque acima do último RPM disponível
        no mapa. A rotação efetivamente usada nos estudos é:

            min(rev_limit, RPM máximo do mapa)

        Assim, um Batch com Rev Limit = 10931 rpm não cria artificialmente
        dados entre 10200 e 10931 rpm quando o mapa fornecido termina em 10200.
        """
        if not mapa_torque_rpm or len(mapa_torque_rpm) < 2:
            raise ValueError("O mapa RPM x Torque precisa conter pelo menos dois pontos.")

        self.mapa = sorted(mapa_torque_rpm, key=lambda row: row[0])
        self.rpm = [float(row[0]) for row in self.mapa]
        self.torque = [float(row[1]) for row in self.mapa]

        # Potência do motor: P[kW] = RPM * Torque[N.m] / 9549.2966.
        self.power_kw = [r * t / 9549.2966 for r, t in zip(self.rpm, self.torque)]
        self.power = [pkw * 1.34102 for pkw in self.power_kw]

        self.relacoes_marcha = sorted([float(x) for x in relacoes_marcha], reverse=True)
        self.relacao_primaria = float(relacao_primaria)
        self.relacao_secundaria = float(relacao_secundaria)
        self.final_drive = self.relacao_primaria * self.relacao_secundaria
        self.raio_roda = float(raio_roda_m)
        self.peso = float(peso)
        self.Cat_pneu = float(Cat_pneu)

        # Eficiência total entre motor e roda. 0.96 = 96 %.
        eff = float(drivetrain_efficiency)
        if eff > 1.0:
            eff /= 100.0
        if not (0 < eff <= 1.0):
            raise ValueError("A eficiência do drivetrain deve estar entre 0 e 1 (ou 0 e 100%).")
        self.drivetrain_efficiency = eff

        # Parâmetros aerodinâmicos e de resistência.
        self.drag_coefficient = float(drag_coefficient)
        self.downforce_coefficient = float(downforce_coefficient)
        self.frontal_area = float(frontal_area)
        self.air_density = float(air_density)
        self.tire_rolling_drag = float(tire_rolling_drag)

        self.longitudinal_friction = float(longitudinal_friction) if longitudinal_friction is not None else self.Cat_pneu
        self.lateral_friction = float(lateral_friction) if lateral_friction is not None else self.Cat_pneu
        self.rear_weight_distribution = float(rear_weight_distribution)
        self.rear_downforce_distribution = float(rear_downforce_distribution)
        self.cg_height = None if cg_height is None else float(cg_height)
        self.wheelbase = None if wheelbase is None else float(wheelbase)

        if self.drag_coefficient < 0 or self.downforce_coefficient < 0:
            raise ValueError("Cd e Cl não podem ser negativos.")
        if self.frontal_area <= 0 or self.air_density <= 0:
            raise ValueError("Área frontal e densidade do ar devem ser maiores que zero.")
        if self.tire_rolling_drag < 0:
            raise ValueError("Tire Rolling Drag não pode ser negativo.")
        if not (0 < self.rear_weight_distribution <= 1):
            raise ValueError("rear_weight_distribution deve estar entre 0 e 1.")
        if not (0 < self.rear_downforce_distribution <= 1):
            raise ValueError("rear_downforce_distribution deve estar entre 0 e 1.")

        # Limite de rotação do motor. Quando o mapa não cobre o limitador,
        # o último ponto do mapa é o limite efetivamente simulável.
        self.rev_limit_declared = float(rev_limit) if rev_limit is not None else max(self.rpm)
        if self.rev_limit_declared <= 0:
            raise ValueError("Rev Limit deve ser maior que zero.")
        self.rev_limit_effective = min(self.rev_limit_declared, max(self.rpm))

        # Gera um mapa operacional truncado/interpolado exatamente no limite
        # de RPM que pode ser representado pelos dados disponíveis.
        self.rpm_operacional, self.torque_operacional, self.power_operacional = self._gerar_mapa_operacional()

        self.potencia_max_hp = max(self.power_operacional)
        self.max_power = self.potencia_max_hp
        self.potencia_roda_kw = [p * self.drivetrain_efficiency for p in [
            r * t / 9549.2966 for r, t in zip(self.rpm_operacional, self.torque_operacional)
        ]]
        self.potencia_roda_hp = [pkw * 1.34102 for pkw in self.potencia_roda_kw]

    def _gerar_mapa_operacional(self):
        """Recorta/interpola o mapa até o limite de RPM efetivamente simulável."""
        rpm = list(self.rpm)
        torque = list(self.torque)
        limite = self.rev_limit_effective

        if limite < rpm[0]:
            raise ValueError(
                f"Rev Limit efetivo ({limite:.0f} rpm) está abaixo do primeiro ponto do mapa ({rpm[0]:.0f} rpm)."
            )

        novo_rpm = []
        novo_torque = []
        for r, t in zip(rpm, torque):
            if r <= limite:
                novo_rpm.append(r)
                novo_torque.append(t)
            else:
                break

        if novo_rpm[-1] < limite and limite < rpm[-1]:
            t_lim = interp_1d([limite], rpm, torque)[0]
            novo_rpm.append(limite)
            novo_torque.append(t_lim)

        potencia = [r * t / 9549.2966 * 1.34102 for r, t in zip(novo_rpm, novo_torque)]
        return novo_rpm, novo_torque, potencia

    @property
    def mapa_cobre_limite_rev(self):
        """Indica se o limitador declarado excede o mapa fornecido."""
        return self.rev_limit_declared > max(self.rpm) + 1e-9

    def potencia_motor_hp(self, rpm):
        """Retorna a potência do motor [HP] interpolada no mapa operacional."""
        return interp_1d([rpm], self.rpm_operacional, self.power_operacional)[0]

    def potencia_roda_hp_em_rpm(self, rpm):
        """Retorna a potência disponível na roda após a eficiência do drivetrain."""
        return self.potencia_motor_hp(rpm) * self.drivetrain_efficiency

    def curvas_potencia(self, fdr=None):
        """Retorna (velocidade, potência na roda, marcha) para cada marcha."""
        fdr = self.final_drive if fdr is None else float(fdr)
        curvas = []
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * fdr
            velocidade = [
                (r / 60.0) * 2.0 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm_operacional
            ]
            curvas.append((velocidade, list(self.potencia_roda_hp), i + 1))
        return curvas

    def curvas_torque(self, fdr=None):
        """Retorna (velocidade, torque na roda, marcha) para cada marcha."""
        fdr = self.final_drive if fdr is None else float(fdr)
        curvas = []
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * fdr
            velocidade = [
                (r / 60.0) * 2.0 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm_operacional
            ]
            torque_roda = [t * rel_total * self.drivetrain_efficiency for t in self.torque_operacional]
            curvas.append((velocidade, torque_roda, i + 1))
        return curvas

    def curvas_marcha(self, fdr=None):
        """Retorna curvas por marcha no formato (velocidade, força, índice)."""
        fdr = self.final_drive if fdr is None else float(fdr)
        if fdr <= 0:
            raise ValueError("FDR deve ser maior que zero.")

        curvas = []
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * fdr
            velocidade = [
                (r / 60.0) * 2.0 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm_operacional
            ]
            # A eficiência da transmissão reduz torque/potência na roda.
            forca = [
                (t * rel_total * self.drivetrain_efficiency) / self.raio_roda
                for t in self.torque_operacional
            ]
            curvas.append((velocidade, forca, i + 1))
        return curvas

    def forca_resistencia(self, v_kmh):
        """Calcula resistência aerodinâmica + resistência de rolamento [N]."""
        v_ms = max(float(v_kmh), 0.0) / 3.6
        drag = 0.5 * self.air_density * self.drag_coefficient * self.frontal_area * v_ms ** 2
        rolling = self.tire_rolling_drag * self.peso * 9.81
        return drag + rolling

    def downforce_total(self, v_kmh):
        """Calcula downforce total [N] usando Cl * A e a densidade do ar."""
        v_ms = max(float(v_kmh), 0.0) / 3.6
        return 0.5 * self.air_density * self.downforce_coefficient * self.frontal_area * v_ms ** 2

    def _normal_traseira(self, v_kmh, aceleracao=0.0):
        """Carga normal no eixo motriz traseiro [N].

        Sem entre-eixos/altura do CG, usa apenas distribuição estática + parcela
        traseira do downforce. Quando esses dois parâmetros são fornecidos no
        carro.csv, inclui uma aproximação simples de transferência longitudinal.
        """
        n_static = self.peso * 9.81 * self.rear_weight_distribution
        n_aero = self.downforce_total(v_kmh) * self.rear_downforce_distribution
        n_transfer = 0.0
        if self.cg_height is not None and self.wheelbase is not None and self.wheelbase > 0:
            n_transfer = self.peso * max(aceleracao, 0.0) * self.cg_height / self.wheelbase
        return n_static + n_aero + n_transfer

    def _limite_atrito(self, v_kmh, aceleracao=0.0):
        """Limite de força trativa no eixo motriz [N]."""
        return self.longitudinal_friction * self._normal_traseira(v_kmh, aceleracao)

    def forca_trativa_disponivel(self, v_kmh, fdr=None, marcha=None, considerar_atrito=True):
        """Maior força trativa disponível [N] em uma velocidade.

        Se ``marcha`` for fornecida, usa somente aquela marcha. Caso contrário,
        seleciona a maior força disponível dentre as marchas que alcançam a
        velocidade informada. A resistência ao movimento NÃO é subtraída aqui:
        esta função representa a capacidade de tração do powertrain.
        """
        curvas = self.curvas_marcha(fdr)
        candidatos = curvas if marcha is None else [curvas[int(marcha) - 1]]
        melhor = None
        for v_arr, f_arr, _ in candidatos:
            if v_arr[0] <= v_kmh <= v_arr[-1]:
                f = interp_1d([v_kmh], v_arr, f_arr)[0]
                if melhor is None or f > melhor:
                    melhor = f

        if melhor is None:
            return 0.0

        if considerar_atrito:
            # Iteração curta para capturar a dependência de transferência de
            # carga com a aceleração quando CG/entre-eixos estiverem disponíveis.
            f_efetiva = melhor
            for _ in range(4):
                a_est = max((f_efetiva - self.forca_resistencia(v_kmh)) / self.peso, 0.0)
                f_lim = self._limite_atrito(v_kmh, a_est)
                novo = min(melhor, f_lim)
                if abs(novo - f_efetiva) < 1e-6:
                    break
                f_efetiva = novo
            melhor = f_efetiva

        return melhor

    def forca_liquida(self, v_kmh, fdr=None, marcha=None, considerar_atrito=True):
        """Força líquida para aceleração [N] = tração - resistências."""
        return self.forca_trativa_disponivel(v_kmh, fdr, marcha, considerar_atrito) - self.forca_resistencia(v_kmh)

    def velocidade_maxima_marcha(self, marcha, fdr=None):
        """Velocidade máxima cinemática da marcha no limite de RPM [km/h]."""
        fdr = self.final_drive if fdr is None else float(fdr)
        rel = self.relacoes_marcha[int(marcha) - 1]
        return (self.rev_limit_effective / 60.0) * 2 * math.pi * self.raio_roda / (rel * fdr) * 3.6

    def calcular_pontos_troca(self, fdr=None, res=0.1, considerar_atrito=False):
        """Encontra os pontos de troca pelo cruzamento das forças de marchas consecutivas.

        Em vez de exigir dois pontos com exatamente a mesma velocidade, o método
        procura mudança de sinal da diferença F_marcha_atual - F_marcha_seguinte
        e interpola o cruzamento. Isso evita o problema de coincidência exata da
        malha numérica.
        """
        if res <= 0:
            raise ValueError("A resolução para pontos de troca deve ser maior que zero.")
        curvas = self.curvas_marcha(fdr)
        pontos = []
        for i in range(len(curvas) - 1):
            vi, fi, _ = curvas[i]
            vj, fj, _ = curvas[i + 1]
            v_ini = max(vi[0], vj[0])
            v_fim = min(vi[-1], vj[-1])
            if v_fim <= v_ini:
                pontos.append({"marcha_de": i + 1, "marcha_para": i + 2, "velocidade_km_h": v_fim, "rpm_de": self.rev_limit_effective, "rpm_para": None, "metodo": "fim_da_marcha"})
                continue

            grid = [v_ini]
            x = v_ini + res
            while x < v_fim:
                grid.append(x)
                x += res
            if grid[-1] != v_fim:
                grid.append(v_fim)

            diffs = []
            for v in grid:
                fi_v = interp_1d([v], vi, fi)[0]
                fj_v = interp_1d([v], vj, fj)[0]
                if considerar_atrito:
                    fi_v = min(fi_v, self._limite_atrito(v))
                    fj_v = min(fj_v, self._limite_atrito(v))
                diffs.append(fi_v - fj_v)

            cruzamento = None
            for k in range(len(grid) - 1):
                d0, d1 = diffs[k], diffs[k + 1]
                if d0 == 0:
                    cruzamento = grid[k]
                    break
                if d0 > 0 and d1 <= 0:
                    frac = d0 / (d0 - d1) if d0 != d1 else 0.0
                    cruzamento = grid[k] + frac * (grid[k + 1] - grid[k])
                    break

            if cruzamento is None:
                # Se não houver cruzamento, a troca não tem ponto de interseção
                # dentro do domínio comum; a proteção é usar o limite de RPM da
                # marcha atual.
                velocidade_troca = self.velocidade_maxima_marcha(i + 1, fdr)
                metodo = "limite_rpm"
            else:
                velocidade_troca = cruzamento
                metodo = "cruzamento_forcas"

            rel_de = self.relacoes_marcha[i] * (self.final_drive if fdr is None else float(fdr))
            rel_para = self.relacoes_marcha[i + 1] * (self.final_drive if fdr is None else float(fdr))
            rpm_de = velocidade_troca * (60 * rel_de) / (2 * math.pi * self.raio_roda * 3.6)
            rpm_para = velocidade_troca * (60 * rel_para) / (2 * math.pi * self.raio_roda * 3.6)
            pontos.append({
                "marcha_de": i + 1,
                "marcha_para": i + 2,
                "velocidade_km_h": velocidade_troca,
                "rpm_de": rpm_de,
                "rpm_para": rpm_para,
                "metodo": metodo,
            })
        return pontos

    def calcular_top_speed(self, fdr=None, res=0.25, considerar_atrito=True):
        """Calcula top speed por equilíbrio entre tração disponível e resistências.

        O resultado não é simplesmente a velocidade correspondente ao último RPM.
        Procuramos o ponto em que a força líquida muda de positiva para negativa.
        A velocidade também é limitada pelo RPM máximo que o mapa consegue representar.
        """
        if res <= 0:
            raise ValueError("A resolução deve ser maior que zero.")
        fdr = self.final_drive if fdr is None else float(fdr)
        vmax_gear = max(self.velocidade_maxima_marcha(i + 1, fdr) for i in range(len(self.relacoes_marcha)))
        grid = list(np.arange(0.0, vmax_gear + res * 0.5, res))
        if not grid or grid[-1] < vmax_gear:
            grid.append(vmax_gear)

        net = [self.forca_liquida(v, fdr=fdr, considerar_atrito=considerar_atrito) for v in grid]
        # Ignora a região inicial onde o mapa só começa acima de zero RPM.
        ultimo_pos = None
        for i in range(len(grid) - 1):
            if net[i] >= 0:
                ultimo_pos = i
            if net[i] >= 0 and net[i + 1] < 0:
                d0, d1 = net[i], net[i + 1]
                frac = d0 / (d0 - d1) if d0 != d1 else 0.0
                return grid[i] + frac * (grid[i + 1] - grid[i])

        if ultimo_pos is not None:
            return grid[ultimo_pos]
        return 0.0

    def calcular_aceleracao_maxima(self, fdr=None, res=0.25, considerar_atrito=True):
        """Calcula a capacidade máxima de aceleração longitudinal [m/s²].

        Ao contrário da simulação temporal, esta métrica varre a faixa inteira
        de velocidades e, em cada ponto, escolhe a melhor marcha disponível.
        Assim ela é mais adequada para comparação direta com o KPI de
        ``Maximum Longitudinal Acceleration`` do OptimumLap.
        """
        if res <= 0:
            raise ValueError("A resolução deve ser maior que zero.")
        fdr = self.final_drive if fdr is None else float(fdr)
        top = self.calcular_top_speed(fdr=fdr, res=res, considerar_atrito=considerar_atrito)
        if top <= 0:
            return 0.0
        vmax = min(top, max(self.velocidade_maxima_marcha(i + 1, fdr) for i in range(len(self.relacoes_marcha))))
        velocidades = list(np.arange(0.0, vmax + res * 0.5, res))
        if not velocidades or velocidades[-1] < vmax:
            velocidades.append(vmax)
        aceleracoes = [
            max(self.forca_liquida(v, fdr=fdr, considerar_atrito=considerar_atrito) / self.peso, 0.0)
            for v in velocidades
        ]
        return max(aceleracoes) if aceleracoes else 0.0

    def simular_aceleracao_fdr(
        self, fdr=None, velocidade_alvo=100.0, dt=0.01, shift_time=0.10,
        considerar_atrito=True, velocidade_inicial=0.0, max_tempo=30.0
    ):
        """Simula longitudinalmente uma aceleração 1D com trocas de marcha.

        Modelo:
            F_liquida = min(F_motor, F_pneu) - F_drag - F_rolling
            a = F_liquida / massa

        A troca ocorre nos pontos de cruzamento das curvas de força. Durante a
        troca, assume-se velocidade constante e adiciona-se ``shift_time`` ao
        cronômetro. Não há modelo de embreagem/largada; portanto, a largada em
        0 km/h é uma aproximação feita usando o menor ponto do mapa de motor.
        """
        if dt <= 0 or shift_time < 0 or max_tempo <= 0:
            raise ValueError("dt e max_tempo devem ser positivos e shift_time não pode ser negativo.")
        fdr = self.final_drive if fdr is None else float(fdr)
        alvo = float(velocidade_alvo)
        v = max(float(velocidade_inicial), 0.0)
        t = 0.0
        distancia = 0.0
        marcha = 1
        trocas = self.calcular_pontos_troca(fdr=fdr, res=max(0.05, dt * 10), considerar_atrito=considerar_atrito)
        proxima_troca = trocas[0]["velocidade_km_h"] if trocas else float("inf")
        historico = []
        max_accel = 0.0
        velocidade_alvo_atingida = None

        while t < max_tempo and v < alvo:
            # Se a marcha atingiu o limitador, realiza a troca programada.
            if marcha < len(self.relacoes_marcha) and v >= proxima_troca - 1e-9:
                historico.append({"tempo_s": t, "velocidade_km_h": v, "marcha_de": marcha, "marcha_para": marcha + 1})
                marcha += 1
                idx = marcha - 1
                proxima_troca = trocas[idx]["velocidade_km_h"] if idx < len(trocas) else float("inf")
                t += shift_time
                continue

            # O mapa de motor fornecido começa em 3500 rpm. Para a largada,
            # como não existe um modelo de embreagem, usamos o primeiro ponto
            # disponível da 1ª marcha até que o veículo entre na faixa do mapa.
            # Essa aproximação é explícita e afeta principalmente o tempo de
            # 0→alvo, não o cálculo de top speed.
            curvas_sim = self.curvas_marcha(fdr)
            curva_marcha = curvas_sim[marcha - 1]
            if marcha == 1 and v < curva_marcha[0][0]:
                f_trac = curva_marcha[1][0]
                if considerar_atrito:
                    f_trac = min(f_trac, self._limite_atrito(v))
            else:
                f_trac = self.forca_trativa_disponivel(
                    v, fdr=fdr, marcha=marcha, considerar_atrito=considerar_atrito
                )
            f_res = self.forca_resistencia(v)
            f_liq = f_trac - f_res
            if f_liq <= 0:
                break

            a = f_liq / self.peso
            max_accel = max(max_accel, a)
            v_ms = v / 3.6
            novo_v_ms = max(v_ms + a * dt, 0.0)
            novo_v = novo_v_ms * 3.6
            distancia += (v_ms + novo_v_ms) * 0.5 * dt

            if novo_v >= alvo:
                frac = (alvo - v) / (novo_v - v) if novo_v != v else 0.0
                tempo_alvo = t + frac * dt
                velocidade_alvo_atingida = alvo
                t = tempo_alvo
                v = alvo
                break

            v = novo_v
            t += dt
            historico.append({"tempo_s": t, "velocidade_km_h": v, "marcha": marcha, "aceleracao_m_s2": a})

        return {
            "fdr": fdr,
            "velocidade_alvo_km_h": alvo,
            "tempo_alvo_s": t if velocidade_alvo_atingida is not None else None,
            "top_speed_km_h": self.calcular_top_speed(fdr=fdr, res=max(0.05, dt * 10), considerar_atrito=considerar_atrito),
            "max_accel_m_s2": max_accel,
            "numero_trocas": len([h for h in historico if "marcha_de" in h]),
            "distancia_m": distancia,
            "atingiu_alvo": velocidade_alvo_atingida is not None,
            "historico": historico,
        }

    def avaliar_fdrs(self, fdrs, velocidade_alvo=100.0, dt=0.01, shift_time=0.10, considerar_atrito=True):
        """Avalia vários FDRs por métricas diretamente ligadas ao desempenho longitudinal."""
        resultados = {}
        for fdr in sorted(set(float(x) for x in fdrs)):
            simulacao = self.simular_aceleracao_fdr(
                fdr=fdr, velocidade_alvo=velocidade_alvo, dt=dt,
                shift_time=shift_time, considerar_atrito=considerar_atrito
            )
            resultados[fdr] = {
                "tempo_alvo_s": simulacao["tempo_alvo_s"],
                "top_speed_km_h": simulacao["top_speed_km_h"],
                "max_accel_m_s2": self.calcular_aceleracao_maxima(
                    fdr=fdr, res=max(0.05, dt * 10), considerar_atrito=considerar_atrito
                ),
                "numero_trocas": simulacao["numero_trocas"],
            }
        return resultados

    def drawRPMxTorquexPower(self):
        start_effectiveruntime = time.time()

        if(not(rc_isdef)):
            setMatplotParameters()
        
        # Cria figura de fundo
        fig, ax = plt.subplots()

        # --- Torque e Potência do Motor ---
        ax.set_xlabel('RPM')
        ax.set_ylabel('Torque [Nm]')
        ax.plot(self.rpm_operacional, self.torque_operacional, label=f'Torque', color='#FE5E41')
        index_torque_max = self.torque_operacional.index(max(self.torque_operacional))
        ax.scatter(self.rpm_operacional[index_torque_max], self.torque_operacional[index_torque_max], s=50.0, color='red', label=f'Max Engine Torque [Nm]: ' + str(round(self.torque[index_torque_max], 2)) + f'\nRPM: ' + str(self.rpm[index_torque_max]))

        ax2 = ax.twinx()
        ax2.set_ylabel('Power [hp]')
        ax2.plot(self.rpm_operacional, self.power_operacional, label=f'Power', color='#0B0500')
        index_power_max = self.power_operacional.index(max(self.power_operacional))
        ax2.scatter(self.rpm_operacional[index_power_max], self.power_operacional[index_power_max], s=50.0, color='cyan', label=f'Max Engine Power [hp]: ' + str(round(self.power[index_power_max], 2)) + f'\nRPM: ' + str(self.rpm[index_power_max]))

        plt.title('Torque and Power Curves')
        #plt.xlabel('RPM')
        #plt.ylabel('Torque [[Nm]')

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)

        ax.xaxis.set_major_locator(MultipleLocator(1000))
        ax.xaxis.set_minor_locator(MultipleLocator(500))
        ax.grid(False)
        ax2.grid(False)
        if self.rev_limit_declared > self.rev_limit_effective:
            ax2.axvline(self.rev_limit_declared, color="gray", linestyle=":", label=f"Rev Limit declarado: {self.rev_limit_declared:.0f} rpm")
        else:
            ax2.axvline(self.rev_limit_effective, color="gray", linestyle=":", label=f"Rev Limit: {self.rev_limit_effective:.0f} rpm")
        print("%s segundos de runtime para desenhar curva RPMxTorquexPower" % (time.time() - start_effectiveruntime))
        _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
        plt.show()

    def gerar_pot_vroda(self, fdr=None):
        """Plota potência na roda por marcha. Retorna as curvas usadas."""
        fdr = self.final_drive if fdr is None else float(fdr)
        fig, ax = plt.subplots(figsize=(10, 6))
        curvas = self.curvas_potencia(fdr)
        for v, p, idx in curvas:
            ax.plot(v, p, label=f"Marcha {idx}")
        for i, ponto in enumerate(self.calcular_pontos_troca(fdr=fdr, res=0.1)):
            ax.scatter(ponto["velocidade_km_h"], self.potencia_roda_hp[-1], marker="D", zorder=5)
        ax.set_title(f"Potência na Roda vs Velocidade — FDR = {fdr:.4f}")
        ax.set_xlabel("Velocidade (km/h)")
        ax.set_ylabel("Potência na roda (HP)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        plt.tight_layout()
        _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
        plt.show()
        return [[v, p, idx] for v, p, idx in curvas]

    def gerar_troda_vroda(self, fdr=None):
        """Plota torque na roda por marcha, já considerando eficiência."""
        fdr = self.final_drive if fdr is None else float(fdr)
        fig, ax = plt.subplots(figsize=(10, 6))
        curvas = self.curvas_torque(fdr)
        for v, torque, idx in curvas:
            ax.plot(v, torque, label=f"Marcha {idx}")
        pontos = self.calcular_pontos_troca(fdr=fdr, res=0.1)
        for i, ponto in enumerate(pontos):
            # O torque de troca é obtido diretamente na curva da marcha de origem.
            valor = interp_1d([ponto["velocidade_km_h"]], curvas[i][0], curvas[i][1])[0]
            ax.scatter(ponto["velocidade_km_h"], valor, marker="D", zorder=5)
        ax.set_title(f"Torque na Roda vs Velocidade — FDR = {fdr:.4f}")
        ax.set_xlabel("Velocidade (km/h)")
        ax.set_ylabel("Torque na roda (N.m)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        plt.tight_layout()
        _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
        plt.show()
        return [[v, torque, idx] for v, torque, idx in curvas]

    def gerar_froda_vroda(self, fdr=None, considerar_atrito=False):
        """Plota força trativa por marcha, sem confundir força disponível com força líquida."""
        fdr = self.final_drive if fdr is None else float(fdr)
        fig, ax = plt.subplots(figsize=(10, 6))
        curvas = self.curvas_marcha(fdr)
        for v, força, idx in curvas:
            ax.plot(v, força, label=f"Marcha {idx}")
        if considerar_atrito:
            vs = np.linspace(0, max(self.velocidade_maxima_marcha(i + 1, fdr) for i in range(len(self.relacoes_marcha))), 250)
            ax.plot(vs, [self._limite_atrito(v) for v in vs], linestyle="--", label="Limite de aderência")
        ax.set_title(f"Força Trativa na Roda vs Velocidade — FDR = {fdr:.4f}")
        ax.set_xlabel("Velocidade (km/h)")
        ax.set_ylabel("Força trativa (N)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        plt.tight_layout()
        _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
        plt.show()
        return [[v, força, idx] for v, força, idx in curvas]

    def gerar_curva_unica_froda_vroda_v1(self, fdr=None, res=0.125, plotar=True):
        """Gera a envoltória de força disponível na roda para um FDR.

        Esta versão antiga permanece como API de compatibilidade. O cálculo foi
        direcionado para a mesma função física usada pelas demais análises,
        evitando que existam duas definições diferentes de força na roda.
        """
        curva = self.gerar_curva_unica_froda_vroda_v2(
            fdr=fdr, res=res, considerar_atrito=False, plotar=False,
            mostrar_marchas=plotar, mostrar_limite_atrito=False
        )
        if plotar and curva:
            fig, ax = plt.subplots(figsize=(10, 6))
            if fdr is None:
                fdr = self.final_drive
            if plotar:
                for v_g, f_g, idx in self.curvas_marcha(fdr):
                    ax.plot(v_g, f_g, linestyle="--", linewidth=1.1, alpha=0.35, label=f"Marcha {idx}")
            ax.plot([p[0] for p in curva], [p[1] for p in curva], linewidth=2.5, label="Curva Única (Envoltória)")
            ax.set_title(f"Curva Única de Força Trativa — FDR = {fdr:.4f}")
            ax.set_xlabel("Velocidade (km/h)")
            ax.set_ylabel("Força Trativa (N)")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="best")
            plt.tight_layout()
            _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
            plt.show()
        return curva

    def gerar_curva_unica_froda_vroda_v2(
        self, fdr=None, res=0.125, considerar_atrito=False, plotar=False,
        mostrar_marchas=True, mostrar_limite_atrito=True, salvar_em=None,
    ):
        """Gera a envoltória de máxima força trativa disponível.

        Diferentemente da versão anterior, ``fdr`` agora é realmente usado no
        cálculo e a mesma eficiência do drivetrain e o mesmo modelo de aderência
        são usados por toda a aplicação.
        """
        if res <= 0:
            raise ValueError("A resolução deve ser maior que zero.")
        fdr = self.final_drive if fdr is None else float(fdr)
        curvas = self.curvas_marcha(fdr)
        v_min = min(c[0][0] for c in curvas)
        v_max = max(c[0][-1] for c in curvas)
        n = int(math.floor((v_max - v_min) / res + 1e-9)) + 1
        velocidades = [round(v_min + k * res, 5) for k in range(n)]
        if velocidades[-1] < v_max - 1e-9:
            velocidades.append(round(v_max, 5))

        curva = []
        for v in velocidades:
            melhor = self.forca_trativa_disponivel(v, fdr=fdr, considerar_atrito=considerar_atrito)
            if melhor > 0:
                curva.append([v, round(melhor, 3)])

        if plotar and curva:
            fig, ax = plt.subplots(figsize=(10, 6))
            if mostrar_marchas:
                for v_g, f_g, idx in curvas:
                    ax.plot(v_g, f_g, linestyle="--", linewidth=1.2, alpha=0.5, label=f"Marcha {idx}")
            ax.plot([p[0] for p in curva], [p[1] for p in curva], linewidth=2.8, label="Curva única (envoltória)")
            if mostrar_limite_atrito:
                vels = np.linspace(0, max(120, v_max), 250)
                ax.plot(vels, [self._limite_atrito(v) for v in vels], linestyle="--", linewidth=1.5, label="Limite de aderência")
            ax.set_title(f"Curva Única de Força Trativa vs Velocidade — FDR = {fdr:.4f}")
            ax.set_xlabel("Velocidade (km/h)")
            ax.set_ylabel("Força Trativa (N)")
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            ax.grid(True, which="both", alpha=0.3)
            ax.legend(loc="best")
            plt.tight_layout()
            _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
            if salvar_em:
                fig.savefig(salvar_em, dpi=180, bbox_inches="tight")
            plt.show()
        return curva

    def calcular_perda_area_potencia(self, fdr=None, res=0.125, plotar=True):
        """Métrica secundária de aproveitamento: área real / potência ideal.

        Esta métrica NÃO deve ser usada isoladamente para escolher o FDR. Ela é
        mantida para compatibilidade e para mostrar quão próxima a envoltória de
        força está de uma curva de potência constante, mas o principal critério
        recomendado é a simulação longitudinal (tempo de aceleração/top speed)
        e a comparação com o Batch Run.
        """
        if res <= 0:
            raise ValueError("A resolução deve ser maior que zero.")
        fdr = self.final_drive if fdr is None else float(fdr)
        curva = self.gerar_curva_unica_froda_vroda_v2(fdr=fdr, res=res, considerar_atrito=False, plotar=False)
        if len(curva) < 2:
            return float("nan")

        rpm_pico_torque = self.rpm_operacional[self.torque_operacional.index(max(self.torque_operacional))]
        rpm_pico_power = self.rpm_operacional[self.power_operacional.index(max(self.power_operacional))]
        rel_1a = self.relacoes_marcha[0] * fdr
        rel_ult = self.relacoes_marcha[-1] * fdr
        v_lim_inf = (rpm_pico_torque / 60.0) * 2 * math.pi * self.raio_roda / rel_1a * 3.6
        v_lim_sup = (rpm_pico_power / 60.0) * 2 * math.pi * self.raio_roda / rel_ult * 3.6
        if v_lim_sup <= v_lim_inf:
            raise ValueError("Intervalo de integração inválido para a perda de área.")

        v_integ = list(np.arange(v_lim_inf, v_lim_sup + res * 0.5, res))
        if v_integ[-1] < v_lim_sup:
            v_integ.append(v_lim_sup)
        p_watts = self.potencia_max_hp * 745.7 * self.drivetrain_efficiency
        f_pot = []
        f_real = []
        xv = [p[0] for p in curva]
        yv = [p[1] for p in curva]
        for v in v_integ:
            v_ms = v / 3.6
            f_pot.append(p_watts / v_ms)
            f_real.append(interp_1d([v], xv, yv)[0])

        area_pot = 0.0
        area_real = 0.0
        for i in range(len(v_integ) - 1):
            dv = v_integ[i + 1] - v_integ[i]
            area_pot += 0.5 * (f_pot[i] + f_pot[i + 1]) * dv
            area_real += 0.5 * (f_real[i] + f_real[i + 1]) * dv
        razao = (area_pot - area_real) / area_pot

        if plotar:
            fig, ax = plt.subplots(figsize=(11, 6.5))
            ax.plot(v_integ, f_real, label="Força trativa disponível")
            ax.plot(v_integ, f_pot, label="Força equivalente à potência máxima disponível")
            ax.fill_between(v_integ, f_real, f_pot, where=[fp >= fr for fp, fr in zip(f_pot, f_real)], alpha=0.25, hatch="//", label="Área de perda")
            ax.axvline(v_lim_inf, linestyle=":", label=f"Limite inferior: {v_lim_inf:.1f} km/h")
            ax.axvline(v_lim_sup, linestyle=":", label=f"Limite superior: {v_lim_sup:.1f} km/h")
            ax.set_title(f"Métrica secundária de área — FDR = {fdr:.4f} | Perda = {razao:.3%}")
            ax.set_xlabel("Velocidade (km/h)")
            ax.set_ylabel("Força (N)")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="best")
            plt.tight_layout()
            _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
            plt.show()
        return razao

    def calcular_perda_area_potencia_range(self, fdr_range, res=0.125):
        """Calcula a métrica secundária de perda de área para vários FDRs."""
        resultados = []
        for fdr in fdr_range:
            resultados.append(self.calcular_perda_area_potencia(fdr=float(fdr), res=res, plotar=False))
        return [list(fdr_range), resultados]

    def gerar_pot_vroda_unificada(self, fdr=None, res=0.125, plotar=True):
        """Gera e plota a curva unificada de máxima potência na roda vs velocidade.

        Parâmetros:
            fdr (float, opcional): Relação final de transmissão. Se None, utiliza
            self.final_drive.
            res (float): Passo da resolução de velocidade em km/h.
            plotar (bool): Se True, exibe o gráfico.

        Retorno:
            list: [V_max, P_max] -> Uma lista contendo duas sublistas:
                - V_max: Velocidades da roda (km/h)
                - P_max: Maiores potências na roda para cada velocidade (HP)
        """
        if fdr == None:
            fdr = self.final_drive

        # 1. Gera as curvas de velocidade e potência para cada marcha
        curvas_marchas = []
        for rel in self.relacoes_marcha:
            rel_total = rel * fdr

            velocidade = [
                (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm
            ]
            potencia_roda = self.potencia_roda_hp  # Potência após eficiência do drivetrain

            curvas_marchas.append((velocidade, potencia_roda))

        # 2. Define os limites globais de velocidade (sem perda de dados nas extremidades)
        v_min = min(v_arr[0] for v_arr, _ in curvas_marchas)
        v_max = max(v_arr[-1] for v_arr, _ in curvas_marchas)

        n_pontos = int(round((v_max - v_min) / res)) + 1
        malha_v = [round(v_min + k * res, 4) for k in range(n_pontos)]

        # 3. Encontra a maior potência entre as marchas para cada ponto de velocidade
        V_max = []
        P_max = []

        for v in malha_v:
            melhor_p = None
            for velocidade, potencia in curvas_marchas:
                # Verifica se v está dentro da faixa real da marcha
                if v < velocidade[0] or v > velocidade[-1]:
                    continue

                p = interp_1d([v], velocidade, potencia)[0]
                if melhor_p is None or p > melhor_p:
                    melhor_p = p

            if melhor_p is not None:
                V_max.append(v)
                P_max.append(round(melhor_p, 3))

        # 4. Plotagem do Gráfico
        if plotar and V_max:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plota as curvas individuais de cada marcha em tracejado
            for i, (v_g, p_g) in enumerate(curvas_marchas):
                ax.plot(
                    v_g,
                    p_g,
                    linestyle="--",
                    linewidth=1.2,
                    alpha=0.4,
                    zorder=i + 3,
                    label=f"Marcha {i+1}",
                )

            # Plota a curva unificada em destaque (envoltória)
            ax.plot(
                V_max,
                P_max,
                color="red",
                linewidth=2.5,
                zorder=20,
                label="Potência Máxima (Unificada)",
            )

            # Configurações estéticas no padrão Matplotlib do seu código original
            plt.xlabel("Speed (km/h)")
            plt.ylabel("Wheel Power (HP)")
            plt.title("Curva Unificada de Potência na Roda vs Velocidade")
            plt.legend(loc="lower right")

            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.grid(True, which="minor", linestyle=":", alpha=0.6)
            ax.grid(True, which="major", linestyle="-", alpha=0.8)

            plt.tight_layout()
            _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
            plt.show()

        # Retorna a lista contendo as duas listas [Velocidades, Potências]
        return [V_max, P_max]

    def comparar_pot_vroda_fdrs(
        self, fdr_list, res=0.125, cmap_name="viridis", plotar=True
    ):
        """Calcula e plota no mesmo gráfico as curvas unificadas de potência na roda

        para diferentes Relações Finais de Transmissão (FDR) em degradê de cores.

        Parâmetros:
            fdr_list (list): Lista com os valores de FDR a serem comparados (ex:
            [3.2, 3.8, 4.2, 4.8]).
            res (float): Resolução do passo de velocidade em km/h.
            cmap_name (str): Nome do colormap do Matplotlib para o degradê (ex:
            'viridis', 'plasma', 'coolwarm', 'rainbow').
            plotar (bool): Se True, exibe o gráfico gerado.

        Retorno:
            dict: Dicionário no formato {fdr: [V_max, P_max]}
        """

        resultados = {}
        n_fdrs = len(fdr_list)

        # 1. Configura a paleta em degradê de acordo com a quantidade de FDRs
        cmap = plt.colormaps.get_cmap(cmap_name)
        colors = [
            cmap(i / (n_fdrs - 1)) if n_fdrs > 1 else cmap(0.5)
            for i in range(n_fdrs)
        ]

        fig, ax = plt.subplots(figsize=(11, 6.5)) if plotar else (None, None)

        # 2. Processa a curva unificada para cada FDR da lista
        for idx, fdr in enumerate(fdr_list):
            curvas_marchas = []

            # Calcula a velocidade de cada marcha para o FDR atual
            for rel in self.relacoes_marcha:
                rel_total = rel * fdr
                velocidade = [
                    (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                    for r in self.rpm
                ]
                curvas_marchas.append((velocidade, self.potencia_roda_hp))

            # Define os limites globais de velocidade para este FDR
            v_min = min(v_arr[0] for v_arr, _ in curvas_marchas)
            v_max = max(v_arr[-1] for v_arr, _ in curvas_marchas)

            n_pontos = int(round((v_max - v_min) / res)) + 1
            malha_v = [round(v_min + k * res, 4) for k in range(n_pontos)]

            # Encontra a envoltória de potência máxima
            V_max = []
            P_max = []

            for v in malha_v:
                melhor_p = None
                for velocidade, potencia in curvas_marchas:
                    if v < velocidade[0] or v > velocidade[-1]:
                        continue

                    p = interp_1d([v], velocidade, potencia)[0]
                    if melhor_p is None or p > melhor_p:
                        melhor_p = p

                if melhor_p is not None:
                    V_max.append(v)
                    P_max.append(round(melhor_p, 3))

            resultados[fdr] = [V_max, P_max]

            # 3. Plota a curva do FDR atual no gráfico compartilhado
            if plotar and V_max:
                ax.plot(
                    V_max,
                    P_max,
                    color=colors[idx],
                    linewidth=2.2,
                    zorder=10 + idx,
                    label=f"FDR = {fdr:.2f}",
                )

        # 4. Configurações estéticas do gráfico final
        if plotar:
            ax.set_xlabel("Speed (km/h)")
            ax.set_ylabel("Wheel Power (HP)")
            ax.set_title(
                "Comparativo de Potência Unificada na Roda para Múltiplas Relações Finais (FDR)"
            )
            ax.legend(loc="lower right", fontsize=9, ncol=max(1, n_fdrs // 5))

            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.grid(True, which="minor", linestyle=":", alpha=0.6)
            ax.grid(True, which="major", linestyle="-", alpha=0.8)

            plt.tight_layout()
            _add_logo_watermark(ax, alpha=0.05, zoom=0.50)
            plt.show()

        return resultados

# =============================================================================
# INTERFACE DE USO
# =============================================================================



class InterfacePlotterPowertrain:
    """Interface de terminal para executar os estudos do powertrain.

    A interface não altera a lógica dos cálculos da classe Carro. Ela apenas:
      - carrega os arquivos do carro;
      - apresenta um menu em loop;
      - solicita parâmetros quando necessários;
      - guarda os últimos resultados calculados;
      - exporta resultados para CSV;
      - mantém os gráficos gerados pelo Matplotlib disponíveis na tela.
    """

    def __init__(self):
        # Os três arquivos são mantidos independentes. Isso permite trocar
        # somente o mapa de torque ou somente o Batch Run sem recarregar tudo.
        self.carro = None
        self.config_carro = None
        self.arquivo_carro = None
        self.arquivo_rpm_torque = None
        self.batch = None
        self.arquivo_batch = None
        self.resultados = {}
        self.pasta_saida = Path.cwd() / "resultados_plotter"
        self.pasta_saida.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Entrada de dados
    # -------------------------------------------------------------------------
    @staticmethod
    def _float(prompt, default=None, minimo=None):
        while True:
            texto = input(prompt).strip()
            if texto == "" and default is not None:
                return float(default)
            try:
                valor = float(texto.replace(',', '.'))
                if minimo is not None and valor < minimo:
                    print(f"Valor deve ser >= {minimo}.")
                    continue
                return valor
            except ValueError:
                print("Entrada inválida. Digite um número.")

    @staticmethod
    def _int(prompt, default=None, minimo=None):
        while True:
            texto = input(prompt).strip()
            if texto == "" and default is not None:
                return int(default)
            try:
                valor = int(texto)
                if minimo is not None and valor < minimo:
                    print(f"Valor deve ser >= {minimo}.")
                    continue
                return valor
            except ValueError:
                print("Entrada inválida. Digite um número inteiro.")

    @staticmethod
    def _sim_nao(prompt, default=True):
        sufixo = "[S/n]" if default else "[s/N]"
        while True:
            valor = input(f"{prompt} {sufixo}: ").strip().lower()
            if not valor:
                return default
            if valor in ("s", "sim", "y", "yes"):
                return True
            if valor in ("n", "nao", "não", "no"):
                return False
            print("Responda S ou N.")

    def _parametros_fisicos_efetivos(self):
        """Combina parâmetros do carro.csv com valores do Batch Run.

        O carro.csv é a fonte primária. O Batch Run só preenche parâmetros que
        não foram explicitamente definidos no carro.csv.
        """
        cfg = self.config_carro or {}
        batch_params = getBatchVehicleParameters(self.batch) if self.batch is not None else {}
        defaults = {
            "drivetrain_efficiency": 0.96,
            "drag_coefficient": 1.34,
            "downforce_coefficient": 3.54,
            "frontal_area": 1.14,
            "air_density": 1.16,
            "tire_rolling_drag": 0.01,
            "rev_limit": None,
            "longitudinal_friction": cfg.get("tire_coefficient", 2.204),
            "lateral_friction": cfg.get("tire_coefficient", 2.204),
            "rear_weight_distribution": 0.55,
            "rear_downforce_distribution": 0.60,
            "cg_height": None,
            "wheelbase": None,
        }
        for chave in defaults:
            if cfg.get(chave) is not None:
                defaults[chave] = cfg[chave]
            elif chave in batch_params:
                defaults[chave] = batch_params[chave]
        return defaults

    def _montar_carro(self):
        """Cria o objeto Carro quando configuração + curva do motor estão disponíveis."""
        if self.config_carro is None or self.arquivo_rpm_torque is None:
            self.carro = None
            return False

        cfg = self.config_carro
        relacoes = cfg["gear_ratios"] if "gear_ratios" in cfg else getGearRatios(str(cfg["gear_ratio_file"]))
        fis = self._parametros_fisicos_efetivos()
        self.carro = Carro(
            getRPMxTorquePoints(str(self.arquivo_rpm_torque)),
            relacoes,
            float(cfg["primary_ratio"]),
            float(cfg["secondary_ratio"]),
            float(cfg["wheel_radius"]),
            float(cfg.get("weight", 240.0)),
            float(cfg.get("tire_coefficient", 2.204)),
            **fis,
        )
        self.resultados.clear()
        return True

    def carregar_carro(self):
        """Carrega somente as configurações do veículo."""
        print("\n--- Carregamento das configurações do veículo ---")
        caminho = input("Caminho do carro.csv: ").strip().strip('"')
        if not caminho:
            print("Operação cancelada.")
            return
        caminho = Path(caminho)
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            return
        try:
            self.config_carro = getCarroConfig(str(caminho))
            self.arquivo_carro = caminho
            montou = self._montar_carro()
            if montou:
                print("\nVeículo carregado com sucesso (carro.csv + curva RPM x Torque).")
                self.mostrar_resumo_carro()
            else:
                print("Configurações do carro carregadas. Agora selecione a curva RPM x Torque.")
        except Exception as exc:
            print(f"Erro ao carregar as configurações do veículo: {exc}")

    def carregar_rpm_torque(self):
        """Seleciona o arquivo externo da curva RPM x Torque e remonta o carro."""
        print("\n--- Carregamento da curva RPM x Torque ---")
        caminho = input("Caminho do CSV RPM x Torque: ").strip().strip('"')
        if not caminho:
            print("Operação cancelada.")
            return
        caminho = Path(caminho)
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            return
        try:
            # Validamos o arquivo imediatamente; o mapa é lido novamente na
            # montagem do objeto para manter uma única fonte de cálculo.
            getRPMxTorquePoints(str(caminho))
            self.arquivo_rpm_torque = caminho
            if self._montar_carro():
                print("Curva RPM x Torque carregada e veículo atualizado.")
                self.mostrar_resumo_carro()
            else:
                print("Curva RPM x Torque carregada. Selecione o carro.csv para completar o veículo.")
        except Exception as exc:
            print(f"Erro ao carregar a curva RPM x Torque: {exc}")

    def carregar_batch(self):
        """Seleciona e interpreta um CSV exportado do Batch Run do OptimumLap."""
        print("\n--- Carregamento do Batch Run ---")
        caminho = input("Caminho do CSV da Batch Run: ").strip().strip('"')
        if not caminho:
            print("Operação cancelada.")
            return
        caminho = Path(caminho)
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            return
        try:
            self.batch = getBatchRun(str(caminho), show_data_index=0)
            self.arquivo_batch = caminho
            print("Batch Run carregado com sucesso.")
            print(f"Runs de FDR: {len(_buscar_linha_por_rotulo(self.batch, 'Final Drive Ratio [-]'))}")
        except Exception as exc:
            print(f"Erro ao carregar o Batch Run: {exc}")

    def mostrar_resumo_carro(self):
        if self.carro is None:
            print("Nenhum veículo completamente carregado. Carregue carro.csv e o CSV RPM x Torque.")
            if self.config_carro:
                print(f"Configuração: {self.arquivo_carro}")
            if self.arquivo_rpm_torque:
                print(f"Curva RPM x Torque: {self.arquivo_rpm_torque}")
            return

        c = self.carro
        print("\n--- Resumo do veículo ---")
        print(f"Carro.csv: {self.arquivo_carro}")
        if self.config_carro.get("name"):
            print(f"Nome do carro: {self.config_carro['name']}")
        print(f"Curva RPM x Torque: {self.arquivo_rpm_torque}")
        print(f"RPM: {c.rpm[0]:.0f} -> {c.rpm[-1]:.0f}")
        print(f"Torque máximo: {max(c.torque):.2f} Nm")
        print(f"Potência máxima: {c.max_power:.2f} HP")
        print(f"Relações de marcha: {[round(x, 4) for x in c.relacoes_marcha]}")
        print(f"Relação primária: {c.relacao_primaria:.4f}")
        print(f"Relação secundária: {c.relacao_secundaria:.4f}")
        print(f"FDR atual: {c.final_drive:.4f}")
        print(f"Raio da roda: {c.raio_roda:.4f} m")
        print(f"Peso: {c.peso:.2f} kg")
        print(f"Coeficiente de pneu: {c.Cat_pneu:.4f}")

    def _salvar_resultado(self, nome, dados):
        self.resultados[nome] = dados
        print(f"Resultado '{nome}' armazenado em memória.")

    # -------------------------------------------------------------------------
    # Exportação CSV
    # -------------------------------------------------------------------------
    @staticmethod
    def _escrever_linhas_csv(caminho, cabecalho, linhas):
        with open(caminho, 'w', newline='', encoding='utf-8-sig') as arquivo:
            writer = csv.writer(arquivo, delimiter=';')
            writer.writerow(cabecalho)
            writer.writerows(linhas)

    def exportar_resultado(self, nome=None):
        if not self.resultados:
            print("Não há resultados calculados para exportar.")
            return

        if nome is None:
            nomes = list(self.resultados.keys())
            print("\nResultados disponíveis:")
            for i, n in enumerate(nomes, 1):
                print(f"{i}) {n}")
            escolha = self._int("Escolha o resultado: ", minimo=1)
            if escolha > len(nomes):
                print("Opção inválida.")
                return
            nome = nomes[escolha - 1]

        if nome not in self.resultados:
            print("Resultado não encontrado.")
            return

        dados = self.resultados[nome]
        arquivo = input(
            f"Nome do arquivo [{nome}.csv]: "
        ).strip()
        if not arquivo:
            arquivo = f"{nome}.csv"
        if not arquivo.lower().endswith('.csv'):
            arquivo += '.csv'

        caminho = Path(arquivo)
        if not caminho.is_absolute():
            caminho = self.pasta_saida / caminho
        caminho.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._exportar_dados_genericos(caminho, dados)
            print(f"CSV exportado: {caminho.resolve()}")
        except Exception as exc:
            print(f"Erro ao exportar CSV: {exc}")

    def _exportar_dados_genericos(self, caminho, dados):
        """Converte os principais formatos retornados pelo código em CSV."""

        # Caso: dicionário de séries com mesmo comprimento, por exemplo
        # {"FDR": [...], "Batch": [...], "Modelo": [...]}.
        if isinstance(dados, dict):
            chaves = list(dados.keys())
            valores = [dados[k] for k in chaves]
            if valores and all(isinstance(v, (list, tuple, np.ndarray)) for v in valores):
                comprimentos = {len(v) for v in valores}
                if len(comprimentos) == 1 and all(
                    all(isinstance(x, (int, float, np.number)) for x in v) for v in valores
                ):
                    self._escrever_linhas_csv(caminho, chaves, zip(*valores))
                    return

            # Caso legado: dict {nome: [x, y]}.
            linhas = []
            for chave, valor in dados.items():
                if isinstance(valor, (list, tuple)) and len(valor) == 2:
                    x, y = valor
                    if isinstance(x, (list, tuple, np.ndarray)) and isinstance(y, (list, tuple, np.ndarray)):
                        for xx, yy in zip(x, y):
                            linhas.append([chave, xx, yy])
                        continue
                linhas.append([chave, valor])
            if linhas and len(linhas[0]) == 3:
                self._escrever_linhas_csv(caminho, ["Serie", "X", "Y"], linhas)
            else:
                self._escrever_linhas_csv(caminho, ["Parametro", "Valor"], linhas)
            return

        # Caso: [x, y] com duas séries de mesmo tamanho.
        if isinstance(dados, (list, tuple)) and len(dados) == 2:
            x, y = dados
            if isinstance(x, (list, tuple, np.ndarray)) and isinstance(
                y, (list, tuple, np.ndarray)
            ):
                if len(x) == len(y):
                    self._escrever_linhas_csv(
                        caminho,
                        ["X", "Y"],
                        zip(x, y),
                    )
                    return

        # Caso: mapa RPM x torque, [[rpm, torque], ...]
        if isinstance(dados, (list, tuple)) and dados:
            if all(isinstance(row, (list, tuple)) for row in dados):
                largura = max(len(row) for row in dados)
                cabecalho = [f"Coluna_{i+1}" for i in range(largura)]
                self._escrever_linhas_csv(caminho, cabecalho, dados)
                return

        # Caso escalar: perda de área etc.
        self._escrever_linhas_csv(caminho, ["Valor"], [[dados]])

    def exportar_dados_base(self):
        if self.carro is None:
            print("Nenhum veículo carregado.")
            return

        self.resultados["mapa_rpm_torque"] = [self.carro.rpm, self.carro.torque]
        self.resultados["relacoes_marcha"] = list(self.carro.relacoes_marcha)
        self.resultados["dados_potencia"] = [self.carro.rpm, self.carro.power]

        print("Dados-base preparados para exportação:")
        print("  - mapa_rpm_torque")
        print("  - relacoes_marcha")
        print("  - dados_potencia")

    def exportar_todos(self):
        if not self.resultados:
            print("Não há resultados para exportar.")
            return

        for nome, dados in self.resultados.items():
            caminho = self.pasta_saida / f"{nome}.csv"
            try:
                self._exportar_dados_genericos(caminho, dados)
                print(f"OK: {caminho}")
            except Exception as exc:
                print(f"Falha em {nome}: {exc}")

    # -------------------------------------------------------------------------
    # Estudos
    # -------------------------------------------------------------------------
    def executar_grafico(self, opcao):
        if self.carro is None:
            print("Carregue um veículo primeiro.")
            return

        c = self.carro
        try:
            if opcao == 1:
                c.drawRPMxTorquexPower()
                self._salvar_resultado("rpm_torque_potencia", [c.rpm, c.torque])

            elif opcao == 2:
                fdr = self._float(
                    f"FDR [{c.final_drive:.4f}]: ",
                    default=c.final_drive,
                )
                dados = c.gerar_pot_vroda(fdr)
                self._salvar_resultado(f"potencia_roda_fdr_{fdr:.4f}", dados)

            elif opcao == 3:
                dados = c.gerar_troda_vroda(c.final_drive)
                self._salvar_resultado("torque_roda", dados)

            elif opcao == 4:
                dados = c.gerar_froda_vroda(c.final_drive)
                self._salvar_resultado("forca_trativa_marchas", dados)

            elif opcao == 5:
                fdr = self._float(
                    f"FDR [{c.final_drive:.4f}]: ",
                    default=c.final_drive,
                )
                res = self._float("Resolução km/h [0.125]: ", default=0.125, minimo=0.0001)
                dados = c.gerar_curva_unica_froda_vroda_v1(fdr=fdr, res=res, plotar=True)
                self._salvar_resultado(f"forca_unificada_fdr_{fdr:.4f}", dados)

            elif opcao == 6:
                res = self._float("Resolução km/h [0.125]: ", default=0.125, minimo=0.0001)
                atrito = self._sim_nao("Considerar limite de atrito?", default=False)
                mostrar_marchas = self._sim_nao("Mostrar marchas?", default=True)
                mostrar_limite = self._sim_nao("Mostrar limite de atrito?", default=True)
                dados = c.gerar_curva_unica_froda_vroda_v2(
                    res=res,
                    considerar_atrito=atrito,
                    plotar=True,
                    mostrar_marchas=mostrar_marchas,
                    mostrar_limite_atrito=mostrar_limite,
                )
                self._salvar_resultado("forca_unificada_v2", dados)

            elif opcao == 7:
                fdr = self._float(
                    f"FDR [{c.final_drive:.4f}]: ",
                    default=c.final_drive,
                )
                res = self._float("Resolução km/h [0.125]: ", default=0.125, minimo=0.0001)
                razao = c.calcular_perda_area_potencia(fdr=fdr, res=res, plotar=True)
                self._salvar_resultado(f"perda_area_fdr_{fdr:.4f}", razao)
                print(f"Razão de perda de área: {razao:.6f} ({razao:.2%})")

            elif opcao == 8:
                inicio = self._float("FDR inicial [6.5]: ", default=6.5)
                fim = self._float("FDR final [8.5]: ", default=8.5)
                passo = self._float("Passo entre FDRs [0.1]: ", default=0.1, minimo=0.000001)
                if fim < inicio:
                    inicio, fim = fim, inicio
                fdrs = list(np.arange(inicio, fim + passo * 0.5, passo))
                fdrs = [round(float(x), 8) for x in fdrs]
                res = self._float("Resolução km/h [0.125]: ", default=0.125, minimo=0.0001)
                dados = c.calcular_perda_area_potencia_range(fdrs, res=res)
                self._salvar_resultado("perda_area_range_fdr", dados)

            elif opcao == 9:
                fdr = self._float(
                    f"FDR [{c.final_drive:.4f}]: ",
                    default=c.final_drive,
                )
                res = self._float("Resolução km/h [0.125]: ", default=0.125, minimo=0.0001)
                dados = c.gerar_pot_vroda_unificada(fdr=fdr, res=res, plotar=True)
                self._salvar_resultado(f"potencia_unificada_fdr_{fdr:.4f}", dados)

            elif opcao == 10:
                texto = input(
                    "FDRs separados por espaço ou vírgula [6.5 7.0 7.5 8.0]: "
                ).strip()
                if not texto:
                    fdrs = [6.5, 7.0, 7.5, 8.0]
                else:
                    fdrs = [
                        float(x.replace(',', '.'))
                        for x in texto.replace(',', ' ').split()
                    ]
                fdrs = sorted(set(fdrs))
                res = self._float("Resolução km/h [0.125]: ", default=0.125, minimo=0.0001)
                dados = c.comparar_pot_vroda_fdrs(fdrs, res=res, plotar=True)
                self._salvar_resultado("comparacao_potencia_fdrs", dados)

            else:
                print("Opção de gráfico inválida.")

        except Exception as exc:
            print(f"Erro durante a análise: {exc}")

    # -------------------------------------------------------------------------
    # Batch Run
    # -------------------------------------------------------------------------
    def executar_batch(self, opcao):
        """Executa um dos estudos do Batch Run já carregado."""
        if self.batch is None:
            self.carregar_batch()
            if self.batch is None:
                return
        try:
            batch = self.batch
            fdr = _buscar_linha_por_rotulo(batch, "Final Drive Ratio [-]")
            laptimes = _buscar_linha_por_rotulo(batch, "Lap time [s]", aliases=("Laptime [s]",))

            if opcao == 11:
                plotBatchLaptimeFDR(batch)
                self._salvar_resultado("batch_fdr_laptime", [fdr, laptimes])
            elif opcao == 12:
                shift = self._float("Tempo de troca por marcha [s] (padrão 0.1): ", default=0.1, minimo=0)
                dados_shift = plotBatchLaptimesFDRShift(batch, shift)
                self._salvar_resultado(
                    "batch_fdr_laptime_shift",
                    {
                        "Laptime": [fdr, laptimes],
                        "Laptime + shift": dados_shift,
                    },
                )
        except Exception as exc:
            print(f"Erro no Batch Run: {exc}")

    # -------------------------------------------------------------------------
    # Menus
    # -------------------------------------------------------------------------
    def executar_estudo_avancado_terminal(self, opcao):
        """Executa os estudos longitudinais/validação também pela interface terminal."""
        try:
            if opcao == 21:
                c = self.carro
                fdr = self._float(f"FDR [{c.final_drive:.4f}]: ", default=c.final_drive)
                alvo = self._float("Velocidade alvo [km/h] (100): ", default=100.0, minimo=0.1)
                dt = self._float("Passo de integração [s] (0.01): ", default=0.01, minimo=0.0001)
                shift = self._float("Tempo por troca [s] (0.10): ", default=0.10, minimo=0)
                atrito = self._sim_nao("Considerar limite de atrito?", default=True)
                dados = c.simular_aceleracao_fdr(fdr, alvo, dt, shift, atrito)
                self._salvar_resultado(f"simulacao_longitudinal_fdr_{fdr:.4f}", dados)
                print(f"Tempo 0→{alvo:g} km/h: {dados['tempo_alvo_s']}")
                print(f"Top speed: {dados['top_speed_km_h']:.2f} km/h")
                print(f"Aceleração máxima: {dados['max_accel_m_s2']:.3f} m/s²")
            elif opcao == 22:
                ini = self._float("FDR inicial [6.5]: ", default=6.5, minimo=0.01)
                fim = self._float("FDR final [8.5]: ", default=8.5, minimo=0.01)
                passo = self._float("Passo [0.1]: ", default=0.1, minimo=0.001)
                fdrs = list(np.arange(min(ini, fim), max(ini, fim) + passo * 0.5, passo))
                dados = self.carro.avaliar_fdrs(fdrs)
                self._salvar_resultado("comparacao_analitica_fdr", dados)
                melhor = min(
                    ((f, r["tempo_alvo_s"]) for f, r in dados.items() if r["tempo_alvo_s"] is not None),
                    key=lambda x: x[1],
                    default=None,
                )
                if melhor:
                    print(f"Menor tempo de aceleração: FDR {melhor[0]:.4f} | {melhor[1]:.3f} s")
            elif opcao in (23, 24):
                if self.batch is None:
                    self.carregar_batch()
                if self.carro is None or self.batch is None:
                    print("Para validar o modelo, carregue carro.csv + RPM x Torque + Batch Run.")
                    return
                fdrs = _buscar_linha_por_rotulo(self.batch, "Final Drive Ratio [-]")
                metric = "Highest Speed [km/h]" if opcao == 23 else "Maximum Longitudinal Acceleration [m/s^2]"
                alias = ("Top Speed [km/h]",) if opcao == 23 else ()
                batch_vals = _buscar_linha_por_rotulo(self.batch, metric, aliases=alias)
                model = self.carro.avaliar_fdrs(fdrs)
                model_vals = [model[f]["top_speed_km_h"] if opcao == 23 else model[f]["max_accel_m_s2"] for f in fdrs]
                dados = {"FDR": fdrs, "Batch": batch_vals, "Modelo": model_vals}
                nome = "validacao_batch_top_speed" if opcao == 23 else "validacao_batch_aceleracao"
                self._salvar_resultado(nome, dados)
                erros = [m-b for m,b in zip(model_vals, batch_vals)]
                mae = sum(abs(e) for e in erros) / len(erros) if erros else float("nan")
                print(f"Erro médio absoluto do modelo: {mae:.4f}")
        except Exception as exc:
            print(f"Erro no estudo avançado: {exc}")

    @staticmethod
    def limpar_tela():
        # Evita dependência de comandos externos: apenas separa visualmente o menu.
        print("\n" + "=" * 78)

    def menu(self):
        print("\n" + "=" * 78)
        print("                 PLOTTER POWERTRAIN - FÓRMULA SAE")
        print("=" * 78)
        if self.carro is None:
            print("Veículo: NÃO CARREGADO")
        else:
            print(
                f"Veículo: carregado | FDR = {self.carro.final_drive:.4f} | "
                f"Pmax = {self.carro.max_power:.2f} HP"
            )
        print(f"Saída CSV: {self.pasta_saida.resolve()}")
        print("-" * 78)
        print(" 1  Carregar/recarregar carro.csv")
        print(" 2  Carregar/recarregar curva RPM x Torque")
        print(" 3  Carregar/recarregar Batch Run")
        print(" 4  Mostrar resumo do veículo")
        print(" 5  Gráfico RPM x Torque x Potência")
        print(" 6  Gráfico Velocidade x Potência na roda")
        print(" 7  Gráfico Velocidade x Torque na roda")
        print(" 8  Gráfico Velocidade x Força trativa por marcha")
        print(" 9  Curva unificada de força trativa (V1)")
        print("10  Curva unificada de força trativa (V2 + atrito)")
        print("11  Perda de área de potência para um FDR")
        print("12  Perda de área para uma faixa de FDRs")
        print("13  Curva unificada de potência na roda")
        print("14  Comparar potência na roda para vários FDRs")
        print("15  Batch Run: FDR x Laptime")
        print("16  Batch Run: Laptime + tempo de troca")
        print("17  Preparar/exportar dados-base")
        print("18  Exportar um resultado CSV")
        print("19  Exportar todos os resultados CSV")
        print("20  Listar resultados em memória")
        print("21  Simulação longitudinal: aceleração")
        print("22  Comparação analítica de FDRs")
        print("23  Validação Batch: Top Speed")
        print("24  Validação Batch: Aceleração máxima")
        print(" 0  Sair")
        print("=" * 78)

    def listar_resultados(self):
        if not self.resultados:
            print("Nenhum resultado armazenado.")
            return
        print("\n--- Resultados em memória ---")
        for i, (nome, dados) in enumerate(self.resultados.items(), 1):
            tipo = type(dados).__name__
            if isinstance(dados, dict):
                detalhe = f"{len(dados)} FDR(s)"
            elif isinstance(dados, (list, tuple)):
                detalhe = f"{len(dados)} elemento(s)"
            else:
                detalhe = str(dados)
            print(f"{i:2d}) {nome:40s} | {tipo:10s} | {detalhe}")

    def executar(self):
        setMatplotParameters()
        print("\nPlotterPowertrain iniciado.")
        print("Os gráficos são exibidos pelo Matplotlib; feche a janela do gráfico para voltar ao menu.")

        # Para facilitar o uso, oferecemos os carregamentos iniciais separadamente.
        if self._sim_nao("Deseja carregar um carro.csv agora?", default=True):
            pass
        else:
            self.carregar_carro()
        if self.config_carro is not None and self.arquivo_rpm_torque is None:
            if self._sim_nao("Deseja carregar agora a curva RPM x Torque?", default=True):
                self.carregar_rpm_torque()

        while True:
            self.menu()
            opcao = input("Opção: ").strip()

            if not opcao.isdigit():
                print("Digite o número correspondente à opção.")
                continue

            opcao = int(opcao)

            if opcao == 0:
                print("Encerrando PlotterPowertrain.")
                break
            elif opcao == 1:
                self.carregar_carro()
            elif opcao == 2:
                self.carregar_rpm_torque()
            elif opcao == 3:
                self.carregar_batch()
            elif opcao == 4:
                self.mostrar_resumo_carro()
            elif 5 <= opcao <= 14:
                # O menu mostra 5..14; internamente os estudos usam 1..10.
                self.executar_grafico(opcao - 4)
            elif opcao in (15, 16):
                self.executar_batch(opcao - 4)
            elif opcao == 17:
                self.exportar_dados_base()
                self.exportar_resultado()
            elif opcao == 18:
                self.exportar_resultado()
            elif opcao == 19:
                self.exportar_todos()
            elif opcao == 20:
                self.listar_resultados()
            elif opcao in (21, 22, 23, 24):
                self.executar_estudo_avancado_terminal(opcao)
            else:
                print("Opção inválida.")


# =============================================================================
# INTERFACE GRÁFICA
# =============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class PlotterPowertrainGUI:
    """Interface gráfica para estudos de relação secundária/FDR.

    A GUI reutiliza os cálculos da classe Carro e mantém todos os resultados
    gerados em memória, permitindo visualizar, consultar e exportar os dados.
    """

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)

        setMatplotParameters()

        self.app = InterfacePlotterPowertrain()
        self.carro = None
        self.config_carro = None
        self.arquivo_carro = None
        self.arquivo_rpm_torque = None
        self.batch = None
        self.arquivo_batch = None
        self.fig = None
        self.canvas = None
        self.toolbar = None
        self.current_result_name = None
        self.current_result = None

        self._criar_estilo()
        self._criar_interface()
        self._atualizar_status()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _criar_estilo(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _criar_interface(self):
        # Cabeçalho
        # A logo fica no lado esquerdo e o nome completo da aplicação no centro.
        # A referência é mantida em ``self.logo_tk`` para o Tkinter não remover
        # a imagem por coleta de lixo.
        header = ttk.Frame(self.root, padding=(12, 10, 12, 5))
        header.pack(fill="x")

        logo_frame = ttk.Frame(header)
        logo_frame.pack(side="left", padx=(0, 12))
        self.logo_tk = None
        if LOGO_PATH.exists():
            try:
                self.logo_tk = tk.PhotoImage(file=str(LOGO_PATH))
                # O PNG original é grande; reduzir mantendo proporção.
                fator = max(1, self.logo_tk.width() // 180)
                if fator > 1:
                    self.logo_tk = self.logo_tk.subsample(fator, fator)
                ttk.Label(logo_frame, image=self.logo_tk).pack()
            except Exception as exc:
                ttk.Label(logo_frame, text="EESC-USP Formula SAE", style="Section.TLabel").pack()
                print(f"Aviso: não foi possível carregar a logo na GUI: {exc}")
        else:
            ttk.Label(logo_frame, text="EESC-USP Formula SAE", style="Section.TLabel").pack()

        titulo_frame = ttk.Frame(header)
        titulo_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(titulo_frame, text=APP_TITLE, style="Title.TLabel").pack(side="left", anchor="w")
        ttk.Label(
            titulo_frame,
            text="Análise de powertrain, FDR e dados de simulação",
            style="Status.TLabel",
        ).pack(side="left", padx=15, pady=(5, 0))

        # Os três carregamentos são independentes: é possível trocar apenas a
        # curva do motor ou apenas o Batch Run e manter o restante do veículo.
        ttk.Button(header, text="Carregar Batch Run", command=self.carregar_batch).pack(side="right", padx=3)
        ttk.Button(header, text="Carregar RPM × Torque", command=self.carregar_rpm_torque).pack(side="right", padx=3)
        ttk.Button(header, text="Carregar carro.csv", command=self.carregar_carro, style="Accent.TButton").pack(side="right", padx=3)

        # Área principal
        paned = ttk.Panedwindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        esquerda = ttk.Frame(paned, padding=8)
        direita = ttk.Frame(paned, padding=8)
        paned.add(esquerda, weight=0)
        paned.add(direita, weight=1)

        # Painel esquerdo: veículo + estudos + parâmetros
        dados_frame = ttk.LabelFrame(esquerda, text="Dados atualmente carregados", padding=8)
        dados_frame.pack(fill="x", pady=(0, 8))

        self.info_text = tk.Text(dados_frame, height=13, width=38, state="disabled", wrap="word")
        self.info_text.pack(fill="x")

        estudo_frame = ttk.LabelFrame(esquerda, text="Estudo / gráfico", padding=8)
        estudo_frame.pack(fill="x", pady=8)

        self.estudo_var = tk.StringVar(value="RPM × Torque × Potência")
        estudos = [
            "RPM × Torque × Potência",
            "Potência na roda por marcha",
            "Torque na roda por marcha",
            "Força trativa por marcha",
            "Força trativa unificada",
            "Força unificada + limite de atrito",
            "Perda de área para um FDR",
            "Perda de área × FDR",
            "Potência na roda unificada",
            "Comparação de potência × FDR",
            "Simulação longitudinal: aceleração",
            "Comparação analítica: FDR",
            "Validação Batch: Top Speed × FDR",
            "Validação Batch: Aceleração Máxima × FDR",
            "Batch Run: FDR × Laptime",
            "Batch Run: FDR × Laptime + trocas",
        ]
        self.estudo_combo = ttk.Combobox(estudo_frame, textvariable=self.estudo_var, values=estudos, state="readonly", width=36)
        self.estudo_combo.pack(fill="x", pady=(0, 8))
        self.estudo_combo.bind("<<ComboboxSelected>>", lambda e: self._atualizar_parametros())

        params = ttk.Frame(estudo_frame)
        params.pack(fill="x")

        self.fdr_var = tk.StringVar()
        self.res_var = tk.StringVar(value="0.125")
        self.fdr_ini_var = tk.StringVar(value="6.5")
        self.fdr_fim_var = tk.StringVar(value="8.5")
        self.fdr_passo_var = tk.StringVar(value="0.1")
        self.fdr_lista_var = tk.StringVar(value="6.5, 7.0, 7.5, 8.0")
        self.shift_time_var = tk.StringVar(value="0.10")
        self.vel_alvo_var = tk.StringVar(value="100")
        self.dt_var = tk.StringVar(value="0.01")
        self.atrito_var = tk.BooleanVar(value=False)
        self.mostrar_marchas_var = tk.BooleanVar(value=True)
        self.mostrar_limite_var = tk.BooleanVar(value=True)

        self.param_widgets = []
        self._criar_parametros(params)

        ttk.Button(estudo_frame, text="Gerar gráfico / dados", command=self.executar_estudo, style="Accent.TButton").pack(fill="x", pady=(10, 4))
        ttk.Button(estudo_frame, text="Limpar resultado atual", command=self.limpar_grafico).pack(fill="x")

        # Exportação
        exp_frame = ttk.LabelFrame(esquerda, text="Exportação", padding=8)
        exp_frame.pack(fill="x", pady=8)
        ttk.Button(exp_frame, text="Exportar resultado atual (.csv)", command=self.exportar_atual).pack(fill="x", pady=2)
        ttk.Button(exp_frame, text="Exportar resultado selecionado...", command=self.exportar_selecionado).pack(fill="x", pady=2)
        ttk.Button(exp_frame, text="Exportar todos os resultados", command=self.exportar_todos).pack(fill="x", pady=2)
        ttk.Button(exp_frame, text="Salvar gráfico como imagem", command=self.salvar_grafico).pack(fill="x", pady=2)

        # Painel direito com abas
        notebook = ttk.Notebook(direita)
        notebook.pack(fill="both", expand=True)

        grafico_tab = ttk.Frame(notebook)
        tabela_tab = ttk.Frame(notebook)
        resultados_tab = ttk.Frame(notebook)
        notebook.add(grafico_tab, text="Gráfico")
        notebook.add(tabela_tab, text="Dados gerados")
        notebook.add(resultados_tab, text="Resultados em memória")
        self.notebook = notebook

        self.grafico_container = ttk.Frame(grafico_tab)
        self.grafico_container.pack(fill="both", expand=True)

        # Tabela de dados gerados
        tabela_top = ttk.Frame(tabela_tab, padding=5)
        tabela_top.pack(fill="x")
        self.tabela_titulo = ttk.Label(tabela_top, text="Nenhum resultado gerado", style="Section.TLabel")
        self.tabela_titulo.pack(side="left")
        ttk.Button(tabela_top, text="Atualizar tabela", command=self._atualizar_tabela).pack(side="right")

        tabela_frame = ttk.Frame(tabela_tab)
        tabela_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_dados = ttk.Treeview(tabela_frame, show="headings")
        scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree_dados.yview)
        scroll_x = ttk.Scrollbar(tabela_frame, orient="horizontal", command=self.tree_dados.xview)
        self.tree_dados.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree_dados.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        tabela_frame.rowconfigure(0, weight=1)
        tabela_frame.columnconfigure(0, weight=1)

        # Resultados armazenados
        res_frame = ttk.Frame(resultados_tab, padding=5)
        res_frame.pack(fill="both", expand=True)
        self.tree_resultados = ttk.Treeview(res_frame, columns=("nome", "tipo", "detalhe"), show="headings", selectmode="browse")
        self.tree_resultados.heading("nome", text="Resultado")
        self.tree_resultados.heading("tipo", text="Tipo")
        self.tree_resultados.heading("detalhe", text="Tamanho / detalhe")
        self.tree_resultados.column("nome", width=330)
        self.tree_resultados.column("tipo", width=100)
        self.tree_resultados.column("detalhe", width=180)
        sr = ttk.Scrollbar(res_frame, orient="vertical", command=self.tree_resultados.yview)
        self.tree_resultados.configure(yscrollcommand=sr.set)
        self.tree_resultados.grid(row=0, column=0, sticky="nsew")
        sr.grid(row=0, column=1, sticky="ns")
        res_frame.rowconfigure(0, weight=1)
        res_frame.columnconfigure(0, weight=1)
        self.tree_resultados.bind("<<TreeviewSelect>>", self._selecionar_resultado)

        # Rodapé
        self.status_var = tk.StringVar(value="Nenhum veículo carregado.")
        ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel", relief="sunken", anchor="w").pack(fill="x", side="bottom")

        self._atualizar_parametros()

    def _criar_parametros(self, parent):
        """Cria os campos de parâmetros que a GUI mostra/oculta por estudo."""
        self.param_entries = {}

        def row(nome, label_text, variable, r):
            label = ttk.Label(parent, text=label_text)
            label.grid(row=r, column=0, sticky="w", pady=2)
            entry = ttk.Entry(parent, textvariable=variable, width=18)
            entry.grid(row=r, column=1, sticky="ew", padx=(8, 0), pady=2)
            self.param_entries[nome] = (label, entry)

        row("fdr", "FDR:", self.fdr_var, 0)
        row("res", "Resolução [km/h]:", self.res_var, 1)
        row("ini", "FDR inicial:", self.fdr_ini_var, 2)
        row("fim", "FDR final:", self.fdr_fim_var, 3)
        row("passo", "Passo FDR:", self.fdr_passo_var, 4)
        row("lista", "FDRs:", self.fdr_lista_var, 5)
        row("shift", "Tempo por troca [s]:", self.shift_time_var, 6)
        row("vel_alvo", "Velocidade alvo [km/h]:", self.vel_alvo_var, 7)
        row("dt", "Passo de integração [s]:", self.dt_var, 8)

        parent.columnconfigure(1, weight=1)
        self.chk_atrito = ttk.Checkbutton(parent, text="Considerar limite de atrito", variable=self.atrito_var)
        self.chk_marchas = ttk.Checkbutton(parent, text="Mostrar marchas", variable=self.mostrar_marchas_var)
        self.chk_limite = ttk.Checkbutton(parent, text="Mostrar limite de atrito", variable=self.mostrar_limite_var)
        self.chk_atrito.grid(row=7, column=0, columnspan=2, sticky="w", pady=2)
        self.chk_marchas.grid(row=8, column=0, columnspan=2, sticky="w", pady=2)
        self.chk_limite.grid(row=9, column=0, columnspan=2, sticky="w", pady=2)

    def _atualizar_parametros(self):
        estudo = self.estudo_var.get()

        mostrar = {
            "fdr": estudo in {
                "Potência na roda por marcha", "Força trativa unificada",
                "Força unificada + limite de atrito", "Perda de área para um FDR",
                "Potência na roda unificada", "Simulação longitudinal: aceleração",
            },
            "res": estudo not in {"RPM × Torque × Potência", "Batch Run: FDR × Laptime", "Batch Run: FDR × Laptime + trocas"},
            "ini": estudo in {"Perda de área × FDR", "Comparação analítica: FDR"},
            "fim": estudo in {"Perda de área × FDR", "Comparação analítica: FDR"},
            "passo": estudo in {"Perda de área × FDR", "Comparação analítica: FDR"},
            "lista": estudo == "Comparação de potência × FDR",
            "shift": estudo in {"Batch Run: FDR × Laptime + trocas", "Simulação longitudinal: aceleração", "Comparação analítica: FDR"},
            "vel_alvo": estudo in {"Simulação longitudinal: aceleração", "Comparação analítica: FDR", "Validação Batch: Aceleração Máxima × FDR"},
            "dt": estudo in {"Simulação longitudinal: aceleração", "Comparação analítica: FDR", "Validação Batch: Aceleração Máxima × FDR"},
        }

        # Primeiro escondemos todos os campos. Depois exibimos somente os
        # necessários ao estudo selecionado, evitando sobreposição dos labels.
        for label, entry in self.param_entries.values():
            label.grid_remove()
            entry.grid_remove()
        self.chk_atrito.grid_remove()
        self.chk_marchas.grid_remove()
        self.chk_limite.grid_remove()

        row = 0
        for nome in ("fdr", "res", "ini", "fim", "passo", "lista", "shift", "vel_alvo", "dt"):
            if mostrar.get(nome, False):
                label, entry = self.param_entries[nome]
                label.grid(row=row, column=0, sticky="w", pady=2)
                entry.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
                row += 1

        if estudo == "Força unificada + limite de atrito":
            self.chk_atrito.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
            row += 1
            self.chk_marchas.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
            row += 1
            self.chk_limite.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)

    # ------------------------------------------------------------------
    # Carregamento / dados
    # ------------------------------------------------------------------
    def _parametros_fisicos_efetivos(self):
        """Combina carro.csv + Batch Run sem sobrescrever valores explicitamente cadastrados."""
        cfg = self.config_carro or {}
        batch_params = getBatchVehicleParameters(self.batch) if self.batch is not None else {}
        defaults = {
            "drivetrain_efficiency": 0.96,
            "drag_coefficient": 1.34,
            "downforce_coefficient": 3.54,
            "frontal_area": 1.14,
            "air_density": 1.16,
            "tire_rolling_drag": 0.01,
            "rev_limit": None,
            "longitudinal_friction": cfg.get("tire_coefficient", 2.204),
            "lateral_friction": cfg.get("tire_coefficient", 2.204),
            "rear_weight_distribution": 0.55,
            "rear_downforce_distribution": 0.60,
            "cg_height": None,
            "wheelbase": None,
        }
        for chave in defaults:
            if cfg.get(chave) is not None:
                defaults[chave] = cfg[chave]
            elif chave in batch_params:
                defaults[chave] = batch_params[chave]
        return defaults

    def _reconstruir_carro(self):
        """Monta o objeto Carro usando exatamente o mesmo pipeline do terminal."""
        if self.config_carro is None or self.arquivo_rpm_torque is None:
            self.carro = None
            self.app.carro = None
            self._mostrar_dados_carregados()
            return False

        cfg = self.config_carro
        relacoes = cfg["gear_ratios"] if "gear_ratios" in cfg else getGearRatios(str(cfg["gear_ratio_file"]))
        fis = self._parametros_fisicos_efetivos()
        self.carro = Carro(
            getRPMxTorquePoints(str(self.arquivo_rpm_torque)),
            relacoes,
            float(cfg["primary_ratio"]),
            float(cfg["secondary_ratio"]),
            float(cfg["wheel_radius"]),
            float(cfg.get("weight", 240.0)),
            float(cfg.get("tire_coefficient", 2.204)),
            **fis,
        )
        self.app.carro = self.carro
        self.app.config_carro = self.config_carro
        self.app.arquivo_carro = Path(self.arquivo_carro) if self.arquivo_carro else None
        self.app.arquivo_rpm_torque = Path(self.arquivo_rpm_torque)
        self.app.resultados.clear()
        self.current_result_name = None
        self.current_result = None
        self._mostrar_dados_carregados()
        self._atualizar_resultados()
        self.limpar_grafico()
        self._atualizar_status()
        return True

    def carregar_carro(self):
        """Abre o carro.csv e carrega somente as configurações do veículo."""
        caminho = filedialog.askopenfilename(
            title="Selecionar carro.csv",
            filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            self.config_carro = getCarroConfig(caminho)
            self.arquivo_carro = Path(caminho)
            # Se uma curva RPM x Torque já estiver carregada, o carro fica
            # pronto imediatamente; caso contrário, a GUI aguarda o outro arquivo.
            montou = self._reconstruir_carro()
            if montou:
                self.status_var.set(f"Veículo completo: {Path(caminho).name} + {Path(self.arquivo_rpm_torque).name}")
            else:
                self.status_var.set(f"Configuração carregada: {Path(caminho).name} | falta a curva RPM × Torque")
        except Exception as exc:
            messagebox.showerror("Erro ao carregar carro.csv", str(exc), parent=self.root)

    def carregar_rpm_torque(self):
        """Abre o CSV externo da curva RPM x Torque."""
        caminho = filedialog.askopenfilename(
            title="Selecionar curva RPM × Torque",
            filetypes=[("CSV/TXT", "*.csv *.txt"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            # Valida antes de trocar a curva atualmente carregada.
            mapa = getRPMxTorquePoints(caminho)
            self.arquivo_rpm_torque = Path(caminho)
            if self.config_carro is not None:
                self._reconstruir_carro()
                self.status_var.set(f"Curva RPM × Torque carregada: {Path(caminho).name} | veículo atualizado")
            else:
                self._mostrar_dados_carregados()
                self.status_var.set(f"Curva RPM × Torque carregada: {Path(caminho).name} | selecione o carro.csv")
        except Exception as exc:
            messagebox.showerror("Erro na curva RPM × Torque", str(exc), parent=self.root)

    def carregar_batch(self):
        """Abre um CSV de Batch Run e o mantém disponível para os estudos."""
        caminho = filedialog.askopenfilename(
            title="Selecionar resultado Batch Run do OptimumLap",
            filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            batch = getBatchRun(caminho, show_data_index=0)
            # O parser já garantiu que existem séries numéricas; guardamos o
            # resultado completo para também mostrar metadados na interface.
            self.batch = batch
            self.app.batch = batch
            self.arquivo_batch = Path(caminho)
            self.app.arquivo_batch = self.arquivo_batch
            # Se o veículo já estiver completo, reconstruímos o objeto para que
            # parâmetros físicos ausentes no carro.csv sejam herdados do Batch.
            if self.config_carro is not None and self.arquivo_rpm_torque is not None:
                self._reconstruir_carro()
            else:
                self._mostrar_dados_carregados()
            fdrs = _buscar_linha_por_rotulo(batch, "Final Drive Ratio [-]")
            self.status_var.set(f"Batch Run carregado: {Path(caminho).name} | {len(fdrs)} runs")
        except Exception as exc:
            messagebox.showerror("Erro no Batch Run", str(exc), parent=self.root)

    def _mostrar_dados_carregados(self):
        """Atualiza o painel textual com tudo que está atualmente carregado."""
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        linhas = []

        linhas.append("=== ENTRADAS ===")
        linhas.append(f"Carro.csv: {self.arquivo_carro or 'não carregado'}")
        linhas.append(f"RPM × Torque: {self.arquivo_rpm_torque or 'não carregado'}")
        linhas.append(f"Batch Run: {self.arquivo_batch or 'não carregado'}")
        linhas.append("")

        if self.carro is not None:
            c = self.carro
            linhas += [
                "=== VEÍCULO PROCESSADO ===",
                f"Nome: {self.config_carro.get('name', 'não informado')}",
                f"RPM: {c.rpm[0]:.0f} → {c.rpm[-1]:.0f}",
                f"Pontos RPM × Torque: {len(c.rpm)}",
                f"Torque máximo: {max(c.torque):.2f} Nm",
                f"Potência máxima: {c.max_power:.2f} HP",
                f"RPM de potência máxima: {c.rpm[c.power.index(max(c.power))]:.0f}",
                "",
                f"Relações de marcha ({len(c.relacoes_marcha)}):",
            ]
            linhas += [f"  {i+1}ª: {r:.5f}" for i, r in enumerate(c.relacoes_marcha)]
            linhas += [
                "",
                f"Relação primária: {c.relacao_primaria:.5f}",
                f"Relação secundária: {c.relacao_secundaria:.5f}",
                f"FDR atual: {c.final_drive:.5f}",
                f"Raio da roda: {c.raio_roda:.5f} m",
                f"Peso usado no modelo: {c.peso:.2f} kg",
                f"Coeficiente de pneu: {c.Cat_pneu:.4f}",
                f"Eficiência drivetrain: {c.drivetrain_efficiency*100:.2f}%",
                f"Cd / Cl: {c.drag_coefficient:.3f} / {c.downforce_coefficient:.3f}",
                f"Área frontal: {c.frontal_area:.3f} m²",
                f"Crr: {c.tire_rolling_drag:.4f}",
                f"Rev Limit declarado / efetivo: {c.rev_limit_declared:.0f} / {c.rev_limit_effective:.0f} rpm",
                f"Top Speed por equilíbrio (FDR atual): {c.calcular_top_speed():.2f} km/h",
            ]
            if c.mapa_cobre_limite_rev:
                linhas.append("ATENÇÃO: o Rev Limit informado excede o RPM máximo disponível no mapa do motor.")
        elif self.config_carro is not None:
            linhas.append("=== CONFIGURAÇÃO DO VEÍCULO ===")
            if "gear_ratios" in self.config_carro:
                linhas.append(f"Relações de marcha: {self.config_carro['gear_ratios']}")
            else:
                linhas.append(f"Arquivo de relações: {self.config_carro.get('gear_ratio_file', 'não identificado')}")
            linhas.append(f"Nome: {self.config_carro.get('name', 'não informado')}")
            linhas.append(f"Primária: {self.config_carro.get('primary_ratio')}")
            linhas.append(f"Secundária: {self.config_carro.get('secondary_ratio')}")
            linhas.append(f"Raio da roda: {self.config_carro.get('wheel_radius')} m")
            linhas.append(f"Peso: {self.config_carro.get('weight')} kg")
            linhas.append(f"Coeficiente de pneu: {self.config_carro.get('tire_coefficient')}")
            linhas.append("Aguardando o CSV RPM × Torque para concluir o veículo.")

        if self.batch is not None:
            linhas += ["", "=== BATCH RUN ==="]
            perfil = self.batch.get("profile", {})
            if perfil.get("Vehicle"): linhas.append(f"Veículo OptimumLap: {perfil['Vehicle']}")
            if perfil.get("Track"): linhas.append(f"Pista: {perfil['Track']}")
            fdrs = _buscar_linha_por_rotulo(self.batch, "Final Drive Ratio [-]")
            linhas.append(f"Runs: {len(fdrs)}")
            linhas.append(f"FDR: {min(fdrs):.3f} → {max(fdrs):.3f}")
            linhas.append(f"Métricas carregadas: {len(self.batch.get('data', {}))}")

        self.info_text.insert("end", "\n".join(linhas))
        self.info_text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Cálculos para gráficos embutidos
    # ------------------------------------------------------------------
    def _curvas_marcha(self, tipo, fdr=None, res=0.125):
        c = self.carro
        fdr = c.final_drive if fdr is None else fdr
        if tipo == "potencia":
            return c.curvas_potencia(fdr)
        if tipo == "torque":
            return c.curvas_torque(fdr)
        return c.curvas_marcha(fdr)

    def _plot_engine(self):
        c = self.carro
        ax = self.fig.add_subplot(111)
        ax.plot(c.rpm_operacional, c.torque_operacional, label="Torque [Nm]")
        ax.scatter([c.rpm_operacional[c.torque_operacional.index(max(c.torque_operacional))]], [max(c.torque_operacional)])
        ax.set_xlabel("RPM")
        ax.set_ylabel("Torque [Nm]")
        ax2 = ax.twinx()
        ax2.plot(c.rpm_operacional, c.power_operacional, label="Potência [HP]")
        ax2.scatter([c.rpm_operacional[c.power_operacional.index(max(c.power_operacional))]], [max(c.power_operacional)])
        ax2.set_ylabel("Potência [HP]")
        ax.set_title("Curva de Torque e Potência do Motor")
        l1, t1 = ax.get_legend_handles_labels()
        l2, t2 = ax2.get_legend_handles_labels()
        ax.legend(l1 + l2, t1 + t2, loc="best")
        ax.grid(True, alpha=0.3)
        return [c.rpm_operacional, c.torque_operacional, c.power_operacional]

    def _plot_gear_curves(self, tipo, titulo, ylabel, fdr):
        ax = self.fig.add_subplot(111)
        curvas = self._curvas_marcha(tipo, fdr)
        for v, y, i in curvas:
            ax.plot(v, y, label=f"Marcha {i}")
        ax.set_xlabel("Velocidade [km/h]")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{titulo} — FDR = {fdr:.4f}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        return [[v, y, i] for v, y, i in curvas]

    def _plot_unified_force(self, fdr, res, atrito=False, mostrar_marchas=True, mostrar_limite=True):
        c = self.carro
        curva = c.gerar_curva_unica_froda_vroda_v2(
            fdr=fdr, res=res, considerar_atrito=atrito, plotar=False,
            mostrar_marchas=mostrar_marchas, mostrar_limite_atrito=mostrar_limite
        )
        ax = self.fig.add_subplot(111)
        if mostrar_marchas:
            for v, f, i in c.curvas_marcha(fdr):
                ax.plot(v, f, linestyle="--", alpha=0.35, label=f"Marcha {i}")
        if curva:
            ax.plot([p[0] for p in curva], [p[1] for p in curva], linewidth=2.5, label="Curva unificada")
        if mostrar_limite:
            vmax = max([p[0] for p in curva], default=120)
            vs = np.linspace(0, max(120, vmax), 250)
            ax.plot(vs, [c._limite_atrito(v) for v in vs], linestyle="--", label="Limite de aderência")
        ax.set_xlabel("Velocidade [km/h]")
        ax.set_ylabel("Força trativa [N]")
        ax.set_title(f"Força Trativa Unificada — FDR = {fdr:.4f}")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        return curva

    def _plot_perda_fdr(self, fdr, res):
        c = self.carro
        razao = c.calcular_perda_area_potencia(fdr=fdr, res=res, plotar=False)
        curva = c.gerar_curva_unica_froda_vroda_v2(fdr=fdr, res=res, considerar_atrito=False, plotar=False)
        ax = self.fig.add_subplot(111)
        if curva:
            v = np.array([p[0] for p in curva])
            f = np.array([p[1] for p in curva])
            ax.plot(v, f, label="Força disponível")
            p_watts = c.max_power * 745.7 * c.drivetrain_efficiency
            ideal = np.divide(p_watts, v / 3.6, out=np.zeros_like(v), where=v > 0)
            ax.plot(v, ideal, label="Força equivalente à potência máxima")
        ax.set_xlabel("Velocidade [km/h]")
        ax.set_ylabel("Força [N]")
        ax.set_title(f"Métrica de área (secundária) — FDR = {fdr:.4f} | Perda = {razao:.3%}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        return razao

    def _plot_analitico_fdr(self, fdrs, velocidade_alvo=100.0, dt=0.01, shift_time=0.10):
        resultados = self.carro.avaliar_fdrs(
            fdrs, velocidade_alvo=velocidade_alvo, dt=dt,
            shift_time=shift_time, considerar_atrito=self.atrito_var.get()
        )
        ax = self.fig.add_subplot(111)
        fdr_vec = list(resultados.keys())
        tempos = [resultados[f]["tempo_alvo_s"] if resultados[f]["tempo_alvo_s"] is not None else np.nan for f in fdr_vec]
        tops = [resultados[f]["top_speed_km_h"] for f in fdr_vec]
        ax2 = ax.twinx()
        ax.plot(fdr_vec, tempos, marker="o", label=f"Tempo 0→{velocidade_alvo:g} km/h")
        ax2.plot(fdr_vec, tops, marker="s", label="Top speed")
        ax.set_xlabel("FDR")
        ax.set_ylabel("Tempo de aceleração [s]")
        ax2.set_ylabel("Top speed [km/h]")
        ax.set_title("Desempenho longitudinal analítico × FDR")
        ax.grid(True, alpha=0.3)
        l1, t1 = ax.get_legend_handles_labels(); l2, t2 = ax2.get_legend_handles_labels()
        ax.legend(l1 + l2, t1 + t2, loc="best")
        return resultados

    def _plot_batch_validation(self, metric):
        if self.batch is None:
            raise ValueError("Carregue um Batch Run antes da validação.")
        fdrs = _buscar_linha_por_rotulo(self.batch, "Final Drive Ratio [-]")
        alvo = float(self.vel_alvo_var.get().replace(',', '.')) if hasattr(self, "vel_alvo_var") and self.vel_alvo_var.get().strip() else 100.0
        dt = float(self.dt_var.get().replace(',', '.')) if hasattr(self, "dt_var") and self.dt_var.get().strip() else 0.01
        shift_time = float(self.shift_time_var.get().replace(',', '.')) if self.shift_time_var.get().strip() else 0.10
        resultados = self.carro.avaliar_fdrs(fdrs, velocidade_alvo=alvo, dt=dt, shift_time=shift_time, considerar_atrito=self.atrito_var.get())
        ax = self.fig.add_subplot(111)
        if metric == "top_speed":
            batch_values = _buscar_linha_por_rotulo(self.batch, "Highest Speed [km/h]", aliases=("Top Speed [km/h]",))
            model_values = [resultados[f]["top_speed_km_h"] for f in fdrs]
            ylabel = "Top Speed [km/h]"
            title = "Validação: Top Speed — Modelo vs OptimumLap Batch Run"
        else:
            batch_values = _buscar_linha_por_rotulo(self.batch, "Maximum Longitudinal Acceleration [m/s^2]")
            model_values = [resultados[f]["max_accel_m_s2"] for f in fdrs]
            ylabel = "Aceleração longitudinal máxima [m/s²]"
            title = "Validação: Aceleração máxima — Modelo vs OptimumLap Batch Run"
        ax.plot(fdrs, batch_values, marker="o", label="OptimumLap Batch Run")
        ax.plot(fdrs, model_values, marker="s", label="Modelo analítico")
        ax.set_xlabel("FDR")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        return {"FDR": fdrs, "Batch": batch_values, "Modelo": model_values}

    def _plot_batch_laptime(self, incluir_shift=False, shift_time=0.1):
        """Desenha os estudos de Batch Run na figura embutida da GUI."""
        if self.batch is None:
            raise ValueError("Carregue um CSV de Batch Run antes deste estudo.")

        fdrs = _buscar_linha_por_rotulo(self.batch, "Final Drive Ratio [-]")
        laptimes = _buscar_linha_por_rotulo(self.batch, "Lap time [s]", aliases=("Laptime [s]",))

        ax = self.fig.add_subplot(111)
        ax.plot(fdrs, laptimes, marker="o", label="Laptime")

        if incluir_shift:
            shifts = _buscar_linha_por_rotulo(self.batch, "Gear Shifts [-]")
            laptimes_shift = [t + n * shift_time for t, n in zip(laptimes, shifts)]
            ax.plot(fdrs, laptimes_shift, marker="o", label=f"Laptime + {shift_time:g}s/troca")
            indice = laptimes_shift.index(min(laptimes_shift))
            ax.scatter(fdrs[indice], laptimes_shift[indice], s=65, zorder=5,
                       label=f"Melhor com trocas: {laptimes_shift[indice]:.3f}s | FDR {fdrs[indice]:.3f}")
            dados = {
                "Laptime": [fdrs, laptimes],
                "Laptime + shift": [fdrs, laptimes_shift],
            }
        else:
            indice = laptimes.index(min(laptimes))
            ax.scatter(fdrs[indice], laptimes[indice], s=65, zorder=5,
                       label=f"Melhor laptime: {laptimes[indice]:.3f}s | FDR {fdrs[indice]:.3f}")
            dados = [fdrs, laptimes]

        ax.set_xlabel("Final Drive Ratio (FDR)")
        ax.set_ylabel("Laptime [s]")
        ax.set_title("Batch Run — FDR × Laptime")
        ax.xaxis.set_major_locator(MultipleLocator(0.5))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        ax.grid(True, which="major", alpha=0.35)
        ax.grid(False, which="minor")
        ax.legend(loc="best")
        return dados

    # ------------------------------------------------------------------
    # Execução do estudo
    # ------------------------------------------------------------------
    def executar_estudo(self):
        estudo = self.estudo_var.get()
        estudos_batch_only = {"Batch Run: FDR × Laptime", "Batch Run: FDR × Laptime + trocas"}
        estudos_validacao = {"Validação Batch: Top Speed × FDR", "Validação Batch: Aceleração Máxima × FDR"}

        if estudo in estudos_batch_only or estudo in estudos_validacao:
            if self.batch is None:
                messagebox.showwarning("Batch Run não carregado", "Carregue um CSV de Batch Run antes deste estudo.", parent=self.root)
                return
        if estudo in estudos_validacao and self.carro is None:
            messagebox.showwarning("Veículo incompleto", "A validação precisa de carro.csv + RPM × Torque + Batch Run.", parent=self.root)
            return
        if estudo not in estudos_batch_only and self.carro is None:
            messagebox.showwarning(
                "Veículo incompleto",
                "Para este estudo é necessário carregar o carro.csv e o CSV externo de RPM × Torque.",
                parent=self.root,
            )
            return

        try:
            c = self.carro
            res = float(self.res_var.get().replace(',', '.')) if self.res_var.get().strip() else 0.125
            if res <= 0:
                raise ValueError("A resolução deve ser maior que zero.")
            fdr = float(self.fdr_var.get().replace(',', '.')) if self.fdr_var.get().strip() else (c.final_drive if c else 0.0)

            self._preparar_figura()
            dados = None
            nome = ""

            if estudo == "RPM × Torque × Potência":
                dados = self._plot_engine()
                nome = "rpm_torque_potencia"

            elif estudo == "Potência na roda por marcha":
                dados = self._plot_gear_curves("potencia", "Potência na Roda por Marcha", "Potência [HP]", fdr)
                nome = f"potencia_roda_marchas_fdr_{fdr:.4f}"

            elif estudo == "Torque na roda por marcha":
                dados = self._plot_gear_curves("torque", "Torque na Roda por Marcha", "Torque [Nm]", fdr)
                nome = f"torque_roda_marchas_fdr_{fdr:.4f}"

            elif estudo == "Força trativa por marcha":
                dados = self._plot_gear_curves("forca", "Força Trativa por Marcha", "Força [N]", fdr)
                nome = f"forca_trativa_marchas_fdr_{fdr:.4f}"

            elif estudo == "Força trativa unificada":
                dados = self._plot_unified_force(fdr, res, False, True, False)
                nome = f"forca_unificada_fdr_{fdr:.4f}"

            elif estudo == "Força unificada + limite de atrito":
                dados = self._plot_unified_force(fdr, res, self.atrito_var.get(), self.mostrar_marchas_var.get(), self.mostrar_limite_var.get())
                nome = f"forca_unificada_atrito_fdr_{fdr:.4f}"

            elif estudo == "Perda de área para um FDR":
                dados = self._plot_perda_fdr(fdr, res)
                nome = f"perda_area_fdr_{fdr:.4f}"

            elif estudo == "Perda de área × FDR":
                ini = float(self.fdr_ini_var.get().replace(',', '.'))
                fim = float(self.fdr_fim_var.get().replace(',', '.'))
                passo = float(self.fdr_passo_var.get().replace(',', '.'))
                if passo <= 0: raise ValueError("O passo de FDR deve ser maior que zero.")
                if fim < ini: ini, fim = fim, ini
                fdrs = [round(float(x), 8) for x in np.arange(ini, fim + passo * 0.5, passo)]
                # A rotina original dessa análise possui plotagem própria e não
                # expõe um parâmetro plotar=False. Na GUI, suprimimos apenas o
                # show() dessa rotina para evitar uma segunda janela do Matplotlib.
                import matplotlib.pyplot as _plt
                _show_original = _plt.show
                try:
                    _plt.show = lambda *args, **kwargs: None
                    dados = c.calcular_perda_area_potencia_range(fdrs, res=res)
                finally:
                    _plt.show = _show_original
                    _plt.close("all")
                ax = self.fig.add_subplot(111)
                ax.plot(dados[0], dados[1], marker="o")
                ax.set_xlabel("Final Drive Ratio (FDR)")
                ax.set_ylabel("Razão de perda de área")
                ax.set_title("Perda de área de potência × FDR")
                ax.grid(True, alpha=0.3)
                nome = "perda_area_range_fdr"

            elif estudo == "Potência na roda unificada":
                dados = c.gerar_pot_vroda_unificada(fdr=fdr, res=res, plotar=False)
                ax = self.fig.add_subplot(111)
                ax.plot(dados[0], dados[1], linewidth=2.5, label="Potência unificada")
                ax.set_xlabel("Velocidade [km/h]")
                ax.set_ylabel("Potência na roda [HP]")
                ax.set_title(f"Potência na Roda Unificada — FDR = {fdr:.4f}")
                ax.grid(True, alpha=0.3)
                ax.legend()
                nome = f"potencia_unificada_fdr_{fdr:.4f}"

            elif estudo == "Comparação de potência × FDR":
                fdrs = [float(x.strip().replace(',', '.')) for x in self.fdr_lista_var.get().replace(';', ',').split(',') if x.strip()]
                if not fdrs: raise ValueError("Informe pelo menos um FDR.")
                dados = c.comparar_pot_vroda_fdrs(fdrs, res=res, plotar=False)
                ax = self.fig.add_subplot(111)
                for f, par in dados.items():
                    ax.plot(par[0], par[1], label=f"FDR = {f:.2f}")
                ax.set_xlabel("Velocidade [km/h]")
                ax.set_ylabel("Potência na roda [HP]")
                ax.set_title("Comparação de Potência na Roda × FDR")
                ax.grid(True, alpha=0.3)
                ax.legend()
                nome = "comparacao_potencia_fdrs"

            elif estudo == "Simulação longitudinal: aceleração":
                alvo = float(self.vel_alvo_var.get().replace(',', '.')) if self.vel_alvo_var.get().strip() else 100.0
                dt = float(self.dt_var.get().replace(',', '.')) if self.dt_var.get().strip() else 0.01
                shift_time = float(self.shift_time_var.get().replace(',', '.')) if self.shift_time_var.get().strip() else 0.10
                if alvo <= 0 or dt <= 0 or shift_time < 0:
                    raise ValueError("Velocidade alvo e dt devem ser positivos; tempo de troca não pode ser negativo.")
                dados = c.simular_aceleracao_fdr(
                    fdr=fdr, velocidade_alvo=alvo, dt=dt, shift_time=shift_time,
                    considerar_atrito=self.atrito_var.get()
                )
                ax = self.fig.add_subplot(111)
                hist = dados["historico"]
                velocidades = [0.0]; tempos = [0.0]
                for h in hist:
                    if "velocidade_km_h" in h and "tempo_s" in h:
                        velocidades.append(h["velocidade_km_h"]); tempos.append(h["tempo_s"])
                ax.plot(tempos, velocidades, label="Velocidade")
                ax.set_xlabel("Tempo [s]")
                ax.set_ylabel("Velocidade [km/h]")
                ax.set_title(f"Simulação longitudinal — FDR = {fdr:.4f}")
                ax.grid(True, alpha=0.3)
                ax.legend()
                nome = f"simulacao_longitudinal_fdr_{fdr:.4f}"

            elif estudo == "Comparação analítica: FDR":
                ini = float(self.fdr_ini_var.get().replace(',', '.')) if self.fdr_ini_var.get().strip() else 6.5
                fim = float(self.fdr_fim_var.get().replace(',', '.')) if self.fdr_fim_var.get().strip() else 8.5
                passo = float(self.fdr_passo_var.get().replace(',', '.')) if self.fdr_passo_var.get().strip() else 0.1
                alvo = float(self.vel_alvo_var.get().replace(',', '.')) if self.vel_alvo_var.get().strip() else 100.0
                dt = float(self.dt_var.get().replace(',', '.')) if self.dt_var.get().strip() else 0.01
                shift_time = float(self.shift_time_var.get().replace(',', '.')) if self.shift_time_var.get().strip() else 0.10
                if passo <= 0 or dt <= 0 or alvo <= 0 or shift_time < 0:
                    raise ValueError("Parâmetros da comparação analítica inválidos.")
                fdrs = [round(float(x), 8) for x in np.arange(min(ini, fim), max(ini, fim) + passo * 0.5, passo)]
                dados = self._plot_analitico_fdr(fdrs, alvo, dt, shift_time)
                nome = "comparacao_analitica_fdr"

            elif estudo == "Validação Batch: Top Speed × FDR":
                dados = self._plot_batch_validation("top_speed")
                nome = "validacao_batch_top_speed"

            elif estudo == "Validação Batch: Aceleração Máxima × FDR":
                dados = self._plot_batch_validation("max_accel")
                nome = "validacao_batch_aceleracao"

            elif estudo == "Batch Run: FDR × Laptime":
                dados = self._plot_batch_laptime(incluir_shift=False)
                nome = "batch_fdr_laptime"

            elif estudo == "Batch Run: FDR × Laptime + trocas":
                shift_time = float(self.shift_time_var.get().replace(',', '.')) if self.shift_time_var.get().strip() else 0.1
                if shift_time < 0:
                    raise ValueError("O tempo por troca não pode ser negativo.")
                dados = self._plot_batch_laptime(incluir_shift=True, shift_time=shift_time)
                nome = f"batch_fdr_laptime_shift_{shift_time:.3f}s"

            self.app.resultados[nome] = dados
            self.current_result_name = nome
            self.current_result = dados
            self._finalizar_figura()
            self._atualizar_tabela()
            self._atualizar_resultados()
            self.notebook.select(0)
            self.status_var.set(f"Resultado gerado: {nome}")
        except Exception as exc:
            if self.fig is not None:
                import matplotlib.pyplot as _plt
                _plt.close(self.fig)
                self.fig = None
            messagebox.showerror("Erro no estudo", str(exc), parent=self.root)

    def _preparar_figura(self):
        if self.fig is not None:
            import matplotlib.pyplot as _plt
            _plt.close(self.fig)
        self.fig = Figure(figsize=(9, 6), dpi=100)

    def _finalizar_figura(self):
        # Aplica a identidade visual no último momento, depois que todos os
        # eixos do estudo foram criados. Assim a mesma marca d'água aparece em
        # todos os gráficos da GUI, inclusive nos estudos de Batch Run.
        if self.fig is not None:
            for eixo in self.fig.axes:
                _add_logo_watermark(eixo, alpha=0.05, zoom=0.50)
        self.fig.tight_layout()
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar is not None:
            try: self.toolbar.destroy()
            except Exception: pass
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.grafico_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.grafico_container, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(fill="x")

    def limpar_grafico(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar is not None:
            try: self.toolbar.destroy()
            except Exception: pass
            self.toolbar = None
        if self.fig is not None:
            import matplotlib.pyplot as _plt
            _plt.close(self.fig)
            self.fig = None
        self.tabela_titulo.configure(text="Nenhum resultado selecionado")
        for item in self.tree_dados.get_children(): self.tree_dados.delete(item)

    # ------------------------------------------------------------------
    # Tabelas
    # ------------------------------------------------------------------
    def _normalizar_tabela(self, dados):
        """Converte resultados comuns em colunas/linhas para o Treeview."""
        if dados is None:
            return [], []
        if isinstance(dados, (int, float, np.number)):
            return ["Valor"], [[float(dados)]]
        if isinstance(dados, dict):
            chaves = list(dados.keys())
            valores = [dados[k] for k in chaves]
            if valores and all(isinstance(v, (list, tuple, np.ndarray)) for v in valores):
                comprimentos = {len(v) for v in valores}
                if len(comprimentos) == 1:
                    return chaves, [list(row) for row in zip(*valores)]
            rows = []
            for chave, valor in dados.items():
                if isinstance(valor, (list, tuple)) and len(valor) == 2 and all(hasattr(x, "__len__") for x in valor):
                    x, y = valor
                    for xx, yy in zip(x, y):
                        rows.append([chave, xx, yy])
                else:
                    rows.append([chave, valor])
            if rows and len(rows[0]) == 3:
                return ["Serie", "X", "Y"], rows
            return ["Parametro", "Valor"], rows
        if isinstance(dados, (list, tuple)):
            if len(dados) == 2 and all(hasattr(x, '__len__') for x in dados):
                x, y = dados
                if len(x) == len(y):
                    return ["X", "Y"], [[a, b] for a, b in zip(x, y)]
            if dados and all(isinstance(r, (list, tuple)) for r in dados):
                # Caso 3+ séries paralelas: [x, y, z] -> uma linha por ponto.
                if len(dados) > 2 and len({len(r) for r in dados}) == 1:
                    return [f"Coluna_{i+1}" for i in range(len(dados))], [list(row) for row in zip(*dados)]
                largura = max(len(r) for r in dados)
                return [f"Coluna_{i+1}" for i in range(largura)], [list(r) + [""] * (largura-len(r)) for r in dados]
            return ["Valor"], [[x] for x in dados]
        return ["Valor"], [[str(dados)]]

    def _atualizar_tabela(self):
        for item in self.tree_dados.get_children(): self.tree_dados.delete(item)
        if self.current_result is None:
            self.tabela_titulo.configure(text="Nenhum resultado selecionado")
            return
        headers, rows = self._normalizar_tabela(self.current_result)
        self.tabela_titulo.configure(text=f"{self.current_result_name} — {len(rows)} linhas")
        self.tree_dados["columns"] = headers
        for h in headers:
            self.tree_dados.heading(h, text=h)
            self.tree_dados.column(h, width=140, anchor="center")
        # Limita somente a quantidade visual de linhas para manter a GUI responsiva.
        for row in rows[:5000]:
            vals = []
            for value in row:
                if isinstance(value, float): vals.append(f"{value:.6g}")
                else: vals.append(str(value))
            self.tree_dados.insert("", "end", values=vals)
        if len(rows) > 5000:
            self.status_var.set(f"Tabela mostrando 5000 de {len(rows)} linhas; o CSV contém todos os dados.")

    def _atualizar_resultados(self):
        for item in self.tree_resultados.get_children(): self.tree_resultados.delete(item)
        for nome, dados in self.app.resultados.items():
            if isinstance(dados, dict): detalhe = f"{len(dados)} séries"
            elif isinstance(dados, (list, tuple)): detalhe = f"{len(dados)} elementos"
            else: detalhe = str(dados)[:40]
            self.tree_resultados.insert("", "end", iid=nome, values=(nome, type(dados).__name__, detalhe))

    def _selecionar_resultado(self, event=None):
        sel = self.tree_resultados.selection()
        if not sel: return
        nome = sel[0]
        if nome not in self.app.resultados: return
        self.current_result_name = nome
        self.current_result = self.app.resultados[nome]
        self._atualizar_tabela()
        self.status_var.set(f"Resultado selecionado: {nome}")

    # ------------------------------------------------------------------
    # Exportação
    # ------------------------------------------------------------------
    def exportar_atual(self):
        if self.current_result is None:
            messagebox.showinfo("Exportação", "Nenhum resultado está selecionado.", parent=self.root)
            return
        self._exportar_nome(self.current_result_name)

    def exportar_selecionado(self):
        sel = self.tree_resultados.selection()
        if not sel:
            messagebox.showinfo("Exportação", "Selecione um resultado na aba 'Resultados em memória'.", parent=self.root)
            return
        self._exportar_nome(sel[0])

    def _exportar_nome(self, nome):
        if nome not in self.app.resultados: return
        caminho = filedialog.asksaveasfilename(
            title="Exportar resultado CSV",
            initialfile=f"{nome}.csv",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not caminho: return
        try:
            self.app._exportar_dados_genericos(Path(caminho), self.app.resultados[nome])
            messagebox.showinfo("Exportação concluída", f"Arquivo salvo em:\n{caminho}", parent=self.root)
        except Exception as exc:
            messagebox.showerror("Erro na exportação", str(exc), parent=self.root)

    def exportar_todos(self):
        if not self.app.resultados:
            messagebox.showinfo("Exportação", "Não há resultados para exportar.", parent=self.root)
            return
        pasta = filedialog.askdirectory(title="Selecionar pasta para exportar todos os CSVs")
        if not pasta: return
        erros = []
        for nome, dados in self.app.resultados.items():
            try:
                self.app._exportar_dados_genericos(Path(pasta) / f"{nome}.csv", dados)
            except Exception as exc:
                erros.append(f"{nome}: {exc}")
        if erros:
            messagebox.showwarning("Exportação parcial", "Alguns arquivos falharam:\n" + "\n".join(erros), parent=self.root)
        else:
            messagebox.showinfo("Exportação concluída", f"{len(self.app.resultados)} arquivos salvos em:\n{pasta}", parent=self.root)

    def salvar_grafico(self):
        if self.fig is None:
            messagebox.showinfo("Salvar gráfico", "Gere um gráfico antes de salvar.", parent=self.root)
            return
        caminho = filedialog.asksaveasfilename(
            title="Salvar gráfico",
            initialfile=f"{self.current_result_name or 'grafico'}.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
        )
        if not caminho: return
        try:
            self.fig.savefig(caminho, dpi=180, bbox_inches="tight")
            messagebox.showinfo("Gráfico salvo", f"Imagem salva em:\n{caminho}", parent=self.root)
        except Exception as exc:
            messagebox.showerror("Erro ao salvar gráfico", str(exc), parent=self.root)

    def _atualizar_status(self):
        if self.carro is not None:
            self.status_var.set(
                f"Veículo completo | FDR = {self.carro.final_drive:.4f} | "
                f"Batch: {'carregado' if self.batch is not None else 'não carregado'} | "
                f"{len(self.app.resultados)} resultado(s) em memória"
            )
        elif self.config_carro is not None or self.arquivo_rpm_torque is not None or self.batch is not None:
            self.status_var.set(
                f"Entradas parciais | carro={'ok' if self.config_carro else '-'} | "
                f"RPM×T={'ok' if self.arquivo_rpm_torque else '-'} | "
                f"Batch={'ok' if self.batch else '-'}"
            )
        else:
            self.status_var.set("Nenhuma entrada carregada. Selecione carro.csv, RPM × Torque ou Batch Run.")


def iniciar_gui():
    root = tk.Tk()
    PlotterPowertrainGUI(root)
    root.mainloop()


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    iniciar_gui()
