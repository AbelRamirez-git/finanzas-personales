from pathlib import Path

import pandas as pd

from database.db import conectar

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = PROJECT_ROOT / "excel" / "finanzas.xlsx"


def exportar_excel():
    EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with conectar() as conexion:
        movimientos = pd.read_sql_query(
            "SELECT id, fecha, tipo, categoria, descripcion, valor FROM movimientos ORDER BY id",
            conexion,
        )
        ahorro = pd.read_sql_query(
            "SELECT fecha, tipo, valor, ahorro_resultante, descripcion FROM ahorro_historial ORDER BY id",
            conexion,
        )

    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        movimientos.to_excel(writer, sheet_name="Movimientos", index=False)
        ahorro.to_excel(writer, sheet_name="Historial ahorro", index=False)
    return EXCEL_PATH


if __name__ == "__main__":
    print(f"Excel actualizado: {exportar_excel()}")
