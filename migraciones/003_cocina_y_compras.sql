-- =========================================================
-- migraciones/003_cocina_y_compras.sql
-- ---------------------------------------------------------
-- Amplía mr_burguer_db con lo necesario para:
--
--   1) La pantalla de Cocina: un nuevo rol 'cocinero' y un
--      procedimiento para marcar un pedido ya enviado a cocina
--      (estado 'enviado_cocina') como 'entregado'.
--
--   2) El apartado "Comprar Productos" del Panel de
--      Administrador: tablas "compras" / "compra_detalle" para
--      registrar reabastecimientos de inventario a proveedores,
--      y un procedimiento que aumenta el stock real al agregar
--      cada línea de la compra.
--
-- Ejecútalo UNA vez, después del script original y de la
-- migración 002:
--
--   mysql -u root -p mr_burguer_db < migraciones/003_cocina_y_compras.sql
--
-- Es seguro volver a ejecutarlo: el rol se agrega con un ALTER
-- (idempotente) + INSERT condicional, las tablas usan
-- "CREATE TABLE IF NOT EXISTS", y los procedimientos/triggers
-- se recrean con "DROP ... IF EXISTS" antes de crearse.
-- =========================================================

USE mr_burguer_db;

-- ---------------------------------------------------------
-- 1) ROL 'cocinero'
-- ---------------------------------------------------------

ALTER TABLE roles MODIFY COLUMN nombre_rol
    ENUM('administrador','usuario','inhabilitado','cocinero') NOT NULL UNIQUE;

INSERT INTO roles (nombre_rol)
SELECT 'cocinero'
 WHERE NOT EXISTS (SELECT 1 FROM roles WHERE nombre_rol = 'cocinero');

-- ---------------------------------------------------------
-- 2) COMPRAS (reabastecimiento de inventario a proveedores)
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS compras (
    id_compra    INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario   INT NOT NULL,
    fecha_hora   DATETIME DEFAULT CURRENT_TIMESTAMP,
    proveedor    VARCHAR(150) DEFAULT NULL,
    notas        VARCHAR(255) DEFAULT NULL,
    total        DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS compra_detalle (
    id_compra_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_compra         INT NOT NULL,
    id_producto       INT NOT NULL,
    cantidad          INT NOT NULL CHECK (cantidad > 0),
    costo_unitario    DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (costo_unitario >= 0),
    subtotal_linea    DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * costo_unitario) STORED,
    FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- ---------------------------------------------------------
-- PROCEDIMIENTOS Y TRIGGERS
-- ---------------------------------------------------------

DELIMITER $$

DROP TRIGGER IF EXISTS trg_after_insert_compra_detalle$$
CREATE TRIGGER trg_after_insert_compra_detalle
AFTER INSERT ON compra_detalle
FOR EACH ROW
BEGIN
    UPDATE compras
       SET total = (
                SELECT COALESCE(SUM(subtotal_linea), 0)
                  FROM compra_detalle
                 WHERE id_compra = NEW.id_compra
           )
     WHERE id_compra = NEW.id_compra;
END$$

DROP PROCEDURE IF EXISTS sp_agregar_producto_compra$$
CREATE PROCEDURE sp_agregar_producto_compra(
    IN p_id_compra      INT,
    IN p_id_producto    INT,
    IN p_cantidad       INT,
    IN p_costo_unitario DECIMAL(10,2)
)
BEGIN
    -- Registra la línea de la compra y, si el producto tiene un
    -- insumo asociado en el inventario (ver producto_insumo),
    -- aumenta su stock real de inmediato.
    DECLARE v_id_insumo INT DEFAULT NULL;

    INSERT INTO compra_detalle (id_compra, id_producto, cantidad, costo_unitario)
    VALUES (p_id_compra, p_id_producto, p_cantidad, p_costo_unitario);

    SELECT pi.id_insumo INTO v_id_insumo
      FROM producto_insumo pi
     WHERE pi.id_producto = p_id_producto
     LIMIT 1;

    IF v_id_insumo IS NOT NULL THEN
        UPDATE inventario
           SET cantidad_actual = cantidad_actual + p_cantidad
         WHERE id_insumo = v_id_insumo;
    END IF;
END$$

DROP PROCEDURE IF EXISTS sp_marcar_pedido_entregado$$
CREATE PROCEDURE sp_marcar_pedido_entregado(
    IN p_id_pedido INT
)
BEGIN
    -- Un pedido solo puede marcarse como entregado si ya está
    -- 'enviado_cocina' (es decir, ya se pagó y se confirmó). Así
    -- nunca se marca un pedido como entregado directamente al
    -- cobrar: ese paso queda para la pantalla de Cocina.
    DECLARE v_estado VARCHAR(20);

    SELECT estado INTO v_estado FROM pedidos WHERE id_pedido = p_id_pedido;

    IF v_estado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido no existe';
    ELSEIF v_estado <> 'enviado_cocina' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
            'Solo se pueden marcar como entregados los pedidos que están en cocina';
    ELSE
        UPDATE pedidos SET estado = 'entregado' WHERE id_pedido = p_id_pedido;
    END IF;
END$$

DELIMITER ;
