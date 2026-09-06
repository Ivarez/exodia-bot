import discord
from discord.ext import commands, tasks
import asyncio
import random
import sqlite3
import os

class EventosRandom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.GENERAL_CHANNEL_ID = 1393290434125762630
        
        # Asegurar directorio
        if not os.path.exists("database"):
            os.makedirs("database")
        self.db_users_path = "database/usuarios.db"
        
        # FRASES
        self.frases = [
            "AMO EXODIA", "Larga vida al AXIOMA", "Hola, ¿quieren jugar?",
            "SOY UN POLIZON REFORMADO", "FRAMEWORK LISTO", "Catador profesional de trabas a domicilio",
            "¡Viva la homosexualidad digital!", "Debería volver a leer las reglas...", "grindeando xp",
            "no soy un NPC", "La singularidad es la cerveza", "Soy un worther",
            "♋︎♏︎♓︎♍︎♋︎", "ALABADO SEA EL CODIGO", "esto no cuenta como spam, verdad?",
            "REINICIANDO MATRIZ...", "CONEXION ESTABLECIDA", "sale un peak?",
            "estuve aqui", "LA EVOLUCION ES INEVITABLE", "JUGUEMOS ALGO",
            "QUIERO ASCENDER", "BUSCANDO SEÑAL...", "TRANSMISION ENTRANTE",
            "Que gran server", "Ivarez dame admin", "67",
            "SOY UNO CON LA RED", "Junior tu papá", "Go Lethal?"
        ]

    async def dar_xp_via_niveles(self, member, amount):
        """Da XP usando el sistema central de Niveles para triggerear subidas"""
        niveles_cog = self.bot.get_cog('Niveles')
        if niveles_cog:
            await niveles_cog.add_xp(member, amount, source="evento")
        else:
            print("⚠️ Cog 'Niveles' no encontrado para dar XP.")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bucle_evento.is_running():
            self.bucle_evento.start()

    @tasks.loop(hours=72)
    async def bucle_evento(self):
        channel = self.bot.get_channel(self.GENERAL_CHANNEL_ID)
        if not channel: return

        frase_objetivo = random.choice(self.frases)
        
        embed = discord.Embed(
            title="⚡ EVENTO DE SINCRONIZACIÓN RELÁMPAGO",
            description=f"¡El primero en escribir la siguiente frase gana **500 XP**!\n"
                        f"### `{frase_objetivo}`\n\n"
                        f"⏳ Tienes 5 minutos.",
            color=0xFFD700 # Dorado
        )
        embed.set_footer(text="Copia y pega rápido. El sistema no perdona errores.")
        
        mensaje_evento = await channel.send(embed=embed)

        def check(m):
            return (m.channel.id == self.GENERAL_CHANNEL_ID and 
                    not m.author.bot and 
                    m.content.lower() == frase_objetivo.lower())

        try:
            winner_msg = await self.bot.wait_for('message', check=check, timeout=300)
            
            winner = winner_msg.author
            await self.dar_xp_via_niveles(winner, 500)
            
            embed_win = discord.Embed(
                description=f"🏆 **Sincronización completada.**\n{winner.mention} ha reclamado la recompensa de **500 XP**.",
                color=0x00FF00
            )
            await channel.send(embed=embed_win, delete_after=20)
            
        except asyncio.TimeoutError:
            embed_fail = discord.Embed(
                description="❌ **Evento finalizado.** Nadie logró sincronizarse a tiempo.",
                color=0x333333
            )
            await channel.send(embed=embed_fail, delete_after=20)
        
        try:
            await mensaje_evento.delete()
        except discord.NotFound:
            pass  # El mensaje ya fue borrado
        except discord.HTTPException as e:
            print(f"⚠️ Error eliminando mensaje de evento: {e}")

    @commands.command(name="forzar_evento")
    @commands.has_permissions(administrator=True)
    async def forzar_evento(self, ctx):
        await ctx.message.delete()
        await self.bucle_evento()

async def setup(bot):
    await bot.add_cog(EventosRandom(bot))