import pandas as pd
from collections import defaultdict, deque
from graphviz import Digraph
import math
from html import escape

plazo_objetivo = 760  # CAMBIAR VALOR AL DESEADO



#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 0) Funciones

def lee_pred(cell):  # Predecesoras
    text = str(cell).strip()

    if text == "-" or text == "" or text.lower() == "nan":
        return []

    return [x.strip() for x in text.split(",")]

def tiempos_pert(To, Tm, Tp):  # Tiempo esperado
    return (To + 4 * Tm + Tp) / 6

def varianza_pert(To, Tp):  # Varianza PERT
    return ((Tp - To) / 6) ** 2

def normal_cdf(z):
    # CDF de la normal estándar usando erf
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))






#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1) Leemos Excel

EXCEL = "Caso_Estudio.xlsx"
SHEET = "Inputs"
tabla = pd.read_excel(EXCEL, sheet_name=SHEET)








#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 2) Limpiar tabla y crear columnas

tabla["ID"] = tabla["ID"].astype(str).str.strip()

lista_pred = []
for i in range(len(tabla)):
    pred = tabla.loc[i, "Predecesoras"]
    pred_leidas = lee_pred(pred)
    lista_pred.append(pred_leidas)

tabla["Pred"] = lista_pred


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
# 3) Validaciones básicas

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






#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 4) ORDEN TOPOLOGICO 

adj = defaultdict(list)     # lista de sucesoras
indeg = defaultdict(int)    # número de predecesoras


for act in ids:
    indeg[act] = 0

# Construir grafo
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    preds = tabla.loc[i, "Pred"]

    for pred in preds:
        adj[pred].append(act)
        indeg[act] += 1

# Kahn
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
# 5) Crear lista de sucesoras

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
# 6) EARLIEST START y EARLIEST FINISH

lista_ES = []
lista_EF = []

for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    predec = tabla.loc[i, "Pred"]
    te = tabla.loc[i, "te"]

    if predec == []:
        ES = 0
    else:
        EF_predecesoras = []

        for pred in predec:
            for j in range(len(tabla)):
                if tabla.loc[j, "ID"] == pred:
                    EF_predecesoras.append(lista_EF[j])

        ES = max(EF_predecesoras)

    EF = ES + te

    lista_ES.append(ES)
    lista_EF.append(EF)

tabla["ES"] = lista_ES
tabla["EF"] = lista_EF








#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 7) LATEST START y LATEST FINISH

duracion_proyecto = max(tabla["EF"])

lista_LF = [0.0] * len(tabla)
lista_LS = [0.0] * len(tabla)

for i in range(len(tabla)-1, -1, -1):
    act = tabla.loc[i, "ID"]
    succ = tabla.loc[i, "Succ"]
    te = tabla.loc[i, "te"]

    if succ == []:
        LF = duracion_proyecto
    else:
        LS_sucesoras = []

        for suc in succ:
            for j in range(len(tabla)):
                if tabla.loc[j, "ID"] == suc:
                    LS_sucesoras.append(lista_LS[j])

        LF = min(LS_sucesoras)

    LS = LF - te

    lista_LF[i] = LF
    lista_LS[i] = LS

tabla["LF"] = lista_LF
tabla["LS"] = lista_LS








#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 8) HOLGURA (*Cambiar a margen) y CAMINO CRÍTICO

lista_holgura = []

for i in range(len(tabla)):
    ES = tabla.loc[i, "ES"]
    LS = tabla.loc[i, "LS"]

    holgura = LS - ES
    lista_holgura.append(holgura)

tabla["Holgura"] = lista_holgura


camino_critico = []

for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    holgura = tabla.loc[i, "Holgura"]

    if abs(holgura) < 0.0001:
        camino_critico.append(act)










#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 9) INCERTIDUMBRE PERT DEL PROYECTO

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
# 10) PROBABILIDAD DE CUMPLIR UN PLAZO OBJETIVO



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
# 11) MOSTRAR RESULTADOS

print("\nTabla completa PERT:")
print(tabla[["ID", "Pred", "Succ", "te", "Var", "ES", "EF", "LS", "LF", "Holgura"]])

print("\nDuración total esperada del proyecto:", round(duracion_proyecto, 2))
print("Camino crítico:", camino_critico)

print("\n--- ANÁLISIS DE INCERTIDUMBRE PERT ---")
print("Varianza del proyecto:", round(var_proyecto, 4))
print("Desviación típica del proyecto:", round(desv_proyecto, 4))

print("\nIntervalo de confianza aproximado del 68%:")
print(f"[{IC_68_inf:.2f}, {IC_68_sup:.2f}]")

