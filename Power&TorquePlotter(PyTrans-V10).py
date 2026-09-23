import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.ticker import MultipleLocator
import matplotlib.patheffects as pe
import os

dpi=400
rc_params = {
    # Fonte e títulos
    #'font.family': 'serif',            # Fonte geral
    'axes.titlesize': 28,               # Título do gráfico
    'axes.titleweight': 'bold',         # Peso do título
    'axes.titlecolor': '#000000',       # Cor do título
    'axes.labelsize': 20,               # Texto dos eixos
    'axes.labelcolor': '#000000',       # Cor dos rótulos

    # Ticks (eixos)
    'xtick.labelsize': 14,              # Tamanho dos ticks X
    'ytick.labelsize': 14,              # Tamanho dos ticks Y
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
    'lines.linewidth': 4,               # Espessura da curva
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
    'axes.xmargin': 40/dpi,              # Margem X
    'axes.ymargin': 50/dpi                # Margem Y
}
plt.rcParams.update(rc_params)

#Imagem de Fundo e Seus Dados
img = mpimg.imread("logo.png")


class Carro:
    def __init__(self, torque_rpm, relacoes_marcha, relacao_primaria, relacao_secundaria, raio_roda_m, hist):
        self.torque_rpm = torque_rpm  # Dicionário {rpm: torque}
        self.rpm = np.array(sorted(torque_rpm.keys()))
        self.torque_motor = np.array([torque_rpm[rpm] for rpm in self.rpm])
        self.potencia_motor = ((self.torque_motor * self.rpm * 2 * np.pi) / 60)*1.34/1000  # Em HP

        self.relacoes_marcha = np.array(relacoes_marcha)
        self.relacao_primaria = relacao_primaria
        self.relacao_secundaria = relacao_secundaria
        self.final_drive = relacao_primaria * relacao_secundaria
        self.raio_roda = raio_roda_m

        self.hist = hist    # Dicionário {vel: pct}
        self.hist_vel = np.array(sorted(hist.keys()))
        self.hist_pct = np.array([hist[hist_vel] for hist_vel in self.hist_vel])

    def gerar_torque_rpm(self):
        # Cria figura de fundo
        fig, ax = plt.subplots()

        # --- Torque e Potência do Motor ---
        ax.plot(self.rpm, self.torque_motor, label=f'Torque [Nm]')
        ax.plot(self.rpm, self.potencia_motor, label=f'Max Power [HP]', color='orange')

        #Ponto Torque Max
        rpm_maxT = self.rpm[np.argmax(self.torque_motor)]
        ax.scatter(rpm_maxT,max(self.torque_motor),label=f'Max Torque:'
                   f'\n {max(self.torque_motor):.2f}Nm @ {rpm_maxT:.0f}RPM',s=0.5*dpi
                   ,edgecolors="#000000",zorder=7)
        
        #Ponto Pot Max
        rpm_maxP = self.rpm[np.argmax(self.potencia_motor)]
        ax.scatter(rpm_maxP,max(self.potencia_motor),label=f'Max Power:'
                   f'\n {max(self.potencia_motor):.2f}Nm @ {rpm_maxP:.0f}RPM',s=0.5*dpi
                   ,edgecolors="#000000", c="orange",zorder=8)


        plt.title('Torque and Power Curves')
        plt.xlabel('RPM')
        plt.ylabel('Torque (Nm) / Power (HP))')
        plt.legend(loc='lower right')
        # Ticks principais a cada 2 unidades
        ax.xaxis.set_major_locator(MultipleLocator(1000))
        # Ticks menores a cada 0.5 unidade
        ax.xaxis.set_minor_locator(MultipleLocator(500))
        ax.grid(True, which='minor')
        # Grade principal
        ax.grid(True, which='major')
        plt.show()
        
    def gerar_vroda_rpm(self):
        # Cria figura de fundo
        fig, ax = plt.subplots()
        # --- RPM vs Velocidade por marcha ---
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * self.final_drive
            velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6  # km/h
            ax.plot(velocidade, self.rpm, label=f'Marcha {i+1}')
        plt.title('RPM vs Speed Per Gear')
        plt.xlabel('Speed (km/h)')
        plt.ylabel('RPM')
        plt.legend()
        # Ticks principais a cada 10 km/h
        ax.xaxis.set_major_locator(MultipleLocator(10))
        # Ticks menores a cada 5 km/h
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.grid(True, which='minor')
        # Grade principal
        ax.grid(True, which='major')
        plt.show()

    def gerar_troda_vroda(self):
        # Cria figura de fundo
        fig, ax = plt.subplots()

        # --- Torque na roda vs Velocidade ---
    
        V_interpolado = []
        T_interpolado = []
        Gears = []
        # --- Torque na roda vs Velocidade ---
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * self.final_drive
            velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6
            potencia_roda = (self.torque_motor)*rel_total  # mesmo da do motor
            #--- Interpolando Velocidades---
            res = 0.0625
            V_interpolado.append(np.arange(int(velocidade[0])+2,int(velocidade[-1])+1,res))
            V_interpolado[i] = [float(x) for x in V_interpolado[i]]
            
            T_interpolado.append(np.interp(V_interpolado[i],velocidade,potencia_roda))
            T_interpolado[i] = [float(x) for x in T_interpolado[i]]
            ax.plot(V_interpolado[i], T_interpolado[i], linewidth=3.5, zorder=i+3)

        #---Achando Pontos de Troca---
        epsilon = 1
        Trocou = False
        V_shift = []
        T_shift = []
        for i in range(1,len(self.relacoes_marcha)):
            Vi, Ti = V_interpolado[i], T_interpolado[i]
            Vj, Tj = V_interpolado[i-1], T_interpolado[i-1]

            for k in range(len(Vi)):
                for l in range(len(Vj)):
                    if Vi[k] == Vj[l] and abs(Ti[k] - Tj[l]) <= (epsilon/i):
                        V_shift.append(Vi[k])
                        f_med = round((Ti[k] + 3*Tj[l])/4,3)
                        T_shift.append(f_med)
                        Trocou = True
                        break
                if Trocou == True:
                    Trocou = False
                    break

        Rpm_from = []
        Rpm_to = []

        for i in range(len(V_shift)):
            #Separa As RPMS de origem e destino
            rel_from = self.relacoes_marcha[i] * self.final_drive
            rel_to = self.relacoes_marcha[i+1] * self.final_drive
            #velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6
            rpm1 = V_shift[i]*(60*rel_from)/(2*np.pi*self.raio_roda*3.6)
            rpm1 = int(rpm1)
            Rpm_from.append(rpm1)
            rpm2 = V_shift[i]*(60*rel_to)/(2*np.pi*self.raio_roda*3.6)
            rpm2 = int(rpm2)
            Rpm_to.append(rpm2)
            ax.scatter(V_shift[i],T_shift[i],
                        marker='D', zorder=8,
                        label = f'From:{rpm1}rpm\nTo:{rpm2}rpm',
                        s=0.25*dpi,edgecolors="#000000", c="#F0F0F0")
            plt.text(V_shift[i] , T_shift[i]+30 ,
                     f"{i+1} to {i+2}\n{V_shift[i]:.1f} km/h",
                       fontsize=16, va='baseline', 
                       bbox=dict(facecolor='#FFFFFF',
                                  edgecolor="#0E0E0E",
                                    boxstyle='round',), 
                       zorder = (50+i))

        plt.title('Wheel Torque vs Speed')
        plt.xlabel('Speed (km/h)')
        plt.ylabel('Wheel Torque (Nm)')
        plt.legend()
        # Ticks principais a cada 10 km/h
        ax.xaxis.set_major_locator(MultipleLocator(10))
        # Ticks menores a cada 5 km/h
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.grid(True, which='minor')
        # Grade principal
        ax.grid(True, which='major')
        plt.show()
    def gerar_pot_vroda(self):
        # Cria figura de fundo
        fig, ax = plt.subplots()
       
        V_interpolado = []
        P_interpolado = []
        Gears = []
        # --- Potência na roda vs Velocidade ---
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * self.final_drive
            velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6
            potencia_roda = (self.torque_motor * self.rpm * 2 * np.pi / 60)*1  # mesmo da do motor
            #--- Interpolando Velocidades---
            res = 0.125
            V_interpolado.append(np.arange(int(velocidade[0])+2,int(velocidade[-1])+1,res))
            V_interpolado[i] = [float(x) for x in V_interpolado[i]]
            
            P_interpolado.append(np.interp(V_interpolado[i],velocidade,potencia_roda))
            P_interpolado[i] = [float(x)/1000 for x in P_interpolado[i]]
            ax.plot(V_interpolado[i], P_interpolado[i], linewidth=3.5, zorder=i+3)

            #Graf_f, = ax.plot(V_interpolado[i], P_interpolado[i],
            #                label=f'Marcha {i+1}',
            #                zorder= i+3)
            #Gears.append(Graf_f)
        
        #---Achando Pontos de Troca---
        epsilon = 0.25
        Trocou = False
        V_shift = []
        P_shift = []
        for i in range(1,len(self.relacoes_marcha)):
            Vi, Pi = V_interpolado[i], P_interpolado[i]
            Vj, Pj = V_interpolado[i-1], P_interpolado[i-1]

            for k in range(len(Vi)):
                for l in range(len(Vj)):
                    if Vi[k] == Vj[l] and abs(Pi[k] - Pj[l]) <= (epsilon/i):
                        V_shift.append(Vi[k])
                        f_med = round((Pi[k] + 3*Pj[l])/4,3)
                        P_shift.append(f_med)
                        Trocou = True
                        break
                if Trocou == True:
                    Trocou = False
                    break
        
        Rpm_from = []
        Rpm_to = []
        for i in range(len(V_shift)):
            #Separa As RPMS de origem e destino
            rel_from = self.relacoes_marcha[i] * self.final_drive
            rel_to = self.relacoes_marcha[i+1] * self.final_drive
            #velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6
            rpm1 = V_shift[i]*(60*rel_from)/(2*np.pi*self.raio_roda*3.6)
            rpm1 = int(rpm1)
            Rpm_from.append(rpm1)
            rpm2 = V_shift[i]*(60*rel_to)/(2*np.pi*self.raio_roda*3.6)
            rpm2 = int(rpm2)
            Rpm_to.append(rpm2)
            ax.scatter(V_shift[i],P_shift[i],
                        marker='D', zorder=8,
                        label = f'From:{rpm1}rpm\nTo:{rpm2}rpm',
                        s=0.25*dpi,edgecolors="#000000", c="#F0F0F0")
            plt.text(V_shift[i] , P_shift[0]+6 ,
                     f"{i+1} to {i+2}\n{V_shift[i]:.1f} km/h",
                       fontsize=16, ha='center', va='baseline', 
                       bbox=dict(facecolor='#FFFFFF',
                                  edgecolor="#0E0E0E",
                                    boxstyle='round',), 
                       zorder = (50+i))
            
        #leg1 = plt.legend(handles=Gears, loc='upper center',title= 'Gears', ncol=2)
        #plt.gca().add_artist(leg1)  # adiciona manualmente ao gráfico
        #plt.title('Potência na Roda vs Velocidade')
        plt.xlabel('Speed (km/h)')
        plt.ylabel('Wheel Power (HP)')
        plt.legend(loc='lower center', ncol=5,markerscale=2 )
        # Ticks principais a cada 10 km/h
        ax.xaxis.set_major_locator(MultipleLocator(10))
        # Ticks menores a cada 5 km/h
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.grid(True, which='minor')
        # Grade principal
        ax.grid(True, which='major')
        # Margens
        ax.margins(x=0.25, y=0.25)
        plt.xlim(xmin=5, xmax=105)
        plt.show()

    def gerar_pot_histvel(self):
        # Cria figura de fundo
        fig, ax = plt.subplots()
        
        # --- Histograma de Velocidades ---
        fat_escala = 0.5
        hist_pct_escalado = self.hist_pct * fat_escala

        # Aplicar colormap 
        #norm = plt.Normalize(self.hist_pct.min(), self.hist_pct.max())
        #cmap = plt.cm.winter_r
        #cores = cmap(norm(self.hist_pct))  # retorna uma lista de cores RGBA
        barras = plt.bar(self.hist_vel, hist_pct_escalado,width=5 , color="#AFAFAF94", zorder=(6), label='Speed Histogram')
        ax.bar_label(barras, labels=[f"{v/fat_escala:.1f}%" for v in hist_pct_escalado ],
                     label_type='edge',
                     rotation=45,
                      padding=0.5, fontsize=24, color = "#000000", zorder=(len(self.relacoes_marcha)+30),
                        path_effects=[pe.Stroke(linewidth=7.5, foreground="#FFFFFFFF"), # Outline effect: linewidth and color
                      pe.Normal()],
                        #bbox=dict(facecolor="#FFFFFF00",
                        #          edgecolor="#FF0000FF",
                        #            boxstyle='round',), 
                       )
        V_interpolado = []
        P_interpolado = []
        # --- Potência na roda vs Velocidade ---
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * self.final_drive
            velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6
            potencia_roda = (self.torque_motor * self.rpm * 2 * np.pi / 60)*1.34 # mesmo da do motor
            #--- Interpolando Velocidades---
            res = 0.25
            V_interpolado.append(np.arange(int(velocidade[0])+2,int(velocidade[-1])+1,res))
            V_interpolado[i] = [float(x) for x in V_interpolado[i]]
            
            P_interpolado.append(np.interp(V_interpolado[i],velocidade,potencia_roda))
            P_interpolado[i] = [float(x)/1000 for x in P_interpolado[i]]
            ax.plot(V_interpolado[i], P_interpolado[i], linewidth=3.5, zorder=i+6)
        
        #---Plotando Eixos de Referencia---
        indices = []
        epsilon = 0.25
        arr = np.array(V_interpolado[0])
        idx = int(np.where(arr==31.5)[0])
        Mpct = P_interpolado[0][idx]/max(P_interpolado[0])
        h_line=(np.max(P_interpolado[0])*Mpct)
        plt.axhline(h_line, color='Red',linestyle='--',alpha=0.75, linewidth=3.5, zorder=(len(self.relacoes_marcha)+11), label=f'{100*Mpct:.1f}% of Max Power\n({h_line:.2f}HP)')
        indices = np.where(abs(h_line - P_interpolado[0]) <= epsilon)[0]
        indice = int(indices[0])
        v_line=V_interpolado[0][indice]
        plt.axvline(v_line,linestyle='--',alpha=0.75, color='purple', linewidth=3.5, zorder=(len(self.relacoes_marcha)+12), label=f'{100*Mpct:.1f}% of Max Power\n({v_line:.2f}km/h)')
        
        plt.xlabel('Wheel Speed (km/h)')
        plt.ylabel('Wheel Power (HP)')
        plt.legend(loc= 'center right')

        # Ticks principais a cada 10 km/h
        ax.xaxis.set_major_locator(MultipleLocator(10))
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.grid(True, which='major',zorder=2)
        plt.xlim(xmin=5, xmax=105)
        # Ticks menores a cada 5 km/h
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.yaxis.set_minor_locator(MultipleLocator(2.5))
        ax.grid(True, which='minor', zorder=1)

        plt.show()

    def gerar_froda_vroda(self):
        peso = 240 #passar para Classe>>>>>>>
        Cat_pneu = 2.204
        # Cria figura de fundo
        fig, ax = plt.subplots()

        # --- Força na roda vs Velocidade ---
        V_interpolado = []
        F_interpolado = []
        Gears = []
        for i, rel in enumerate(self.relacoes_marcha):
            rel_total = rel * self.final_drive
            velocidade = (self.rpm / 60) * 2 * np.pi * self.raio_roda / rel_total * 3.6
            forca_roda = (self.torque_motor *rel_total / self.raio_roda)
            
            
            #--- Interpolando Velocidades---
            V_interpolado.append(np.arange(int(velocidade[0])+1,int(velocidade[-1])+1,0.125))
            V_interpolado[i] = [float(x) for x in V_interpolado[i]]
            
            F_interpolado.append(np.interp(V_interpolado[i],velocidade,forca_roda))
            F_interpolado[i] = [float(x) for x in F_interpolado[i]]
            Graf_f, = ax.plot(V_interpolado[i], F_interpolado[i],
                            label=f'Marcha {i+1}',
                            zorder= i+3)
            Gears.append(Graf_f)
        #---Achando Pontos de Troca---
        epsilon = 3
        Trocou = False
        V_shift = []
        F_shift = []
        for i in range(1,len(self.relacoes_marcha)):
            Vi, Fi = V_interpolado[i], F_interpolado[i]
            Vj, Fj = V_interpolado[i-1], F_interpolado[i-1]

            for k in range(len(Vi)):
                for l in range(len(Vj)):
                    if Vi[k] == Vj[l] and abs(Fi[k] - Fj[l]) <= (epsilon/i):
                        V_shift.append(Vi[k])
                        f_med = round((3*Fi[k] + Fj[l])/4,3)
                        F_shift.append(f_med)
                        Trocou = True
                        break
                if Trocou == True:
                    Trocou = False
                    break

        for i in range(len(V_shift)):
            ax.scatter(V_shift[i],F_shift[i],
                        marker='o', zorder=8,
                        s=0.25*dpi,edgecolors="#000000", c="#FFFFFF",
                          label = f'{i+1}>{i+2}\n{V_shift[i]:.0f} km/h')
            plt.text(V_shift[i] +4, F_shift[i]+7,
                     f"{i+1} to {i+2}\n{V_shift[i]:.1f} km/h",
                       fontsize=12, ha='center', va='center', 
                       bbox=dict(facecolor='#FFFFFF',
                                  edgecolor="#0E0E0E",
                                    boxstyle='round',), 
                       zorder = (len(self.relacoes_marcha)+4+i))
        plt.title('Força na Roda vs Velocidade')
        plt.xlabel('Speed (km/h)')
        plt.ylabel('Traction Force (N)')
        
        leg1 = plt.legend(handles=Gears, loc='upper center',title= 'Gears', ncol=2)
        plt.gca().add_artist(leg1)  # adiciona manualmente ao gráfico

         #Downforce
        downforce = []
        Atrito = []
        V_min , V_max = ax.get_xlim()
        Vels = np.linspace(0,120,200)
        downforce = (1.16 * 1.14 * 3.87 * (Vels/3.6)**2)/2 #3,54 = CL, Rever depois
        Atrito = (peso*9.81+downforce)*Cat_pneu
        ax.plot(Vels,Atrito)


        # Ticks principais a cada 10 km/h
        ax.xaxis.set_major_locator(MultipleLocator(1/0.125))
        ax.yaxis.set_major_locator(MultipleLocator(2000))
        # Ticks menores a cada 5 km/h
        ax.xaxis.set_minor_locator(MultipleLocator(5/0.125))
        ax.yaxis.set_minor_locator(MultipleLocator(1000))
        ax.grid(True, which='minor',zorder=1)
        # Grade principal
        ax.grid(True, which='major',zorder = 2)

        plt.show()
        


