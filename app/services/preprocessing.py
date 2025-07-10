def generar_features(data):
    # Extrae características como días entre estados, cliente codificado, etc.
    # Aquí puedes aplicar cualquier transformación basada en tu análisis previo
    estado_fechas = sorted(data.estados, key=lambda e: e.fecha)
    dias_estado = (estado_fechas[-1].fecha - data.fecha_inicio).days
    return [dias_estado, data.valor_total]
