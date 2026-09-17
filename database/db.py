import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "finanzas.db"

TIPOS_VALIDOS = {"ingreso", "gasto"}


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def conectar():
    conexion = sqlite3.connect(DB_PATH, factory=ClosingConnection)
    conexion.row_factory = sqlite3.Row
    return conexion


def _normalizar_texto(valor, predeterminado=""):
    texto = str(valor or "").strip().lower()
    return texto or predeterminado


def _validar_valor(valor):
    if isinstance(valor, bool):
        raise ValueError("El valor debe ser un número entero.")
    try:
        numero = int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError("El valor debe ser un número entero.") from exc
    if numero <= 0:
        raise ValueError("El valor debe ser mayor que cero.")
    return numero


def crear_base_datos():
    with conectar() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'gasto')),
                categoria TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                valor INTEGER NOT NULL CHECK(valor > 0)
            )
        """)
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor INTEGER NOT NULL CHECK(valor >= 0)
            )
        """)
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS ahorro_historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('aporte', 'retiro', 'ajuste')),
                valor INTEGER NOT NULL CHECK(valor >= 0),
                ahorro_resultante INTEGER NOT NULL CHECK(ahorro_resultante >= 0),
                descripcion TEXT NOT NULL
            )
        """)
        conexion.execute(
            "INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('ahorro_actual', 0)"
        )

        migrada = conexion.execute(
            "SELECT valor FROM configuracion WHERE clave = 'migracion_ahorro_v2'"
        ).fetchone()
        if not migrada:
            columnas = [fila[1] for fila in conexion.execute("PRAGMA table_info(movimientos)").fetchall()]
            if "tipo" in columnas:
                legado = conexion.execute(
                    "SELECT COALESCE(SUM(valor), 0) FROM movimientos WHERE LOWER(tipo) = 'ahorro'"
                ).fetchone()[0]
                ahorro_config = conexion.execute(
                    "SELECT valor FROM configuracion WHERE clave = 'ahorro_actual'"
                ).fetchone()[0]
                if legado and ahorro_config == 0:
                    conexion.execute(
                        "UPDATE configuracion SET valor = ? WHERE clave = 'ahorro_actual'",
                        (int(legado),),
                    )
                conexion.execute("DELETE FROM movimientos WHERE LOWER(tipo) = 'ahorro'")
            conexion.execute(
                "INSERT OR REPLACE INTO configuracion (clave, valor) VALUES ('migracion_ahorro_v2', 1)"
            )
        conexion.commit()


def registrar_movimiento(tipo, categoria, descripcion, valor):
    crear_base_datos()
    tipo = _normalizar_texto(tipo)
    if tipo not in TIPOS_VALIDOS:
        raise ValueError("Tipo inválido. Debe ser ingreso o gasto.")

    categoria = _normalizar_texto(categoria, "general")
    descripcion = _normalizar_texto(descripcion, categoria)
    valor = _validar_valor(valor)
    fecha = datetime.now().strftime("%Y-%m-%d")

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO movimientos (fecha, tipo, categoria, descripcion, valor)
            VALUES (?, ?, ?, ?, ?)
            """,
            (fecha, tipo, categoria, descripcion, valor),
        )
        conexion.commit()
        movimiento_id = cursor.lastrowid

    _exportar_excel_seguro()
    return movimiento_id


