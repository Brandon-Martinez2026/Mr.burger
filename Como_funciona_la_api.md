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
Agrega 2 usuarios base 

También agrega las categorías y algunos productos de ejemplo si
la tabla `productos` está vacía.

## 5. Ejecutar el programa

```bash
python IniciarSesion.py
```

Inicia sesión con `admin`/`admin123` (Panel de Administrador) o
`cajero`/`cajero123` (Punto de Venta). A partir de aquí, todo lo
que se haga en el programa —agregar productos, categorías,
registrar ventas, cambios de inventario— se guarda directamente
en `mr_burguer_db`.

## lo conectado a la base de datos


- **Login** (`IniciarSesion.py`): valida usuario y contraseña
  contra la tabla `usuarios` (contraseña con hash, nunca en
  texto plano).
- **Punto de Venta**: el menú se carga desde `productos`/
  `categorias`; al cobrar, se crea el pedido, se agregan los
  productos, se registran los pagos (incluye pago mixto) y se
  confirma usando los procedimientos `sp_agregar_producto_pedido`,
  `sp_registrar_pago` y `sp_confirmar_pedido`, que ya validan y
  descuentan el inventario real.
- **Panel de Administrador**: alta/edición/baja de productos y
  categorías, consulta de inventario, ventas, pedidos, cajeros y
  reportes — todo contra la base de datos.
