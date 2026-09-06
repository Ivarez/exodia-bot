import discord
from discord.ext import commands
import sqlite3
import os
import datetime

class Sugerencias(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # --- CONFIGURACIÓN ---
        self.SUGGESTIONS_CHANNEL_ID = 1449884873560162575
        
        # Base de datos para trackear IDs de mensajes y números de sugerencia
        self.db_path = "database/sugerencias.db"
        self.init_db()

    def init_db(self):
        # Crear carpeta si no existe (ya debería existir por los otros cogs, pero por seguridad)
        if not os.path.exists("database"):
            os.makedirs("database")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sugerencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                author_id INTEGER,
                contenido TEXT,
                estado TEXT DEFAULT 'PENDIENTE'
            )
        ''')
        conn.commit()
        conn.close()

    # --- COMANDO PARA ENVIAR SUGERENCIA ---
    @commands.command(name="sugerencia", aliases=["sugg", "idea"])
    async def sugerencia(self, ctx, *, contenido: str = None):
        """Envía una propuesta al sistema central"""
        if contenido is None:
            await ctx.send(f"⚠️ **ERROR DE SINTAXIS:** Debes escribir la sugerencia.\nEjemplo: `!sugerencia Añadir un canal de música`", delete_after=5)
            return

        # 1. Borrar el mensaje original del usuario para limpieza
        await ctx.message.delete()

        # 2. Insertar en DB para obtener el ID único
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sugerencias (author_id, contenido) VALUES (?, ?)', (ctx.author.id, contenido))
            sugerencia_id = cursor.lastrowid
            conn.commit()

            # 3. Crear el Embed PENDIENTE (Amarillo)
            embed = discord.Embed(description=contenido, color=0xFFFF00) # Amarillo
            embed.set_author(name=f"💡 SUGERENCIA #{sugerencia_id}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_footer(text="Estado: ⏳ PENDIENTE DE REVISIÓN")
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

            # 4. Enviar al canal de sugerencias
            channel = self.bot.get_channel(self.SUGGESTIONS_CHANNEL_ID)
            if channel:
                msg = await channel.send(embed=embed)
                
                # 5. Guardar el ID del mensaje en la DB (para poder editarlo luego)
                cursor.execute('UPDATE sugerencias SET message_id = ? WHERE id = ?', (msg.id, sugerencia_id))
                conn.commit()
                
                # 6. Reacciones automáticas
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                
                # Confirmación al usuario (temporal)
                await ctx.send(f"✅ Tu propuesta **#{sugerencia_id}** ha sido registrada en el sistema.", delete_after=5)
            else:
                await ctx.send("❌ Error crítico: No encuentro el canal de sugerencias configurado.")
        finally:
            conn.close()

    # --- LÓGICA INTERNA PARA ACEPTAR/RECHAZAR ---
    async def gestionar_sugerencia(self, ctx, id_sugerencia, razon, estado_nuevo):
        # Validar permisos de admin
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("⛔ **ACCESO DENEGADO:** Solo el Alto Mando puede gestionar solicitudes.")

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT message_id, author_id, contenido FROM sugerencias WHERE id = ?', (id_sugerencia,))
            result = cursor.fetchone()

            if not result:
                return await ctx.send(f"❌ No existe ninguna sugerencia con el ID **#{id_sugerencia}**.")

            msg_id, author_id, contenido = result
            channel = self.bot.get_channel(self.SUGGESTIONS_CHANNEL_ID)
            
            try:
                msg = await channel.fetch_message(msg_id)
            except discord.NotFound:
                return await ctx.send("❌ El mensaje original de la sugerencia fue borrado, no puedo editarlo.")

            # Obtener usuario original para el icono
            autor_original = ctx.guild.get_member(author_id)
            avatar_url = (autor_original.avatar.url if autor_original and autor_original.avatar 
                         else (self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url))

            # Configurar colores y textos según decisión
            if estado_nuevo == "APROBADA":
                color = 0x00FF00 # Verde
                titulo_estado = "Aprobada ✅"
                footer_text = f"Aprobado por: {ctx.author.display_name}"
            else:
                color = 0xFF0000 # Rojo
                titulo_estado = " Rechazada ⛔"
                footer_text = f"Rechazado por: {ctx.author.display_name}"

            # RECONSTRUIR EL EMBED
            embed = discord.Embed(description=contenido, color=color)
            embed.set_author(name=f"SUGERENCIA #{id_sugerencia} | {titulo_estado}", icon_url=avatar_url)
            
            # Añadir campo de justificación
            embed.add_field(name="📋 Resolución del Mando:", value=razon, inline=False)
            embed.set_footer(text=footer_text)
            embed.timestamp = datetime.datetime.now()

            # Editar mensaje
            await msg.edit(embed=embed)
            
            # Actualizar DB
            cursor.execute('UPDATE sugerencias SET estado = ? WHERE id = ?', (estado_nuevo, id_sugerencia))
            conn.commit()
        finally:
            conn.close()

        await ctx.message.delete() # Borrar el comando del admin para limpiar
        await ctx.send(f"📝 Sugerencia **#{id_sugerencia}** actualizada correctamente.", delete_after=3)

    # --- COMANDO ACEPTAR ---
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def aceptar(self, ctx, id_sugerencia: int, *, justificacion: str = "Medida aprobada para implementación inmediata."):
        """Aprueba una sugerencia (Color Verde)"""
        await self.gestionar_sugerencia(ctx, id_sugerencia, justificacion, "APROBADA")

    # --- COMANDO RECHAZAR ---
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rechazar(self, ctx, id_sugerencia: int, *, justificacion: str = "La propuesta no cumple con los protocolos de la estación."):
        """Rechaza una sugerencia (Color Rojo)"""
        await self.gestionar_sugerencia(ctx, id_sugerencia, justificacion, "RECHAZADA")

async def setup(bot):
    await bot.add_cog(Sugerencias(bot))