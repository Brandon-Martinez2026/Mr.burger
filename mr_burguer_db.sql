DROP DATABASE IF EXISTS mr_burguer_db;
CREATE DATABASE mr_burguer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mr_burguer_db;

-- =========================================================
-- TABLAS
-- =========================================================

-- Roles
CREATE TABLE roles (
    id_rol      INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol  ENUM('administrador','usuario','inhabilitado') NOT NULL UNIQUE
);
INSERT INTO roles (nombre_rol) VALUES ('administrador'), ('usuario'), ('inhabilitado');

-- Usuarios
CREATE TABLE usuarios (
    id_usuario       INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo  VARCHAR(100) NOT NULL,
    usuario          VARCHAR(50)  NOT NULL UNIQUE,
    contrasena_hash  VARCHAR(255) NOT NULL,
    id_rol           INT NOT NULL DEFAULT 2,
    fecha_registro   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- Categorias
CREATE TABLE categorias (
    id_categoria    INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE
);

-- Productos (platillos y combos)
CREATE TABLE productos (
    id_producto         INT AUTO_INCREMENT PRIMARY KEY,
    nombre_producto     VARCHAR(100) NOT NULL,
    descripcion         VARCHAR(255),
    precio              DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    id_categoria        INT,
    tipo_producto       ENUM('platillo','combo','bebida','extra') NOT NULL DEFAULT 'platillo',
    habilitado          BOOLEAN NOT NULL DEFAULT TRUE,
    restringido_horario BOOLEAN NOT NULL DEFAULT FALSE,
    hora_inicio         TIME DEFAULT NULL,
    hora_fin            TIME DEFAULT NULL,
    fecha_creacion      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

-- Detalle de combos
CREATE TABLE combo_detalle (
    id_combo_detalle    INT AUTO_INCREMENT PRIMARY KEY,
    id_combo             INT NOT NULL,
    id_producto_incluido INT NOT NULL,
    cantidad              INT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_combo) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_producto_incluido) REFERENCES productos(id_producto)
);

