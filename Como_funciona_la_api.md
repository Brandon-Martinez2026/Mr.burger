# Mr.Burger — Conectar el programa a la base de datos

Pequeña documentación sohre como funciona esta cosa

## 1. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

## 2. Crear la base de datos

Ejecuta el script SQL original del proyecto (el que crea
`mr_burguer_db`, sus tablas, vistas, triggers y procedimientos):

```bash
mysql -u root -p < mr_burguer_db.sql
```

Luego ejecuta la migración que agrega las columnas que usa el
programa de escritorio (icono de cada producto, y tipo de
pedido/mesa/notas):

```bash
mysql -u root -p mr_burguer_db < migraciones/002_extension_app.sql
```

Y la migración que agrega el rol de cocinero (para la pantalla
de Cocina) y las tablas de compras/reabastecimiento (para el
apartado "Comprar Productos" del Panel de Administrador):

```bash
mysql -u root -p mr_burguer_db < migraciones/003_cocina_y_compras.sql
```

## 3. Configurar la conexión

Por defecto el programa se conecta a:

- host: `localhost`
- puerto: `3306`
- usuario: `Ruth`
- contraseña: (vacía)
- base de datos: `mr_burguer_db`

Si tu instalación de MySQL usa otros datos, defínelos como
variables de entorno antes de ejecutar el programa:

```bash
$env:MRBURGER_DB_USER = "Ruth <2"
$env:MRBURGER_DB_PASSWORD = "la formula osuna beibe"

# macOS / Linux
export MRBURGER_DB_USER=root
export MRBURGER_DB_PASSWORD=tu_contraseña
```

Variables disponibles: `MRBURGER_DB_HOST`, `MRBURGER_DB_PORT`,
`MRBURGER_DB_USER`, `MRBURGER_DB_PASSWORD`, `MRBURGER_DB_NAME`.

## 4. Sembrar datos iniciales (usuarios, categorías, productos)

```bash
python sembrar_datos.py
```
Agrega 3 usuarios base (administrador, cajero y cocina)

También agrega las categorías y algunos productos de ejemplo si
la tabla `productos` está vacía.

## 5. Ejecutar el programa

```bash
python IniciarSesion.py
```

Inicia sesión con `admin`/`admin123` (Panel de Administrador),
`cajero`/`cajero123` (Punto de Venta) o `cocina`/`cocina123`
(pantalla de Cocina). A partir de aquí, todo lo que se haga en
el programa —agregar productos, categorías, registrar ventas,
compras, cambios de inventario, entregar pedidos— se guarda
directamente en `mr_burguer_db`.

## lo conectado a la base de datos


- **Login** (`IniciarSesion.py`): valida usuario y contraseña
  contra la tabla `usuarios` (contraseña con hash, nunca en
  texto plano).
- **Punto de Venta**: el menú se carga desde `productos`/
  `categorias`; al cobrar, se crea el pedido, se agregan los
  productos, se registran los pagos (incluye pago mixto) y se
  confirma usando los procedimientos `sp_agregar_producto_pedido`,
  `sp_registrar_pago` y `sp_confirmar_pedido`, que ya validan y
  descuentan el inventario real. Al confirmarse, el pedido queda
  en estado `enviado_cocina` (no `entregado`): la entrega real la
  marca la pantalla de Cocina.
- **Cocina**: muestra los pedidos con estado `enviado_cocina`
  (los más antiguos primero) con sus productos y notas; el botón
  "Marcar como Listo" llama a `sp_marcar_pedido_entregado`, que
  solo permite pasar un pedido de `enviado_cocina` a `entregado`.
- **Panel de Administrador**: alta/edición/baja de productos y
  categorías, consulta de inventario, ventas, pedidos (con su
  estado real: en cocina / entregado), cajeros y reportes — todo
  contra la base de datos. El apartado "Comprar Productos"
  registra compras a proveedores (`compras`/`compra_detalle`) y
  aumenta el stock real mediante `sp_agregar_producto_compra`.
