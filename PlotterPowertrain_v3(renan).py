
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
        self.peso = 240
        self.Cat_pneu = 2.204
        self.potencia_max_hp = max(self.power)

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

    def gerar_pot_vroda(self):
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

    def gerar_curva_unica_froda_vroda_v1(self, res=0.125, plotar=True):
        """Gera a curva única (envoltória) de força trativa por velocidade e plota o gráfico.

        Parâmetros:
            res (float): Passo de velocidade em km/h.
            plotar (bool): Se True, exibe o gráfico formatado.

        Retorno:
            lista de listas [[velocidade_km/h, forca_N]]
        """
        relacoes_ordenadas = sorted(self.relacoes_marcha, reverse=True)

        # 1. Curvas originais exatas por marcha
        curvas_marchas = []
        for rel in relacoes_ordenadas:
            rel_total = rel * self.final_drive

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

    def calcular_perda_area_potencia(self, res=0.125, plotar=True):
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
        rel_1a = relacoes_ordenadas[0] * self.final_drive
        rel_ult = relacoes_ordenadas[-1] * self.final_drive

        # 3. Calcula os limites de velocidade de integração [km/h]
        v_lim_inf = (
            (rpm_pico_torque / 60) * 2 * math.pi * self.raio_roda / rel_1a * 3.6
        )
        v_lim_sup = (
            (rpm_pico_power / 60) * 2 * math.pi * self.raio_roda / rel_ult * 3.6
        )

        # 4. Obtém a curva única (envoltória real de tração)
        curva_unificada = self.gerar_curva_unica_froda_vroda_v1(res=res, plotar=False)
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

#porcao executavel (eu prefiro, fodase)
if __name__ == "__main__":
    setMatplotParameters()

    #mapa = getRPMxTorquePoints()
    #print(mapa)
    #escalonamento = getGearRatios()
    #print(escalonamento)

    #carro.csv 
    dados = getCarroCSV("C:\\Users\\Renan\\Desktop\\FORMULA\\E24\\RELACAOSECUNDARIA\\carro_teste.csv")
    print(dados)

    carro1 = Carro(getRPMxTorquePoints(str(dados[0])), getGearRatios(str(dados[1])), float(dados[2]), float(dados[3]), float(dados[4]))
    option = ''

    while(option != 0):
        option = input("Selecione uma opção digitando o número no terminal:\n0) Sair\n1) Gerar gráfico RPM x Torque\n2) Gerar gráfico Vel. de roda x Potência\n3) Gerar gráfico Vel. de roda x Torque na Roda\n4) Gerar gráfico Vel. de roda x Força trativa dispoível\n Opção: ")
        match (int(option)):
            case 0:
                option = 0
                break
            case 1:
                carro1.drawRPMxTorquexPower()
            case 2:
                carro1.gerar_pot_vroda()
            case 3:
                carro1.gerar_troda_vroda()
            case 4:
                carro1.gerar_froda_vroda()
            case 5:
                carro1.gerar_curva_unica_froda_vroda_v1()
            case 6:
                carro1.gerar_curva_unica_froda_vroda_v2(plotar=True)
            case 7:
                carro1.calcular_perda_area_potencia()

    #dados_batch = getBatchRun(0)
    #plotBatchLaptimesFDRShift(dados_batch, 0.1)
    #plotBatchLaptimeFDR(dados_batch)
    
    print("Codigo executado com sucesso")