-- Inventario
CREATE TABLE inventario (
    id_insumo            INT AUTO_INCREMENT PRIMARY KEY,
    nombre_insumo        VARCHAR(100) NOT NULL,
    unidad_medida         VARCHAR(20) NOT NULL,
    cantidad_actual       DECIMAL(10,2) NOT NULL DEFAULT 0,
    cantidad_minima       DECIMAL(10,2) NOT NULL DEFAULT 0,
    fecha_actualizacion   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Receta de insumos por producto
CREATE TABLE producto_insumo (
    id_producto_insumo INT AUTO_INCREMENT PRIMARY KEY,
    id_producto         INT NOT NULL,
    id_insumo           INT NOT NULL,
    cantidad_requerida  DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES inventario(id_insumo)
);

-- Pedidos
CREATE TABLE pedidos (
    id_pedido        INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario       INT NOT NULL,
    fecha_hora       DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado           ENUM('en_proceso','confirmado','enviado_cocina','entregado','cancelado')
                     NOT NULL DEFAULT 'en_proceso',
    metodo_pago      ENUM('efectivo','tarjeta','mixto') DEFAULT NULL,
    subtotal         DECIMAL(10,2) NOT NULL DEFAULT 0,
    total            DECIMAL(10,2) NOT NULL DEFAULT 0,
    monto_recibido   DECIMAL(10,2) DEFAULT NULL,
    cambio           DECIMAL(10,2) DEFAULT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Detalle de pedido
CREATE TABLE detalle_pedido (
    id_detalle       INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido        INT NOT NULL,
    id_producto      INT NOT NULL,
    cantidad         INT NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    precio_unitario  DECIMAL(10,2) NOT NULL,
    subtotal_linea   DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Pagos de un pedido (permite pago mixto: varias filas, distintos metodos)
CREATE TABLE pedido_pagos (
    id_pago      INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido    INT NOT NULL,
    metodo_pago  ENUM('efectivo','tarjeta') NOT NULL,
    monto        DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    fecha_pago   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE
);

-- =========================================================
-- ÍNDICES
-- =========================================================

CREATE INDEX idx_productos_habilitado_horario ON productos(habilitado, restringido_horario);
CREATE INDEX idx_productos_id_categoria ON productos(id_categoria);
CREATE INDEX idx_usuarios_id_rol ON usuarios(id_rol);
CREATE INDEX idx_combo_detalle_id_combo ON combo_detalle(id_combo);
CREATE INDEX idx_combo_detalle_id_producto_incluido ON combo_detalle(id_producto_incluido);
CREATE INDEX idx_producto_insumo_id_producto ON producto_insumo(id_producto);
CREATE INDEX idx_producto_insumo_id_insumo ON producto_insumo(id_insumo);
CREATE INDEX idx_inventario_cantidad_actual ON inventario(cantidad_actual);
CREATE INDEX idx_pedidos_estado_fecha ON pedidos(estado, fecha_hora);
CREATE INDEX idx_pedidos_id_usuario ON pedidos(id_usuario);
CREATE INDEX idx_pedidos_fecha_hora ON pedidos(fecha_hora);
CREATE INDEX idx_detalle_pedido_id_pedido ON detalle_pedido(id_pedido);
CREATE INDEX idx_detalle_pedido_id_producto ON detalle_pedido(id_producto);
CREATE INDEX idx_pedido_pagos_id_pedido ON pedido_pagos(id_pedido);

-- =========================================================
-- VISTAS
-- =========================================================

CREATE VIEW vista_menu_disponible AS
SELECT p.*
FROM productos p
WHERE p.habilitado = TRUE
  AND (
        p.restringido_horario = FALSE
        OR (
              p.hora_inicio <= p.hora_fin
              AND CURTIME() BETWEEN p.hora_inicio AND p.hora_fin
           )
        OR (
              p.hora_inicio > p.hora_fin
              AND (CURTIME() >= p.hora_inicio OR CURTIME() <= p.hora_fin)
           )
      );

CREATE VIEW vista_reporte_ventas_diarias AS
SELECT DATE(fecha_hora) AS fecha,
       COUNT(*)         AS total_pedidos,
       SUM(total)        AS total_ventas
FROM pedidos
WHERE estado IN ('enviado_cocina','entregado')
GROUP BY DATE(fecha_hora);

CREATE VIEW vista_reporte_productos_vendidos AS
SELECT p.nombre_producto,
       SUM(dp.cantidad)        AS unidades_vendidas,
       SUM(dp.subtotal_linea)  AS total_generado
FROM detalle_pedido dp
JOIN productos p  ON p.id_producto = dp.id_producto
JOIN pedidos pe   ON pe.id_pedido = dp.id_pedido
WHERE pe.estado IN ('enviado_cocina','entregado')
GROUP BY p.nombre_producto
ORDER BY unidades_vendidas DESC;

CREATE VIEW vista_inventario_bajo_minimo AS
SELECT * FROM inventario WHERE cantidad_actual <= cantidad_minima;

CREATE VIEW vista_pedido_pagos_resumen AS
SELECT pp.id_pedido,
       pe.estado,
       pe.total,
       SUM(pp.monto) AS total_pagado,
       SUM(CASE WHEN pp.metodo_pago = 'efectivo' THEN pp.monto ELSE 0 END) AS total_efectivo,
       SUM(CASE WHEN pp.metodo_pago = 'tarjeta'  THEN pp.monto ELSE 0 END) AS total_tarjeta,
       COUNT(DISTINCT pp.metodo_pago) AS metodos_usados
FROM pedido_pagos pp
JOIN pedidos pe ON pe.id_pedido = pp.id_pedido
GROUP BY pp.id_pedido, pe.estado, pe.total;

-- =========================================================
-- TRIGGERS
-- =========================================================

DELIMITER $$

CREATE TRIGGER trg_after_insert_detalle
AFTER INSERT ON detalle_pedido
FOR EACH ROW
BEGIN
    UPDATE pedidos
    SET subtotal = (SELECT COALESCE(SUM(subtotal_linea),0) FROM detalle_pedido WHERE id_pedido = NEW.id_pedido),
        total    = (SELECT COALESCE(SUM(subtotal_linea),0) FROM detalle_pedido WHERE id_pedido = NEW.id_pedido)
    WHERE id_pedido = NEW.id_pedido;
END$$

CREATE TRIGGER trg_after_update_detalle
AFTER UPDATE ON detalle_pedido
FOR EACH ROW
BEGIN
    UPDATE pedidos
    SET subtotal = (SELECT COALESCE(SUM(subtotal_linea),0) FROM detalle_pedido WHERE id_pedido = NEW.id_pedido),
        total    = (SELECT COALESCE(SUM(subtotal_linea),0) FROM detalle_pedido WHERE id_pedido = NEW.id_pedido)
    WHERE id_pedido = NEW.id_pedido;
END$$

CREATE TRIGGER trg_after_delete_detalle
AFTER DELETE ON detalle_pedido
FOR EACH ROW
BEGIN
    UPDATE pedidos
    SET subtotal = (SELECT COALESCE(SUM(subtotal_linea),0) FROM detalle_pedido WHERE id_pedido = OLD.id_pedido),
        total    = (SELECT COALESCE(SUM(subtotal_linea),0) FROM detalle_pedido WHERE id_pedido = OLD.id_pedido)
    WHERE id_pedido = OLD.id_pedido;
END$$

CREATE TRIGGER trg_before_update_pedido_pago
BEFORE UPDATE ON pedidos
FOR EACH ROW
BEGIN
    IF NEW.metodo_pago IN ('efectivo','mixto') AND NEW.monto_recibido IS NOT NULL THEN
        SET NEW.cambio = NEW.monto_recibido - NEW.total;
    ELSE
        SET NEW.cambio = NULL;
    END IF;
END$$

DELIMITER ;

-- =========================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =========================================================

DELIMITER $$

CREATE PROCEDURE sp_agregar_producto_pedido(
    IN p_id_pedido   INT,
    IN p_id_producto INT,
    IN p_cantidad    INT
)
BEGIN
    DECLARE v_disponible INT DEFAULT 0;
    DECLARE v_precio DECIMAL(10,2);
    SELECT COUNT(*), MAX(precio) INTO v_disponible, v_precio
    FROM vista_menu_disponible
    WHERE id_producto = p_id_producto;
    IF v_disponible = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Producto no disponible en este horario o esta deshabilitado';
    ELSE
        INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
        VALUES (p_id_pedido, p_id_producto, p_cantidad, v_precio);
    END IF;
END$$

CREATE PROCEDURE sp_registrar_pago(
    IN p_id_pedido   INT,
    IN p_metodo_pago ENUM('efectivo','tarjeta'),
    IN p_monto       DECIMAL(10,2)
)
BEGIN
    DECLARE v_estado VARCHAR(20);

    SELECT estado INTO v_estado FROM pedidos WHERE id_pedido = p_id_pedido;

    IF v_estado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido no existe';
    ELSEIF v_estado NOT IN ('en_proceso','confirmado') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pueden registrar pagos en este estado del pedido';
    ELSE
        INSERT INTO pedido_pagos (id_pedido, metodo_pago, monto)
        VALUES (p_id_pedido, p_metodo_pago, p_monto);
    END IF;
END$$

CREATE PROCEDURE sp_eliminar_pago(
    IN p_id_pago INT
)
BEGIN
    DECLARE v_id_pedido INT;
    DECLARE v_estado VARCHAR(20);

    SELECT pp.id_pedido, pe.estado INTO v_id_pedido, v_estado
    FROM pedido_pagos pp
    JOIN pedidos pe ON pe.id_pedido = pp.id_pedido
    WHERE pp.id_pago = p_id_pago;

    IF v_id_pedido IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pago no existe';
    ELSEIF v_estado NOT IN ('en_proceso','confirmado') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pueden eliminar pagos de un pedido ya confirmado';
    ELSE
        DELETE FROM pedido_pagos WHERE id_pago = p_id_pago;
    END IF;
END$$

CREATE PROCEDURE sp_confirmar_pedido(
    IN p_id_pedido INT
)
BEGIN
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

    SELECT total INTO v_total FROM pedidos WHERE id_pedido = p_id_pedido;

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
        monto_recibido = v_total_pagado
    WHERE id_pedido = p_id_pedido;
END$$

CREATE PROCEDURE sp_actualizar_rol_usuario(
    IN p_id_usuario INT,
    IN p_nuevo_rol   ENUM('administrador','usuario','inhabilitado')
)
BEGIN
    DECLARE v_id_rol INT;
    SELECT id_rol INTO v_id_rol FROM roles WHERE nombre_rol = p_nuevo_rol;
    UPDATE usuarios SET id_rol = v_id_rol WHERE id_usuario = p_id_usuario;
END$$

DELIMITER ;
