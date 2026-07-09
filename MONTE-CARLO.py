import pandas as pd
from collections import defaultdict, deque
from graphviz import Digraph
import math
import numpy as np
import matplotlib.pyplot as plt

plazo_objetivo = 19  # Cambiar al plazo deseado
N = 40000  # Número de simulaciones


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 0) Funciones generales

def lee_pred(cell):  # Predecesoras
    text = str(cell).strip()

    if text == "-" or text == "" or text.lower() == "nan":
        return []

    return [x.strip() for x in text.split(",")]


def tiempos_pert(To, Tm, Tp):  # Tiempo esperado PERT
    return (To + 4 * Tm + Tp) / 6


def varianza_pert(To, Tp):  # Varianza PERT aproximada
    return ((Tp - To) / 6) ** 2


def normal_cdf(z):
    # Función de distribución acumulada de la normal estándar
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def beta_pert(To, Tm, Tp, lamb=4):
    """
    Genera una duración aleatoria siguiendo una distribución beta-PERT.
    To: tiempo optimista
    Tm: tiempo más probable
    Tp: tiempo pesimista
    lamb: parámetro de forma. En PERT clásico suele tomarse lamb = 4.
    """

    if Tp == To:
        return To

    alpha = 1 + lamb * (Tm - To) / (Tp - To)
    beta = 1 + lamb * (Tp - Tm) / (Tp - To)

    x = np.random.beta(alpha, beta)

    return To + x * (Tp - To)


def calcular_pert(tabla, columna_duracion):
    """
    Calcula ES, EF, LS, LF, holguras, camino crítico y duración total del proyecto
    usando la columna de duración indicada.
    """

    #----------------------------------------------------------------------
    # Recorrido hacia delante: ES y EF

    lista_ES = []
    lista_EF = []

    for i in range(len(tabla)):
        predec = tabla.loc[i, "Pred"]
        dur = tabla.loc[i, columna_duracion]

        if predec == []:
            ES = 0
        else:
            EF_predecesoras = []

            for pred in predec:
                for j in range(len(tabla)):
                    if tabla.loc[j, "ID"] == pred:
                        EF_predecesoras.append(lista_EF[j])

            ES = max(EF_predecesoras)

        EF = ES + dur

        lista_ES.append(ES)
        lista_EF.append(EF)

    duracion_proyecto = max(lista_EF)

    #----------------------------------------------------------------------
    # Recorrido hacia atrás: LS y LF

    lista_LF = [0.0] * len(tabla)
    lista_LS = [0.0] * len(tabla)

    for i in range(len(tabla)-1, -1, -1):
        succ = tabla.loc[i, "Succ"]
        dur = tabla.loc[i, columna_duracion]

        if succ == []:
            LF = duracion_proyecto
        else:
            LS_sucesoras = []

            for suc in succ:
                for j in range(len(tabla)):
                    if tabla.loc[j, "ID"] == suc:
                        LS_sucesoras.append(lista_LS[j])

            LF = min(LS_sucesoras)

        LS = LF - dur

        lista_LF[i] = LF
        lista_LS[i] = LS

    #----------------------------------------------------------------------
    # Holgura y camino crítico

    lista_holgura = []

    for i in range(len(tabla)):
        holgura = lista_LS[i] - lista_ES[i]
        lista_holgura.append(holgura)

    camino_critico = []

    for i in range(len(tabla)):
        act = tabla.loc[i, "ID"]
        holgura = lista_holgura[i]

        if abs(holgura) < 0.0001:
            camino_critico.append(act)

    return lista_ES, lista_EF, lista_LS, lista_LF, lista_holgura, camino_critico, duracion_proyecto


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1) Leemos Excel

EXCEL = "Caso_Prueba.xlsx"
SHEET = "Inputs"

tabla = pd.read_excel(EXCEL, sheet_name=SHEET)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 2) Limpiar tabla y crear columnas básicas

tabla["ID"] = tabla["ID"].astype(str).str.strip()

