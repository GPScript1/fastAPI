import pandas as pd
import json
from datetime import datetime

def generar_features(data):
    with open(data, 'r', encoding='utf-8') as f:
        dataCSV = json.load(f)

    IGNORE_PREFIXES = ('ADI', 'OTR', 'SPD')
    VALID_ESTADOS_COM = {0, 1, 3}
    INVALID_FACTURA_ESTADOS = {5, 6, 7}

    def parse_fecha(fecha_str):
        return datetime.strptime(fecha_str, "%d/%m/%Y")

    registros = []

    for c in dataCSV:
        if any(c.get("CodigoCotizacion", "").startswith(pref) for pref in IGNORE_PREFIXES):
            continue
        if not any(e.get("EstadoComercializacion") == 1 for e in c.get("Estados", [])):
            continue
        if any(e.get("EstadoComercializacion") not in VALID_ESTADOS_COM for e in c.get("Estados", [])):
            continue
        if any(e.get("estado") in INVALID_FACTURA_ESTADOS for f in c.get("Facturas", []) for e in f.get("EstadosFactura", [])):
            continue
        if not any(c.get("Facturas", [])):
            continue
        
        id_com = c.get("idComercializacion")
        codigo_cot = c.get("CodigoCotizacion")
        estados_helper = sorted(c.get("Estados", []), key=lambda e: parse_fecha(e.get("Fecha")))
        if (parse_fecha(c.get("FechaInicio")) < parse_fecha(estados_helper[0].get("Fecha"))):
            fecha_inicio = parse_fecha(c.get("FechaInicio"))
        else:
            fecha_inicio = parse_fecha(estados_helper[0].get("Fecha"))
        nombre_cliente = c.get("NombreCliente", "")
        lider_comercial = c.get("CorreoCreador", "")
        valor_final = c.get("ValorFinalComercializacion", 0)
        estado_inicial = estados_helper[0].get("EstadoComercializacion", 0)
        fecha_estado_inicial = parse_fecha(estados_helper[0].get("Fecha", ""))
        estado_final = estados_helper[-1].get("EstadoComercializacion", 0)
        fecha_estado_final = parse_fecha(estados_helper[-1].get("Fecha", ""))
        
        estado_facturas_helper = []
        for factura in c.get("Facturas", []):
            if any(est.get("estado") in INVALID_FACTURA_ESTADOS for est in factura.get("EstadosFactura", [])):
                continue
            estado_facturas_helper.append(parse_fecha(factura.get("FechaFacturacion", "")))
            for est in factura.get("EstadosFactura", []):
                estado_facturas_helper.append(parse_fecha(est.get("Fecha", "")))
        estado_facturas_helper = sorted(estado_facturas_helper, key=lambda x: x if isinstance(x, datetime) else datetime.strptime(x, "%d/%m/%Y"))
        fecha_factura_inicial = estado_facturas_helper[0] if estado_facturas_helper else None
        fecha_factura_final = estado_facturas_helper[-1] if estado_facturas_helper else None

        monto_acumulado_facturas = 0
        for factura in c.get("Facturas", []):
            if any(est.get("estado") in INVALID_FACTURA_ESTADOS for est in factura.get("EstadosFactura", [])):
                continue
            for est in factura.get("EstadosFactura", []):
                monto_acumulado_facturas += est.get("Pagado")

        registros.append({
            "IdComercializacion": id_com,
            "CodigoCotizacion": codigo_cot,
            "NombreCliente": nombre_cliente,
            "LiderComercial": lider_comercial,
            "ValorFinal": valor_final,
            "MontoFacturas": monto_acumulado_facturas,
            "EstadoInicial": estado_inicial,
            "FechaEstadoInicial": fecha_estado_inicial,
            "EstadoFinal": estado_final,
            "FechaEstadoFinal": fecha_estado_final,
            "FechaFacturaInicial": fecha_factura_inicial,
            "FechaFacturaFinal": fecha_factura_final
        })

    df_resultado = pd.DataFrame(registros)
    df_resultado.to_csv(f'../data/comercializaciones_data.csv', index=False)
