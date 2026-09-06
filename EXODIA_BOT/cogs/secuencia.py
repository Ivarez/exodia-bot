import discord
from discord.ext import commands
import sqlite3
import os
import ast
import operator

class Secuencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CHANNEL_ID = 1449881077819637760
        
        # Asegurar directorio
        if not os.path.exists("database"):
            os.makedirs("database")
            
        self.db_path = "database/secuencia.db"
        self.db_users_path = "database/usuarios.db"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secuencia (
                id INTEGER PRIMARY KEY,
                numero_actual INTEGER DEFAULT 0,
                ultimo_user_id INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('INSERT OR IGNORE INTO secuencia (id, numero_actual, ultimo_user_id) VALUES (1, 0, 0)')
        conn.commit()
        conn.close()

    async def dar_xp_via_niveles(self, member, amount=5):
        """Da XP usando el sistema central de Niveles para triggerear subidas"""
        niveles_cog = self.bot.get_cog('Niveles')
        if niveles_cog:
            await niveles_cog.add_xp(member, amount, source="secuencia")
        else:
            print("⚠️ Cog 'Niveles' no encontrado para dar XP.")

    # --- CALCULADORA SEGURA ---
    def evaluar_matematica(self, texto):
        """Permite inputs como '1+1' o '10/2' de forma segura sin eval()"""
        # Caracteres permitidos (solo números y operadores básicos)
        permitidos = set("0123456789+-*/() ")
        
        # Si tiene letras o cosas raras, no es matemáticas
        if not set(texto).issubset(permitidos):
            return None
            
        # Limitar longitud para evitar spam/lag
        if len(texto) > 20: 
            return None

        try:
            tree = ast.parse(texto, mode='eval')
            # Solo permitir operaciones matemáticas básicas
            for node in ast.walk(tree):
                if isinstance(node, ast.Expression):
                    continue
                elif isinstance(node, ast.BinOp):
                    if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod)):
                        return None
                elif isinstance(node, ast.UnaryOp):
                    if not isinstance(node.op, (ast.UAdd, ast.USub)):
                        return None
                elif isinstance(node, ast.Constant):
                    if not isinstance(node.value, (int, float)):
                        return None
                    # Prevenir números absurdamente grandes
                    if isinstance(node.value, (int, float)) and abs(node.value) > 1_000_000:
                        return None
                else:
                    return None  # Cualquier otro nodo es rechazado
            
            resultado = compile(tree, '<string>', 'eval')
            valor = eval(resultado)
            return int(valor)
        except:
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.channel.id != self.CHANNEL_ID: return

        numero_usuario = self.evaluar_matematica(message.content)

        if numero_usuario is None:
            await message.delete()
            return

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT numero_actual, ultimo_user_id FROM secuencia WHERE id = 1')
            data = cursor.fetchone()
            numero_actual, ultimo_user = data

            if message.author.id == ultimo_user:
                await message.add_reaction("⚠️")
                await message.delete(delay=3)
                return

            if numero_usuario == numero_actual + 1:
                await message.add_reaction("✅")
                
                cursor.execute('UPDATE secuencia SET numero_actual = ?, ultimo_user_id = ? WHERE id = 1', (numero_usuario, message.author.id))
                conn.commit()
                
                await self.dar_xp_via_niveles(message.author, 5)
            else:
                await message.add_reaction("❌")
                await message.channel.send(f"💥 **SECUENCIA ROTA** por {message.author.mention}. Escribió `{numero_usuario}` pero seguía `{numero_actual + 1}`.\n¡Reiniciando a 0!", delete_after=10)
                cursor.execute('UPDATE secuencia SET numero_actual = 0, ultimo_user_id = 0 WHERE id = 1')
                conn.commit()
        finally:
            conn.close()

async def setup(bot):
    await bot.add_cog(Secuencia(bot))