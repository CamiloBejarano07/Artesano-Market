from django.urls import path
from core.views import admin_views
from core.views import auth_views
from core.views import categoria_views
from core.views import clientes_views
from core.views import compra_views
from core.views import home_views
from core.views.personas_views import PersonasView
from core.views import vendedores_views
from core.views.ventas_views import listar_ventas, obtener_venta
from core.views import productos_views
from django.conf import settings
from django.conf.urls.static import static
from core.views.auth_views import terminos


urlpatterns = [
    # Administración
    path('correos/admin/', admin_views.mostrar_formulario_correos, name='mostrar_formulario_correos'),
    path('enviar-correos/admin/', admin_views.enviar_correos_masivos, name='enviar_correos_masivos'),
    path('estadisticas/admin', admin_views.estadisticas_admin, name='estadisticas'),
    path('estadisticas/seller/', vendedores_views.dashboard_vendedor, name='estadisticas_seller'),
    
    # Autenticación
    path('login/', auth_views.show_login_page, name='login'),
    path('auth/login/', auth_views.login, name='auth_login'),  
    path('auth/register/', auth_views.register, name='register'),
    path('auth/logout/', auth_views.logout, name='auth_logout'),
    path("terminos/", terminos, name="terminos"),
    
    # Recuperación de contraseña
    path('password-recovery/', auth_views.password_recovery_request, name='password_recovery_request'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),


    # Categorías
    path('categorias/vista/', categoria_views.mostrar_catalogo, name='mostrar_catalogo'),
    path('categorias/', categoria_views.listar_categorias, name='listar_categorias'),
    path('categorias/<int:id>/', categoria_views.obtener_categoria, name='obtener_categoria'),
    path('categorias/crear/', categoria_views.crear_categoria, name='crear_categoria'),
    path('categorias/<int:id>/actualizar/', categoria_views.actualizar_categoria, name='actualizar_categoria'),
    path('categorias/<int:id>/eliminar/', categoria_views.eliminar_categoria, name='eliminar_categoria'),
    path('categorias/reporte/csv/', categoria_views.exportar_csv, name='exportar_csv'),

    # Compras
    path('compras/', compra_views.listar_compras, name='listar_compras'),
    path('compras/<int:id>/', compra_views.obtener_compra, name='obtener_compra'),
    path('compras/crear/', compra_views.crear_compra, name='crear_compra'),
    path('compras/<int:id>/actualizar/', compra_views.actualizar_compra, name='actualizar_compra'),
    path('compras/<int:id>/eliminar/', compra_views.eliminar_compra, name='eliminar_compra'),
    path('compras/reporte/csv/', compra_views.exportar_compras_csv, name='exportar_compras_csv'),

    # Páginas principales
    path('', home_views.home, name='inicio'),
    path('catalog/', home_views.catalog, name='catalog'),
    path('help/', home_views.help_page, name='help'),
    path('cart/', home_views.cart, name='cart'),
    path('historial/', home_views.historial, name='historial'),
    path('error404/', home_views.error404, name='error404'),
    path('product/', home_views.product, name='product'),
    path('checkout/', home_views.checkout, name='checkout'),
    path('agregar_carrito/<int:producto_id>/', home_views.agregar_carrito, name='agregar_carrito'),
    path('disminuir_carrito/<int:producto_id>/', home_views.disminuir_carrito, name='disminuir_carrito'),
    path('eliminar_carrito/<int:producto_id>/', home_views.eliminar_carrito, name='eliminar_carrito'),


    # Dashboards
    path('dashboard/admin/', home_views.dashboard_admin, name='dashboard_admin'),
    path('seller/dashboard/', home_views.dashboard_seller, name='dashboard_seller'),
    path('cliente/dashboard/', home_views.dashboard_cliente, name='dashboard_cliente'),

    # Configuraciones
    path('configuraciones/admin/', home_views.admin_settings, name='admin_settings'),
    path('perfil/admin/', home_views.admin_perfil, name='admin_perfil'),
    path('perfil/admin/editar/', home_views.editar_perfil_admin, name='editar_perfil_admin'),
    path('categorias/admin/', categoria_views.listar_categorias_admin, name='listar_categorias_admin'),
    path('categorias/admin/crear/', categoria_views.crear_categoria_admin, name='crear_categoria_admin'),
    path('categorias/admin/<int:id>/editar/', categoria_views.editar_categoria_admin, name='editar_categoria_admin'),
    path('categorias/admin/<int:id>/eliminar/', categoria_views.eliminar_categoria_admin, name='eliminar_categoria_admin'),
    path('seller/settings/', home_views.seller_settings, name='seller_settings'),
    path('seller/panel-productos/', vendedores_views.panel_productos_vendedor, name='panel_productos_vendedor'),
    path('cliente/settings/', home_views.cliente_settings, name='cliente_settings'),
    path('cliente/perfil/', home_views.cliente_perfil, name='perfil'),
    path('cliente/perfil/editar/', home_views.editar_perfil, name='editar_perfil'),
    path('seller/perfil/', home_views.seller_perfil, name='perfil_seller'),
    path('seller/editar-perfil/', home_views.editar_perfil_seller, name='editar_perfil_seller'),
    path('seller/historial-ventas/', vendedores_views.historial_ventas_vendedor, name='historial_ventas_vendedor'),
    path('seller/marcar-enviado/<int:id_venta>/', vendedores_views.marcar_pedido_enviado, name='marcar_pedido_enviado'),


    # Personas
    path('personas/', PersonasView.as_view(), name='personas_list'),
    path('personas/<int:id>/', PersonasView.as_view(), name='personas_detail'),

    # Productos
    # Productos
    path('productos/', productos_views.productos, name='productos'),
    path('productos/crear/', productos_views.producto_create, name='producto_create'),
    path('productos/editar/<int:id>/', productos_views.producto_editar, name='producto_editar'),
    path('productos/eliminar/<int:id>/', productos_views.producto_eliminar, name='producto_eliminar'),
    path('productos/reporte/csv/', productos_views.productos_reporte_csv, name='productos_reporte_csv'),
    path('productos/reporte/pdf/', productos_views.productos_pdf, name='productos_pdf'),



    # Vendedores
    path("lista/admin/", vendedores_views.listar_vendedores, name="listar_vendedores"),
    path("create/admin/", vendedores_views.crear_vendedor, name="crear_vendedor"),
    path("show/admin/<int:id>/", vendedores_views.detalle_vendedor, name="detalle_vendedor"),
    path("edit/admin/<int:id>/", vendedores_views.editar_vendedor, name="editar_vendedor"),
    path("delete/admin/<int:id>/", vendedores_views.eliminar_vendedor, name="eliminar_vendedor"),
    path("filtro/admin/", vendedores_views.filtrar_vendedores, name="filtrar_vendedores"),
    path("reporte/admin/", vendedores_views.reporte_vendedores, name="reporte_vendedores"),
    path("reporte/admin/csv/", vendedores_views.exportar_csv, name="exportar_csv"),
    path("upload/admin/csv/", vendedores_views.cargar_csv, name="cargar_csv"),
    path("reactivar/admin/<int:id>/", vendedores_views.reactivar_vendedor, name="reactivar_vendedor"),

    # Ventas
    path("ventas/", listar_ventas, name="listar_ventas"),
    path("ventas/<int:id>/", obtener_venta, name="obtener_venta"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)