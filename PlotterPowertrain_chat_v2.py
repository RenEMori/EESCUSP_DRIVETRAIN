
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.ticker import MultipleLocator
import matplotlib.patheffects as pe
import time
import ctypes  # An included library with Python install.   
import math


rc_isdef = False
dpi = 0

def setMatplotParameters():
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

def getRPMxTorquePoints(filename) -> list:
    '''
    ctypes.windll.user32.MessageBoxW(0, "Selecione o arquivo .csv contendo os pontos RPM x Torque", "PlotterPowertrain", 0)

    from tkinter.filedialog import askopenfilename
    filename = askopenfilename()
    #print(filename)
    '''
    start_effectiveruntime = time.time()

    mapa = []
    temp = []

    with open(filename, mode='r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            #print(row)
            temp = []
            for cell in row:
                temp.append(float(cell.replace(',', '.')))
            mapa.append(temp)

    mapa.sort() #ordem crescente em RPM

    #print(type(mapa)) mapa e uma variavel do tipo lists de lists
    print("%s segundos de runtime para adquirir dados RPMxTorque" % (time.time() - start_effectiveruntime))
    #ctypes.windll.user32.MessageBoxW(0, "Arquivo pontos extraidos com sucesso", "PlotterPowertrain", 0)
    return mapa

def getGearRatios(filename) -> list: #exige que esteja no formato ctrl c + ctrl v direto do optimum lap
    #basicamente na forma: rpm  torque
    '''
    ctypes.windll.user32.MessageBoxW(0, "Selecione o arquivo .csv contendo o escalonamento de marchas", "PlotterPowertrain", 0)
    from tkinter.filedialog import askopenfilename
    filename = askopenfilename()
    '''
    start_effectiveruntime = time.time()

    mapa = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            mapa.append(float(row[1].replace(',', '.')))

    mapa.sort()
    mapa.reverse()
    #print(type(mapa)) #mapa e uma variavel do tipo lists de lists
    print("%s segundos de runtime para adquirir escalonamento de marchas" % (time.time() - start_effectiveruntime))
    #ctypes.windll.user32.MessageBoxW(0, "Arquivo pontos extraidos com sucesso", "PlotterPowertrain", 0)
    return mapa

def getBatchRun(show_data_index) -> list: # show_data_index: 1 para mostrar no terminal o indice para cada conjunto de dados, 0 para nao mostrar

    ctypes.windll.user32.MessageBoxW(0, "Selecione o arquivo .csv contendo os resultados da Batch Run", "PlotterPowertrain", 0)
    from tkinter.filedialog import askopenfilename
    filename = askopenfilename()
    start_effectiveruntime = time.time()

    #lembrando, o arquivo .csv fica na ordem:
    # 1)perfil do resultado (nome, carro, pista, etc) - [Result Details]
    # 2)KPIs gerais - [KPI Values]
    # 3)Parametros especificos do carro (FDR, downforce, raio de roda, etc) - [Vehicle Parameters]
    # 4)KPIs do carro (pontos de troca, top speed, etc) [Vehicle KPIs]

    perfil = []
    dados = []
    indice = []
    is_perfil = True
    with open(filename, mode='r') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)
        for row in reader:
            #print(row)

            #leitura do perfil da batch run
            if row and is_perfil:
                perfil.append(row)
                continue
            is_perfil = False

            #leitura dos dados
            temp = []
            if row and (len(row) > 2):
                indice.append(row[0])
                for value in row[1:len(row)-1]:
                    temp.append(float(value))
                dados.append(temp)

    #print do perfil
    perfil_text = ""
    for row_perfil in perfil:
        #print(row_perfil[0] + ": " + row_perfil[1])
        perfil_text = perfil_text + row_perfil[0] + ": " + row_perfil[1] + '\n'

    #print dos dados
    #for row_dados in dados:
    #    print(row_dados)
    #print(indice)

    #mostra o indice de cada dado
    if(show_data_index == 1):
        count = 0
        for ii in indice:
            print(str(count) + ": " + ii)
            count = count + 1

    print("%s segundos de runtime para adquirir dados da Batch Run" % (time.time() - start_effectiveruntime))
    ctypes.windll.user32.MessageBoxW(0, "Dados adquiridos com sucesso!\n" + perfil_text + "Tempo para aquisição: " + str(time.time() - start_effectiveruntime), "PlotterPowertrain", 0)
    return dados

def plotBatchLaptimesFDRShift(batch, shift_time):
    # [0]:  laptimes
    # [12]: num de gearshifts
    # [37]: FDR
    start_effectiveruntime = time.time()

    laptimes = batch[0]
    num_shifts = batch[12]
    fdr_range = batch[37]
    fdr_min = fdr_range[0]
    fdr_max = fdr_range[len(fdr_range) - 1]
    laptimes_with_shifts = [t + (gs*shift_time) for t, gs in zip(laptimes, num_shifts)]

    #print(laptimes)
    #print(laptime_with_shifts)

    if(not(rc_isdef)):
        setMatplotParameters()
    
    # Cria figura de fundo
    fig, ax = plt.subplots()

    ax.set_xlabel("Final Drive Ratio [" + str(fdr_min) + "; " + str(fdr_max) + "]")
    ax.set_ylabel("Number of gearshifts")
    ax.bar(fdr_range, num_shifts, label=f"Number of gearshifts\n(" + str(shift_time) + f"s per shift)", color="#00A878", alpha=0.2, width=(fdr_range[1]-fdr_range[0])*0.8)

    ax2 = ax.twinx()
    ax2.set_ylabel('Laptime [s]')
    ax2.plot(fdr_range, laptimes, label=f'Laptimes without shift times', color='#01BAEF')
    ax2.plot(fdr_range, laptimes_with_shifts, label=f'Laptimes with shift times', color='#FE5E41')
    ax2.scatter(fdr_range[laptimes_with_shifts.index(min(laptimes_with_shifts))], min(laptimes_with_shifts), s=50.0, color='red', label=f'Fastest Laptime [s]: ' + str(round(laptimes_with_shifts[laptimes_with_shifts.index(min(laptimes_with_shifts))], 2)) + f'\nFDR: ' + str(fdr_range[laptimes_with_shifts.index(min(laptimes_with_shifts))]))

    plt.title('Laptimes for FDR Batch Runs with Shift Times')

    ax2.xaxis.set_major_locator(MultipleLocator(0.5))
    ax2.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax2.grid(False, which='minor')
    ax2.grid(True, which='major')
    ax.grid(False)

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)

    print("%s segundos de runtime para desenhar grafico FDRxLaptime com shifttimes" % (time.time() - start_effectiveruntime))
    #ctypes.windll.user32.MessageBoxW(0, "Gráfico FDRxLaptime Batch Runs plotado com sucesso!\nTempo para plotar: " + str(time.time() - start_effectiveruntime), "PlotterPowertrain", 0)
    plt.show()

def plotBatchLaptimeFDR(batch):
    # [0]:  laptimes
    # [37]: FDR
    start_effectiveruntime = time.time()

    laptimes = batch[0]
    fdr_range = batch[37]
    fdr_min = fdr_range[0]
    fdr_max = fdr_range[len(fdr_range) - 1]

    if(not(rc_isdef)):
        setMatplotParameters()
    
    # Cria figura de fundo
    fig, ax = plt.subplots()

    ax.set_xlabel("Final Drive Ratio [" + str(fdr_min) + "; " + str(fdr_max) + "]")
    ax.set_ylabel('Laptime [s]')
    ax.plot(fdr_range, laptimes, label=f'Laptimes', color='#01BAEF')

    ax.scatter(fdr_range[laptimes.index(min(laptimes))], min(laptimes), s=50.0, color='red', label=f'Fastest Laptime [s]: ' + str(round(laptimes[laptimes.index(min(laptimes))], 2)) + f'\nFDR: ' + str(fdr_range[laptimes.index(min(laptimes))]))
    #ax.scatter(laptimes.index(max(laptimes)), max(laptimes), s=1.0, color='red', label=f'Slowest Laptime')

    plt.title('Laptimes for FDR Batch Runs')
    plt.legend()

    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(False, which='minor')
    ax.grid(True, which='major')

    print("%s segundos de runtime para desenhar grafico FDRxLaptime" % (time.time() - start_effectiveruntime))
    #ctypes.windll.user32.MessageBoxW(0, "Gráfico FDRxLaptime Batch Runs plotado com sucesso!\nTempo para plotar: " + str(time.time() - start_effectiveruntime), "PlotterPowertrain", 0)
    plt.show()

