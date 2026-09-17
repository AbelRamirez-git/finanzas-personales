# Finanzas Personales

Aplicación local de finanzas personales desarrollada con Python, Flask y SQLite. Permite registrar ingresos y gastos mediante comandos de texto, mantener un ahorro manual independiente, visualizar indicadores y exportar datos a Excel.

## Funciones

- Registro de ingresos y gastos.
- Saldo disponible = ingresos - gastos.
- Ahorro actual administrado manualmente, sin mezclarlo con los movimientos.
- Aportes, retiros y ajuste directo del ahorro.
- Dashboard responsive con Chart.js.
- Gastos por categoría y por mes.
- Historial de ahorro.
- Exportación automática a Excel.
- Validaciones de datos y mensajes de error controlados.

## Comandos

```text
ingreso 1500000 salario
gasto 25000 comida
ahorrar 300000
establecer ahorro 500000
retirar ahorro 50000
saldo
resumen
ahorro actual
mayor gasto
ayuda
```

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m database.db
python web/app.py
```

Luego abre `http://127.0.0.1:5000`.

En Windows también puedes ejecutar `iniciar_finanzas.bat`.

## Privacidad

`finanzas.db` y los Excel generados están excluidos por `.gitignore`, por lo que los datos financieros personales no deben subirse a GitHub.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Estructura principal

```text
core/            lógica de comandos y consultas
database/        persistencia SQLite
excel/           exportación a Excel
visualizacion/   gráficos de escritorio opcionales
web/             aplicación Flask y dashboard
tests/           pruebas automatizadas
```
