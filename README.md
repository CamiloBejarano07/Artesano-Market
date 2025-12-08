Artesano Market

Artesano Market es una aplicación web desarrollada con Django que permite gestionar productos artesanales, realizar pedidos y administrar información de clientes y vendedores. El proyecto utiliza MySQL como base de datos principal y está estructurado para facilitar el despliegue y la colaboración en equipo.

Características principales

Gestión de usuarios, productos y pedidos.

Conexión a base de datos MySQL mediante MySQL Workbench.

Generación de archivos PDF usando ReportLab.

Frontend con HTML, CSS y JavaScript.

Proyecto preparado para ser desplegado en servidores como AWS.

Estructura ordenada y lista para incluir futuras integraciones de pago.

Requisitos previos

Antes de ejecutar el proyecto, asegúrese de tener instalado:

Python 3.10 o superior

MySQL Server

MySQL Workbench

Git

pip para instalar dependencias

Instalación del proyecto

Clonar el repositorio:

git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio


Crear y activar un entorno virtual:

python -m venv venv
venv\Scripts\activate


Instalar dependencias:

pip install -r requirements.txt


Crear la base de datos en MySQL:

Abrir MySQL Workbench

Crear una base de datos llamada artesano_db (o el nombre que uses en settings.py)

Configurar la base de datos en settings.py:

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


Ejecutar migraciones:

python manage.py migrate


Ejecutar el servidor:

python manage.py runserver

Estructura del proyecto
Artesano/
│── core/
│   ├── models.py
│   ├── views/
│   ├── templates/
│   └── static/
│
│── Artesano/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
│── requirements.txt
│── manage.py
│── README.md

Uso

Acceder a la aplicación en:

http://127.0.0.1:8000/


Iniciar sesión si está habilitado.

Administrar productos y pedidos desde el panel.