# Exemplo de uso:
torque_exemplo = {
    3500:19.1,3750:20.0,
    4000: 20.5, 4050: 21.6, 4100: 22.4, 4150: 23.1,4200: 23.7,4250: 24.1,
    4300: 24.5,4400: 25.1,4500: 25.5,4600: 25.7,4700:25.7,4800: 25.6,4900: 25.5
    ,5000:25.5,5250:26.0,5500: 27.8,5750: 29.8,6000: 30.7,6250:31.2,6500:31.7,
    6750:32.4,7000:32.9,7180:32.9,7250:32.8,7500:32.4,7600:32.2,7700:32.1,7800:31.9,
    7900:31.8,8000:31.8,8100:31.7,8200:31.7,8300:31.6,8400:31.4,8500:31.2,8580:30.9,
    8600:30.9,8700:30.4,8800:29.9,8900:29.3,9000:28.6,9100:27.9,9200:27.2,9300:26.6,
    9400:26.0,9500:25.4,9600:24.9,9700:24.5,9900:23.7,10000:23.3,10100:23.0,10200:22.5
    }

for key in torque_exemplo:
    torque_exemplo[key] = torque_exemplo[key]*1

hist_exemplo = {
    10: 2.20, 20: 5.83, 30: 8.12,
    40: 23.32, 50: 21.12, 60: 17.35, 70: 13.05,80:5.93,
    90: 2.34, 100: 0.72
}

carro = Carro(
    torque_rpm=torque_exemplo,
    relacoes_marcha=[32/12, 26/14, 27/19, 24/21, 22/23, 21/25],
    relacao_primaria=80/30,
    relacao_secundaria=36/11,
    raio_roda_m=0.194,
    hist=hist_exemplo
)
#-------------------------------------------------------
carro.gerar_troda_vroda()
carro.gerar_vroda_rpm()
carro.gerar_torque_rpm()
carro.gerar_pot_vroda()
carro.gerar_pot_histvel()
#carro.gerar_froda_vroda()