# Selección de columnas candidatas
features = [
    "Dias_InicioCom_FinCom",
    "Dias_FinCom_InicioFactura",
    "Dias_InicioFactura_FinPagado", # ← Variable Y para entrenamiento
    "Dias_InicioCom_FinPagado", # ← Variable Y alternativa
    
    "ValorFinalComercializacion",
    "LiderComercial",  # codificado
    "NombreCliente",
    "Cliente_Prom_InicioCom_FinCom",
    "Cliente_Prom_FinCom_InicioFactura",
    "Cliente_Prom_InicioFactura_FinPagado",
    "Cliente_Prom_InicioCom_FinPagado",
    "Cliente_CantComercializaciones",
    "Cliente_ValorTotalComercializaciones"
]

import pandas as pd
import json
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def entrenar_modelo(data):
    clientes_json = [cliente.dict(by_alias=True) for cliente in data.clientePromedio]
    comercial_json = [comercial.dict(by_alias=True) for comercial in data.comercializaciones]

    # === TRANSFORMACIÓN A DATAFRAMES ===
    df_clientes = pd.DataFrame(clientes_json)
    df_comercial = pd.DataFrame(comercial_json)

    # === FILTRAR COMERCIALIZACIONES VÁLIDAS (sin @insecap) ===
    df_clientes = df_clientes[~df_clientes["NombreEnte"].str.contains("@insecap", case=False, na=False)]
    df_comercial = df_comercial[~df_comercial["NombreEnte"].str.contains("@insecap", case=False, na=False)]

    # === RENOMBRAR COLUMNAS ===
    map_clientes = {
        "NombreEnte": "NombreCliente",
        "PromedioInicioComFinCom": "Cliente_Prom_InicioCom_FinCom",
        "PromedioFinComInicioFactura": "Cliente_Prom_FinCom_InicioFactura",
        "PromedioInicioFacturaFinPagado": "Cliente_Prom_InicioFactura_FinPagado",
        "PromedioInicioComFinPagado": "Cliente_Prom_InicioCom_FinPagado",
        "CantidadComercializaciones": "Cliente_CantComercializaciones",
        "ValorTotalComercializaciones": "Cliente_ValorTotalComercializaciones"
    }
    map_comercial = {
        "NombreEnte": "NombreCliente",
        "DiasInicioComFinCom": "Dias_InicioCom_FinCom",
        "DiasFinComInicioFactura": "Dias_FinCom_InicioFactura",
        "DiasInicioFacturaFinPagado": "Dias_InicioFactura_FinPagado",  # Y alternativa
        "DiasInicioComFinPagado": "Dias_InicioCom_FinPagado",          # Y principal
        "ValorComercializacion": "ValorFinalComercializacion"
    }
    df_clientes.rename(columns=map_clientes, inplace=True)
    df_comercial.rename(columns=map_comercial, inplace=True)

    # === MERGE CLIENTE + COMERCIALIZACIÓN ===
    df = pd.merge(df_comercial, df_clientes, on="NombreCliente", how="left")

    # === CODIFICAR VARIABLES CATEGÓRICAS ===
    df["LiderComercial"] = LabelEncoder().fit_transform(df.get("LiderComercial", pd.Series(["sin_data"] * len(df))))
    df["NombreCliente"] = LabelEncoder().fit_transform(df["NombreCliente"])

    # === INFO BÁSICA Y ESTADÍSTICAS (sin prints para API) ===

    # === FILTRAR FEATURES NUMÉRICAS PARA CORRELACIÓN ===
    features_numericas = [
        "Dias_InicioCom_FinCom",
        "Dias_FinCom_InicioFactura",
        "Dias_InicioFactura_FinPagado",      # opcional como Y
        "Dias_InicioCom_FinPagado",          # Y principal
        "ValorFinalComercializacion",
        "LiderComercial",
        "NombreCliente",
        "Cliente_Prom_InicioCom_FinCom",
        "Cliente_Prom_FinCom_InicioFactura",
        "Cliente_Prom_InicioFactura_FinPagado",
        "Cliente_Prom_InicioCom_FinPagado",
        "Cliente_CantComercializaciones",
        "Cliente_ValorTotalComercializaciones"
    ]

    df_corr = df[features_numericas].dropna().corr()

    # === MATRIZ DE CORRELACIÓN COMPLETA (sin visualización para API) ===
    df_corr = df[features_numericas].dropna().corr()

    # === CORRELACIÓN INDIVIDUAL CONTRA Y ===

    # === SUGERENCIA AUTOMÁTICA DE TOP FEATURES PARA ENTRENAR ===
    correlacion_con_y = df_corr["Dias_InicioCom_FinPagado"].abs().sort_values(ascending=False)
    mejores_features = correlacion_con_y.drop("Dias_InicioCom_FinPagado").head(8).index.tolist()

    # === VARIABLES PARA PREDICCIÓN REAL (solo variables disponibles al inicio del proceso)
    features_prediccion_real = [
        "Dias_InicioCom_FinCom",
        "Cliente_Prom_InicioCom_FinCom",
        "Cliente_Prom_InicioFactura_FinPagado",
        "Cliente_Prom_InicioCom_FinPagado",
        "Cliente_ValorTotalComercializaciones"
    ]

    # === VARIABLE Y A PREDECIR
    target_variable = "Dias_InicioCom_FinPagado"

    # === FILTRAR DATOS COMPLETOS PARA ENTRENAMIENTO
    df_train = df[features_prediccion_real + [target_variable]].dropna()

    # === DEFINIR X E Y
    X = df_train[features_prediccion_real]
    y = df_train[target_variable]

    # === DIVIDIR EN TRAIN Y TEST
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # === ENTRENAMIENTO DEL MODELO
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # ====== PREDICCIÓN DEL MODELO SOBRE NUEVOS DATOS ======
    df_pred = df.copy()
    df_pred = df_pred[features_prediccion_real].dropna()

    # Asegurar alineación de índices
    df_pred_clean = df.loc[df_pred.index].copy()

    # Predecir Y para todas las comercializaciones usando el MODELO
    df_pred_clean["Dias_InicioCom_FinPagado_Predicho"] = modelo.predict(df_pred)

    # === OPCIONAL: Comparar con Y real si está disponible
    if "Dias_InicioCom_FinPagado" in df_pred_clean.columns:
        df_pred_clean["Error_Prediccion"] = (
            df_pred_clean["Dias_InicioCom_FinPagado_Predicho"] - df_pred_clean["Dias_InicioCom_FinPagado"]
        ).abs()

    # === Guardar modelo y predicciones
    joblib.dump(modelo, "app/models/modelo_randomforest_pago.pkl")

    # ====== PREDICCIONES DE DÍAS DE DEMORA POR CLIENTE ======================================

    # === CREAR MAPEO DE IDs A NOMBRES REALES ===
    # Crear diccionario para convertir IDs codificados a nombres reales
    nombres_encoder = LabelEncoder()
    nombres_encoder.fit(df_comercial["NombreCliente"])
    id_to_nombre = dict(zip(range(len(nombres_encoder.classes_)), nombres_encoder.classes_))

    # === GENERAR PREDICCIONES PARA CADA CLIENTE ===
    predicciones_cliente = []

    for cliente_id in df['NombreCliente'].unique():
        cliente_data = df[df['NombreCliente'] == cliente_id]
        
        if len(cliente_data) > 0:
            # Obtener el nombre real del cliente
            nombre_real = id_to_nombre.get(cliente_id, f"Cliente_{cliente_id}")
            
            # Obtener características promedio del cliente para predicción
            dias_com_promedio = cliente_data['Dias_InicioCom_FinCom'].mean()
            cliente_prom_pago = cliente_data['Cliente_Prom_InicioCom_FinPagado'].iloc[0]
            cliente_prom_factura = cliente_data['Cliente_Prom_InicioFactura_FinPagado'].iloc[0]
            cliente_prom_com = cliente_data['Cliente_Prom_InicioCom_FinCom'].iloc[0]
            cliente_valor_total = cliente_data['Cliente_ValorTotalComercializaciones'].iloc[0]
            
            # Crear escenario para predicción usando el historial del cliente
            escenario_cliente = pd.DataFrame({
                'Dias_InicioCom_FinCom': [dias_com_promedio],
                'Cliente_Prom_InicioCom_FinCom': [cliente_prom_com],
                'Cliente_Prom_InicioFactura_FinPagado': [cliente_prom_factura],
                'Cliente_Prom_InicioCom_FinPagado': [cliente_prom_pago],
                'Cliente_ValorTotalComercializaciones': [cliente_valor_total]
            })
            
            # Hacer predicción de días de demora
            dias_demora_predichos = modelo.predict(escenario_cliente)[0]
            
            # Estadísticas del cliente
            real_promedio = cliente_data['Dias_InicioCom_FinPagado'].mean()
            
            predicciones_cliente.append({
                'NombreCliente': nombre_real,
                'Dias_Demora_Real_Promedio': round(real_promedio, 1),
                'Dias_Demora_Predicho': round(dias_demora_predichos, 1),
                'Diferencia_Dias': round(abs(dias_demora_predichos - real_promedio), 1)
            })

    # === CONVERTIR A DATAFRAME Y ORDENAR RESULTADOS ===
    return (predicciones_cliente)