print("\nIntervalo de confianza aproximado del 95%:")
print(f"[{IC_95_inf:.2f}, {IC_95_sup:.2f}]")

print("\nIntervalo de confianza aproximado del 99.7%:")
print(f"[{IC_997_inf:.2f}, {IC_997_sup:.2f}]")

print("\n--- PROBABILIDAD DE CUMPLIMIENTO DE PLAZO ---")
print("Plazo objetivo:", plazo_objetivo)
print("Probabilidad de terminar antes del plazo:", f"{prob_cumplimiento * 100:.2f}%")









#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 12) Crear grafo AoN con nodos tipo tabla y resaltando camino crítico

grafo = Digraph("AoN", format="png")
grafo.attr(rankdir="LR")
grafo.attr("graph", splines="ortho", nodesep="0.8", ranksep="1.2")
grafo.attr("node", shape="plain")
grafo.attr("edge", arrowsize="0.8")

# Buscar columna de nombre de actividad, si existe
if "Actividad" in tabla.columns:
    col_nombre = "Actividad"
elif "Nombre de tarea" in tabla.columns:
    col_nombre = "Nombre de tarea"
else:
    col_nombre = None


def formato_numero(x):
    return f"{x:.1f}"


def formato_numero(x):
    if abs(x) < 0.0001:
        x = 0
    return f"{x:.1f}"



def crear_label_aon(act, nombre, duracion, ES, EF, LS, LF, holgura, critica):
    """
    Crea una etiqueta HTML para Graphviz con formato tipo nodo AoN:
    ES | Duration | EF
    Activity Description
    LS | Total Float | LF
    """

    if critica:
        color_borde = "red"
        color_fondo = "#FFE6E6"
    else:
        color_borde = "blue"
        color_fondo = "#EEF7F7"

    act = escape(str(act))

    # Evitar nombres vacíos o NaN
    if nombre is None or str(nombre).lower() == "nan":
        nombre = ""
    else:
        nombre = escape(str(nombre))

    duracion = formato_numero(duracion)
    ES = formato_numero(ES)
    EF = formato_numero(EF)
    LS = formato_numero(LS)
    LF = formato_numero(LF)
    holgura = formato_numero(holgura)

    # Si no hay descripción, solo se muestra el ID
    if nombre == "":
        texto_central = f"""
        <FONT POINT-SIZE="12"><B>{act}</B></FONT>
        """
    else:
        texto_central = f"""
        <FONT POINT-SIZE="12"><B>{act}</B></FONT><BR/>
        <FONT POINT-SIZE="10">{nombre}</FONT>
        """

    label = f"""<
<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" COLOR="{color_borde}">
    <TR>
        <TD><FONT POINT-SIZE="10">ES<BR/><B>{ES}</B></FONT></TD>
        <TD><FONT POINT-SIZE="10">Duracion<BR/><B>{duracion}</B></FONT></TD>
        <TD><FONT POINT-SIZE="10">EF<BR/><B>{EF}</B></FONT></TD>
    </TR>
    <TR>
        <TD COLSPAN="3" BGCOLOR="{color_fondo}">
            {texto_central}
        </TD>
    </TR>
    <TR>
        <TD><FONT POINT-SIZE="10">LS<BR/><B>{LS}</B></FONT></TD>
        <TD><FONT POINT-SIZE="10">Margen<BR/><B>{holgura}</B></FONT></TD>
        <TD><FONT POINT-SIZE="10">LF<BR/><B>{LF}</B></FONT></TD>
    </TR>
</TABLE>
>"""

    return label


# Crear nodos
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]

    if col_nombre is not None:
        nombre = tabla.loc[i, col_nombre]
    else:
        nombre = ""

    duracion = tabla.loc[i, "te"]
    ES = tabla.loc[i, "ES"]
    EF = tabla.loc[i, "EF"]
    LS = tabla.loc[i, "LS"]
    LF = tabla.loc[i, "LF"]
    holgura = tabla.loc[i, "Holgura"]

    critica = act in camino_critico

    label = crear_label_aon(
        act=act,
        nombre=nombre,
        duracion=duracion,
        ES=ES,
        EF=EF,
        LS=LS,
        LF=LF,
        holgura=holgura,
        critica=critica
    )

    grafo.node(act, label=label)


# Crear flechas
for i in range(len(tabla)):
    act = tabla.loc[i, "ID"]
    predec = tabla.loc[i, "Pred"]

    for pred in predec:
        if pred in camino_critico and act in camino_critico:
            grafo.edge(pred, act, color="red", penwidth="2.5")
        else:
            grafo.edge(pred, act, color="black")


grafo.render("diagrama_AoN_critico", view=True)
print("\nDiagrama AoN con nodos detallados generado")
