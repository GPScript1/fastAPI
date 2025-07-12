import pandas as pd
from sklearn.cluster import KMeans

def cluster_classify(data):
    if hasattr(data[0], "dict"):
        df = pd.DataFrame([item.dict() for item in data])
    else:
        df = pd.DataFrame(data)

    X = df[[
        "promedioInicioFacturaFinPagado",
        "promedioInicioComFinPagado"
    ]]

    kmeans = KMeans(n_clusters=4, random_state=42)
    df['Cluster'] = kmeans.fit_predict(X)

    cluster_stats = df[df["Cluster"] != -1].groupby("Cluster").agg({
        "promedioInicioFacturaFinPagado": "mean"
    }).rename(columns={"promedioInicioFacturaFinPagado": "PromedioDiasFacturaPago"})

    def asignar_categoria(dias):
        if dias <= 30:
            return "Riesgo Bajo"
        elif dias <= 60:
            return "Riesgo Medio"
        elif dias <= 90:
            return "Riesgo Alto"
        else:
            return "Riesgo Crítico"

    cluster_stats["CategoriaRiesgo"] = cluster_stats["PromedioDiasFacturaPago"].apply(asignar_categoria)

    df = df.merge(cluster_stats["CategoriaRiesgo"], how="left", left_on="Cluster", right_index=True)

    return df.to_dict(orient="records")