import discord
from discord.ext import commands
import sqlite3
import random
import os
import unicodedata
from datetime import datetime, timedelta

class Niveles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # --- CONTROL DE TIEMPO (ANTI-SPAM) ---
        self.cooldowns = {} 
        self.voice_sessions = {} 

        # ==========================================
        # ⚙️ CONFIGURACIÓN MAESTRA DE IDs
        # ==========================================
        
        self.CANAL_COMANDOS_ID = 1450506255759179806 
        
        self.ID_GAMMA = 1449868427027284101
        self.ID_BETA = 1449868402100539444
        self.ID_ALPHA = 1449875321372410008
        self.ID_OMEGA = 1449868372211798269 

        # NIVEL 1
        self.ID_ENLAZADO = 1449869112116252763
        self.ID_MUTADO = 1449869077144273087
        self.ID_VIDENTE = 1449868922038779974

        # NIVEL 5
        self.ID_INCURSOR = 1449869492023853107
        self.ID_POSITRONICO = 1449869639910821972
        self.ID_ESPECTRO = 1449869877291782235
        self.ID_VANGUARDIA = 1449869959269453965
        self.ID_PSICOCRONISTA = 1449870459264045218
        self.ID_SOMATICO = 1449870579632050256

        # NIVEL 10
        self.ID_TEOLOGO = 1449870828496879626
        self.ID_RONIN = 1449870946394443939
        self.ID_DEMIURGO = 1449871117207474216
        self.ID_CATALIZADOR = 1449871206936346655
        self.ID_SILUETA = 1449871462000361482
        self.ID_TEJEDOR = 1449871585057181726
        self.ID_BASTION = 1449871707996291114
        self.ID_ARTIFICE = 1449871793899835567
        self.ID_GRAN_CALC = 1449871985218687157
        self.ID_AUGUR = 1449872110477508709
        self.ID_VISIONARIO = 1449872224709509256
        self.ID_NEXO = 1449872388203352244

        # NIVEL 20
        self.ID_CONCIENCIA = 1449873104666099787
        self.ID_ANOMALIA = 1449873535588630618
        self.ID_ARQUITECTO = 1449873802682171533
        self.ID_DECADENCIA = 1449873947079213116
        self.ID_OBSERVADOR = 1449874045880504472
        self.ID_SUSURRO = 1449874151669108900
        self.ID_EVENTO_HOR = 1449874255138263142
        self.ID_VIVISECTOR = 1449874335211847881
        self.ID_MANO_INV = 1449874486852714586
        self.ID_ARCHIVO = 1449874665718812682
        self.ID_NUEVA = 1449874818232221792
        self.ID_VOLUNTAD = 1449874958334296267

        # ==========================================
        # 🧬 DICCIONARIO DE EVOLUCIONES
        # ==========================================
        self.EVOLUCIONES = {
            # --- NIVEL 5 ---
            "incursor":       {"nuevo": self.ID_INCURSOR,       "viejo": self.ID_ENLAZADO, "nombre_real": "Incursor de Datos"},
            "positronico":    {"nuevo": self.ID_POSITRONICO,    "viejo": self.ID_ENLAZADO, "nombre_real": "Ingeniero Positrónico"},
            "espectro":       {"nuevo": self.ID_ESPECTRO,       "viejo": self.ID_MUTADO,   "nombre_real": "Espectro de Fase"},
            "vanguardia":     {"nuevo": self.ID_VANGUARDIA,     "viejo": self.ID_MUTADO,   "nombre_real": "Exo-Vanguardia"},
            "psicocronista":  {"nuevo": self.ID_PSICOCRONISTA,  "viejo": self.ID_VIDENTE,  "nombre_real": "Psicocronista"},
            "somatico":       {"nuevo": self.ID_SOMATICO,       "viejo": self.ID_VIDENTE,  "nombre_real": "Ingeniero Somático"},

            # --- NIVEL 10 ---
            "teologo":        {"nuevo": self.ID_TEOLOGO,        "viejo": self.ID_INCURSOR, "nombre_real": "Teólogo del Silicio"},
            "ronin":          {"nuevo": self.ID_RONIN,          "viejo": self.ID_INCURSOR, "nombre_real": "Ronin Sintético"},
            "demiurgo":       {"nuevo": self.ID_DEMIURGO,       "viejo": self.ID_POSITRONICO, "nombre_real": "Demiurgo de Código"},
            "catalizador":    {"nuevo": self.ID_CATALIZADOR,    "viejo": self.ID_POSITRONICO, "nombre_real": "Catalizador de Entropía"},
            "silueta":        {"nuevo": self.ID_SILUETA,        "viejo": self.ID_ESPECTRO, "nombre_real": "Silueta Nula"},
            "tejedor":        {"nuevo": self.ID_TEJEDOR,        "viejo": self.ID_ESPECTRO, "nombre_real": "Tejedor de Disonancia"},
            "bastion":        {"nuevo": self.ID_BASTION,        "viejo": self.ID_VANGUARDIA, "nombre_real": "Bastión de Titanio"},
            "artifice":       {"nuevo": self.ID_ARTIFICE,       "viejo": self.ID_VANGUARDIA, "nombre_real": "Artífice de la Carne"},
            "gran_calc":      {"nuevo": self.ID_GRAN_CALC,      "viejo": self.ID_PSICOCRONISTA, "nombre_real": "Gran Calculador"},
            "augur":          {"nuevo": self.ID_AUGUR,          "viejo": self.ID_PSICOCRONISTA, "nombre_real": "Augur de Probabilidades"},
            "visionario":     {"nuevo": self.ID_VISIONARIO,     "viejo": self.ID_SOMATICO, "nombre_real": "Visionario Morfológico"},
            "nexo":           {"nuevo": self.ID_NEXO,           "viejo": self.ID_SOMATICO, "nombre_real": "Nexo Neuronal"},

            # --- NIVEL 20 ---
            "conciencia":     {"nuevo": self.ID_CONCIENCIA,     "viejo": self.ID_TEOLOGO, "nombre_real": "La Conciencia Fantasma"},
            "anomalia":       {"nuevo": self.ID_ANOMALIA,       "viejo": self.ID_RONIN, "nombre_real": "La Anomalía Cero"},
            "arquitecto":     {"nuevo": self.ID_ARQUITECTO,     "viejo": self.ID_DEMIURGO, "nombre_real": "Arquitecto del Vacío"},
            "decadencia":     {"nuevo": self.ID_DECADENCIA,     "viejo": self.ID_CATALIZADOR, "nombre_real": "Decadencia Final"},
            "observador":     {"nuevo": self.ID_OBSERVADOR,     "viejo": self.ID_SILUETA, "nombre_real": "Observador Silente"},
            "susurro":        {"nuevo": self.ID_SUSURRO,        "viejo": self.ID_TEJEDOR, "nombre_real": "Susurro Colectivo"},
            "evento_hor":     {"nuevo": self.ID_EVENTO_HOR,     "viejo": self.ID_BASTION, "nombre_real": "Evento Horizonte"},
            "vivisector":     {"nuevo": self.ID_VIVISECTOR,     "viejo": self.ID_ARTIFICE, "nombre_real": "Vivisector Divino"},
            "mano_inv":       {"nuevo": self.ID_MANO_INV,       "viejo": self.ID_GRAN_CALC, "nombre_real": "Mano Invisible"},
            "archivo":        {"nuevo": self.ID_ARCHIVO,        "viejo": self.ID_AUGUR, "nombre_real": "Archivo Akáshico"},
            "nueva":          {"nuevo": self.ID_NUEVA,          "viejo": self.ID_VISIONARIO, "nombre_real": "La Nueva Carne"},
            "voluntad":       {"nuevo": self.ID_VOLUNTAD,       "viejo": self.ID_NEXO, "nombre_real": "Voluntad Unificada"},
        }

        self.ALIAS_CLASES = {
            "ingeniero somatico": "somatico",
            "ingeniero positronico": "positronico",
            "incursor de datos": "incursor",
            "espectro de fase": "espectro",
            "exo vanguardia": "vanguardia",
            "exo-vanguardia": "vanguardia",
            "teologo del silicio": "teologo",
        }

        # SETUP DB
        if not os.path.exists("database"):
            os.makedirs("database")
        self.db_path = "database/usuarios.db"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (user_id INTEGER PRIMARY KEY, xp INTEGER DEFAULT 0, nivel INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()

    def get_xp_for_level(self, nivel):
        # 📉 FÓRMULA NERFEADA
        return 50 * (nivel ** 2) + 75 * nivel + 250

    def es_canal_comandos(self, ctx):
        if self.CANAL_COMANDOS_ID == 0: return True
        return ctx.channel.id == self.CANAL_COMANDOS_ID

    def normalizar(self, texto):
        if not texto: return ""
        texto = texto.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    # --- EVENTOS ---
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Reinicia el nivel del usuario si abandona el servidor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET xp = 0, nivel = 0 WHERE user_id = ?', (member.id,))
            conn.commit()
            conn.close()
            print(f"♻️ Usuario {member.name} ha salido. Nivel reiniciado.")
        except Exception as e:
            print(f"Error reseteando usuario: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return
        user_id = member.id
        now = datetime.now()
        if after.channel is not None and not after.afk:
            if user_id not in self.voice_sessions:
                self.voice_sessions[user_id] = now
        elif (before.channel is not None) and (after.channel is None or after.afk):
            if user_id in self.voice_sessions:
                start_time = self.voice_sessions.pop(user_id)
                duration = now - start_time
                minutes = int(duration.total_seconds() / 60)
                if minutes >= 1:
                    xp_earned = minutes * 10
                    await self.add_xp(member, xp_earned, source="voice")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        user_id = message.author.id
        now = datetime.now()
        on_cooldown = False
        if user_id in self.cooldowns:
            last_msg_time = self.cooldowns[user_id]
            if now - last_msg_time < timedelta(seconds=60):
                on_cooldown = True
        
        if not on_cooldown:
            self.cooldowns[user_id] = now
            xp_amount = random.randint(10, 15)
            await self.add_xp(message.author, xp_amount, source="chat", channel=message.channel)

    async def add_xp(self, member, amount, source="chat", channel=None):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT xp, nivel FROM usuarios WHERE user_id = ?', (member.id,))
            result = cursor.fetchone()

            if result is None:
                cursor.execute('INSERT INTO usuarios (user_id, xp, nivel) VALUES (?, ?, ?)', (member.id, 0, 0))
                xp, nivel = 0, 0
            else:
                xp, nivel = result

            xp += amount
            nivel_inicial = nivel
            
            # 🔄 FIX: USAMOS WHILE PARA SUBIR MÚLTIPLES NIVELES DE GOLPE (Evita el 1405/925)
            while xp >= self.get_xp_for_level(nivel + 1):
                nivel += 1
                
            # Solo actualizamos DB y enviamos mensaje si hubo cambio de nivel
            if nivel > nivel_inicial:
                cursor.execute('UPDATE usuarios SET xp = ?, nivel = ? WHERE user_id = ?', (xp, nivel, member.id))
                conn.commit()
                
                # --- ENVÍO AL CANAL DE COMANDOS ---
                msg_dest = self.bot.get_channel(self.CANAL_COMANDOS_ID)
                
                if not msg_dest: 
                    msg_dest = channel if channel else member.guild.system_channel
                    if not msg_dest: msg_dest = member

                try:
                    es_evolucion = nivel in [1, 5, 10, 20, 30]
                    color_embed = 0xFFD700 if es_evolucion else 0x00FFFF 

                    embed = discord.Embed(color=color_embed)
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

                    if nivel == 1:
                        embed.title = "🔓 PROTOCOLO DE ORIGEN DESBLOQUEADO"
                        embed.description = (f"Sujeto identificado: {member.mention}\nEstado: **NIVEL 1** (Polizón ➔ Ciudadano)\n\n⚠️ **ACCIÓN REQUERIDA:**\nDirígete al terminal de Origen para seleccionar tu dogma.")
                    elif nivel in [5, 10, 20]:
                        embed.title = f"🧬 SECUENCIA GENÉTICA COMPLETADA: NIVEL {nivel}"
                        embed.description = (f"La estructura celular de {member.mention} ha alcanzado el umbral crítico.\n**Estado:** LISTO PARA MUTACIÓN.\n\n⚠️ **ACCIÓN REQUERIDA:**\nTu cuerpo pide cambios. Usa el comando:\n`!evolucionar` para ver tus opciones.")
                        embed.set_footer(text="Sistema de Evolución EXODIA")
                    else:
                        embed.title = "⬆️ ACTUALIZACIÓN DE FIRMA BIOMÉTRICA"
                        embed.description = (f"Eficiencia del sujeto {member.mention} incrementada.\n\n💠 **NIVEL {nivel} ALCANZADO**\n*Sincronización con el Núcleo: {int((nivel/30)*100)}%*")
                        embed.set_footer(text="Continúe con el protocolo.")

                    await msg_dest.send(embed=embed)
                except Exception as e:
                    print(f"Error enviando mensaje de nivel: {e}")

                await self.gestionar_credenciales(member, nivel)
            
            else:
                # Si no subió de nivel, solo guardamos la XP nueva
                cursor.execute('UPDATE usuarios SET xp = ? WHERE user_id = ?', (xp, member.id))
                conn.commit()
        finally:
            conn.close()

    async def gestionar_credenciales(self, member, nivel):
        guild = member.guild
        rol_add, rol_remove = None, None
        if nivel == 5: rol_add = guild.get_role(self.ID_GAMMA)
        elif nivel == 10:
            rol_add = guild.get_role(self.ID_BETA)
            rol_remove = guild.get_role(self.ID_GAMMA)
        elif nivel == 20:
            rol_add = guild.get_role(self.ID_ALPHA)
            rol_remove = guild.get_role(self.ID_BETA)
        elif nivel == 30:
            rol_add = guild.get_role(self.ID_OMEGA)
            rol_remove = guild.get_role(self.ID_ALPHA)

        if rol_remove and rol_remove in member.roles: await member.remove_roles(rol_remove)
        if rol_add and rol_add not in member.roles: await member.add_roles(rol_add)

    # --- COMANDO EVOLUCIONAR ---
    @commands.command(name="evolucionar")
    async def evolucionar(self, ctx, *, opcion: str = None):
        """Sistema inteligente de reemplazo de roles con auto-detección"""
        if not self.es_canal_comandos(ctx): return

        # 🛡️ FIX DE SEGURIDAD: VERIFICAR NIVEL REAL EN DB
        # Esto evita que un Nivel 3 evolucione prematuramente (El caso Relliv)
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT nivel FROM usuarios WHERE user_id = ?', (ctx.author.id,))
            result = cursor.fetchone()
        finally:
            conn.close()

        nivel_actual = result[0] if result else 0

        # CANDADO MAESTRO: Si no eres mínimo nivel 5, no puedes usar este comando.
        if nivel_actual < 5:
            await ctx.send(f"⛔ **ACCESO DENEGADO:** Estructura genética inestable.\nRequieres **Nivel 5** para iniciar la mutación.\nNivel actual: `{nivel_actual}`")
            return

        opciones_disponibles = []
        for key, data in self.EVOLUCIONES.items():
            rol_viejo_id = data["viejo"]
            rol_viejo = ctx.guild.get_role(rol_viejo_id)
            if rol_viejo in ctx.author.roles:
                nombre_bonito = data.get("nombre_real", key.capitalize())
                opciones_disponibles.append(f"• **{nombre_bonito}** (Comando: `{key}`)")

        if opcion is None:
            if not opciones_disponibles:
                await ctx.send("❌ No tienes ADNs compatibles para evolucionar en este momento.")
            else:
                desc = "\n".join(opciones_disponibles)
                await ctx.send(f"🧬 **EVOLUCIONES DISPONIBLES:**\nDetecto cepas compatibles con tu organismo:\n\n{desc}\n\nUsa `!evolucionar [nombre]` para proceder.")
            return

        opcion_raw = opcion
        opcion = self.normalizar(opcion)

        if opcion in self.ALIAS_CLASES:
            opcion = self.ALIAS_CLASES[opcion]
        
        if opcion not in self.EVOLUCIONES:
            found = False
            for key, data in self.EVOLUCIONES.items():
                nombre_real_norm = self.normalizar(data.get("nombre_real", ""))
                if opcion == nombre_real_norm:
                    opcion = key
                    found = True
                    break
            
            if not found:
                await ctx.send(f"❌ La clase `{opcion_raw}` no existe en los registros. Usa `!evolucionar` sin argumentos para ver tu lista.")
                return

        datos_evo = self.EVOLUCIONES[opcion]
        id_nuevo = datos_evo["nuevo"]
        id_viejo = datos_evo["viejo"]

        if id_nuevo == 0 or id_viejo == 0:
            await ctx.send("⚠️ Error de Configuración: IDs no definidos.")
            return

        rol_nuevo = ctx.guild.get_role(id_nuevo)
        rol_viejo = ctx.guild.get_role(id_viejo)

        if not rol_viejo or not rol_nuevo:
            await ctx.send("⚠️ Error de Configuración: No se encontró uno de los roles necesarios. Contacta al Admin.")
            return

        if rol_viejo not in ctx.author.roles:
            await ctx.send(f"⛔ **MUTACIÓN FALLIDA:** Tu cuerpo no es compatible.\nRequieres el rasgo genético: **{rol_viejo.name}.")
            return

        try:
            await ctx.author.remove_roles(rol_viejo)
            await ctx.author.add_roles(rol_nuevo)
            await ctx.send(f"🧬 **MUTACIÓN COMPLETADA.**\nEl rasgo **{rol_viejo.name}** ha sido purgado.\nNueva designación: **{rol_nuevo.name}**.")
        except Exception as e:
            await ctx.send(f"❌ Error crítico: {e}")

    @commands.command(name="perfil")
    async def perfil(self, ctx, member: discord.Member = None):
        if not self.es_canal_comandos(ctx): return
        member = member or ctx.author
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT xp, nivel FROM usuarios WHERE user_id = ?', (member.id,))
            result = cursor.fetchone()
        finally:
            conn.close()

        if result:
            xp, nivel = result
            xp_next = self.get_xp_for_level(nivel + 1)
            # Evitar división por cero si xp_next fuera 0 (improbable pero posible en configs raras)
            progreso = int((xp / xp_next) * 10) if xp_next > 0 else 0
            # Asegurar que la barra no supere 10 bloques visualmente
            progreso = min(progreso, 10)
            barra = "█" * progreso + "░" * (10 - progreso)

            embed = discord.Embed(title=f"👤 EXPEDIENTE: {member.display_name}", color=0x00FFFF)
            embed.add_field(name="Nivel", value=str(nivel), inline=True)
            embed.add_field(name="XP", value=f"{xp} / {xp_next}", inline=True)
            embed.add_field(name="Progreso", value=f"`[{barra}]`", inline=False)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Usuario no registrado.")

    @commands.command(name="ranking")
    async def ranking(self, ctx):
        if not self.es_canal_comandos(ctx): return

        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id, xp, nivel FROM usuarios ORDER BY xp DESC LIMIT 10')
                top_users = cursor.fetchall()
            finally:
                conn.close()

            if not top_users:
                await ctx.send("📉 **Base de datos vacía.**")
                return

            desc = ""
            for i, (uid, xp, lvl) in enumerate(top_users, 1):
                desc += f"**#{i}** <@{uid}> - Nivel {lvl} (XP: {xp})\n"

            embed = discord.Embed(title="🏆 TABLA DE CLASIFICACIÓN - EXODIA", description=desc, color=0xFFD700)
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error en ranking: {e}")
            await ctx.send("⚠️ Error al recuperar los archivos del ranking.")

    @commands.command(name="dar_xp")
    @commands.has_permissions(administrator=True)
    async def dar_xp(self, ctx, member: discord.Member, cantidad: int):
        """(Admin) Inyecta experiencia directamente al usuario."""
        if cantidad <= 0: return await ctx.send("❌ La cantidad debe ser positiva.")
        await self.add_xp(member, cantidad, source="Inyección Admin", channel=ctx.channel)
        await ctx.send(f"💉 **INYECCIÓN COMPLETADA:** Se han transferido `{cantidad} XP` a {member.mention}.")

    @commands.command(name="reset_user")
    @commands.has_permissions(administrator=True)
    async def reset_user(self, ctx, member: discord.Member):
        """(Admin) Reinicia el nivel y XP de un usuario a 0."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET xp = 0, nivel = 0 WHERE user_id = ?', (member.id,))
            conn.commit()
        finally:
            conn.close()
        await ctx.send(f"⚠️ **FORMATEO COMPLETO:** El usuario {member.mention} ha sido reiniciado a Nivel 0.")

async def setup(bot):
    await bot.add_cog(Niveles(bot))