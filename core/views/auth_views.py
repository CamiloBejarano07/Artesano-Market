from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import timedelta
from core.models import Personas, Clientes, Vendedores
from core.forms import PasswordRecoveryEmailForm, SetNewPasswordForm, RegisterForm
import re
from django.conf import settings


# Generador de tokens personalizado compatible con modelo Personas
class PersonasPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """
    Generador de tokens para recuperación de contraseña del modelo Personas.
    Compatible con modelos que no heredan de AbstractBaseUser.
    """
    def _make_hash_value(self, persona, timestamp):
        """
        Genera un valor hash basado en:
        - ID del usuario
        - Contraseña hasheada
        - Timestamp
        - last_login (si existe)
        """
        # Usar password hasheado (o plain si no existe) como parte del token
        password_part = persona.password or ''
        
        # Obtener last_login de forma segura
        last_login = ''
        if hasattr(persona, 'last_login') and persona.last_login:
            last_login = str(persona.last_login)
        
        return f"{persona.id_personas}{password_part}{last_login}{timestamp}"


# Instancia del generador de tokens personalizado
token_generator = PersonasPasswordResetTokenGenerator()


# -------------------------------------
# VALIDACIONES
# -------------------------------------
def validate_email(email: str):
    """Valida que el correo contenga un signo @ y que no tenga caracteres especiales."""
    if not email or '@' not in email:
        return False, "El correo debe contener el caracter '@'."

    pattern = r'^[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]{2,}$'
    if not re.match(pattern, email):
        return False, "El correo no tiene un formato válido o contiene caracteres no permitidos."

    return True, ""


def validate_password(password: str):
    """Valida la seguridad de la contraseña."""
    if not password or len(password) < 10:
        return False, "La contraseña debe tener al menos 10 caracteres."
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una letra minúscula."
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una letra mayúscula."
    if not re.search(r'\d', password):
        return False, "Debe contener al menos un número."

    special_chars = re.findall(r'[!@#$%^&*()_+\-=[\]{}|;:\\\",.<>/?]', password)
    if len(special_chars) < 2:
        return False, "Debe contener al menos dos caracteres especiales."

    return True, ""


# -------------------------------------
# LOGIN PAGE
# -------------------------------------
def show_login_page(request):
    if request.method == 'GET':
        return render(request, 'auth/login.html', {'persona': {}})
    return redirect('login')


# -------------------------------------
# LOGIN
# -------------------------------------
@csrf_exempt
def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correoPersona')
        password = request.POST.get('password')

        try:
            user = Personas.objects.get(correo_persona=correo)
        except Personas.DoesNotExist:
            user = None

        if not user:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'auth/login.html', {'persona': {'correoPersona': correo}})

        if hasattr(user, 'estado') and user.estado.lower() == 'suspendido':
            messages.error(request, "Tu cuenta ha sido suspendida.")
            return render(request, 'auth/login.html', {'persona': {'correoPersona': correo}})

        # Verificar contraseña: preferir hash, pero aceptar texto plano antiguo y re-hashear
        password_ok = False
        try:
            if user.password and check_password(password, user.password):
                password_ok = True
            else:
                # Fallback: si la contraseña en DB está en texto plano y coincide, re-hashear
                if user.password and user.password == password:
                    user.password = make_password(password)
                    user.save()
                    password_ok = True
        except Exception:
            # En caso de cualquier error con el hasheo, intentar comparación directa (último recurso)
            if user.password and user.password == password:
                user.password = make_password(password)
                user.save()
                password_ok = True

        if password_ok:
            request.session['user_id'] = user.id_personas
            request.session['rol'] = user.rol.lower() if user.rol else 'cliente'

            rol = request.session['rol']
            print(f"ROL DETECTADO: {rol}")

            if rol in ['administrador', 'admin']:
                return redirect('dashboard_admin')
            elif rol == 'vendedor':
                return redirect('dashboard_seller')
            elif rol == 'cliente':
                return redirect('dashboard_cliente')
            else:
                return redirect('inicio')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'auth/login.html', {'persona': {'correoPersona': correo}})

    return redirect('login')