def getCarroCSV(filename):
    #ordem dos aquivos no .csv
    dados = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file, delimiter=';')
        dados = [row[1] for row in reader]
        return dados

class Carro:
    def __init__(self, mapa_torque_rpm, relacoes_marcha, relacao_primaria, relacao_secundaria, raio_roda_m):
        self.mapa = mapa_torque_rpm #lista [rpm x torque]

        self.rpm = [row[0] for row in self.mapa] #lista
        self.torque = [row[1] for row in self.mapa] #lista
        self.power_kw = [r * t / 9549.2966 for r,t in zip(self.rpm, self.torque)] #potencia em kW #lista
        self.power = [pkw * 1.34102 for pkw in self.power_kw] #potencia em hp #lista

        self.relacoes_marcha = relacoes_marcha # lista
        self.relacao_primaria = relacao_primaria #float
        self.relacao_secundaria = relacao_secundaria #float
        self.final_drive = relacao_primaria * relacao_secundaria
        self.raio_roda = raio_roda_m #float [m]
        self.potencia_max_hp = max(self.power)
        self.max_power = max(self.power)

    def drawRPMxTorquexPower(self):
        start_effectiveruntime = time.time()

        if(not(rc_isdef)):
            setMatplotParameters()
        
        # Cria figura de fundo
        fig, ax = plt.subplots()

        # --- Torque e Potência do Motor ---
        ax.set_xlabel('RPM')
        ax.set_ylabel('Torque [Nm]')
        ax.plot(self.rpm, self.torque, label=f'Torque', color='#FE5E41')
        index_torque_max = self.torque.index(max(self.torque))
        ax.scatter(self.rpm[index_torque_max], self.torque[index_torque_max], s=50.0, color='red', label=f'Max Engine Torque [Nm]: ' + str(round(self.torque[index_torque_max], 2)) + f'\nRPM: ' + str(self.rpm[index_torque_max]))

        ax2 = ax.twinx()
        ax2.set_ylabel('Power [hp]')
        ax2.plot(self.rpm, self.power, label=f'Power', color='#0B0500')
        index_power_max = self.power.index(max(self.power))
        ax.scatter(self.rpm[index_power_max], self.power[index_power_max], s=50.0, color='cyan', label=f'Max Engine Power [hp]: ' + str(round(self.power[index_power_max], 2)) + f'\nRPM: ' + str(self.rpm[index_power_max]))

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
        print("%s segundos de runtime para desenhar curva RPMxTorquexPower" % (time.time() - start_effectiveruntime))
        plt.show()

    def gerar_pot_vroda(self, fdr=None):
            if fdr == None:
                fdr = self.final_drive

            # 1. Cria figura e eixos no Matplotlib
            fig, ax = plt.subplots(figsize=(10, 6))
            dpi_val = fig.dpi  # Obtém resolução da figura para dimensionar pontos

            V_interpolado = []
            P_interpolado = []

            # --- Cálculo de Potência na Roda vs Velocidade para cada marcha ---
            for i, rel in enumerate(self.relacoes_marcha):
                # Relação total de transmissão para a marcha atual
                rel_total = rel * self.final_drive

                # Calcula a velocidade (km/h) para cada ponto de RPM usando list comprehension
                velocidade = [
                    (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                    for r in self.rpm
                ]

                # Potência na roda em HP (utiliza self.power calculado no __init__)
                potencia_roda = self.power

                # --- Gerando vetor de velocidades interpoladas (substituindo np.arange) ---
                res = 0.125
                v_start = int(velocidade[0]) + 2
                v_end = int(velocidade[-1]) + 1

                v_range = []
                curr = float(v_start)
                while curr < v_end:
                    v_range.append(round(curr, 4))
                    curr += res
                V_interpolado.append(v_range)

                # Interpolação linear da potência para os novos pontos de velocidade
                p_interp = interp_1d(V_interpolado[i], velocidade, potencia_roda)
                P_interpolado.append(p_interp)

                # Plota curva de potência x velocidade da marcha atual
                ax.plot(
                    V_interpolado[i],
                    P_interpolado[i],
                    linewidth=1,
                    zorder=i + 3,
                    label=f"Marcha {i+1}",
                )

            # --- Encontrando Pontos Ótimos de Troca de Marcha ---
            epsilon = 0.25
            Trocou = False
            V_shift = []
            P_shift = []

            # Varre marchas consecutivas para identificar intersecções de potência
            for i in range(1, len(self.relacoes_marcha)):
                Vi, Pi = V_interpolado[i], P_interpolado[i]
                Vj, Pj = V_interpolado[i - 1], P_interpolado[i - 1]

                for k in range(len(Vi)):
                    for l in range(len(Vj)):
                        # Verifica igualdade de velocidade e proximidade de potência
                        if Vi[k] == Vj[l] and abs(Pi[k] - Pj[l]) <= (epsilon / i):
                            V_shift.append(Vi[k])
                            f_med = round((Pi[k] + 3 * Pj[l]) / 4, 3)
                            P_shift.append(f_med)
                            Trocou = True
                            break
                    if Trocou:
                        Trocou = False
                        break

            # --- Cálculo das RPMs de Origem/Destino e Anotações no Gráfico ---
            Rpm_from = []
            Rpm_to = []

            for i in range(len(V_shift)):
                rel_from = self.relacoes_marcha[i] * self.final_drive
                rel_to = self.relacoes_marcha[i + 1] * self.final_drive

                # Converte velocidade do ponto de troca de volta para RPM da marcha anterior
                rpm1 = int(
                    V_shift[i]
                    * (60 * rel_from)
                    / (2 * math.pi * self.raio_roda * 3.6)
                )
                Rpm_from.append(rpm1)

                # Converte velocidade do ponto de troca para RPM da próxima marcha
                rpm2 = int(
                    V_shift[i]
                    * (60 * rel_to)
                    / (2 * math.pi * self.raio_roda * 3.6)
                )
                Rpm_to.append(rpm2)

                # Plota marcador do ponto de troca (Losango)
                ax.scatter(
                    V_shift[i],
                    P_shift[i],
                    marker="D",
                    zorder=8,
                    s=0.25 * dpi_val,
                    edgecolors="#000000",
                    c="#F0F0F0",
                )

                # Caixa de texto com indicação das marchas e velocidade da troca
                plt.text(
                    V_shift[i],
                    P_shift[0] + 6,
                    f"{i+1} to {i+2}\n{V_shift[i]:.1f} km/h",
                    fontsize=8,
                    ha="center",
                    va="baseline",
                    bbox=dict(
                        facecolor="#FFFFFF", edgecolor="#0E0E0E", boxstyle="round"
                    ),
                    zorder=(50 + i),
                )

            # --- Configurações Estéticas do Matplotlib ---
            plt.xlabel("Speed (km/h)")
            plt.ylabel("Wheel Power (HP)")
            plt.legend(loc="lower center", ncol=5, markerscale=1.5)

            # Marcações principais (10 km/h) e secundárias (5 km/h) no eixo X
            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.grid(True, which="minor", linestyle=":", alpha=0.6)
            ax.grid(True, which="major", linestyle="-", alpha=0.8)

            ax.margins(x=0.25, y=0.25)
            plt.xlim(left=5, right=105)
            plt.tight_layout()
            plt.show()

    def gerar_troda_vroda(self):
        # 1. Cria figura e eixos no Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        dpi_val = fig.dpi  # Obtém a resolução da figura para dimensionar os marcadores

        # Garante que as relações estejam ordenadas da 1ª para a última marcha (decrescente)
        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)

        V_interpolado = []
        T_interpolado = []

        # --- Cálculo do Torque na Roda vs Velocidade para cada marcha ---
        for i, rel in enumerate(relacoes_ordenadas):
            # Relação total de transmissão para a marcha atual
            rel_total = rel * self.final_drive

            # Calcula a velocidade (km/h) para cada ponto de RPM via list comprehension
            velocidade = [
                (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm
            ]

            # Torque na roda (N.m) = Torque do motor * relação total
            torque_roda = [t * rel_total for t in self.torque]

            # --- Vetor de velocidades interpoladas (substituindo np.arange) ---
            res = 0.0625
            v_start = int(velocidade[0]) + 2
            v_end = int(velocidade[-1]) + 1

            v_range = []
            curr = float(v_start)
            while curr < v_end:
                v_range.append(round(curr, 4))
                curr += res
            V_interpolado.append(v_range)

            # Interpolação linear do torque para os novos pontos de velocidade
            t_interp = interp_1d(V_interpolado[i], velocidade, torque_roda)
            T_interpolado.append(t_interp)

            # Plota a curva de torque x velocidade para a marcha atual
            ax.plot(
                V_interpolado[i],
                T_interpolado[i],
                linewidth=2.5,
                zorder=i + 3,
                label=f"Marcha {i+1}",
            )

        # --- Encontrando Pontos Ótimos de Troca de Marcha ---
        epsilon = 1.0
        Trocou = False
        V_shift = []
        T_shift = []

        # Varre marchas consecutivas para identificar intersecções de torque
        for i in range(1, len(relacoes_ordenadas)):
            Vi, Ti = V_interpolado[i], T_interpolado[i]
            Vj, Tj = V_interpolado[i - 1], T_interpolado[i - 1]

            for k in range(len(Vi)):
                for l in range(len(Vj)):
                    # Utiliza tolerância para comparação de float e verifica aproximação de torque
                    if abs(Vi[k] - Vj[l]) < 1e-4 and abs(Ti[k] - Tj[l]) <= (
                        epsilon / i
                    ):
                        V_shift.append(Vi[k])
                        f_med = round((Ti[k] + 3 * Tj[l]) / 4, 3)
                        T_shift.append(f_med)
                        Trocou = True
                        break
                if Trocou:
                    Trocou = False
                    break

        # --- Cálculo de RPMs de Origem/Destino e Anotações ---
        Rpm_from = []
        Rpm_to = []

        for i in range(len(V_shift)):
            rel_from = relacoes_ordenadas[i] * self.final_drive
            rel_to = relacoes_ordenadas[i + 1] * self.final_drive

            # Converte velocidade do ponto de troca de volta para RPM da marcha anterior
            rpm1 = int(
                V_shift[i]
                * (60 * rel_from)
                / (2 * math.pi * self.raio_roda * 3.6)
            )
            Rpm_from.append(rpm1)

            # Converte velocidade do ponto de troca para RPM da próxima marcha
            rpm2 = int(
                V_shift[i] * (60 * rel_to) / (2 * math.pi * self.raio_roda * 3.6)
            )
            Rpm_to.append(rpm2)

            # Plota marcador do ponto de troca (Losango)
            ax.scatter(
                V_shift[i],
                T_shift[i],
                marker="D",
                zorder=8,
                s=0.25 * dpi_val,
                edgecolors="#000000",
                c="#F0F0F0",
                label=f"From:{rpm1}rpm\nTo:{rpm2}rpm",
            )

            # Caixa de texto posicionada proporcionalmente acima de T_shift[i]
            plt.text(
                V_shift[i],
                T_shift[i] + 30,
                f"{i+1} to {i+2}\n{V_shift[i]:.1f} km/h",
                fontsize=9,
                ha="center",
                va="baseline",
                bbox=dict(
                    facecolor="#FFFFFF", edgecolor="#0E0E0E", boxstyle="round"
                ),
                zorder=(50 + i),
            )

        # --- Configurações Estéticas do Matplotlib ---
        plt.title("Wheel Torque vs Speed")
        plt.xlabel("Speed (km/h)")
        plt.ylabel("Wheel Torque (Nm)")
        plt.legend(loc="upper right", ncol=2)

        # Configuração dos grids e eixos principais (10 km/h) e secundários (5 km/h)
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.grid(True, which="minor", linestyle=":", alpha=0.6)
        ax.grid(True, which="major", linestyle="-", alpha=0.8)

        # Limite superior dinâmico para a velocidade
        max_speed = max(max(v) for v in V_interpolado) if V_interpolado else 105
        plt.xlim(left=0, right=max_speed + 5)

        ax.margins(x=0.05, y=0.15)
        plt.tight_layout()
        plt.show()

    def gerar_froda_vroda(self):
        # =========================================================================
        # 1. INICIALIZAÇÃO DA FIGURA E PARÂMETROS INICIAIS
        # =========================================================================
        fig, ax = plt.subplots(figsize=(10, 6))

        # Obtém o DPI da figura (usado para dimensionar os marcadores graficamente)
        dpi_val = getattr(self, "dpi", fig.dpi)

        # Ordena as relações de marcha da 1ª para a última (ordem decrescente de relação)
        # Isso evita inversões na identificação das marchas no gráfico
        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)

        V_interpolado = []  # Armazenará os vetores de velocidade interpolados por marcha
        F_interpolado = []  # Armazenará os vetores de força na roda interpolados por marcha
        Gears = []  # Lista de objetos de linha do Matplotlib para montar a legenda

        # =========================================================================
        # 2. CÁLCULO DA FORÇA NA RODA E VELOCIDADE POR MARCHA
        # =========================================================================
        for i, rel in enumerate(relacoes_ordenadas):
            # Relação total de transmissão (Relação da Marcha x Relação Final/Diferencial)
            rel_total = rel * self.final_drive

            # Cálculo da Velocidade do Veículo [km/h] para cada ponto de RPM (utilizando Lista)
            velocidade = [
                (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm
            ]

            # Cálculo da Força de Tração na Roda [N] (Torque no Motor * Relação Total / Raio do Pneu)
            forca_roda = [
                (t * rel_total) / self.raio_roda for t in self.torque
            ]

            # --- Criação do Vetor de Velocidades Interpoladas (Substituindo np.arange) ---
            res = 0.125  # Passo de velocidade em km/h
            v_start = int(velocidade[0]) + 1
            v_end = int(velocidade[-1]) + 1

            v_range = []
            curr = float(v_start)
            while curr < v_end:
                v_range.append(round(curr, 4))
                curr += res

            V_interpolado.append(v_range)

            # Interpolação da força para a nova malha fina de velocidades
            f_interp = interp_1d(V_interpolado[i], velocidade, forca_roda)
            F_interpolado.append(f_interp)

            # Plota a curva de tração da marcha atual
            (graf_f,) = ax.plot(
                V_interpolado[i],
                F_interpolado[i],
                label=f"Marcha {i+1}",
                zorder=i + 3,
                linewidth=2.5,
            )
            Gears.append(graf_f)

        # =========================================================================
        # 3. ALGORITMO DE BUSCA DOS PONTOS ÓTIMOS DE TROCA DE MARCHA
        # =========================================================================
        epsilon = 3.0  # Tolerância para a diferença de força entre curvas
        Trocou = False
        V_shift = []  # Velocidades em que ocorrem as trocas
        F_shift = []  # Forças correspondentes nos pontos de troca

        # Compara a marcha atual (i) com a marcha anterior (i-1)
        for i in range(1, len(relacoes_ordenadas)):
            Vi, Fi = V_interpolado[i], F_interpolado[i]  # Marcha superior (ex: 2ª)
            Vj, Fj = V_interpolado[i - 1], F_interpolado[i - 1]  # Marcha inferior (ex: 1ª)

            for k in range(len(Vi)):
                for l in range(len(Vj)):
                    # Comparação segura de float para velocidade (< 1e-4) e verificação de convergência da força
                    if abs(Vi[k] - Vj[l]) < 1e-4 and abs(Fi[k] - Fj[l]) <= (
                        epsilon / i
                    ):
                        V_shift.append(Vi[k])

                        # Média ponderada da força no ponto de intersecção
                        f_med = round((3 * Fi[k] + Fj[l]) / 4, 3)
                        F_shift.append(f_med)

                        Trocou = True
                        break
                if Trocou:
                    Trocou = False
                    break

        # =========================================================================
        # 4. PLOTAGEM DOS MARCADORES E ANOTAÇÕES DE TROCA DE MARCHA
        # =========================================================================
        for i in range(len(V_shift)):
            # Plota o ponto de troca como um círculo branco com borda preta
            ax.scatter(
                V_shift[i],
                F_shift[i],
                marker="o",
                zorder=8,
                s=0.25 * dpi_val,
                edgecolors="#000000",
                c="#FFFFFF",
                label=f"{i+1}>{i+2}\n{V_shift[i]:.0f} km/h",
            )

            # Adiciona a caixa de texto indicando a troca (ex: "1 to 2") acima do ponto exato
            plt.text(
                V_shift[i] + 4,
                F_shift[i] + 7,
                f"{i+1} to {i+2}\n{V_shift[i]:.1f} km/h",
                fontsize=10,
                ha="center",
                va="center",
                bbox=dict(
                    facecolor="#FFFFFF", edgecolor="#0E0E0E", boxstyle="round"
                ),
                zorder=(len(relacoes_ordenadas) + 4 + i),
            )

        # =========================================================================
        # 5. CÁLCULO DA AERO / DOWNFORCE E LIMITE DE ATRITO DOS PNEUS
        # =========================================================================
        # Gera 200 pontos de velocidade entre 0 e 120 km/h
        vels = linspace_pure(0, 120, 200)

        # Cálculo da Carga Aerodinâmica (Downforce [N]) = (1/2) * rho * CdA * v^2
        # Transforma km/h para m/s dividindo por 3.6
        downforce = [(1.16 * 1.14 * 3.87 * ((v / 3.6) ** 2)) / 2 for v in vels]

        # Cálculo do Limite Mecânico de Tração = (Massa * g + Downforce) * Coeficiente_Atrito
        atrito = [
            (self.peso * 9.81 + df) * self.Cat_pneu for df in downforce
        ]

        # Plota a curva do limite de atrito mecânico/aerodinâmico
        ax.plot(
            vels,
            atrito,
            label="Limite de Aderência",
            color="black",
            linestyle="--",
            zorder=2,
        )

        # =========================================================================
        # 6. CONFIGURAÇÕES ESTÉTICAS E FORMATAÇÃO DO GRÁFICO
        # =========================================================================
        plt.title("Força na Roda vs Velocidade")
        plt.xlabel("Speed (km/h)")
        plt.ylabel("Traction Force (N)")

        # Adiciona a legenda referente às curvas de marcha
        leg1 = plt.legend(
            handles=Gears, loc="upper center", title="Gears", ncol=2
        )
        plt.gca().add_artist(leg1)

        # Ticks principais e secundários nos eixos (passo numérico direto)
        ax.xaxis.set_major_locator(MultipleLocator(10))  # Ticks principais a cada 10 km/h
        ax.xaxis.set_minor_locator(MultipleLocator(5))   # Ticks secundários a cada 5 km/h
        ax.yaxis.set_major_locator(MultipleLocator(2000)) # Ticks principais a cada 2000 N
        ax.yaxis.set_minor_locator(MultipleLocator(1000)) # Ticks secundários a cada 1000 N

        # Configuração da grade
        ax.grid(True, which="minor", zorder=1, linestyle=":", alpha=0.5)
        ax.grid(True, which="major", zorder=2, linestyle="-", alpha=0.8)

        plt.tight_layout()
        plt.show()

    def gerar_curva_unica_froda_vroda_v1(self, fdr=None, res=0.125, plotar=True):
        """Gera a curva única (envoltória) de força trativa por velocidade e plota o gráfico.

        Parâmetros:
            res (float): Passo de velocidade em km/h.
            plotar (bool): Se True, exibe o gráfico formatado.

        Retorno:
            lista de listas [[velocidade_km/h, forca_N]]
        """

        if fdr == None:
            fdr = self.final_drive

        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)

        # 1. Curvas originais exatas por marcha
        curvas_marchas = []
        for rel in relacoes_ordenadas:
            rel_total = rel * fdr

            velocidade = [
                (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm
            ]
            forca_roda = [(t * rel_total) / self.raio_roda for t in self.torque]

            curvas_marchas.append((velocidade, forca_roda))

        # 2. Malha global de velocidade
        v_min = min(v_arr[0] for v_arr, _ in curvas_marchas)
        v_max = max(v_arr[-1] for v_arr, _ in curvas_marchas)

        n_pontos = int(round((v_max - v_min) / res)) + 1
        malha = [round(v_min + k * res, 4) for k in range(n_pontos)]

        # 3. Construção da envoltória
        curva = []
        for v in malha:
            melhor_f = None
            for velocidade, forca_roda in curvas_marchas:
                if v < velocidade[0] or v > velocidade[-1]:
                    continue

                f = interp_1d([v], velocidade, forca_roda)[0]
                if melhor_f is None or f > melhor_f:
                    melhor_f = f

            if melhor_f is not None:
                curva.append([v, round(melhor_f, 3)])

        # 4. Plotagem do gráfico
        if plotar and curva:
            vels = [p[0] for p in curva]
            forcas = [p[1] for p in curva]

            fig, ax = plt.subplots(figsize=(10, 6))

            # Plota as marchas individuais suavemente ao fundo para referência visual
            for idx, (v_g, f_g) in enumerate(curvas_marchas):
                ax.plot(
                    v_g,
                    f_g,
                    linestyle="--",
                    alpha=0.35,
                    linewidth=1.2,
                    label=f"Marcha {idx + 1}",
                )

            # Plota a curva única unificada em destaque
            ax.plot(
                vels,
                forcas,
                color="red",
                linewidth=2.5,
                label="Curva Única (Envoltória)",
                zorder=5,
            )

            # Configurações do gráfico
            ax.set_title(
                "Curva Única de Força Trativa na Roda vs Velocidade", fontsize=12
            )
            ax.set_xlabel("Velocidade (km/h)")
            ax.set_ylabel("Força Trativa (N)")

            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.yaxis.set_major_locator(MultipleLocator(2000))
            ax.yaxis.set_minor_locator(MultipleLocator(1000))

            ax.grid(True, which="minor", linestyle=":", alpha=0.5, zorder=1)
            ax.grid(True, which="major", linestyle="-", alpha=0.8, zorder=2)
            ax.legend(loc="upper right")

            plt.tight_layout()
            plt.show()

        return curva

    def _limite_atrito(self, v_kmh):
        """Limite de tração [N] por aderência, incluindo downforce."""
        v_ms = v_kmh / 3.6
        downforce = (1.16 * 1.14 * 3.87 * v_ms**2) / 2
        return (self.peso * 9.81 + downforce) * self.Cat_pneu


    def gerar_curva_unica_froda_vroda_v2(
        self,
        res=0.125,
        considerar_atrito=False,
        plotar=False,
        mostrar_marchas=True,
        mostrar_limite_atrito=True,
        salvar_em=None,
    ):
        """Gera uma curva única (envoltória) de força trativa por velocidade.

        Parâmetros:
            res: passo de velocidade [km/h]
            considerar_atrito: limita a força ao limite de aderência dos pneus
            plotar: se True, plota o gráfico
            mostrar_marchas: desenha as curvas individuais de cada marcha (tracejadas, ao fundo)
            mostrar_limite_atrito: desenha a curva do limite de aderência
            salvar_em: caminho de arquivo para salvar a figura (opcional)

        Retorna:
            [[velocidade_1, forca_1], [velocidade_2, forca_2], ...]
        """
        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)

        # 1. Curvas individuais por marcha
        curvas_marchas = []
        for rel in relacoes_ordenadas:
            rel_total = rel * self.final_drive
            v_gear = [
                (r / 60) * 2 * math.pi * self.raio_roda / rel_total * 3.6
                for r in self.rpm
            ]
            f_gear = [(t * rel_total) / self.raio_roda for t in self.torque]
            curvas_marchas.append({"v": v_gear, "f": f_gear})

        # 2. Intervalo global
        v_min_global = min(c["v"][0] for c in curvas_marchas)
        v_max_global = max(c["v"][-1] for c in curvas_marchas)

        # 3. Função auxiliar: maior força disponível em uma velocidade
        def _forca_max(v):
            f_max = None
            for c in curvas_marchas:
                if c["v"][0] <= v <= c["v"][-1]:
                    f_val = interp_1d([v], c["v"], c["f"])[0]
                    if f_max is None or f_val > f_max:
                        f_max = f_val
            if f_max is not None and considerar_atrito:
                f_max = min(f_max, self._limite_atrito(v))
            return f_max

        # 4. Varredura (sem acúmulo de erro) + endpoint exato
        n = int(math.floor((v_max_global - v_min_global) / res + 1e-9)) + 1
        velocidades = [round(v_min_global + k * res, 4) for k in range(n)]
        if velocidades[-1] < v_max_global - 1e-9:
            velocidades.append(round(v_max_global, 4))

        curva_combinada = []
        for v in velocidades:
            f = _forca_max(v)
            if f is not None:
                curva_combinada.append([v, round(f, 3)])

        # 5. Plot opcional
        if plotar:
            fig, ax = plt.subplots(figsize=(10, 6))

            if mostrar_marchas:
                for i, c in enumerate(curvas_marchas):
                    ax.plot(
                        c["v"], c["f"],
                        linestyle="--", linewidth=1.2, alpha=0.6,
                        label=f"Marcha {i+1}", zorder=3,
                    )

            ax.plot(
                [p[0] for p in curva_combinada],
                [p[1] for p in curva_combinada],
                color="red", linewidth=2.8,
                label="Curva única (envoltória)", zorder=5,
            )

            if mostrar_limite_atrito:
                vels = linspace_pure(0, max(120, v_max_global), 200)
                ax.plot(
                    vels, [self._limite_atrito(v) for v in vels],
                    color="black", linestyle="--", linewidth=1.5,
                    label="Limite de Aderência", zorder=2,
                )

            ax.set_title("Curva Única de Força Trativa vs Velocidade")
            ax.set_xlabel("Speed (km/h)")
            ax.set_ylabel("Traction Force (N)")
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)

            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.yaxis.set_major_locator(MultipleLocator(2000))
            ax.yaxis.set_minor_locator(MultipleLocator(1000))
            ax.grid(True, which="minor", linestyle=":", alpha=0.5, zorder=1)
            ax.grid(True, which="major", linestyle="-", alpha=0.8, zorder=1)

            ax.legend(loc="upper right")
            fig.tight_layout()

            if salvar_em:
                fig.savefig(salvar_em, dpi=150)
            plt.show()

        return curva_combinada

    def calcular_perda_area_potencia(self, fdr=None, res=0.125, plotar=True):
        """Calcula a razão entre a perda de área de tração real e a área de potência ideal.

        Parâmetros:
            potencia_max_hp (float): Potência máxima em cv / hp.
            res (float): Resolução da malha de velocidade em km/h.
            plotar (bool): Se True, exibe o gráfico com as curvas e a área
            rachurada.

        Retorno:
            float: Razão (Area_potencia - Area_real) / Area_potencia
        """

        if fdr == None:
            fdr = self.final_drive

        # 1. Identifica a rotação (RPM) dos picos de torque e potência do motor
        max_torque = max(self.torque)
        rpm_pico_torque = self.rpm[self.torque.index(max_torque)]

        max_power = max(self.power)
        rpm_pico_power = self.rpm[self.power.index(max_power)]

        # 2. Define as relações totais da 1ª marcha (maior) e da última marcha (menor)
        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)
        rel_1a = relacoes_ordenadas[0] * fdr
        rel_ult = relacoes_ordenadas[-1] * fdr

        # 3. Calcula os limites de velocidade de integração [km/h]
        v_lim_inf = (
            (rpm_pico_torque / 60) * 2 * math.pi * self.raio_roda / rel_1a * 3.6
        )
        v_lim_sup = (
            (rpm_pico_power / 60) * 2 * math.pi * self.raio_roda / rel_ult * 3.6
        )

        # 4. Obtém a curva única (envoltória real de tração)
        curva_unificada = self.gerar_curva_unica_froda_vroda_v1(fdr=fdr, res=res, plotar=False)
        v_env = [p[0] for p in curva_unificada]
        f_env = [p[1] for p in curva_unificada]

        # 5. Gera a malha de velocidades dentro do intervalo [v_lim_inf, v_lim_sup]
        n_pts = max(2, int(round((v_lim_sup - v_lim_inf) / res)) + 1)
        v_integ = [round(v_lim_inf + k * res, 4) for k in range(n_pts)]
        if v_integ[-1] < v_lim_sup:
            v_integ.append(round(v_lim_sup, 4))

        # Converte a potência máxima de HP para Watts (1 HP = 745.7 W)
        p_watts = self.potencia_max_hp * 745.7

        f_pot_integ = []
        f_real_integ = []

        # 6. Avalia as forças ideais (P_max / v) e reais (envoltória)
        for v in v_integ:
            v_ms = v / 3.6  # km/h para m/s
            f_pot = p_watts / v_ms
            f_real = interp_1d([v], v_env, f_env)[0]

            f_pot_integ.append(f_pot)
            f_real_integ.append(f_real)

        # 7. Integração numérica pelas Áreas (Regra do Trapézio)
        area_pot = 0.0
        area_real = 0.0
        for i in range(len(v_integ) - 1):
            dv = v_integ[i + 1] - v_integ[i]
            area_pot += (f_pot_integ[i] + f_pot_integ[i + 1]) / 2.0 * dv
            area_real += (f_real_integ[i] + f_real_integ[i + 1]) / 2.0 * dv

        diferenca_area = area_pot - area_real
        razao = diferenca_area / area_pot

        # 8. Plotagem do gráfico
        if plotar:
            fig, ax = plt.subplots(figsize=(11, 6.5))

            # Plota curvas das marchas individuais ao fundo
            for idx, rel in enumerate(relacoes_ordenadas):
                rel_tot = rel * self.final_drive
                v_g = [
                    (r / 60) * 2 * math.pi * self.raio_roda / rel_tot * 3.6
                    for r in self.rpm
                ]
                f_g = [(t * rel_tot) / self.raio_roda for t in self.torque]
                ax.plot(
                    v_g,
                    f_g,
                    linestyle="--",
                    alpha=0.35,
                    linewidth=1.2,
                    label=f"Marcha {idx + 1}",
                )

            # Plota curva única real (envoltória)
            ax.plot(
                v_env,
                f_env,
                color="red",
                linewidth=2.5,
                label="Força Trativa Real (Envoltória)",
                zorder=4,
            )

            # Plota curva de potência máxima constante
            ax.plot(
                v_integ,
                f_pot_integ,
                color="blue",
                linewidth=2.0,
                label="Curva de Potência Máxima Ideal",
                zorder=5,
            )

            # Preenche a área entre as curvas com rachura (hatch)
            ax.fill_between(
                v_integ,
                f_real_integ,
                f_pot_integ,
                where=[fp >= fr for fp, fr in zip(f_pot_integ, f_real_integ)],
                color="orange",
                alpha=0.35,
                hatch="//",
                edgecolor="darkorange",
                label="Área de Perda Trativa",
                zorder=3,
            )

            # Linhas verticais indicando os limites de integração
            ax.axvline(
                v_lim_inf,
                color="green",
                linestyle=":",
                linewidth=1.5,
                label=f"Limite Inf (Pico Torque 1ª): {v_lim_inf:.1f} km/h",
            )
            ax.axvline(
                v_lim_sup,
                color="purple",
                linestyle=":",
                linewidth=1.5,
                label=f"Limite Sup (Pico Pot. Úl): {v_lim_sup:.1f} km/h",
            )

            # Formatação do gráfico
            ax.set_title(
                f"Análise de Eficiência de Tração vs Potência Máxima\n"
                f"Razão de Perda de Área: {razao:.2%} ({razao:.4f})",
                fontsize=12,
            )
            ax.set_xlabel("Velocidade (km/h)")
            ax.set_ylabel("Força Trativa (N)")

            ax.xaxis.set_major_locator(MultipleLocator(10))
            ax.xaxis.set_minor_locator(MultipleLocator(5))
            ax.yaxis.set_major_locator(MultipleLocator(2000))
            ax.yaxis.set_minor_locator(MultipleLocator(1000))

            ax.grid(True, which="minor", linestyle=":", alpha=0.5, zorder=1)
            ax.grid(True, which="major", linestyle="-", alpha=0.8, zorder=2)
            ax.legend(loc="upper right", fontsize=9)

            plt.tight_layout()
            plt.show()

        return razao

    def calcular_perda_area_potencia_range(self, fdr_range, res=0.125):
        """Calcula a razão entre a perda de área de tração real e a área de potência ideal.

        Parâmetros:
            potencia_max_hp (float): Potência máxima em cv / hp.
            res (float): Resolução da malha de velocidade em km/h.
            plotar (bool): Se True, exibe o gráfico com as curvas e a área
            rachurada.

        Retorno:
            float: Razão (Area_potencia - Area_real) / Area_potencia
        """

        # 1. Identifica a rotação (RPM) dos picos de torque e potência do motor
        max_torque = max(self.torque)
        rpm_pico_torque = self.rpm[self.torque.index(max_torque)]

        max_power = max(self.power)
        rpm_pico_power = self.rpm[self.power.index(max_power)]

        # 2. Define as relações totais da 1ª marcha (maior) e da última marcha (menor)
        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)

        range_razoes = []

        for fdr in fdr_range:
            rel_1a = relacoes_ordenadas[0] * fdr
            rel_ult = relacoes_ordenadas[-1] * fdr
    
            # 3. Calcula os limites de velocidade de integração [km/h]
            v_lim_inf = (
                (rpm_pico_torque / 60) * 2 * math.pi * self.raio_roda / rel_1a * 3.6
            )
            v_lim_sup = (
                (rpm_pico_power / 60) * 2 * math.pi * self.raio_roda / rel_ult * 3.6
            )
    
            # 4. Obtém a curva única (envoltória real de tração)
            curva_unificada = self.gerar_curva_unica_froda_vroda_v1(fdr=fdr,res=res, plotar=False)
            v_env = [p[0] for p in curva_unificada]
            f_env = [p[1] for p in curva_unificada]
    
            # 5. Gera a malha de velocidades dentro do intervalo [v_lim_inf, v_lim_sup]
            n_pts = max(2, int(round((v_lim_sup - v_lim_inf) / res)) + 1)
            v_integ = [round(v_lim_inf + k * res, 4) for k in range(n_pts)]
            if v_integ[-1] < v_lim_sup:
                v_integ.append(round(v_lim_sup, 4))
    
            # Converte a potência máxima de HP para Watts (1 HP = 745.7 W)
            p_watts = self.potencia_max_hp * 745.7
    
            f_pot_integ = []
            f_real_integ = []
    
            # 6. Avalia as forças ideais (P_max / v) e reais (envoltória)
            for v in v_integ:
                v_ms = v / 3.6  # km/h para m/s
                f_pot = p_watts / v_ms
                f_real = interp_1d([v], v_env, f_env)[0]
    
                f_pot_integ.append(f_pot)
                f_real_integ.append(f_real)
    
            # 7. Integração numérica pelas Áreas (Regra do Trapézio)
            area_pot = 0.0
            area_real = 0.0
            for i in range(len(v_integ) - 1):
                dv = v_integ[i + 1] - v_integ[i]
                area_pot += (f_pot_integ[i] + f_pot_integ[i + 1]) / 2.0 * dv
                area_real += (f_real_integ[i] + f_real_integ[i + 1]) / 2.0 * dv
    
            diferenca_area = area_pot - area_real
            razao = diferenca_area / area_pot
            range_razoes.append(razao)

        resultados = [fdr_range, range_razoes]

        if(not(rc_isdef)):
                setMatplotParameters()
            
        # Cria figura de fundo
        fig, ax = plt.subplots()

        ax.set_xlabel("Final Drive Ratio [" + str(min(fdr_range)) + "; " + str(max(fdr_range)) + "]")
        ax.set_ylabel('Razão de aproveitamento')
        ax.plot(fdr_range, range_razoes, label=f'Razões', color='#01BAEF')

        ax.scatter(fdr_range[range_razoes.index(min(range_razoes))], min(range_razoes), s=50.0, color='red', label=f'Menor razão: ' + str(round(range_razoes[range_razoes.index(min(range_razoes))], 4)) + f'\nFDR: ' + str(fdr_range[range_razoes.index(min(range_razoes))]))
        #ax.scatter(laptimes.index(max(laptimes)), max(laptimes), s=1.0, color='red', label=f'Slowest Laptime')

        plt.title('Laptimes for FDR Batch Runs')
        plt.legend()

        ax.xaxis.set_major_locator(MultipleLocator(0.5))
        ax.xaxis.set_minor_locator(MultipleLocator(0.1))
        ax.grid(False, which='minor')
        ax.grid(True, which='major')

        plt.show()

        return resultados

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
            potencia_roda = self.power  # Potência correspondente ao RPM

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
                curvas_marchas.append((velocidade, self.power))

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
            plt.show()

        return resultados

