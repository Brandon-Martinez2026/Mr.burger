DROP DATABASE IF EXISTS mr_burguer_db;
CREATE DATABASE mr_burguer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mr_burguer_db;

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
    id_categoria     INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE
);

-- Productos (platillos y combps)
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
    id_combo_detalle     INT AUTO_INCREMENT PRIMARY KEY,
    id_combo             INT NOT NULL,
    id_producto_incluido INT NOT NULL,
    cantidad             INT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_combo) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_producto_incluido) REFERENCES productos(id_producto)
);

-- Inventario
CREATE TABLE inventario (
    id_insumo            INT AUTO_INCREMENT PRIMARY KEY,
    nombre_insumo        VARCHAR(100) NOT NULL,
    unidad_medida        VARCHAR(20) NOT NULL,
    cantidad_actual      DECIMAL(10,2) NOT NULL DEFAULT 0,
    cantidad_minima      DECIMAL(10,2) NOT NULL DEFAULT 0,
    fecha_actualizacion  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Receta de insumos por producto
CREATE TABLE producto_insumo (
    id_producto_insumo INT AUTO_INCREMENT PRIMARY KEY,
    id_producto        INT NOT NULL,
    id_insumo          INT NOT NULL,
    cantidad_requerida DECIMAL(10,2) NOT NULL,
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

-- Pagos de un pedido 
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
#pollo
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

-- =========================================================
-- INSERCIÓN DE MENÚ MR. BURGER
-- Basado en el documento: Menu_MrBurger
-- Incluye: categorías, productos individuales, combos con su
-- detalle (productos que incluye cada combo) e inventario con
-- stock inicial de 350 unidades por cada producto individual.
-- =========================================================

USE mr_burguer_db;

-- =========================================================
-- 1) CATEGORÍAS
-- =========================================================
INSERT INTO categorias (nombre_categoria) VALUES
('Hamburguesas'),
('Extras y Acompañamientos'),
('Bebidas'),
('Desayunos'),
('Combos Pareja'),
('Combos Individuales'),
('Combos Familiares');

-- =========================================================
-- 2) PRODUCTOS INDIVIDUALES
-- =========================================================

