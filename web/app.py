from pathlib import Path
import sys

from flask import Flask, jsonify, render_template, request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.comandos import procesar_comando
from core.consultas import (
    ahorro_actual,
    ahorro_por_mes,
    gastos_por_categoria,
    gastos_por_mes,
    gastos_totales,
    ingresos_totales,
    obtener_movimientos,
    saldo_disponible,
)
from database.db import crear_base_datos

app = Flask(__name__)


def formato_cop(valor):
    return f"{int(valor):,}".replace(",", ".")


app.jinja_env.filters["cop"] = formato_cop


@app.route("/")
def inicio():
    categorias = gastos_por_categoria()
    gastos_mes = gastos_por_mes()
    ahorro_mes = ahorro_por_mes()

    return render_template(
        "index.html",
        movimientos=obtener_movimientos(),
        ingresos=ingresos_totales(),
        gastos=gastos_totales(),
        ahorro_actual=ahorro_actual(),
        saldo=saldo_disponible(),
        labels=[c[0] for c in categorias],
        valores=[c[1] for c in categorias],
        labels_mes=[m[0] for m in gastos_mes],
        valores_mes=[m[1] for m in gastos_mes],
        labels_ahorro=[a[0] for a in ahorro_mes],
        valores_ahorro=[a[1] for a in ahorro_mes],
    )


@app.route("/comando", methods=["POST"])
def comando():
    datos = request.get_json(silent=True) or {}
    texto = str(datos.get("texto", "")).strip()
    if not texto:
        return jsonify({"respuesta": "Escribe un comando antes de enviarlo."}), 400
    return jsonify({"respuesta": procesar_comando(texto)})


if __name__ == "__main__":
    crear_base_datos()
    app.run(host="127.0.0.1", port=5000, debug=True)
