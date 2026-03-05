import webbrowser
import customtkinter as ctk
from tkinter import messagebox, filedialog
from db import *
from datetime import datetime
from fpdf import FPDF
import os

# === CONFIGURACIÓN ESTÉTICA ===
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

LILA_FONDO = "#B57EDC" 
VERDE_MENTA = "#B2D8B2" 
ROSA_VIEJO = "#D4A5A5"  
ROJO_ELIMINAR = "#E57373"

LISTA_TERAPIAS = ["Reiki", "Tarot", "Velas", "Péndulo", "Flores de Bach"]

def preparar_ventana(v):
    v.focus(); v.grab_set(); v.configure(fg_color=LILA_FONDO)

def imprimir_ficha_pdf(idc):
    try:
        d = obtener_consultante_por_id(idc)
        ses = obtener_sesiones_por_consultante(idc)
        ruta = filedialog.asksaveasfilename(initialfile=f"Ficha_{d[1]}.pdf", defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
        if not ruta: return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(200, 10, f"ARMONIA STUDIO - {d[1].upper()}", ln=True, align='C')
        pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "DATOS PERSONALES:", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"Nombre completo: {d[1]}\nTeléfono: {d[2]}\nEmail: {d[3]}\nNacimiento: {d[4]}\nMotivo: {d[5]}\nObservaciones: {d[6]}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "HISTORIAL DE SESIONES:", ln=True)
        for s in ses:
            pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, f"FECHA: {s[3]} - {s[2]}", ln=True)
            pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 6, f"Detalle: {s[4]}\nNotas: {s[5]}\nProx: {s[6]}\n" + "-"*50)
        pdf.output(ruta); messagebox.showinfo("Éxito", "Ficha guardada correctamente.")
    except Exception as e: messagebox.showerror("Error", str(e))

