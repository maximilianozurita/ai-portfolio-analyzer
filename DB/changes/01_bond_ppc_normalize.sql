-- Migración: normalizar ppc de bond_holding dividiendo por 100
-- Ejecutar UNA sola vez sobre la BD existente.
-- Antes: ppc se guardaba como precio bruto (ej. 85.50)
-- Después: ppc se guarda dividido por 100 (ej. 0.855)
-- El display en el frontend ya NO divide por 100, por lo que el valor
-- mostrado (ppc * quantity) sigue siendo correcto.

UPDATE bond_holding SET ppc = ROUND(ppc / 100, 6);