# =============================================================================
# INTERFACE DE USO
# =============================================================================

from pathlib import Path


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
        self.carro = None
        self.arquivo_carro = None
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

    def carregar_carro(self):
        print("\n--- Carregamento do veículo ---")
        caminho = input("Caminho do carro.csv: ").strip().strip('"')
        if not caminho:
            print("Operação cancelada.")
            return

        caminho = Path(caminho)
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            return

        try:
            dados = getCarroCSV(str(caminho))
            if len(dados) < 5:
                raise ValueError(
                    "O carro.csv deve conter pelo menos 5 linhas: "
                    "mapa RPM x torque, relações, relação primária, "
                    "relação secundária e raio da roda."
                )

            self.carro = Carro(
                getRPMxTorquePoints(str(dados[0])),
                getGearRatios(str(dados[1])),
                float(dados[2].replace(',', '.')),
                float(dados[3].replace(',', '.')),
                float(dados[4].replace(',', '.')),
            )
            self.arquivo_carro = caminho
            self.resultados.clear()
            print("\nVeículo carregado com sucesso.")
            self.mostrar_resumo_carro()
        except Exception as exc:
            print(f"Erro ao carregar o veículo: {exc}")

    def mostrar_resumo_carro(self):
        if self.carro is None:
            print("Nenhum veículo carregado.")
            return

        c = self.carro
        print("\n--- Resumo do veículo ---")
        print(f"Arquivo: {self.arquivo_carro}")
        print(f"RPM: {c.rpm[0]:.0f} -> {c.rpm[-1]:.0f}")
        print(f"Torque máximo: {max(c.torque):.2f} Nm")
        print(f"Potência máxima: {c.max_power:.2f} HP")
        print(f"Relações de marcha: {[round(x, 4) for x in c.relacoes_marcha]}")
        print(f"Relação primária: {c.relacao_primaria:.4f}")
        print(f"Relação secundária: {c.relacao_secundaria:.4f}")
        print(f"FDR atual: {c.final_drive:.4f}")
        print(f"Raio da roda: {c.raio_roda:.4f} m")

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

        # Caso: dict {FDR: [velocidades, valores]}
        if isinstance(dados, dict):
            linhas = []
            for chave, valor in dados.items():
                if isinstance(valor, (list, tuple)) and len(valor) == 2:
                    x, y = valor
                    for xx, yy in zip(x, y):
                        linhas.append([chave, xx, yy])
                else:
                    linhas.append([chave, valor])

            if linhas and len(linhas[0]) == 3:
                self._escrever_linhas_csv(
                    caminho, ["FDR", "Velocidade_km_h", "Valor"], linhas
                )
            else:
                self._escrever_linhas_csv(caminho, ["FDR", "Valor"], linhas)
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
                dados = c.gerar_troda_vroda()
                self._salvar_resultado("torque_roda", dados)

            elif opcao == 4:
                dados = c.gerar_froda_vroda()
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
        try:
            batch = getBatchRun(0)
            if opcao == 11:
                plotBatchLaptimeFDR(batch)
                dados = [batch[37], batch[0]]
                self._salvar_resultado("batch_fdr_laptime", dados)
            elif opcao == 12:
                shift = self._float("Tempo de troca por marcha [0.1 s]: ", default=0.1, minimo=0)
                plotBatchLaptimesFDRShift(batch, shift)
                fdr = batch[37]
                laptimes = batch[0]
                shifts = batch[12]
                laptimes_com_shift = [t + n * shift for t, n in zip(laptimes, shifts)]
                self._salvar_resultado(
                    "batch_fdr_laptime_shift",
                    {
                        "FDR": [fdr, laptimes],
                        "FDR_com_shift": [fdr, laptimes_com_shift],
                    },
                )
        except Exception as exc:
            print(f"Erro no Batch Run: {exc}")

    # -------------------------------------------------------------------------
    # Menus
    # -------------------------------------------------------------------------
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
        print(" 2  Mostrar resumo do veículo")
        print(" 3  Gráfico RPM x Torque x Potência")
        print(" 4  Gráfico Velocidade x Potência na roda")
        print(" 5  Gráfico Velocidade x Torque na roda")
        print(" 6  Gráfico Velocidade x Força trativa por marcha")
        print(" 7  Curva unificada de força trativa (V1)")
        print(" 8  Curva unificada de força trativa (V2 + atrito)")
        print(" 9  Perda de área de potência para um FDR")
        print("10  Perda de área para uma faixa de FDRs")
        print("11  Curva unificada de potência na roda")
        print("12  Comparar potência na roda para vários FDRs")
        print("13  Batch Run: FDR x Laptime")
        print("14  Batch Run: Laptime + tempo de troca")
        print("15  Preparar/exportar dados-base")
        print("16  Exportar um resultado CSV")
        print("17  Exportar todos os resultados CSV")
        print("18  Listar resultados em memória")
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

        # Permite iniciar diretamente solicitando o carro, sem obrigar o usuário a navegar no menu.
        carregar = self._sim_nao("Deseja carregar um carro.csv agora?", default=True)
        if carregar:
            self.carregar_carro()

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
                self.mostrar_resumo_carro()
            elif 3 <= opcao <= 12:
                # O menu foi numerado para o usuário; as opções da classe usam 1..10.
                self.executar_grafico(opcao - 2)
            elif opcao in (13, 14):
                self.executar_batch(opcao - 2)
            elif opcao == 15:
                self.exportar_dados_base()
                self.exportar_resultado()
            elif opcao == 16:
                self.exportar_resultado()
            elif opcao == 17:
                self.exportar_todos()
            elif opcao == 18:
                self.listar_resultados()
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
        self.root.title("Plotter Powertrain - Fórmula SAE")
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)

        setMatplotParameters()

        self.app = InterfacePlotterPowertrain()
        self.carro = None
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
        header = ttk.Frame(self.root, padding=(12, 10, 12, 5))
        header.pack(fill="x")
        ttk.Label(header, text="Plotter Powertrain", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Estudo de relação secundária / Final Drive Ratio", style="Status.TLabel").pack(side="left", padx=15, pady=5)
        ttk.Button(header, text="Carregar carro.csv", command=self.carregar_carro, style="Accent.TButton").pack(side="right")

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
        def row(label, variable, r):
            ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", pady=2)
            entry = ttk.Entry(parent, textvariable=variable, width=18)
            entry.grid(row=r, column=1, sticky="ew", padx=(8, 0), pady=2)
            return entry

        self.param_widgets.append(("fdr", row("FDR:", self.fdr_var, 0)))
        self.param_widgets.append(("res", row("Resolução [km/h]:", self.res_var, 1)))
        self.param_widgets.append(("ini", row("FDR inicial:", self.fdr_ini_var, 2)))
        self.param_widgets.append(("fim", row("FDR final:", self.fdr_fim_var, 3)))
        self.param_widgets.append(("passo", row("Passo FDR:", self.fdr_passo_var, 4)))
        self.param_widgets.append(("lista", row("FDRs:", self.fdr_lista_var, 5)))

        parent.columnconfigure(1, weight=1)
        self.chk_atrito = ttk.Checkbutton(parent, text="Considerar limite de atrito", variable=self.atrito_var)
        self.chk_marchas = ttk.Checkbutton(parent, text="Mostrar marchas", variable=self.mostrar_marchas_var)
        self.chk_limite = ttk.Checkbutton(parent, text="Mostrar limite de atrito", variable=self.mostrar_limite_var)
        self.chk_atrito.grid(row=6, column=0, columnspan=2, sticky="w", pady=2)
        self.chk_marchas.grid(row=7, column=0, columnspan=2, sticky="w", pady=2)
        self.chk_limite.grid(row=8, column=0, columnspan=2, sticky="w", pady=2)

    def _atualizar_parametros(self):
        estudo = self.estudo_var.get()
        usar_fdr = estudo in {
            "Potência na roda por marcha", "Força trativa unificada",
            "Perda de área para um FDR", "Potência na roda unificada"
        }
        usar_range = estudo == "Perda de área × FDR"
        usar_lista = estudo == "Comparação de potência × FDR"
        usar_res = estudo not in {"RPM × Torque × Potência"}
        usar_atrito = estudo == "Força unificada + limite de atrito"
        usar_checks = estudo == "Força unificada + limite de atrito"

        for nome, widget in self.param_widgets:
            widget.grid_remove()
        self.chk_atrito.grid_remove()
        self.chk_marchas.grid_remove()
        self.chk_limite.grid_remove()

        nomes = []
        if usar_fdr: nomes.append("fdr")
        if usar_res: nomes.append("res")
        if usar_range: nomes += ["ini", "fim", "passo"]
        if usar_lista: nomes.append("lista")

        row = 0
        for nome, widget in self.param_widgets:
            if nome in nomes:
                widget.grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
                # Label correspondente está na coluna 0; recupera o label pelo grid slaves.
                row += 1

        # Os labels não acompanham o grid_remove acima, então reconstruímos visibilidade.
        for child in self.param_widgets:
            pass

        # Melhor abordagem: ocultar toda a área e reconstruir labels/entries de forma simples.
        for child in self.param_widgets:
            child[1].grid_remove()
            info = child[1].grid_info()
            # O label é obtido pelos widgets na mesma linha original.

        # Reposicionamento explícito dos widgets e labels associados.
        # Os labels foram criados antes e permanecem em parent.children.
        parent = self.param_widgets[0][1].master
        widgets = list(parent.winfo_children())
        labels = [w for w in widgets if isinstance(w, ttk.Label)]
        label_map = {}
        for lab in labels:
            txt = str(lab.cget("text"))
            label_map[txt] = lab

        entry_map = {nome: widget for nome, widget in self.param_widgets}
        label_names = {
            "fdr": "FDR:", "res": "Resolução [km/h]:", "ini": "FDR inicial:",
            "fim": "FDR final:", "passo": "Passo FDR:", "lista": "FDRs:"
        }
        for lab in labels:
            lab.grid_remove()
        row = 0
        for nome in nomes:
            label_map[label_names[nome]].grid(row=row, column=0, sticky="w", pady=2)
            entry_map[nome].grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
            row += 1

        if usar_atrito:
            self.chk_atrito.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
            row += 1
        if usar_checks:
            self.chk_marchas.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
            row += 1
            self.chk_limite.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)

    # ------------------------------------------------------------------
    # Carregamento / dados
    # ------------------------------------------------------------------
    def carregar_carro(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar carro.csv",
            filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            dados = getCarroCSV(caminho)
            if len(dados) < 5:
                raise ValueError("O arquivo precisa conter as 5 entradas esperadas do carro.csv.")
            carro = Carro(
                getRPMxTorquePoints(dados[0]),
                getGearRatios(dados[1]),
                float(dados[2].replace(',', '.')),
                float(dados[3].replace(',', '.')),
                float(dados[4].replace(',', '.')),
            )
            self.carro = carro
            self.app.carro = carro
            self.app.arquivo_carro = Path(caminho)
            self.app.resultados.clear()
            self._mostrar_dados_carregados()
            self._atualizar_resultados()
            self.limpar_grafico()
            self.status_var.set(f"Carregado: {Path(caminho).name} | FDR = {carro.final_drive:.4f}")
        except Exception as exc:
            messagebox.showerror("Erro ao carregar", str(exc), parent=self.root)

    def _mostrar_dados_carregados(self):
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        if self.carro is None:
            self.info_text.insert("end", "Nenhum veículo carregado.")
        else:
            c = self.carro
            linhas = [
                f"Arquivo: {self.app.arquivo_carro}",
                "",
                f"RPM: {c.rpm[0]:.0f} → {c.rpm[-1]:.0f}",
                f"Pontos RPM × torque: {len(c.rpm)}",
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
            ]
            self.info_text.insert("end", "\n".join(linhas))
        self.info_text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Cálculos para gráficos embutidos
    # ------------------------------------------------------------------
    def _curvas_marcha(self, tipo, fdr=None, res=0.125):
        c = self.carro
        fdr = c.final_drive if fdr is None else fdr
        curvas = []
        for i, rel in enumerate(c.relacoes_marcha):
            rel_total = rel * fdr
            velocidade = [
                (r / 60) * 2 * math.pi * c.raio_roda / rel_total * 3.6
                for r in c.rpm
            ]
            if tipo == "potencia":
                valores = c.power
            elif tipo == "torque":
                valores = [t * rel_total for t in c.torque]
            else:
                valores = [(t * rel_total) / c.raio_roda for t in c.torque]
            curvas.append((velocidade, valores, i + 1))
        return curvas

    def _plot_engine(self):
        c = self.carro
        ax = self.fig.add_subplot(111)
        ax.plot(c.rpm, c.torque, label="Torque [Nm]")
        ax.scatter([c.rpm[c.torque.index(max(c.torque))]], [max(c.torque)])
        ax.set_xlabel("RPM")
        ax.set_ylabel("Torque [Nm]")
        ax2 = ax.twinx()
        ax2.plot(c.rpm, c.power, label="Potência [HP]")
        ax2.scatter([c.rpm[c.power.index(max(c.power))]], [max(c.power)])
        ax2.set_ylabel("Potência [HP]")
        ax.set_title("Curva de Torque e Potência do Motor")
        l1, t1 = ax.get_legend_handles_labels()
        l2, t2 = ax2.get_legend_handles_labels()
        ax.legend(l1 + l2, t1 + t2, loc="best")
        ax.grid(True, alpha=0.3)
        return [c.rpm, c.torque, c.power]

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
        # Usa a função existente para garantir que a curva calculada seja exatamente a do modelo.
        curva = c.gerar_curva_unica_froda_vroda_v2(
            res=res, considerar_atrito=atrito, plotar=False,
            mostrar_marchas=mostrar_marchas, mostrar_limite_atrito=mostrar_limite
        )
        # A função v2 usa self.final_drive; para estudo de um FDR diferente usamos a v1,
        # que recebe FDR, e aplicamos o limite de aderência quando solicitado.
        if abs(fdr - c.final_drive) > 1e-12:
            curva = c.gerar_curva_unica_froda_vroda_v1(fdr=fdr, res=res, plotar=False)
            if atrito:
                curva = [[v, min(f, c._limite_atrito(v))] for v, f in curva]

        ax = self.fig.add_subplot(111)
        if mostrar_marchas:
            for v, f, i in self._curvas_marcha("forca", fdr, res):
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
        # A função retorna somente o escalar. Recria as curvas para fornecer visualização.
        curva = c.gerar_curva_unica_froda_vroda_v1(fdr=fdr, res=res, plotar=False)
        ax = self.fig.add_subplot(111)
        if curva:
            v = np.array([p[0] for p in curva])
            f = np.array([p[1] for p in curva])
            ax.plot(v, f, label="Força real")
            p_watts = c.max_power * 745.7
            v_ms = v / 3.6
            ideal = np.divide(p_watts, v_ms, out=np.zeros_like(v), where=v_ms > 0)
            ax.plot(v, ideal, label="Força ideal por potência máxima")
        ax.set_xlabel("Velocidade [km/h]")
        ax.set_ylabel("Força [N]")
        ax.set_title(f"Perda de área — FDR = {fdr:.4f} | Razão = {razao:.5f} ({razao:.2%})")
        ax.legend()
        ax.grid(True, alpha=0.3)
        return razao

    # ------------------------------------------------------------------
    # Execução do estudo
    # ------------------------------------------------------------------
    def executar_estudo(self):
        if self.carro is None:
            messagebox.showwarning("Veículo não carregado", "Carregue um carro.csv antes de executar um estudo.", parent=self.root)
            return

        try:
            estudo = self.estudo_var.get()
            c = self.carro
            res = float(self.res_var.get().replace(',', '.')) if self.res_var.get().strip() else 0.125
            if res <= 0:
                raise ValueError("A resolução deve ser maior que zero.")
            fdr = float(self.fdr_var.get().replace(',', '.')) if self.fdr_var.get().strip() else c.final_drive

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
        if dados is None:
            return [], []
        if isinstance(dados, (int, float, np.number)):
            return ["Valor"], [[float(dados)]]
        if isinstance(dados, dict):
            rows = []
            for chave, valor in dados.items():
                if isinstance(valor, (list, tuple)) and len(valor) == 2 and all(hasattr(x, '__len__') for x in valor):
                    x, y = valor
                    for xx, yy in zip(x, y): rows.append([chave, xx, yy])
                else:
                    rows.append([chave, valor])
            if rows and len(rows[0]) == 3: return ["FDR", "X", "Y"], rows
            return ["FDR", "Valor"], rows
        if isinstance(dados, (list, tuple)):
            if len(dados) == 2 and all(hasattr(x, '__len__') for x in dados):
                x, y = dados
                if len(x) == len(y): return ["X", "Y"], [[a, b] for a, b in zip(x, y)]
            if dados and all(isinstance(r, (list, tuple)) for r in dados):
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
        if self.carro is None:
            self.status_var.set("Nenhum veículo carregado. Selecione um carro.csv para começar.")
        else:
            self.status_var.set(f"Veículo carregado | FDR = {self.carro.final_drive:.4f} | {len(self.app.resultados)} resultado(s) em memória")


def iniciar_gui():
    root = tk.Tk()
    PlotterPowertrainGUI(root)
    root.mainloop()


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    iniciar_gui()
