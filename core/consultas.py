from database.db import conectar, obtener_ahorro_actual


def obtener_movimientos():
    with conectar() as conexion:
        filas = conexion.execute("""
            SELECT id, fecha, tipo, categoria, descripcion, valor
            FROM movimientos
            ORDER BY id DESC
        """).fetchall()
    return [tuple(fila) for fila in filas]


def _total_por_tipo(tipo):
    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT COALESCE(SUM(valor), 0) AS total FROM movimientos WHERE tipo = ?",
            (tipo,),
        ).fetchone()
    return int(fila["total"])


def ingresos_totales():
    return _total_por_tipo("ingreso")


def gastos_totales():
    return _total_por_tipo("gasto")


def ahorro_actual():
    return obtener_ahorro_actual()


def ahorro_totales():
    """Alias conservado para compatibilidad con código anterior."""
    return ahorro_actual()


def saldo_disponible():
    return ingresos_totales() - gastos_totales()


def mayor_gasto():
    with conectar() as conexion:
        fila = conexion.execute("""
            SELECT categoria, valor
            FROM movimientos
            WHERE tipo = 'gasto'
            ORDER BY valor DESC, id DESC
            LIMIT 1
        """).fetchone()
    return (fila["categoria"], int(fila["valor"])) if fila else ("Sin datos", 0)


def gastos_por_categoria():
    with conectar() as conexion:
        filas = conexion.execute("""
            SELECT categoria, SUM(valor) AS total
            FROM movimientos
            WHERE tipo = 'gasto'
            GROUP BY categoria
            ORDER BY total DESC
        """).fetchall()
    return [(fila["categoria"], int(fila["total"])) for fila in filas]


def gastos_por_mes():
    with conectar() as conexion:
        filas = conexion.execute("""
            SELECT substr(fecha, 1, 7) AS mes, SUM(valor) AS total
            FROM movimientos
            WHERE tipo = 'gasto'
            GROUP BY mes
            ORDER BY mes
        """).fetchall()
    return [(fila["mes"], int(fila["total"])) for fila in filas]


def ahorro_por_mes():
    with conectar() as conexion:
        filas = conexion.execute("""
            SELECT substr(fecha, 1, 7) AS mes,
                   SUM(CASE WHEN tipo = 'aporte' THEN valor
                            WHEN tipo = 'retiro' THEN -valor
                            ELSE 0 END) AS variacion
            FROM ahorro_historial
            GROUP BY mes
            ORDER BY mes
        """).fetchall()
    return [(fila["mes"], int(fila["variacion"] or 0)) for fila in filas]


def movimiento_por_id(movimiento_id):
    with conectar() as conexion:
        fila = conexion.execute("""
            SELECT id, fecha, tipo, categoria, descripcion, valor
            FROM movimientos
            WHERE id = ?
        """, (movimiento_id,)).fetchone()
    return tuple(fila) if fila else None