-- 2.1 Hamburguesas
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto) VALUES
('Hamburguesa Clásica',    'Carne, queso, lechuga, tomate, cebolla',            35.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
('Hamburguesa Doble Carne','Doble carne, doble queso, vegetales',               48.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
('Queso Burguesa',         'Carne, doble queso, salsa especial',                40.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
('Hamburguesa BBQ',        'Carne, queso, tocino, aro de cebolla, salsa BBQ',   45.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
('Hamburguesa Hawaiana',   'Carne, queso, piña asada, tocino',                  42.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
('Hamburguesa Vegetariana','Base de vegetales/legumbres, queso, vegetales',     38.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
('Chicken Burger',         'Pechuga de pollo empanizada, lechuga, mayonesa',    40.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo'),
-- Producto usado únicamente como componente del "Combo Infantil"; no aparece con precio
-- individual en el menú, se agrega para poder registrarlo en combo_detalle.
('Hamburguesa Pequeña',    'Versión pequeña de hamburguesa, incluida en Combo Infantil', 20.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Hamburguesas'), 'platillo');

-- 2.2 Extras y acompañamientos
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto) VALUES
('Papas Fritas (individual)',      'Porción mediana',                          15.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra'),
('Papas Fritas (grande)',          'Porción grande',                           22.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra'),
('Papas con queso y tocino',       'Papas bañadas en queso cheddar y tocino',  28.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra'),
('Aros de cebolla',                'Porción mediana',                          18.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra'),
('Galletas',                       NULL,                                        15.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra'),
('Nuggets de pollo (6 pzas)',      'Con salsa a elección',                     20.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra'),
-- Componente exclusivo del "Combo Infantil" (3 pzas), sin precio individual en el menú.
('Nuggets de pollo (3 pzas)',      'Con salsa a elección, incluido en Combo Infantil', 12.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Extras y Acompañamientos'), 'extra');

-- 2.3 Bebidas
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto) VALUES
('Gaseosa (12 oz)',              'Coca-Cola, Fanta, Sprite, etc.', 10.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
('Gaseosa (grande)',             '22 oz',                          15.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
('Limonada / Refresco natural',  NULL,                             14.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
('Malteada',                     'Vainilla, chocolate o fresa',    22.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
('Café con leche',               NULL,                             10.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
('Café',                         NULL,                             8.00,  (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
('Agua pura',                    NULL,                             8.00,  (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida'),
-- Componente exclusivo del "Combo Infantil", sin precio individual en el menú.
('Jugo',                         'Incluido en Combo Infantil',     10.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Bebidas'), 'bebida');

-- 2.4 Desayunos (con restricción de horario 06:00 - 11:00)
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto, restringido_horario, hora_inicio, hora_fin) VALUES
('Desayuno Mr. Burger',        'Huevos, tocino, pan, café',                                              35.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00'),
('Bagel con queso crema',      NULL,                                                                      25.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00'),
('Desayuno Chapín',            'Huevos al gusto, frijoles volteados, plátanos fritos, crema y queso fresco', 38.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00'),
('Pan queque',                 '3 pancakes esponjosos acompañados de mantequilla y miel maple',           30.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00'),
('Sándwich de Huevos y Tocino','Pan brioche con huevo frito, queso cheddar y tocino crocante',            28.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00'),
('Waffle Mr. Burger',          'Waffle crujiente acompañado de tiras de pollo empanizado y miel maple',  35.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00'),
('Omelette Supremo',           'Omelette de 3 huevos relleno de jamón, queso, pimientos y cebolla',       36.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Desayunos'), 'platillo', TRUE, '06:00:00', '11:00:00');

-- =========================================================
-- 3) COMBOS (productos tipo 'combo')
-- =========================================================

-- 3.1 Combos para pareja
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto) VALUES
('Combo Pareja Clásico', '2 Hamburguesas Clásicas + 1 Papas grande + 2 Gaseosas',            95.00,  (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Pareja'), 'combo'),
('Combo Pareja BBQ',     '2 Hamburguesas BBQ + 1 Aros de cebolla + 2 Gaseosas',              110.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Pareja'), 'combo'),
('Combo Pareja Mixto',   '1 Hamburguesa Clásica + 1 Chicken Burger + Papas grande + 2 Gaseosas', 100.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Pareja'), 'combo');

-- 3.2 Combos individuales
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto) VALUES
('Combo Clásico',      'Hamburguesa Clásica + Papas individual + Gaseosa',        55.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Individuales'), 'combo'),
('Combo Queso Burguesa','Queso Burguesa + Papas individual + Gaseosa',            58.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Individuales'), 'combo'),
('Combo Doble Carne',  'Hamburguesa Doble Carne + Papas grande + Gaseosa',        68.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Individuales'), 'combo'),
('Combo Chicken',      'Chicken Burger + Papas individual + Gaseosa',             58.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Individuales'), 'combo'),
('Combo Infantil',     'Hamburguesa pequeña + Nuggets (3 pzas) + Jugo',           40.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Individuales'), 'combo');

-- 3.3 Combos familiares (4-5 personas)
INSERT INTO productos (nombre_producto, descripcion, precio, id_categoria, tipo_producto) VALUES
('Combo Familiar Clásico', '4 Hamburguesas Clásicas + 2 Papas grandes + 4 Gaseosas',                          175.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Familiares'), 'combo'),
('Combo Familiar BBQ',     '4 Hamburguesas BBQ + 2 Papas grandes + Aros de cebolla + 4 Gaseosas',              210.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Familiares'), 'combo'),
-- "5 Hamburguesas (mixtas a elección)": se registra como 5 Hamburguesas Clásicas por defecto;
-- el sistema puede permitir sustituir el tipo de hamburguesa al momento de la venta.
('Combo Fiesta Mr. Burger','5 Hamburguesas (mixtas a elección) + 2 Papas grandes + 6 Nuggets + 5 Gaseosas',   260.00, (SELECT id_categoria FROM categorias WHERE nombre_categoria='Combos Familiares'), 'combo');

-- =========================================================
-- 4) DETALLE DE COMBOS (productos que incluye cada combo)
-- =========================================================

-- Combo Pareja Clásico
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Clásica'), 2),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (grande)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 2);

-- Combo Pareja BBQ
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa BBQ'), 2),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Aros de cebolla'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 2);

-- Combo Pareja Mixto
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Mixto'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Clásica'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Mixto'), (SELECT id_producto FROM productos WHERE nombre_producto='Chicken Burger'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Mixto'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (grande)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Pareja Mixto'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 2);

-- Combo Clásico
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Clásica'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (individual)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 1);

-- Combo Queso Burguesa
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Queso Burguesa'), (SELECT id_producto FROM productos WHERE nombre_producto='Queso Burguesa'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Queso Burguesa'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (individual)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Queso Burguesa'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 1);

-- Combo Doble Carne
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Doble Carne'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Doble Carne'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Doble Carne'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (grande)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Doble Carne'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 1);

-- Combo Chicken
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Chicken'), (SELECT id_producto FROM productos WHERE nombre_producto='Chicken Burger'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Chicken'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (individual)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Chicken'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 1);

-- Combo Infantil
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Infantil'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Pequeña'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Infantil'), (SELECT id_producto FROM productos WHERE nombre_producto='Nuggets de pollo (3 pzas)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Infantil'), (SELECT id_producto FROM productos WHERE nombre_producto='Jugo'), 1);

-- Combo Familiar Clásico
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Clásica'), 4),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (grande)'), 2),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar Clásico'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 4);

-- Combo Familiar BBQ
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa BBQ'), 4),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (grande)'), 2),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Aros de cebolla'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Familiar BBQ'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 4);

-- Combo Fiesta Mr. Burger (hamburguesas mixtas -> se listan 5 Hamburguesas Clásicas por defecto)
INSERT INTO combo_detalle (id_combo, id_producto_incluido, cantidad) VALUES
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Fiesta Mr. Burger'), (SELECT id_producto FROM productos WHERE nombre_producto='Hamburguesa Clásica'), 5),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Fiesta Mr. Burger'), (SELECT id_producto FROM productos WHERE nombre_producto='Papas Fritas (grande)'), 2),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Fiesta Mr. Burger'), (SELECT id_producto FROM productos WHERE nombre_producto='Nuggets de pollo (6 pzas)'), 1),
((SELECT id_producto FROM productos WHERE nombre_producto='Combo Fiesta Mr. Burger'), (SELECT id_producto FROM productos WHERE nombre_producto='Gaseosa (12 oz)'), 5);

-- =========================================================
-- 5) INVENTARIO: stock de 350 por cada producto individual
--    (no se crea insumo para los combos, ya que su stock
--    depende de los insumos de los productos que los componen)
-- =========================================================

INSERT INTO inventario (nombre_insumo, unidad_medida, cantidad_actual, cantidad_minima)
SELECT nombre_producto, 'unidad', 350, 20
FROM productos
WHERE tipo_producto <> 'combo';

-- Vincula cada producto individual con su propio insumo (1 unidad de insumo = 1 unidad de producto)
INSERT INTO producto_insumo (id_producto, id_insumo, cantidad_requerida)
SELECT p.id_producto, i.id_insumo, 1
FROM productos p
JOIN inventario i ON i.nombre_insumo = p.nombre_producto
WHERE p.tipo_producto <> 'combo';