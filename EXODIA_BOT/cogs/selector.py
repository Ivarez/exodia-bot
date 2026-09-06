import discord
from discord.ext import commands
import sqlite3
import os

class SelectorOrigen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 1. ROL POLIZÓN 
        self.ROL_POLIZON_ID = 1449866937915150346
        
        # 2. ROL DE ESTATUS 
        self.ROL_CIUDADANO_ID = 1451051356621242430
        
        # 3. ROLES DE CLASE 
        self.ROL_ENLAZADO_ID = 1449869112116252763
        self.ROL_MUTADO_ID = 1449869077144273087
        self.ROL_VIDENTE_ID = 1449868922038779974

        # 4. ROLES DE NOTIFICACIONES
        self.ROL_LUDICA_ID = 1450899057169141843
        self.ROL_PRIORIDAD_ID = 1450899036008743024
        self.ROL_RECURSOS_ID = 1450894542680227870
        
        # Asegurar Directorio DB
        if not os.path.exists("database"):
            os.makedirs("database")
        self.db_path = "database/usuarios.db"

        # --- 🛡️ SEGURIDAD: INICIAR DB ---
        self.init_db()

        # --- 🔥 PERSISTENCIA (Vital para que no mueran los botones) ---
        self.bot.add_view(NotificacionesView(self))
        self.bot.add_view(OrigenView(self))

    def init_db(self):
        """Crea la tabla si no existe para evitar errores"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    user_id INTEGER PRIMARY KEY, 
                    xp INTEGER DEFAULT 0, 
                    nivel INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error inicializando DB en Selector: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_origen(self, ctx):
        """Despliega los paneles de selección"""
        await ctx.message.delete()
        
        # --- MENSAJE 1: NOTIFICACIONES ---
        embed_notif = discord.Embed(
            title="📡 FRECUENCIAS DE ENLACE",
            description="Configura los canales de información que deseas recibir en tu implante neural.\n"
                        "Puedes activar o desactivar estas frecuencias en cualquier momento.",
            color=0x00FFFF
        )
        embed_notif.add_field(
            name="Canales Disponibles",
            value="🎭 **Sincronía Lúdica:** Juegos, Turing y eventos sociales.\n"
                  "📡 **Frecuencia Prioritaria:** Anuncios vitales de la estación.\n"
                  "📦 **Reasignación de Recursos:** Sorteos y suministros.",
            inline=False
        )
        view_notif = NotificacionesView(self)
        await ctx.send(embed=embed_notif, view=view_notif)
        
        # --- MENSAJE 2: ORIGEN (CLASES) ---
        embed_origen = discord.Embed(
            title="🧬 PROTOCOLO DE ORIGEN",
            description="**ACCESO RESTRINGIDO:** Solo personal de Nivel 1+.\n\n"
                        "Si has sobrevivido lo suficiente para dejar de ser un Polizón, "
                        "el Sistema te permite elegir tu dogma y oficializar tu estatus.\n\n"
                        "🔵 **ENLAZADO:** La salvación reside en el código eterno.\n"
                        "🟠 **MUTADO:** La salvación es la evolución de la carne.\n"
                        "🟣 **VIDENTE:** La salvación es el control de la información.",
            color=0xFFFFFF
        )
        embed_origen.set_footer(text="⚠️ Si eres Nivel 0, el sistema rechazará tu solicitud.")
        view_origen = OrigenView(self)
        await ctx.send(embed=embed_origen, view=view_origen)


# --- VISTA 1: NOTIFICACIONES ---
class NotificacionesView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.select(
        placeholder="📡 Ajustar Frecuencias y notificaciones...",
        min_values=0, 
        max_values=3,
        custom_id="sel_notif_persistent",
        options=[
            discord.SelectOption(label="Sincronía Lúdica", description="Juegos y Entretenimiento", emoji="🎭", value="ludica"),
            discord.SelectOption(label="Frecuencia Prioritaria", description="Anuncios Importantes", emoji="📡", value="prioridad"),
            discord.SelectOption(label="Reasignación de Recursos", description="Sorteos", emoji="📦", value="recursos")
        ]
    )
    async def notif_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # Usamos defer aquí también para consistencia
        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        guild = interaction.guild
        
        mapa_roles = {
            "ludica": self.cog.ROL_LUDICA_ID,
            "prioridad": self.cog.ROL_PRIORIDAD_ID,
            "recursos": self.cog.ROL_RECURSOS_ID
        }
        
        roles_agregados = []
        roles_quitados = []
        seleccionados = select.values

        for key, role_id in mapa_roles.items():
            if role_id == 0: continue
            role = guild.get_role(role_id)
            if not role: continue

            try:
                if key in seleccionados:
                    if role not in user.roles:
                        await user.add_roles(role)
                        roles_agregados.append(role.name)
                else:
                    if role in user.roles:
                        await user.remove_roles(role)
                        roles_quitados.append(role.name)
            except discord.Forbidden:
                await interaction.followup.send(f"🚫 **ERROR DE PERMISOS:** No puedo gestionar el rol {role.name}.", ephemeral=True)
                return

        msj = "✅ **Configuración actualizada.**"
        if roles_agregados: msj += f"\n📥 Activado: {', '.join(roles_agregados)}"
        if roles_quitados: msj += f"\n📤 Desactivado: {', '.join(roles_quitados)}"
        if not roles_agregados and not roles_quitados: msj = "✅ **Sincronización estable.**"

        await interaction.followup.send(msj, ephemeral=True)


# --- VISTA 2: ORIGEN (BLINDADA CON DEFER Y CHECK DE ROLES) ---
class OrigenView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.select(
        placeholder="Inicializar Protocolo de Origen...",
        min_values=1,
        max_values=1,
        custom_id="selector_origen_persistent", 
        options=[
            discord.SelectOption(label="El Enlazado", description="Rama Silicio", emoji="🔵", value="enlazado"),
            discord.SelectOption(label="El Mutado", description="Rama Cromo", emoji="🟠", value="mutado"),
            discord.SelectOption(label="El Vidente", description="Rama Psiqué", emoji="🟣", value="vidente")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # ⏳ 1. ANTI-SPAM (DEFER)
        # Esto avisa a Discord que estamos procesando.
        # A partir de aquí usamos 'interaction.followup.send' en vez de 'response.send_message'
        await interaction.response.defer(ephemeral=True)
        
        user = interaction.user
        guild = interaction.guild
        
        # 🛡️ 2. VALIDACIÓN DE EXISTENCIA DE ROL (Evita Crash)
        ciudadano_rol = guild.get_role(self.cog.ROL_CIUDADANO_ID)
        
        if ciudadano_rol is None:
            await interaction.followup.send("❌ **ERROR CRÍTICO:** El rol 'Ciudadano' no existe o fue borrado. Contacta al Admin.", ephemeral=True)
            return

        # 🔒 3. CANDADO DE CIUDADANÍA
        if ciudadano_rol in user.roles:
            await interaction.followup.send(
                f"⛔ **ACCESO DENEGADO:** Ya estás registrado en el sistema.\n"
                f"Estatus actual: **{ciudadano_rol.name}**\n"
                f"*No puedes cambiar tu origen una vez establecido.*",
                ephemeral=True
            )
            return

        # 4. VERIFICACIÓN DE NIVEL
        conn = sqlite3.connect(self.cog.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT nivel FROM usuarios WHERE user_id = ?', (user.id,))
        result = cursor.fetchone()
        conn.close()

        nivel_actual = result[0] if result else 0

        # SI ES NIVEL 0 -> RECHAZAR
        if nivel_actual < 1:
            await interaction.followup.send(
                f"⛔ **ACCESO DENEGADO.**\nIdentidad: {user.mention}\nNivel Actual: `{nivel_actual}`\nRequisito: `Nivel 1`\n\n*Interactúa en la estación para ganar experiencia y dejar de ser un Polizón.*", 
                ephemeral=True
            )
            return

        # 5. PROCESAR ELECCIÓN
        polizon_rol = guild.get_role(self.cog.ROL_POLIZON_ID)
        nuevo_rol_clase = None
        
        opcion = select.values[0]
        if opcion == "enlazado": nuevo_rol_clase = guild.get_role(self.cog.ROL_ENLAZADO_ID)
        elif opcion == "mutado": nuevo_rol_clase = guild.get_role(self.cog.ROL_MUTADO_ID)
        elif opcion == "vidente": nuevo_rol_clase = guild.get_role(self.cog.ROL_VIDENTE_ID)

        if nuevo_rol_clase:
            try:
                # A. Dar el rol de CLASE
                if nuevo_rol_clase not in user.roles:
                    await user.add_roles(nuevo_rol_clase)
                
                # B. Dar el rol de CIUDADANO (Esto activará el candado futuro)
                if ciudadano_rol not in user.roles:
                    await user.add_roles(ciudadano_rol)

                # C. Quitar Polizón
                if polizon_rol and polizon_rol in user.roles:
                    await user.remove_roles(polizon_rol)
                    
                estatus_texto = ciudadano_rol.name
                
                await interaction.followup.send(
                    f"✅ **IDENTIDAD CONFIRMADA.**\n"
                    f"Bienvenido a la ciudadanía, {user.mention}.\n"
                    f"Nuevo Estatus: **{estatus_texto}**\n"
                    f"Dogma: **{nuevo_rol_clase.name}**", 
                    ephemeral=True
                )

            except discord.Forbidden:
                 await interaction.followup.send(
                    f"🚫 **ERROR CRÍTICO DE PERMISOS:** No tengo autoridad para asignarte roles.\n"
                    "⚠️ **SOLUCIÓN PARA EL ADMIN:** Mueve el rol de 'Exodus' **ARRIBA** de los roles de Ciudadano y Clases en la lista del servidor.", 
                    ephemeral=True
                )
        else:
            await interaction.followup.send("❌ Error crítico: Rol de clase no encontrado en la configuración.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SelectorOrigen(bot))