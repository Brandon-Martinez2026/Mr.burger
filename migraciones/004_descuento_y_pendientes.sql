-- =========================================================
-- migraciones/004_descuento_y_pendientes.sql
-- ---------------------------------------------------------
-- Permite aplicar un descuento a un pedido al cobrarlo.
--
-- Por qué es necesaria: sp_confirmar_pedido comparaba el monto
-- pagado contra pedidos.total (la suma automática de las líneas
-- del pedido, mantenida por triggers). Si el cajero aplica un
-- descuento y solo cobra el monto ya descontado, esa validación
-- rechazaba el pago con "El monto pagado no cubre el total del
-- pedido". Esta migración le agrega un parámetro de descuento al
-- procedimiento: valida el pago contra (subtotal - descuento) y
-- deja el "total" final ya con el descuento aplicado.
--
-- Ejecútala UNA vez, después de 002_extension_app.sql y
-- 003_cocina_y_compras.sql:
--   mysql -u root -p mr_burguer_db < migraciones/004_descuento_y_pendientes.sql
-- =========================================================

USE mr_burguer_db;

DROP PROCEDURE IF EXISTS sp_confirmar_pedido;

DELIMITER $$

CREATE PROCEDURE sp_confirmar_pedido(
    IN p_id_pedido INT,
    IN p_descuento DECIMAL(10,2)
)
BEGIN
    DECLARE v_subtotal          DECIMAL(10,2);
    DECLARE v_total             DECIMAL(10,2);
    DECLARE v_total_pagado      DECIMAL(10,2);
    DECLARE v_metodos_distintos INT;
    DECLARE v_metodo_final      ENUM('efectivo','tarjeta','mixto');
    DECLARE v_insuficiente      INT DEFAULT 0;

    SELECT COUNT(*) INTO v_insuficiente
    FROM (
        SELECT pi.id_insumo,
               SUM(pi.cantidad_requerida * dp.cantidad) AS necesario,
               MAX(inv.cantidad_actual) AS disponible
        FROM detalle_pedido dp
        JOIN producto_insumo pi ON pi.id_producto = dp.id_producto
        JOIN inventario inv     ON inv.id_insumo = pi.id_insumo
        WHERE dp.id_pedido = p_id_pedido
        GROUP BY pi.id_insumo
        HAVING necesario > disponible
    ) AS faltantes;

    IF v_insuficiente > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Inventario insuficiente para completar el pedido';
    END IF;

    SELECT subtotal INTO v_subtotal FROM pedidos WHERE id_pedido = p_id_pedido;

    SET v_total = v_subtotal - IFNULL(p_descuento, 0);

    IF v_total < 0 THEN
        SET v_total = 0;
    END IF;

    SELECT COALESCE(SUM(monto), 0), COUNT(DISTINCT metodo_pago)
    INTO v_total_pagado, v_metodos_distintos
    FROM pedido_pagos
    WHERE id_pedido = p_id_pedido;

    IF v_total_pagado < v_total THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El monto pagado no cubre el total del pedido';
    END IF;

    IF v_metodos_distintos > 1 THEN
        SET v_metodo_final = 'mixto';
    ELSE
        SELECT metodo_pago INTO v_metodo_final
        FROM pedido_pagos
        WHERE id_pedido = p_id_pedido
        LIMIT 1;
    END IF;

    UPDATE inventario inv
    JOIN (
        SELECT pi.id_insumo, SUM(pi.cantidad_requerida * dp.cantidad) AS cantidad_usada
        FROM detalle_pedido dp
        JOIN producto_insumo pi ON pi.id_producto = dp.id_producto
        WHERE dp.id_pedido = p_id_pedido
        GROUP BY pi.id_insumo
    ) uso ON uso.id_insumo = inv.id_insumo
    SET inv.cantidad_actual = inv.cantidad_actual - uso.cantidad_usada;

    UPDATE pedidos
    SET estado         = 'enviado_cocina',
        metodo_pago    = v_metodo_final,
        monto_recibido = v_total_pagado,
        total          = v_total
    WHERE id_pedido = p_id_pedido;
END$$

DELIMITER ;
