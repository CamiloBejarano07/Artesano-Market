```
Artesano Market

Artesano Market es una aplicación web desarrollada con Django que ofrece una plataforma completa para la gestión de productos artesanales, el procesamiento de pedidos y la administración de clientes y vendedores.

El proyecto utiliza MySQL como base de datos y una arquitectura modular que facilita el despliegue en la nube y la colaboración en equipo.

Requisitos Previos

Asegúrese de tener instalado:

- Python 3.10 o superior  
- MySQL Server  
- MySQL Workbench  
- Git  
- pip  

Instalación del Proyecto

 1. Clonar el Repositorio


git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
2. Crear el Entorno Virtual

python -m venv venv
Activar en Windows:



venv\Scripts\activate
Activar en Linux o macOS:


source venv/bin/activate
3. Instalar Dependencias

pip install -r requirements.txt
Configuración de la Base de Datos
4. Crear Base de Datos
En MySQL Workbench cree una base llamada:


artesano_db
5. Configurar settings.py
Editar el archivo Artesano/settings.py:


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
Ejecutar Migraciones

python manage.py migrate
Ejecutar el Servidor

python manage.py runserver
Acceder en el navegador:

http://127.0.0.1:8000/

Flujo de Uso
Inicie sesión (si está habilitado).

Gestione productos, pedidos y usuarios desde el panel.

Explore el catálogo disponible.

Estructura del Proyecto

ArtesanoMarket/
│
├── core/                     
│   ├── models.py             
│   ├── views/                
│   ├── templates/            
│   └── static/               
│
├── Artesano/                 
│   ├── settings.py           
│   ├── urls.py               
│   └── wsgi.py               
│
├── requirements.txt          
├── manage.py                 
└── README.md           
