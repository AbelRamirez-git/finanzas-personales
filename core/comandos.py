import re
import unicodedata

from core.consultas import (
    ahorro_actual,
    gastos_totales,
    ingresos_totales,
    mayor_gasto,
    saldo_disponible,
)
from database.db import agregar_ahorro, establecer_ahorro, registrar_movimiento, retirar_ahorro


def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto or ""))
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.lower().strip()


def formato_pesos(valor):
    return f"{int(valor):,}".replace(",", ".")


def limpiar_categoria(texto):
    texto = texto.strip()
    if texto.startswith("en "):
        texto = texto[3:].strip()
    return texto or "general"


def _registrar(tipo, coincidencia):
    valor = int(coincidencia.group(2))
    categoria = limpiar_categoria(coincidencia.group(3))
    registrar_movimiento(tipo, categoria, categoria, valor)
    etiqueta = "Ingreso" if tipo == "ingreso" else "Gasto"
    return f"{etiqueta} registrado correctamente\n${formato_pesos(valor)} en {categoria}"


def procesar_comando(texto):
    texto_n = normalizar(texto)
    if not texto_n:
        return "Escribe un comando. Usa 'ayuda' para ver las opciones."

    patrones = {
        "gasto": r"^(gasto|gastos|gaste|pague)\s+(\d+)\s*(.*)$",
        "ingreso": r"^(ingreso|ingresos|recibi|gane)\s+(\d+)\s*(.*)$",
        "ahorro_aporte": r"^(ahorrar|ahorre|aporte ahorro)\s+(\d+)\s*(.*)$",
        "ahorro_establecer": r"^(establecer ahorro|ahorro establecer|fijar ahorro)\s+(\d+)\s*(.*)$",
        "ahorro_retiro": r"^(retirar ahorro|retiro ahorro)\s+(\d+)\s*(.*)$",
    }

    try:
        for nombre, patron in patrones.items():
            coincidencia = re.match(patron, texto_n)
            if not coincidencia:
                continue

            if nombre == "gasto":
                return _registrar("gasto", coincidencia)
            if nombre == "ingreso":
                return _registrar("ingreso", coincidencia)

            valor = int(coincidencia.group(2))
            descripcion = limpiar_categoria(coincidencia.group(3))
            if nombre == "ahorro_aporte":
                nuevo = agregar_ahorro(valor, descripcion)
                return f"Ahorro actualizado\nNuevo ahorro actual: ${formato_pesos(nuevo)}"
            if nombre == "ahorro_establecer":
                nuevo = establecer_ahorro(valor, descripcion)
                return f"Ahorro establecido\nAhorro actual: ${formato_pesos(nuevo)}"
            if nombre == "ahorro_retiro":
                nuevo = retirar_ahorro(valor, descripcion)
                return f"Retiro de ahorro registrado\nAhorro actual: ${formato_pesos(nuevo)}"

        if texto_n in ("saldo", "balance", "disponible"):
            return f"Saldo disponible actual:\n${formato_pesos(saldo_disponible())}"

        if texto_n in ("resumen", "estado", "finanzas"):
            return (
                "RESUMEN FINANCIERO\n\n"
                f"Ingresos: ${formato_pesos(ingresos_totales())}\n"
                f"Gastos: ${formato_pesos(gastos_totales())}\n"
                f"Ahorro actual: ${formato_pesos(ahorro_actual())}\n"
                f"Saldo disponible: ${formato_pesos(saldo_disponible())}"
            )

        if texto_n in ("ingresos", "mis ingresos"):
            return f"Ingresos totales: ${formato_pesos(ingresos_totales())}"
        if texto_n in ("gastos", "mis gastos"):
            return f"Gastos totales: ${formato_pesos(gastos_totales())}"
        if texto_n in ("ahorro", "mis ahorros", "ahorro actual"):
            return f"Ahorro actual: ${formato_pesos(ahorro_actual())}"
        if texto_n == "mayor gasto":
            categoria, valor = mayor_gasto()
            return f"Tu mayor gasto fue ${formato_pesos(valor)} en {categoria}"

        if texto_n == "ayuda":
            return (
                "COMANDOS DISPONIBLES\n\n"
                "INGRESOS\n- ingreso 1500000 salario\n\n"
                "GASTOS\n- gasto 25000 comida\n- gaste 10000 transporte\n\n"
                "AHORRO MANUAL\n- ahorrar 300000\n- establecer ahorro 500000\n- retirar ahorro 50000\n\n"
                "CONSULTAS\n- saldo\n- resumen\n- ingresos\n- gastos\n- ahorro actual\n- mayor gasto"
            )

        return "No entendí el comando. Escribe 'ayuda' para ver las opciones."
    except ValueError as exc:
        return f"Error: {exc}"
    except Exception:
        return "Ocurrió un error inesperado al procesar el comando."
