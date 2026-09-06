import discord
from discord.ext import commands
from PIL import Image, ImageDraw
import io
import os

class Bienvenida(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.WELCOME_CHANNEL_ID = 1393290725306667191
        self.POLIZON_ROLE_ID = 1449866937915150346
        self.PROTOCOLS_CHANNEL_ID = 1393290301077983413

    def make_circle(self, avatar_img):
        mask = Image.new("L", avatar_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_img.size, fill=255)
        output = Image.new("RGBA", avatar_img.size, (0,0,0,0))
        output.paste(avatar_img, (0,0), mask=mask)
        return output

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # 1. Asignar Rol
        role_name = "N/A"
        try:
            role = member.guild.get_role(self.POLIZON_ROLE_ID)
            if role:
                await member.add_roles(role)
                role_name = role.name
                print(f"✅ Rol asignado a {member.name}")
        except Exception as e:
            print(f"❌ Error con el rol: {e}")

        # 2. Generar Imagen y Embed
        channel = self.bot.get_channel(self.WELCOME_CHANNEL_ID)
        if channel:
            try:
                bg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fondo.png")
                if not os.path.exists(bg_path):
                    print("⚠️ No encuentro 'fondo.png', saltando generación de imagen.")
                    return

                background = Image.open(bg_path).convert("RGBA")
                
                if member.avatar:
                    avatar_bytes = await member.avatar.read()
                    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                else:
                    avatar_bytes = await member.default_avatar.read()
                    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                
                avatar_image = avatar_image.resize((150, 150))
                circular_avatar = self.make_circle(avatar_image)
                background.paste(circular_avatar, (50, 50), circular_avatar)
                
                buffer = io.BytesIO()
                background.save(buffer, format="PNG")
                buffer.seek(0)
                
                file = discord.File(buffer, filename="welcome.png")
                
                embed = discord.Embed(
                    title="🚨 DETECCIÓN DE ENTRADA",
                    description=(
                        f"Sujeto identificado: {member.mention}\n"
                        f"Credencial asignada: **{role_name}**\n\n"
                        f"*Por favor, lea los protocolos en <#{self.PROTOCOLS_CHANNEL_ID}> para iniciar su asignación.*"
                    ),
                    color=0x00FFFF
                )
                
                embed.set_image(url="attachment://welcome.png")
                embed.set_footer(text="Sistema de Seguridad EXODUS")

                await channel.send(file=file, embed=embed) 
                
            except Exception as e:
                print(f"❌ Error imagen/embed: {e}")

async def setup(bot):
    await bot.add_cog(Bienvenida(bot))