def descargar_respaldo_local():
    try:
        datos = obtener_consultantes()
        if not datos:
            messagebox.showwarning("Atención", "No hay datos para respaldar.")
            return
        # Guarda en la carpeta Documentos del usuario actual
        ruta_documentos = os.path.join(os.path.expanduser("~"), "Documents", "Respaldo_Armonia_2026.txt")
        with open(ruta_documentos, "w", encoding="utf-8") as f_file:
            f_file.write(f"--- RESPALDO ARMONIA STUDIO ---\n")
            f_file.write(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f_file.write("="*50 + "\n")
            for c in datos:
                f_file.write(f"CLIENTE: {c[1]}\nTEL: {c[2]}\nMAIL: {c[3]}\nMOTIVO: {c[5]}\n")
                f_file.write("-" * 30 + "\n")
        messagebox.showinfo("Éxito", f"Respaldo guardado en:\n{ruta_documentos}")
        os.startfile(os.path.join(os.path.expanduser("~"), "Documents"))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo respaldar: {str(e)}")

# --- VENTANA CONSULTANTES ---
def abrir_consultantes():
    ventana = ctk.CTkToplevel(app); ventana.title("Gestión de Consultantes"); ventana.geometry("950x800"); preparar_ventana(ventana)
    sel_id = {"id": None}
    
    # Buscador arriba de la lista
    ctk.CTkLabel(ventana, text="Buscar:", font=("Arial", 12, "bold"), text_color="white").place(x=15, y=15)
    e_busqueda = ctk.CTkEntry(ventana, width=200, placeholder_text="Nombre...")
    e_busqueda.place(x=70, y=10)

    frame_lista = ctk.CTkScrollableFrame(ventana, width=280, label_text="Consultantes (A-Z)"); frame_lista.pack(side="left", fill="y", padx=10, pady=(50, 10))
    frame_form = ctk.CTkScrollableFrame(ventana, label_text="Ficha Técnica Detallada"); frame_form.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def campo(txt, largo=False):
        ctk.CTkLabel(frame_form, text=txt, font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        e = ctk.CTkTextbox(frame_form, height=100, width=450) if largo else ctk.CTkEntry(frame_form, width=450)
        e.pack(pady=8, padx=20); return e

    e_nom = campo("Nombre y Apellido"); e_tel = campo("Teléfono de contacto")

    def enviar_wa():
        tel = e_tel.get().strip()
        if not tel: return messagebox.showwarning("Atención", "No hay teléfono.")
        tel_limpio = "".join(filter(str.isdigit, tel))
        if not tel_limpio.startswith("54"): tel_limpio = "54" + tel_limpio
        webbrowser.open(f"https://wa.me/{tel_limpio}")

    ctk.CTkButton(frame_form, text="💬 ENVIAR WHATSAPP", fg_color="#25D366", text_color="white", font=("Arial", 12, "bold"), command=enviar_wa).pack(pady=5)

    e_mail = campo("Correo Electrónico"); e_fec = campo("Nacimiento (DD-MM-AAAA)")
    e_mot = campo("Motivo inicial"); e_obs = campo("Observaciones Públicas", True); e_not = campo("Notas Privadas", True)

    def refrescar(event=None):
        filtro = e_busqueda.get().lower()
        for w in frame_lista.winfo_children(): w.destroy()
        for c in obtener_consultantes():
            if filtro in c[1].lower():
                ctk.CTkButton(frame_lista, text=f"👤 {c[1]}", fg_color="white", text_color="black", anchor="w", command=lambda x=c[0]: cargar(x)).pack(fill="x", pady=2)

    e_busqueda.bind("<KeyRelease>", refrescar)

    def cargar(idc):
        d = obtener_consultante_por_id(idc); sel_id["id"] = idc
        for e, v in zip([e_nom, e_tel, e_mail, e_fec, e_mot], [d[1], d[2], d[3], d[4], d[5]]):
            e.delete(0, "end"); e.insert(0, v if v else "")
        e_obs.delete("1.0", "end"); e_obs.insert("1.0", d[6] if d[6] else "")
        e_not.delete("1.0", "end"); e_not.insert("1.0", d[7] if d[7] else "")

    def guardar():
        if not e_nom.get(): return messagebox.showwarning("Atención", "El nombre es obligatorio")
        datos = [e_nom.get(), e_tel.get(), e_mail.get(), e_fec.get(), e_mot.get(), e_obs.get("1.0", "end-1c"), e_not.get("1.0", "end-1c")]
        if sel_id["id"]: actualizar_consultante(sel_id["id"], *datos)
        else: guardar_consultante(*datos)
        refrescar(); messagebox.showinfo("Éxito", "Guardado.")

    def borrar():
        if sel_id["id"] and messagebox.askyesno("Borrar", "¿Eliminar permanentemente?"):
            eliminar_consultante_db(sel_id["id"]); sel_id["id"] = None; refrescar()

    ctk.CTkButton(frame_form, text="GUARDAR CAMBIOS", fg_color=VERDE_MENTA, text_color="black", font=("Arial", 16, "bold"), height=45, command=guardar).pack(pady=20)
    ctk.CTkButton(frame_form, text="ELIMINAR", fg_color=ROJO_ELIMINAR, text_color="white", command=borrar).pack()
    refrescar()

# --- VENTANA SESIONES ---
def abrir_sesiones():
    ventana = ctk.CTkToplevel(app); ventana.title("Registrar Sesión"); ventana.geometry("650x750"); preparar_ventana(ventana)
    cons = obtener_consultantes(); c_dict = {c[1]: c[0] for c in cons}
    
    ctk.CTkLabel(ventana, text="Consultante:", font=("Arial", 13, "bold")).pack(pady=10)
    cb = ctk.CTkComboBox(ventana, values=list(c_dict.keys()), width=400); cb.pack()
    ctk.CTkLabel(ventana, text="Terapia Realizada:", font=("Arial", 13, "bold")).pack(pady=10)
    tp = ctk.CTkOptionMenu(ventana, values=LISTA_TERAPIAS, fg_color=ROSA_VIEJO, text_color="black", width=400); tp.pack()
    ctk.CTkLabel(ventana, text="Observación sesión:", font=("Arial", 13, "bold")).pack(pady=10)
    ob = ctk.CTkEntry(ventana, width=400); ob.pack()
    ctk.CTkLabel(ventana, text="Notas Privadas:", font=("Arial", 13, "bold")).pack(pady=10)
    nt = ctk.CTkTextbox(ventana, width=400, height=150); nt.pack()
    ctk.CTkLabel(ventana, text="Próxima Cita:", font=("Arial", 13, "bold")).pack(pady=10)
    px = ctk.CTkEntry(ventana, width=250); px.pack()

    def confirmar():
        if cb.get() in c_dict:
            if guardar_sesion(c_dict[cb.get()], tp.get(), datetime.now().strftime("%d-%m-%Y"), ob.get(), nt.get("1.0", "end-1c"), px.get()):
                messagebox.showinfo("Éxito", "Sesión registrada."); ventana.destroy()
            else: messagebox.showerror("Error", "Error al guardar.")
        else: messagebox.showwarning("Atención", "Seleccione un consultante.")

    ctk.CTkButton(ventana, text="REGISTRAR SESIÓN", fg_color=VERDE_MENTA, text_color="black", font=("Arial", 16, "bold"), height=50, command=confirmar).pack(pady=30)

# --- VENTANA HISTORIAL ---
def abrir_historial():
    ventana = ctk.CTkToplevel(app); ventana.title("Historial de Armonía"); ventana.geometry("950x850"); preparar_ventana(ventana)
    
    def mostrar(val):
        actuales = {c[1]: c[0] for c in obtener_consultantes()}
        if val not in actuales: return
        txt.delete("1.0", "end")
        idc = actuales[val]
        d = obtener_consultante_por_id(idc)
        sesiones = obtener_sesiones_por_consultante(idc)
        info = f"FICHA TÉCNICA: {d[1].upper()}\n" + "="*75 + f"\nTel: {d[2]} | Email: {d[3]}\nMotivo: {d[5]}\nObs: {d[6]}\n"
        info += "="*75 + "\nHISTORIAL DE SESIONES:\n" + "="*75 + "\n\n"
        txt.insert("end", info)
        if sesiones:
            for s in sesiones:
                txt.insert("end", f"📅 {s[3]} | ✨ {s[2]}\nOBS: {s[4]}\n🔒 NOTAS: {s[5]}\n🗓️ PROX: {s[6]}\n{'-'*65}\n")
        else: txt.insert("end", "\nNo se encontraron sesiones registradas.")

    cons = obtener_consultantes()
    cb = ctk.CTkComboBox(ventana, values=[c[1] for c in cons], width=450, command=mostrar); cb.pack(pady=20)
    txt = ctk.CTkTextbox(ventana, width=880, height=500, font=("Courier New", 12)); txt.pack(padx=20)
    
    def imprimir_actual():
        actuales = {c[1]: c[0] for c in obtener_consultantes()}
        if cb.get() in actuales: imprimir_ficha_pdf(actuales[cb.get()])

    ctk.CTkButton(ventana, text="🖨️ IMPRIMIR FICHA COMPLETA", fg_color=ROSA_VIEJO, text_color="black", font=("Arial", 15, "bold"), height=45, command=imprimir_actual).pack(pady=15)

# --- LOGIN ---
def pantalla_login():
    def registrar():
        if not em.get() or not ps.get(): return messagebox.showwarning("Atención", "Complete todos los campos.")
        exito, msg = registrar_usuario(em.get(), ps.get())
        if exito: messagebox.showinfo("Éxito", "Usuario registrado.\nYa puede iniciar sesión.")
        else: messagebox.showerror("Error", f"No se pudo registrar: {msg}")

    def log():
        mail = em.get()
        if login_usuario(mail, ps.get())[0]: 
            vl.destroy()
            sesion_label.configure(text=f"🟢 Sesión activa: {mail}")
            app.deiconify()
        else: messagebox.showerror("Error", "Acceso incorrecto.")
    
    vl = ctk.CTkToplevel(); vl.title("Acceso Armonía"); vl.geometry("450x600"); vl.configure(fg_color=LILA_FONDO); vl.attributes('-topmost', True)
    ctk.CTkLabel(vl, text="ARMONIA", font=("Arial", 45, "bold"), text_color="white").pack(pady=50)
    em = ctk.CTkEntry(vl, placeholder_text="Email", width=300, height=40); em.pack(pady=10)
    ps = ctk.CTkEntry(vl, placeholder_text="Contraseña", show="*", width=300, height=40); ps.pack(pady=10)
    
    if recuperar_sesion_guardada() and usuario_actual:
        em.insert(0, usuario_actual.email); ps.focus()

    ctk.CTkButton(vl, text="ENTRAR", fg_color=VERDE_MENTA, text_color="black", font=("Arial", 16, "bold"), width=300, height=45, command=log).pack(pady=25)
    ctk.CTkButton(vl, text="REGISTRAR NUEVA CUENTA", fg_color=ROSA_VIEJO, text_color="black", font=("Arial", 12), command=registrar).pack()

# --- CONFIGURACIÓN APP PRINCIPAL ---
app = ctk.CTk(); app.withdraw(); app.title("Armonía - Reiki a Distancia")
app.geometry("1000x800"); app.configure(fg_color=LILA_FONDO)

# 1. EL TÍTULO (Arriba de todo)
ctk.CTkLabel(app, text="ARMONIA", font=("Arial", 80, "bold"), text_color="white").pack(pady=(30, 0))
ctk.CTkLabel(app, text="Reiki a distancia", font=("Arial", 22, "italic"), text_color="white").pack(pady=(0, 10))

# 2. EL FOOTER BLANCO (Lo empaquetamos PRIMERO como bottom para que sea el piso)
footer_frame = ctk.CTkFrame(app, height=60, fg_color="white", corner_radius=0)
footer_frame.pack(side="bottom", fill="x")
footer_frame.pack_propagate(False) 

ctk.CTkLabel(footer_frame, 
             text="Desarrollado por Solange Blanc - Todos los derechos reservados 2026", 
             font=("Arial", 12, "bold"), 
             text_color="black").pack(expand=True)

# 3. LA SESIÓN ACTIVA (Se apoya ARRIBA del footer blanco)
sesion_label = ctk.CTkLabel(app, text="Inicie sesión para comenzar", font=("Arial", 13, "bold"), text_color="white")
sesion_label.pack(side="bottom", pady=(10, 5))

# 4. LOS BOTONES (Ocupan el centro restante)
f = ctk.CTkFrame(app, fg_color="transparent")
f.pack(expand=True)

btn_conf = {"width": 450, "height": 60, "font": ("Arial", 16, "bold"), "text_color": "black"}

ctk.CTkButton(f, text="📁 GESTIÓN DE CONSULTANTES", fg_color=VERDE_MENTA, command=abrir_consultantes, **btn_conf).pack(pady=8)
ctk.CTkButton(f, text="✨ REGISTRAR SESIÓN", fg_color=VERDE_MENTA, command=abrir_sesiones, **btn_conf).pack(pady=8)
ctk.CTkButton(f, text="📜 HISTORIAL E IMPRESIÓN", fg_color=VERDE_MENTA, command=abrir_historial, **btn_conf).pack(pady=8)
ctk.CTkButton(f, text="📥 DESCARGAR BACKUP LOCAL", fg_color="gray", command=descargar_respaldo_local, **btn_conf).pack(pady=8)

app.after(300, pantalla_login)
app.mainloop()