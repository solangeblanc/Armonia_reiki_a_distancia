import json
import os
from supabase import create_client, Client

# === CREDENCIALES ===
URL = "https://jixxwasttotavpenmlho.supabase.co"
KEY = "sb_publishable_7YVSjE0JQlNkOSeb1MCRMw_Ygqpwl_G"

supabase: Client = create_client(URL, KEY)
usuario_actual = None
SESSION_FILE = "session.json"

def guardar_sesion_local(session):
    with open(SESSION_FILE, "w") as f: json.dump(session, f)

def recuperar_sesion_guardada():
    global usuario_actual
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                res = supabase.auth.set_session(data['access_token'], data['refresh_token'])
                usuario_actual = res.user
                return True
        except: return False
    return False

def registrar_usuario(email, password):
    try:
        supabase.auth.sign_up({"email": email, "password": password})
        return True, "Cuenta creada con éxito."
    except Exception as e: return False, str(e)

def login_usuario(email, password):
    global usuario_actual
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        usuario_actual = res.user
        guardar_sesion_local({"access_token": res.session.access_token, "refresh_token": res.session.refresh_token})
        return True, "Entrando..."
    except Exception as e: return False, "Error de acceso"

# --- GESTIÓN DE CONSULTANTES (FILTRADO POR USUARIO) ---
def guardar_consultante(nombre, tel, email, fecha, motivo, obs, notas):
    data = {
        "user_id": usuario_actual.id, 
        "nombre": nombre, "telefono": tel, "email": email, 
        "fecha_nacimiento": fecha, "motivo": motivo, 
        "observaciones": obs, "notas_privadas": notas
    }
    supabase.table("consultantes").insert(data).execute()

def obtener_consultantes():
    # Solo trae los que pertenecen al usuario logueado
    res = supabase.table("consultantes").select("*").eq("user_id", usuario_actual.id).order("nombre").execute()
    return [[
        c.get('id'), c.get('nombre', ''), c.get('telefono', ''), 
        c.get('email', ''), c.get('fecha_nacimiento', ''), 
        c.get('motivo', ''), c.get('observaciones', ''), c.get('notas_privadas', '')
    ] for c in res.data]

def obtener_consultante_por_id(idc):
    res = supabase.table("consultantes").select("*").eq("id", idc).eq("user_id", usuario_actual.id).single().execute()
    c = res.data
    return [
        c.get('id'), c.get('nombre', ''), c.get('telefono', ''), 
        c.get('email', ''), c.get('fecha_nacimiento', ''), 
        c.get('motivo', ''), c.get('observaciones', ''), c.get('notas_privadas', '')
    ]

def actualizar_consultante(idc, nombre, tel, email, fecha, motivo, obs, notas):
    data = {
        "nombre": nombre, "telefono": tel, "email": email, 
        "fecha_nacimiento": fecha, "motivo": motivo, 
        "observaciones": obs, "notas_privadas": notas
    }
    supabase.table("consultantes").update(data).eq("id", idc).eq("user_id", usuario_actual.id).execute()

def eliminar_consultante_db(idc):
    supabase.table("consultantes").delete().eq("id", idc).eq("user_id", usuario_actual.id).execute()

# --- GESTIÓN DE SESIONES (FILTRADO POR USUARIO) ---
def guardar_sesion(idc, terapia, inicio, obs, notas_p, prox):
    try:
        data = {
            "user_id": usuario_actual.id, 
            "consultante_id": idc, 
            "terapia": terapia, 
            "fecha_inicio": inicio, 
            "observaciones": obs, 
            "notas_privadas": notas_p,
            "proxima_sesion": prox
        }
        supabase.table("sesiones").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def obtener_sesiones_por_consultante(idc):
    try:
        # Doble filtro: por consultante y por dueño de la sesión
        res = supabase.table("sesiones").select("*").eq("consultante_id", idc).eq("user_id", usuario_actual.id).order("created_at", desc=True).execute()
        return [[
            s.get('id'), s.get('consultante_id'), s.get('terapia', 'N/A'),
            s.get('fecha_inicio', ''), s.get('observaciones') or "",
            s.get('notas_privadas') or "Sin notas", s.get('proxima_sesion') or ""
        ] for s in res.data]
    except: return []