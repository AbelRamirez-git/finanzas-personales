import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database.db as db
from core.comandos import procesar_comando
from core.consultas import ahorro_actual, gastos_totales, ingresos_totales, saldo_disponible


class FinanzasTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "test.db"
        self.patch_db = patch.object(db, "DB_PATH", self.db_path)
        self.patch_db.start()
        self.patch_export = patch.object(db, "_exportar_excel_seguro", return_value=None)
        self.patch_export.start()
        db.crear_base_datos()

    def tearDown(self):
        self.patch_export.stop()
        self.patch_db.stop()
        self.tempdir.cleanup()

    def test_registro_ingreso_y_gasto(self):
        db.registrar_movimiento("ingreso", "salario", "salario", 1_500_000)
        db.registrar_movimiento("gasto", "comida", "almuerzo", 25_000)
        self.assertEqual(ingresos_totales(), 1_500_000)
        self.assertEqual(gastos_totales(), 25_000)
        self.assertEqual(saldo_disponible(), 1_475_000)

    def test_ahorro_es_independiente_del_saldo(self):
        db.registrar_movimiento("ingreso", "salario", "salario", 1_000_000)
        db.agregar_ahorro(300_000)
        self.assertEqual(ahorro_actual(), 300_000)
        self.assertEqual(saldo_disponible(), 1_000_000)

    def test_establecer_y_retirar_ahorro(self):
        db.establecer_ahorro(500_000)
        db.retirar_ahorro(125_000)
        self.assertEqual(ahorro_actual(), 375_000)

    def test_no_permite_retirar_mas_del_ahorro(self):
        db.establecer_ahorro(50_000)
        with self.assertRaises(ValueError):
            db.retirar_ahorro(60_000)

    def test_validacion_movimiento(self):
        with self.assertRaises(ValueError):
            db.registrar_movimiento("otro", "x", "x", 100)
        with self.assertRaises(ValueError):
            db.registrar_movimiento("gasto", "x", "x", 0)
        with self.assertRaises(ValueError):
            db.registrar_movimiento("gasto", "x", "x", -5)

    def test_actualizacion_aplica_validaciones(self):
        movimiento_id = db.registrar_movimiento("gasto", "comida", "almuerzo", 10_000)
        with self.assertRaises(ValueError):
            db.actualizar_movimiento(movimiento_id, "gasto", "comida", "almuerzo", -1)
        with self.assertRaises(ValueError):
            db.actualizar_movimiento(movimiento_id, "ahorro", "x", "x", 1)

    def test_comandos_de_ahorro(self):
        self.assertIn("300.000", procesar_comando("ahorrar 300000"))
        self.assertIn("500.000", procesar_comando("establecer ahorro 500000"))
        self.assertIn("450.000", procesar_comando("retirar ahorro 50000"))


if __name__ == "__main__":
    unittest.main()