# -------------------------------------
# REGISTRO
# -------------------------------------
@csrf_exempt
def register(request):
    if request.method == 'POST':


        if not request.POST.get('acepto_terminos'):
            messages.error(request, "Debes aceptar los términos y condiciones para continuar.")
            return render(request, 'auth/login.html', {'persona': {}})
        nombre = request.POST.get('nombrePersona')
        apellido = request.POST.get('apellidoPersona')
        correo = request.POST.get('correoPersona')
        password = request.POST.get('password')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')

        if not all([nombre, apellido, correo, password, telefono, direccion]):
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'auth/login.html', {'persona': {}})

        valid_email, email_msg = validate_email(correo)
        if not valid_email:
            messages.error(request, email_msg)
            return render(request, 'auth/login.html', {'persona': {'correoPersona': correo}})

        valid_pass, pass_msg = validate_password(password)
        if not valid_pass:
            messages.error(request, pass_msg)
            return render(request, 'auth/login.html', {'persona': {'correoPersona': correo}})

        if Personas.objects.filter(correo_persona=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'auth/login.html', {'persona': {}})

        persona = Personas(
            nombre_persona=nombre,
            apellido_persona=apellido,
            correo_persona=correo,
            password=make_password(password),
            telefono=telefono,
            direccion=direccion,
            rol='cliente',
            estado='activo',
            is_superuser=False,
            is_staff=False,
            is_active=True
        )
        persona.save()

        # CREAR RELACIÓN EN TABLA CLIENTES (obligatorio para todos los usuarios del registro web)
        Clientes.objects.create(personas_id_personas=persona)

        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return render(request, 'auth/login.html', {'persona': {}})

    return redirect('login')

def terminos(request):
    return render(request, 'pages/terminos.html')


# -------------------------------------
# LOGOUT
# -------------------------------------
@csrf_exempt
def logout(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('login')


# Nota: El token_generator ya está instanciado en la sección de imports

# RECUPERACIÓN DE CONTRASEÑA - PASO 1: SOLICITAR EMAIL
# -------------------------------------
def password_recovery_request(request):
    """
    Vista para que el usuario solicite recuperación de contraseña
    Valida que el correo exista en la base de datos
    """
    if request.method == 'POST':
        form = PasswordRecoveryEmailForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            
            # Verificar si el correo existe
            try:
                persona = Personas.objects.get(correo_persona=correo)
            except Personas.DoesNotExist:
                # Por seguridad, no revelar si el correo existe o no
                messages.info(
                    request, 
                    'Si el correo existe en nuestro sistema, recibirás un enlace de recuperación en tu bandeja de entrada.'
                )
                return render(request, 'auth/password_recovery_request.html', {'form': form})
            
            # Generar token seguro usando Django
            uid = urlsafe_base64_encode(force_bytes(persona.id_personas))
            token = token_generator.make_token(persona)
            
            # Construir enlace de recuperación
            reset_link = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            
            # Enviar correo
            try:
                send_mail(
                    subject='Recuperación de Contraseña - Artesano Market',
                    message=f'''
Hola {persona.nombre_persona},

Recibimos una solicitud para recuperar tu contraseña. 
Si fuiste tú, haz clic en el siguiente enlace para restablecer tu contraseña:

{reset_link}

Este enlace es válido por 24 horas.

Si no solicitaste esta recuperación, ignora este correo.

Saludos,
El equipo de Artesano Market
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[persona.correo_persona],
                    fail_silently=False,
                )
                
                messages.success(
                    request,
                    'Se ha enviado un enlace de recuperación a tu correo. Por favor revisa tu bandeja de entrada.'
                )
                return redirect('login')
                
            except Exception as e:
                messages.error(
                    request,
                    'Error al enviar el correo. Por favor intenta de nuevo más tarde.'
                )
                print(f"Error enviando correo: {str(e)}")
                return render(request, 'auth/password_recovery_request.html', {'form': form})
    else:
        form = PasswordRecoveryEmailForm()
    
    return render(request, 'auth/password_recovery_request.html', {'form': form})


# -------------------------------------
# RECUPERACIÓN DE CONTRASEÑA - PASO 2: CONFIRMAR TOKEN Y CAMBIAR CONTRASEÑA
# -------------------------------------
def password_reset_confirm(request, uidb64, token):
    """
    Vista para validar el token y permitir al usuario establecer una nueva contraseña
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        persona = Personas.objects.get(id_personas=uid)
    except (TypeError, ValueError, OverflowError, Personas.DoesNotExist):
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return redirect('login')
    
    # Verificar que el token sea válido
    if not token_generator.check_token(persona, token):
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return redirect('password_recovery_request')
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            nueva_contraseña = form.cleaned_data['password']
            
            # Validar seguridad de la nueva contraseña
            valid_pass, pass_msg = validate_password(nueva_contraseña)
            if not valid_pass:
                messages.error(request, pass_msg)
                return render(
                    request, 
                    'auth/password_reset_confirm.html', 
                    {'form': form, 'uidb64': uidb64, 'token': token}
                )
            
            # Actualizar contraseña
            persona.password = make_password(nueva_contraseña)
            persona.save()
            
            messages.success(
                request,
                'Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión.'
            )
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'auth/password_reset_confirm.html', {'form': form, 'uidb64': uidb64, 'token': token})

