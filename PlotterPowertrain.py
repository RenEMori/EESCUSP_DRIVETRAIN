
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

def plotterPrint(text):
    print("PlotterPowertrain: " + text)

def getRPMxTorquePoints() -> list:

    ctypes.windll.user32.MessageBoxW(0, "Selecione o arquivo .csv contendo os pontos RPM x Torque", "PlotterPowertrain", 0)

    from tkinter.filedialog import askopenfilename
    filename = askopenfilename()
    #print(filename)

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

def getGearRatios() -> list: #exige que esteja no formato ctrl c + ctrl v direto do optimum lap
    #basicamente na forma: rpm  torque

    ctypes.windll.user32.MessageBoxW(0, "Selecione o arquivo .csv contendo o escalonamento de marchas", "PlotterPowertrain", 0)
    from tkinter.filedialog import askopenfilename
    filename = askopenfilename()

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

#porcao executavel (eu prefiro, fodase)
if __name__ == "__main__":
    setMatplotParameters()

    mapa = getRPMxTorquePoints()
    print(mapa)
    escalonamento = getGearRatios()
    print(escalonamento)

    carro1 = Carro(mapa, escalonamento, 80/30, 32/11, 0.194)
    #carro1.drawRPMxTorquexPower()
    carro1.gerar_pot_vroda()

    #dados_batch = getBatchRun(0)
    #plotBatchLaptimesFDRShift(dados_batch, 0.1)
    #plotBatchLaptimeFDR(dados_batch)
    
    print("Codigo executado com sucesso")