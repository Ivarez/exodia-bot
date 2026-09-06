import discord
from discord.ext import commands, tasks
import itertools 

class Sistema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ciclo de estados del bot (Vida artificial)
        self.status_cycle = itertools.cycle([
            "Vigilando Sector Omega",
            "Analizando ADNs...",
            "Esperando la Apoteosis",
            "Sistema EXODIA v1.1",
            "Monitoreando Secuencia",
            "Procesando Suministros"
        ])

    # --- EVENTO: AL INICIAR EL COG ---
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.change_status.is_running():
            self.change_status.start()

    # --- TAREA: ROTAR ESTADO CADA 5 MINUTOS ---
    @tasks.loop(minutes=5)
    async def change_status(self):
        new_status = next(self.status_cycle)
        await self.bot.change_presence(activity=discord.Game(name=new_status))

    # --- MANEJO DE ERRORES GLOBAL ---
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return 

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="⚠️ ERROR DE SINTAXIS",
                description=f"Te falta información para ejecutar este protocolo.\nUsa `!help` para consultar la documentación.",
                color=0xFFA500
            )
            await ctx.send(embed=embed, delete_after=10)

        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="⛔ ACCESO DENEGADO",
                description="Tu credencial actual no tiene autorización para este comando.",
                color=0xFF0000
            )
            await ctx.send(embed=embed, delete_after=10)
        
        else:
            print(f"❌ ERROR NO CONTROLADO: {error}")

    # --- COMANDO HELP MEJORADO ---
    @commands.command(name="help", aliases=["ayuda", "comandos"])
    async def help(self, ctx):
        embed = discord.Embed(
            title="💠 INTERFAZ CENTRAL - EXODIA",
            description="Lista de protocolos disponibles para tu unidad.",
            color=0x00FFFF
        )
        
        thumbnail_url = None
        if self.bot.user.avatar:
            thumbnail_url = self.bot.user.avatar.url
        elif ctx.guild and ctx.guild.icon:
            thumbnail_url = ctx.guild.icon.url
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        # SECCIÓN 1: GENERAL (Usuarios)
        embed.add_field(
            name="🔰 Protocolos Básicos", 
            value="`!perfil` - Muestra tu credencial, Nivel y XP.\n"
                  "`!ranking` - Tabla de líderes de la estación.\n"
                  "`!sugerencia [texto]` - Envía una propuesta al alto mando.",
            inline=False
        )

        # SECCIÓN 2: EVOLUCIÓN (Usuarios)
        embed.add_field(
            name="🧬 Genética y Evolución", 
            value="`!evolucionar` - Escanea tu ADN y muestra tus opciones de mejora.\n"
                  "`!evolucionar [clase]` - Ejecuta la mutación (Niveles 5, 10, 20).\n"
                  "*Nota: Requiere alcanzar el nivel de XP necesario.*",
            inline=False
        )

        # SECCIÓN 3: ADMINISTRACIÓN (Solo visible si eres Admin)
        if ctx.author.guild_permissions.administrator:
            # Agrupamos los comandos para que se vea ordenado
            admin_desc = (
                "**👮‍♂️ Gestión de Usuarios:**\n"
                "`!dar_xp [@user] [cantidad]` - Inyecta experiencia.\n"
                "`!reset_user [@user]` - Reinicia nivel a 0.\n\n"
                "**🗳️ Burocracia (Sugerencias):**\n"
                "`!aceptar [id] [razón]` - Aprueba solicitud.\n"
                "`!rechazar [id] [razón]` - Rechaza solicitud.\n\n"
                "**🎉 Eventos y Entretenimiento:**\n"
                "`!sorteo [tiempo] [premio]` - Inicia un Drop (ej: `1h` Vip).\n"
                "`!forzar_turing` - Lanza pregunta semanal manualmente.\n\n"
                ""
                "**⚙️ Sistema:**\n"
                "`!setup_origen` - Despliega paneles de Roles/Clases.\n"
                "`!backup` - Envía copia de seguridad al MD."
            )
            
            embed.add_field(
                name="🔧 Panel de Control (Admin)\n", 
                value=admin_desc,
                inline=False
            )

        embed.set_footer(text="Sistema Operativo EXODUS • v1.1")
        
        await ctx.send(embed=embed)

    # --- COMANDO BACKUP ---
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        """Envía una copia de las bases de datos al MD del Admin"""
        await ctx.message.add_reaction("📦")
        
        # Lista de bases de datos actuales
        archivos = [
            "database/usuarios.db", 
            "database/secuencia.db", 
            "database/sugerencias.db", 
            "database/turing.db"
        ]
        enviados = 0
        
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send(f"💾 **BACKUP DEL SISTEMA EXODIA** - {discord.utils.utcnow().date()}")
            
            for ruta in archivos:
                try:
                    file = discord.File(ruta)
                    await dm_channel.send(file=file)
                    enviados += 1
                except FileNotFoundError:
                    # No avisamos en el chat público para no ensuciar, solo log interno si quieres
                    pass
            
            await ctx.send(f"✅ Backup completado. {enviados} bases de datos enviadas a tu privado.", delete_after=10)
            
        except discord.Forbidden:
            await ctx.send("❌ No te puedo enviar mensajes privados. Abre tu MD.")

async def setup(bot):
    await bot.add_cog(Sistema(bot))