lista_pred = []

for i in range(len(tabla)):
    pred = tabla.loc[i, "Predecesoras"]
    pred_leidas = lee_pred(pred)
    lista_pred.append(pred_leidas)

tabla["Pred"] = lista_pred


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 3) Calcular tiempo esperado y varianza PERT

lista_te = []

for i in range(len(tabla)):
    To = tabla.loc[i, "To"]
    Tm = tabla.loc[i, "Tm"]
    Tp = tabla.loc[i, "Tp"]

    te = tiempos_pert(To, Tm, Tp)
    lista_te.append(te)

tabla["te"] = lista_te


lista_var = []

for i in range(len(tabla)):
    To = tabla.loc[i, "To"]
    Tp = tabla.loc[i, "Tp"]

    var = varianza_pert(To, Tp)
    lista_var.append(var)

tabla["Var"] = lista_var


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 4) Validaciones básicas

ids = tabla["ID"].tolist()

# IDs duplicados
if len(ids) != len(set(ids)):
    raise ValueError("Hay IDs de actividades duplicados en el Excel.")

# Predecesoras inexistentes
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    preds = tabla.loc[i, "Pred"]

    for pred in preds:
        if pred not in ids:
            raise ValueError(f"La actividad '{act}' tiene una predecesora inexistente: '{pred}'.")

# Validar que To <= Tm <= Tp
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    To = tabla.loc[i, "To"]
    Tm = tabla.loc[i, "Tm"]
    Tp = tabla.loc[i, "Tp"]

    if not (To <= Tm <= Tp):
        raise ValueError(f"La actividad '{act}' no cumple To <= Tm <= Tp.")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 5) Orden topológico automático

adj = defaultdict(list)     # lista de sucesoras
indeg = defaultdict(int)    # número de predecesoras

# Inicializar indeg en 0 para todas
for act in ids:
    indeg[act] = 0

# Construir grafo
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    preds = tabla.loc[i, "Pred"]

    for pred in preds:
        adj[pred].append(act)
        indeg[act] += 1

# Algoritmo de Kahn
cola = deque()

for act in ids:
    if indeg[act] == 0:
        cola.append(act)

orden_topologico = []

while cola:
    nodo = cola.popleft()
    orden_topologico.append(nodo)

    for suc in adj[nodo]:
        indeg[suc] -= 1

        if indeg[suc] == 0:
            cola.append(suc)

# Comprobar ciclos
if len(orden_topologico) != len(ids):
    raise ValueError("El grafo tiene un ciclo o una dependencia inválida. No se puede obtener un orden topológico.")

# Reordenar tabla según orden topológico
tabla["OrdenTopo"] = tabla["ID"].apply(lambda x: orden_topologico.index(x))
tabla = tabla.sort_values("OrdenTopo").reset_index(drop=True)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 6) Crear lista de sucesoras

lista_succ = []

for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    sucesoras = []

    for j in range(len(tabla)):
        pred_j = tabla.loc[j, "Pred"]

        if act in pred_j:
            sucesoras.append(tabla.loc[j, "ID"])

    lista_succ.append(sucesoras)

tabla["Succ"] = lista_succ


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 7) PERT clásico con tiempos esperados

ES, EF, LS, LF, Holgura, camino_critico, duracion_proyecto = calcular_pert(tabla, "te")

tabla["ES"] = ES
tabla["EF"] = EF
tabla["LS"] = LS
tabla["LF"] = LF
tabla["Holgura"] = Holgura


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 8) Incertidumbre PERT clásica del proyecto

var_proyecto = 0

for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]

    if act in camino_critico:
        var_proyecto += tabla.loc[i, "Var"]

desv_proyecto = math.sqrt(var_proyecto)
media_proyecto = duracion_proyecto

IC_68_inf = media_proyecto - 1 * desv_proyecto
IC_68_sup = media_proyecto + 1 * desv_proyecto

