-- =========================================================
-- migraciones/002_extension_app.sql
-- ---------------------------------------------------------
-- Amplía el esquema de mr_burguer_db (creado por el script SQL
-- original) con las columnas que necesita el programa de
-- escritorio Mr.Burger:
--
--   productos.emoji         -> icono que se muestra en cada
--                              tarjeta de producto del menú
--   pedidos.tipo_pedido     -> "mesa" o "llevar"
--   pedidos.numero_mesa     -> número de mesa (NULL si es "llevar")
--   pedidos.notas           -> notas del cajero para el pedido
--
-- Ejecútalo UNA sola vez, después de haber creado la base de
-- datos con el script original (mr_burguer_db.sql):
--
--   mysql -u root -p mr_burguer_db < migraciones/002_extension_app.sql
--
-- Es seguro volver a ejecutarlo: cada ALTER está protegido con
-- una comprobación de "si la columna no existe todavía".
-- =========================================================

USE mr_burguer_db;

-- ---------------------------------------------------------
-- productos.emoji
-- ---------------------------------------------------------
SET @columna_existe := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'productos'
       AND COLUMN_NAME = 'emoji'
);

SET @sql := IF(
    @columna_existe = 0,
    'ALTER TABLE productos ADD COLUMN emoji VARCHAR(10) NOT NULL DEFAULT ''🍽'' AFTER descripcion',
    'SELECT ''productos.emoji ya existe, no se modifica.'''
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------
-- pedidos.tipo_pedido / numero_mesa / notas
-- ---------------------------------------------------------
SET @columna_existe := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'pedidos'
       AND COLUMN_NAME = 'tipo_pedido'
);

SET @sql := IF(
    @columna_existe = 0,
    'ALTER TABLE pedidos
        ADD COLUMN tipo_pedido ENUM(''mesa'',''llevar'') NOT NULL DEFAULT ''mesa'' AFTER id_usuario,
        ADD COLUMN numero_mesa INT DEFAULT NULL AFTER tipo_pedido,
        ADD COLUMN notas VARCHAR(255) DEFAULT NULL AFTER numero_mesa',
    'SELECT ''pedidos.tipo_pedido ya existe, no se modifica.'''
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
