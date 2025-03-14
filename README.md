# Golf Scorecard Manager

Una aplicación de línea de comandos para gestionar tarjetas de puntuación de golf, con una interfaz moderna y fácil de usar.

## Características

- Gestión de jugadores: añadir, editar, eliminar y listar jugadores con sus hándicaps
- Gestión de campos: añadir, editar, eliminar y listar campos con sus características (par, slope, course rating)
- Gestión de tarjetas: registrar, visualizar y eliminar tarjetas de puntuación
- Cálculo automático de puntos y sistema Stableford
- Interfaz de línea de comandos moderna con colores y formato mejorado
- Base de datos SQLite para almacenamiento persistente

## Requisitos

- Python 3.6 o superior
- Paquetes Python especificados en `requirements.txt`

## Instalación

1. Clona o descarga este repositorio
2. Navega al directorio del proyecto
3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Para iniciar la aplicación, ejecuta:

```bash
python src/main.py
```

### Menú Principal

La aplicación presenta un menú principal con las siguientes opciones:

- **Jugadores**: Ver, añadir, editar y eliminar jugadores
- **Campos**: Ver, añadir, editar y eliminar campos de golf
- **Tarjetas**: Ver, añadir y eliminar tarjetas de puntuación
- **Sistema**: Salir de la aplicación

### Flujo de trabajo típico

1. Añadir jugadores con sus hándicaps
2. Añadir campos con sus características (par, slope, course rating)
3. Registrar tarjetas de puntuación para los jugadores en los campos
4. Consultar las tarjetas registradas y ver estadísticas

## Estructura del Proyecto

```
golf-scorecard-new/
├── data/                  # Directorio para la base de datos
├── src/                   # Código fuente
│   ├── controllers/       # Controladores para la lógica de negocio
│   ├── models/            # Modelos de datos
│   ├── utils/             # Utilidades y helpers
│   ├── views/             # Vistas para la interfaz de usuario
│   ├── database.py        # Gestión de la base de datos
│   └── main.py            # Punto de entrada principal
└── requirements.txt       # Dependencias del proyecto
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.
