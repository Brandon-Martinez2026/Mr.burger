-- =========================================================
-- 005_personalizacion_hamburguesas.sql
-- Personalización real por ingrediente, no por nota de pedido.
-- Ejecutar después de 004_descuento_y_pendientes.sql.
-- =========================================================

CREATE TABLE IF NOT EXISTS producto_modificador (
    id_producto_modificador INT AUTO_INCREMENT PRIMARY KEY,
    id_producto             INT NOT NULL,
    id_insumo               INT NOT NULL,
    cantidad_por_extra      DECIMAL(10,2) NOT NULL,
    permite_quitar          BOOLEAN NOT NULL DEFAULT FALSE,
    permite_extra           BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES inventario(id_insumo),
    UNIQUE KEY uq_producto_modificador (id_producto, id_insumo)
);

CREATE TABLE IF NOT EXISTS detalle_pedido_modificador (
    id_detalle_modificador INT AUTO_INCREMENT PRIMARY KEY,
    id_detalle             INT NOT NULL,
    id_insumo              INT NOT NULL,
    quitar                 BOOLEAN NOT NULL DEFAULT FALSE,
    cantidad_extra         INT NOT NULL DEFAULT 0,
    cantidad_por_extra     DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_detalle) REFERENCES detalle_pedido(id_detalle) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES inventario(id_insumo)
);

INSERT INTO inventario (nombre_insumo, unidad_medida, cantidad_actual, cantidad_minima)
SELECT 'Pepinillos', 'g', 8000, 800
WHERE NOT EXISTS (SELECT 1 FROM inventario WHERE nombre_insumo = 'Pepinillos');

INSERT IGNORE INTO producto_modificador (id_producto, id_insumo, cantidad_por_extra, permite_quitar, permite_extra)
SELECT p.id_producto, i.id_insumo, 15, FALSE, TRUE
FROM productos p
JOIN inventario i ON i.nombre_insumo = 'Pepinillos'
WHERE p.nombre_producto IN (
    'Hamburguesa Clásica', 'Hamburguesa Doble Carne', 'Queso Burguesa',
    'Hamburguesa BBQ', 'Hamburguesa Hawaiana', 'Hamburguesa Vegetariana',
    'Chicken Burger', 'Hamburguesa Pequeña'
);

DELIMITER $$
DROP PROCEDURE IF EXISTS sp_confirmar_pedido$$
CREATE PROCEDURE sp_confirmar_pedido(
    IN p_id_pedido INT,
    IN p_descuento DECIMAL(10,2)
)
BEGIN
    DECLARE v_subtotal DECIMAL(10,2);
    DECLARE v_total DECIMAL(10,2);
    DECLARE v_total_pagado DECIMAL(10,2);
    DECLARE v_metodos_distintos INT;
    DECLARE v_metodo_final ENUM('efectivo','tarjeta','mixto');
    DECLARE v_insuficiente INT DEFAULT 0;

    SELECT COUNT(*) INTO v_insuficiente
    FROM (
        SELECT uso.id_insumo, SUM(uso.cantidad_necesaria) AS necesario,
               MAX(inv.cantidad_actual) AS disponible
        FROM (
            SELECT pi.id_insumo, SUM(pi.cantidad_requerida * dp.cantidad) AS cantidad_necesaria
              FROM detalle_pedido dp
              JOIN producto_insumo pi ON pi.id_producto = dp.id_producto
             WHERE dp.id_pedido = p_id_pedido
             GROUP BY pi.id_insumo
            UNION ALL
            SELECT dpm.id_insumo,
                   SUM(CASE WHEN dpm.quitar = 1
                            THEN -dpm.cantidad_por_extra * dp.cantidad
                            ELSE dpm.cantidad_por_extra * dpm.cantidad_extra * dp.cantidad END)
              FROM detalle_pedido dp
              JOIN detalle_pedido_modificador dpm ON dpm.id_detalle = dp.id_detalle
             WHERE dp.id_pedido = p_id_pedido
             GROUP BY dpm.id_insumo
        ) uso
        JOIN inventario inv ON inv.id_insumo = uso.id_insumo
        GROUP BY uso.id_insumo
        HAVING necesario > disponible
    ) AS faltantes;

    IF v_insuficiente > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Inventario insuficiente para completar el pedido';
    END IF;

    SELECT subtotal INTO v_subtotal FROM pedidos WHERE id_pedido = p_id_pedido;
    SET v_total = v_subtotal - IFNULL(p_descuento, 0);
    IF v_total < 0 THEN SET v_total = 0; END IF;

    SELECT COALESCE(SUM(monto), 0), COUNT(DISTINCT metodo_pago)
      INTO v_total_pagado, v_metodos_distintos
      FROM pedido_pagos WHERE id_pedido = p_id_pedido;

    IF v_total_pagado < v_total THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El monto pagado no cubre el total del pedido';
    END IF;

    IF v_metodos_distintos > 1 THEN
        SET v_metodo_final = 'mixto';
    ELSE
        SELECT metodo_pago INTO v_metodo_final FROM pedido_pagos
         WHERE id_pedido = p_id_pedido LIMIT 1;
    END IF;

    UPDATE inventario inv
    JOIN (
        SELECT uso.id_insumo, SUM(uso.cantidad_necesaria) AS cantidad_usada
        FROM (
            SELECT pi.id_insumo, SUM(pi.cantidad_requerida * dp.cantidad) AS cantidad_necesaria
              FROM detalle_pedido dp
              JOIN producto_insumo pi ON pi.id_producto = dp.id_producto
             WHERE dp.id_pedido = p_id_pedido
             GROUP BY pi.id_insumo
            UNION ALL
            SELECT dpm.id_insumo,
                   SUM(CASE WHEN dpm.quitar = 1
                            THEN -dpm.cantidad_por_extra * dp.cantidad
                            ELSE dpm.cantidad_por_extra * dpm.cantidad_extra * dp.cantidad END)
              FROM detalle_pedido dp
              JOIN detalle_pedido_modificador dpm ON dpm.id_detalle = dp.id_detalle
             WHERE dp.id_pedido = p_id_pedido
             GROUP BY dpm.id_insumo
        ) uso
        GROUP BY uso.id_insumo
    ) uso ON uso.id_insumo = inv.id_insumo
    SET inv.cantidad_actual = inv.cantidad_actual - uso.cantidad_usada;

    UPDATE pedidos
       SET estado='enviado_cocina', metodo_pago=v_metodo_final,
           monto_recibido=v_total_pagado, total=v_total
     WHERE id_pedido=p_id_pedido;
END$$
DELIMITER ;
