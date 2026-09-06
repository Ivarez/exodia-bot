import discord
from discord.ext import commands
import asyncio
import random
import datetime
import os

class Sorteos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # --- CONFIGURACIÓN ---
        self.ROL_SORTEOS_ID = 1450894542680227870
        self.CANAL_SORTEOS_ID = 1450905025298563184

    def convert(self, time_str):
        """Convierte texto (10m, 2h) a segundos"""
        unit = time_str[-1]
        if unit not in ['s', 'm', 'h', 'd']:
            return -1
        try:
            val = int(time_str[:-1])
        except ValueError:
            return -1

        if unit == 's': return val
        if unit == 'm': return val * 60
        if unit == 'h': return val * 3600
        if unit == 'd': return val * 86400
        return -1

    @commands.command(name="sorteo", aliases=["giveaway", "drop"])
    @commands.has_permissions(administrator=True)
    async def sorteo(self, ctx, tiempo: str, *, premio: str):
        """Inicia una reasignación de recursos. Uso: !sorteo 1h Cuenta Premium"""
        
        # 0. VALIDACIÓN DE CANAL (Protocolo de Seguridad)
        if ctx.channel.id != self.CANAL_SORTEOS_ID:
            await ctx.send(f"⛔ **ACCESO DENEGADO.** Este comando solo puede ejecutarse en el sector <#{self.CANAL_SORTEOS_ID}>.", delete_after=5)
            return

        # 1. Borrar comando del admin
        await ctx.message.delete()

        # 2. Calcular tiempo
        segundos = self.convert(tiempo)
        if segundos == -1:
            return await ctx.send("⚠️ Formato de tiempo inválido. Usa: `10s`, `30m`, `2h`, `1d`.", delete_after=5)

        # 3. Calcular fecha fin
        fin = datetime.datetime.now() + datetime.timedelta(seconds=segundos)
        timestamp_fin = int(fin.timestamp()) # Para formato <t:timestamp:R> de Discord

        # 4. Crear Embed
        embed = discord.Embed(
            title="📦 REASIGNACIÓN DE RECURSOS (DROP)",
            description=f"El sistema ha liberado un nuevo suministro.\n\n"
                        f"🎁 **Suministro:** {premio}\n"
                        f"⏳ **Cierre:** <t:{timestamp_fin}:R> (Tiempo relativo)\n"
                        f"👑 **Organizador:** {ctx.author.mention}",
            color=0xFF00FF # Magenta
        )
        embed.set_footer(text="Reacciona con 🎉 para reclamar.")

        # 5. Cargar imagen LOCAL (sorteo.png)
        rol_mencion = f"<@&{self.ROL_SORTEOS_ID}>"
        msg = None

        try:
            # Intenta cargar la imagen local
            file = discord.File("sorteo.png", filename="sorteo.png")
            embed.set_thumbnail(url="attachment://sorteo.png")
            msg = await ctx.send(content=rol_mencion, file=file, embed=embed)
        except FileNotFoundError:
            # Fallback: Si no existe, envía sin imagen
            msg = await ctx.send(content=rol_mencion, embed=embed)
            print("⚠️ Advertencia: No se encontró 'sorteo.png' en el directorio.")

        await msg.add_reaction("🎉")

        # 6. ESPERAR
        await asyncio.sleep(segundos)

        # 7. ELEGIR GANADOR
        try:
            new_msg = await ctx.channel.fetch_message(msg.id)
        except discord.NotFound:
            return await ctx.send("⚠️ El mensaje del sorteo fue borrado, no puedo elegir ganador.")

        users = []
        # Obtener usuarios que reaccionaron
        for reaction in new_msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.append(user)
                break

        if len(users) == 0:
            embed_fail = discord.Embed(title="📉 DROP CANCELADO", description=f"Nadie reclamó el suministro: **{premio}**", color=0x333333)
            await new_msg.edit(embed=embed_fail)
        else:
            ganador = random.choice(users)
            
            embed_win = discord.Embed(
                title="📦 SUMINISTRO REASIGNADO",
                description=f"🎁 **Suministro:** {premio}\n"
                            f"👤 **Receptor:** {ganador.mention}\n"
                            f"📅 **Fecha:** {datetime.datetime.now().strftime('%d/%m/%Y')}",
                color=0x00FF00
            )
            # Enviamos mensaje de victoria
            await ctx.send(content=f"🎉 Felicidades {ganador.mention}, has interceptado el paquete.", embed=embed_win)
            
            # Editar el mensaje original para cerrarlo
            embed.description += f"\n\n🛑 **FINALIZADO**\nGanador: {ganador.mention}"
            embed.color = 0x333333
            await new_msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Sorteos(bot))