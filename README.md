Artesano Market

Artesano Market es una aplicación web robusta desarrollada con **Django** que ofrece una plataforma completa para la gestión de productos artesanales, el procesamiento de pedidos y la administración de información esencial de clientes y vendedores.

El proyecto está diseñado para ser escalable, utilizando MySQL como base de datos principal y una estructura modular que facilita tanto el despliegue en la nube (como AWS) como la colaboración en equipo.


Características Principales

Gestión Completa: Sistema para la administración de usuarios, inventario de productos artesanales y seguimiento de pedidos.
Conexión a MySQL: Utiliza MySQL Workbench y un motor de base de datos MySQL para almacenamiento persistente y escalable.
Generación de Documentos: Capacidad para generar archivos PDF utilizando la librería ReportLab.
Tecnologías Frontend: Interfaz de usuario desarrollada con HTML, CSS y JavaScript.
Preparado para Despliegue: Estructura optimizada para su implementación en servidores cloud (ej. AWS).
Escalabilidad: Arquitectura lista para futuras integraciones, incluyendo módulos de pago.

## Requisitos Previos

Antes de proceder con la instalación y ejecución del proyecto, asegúrese de tener los siguientes componentes instalados en su sistema:

Python 3.10 o superior
MySQL Server
MySQL Workbench
Git
pip (Administrador de paquetes de Python)

Instalación del Proyecto

Siga estos pasos para configurar y ejecutar la aplicación Artesano Market de forma local:

1. Clonar el Repositorio

Abra su terminal y ejecute los siguientes comandos:


git clone [https://github.com/tu_usuario/tu_repositorio.git](https://github.com/tu_usuario/tu_repositorio.git)
cd tu_repositorio
2. Configurar el Entorno Virtual
Se recomienda usar un entorno virtual para aislar las dependencias:



Crear el entorno virtual
python -m venv venv

Activar el entorno virtual (Windows)
venv\Scripts\activate

Si usa Linux/macOS:
source venv/bin/activate
3. Instalar Dependencias
Con el entorno virtual activado, instale todas las librerías necesarias:


pip install -r requirements.txt
4. Configuración de la Base de Datos
a. Crear la Base de Datos en MySQL
Abra MySQL Workbench.

Crear una base de datos llamada artesano_db (o el nombre que desee utilizar).

b. Configurar settings.py
Edite el archivo Artesano/settings.py para establecer la conexión a su base de datos local.

Importante: Reemplace 'tu_usuario' y 'tu_contraseña' con sus credenciales de MySQL.

Python

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'artesano_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
5. Ejecutar Migraciones
Aplique las migraciones de Django para crear las tablas en su base de datos:

python manage.py migrate
6. Ejecutar el Servidor
Inicie el servidor de desarrollo de Django:


python manage.py runserver
Uso
Una vez que el servidor se esté ejecutando, podrá acceder a la aplicación desde su navegador.

Acceder a la aplicación en: http://127.0.0.1:8000/

Flujo: Inicie sesión (si está habilitado) y comience a administrar productos y pedidos desde el panel.

Estructura del Proyecto
La aplicación Artesano Market sigue una estructura estándar de Django:

Artesano/
│
├── core/                         # Aplicación principal de Django
│   ├── models.py                 # Definición de modelos de la base de datos
│   ├── views/                    # Lógica de las vistas y controladores
│   ├── templates/                # Archivos HTML (vistas)
│   └── static/                   # Archivos estáticos (CSS, JS, imágenes)
│
├── Artesano/                     # Configuración principal del proyecto
│   ├── settings.py               # Configuración global del proyecto
│   ├── urls.py                   # Definición de rutas URL
│   └── wsgi.py                   # Puerta de enlace para despliegue en producción
│
├── requirements.txt              # Lista de dependencias de Python
├── manage.py                     # Utilidad de línea de comandos de Django
└── README.md                     # Este archivo