IC_95_inf = media_proyecto - 1.96 * desv_proyecto
IC_95_sup = media_proyecto + 1.96 * desv_proyecto

IC_997_inf = media_proyecto - 3 * desv_proyecto
IC_997_sup = media_proyecto + 3 * desv_proyecto


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 9) Probabilidad clásica de cumplir un plazo objetivo usando aproximación normal



if desv_proyecto == 0:
    if plazo_objetivo >= media_proyecto:
        prob_cumplimiento = 1.0
        z = 0
    else:
        prob_cumplimiento = 0.0
        z = 0
else:
    z = (plazo_objetivo - media_proyecto) / desv_proyecto
    prob_cumplimiento = normal_cdf(z)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 10) Mostrar resultados PERT clásico

print("\nTabla completa PERT clásico:")
print(tabla[["ID", "Pred", "Succ", "te", "Var", "ES", "EF", "LS", "LF", "Holgura"]])

print("\nDuración total esperada del proyecto:", round(duracion_proyecto, 2))
print("Camino crítico:", camino_critico)

print("\n--- ANÁLISIS DE INCERTIDUMBRE PERT CLÁSICO ---")
print("Varianza del proyecto:", round(var_proyecto, 4))
print("Desviación típica del proyecto:", round(desv_proyecto, 4))

print("\nIntervalo de confianza aproximado del 68%:")
print(f"[{IC_68_inf:.2f}, {IC_68_sup:.2f}]")

print("\nIntervalo de confianza aproximado del 95%:")
print(f"[{IC_95_inf:.2f}, {IC_95_sup:.2f}]")

print("\nIntervalo de confianza aproximado del 99.7%:")
print(f"[{IC_997_inf:.2f}, {IC_997_sup:.2f}]")

print("\n--- PROBABILIDAD DE CUMPLIMIENTO DE PLAZO PERT CLÁSICO ---")
print("Plazo objetivo:", plazo_objetivo)
print("Valor z:", round(z, 4))
print("Probabilidad de terminar antes del plazo:", f"{prob_cumplimiento * 100:.2f}%")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 11) Simulación Monte Carlo



duraciones_simuladas = []
frecuencia_critica = {act: 0 for act in tabla["ID"]}

for simulacion in range(N):

    #--------------------------------------------------------
    # 11.1) Generar una duración aleatoria para cada actividad

    lista_dur_sim = []

    for i in range(len(tabla)):
        To = tabla.loc[i, "To"]
        Tm = tabla.loc[i, "Tm"]
        Tp = tabla.loc[i, "Tp"]

        dur = beta_pert(To, Tm, Tp)
        lista_dur_sim.append(dur)

    tabla["dur_sim"] = lista_dur_sim

    #--------------------------------------------------------
    # 11.2) Recalcular PERT con las duraciones simuladas

    ES_sim, EF_sim, LS_sim, LF_sim, Holgura_sim, camino_critico_sim, duracion_sim = calcular_pert(tabla, "dur_sim")

    #--------------------------------------------------------
    # 11.3) Guardar duración total simulada

    duraciones_simuladas.append(duracion_sim)

    #--------------------------------------------------------
    # 11.4) Contar frecuencia de criticidad

    for act in camino_critico_sim:
        frecuencia_critica[act] += 1


# Convertir a array de NumPy para calcular estadísticas
duraciones_simuladas = np.array(duraciones_simuladas)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 12) Resultados estadísticos de Monte Carlo

media_MC = np.mean(duraciones_simuladas)
desv_MC = np.std(duraciones_simuladas, ddof=1)

min_MC = np.min(duraciones_simuladas)
max_MC = np.max(duraciones_simuladas)

p5 = np.percentile(duraciones_simuladas, 5)
p50 = np.percentile(duraciones_simuladas, 50)
p80 = np.percentile(duraciones_simuladas, 80)
p90 = np.percentile(duraciones_simuladas, 90)
p95 = np.percentile(duraciones_simuladas, 95)

