import discord
from discord.ext import commands
import datetime

class Panoptico(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # --- CONFIGURACIÓN ---
        self.LOG_CHANNEL_ID = 1450887539429871820
        # ID DEL AXIOMA (Primer Radiante) - Inmune a la vigilancia
        self.AXIOMA_ID = 423592947158876163

    async def enviar_log(self, embed):
        """Envía el reporte al canal de seguridad"""
        channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
        else:
            print("⚠️ Error: No encuentro el canal de logs (Panóptico).")

    # --- 1. DETECCIÓN DE MENSAJE ELIMINADO ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignorar si es el propio bot o mensajes de sistema
        if message.author.bot: return
        if message.is_system(): return
        
        # 🛡️ PROTOCOLO DE INMUNIDAD: Ignorar al Primer Radiante
        if message.author.id == self.AXIOMA_ID: return

        embed = discord.Embed(
            title="🗑️ Supresión de datos (Mensaje Borrado)", 
            color=0xFF0000 # Rojo Intenso
        )
        embed.set_author(name=f"{message.author.display_name} ({message.author.name})", icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
        
        # Información del canal
        embed.add_field(name="📍 Sector (Canal)", value=message.channel.mention, inline=True)
        
        # Contenido (Manejo seguro si era solo imagen)
        contenido = message.content if message.content else "*[Archivo Multimedia o Embed sin texto]*"
        if len(contenido) > 1024: contenido = contenido[:1021] + "..." 
        
        embed.add_field(name="📄 Contenido Eliminado", value=contenido, inline=False)
        
        # Adjuntos (Fotos/Archivos)
        if message.attachments:
            lista_archivos = "\n".join([f"• {a.filename}" for a in message.attachments])
            embed.add_field(name="📎 Archivos Adjuntos", value=lista_archivos, inline=False)

        embed.set_footer(text=f"ID Usuario: {message.author.id} | ID Mensaje: {message.id}")
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await self.enviar_log(embed)

    # --- 2. DETECCIÓN DE EDICIÓN (ALTERACIÓN) ---
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Ignorar bots
        if before.author.bot: return
        
        # 🛡️ PROTOCOLO DE INMUNIDAD: Ignorar al Primer Radiante
        if before.author.id == self.AXIOMA_ID: return

        # Ignorar si el contenido es idéntico
        if before.content == after.content: return

        embed = discord.Embed(
            title="✏️ Manipulación de Registros (Edición)", 
            color=0xFFA500 # Naranja
        )
        embed.set_author(name=before.author.display_name, icon_url=before.author.avatar.url if before.author.avatar else before.author.default_avatar.url)
        
        embed.add_field(name="📍 Sector", value=before.channel.mention, inline=True)
        embed.add_field(name="🔗 Salto", value=f"[Ir al mensaje]({after.jump_url})", inline=True)

        # Antes
        txt_before = before.content if before.content else "*[Vacío]*"
        if len(txt_before) > 1024: txt_before = txt_before[:1021] + "..."
        embed.add_field(name="🔴 Antes", value=txt_before, inline=False)

        # Después
        txt_after = after.content if after.content else "*[Vacío]*"
        if len(txt_after) > 1024: txt_after = txt_after[:1021] + "..."
        embed.add_field(name="🟢 Ahora", value=txt_after, inline=False)

        embed.set_footer(text=f"ID Usuario: {before.author.id}")
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        await self.enviar_log(embed)

    # --- 3. DETECCIÓN DE SALIDA (DESERCIÓN) ---
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # 🛡️ PROTOCOLO DE INMUNIDAD: Ignorar al Primer Radiante
        if member.id == self.AXIOMA_ID: return

        # Lista de roles que tenía al irse
        roles = [r.name for r in member.roles if r.name != "@everyone"]
        lista_roles = ", ".join(roles) if roles else "Ninguno (Polizón)"

        embed = discord.Embed(
            title="👋 Deserción Confirmada (Salida)", 
            description=f"El sujeto **{member.mention}** ha abandonado la estación.", 
            color=0x36393F # Gris Oscuro
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        embed.add_field(name="👤 Identidad", value=f"{member.name} (ID: {member.id})", inline=False)
        embed.add_field(name="🎖️ Roles Perdidos", value=lista_roles, inline=False)
        
        # Calcular cuánto tiempo estuvo
        if member.joined_at:
            tiempo_estancia = datetime.datetime.now(datetime.timezone.utc) - member.joined_at
            dias = tiempo_estancia.days
            embed.set_footer(text=f"Tiempo de servicio: {dias} días")
        
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await self.enviar_log(embed)

async def setup(bot):
    await bot.add_cog(Panoptico(bot))