import matplotlib.pyplot as plt

from core.consultas import (
    ahorro_actual,
    gastos_por_categoria,
    gastos_por_mes,
    gastos_totales,
    ingresos_totales,
)


def grafico_gastos_categoria():
    datos = gastos_por_categoria()
    if not datos:
        print("No hay gastos registrados")
        return
    categorias = [fila[0] for fila in datos]
    valores = [fila[1] for fila in datos]
    plt.figure(figsize=(8, 6))
    plt.pie(valores, labels=categorias, autopct="%1.1f%%")
    plt.title("Gastos por categoría")
    plt.tight_layout()
    plt.show()


def grafico_ingresos_vs_gastos():
    plt.figure(figsize=(7, 5))
    plt.bar(
        ["Ingresos", "Gastos", "Ahorro actual"],
        [ingresos_totales(), gastos_totales(), ahorro_actual()],
    )
    plt.title("Resumen financiero")
    plt.tight_layout()
    plt.show()


def grafico_gastos_por_mes():
    datos = gastos_por_mes()
    if not datos:
        print("No hay gastos por mes registrados")
        return
    plt.figure(figsize=(8, 5))
    plt.plot([x[0] for x in datos], [x[1] for x in datos], marker="o")
    plt.title("Gastos por mes")
    plt.xlabel("Mes")
    plt.ylabel("Valor")
    plt.tight_layout()
    plt.show()