prob_cumplimiento_MC = np.mean(duraciones_simuladas <= plazo_objetivo)


print("\n\n============================================================")
print("RESULTADOS DE SIMULACIÓN MONTE CARLO")
print("============================================================")

print("\nNúmero de simulaciones:", N)

print("\nDuración media simulada:", round(media_MC, 2))
print("Desviación típica simulada:", round(desv_MC, 2))
print("Duración mínima simulada:", round(min_MC, 2))
print("Duración máxima simulada:", round(max_MC, 2))

print("\nPercentiles de duración:")
print("P5 :", round(p5, 2))
print("P50:", round(p50, 2))
print("P80:", round(p80, 2))
print("P90:", round(p90, 2))
print("P95:", round(p95, 2))

print("\nProbabilidad simulada de cumplir el plazo objetivo:")
print(f"{prob_cumplimiento_MC * 100:.2f}%")

print("\n--- FRECUENCIA DE CRITICIDAD ---")

for act in frecuencia_critica:
    porcentaje = frecuencia_critica[act] / N * 100
    print(act, ":", f"{porcentaje:.2f}%")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 13) Crear tabla resumen de frecuencias críticas

tabla_criticidad = pd.DataFrame({
    "ID": list(frecuencia_critica.keys()),
    "Frecuencia crítica": list(frecuencia_critica.values())
})

tabla_criticidad["Porcentaje crítico"] = tabla_criticidad["Frecuencia crítica"] / N * 100

tabla_criticidad = tabla_criticidad.sort_values("Porcentaje crítico", ascending=False).reset_index(drop=True)

print("\nTabla de criticidad:")
print(tabla_criticidad)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 14) Guardar resultados en Excel

with pd.ExcelWriter("Resultados_PERT_MonteCarlo.xlsx") as writer:
    tabla.to_excel(writer, sheet_name="PERT_Clasico", index=False)
    pd.DataFrame({"Duracion_simulada": duraciones_simuladas}).to_excel(writer, sheet_name="MonteCarlo", index=False)
    tabla_criticidad.to_excel(writer, sheet_name="Criticidad", index=False)

print("\nResultados guardados en 'Resultados_PERT_MonteCarlo.xlsx'")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 15) Curva continua aproximada de las duraciones simuladas sin usar scipy

# Crear histograma internamente, pero sin dibujarlo
densidad, bordes = np.histogram(duraciones_simuladas, bins=60, density=True)

# Calcular el centro de cada intervalo
centros = (bordes[:-1] + bordes[1:]) / 2

# Suavizado mediante media móvil
ventana = 5
kernel = np.ones(ventana) / ventana
densidad_suavizada = np.convolve(densidad, kernel, mode="same")

plt.figure()

plt.plot(centros, densidad_suavizada, linewidth=2, label="Densidad estimada Monte Carlo")

plt.axvline(plazo_objetivo, color="red", linestyle="--", linewidth=2, label="Plazo objetivo")
plt.axvline(media_MC, color="green", linestyle="-", linewidth=2, label="Media simulada")

plt.xlabel("Duración total del proyecto")
plt.ylabel("Densidad de probabilidad")
plt.title("Distribución continua aproximada de la duración del proyecto")
plt.legend()
plt.grid(True)
plt.show()



#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 16) Grafo AoN resaltando camino crítico clásico

grafo = Digraph("AoN", format="png")
grafo.attr(rankdir="LR")

# Crear nodos
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]

    if act in camino_critico:
        grafo.node(act, act, shape="circle", style="filled", fillcolor="red", fontcolor="white")
    else:
        grafo.node(act, act, shape="circle")

# Crear flechas
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    predec = tabla.loc[i, "Pred"]

    for pred in predec:
        if pred in camino_critico and act in camino_critico:
            grafo.edge(pred, act, color="red", penwidth="2")
        else:
            grafo.edge(pred, act)

grafo.render("diagrama_AoN_critico", view=True)

print("\nDiagrama AoN con camino crítico clásico generado.")
