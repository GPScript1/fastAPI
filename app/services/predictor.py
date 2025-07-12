# Selección de columnas candidatas
features = [
    "Dias_InicioCom_FinCom",
    "Dias_FinCom_InicioFactura",
    "Dias_InicioFactura_FinPagado", # Variable Y para entrenamiento
    "Dias_InicioCom_FinPagado", # Variable Y alternativa
    
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
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import os

def entrenar_modelo(data):
    # Selección de columnas candidatas
    features = [
        "Dias_InicioCom_FinCom",
        "Dias_FinCom_InicioFactura",
        "Dias_InicioFactura_FinPagado", # Variable Y para entrenamiento
        "Dias_InicioCom_FinPagado", # Variable Y alternativa
        
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
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    from sklearn.preprocessing import LabelEncoder
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score

    # === CARGA DE DATOS DESDE JSON ===
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

    # === SUGERENCIA AUTOMÁTICA DE TOP FEATURES PARA ENTRENAR ===
    correlacion_con_y = df_corr["Dias_InicioCom_FinPagado"].abs().sort_values(ascending=False)
    mejores_features = correlacion_con_y.drop("Dias_InicioCom_FinPagado").head(8).index.tolist()

    # === VARIABLES X PARA ENTRENAMIENTO (incluye Dias_InicioFactura_FinPagado SOLO para entrenamiento)
    features_entrenamiento = [
        "Dias_InicioCom_FinCom",
        "Dias_InicioFactura_FinPagado",  # solo en entrenamiento
        "Cliente_Prom_InicioCom_FinCom",
        "Cliente_Prom_InicioFactura_FinPagado",
        "Cliente_Prom_InicioCom_FinPagado",
        "Cliente_ValorTotalComercializaciones"
    ]

    # === VARIABLE Y A PREDECIR
    target_variable = "Dias_InicioCom_FinPagado"

    # === FILTRAR DATOS COMPLETOS PARA ENTRENAMIENTO
    df_train = df[features_entrenamiento + [target_variable]].dropna()

    # === DEFINIR X E Y
    X = df_train[features_entrenamiento]
    y = df_train[target_variable]

    # === DIVIDIR EN TRAIN Y TEST
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # === ENTRENAMIENTO DEL MODELO
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)


    from sklearn.model_selection import cross_val_score, KFold

    # === CONFIGURAR VALIDACIÓN CRUZADA ===
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    # === EJECUTAR VALIDACIÓN CRUZADA CON R² Y MAE ===
    scores_r2 = cross_val_score(modelo, X, y, cv=cv, scoring='r2')
    scores_mae = -cross_val_score(modelo, X, y, cv=cv, scoring='neg_mean_absolute_error')  # MAE da valores negativos

    # === EVALUACIÓN DEL MODELO
    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # === CÁLCULO DE MÉTRICAS COMPLETAS =========================================================
    # Residuos (diferencias entre valores reales y predichos)
    residuos = y_test - y_pred

    # Métricas básicas
    standard_error = np.std(residuos, ddof=1)
    rmse = np.sqrt(np.mean(residuos**2))
    mse = np.mean(residuos**2)

    # R² ajustado
    n_samples = len(y_test)
    n_features = X_test.shape[1]
    r2_adjusted = 1 - (1 - r2) * (n_samples - 1) / (n_samples - n_features - 1)

    # Métricas adicionales
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    median_ae = np.median(np.abs(residuos))
    cv_error = (standard_error / np.mean(y_test)) * 100

    # Diagnóstico de overfitting
    y_train_pred = modelo.predict(X_train)
    r2_train = r2_score(y_train, y_train_pred)
    mae_train = mean_absolute_error(y_train, y_train_pred)
    r2_diff = r2_train - r2
    mae_diff = mae - mae_train

    # Distribución de errores
    percentil_95 = np.percentile(np.abs(residuos), 95)

    # Feature importance
    feature_importance = modelo.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': features_entrenamiento,
        'Importance': feature_importance
    }).sort_values('Importance', ascending=False)

    import joblib
    ruta_directorio = "./app/models"
    os.makedirs(ruta_directorio, exist_ok=True)
    ruta_modelo = os.path.join(ruta_directorio, "modelo_randomforest_pago.pkl")
    resultado = joblib.dump(modelo, ruta_modelo)
    print(f"Modelo guardado en: {resultado}")
    return { "mensaje": "Modelo entrenado y guardado exitosamente."}