def actualizar_movimiento(movimiento_id, tipo, categoria, descripcion, valor):
    crear_base_datos()
    try:
        movimiento_id = int(movimiento_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("El ID del movimiento debe ser numérico.") from exc
    if movimiento_id <= 0:
        raise ValueError("El ID del movimiento debe ser mayor que cero.")

    tipo = _normalizar_texto(tipo)
    if tipo not in TIPOS_VALIDOS:
        raise ValueError("Tipo inválido. Debe ser ingreso o gasto.")
    categoria = _normalizar_texto(categoria, "general")
    descripcion = _normalizar_texto(descripcion, categoria)
    valor = _validar_valor(valor)

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            UPDATE movimientos
            SET tipo = ?, categoria = ?, descripcion = ?, valor = ?
            WHERE id = ?
            """,
            (tipo, categoria, descripcion, valor, movimiento_id),
        )
        conexion.commit()
        if cursor.rowcount == 0:
            raise ValueError("No existe un movimiento con ese ID.")

    _exportar_excel_seguro()
    return True


def eliminar_movimiento(movimiento_id):
    crear_base_datos()
    try:
        movimiento_id = int(movimiento_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("El ID del movimiento debe ser numérico.") from exc

    with conectar() as conexion:
        cursor = conexion.execute("DELETE FROM movimientos WHERE id = ?", (movimiento_id,))
        conexion.commit()
        if cursor.rowcount == 0:
            raise ValueError("No existe un movimiento con ese ID.")

    _exportar_excel_seguro()
    return True


def obtener_ahorro_actual():
    crear_base_datos()
    with conectar() as conexion:
        fila = conexion.execute(
            "SELECT valor FROM configuracion WHERE clave = 'ahorro_actual'"
        ).fetchone()
    return int(fila["valor"]) if fila else 0


def establecer_ahorro(valor, descripcion="ajuste manual"):
    crear_base_datos()
    try:
        valor = int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError("El ahorro debe ser un número entero.") from exc
    if valor < 0:
        raise ValueError("El ahorro no puede ser negativo.")

    anterior = obtener_ahorro_actual()
    fecha = datetime.now().strftime("%Y-%m-%d")
    descripcion = _normalizar_texto(descripcion, "ajuste manual")

    with conectar() as conexion:
        conexion.execute(
            "UPDATE configuracion SET valor = ? WHERE clave = 'ahorro_actual'",
            (valor,),
        )
        conexion.execute(
            """
            INSERT INTO ahorro_historial (fecha, tipo, valor, ahorro_resultante, descripcion)
            VALUES (?, 'ajuste', ?, ?, ?)
            """,
            (fecha, abs(valor - anterior), valor, descripcion),
        )
        conexion.commit()
    return valor


def agregar_ahorro(valor, descripcion="aporte manual"):
    valor = _validar_valor(valor)
    actual = obtener_ahorro_actual()
    nuevo = actual + valor
    fecha = datetime.now().strftime("%Y-%m-%d")
    descripcion = _normalizar_texto(descripcion, "aporte manual")

    with conectar() as conexion:
        conexion.execute(
            "UPDATE configuracion SET valor = ? WHERE clave = 'ahorro_actual'",
            (nuevo,),
        )
        conexion.execute(
            """
            INSERT INTO ahorro_historial (fecha, tipo, valor, ahorro_resultante, descripcion)
            VALUES (?, 'aporte', ?, ?, ?)
            """,
            (fecha, valor, nuevo, descripcion),
        )
        conexion.commit()
    return nuevo


def retirar_ahorro(valor, descripcion="retiro manual"):
    valor = _validar_valor(valor)
    actual = obtener_ahorro_actual()
    if valor > actual:
        raise ValueError("El retiro no puede ser mayor que el ahorro actual.")
    nuevo = actual - valor
    fecha = datetime.now().strftime("%Y-%m-%d")
    descripcion = _normalizar_texto(descripcion, "retiro manual")

    with conectar() as conexion:
        conexion.execute(
            "UPDATE configuracion SET valor = ? WHERE clave = 'ahorro_actual'",
            (nuevo,),
        )
        conexion.execute(
            """
            INSERT INTO ahorro_historial (fecha, tipo, valor, ahorro_resultante, descripcion)
            VALUES (?, 'retiro', ?, ?, ?)
            """,
            (fecha, valor, nuevo, descripcion),
        )
        conexion.commit()
    return nuevo


def _exportar_excel_seguro():
    try:
        from excel.exportar_excel import exportar_excel
        exportar_excel()
    except Exception as exc:
        print(f"Advertencia: no se pudo actualizar el Excel: {exc}")


if __name__ == "__main__":
    crear_base_datos()
    print(f"Base de datos lista en: {DB_PATH}")
