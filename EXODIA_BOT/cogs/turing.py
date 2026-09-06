import discord
from discord.ext import commands, tasks
import sqlite3
import datetime
import os
import random

class TestTuring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # --- CONFIGURACIÓN ---
        self.CHANNEL_ID = 1449881775584182302
        self.ROL_LUDICA_ID = 1450899057169141843 
        
        # Horario: Viernes (4) a las 18:00
        self.DIA_PUBLICACION = 4 
        self.HORA_PUBLICACION = 18 
        
        # Directorios
        if not os.path.exists("database"):
            os.makedirs("database")
        self.db_path = "database/turing.db"
        self.db_users_path = "database/usuarios.db"
        
        # Lista de preguntas
        self.preguntas = [
            "¿Preferirías tener ganchos de pirata en vez de manos O ruedas en vez de pies?",
            "¿Preferirías que tu vida sea un musical (tienes que cantar todo) O una película muda (nadie te escucha)?",
            "¿Preferirías pelear con una gallina cada vez que subes a un auto O pelear con un león una vez al año?",
            "¿Preferirías tener la piel permanentemente azul (tipo Avatar) O verde (tipo Shrek)?",
            "¿Preferirías comer comida de perro gourmet O comida humana un poco podrida?",
            "¿Preferirías saber todos los secretos de tus amigos O que ellos sepan todos los tuyos?",
            "¿Preferirías ser inmune al fuego O inmune al daño por caída (lógica de Minecraft)?",
            "¿Preferirías tener un botón de 'Saltar Intro' en conversaciones reales O un botón de 'Velocidad x2'?",
            "¿Preferirías que tu almohada siempre esté caliente por los dos lados O que tu sábana siempre te quede corta?",
            "¿Preferirías ser un mago mediocre O un científico loco exitoso?",
            "¿Preferirías tener que comer un limón entero cada mañana O tener que comer una cebolla cruda cada noche?",
            "¿Preferirías vivir en un mundo donde todos mienten O en un mundo donde nadie puede mentir?",
            "¿Preferirías tener brazos de fideo cocido O piernas de madera?",
            "¿Preferirías ser perseguido por un caracol inmortal que si te toca mueres O ser perseguido por Jason Voorhees pero camina lento?",
            "¿Preferirías tener un inodoro que te habla y te da consejos O un espejo que se ríe de ti?",
            "¿Preferirías usar ropa interior hecha de lija O usar zapatos llenos de canicas?",
            "¿Preferirías que tu nombre legal sea 'Cochinote' O 'Bebote'?",
            "¿Preferirías perder todo tu dinero y objetos O perder todos tus recuerdos?",
            "¿Preferirías poder transformarte en cualquier objeto (pero no te puedes mover) O transformarte en cualquier animal (pero mantienes tu cara humana)?",
            "¿Preferirías tener siempre la sensación de que se te durmió el pie O tener siempre la sensación de cerebro congelado?",
            "¿Preferirías ser el mejor en un juego que nadie juega O ser un 'noob' en el juego más popular?",
            "¿Preferirías tener que anunciar cada vez que vas al baño con un megáfono O tener que pedir permiso a tu mamá para ir al baño por siempre?",
            "¿Preferirías tener una tercera pierna O un tercer brazo?",
            "¿Preferirías vivir en la película de 'Mad Max' O en la de 'Wall-E' (siendo los humanos gordos)?",
            "¿Preferirías que todos los animales te ataquen al verte O que todos los bebés lloren al verte?",
            "¿Preferirías tener el pelo hecho de plumas O la piel hecha de escamas?",
            "¿Preferirías solo poder comer con cuchara O solo poder comer con palillos chinos?",
            "¿Preferirías ser la persona más rica del cementerio O la persona más pobre de la fiesta?",
            "¿Preferirías tener un botón de 'Deshacer' en la vida real (3 usos totales) O un botón de 'Pausa' (uso ilimitado)?",
            "¿Preferirías que tu mascota pueda hablar pero te odie O que tu mascota sea un Pokémon?",
            "¿Preferirías eructar confeti O tirarte pedos que huelen a perfume?",
            "¿Preferirías tener que correr a todos lados O tener que caminar hacia atrás a todos lados?",
            "¿Preferirías ser un NPC en GTA V (te atropellan) O un NPC en Skyrim (te ataca un dragón)?",
            "¿Preferirías tener un ejército de 1000 hámsters rabiosos O un T-Rex obediente pero torpe?",
            "¿Preferirías vomitar babosas vivas O llorar sangre (sin dolor, pero da miedo)?",
            "¿Preferirías siempre tener arena en la ropa interior O siempre tener los calcetines mojados?",
            "¿Preferirías que tu abuela vea todo tu historial de internet O tú tener que ver todo el historial de tu abuela?",
            "¿Preferirías no poder distinguir entre un bebé y un muffin O no poder distinguir entre un perro y un pan?",
            "¿Preferirías vivir atrapado en un ascensor con tu ex O con tu enemigo mortal?",
            "¿Preferirías tener una cola de canguro (te estorba) O orejas de burro?",
            "¿Preferirías que cada vez que aplaudas se apague la luz O que cada vez que parpadees suene un 'clic' de cámara?",
            "¿Preferirías ser un genio malvado O un superhéroe tonto?",
            "¿Preferirías comer solo postres para siempre O comer solo carne para siempre?",
            "¿Preferirías no tener cejas O no tener pestañas?",
            "¿Preferirías vivir en una isla desierta solo O vivir en una cárcel de máxima seguridad?",
            "¿Preferirías que tu vida sea narrada por Morgan Freeman O por un niño de 5 años que no sabe leer bien?",
            "¿Preferirías tener manos pegajosas para siempre O manos resbaladizas para siempre?",
            "¿Preferirías usar un traje de payaso en todos los eventos serios O usar un vestido de novia/traje de novio en el gimnasio?",
            "¿Preferirías tener el superpoder de invocar patos O el superpoder de hacer que la fruta madure al instante?",
            "¿Preferirías que todo lo que comas sepa a pollo O que todo lo que bebas sepa a agua de mar?",
            "¿Preferirías tener un detector de mentiras infalible O un detector de 'gente que le gustas'?",
            "¿Preferirías ser calvo pero con una barba increíble O tener un pelo increíble pero no poder tener barba/cejas?",
            "¿Preferirías que llueva cada vez que estás triste O que salga un arcoíris cada vez que vas al baño?",
            "¿Preferirías ser un pirata espacial O un vaquero samurái?",
            "¿Preferirías olvidar quién eres cada mañana O olvidar quiénes son todos los demás?",
            "¿Preferirías tener un solo ojo gigante (cíclope) O dos caras (una atrás)?",
            "¿Preferirías poder atravesar paredes (pero pierdes la ropa) O poder leer mentes (pero solo pensamientos sucios)?",
            "¿Preferirías vivir sin espejos O vivir sin relojes?",
            "¿Preferirías que te laman la cara 5 perros O que te lama la cara una persona desconocida?",
            "¿Preferirías tener un auto que nunca necesita gasolina pero va a 20 km/h O un auto rapidísimo que se rompe cada semana?",
            "¿Preferirías ser baneado de tu videojuego favorito para siempre O ser baneado de todas las redes sociales?",
            "¿Preferirías tener pesadillas todas las noches O tener alucinaciones despierto una vez al día?",
            "¿Preferirías comer un tazón de gusanos fritos O beber un vaso de sudor?",
            "¿Preferirías que cada vez que hables suenes como si hubieras aspirado helio O como si fueras un demonio?",
            "¿Preferirías tener pies de hobbit (peludos y grandes) O manos de Mickey Mouse (guantes blancos pegados)?",
            "¿Preferirías encontrar un cadáver O encontrar un fantasma?",
            "¿Preferirías ser un robot sin sentimientos O un humano que siente todo x10 veces más fuerte?",
            "¿Preferirías tener que saludar de mano a todos los que ves O tener que guiñar el ojo a todos los que ves?",
            "¿Preferirías vivir en una casa embrujada O vivir con 10 gatos y ser alérgico?",
            "¿Preferirías ser el primer humano en Marte O el inventor de la cura contra el cáncer?",
            "¿Preferirías tener el poder de cambiar de forma O el poder de controlar los elementos?",
            "¿Preferirías tener una nariz de payaso roja permanente O zapatos de payaso permanentes?",
            "¿Preferirías nunca más tener tráfico O nunca más hacer fila en ningún lado?",
            "¿Preferirías que tu risa suene como un claxon de camión O como un vidrio rompiéndose?",
            "¿Preferirías ser atacado por 50 patitos O por 2 cisnes muy agresivos?",
            "¿Preferirías que te crezca bigote instantáneamente si dices una mentira O perder un pelo de la cabeza por cada verdad?",
            "¿Preferirías comer cereal con agua O comer cereal con jugo de naranja?",
            "¿Preferirías que tus padres elijan tu pareja O que tus padres elijan tu trabajo?",
            "¿Preferirías ser un personaje de Los Simpson O un personaje de South Park?",
            "¿Preferirías tener hipo por 24 horas seguidas una vez al año O tener hipo 10 segundos cada hora todos los días?",
            "¿Preferirías que te piquen las plantas de los pies O que te pique el cielo de la boca?",
            "¿Preferirías tener dientes de oro O tener ojos violeta?",
            "¿Preferirías ser un streamer famoso pero tóxico O un youtuber amado pero con 100 subs?",
            "¿Preferirías usar calcetines mojados por un año O no usar calcetines nunca más?",
            "¿Preferirías tener un ping de 0 en la vida real (reflejos dios) O tener 'aimbot' en la vida real (puntería perfecta)?",
            "¿Preferirías que todo el mundo sepa tu historial de reproducciones de Spotify O tu historial de YouTube?",
            "¿Preferirías ser perseguido por la policía por un crimen que no cometiste O ser ignorado por la policía cuando necesitas ayuda?",
            "¿Preferirías tener un dinosaurio de mascota O un alien de mejor amigo?",
            "¿Preferirías hablar en rima todo el tiempo O tener que cantar ópera para pedir comida?",
            "¿Preferirías que tus pedos sean visibles (humo verde) O que tus pedos suenen como sirena de policía?",
            "¿Preferirías vivir debajo del mar (como Bob Esponja) O vivir en una nube?",
            "¿Preferirías tener un control remoto para controlar a tus padres O un control remoto para controlar a tus profesores/jefes?",
            "¿Preferirías comer helado con sabor a pescado O pescado con sabor a helado?",
            "¿Preferirías tener la capacidad de dormir a comando (te duermes ya) O la capacidad de no cansarte nunca?",
            "¿Preferirías que tu sudor sea pegajoso como miel O resbaloso como aceite?",
            "¿Preferirías tener un botón para silenciar a los niños llorando O un botón para silenciar a los perros ladrando?",
            "¿Preferirías ser la persona más divertida del mundo O la más atractiva?",
            "¿Preferirías tener un loro que repite todo lo que dices cuando duermes O un gato que te juzga en voz alta?",
            "¿Preferirías vivir sin codos O vivir sin rodillas?",
            "¿Preferirías tener el poder de hablar con la fruta O el poder de revivir insectos muertos?",
            "¿Preferirías tener un brazo mecánico con herramientas infinitas O un ojo biónico que puede ver a través de las paredes?",
            "¿Preferirías vivir en una simulación perfecta y feliz para siempre O en una realidad dolorosa pero verdadera?",
            "¿Preferirías que la IA gobierne el mundo de forma justa y sin guerras O que los humanos sigan gobernando con libertad pero con caos?",
            "¿Preferirías poder descargar cualquier habilidad en tu cerebro en segundos O poder transferir tu conciencia a un nuevo cuerpo cuando mueras?",
            "¿Preferirías viajar al pasado y conocer a tus ancestros O viajar al futuro y conocer a tus descendientes?",
            "¿Preferirías saber cuándo vas a morir O saber cómo vas a morir?",
            "¿Preferirías ser la persona más inteligente del mundo pero estar solo O ser el más tonto pero rodeado de amigos que te aman?",
            "¿Preferirías tener el poder de volar (pero lento) O el poder de teletransportarte (pero solo a lugares que has visto)?",
            "¿Preferirías no tener que dormir nunca más O no tener que comer nunca más (sin efectos negativos)?",
            "¿Preferirías encontrar el amor verdadero hoy O ganar la lotería mañana?",
            "¿Preferirías tener dedos de salchicha que huelen rico O tener piernas de fideos que nunca se cansan?",
            "¿Preferirías que todo el mundo reciba un cachorro gratis O tener diarrea explosiva para siempre?",
            "¿Preferirías luchar contra 100 caballos del tamaño de un pato O contra un pato del tamaño de un caballo?",
            "¿Preferirías tener siempre una piedra en el zapato O tener siempre la sensación de que te van a estornudar pero no sale?",
            "¿Preferirías hablar todos los idiomas fluidamente O saber tocar todos los instrumentos perfectamente?",
            "¿Preferirías vivir en un mundo cyberpunk distópico O en un mundo de fantasía medieval sin baños?",
            "¿Preferirías tener botones de 'Ctrl+Z' en la vida real O tener una barra de búsqueda para encontrar objetos perdidos?",
            "¿Preferirías que tu historial de búsqueda se haga público O que tu galería de fotos se envíe a tu jefe?",
            "¿Preferirías usar siempre ropa mojada O usar siempre ropa dos tallas más pequeña?",
            "¿Preferirías tener lag de 900ms en la vida real O tener 10 FPS en la vida real?",
            "¿Preferirías ser inmortal pero flotar en el espacio para siempre al final O morir a los 40 habiendo vivido al máximo?",
            "¿Preferirías tener pezones que brillan en la oscuridad O que suene una bocina cada vez que te sientas?",
            "¿Preferirías tener sabor a caca en la boca por 5 años O comer caca una vez y que sepa a chocolate?",
            "¿Preferirías poder hablar con los animales pero que todos sean unos groseros O poder hablar con fantasmas pero que solo te cuenten chistes malos?",
            "¿Preferirías reiniciar tu vida con todo tu conocimiento actual O recibir 10 millones de dólares ahora mismo?",
            "¿Preferirías no tener codos O no tener rodillas?",
            "¿Preferirías tener un dragón doméstico O ser un dragón?",
            "¿Preferirías que cada vez que entres a una habitación suene música épica O que cada vez que hables suene una risa grabada de sitcom?",
            "¿Preferirías tener el cuello de una jirafa O los ojos de un camaleón?",
            "¿Preferirías vivir sin música O vivir sin películas/series?",
            "¿Preferirías ser el mejor jugador del peor equipo O el peor jugador del mejor equipo?",
            "¿Preferirías tener un botón de 'mute' para la gente O un botón de 'pausa' para momentos incómodos?",
            "¿Preferirías tener siempre el celular al 1% de batería O tener siempre internet lentísimo?",
            "¿Preferirías oler a cebolla siempre que hace calor O oler a ajo siempre que llueve?",
            "¿Preferirías salvar a 100 desconocidos O salvar a tu mejor amigo?",
            "¿Preferirías tener manos de jamón (y te las puedes comer pero no regeneran) O tener pies de queso?",
            "¿Preferirías ver tu futuro en HD O ver el pasado de los demás en 144p?",
            "¿Preferirías ser alérgico al agua (te pica) O ser alérgico a tu comida favorita?",
            "¿Preferirías tener que gritar todo lo que dices O tener que susurrar todo lo que dices?",
            "¿Preferirías ser famoso por algo vergonzoso O ser un héroe anónimo?",
            "¿Preferirías tener un sable de luz O tener la varita de Harry Potter?",
            "¿Preferirías que tu sudor sea mayonesa O que tu saliva sea salsa picante?",
            "¿Preferirías vivir en una casa hecha de cristal transparente O vivir en una casa subterránea sin ventanas?",
            "¿Preferirías tener que usar pañales el resto de tu vida O tener que usar un chupete el resto de tu vida?",
            "¿Preferirías perder la capacidad de leer O perder la capacidad de hablar?",
            "¿Preferirías tener siempre hipo O estornudar cada 5 minutos?",
            "¿Preferirías ser atacado por un oso O ser atacado por un enjambre de avispas?",
            "¿Preferirías ser un genio en un mundo de idiotas O ser un idiota en un mundo de genios?",
            "¿Preferirías tener cabello hecho de espaguetis O sudar jarabe de arce?",
            "¿Preferirías ir al espacio O explorar lo más profundo del océano?",
            "¿Preferirías detener el tiempo 10 segundos al día O retroceder el tiempo 1 minuto al día?",
            "¿Preferirías tener visión de rayos X (no se apaga) O superoído (escuchas todo)?",
            "¿Preferirías ser un personaje secundario en tu anime favorito O el protagonista de un anime de terror?",
            "¿Preferirías comer pizza con piña por el resto de tu vida O no comer pizza nunca más?",
            "¿Preferirías tener brazos de T-Rex O tener piernas de canguro?",
            "¿Preferirías que te piquen 100 mosquitos en la espalda O tener una mosca zumbando en tu oído para siempre?",
            "¿Preferirías usar Discord en modo claro para siempre O usar Internet Explorer para siempre?",
            "¿Preferirías saber la verdad absoluta sobre los aliens O saber la verdad absoluta sobre quién mató a Kennedy?",
            "¿Preferirías tener un tercer ojo en la frente O tener una segunda boca en la mano?",
            "¿Preferirías que cada vez que mientas te crezca la nariz O que cada vez que digas la verdad te encojas 1 cm?",
            "¿Preferirías pelear contra Mike Tyson en su prime O pelear contra un gorila enojado?",
            "¿Preferirías ser invisible pero hueles horrible O oler increíble pero ser fosforescente?",
            "¿Preferirías poder teletransportarte pero tu ropa no viaja contigo O poder volar pero solo a 1 metro del suelo?",
            "¿Preferirías tener dientes de madera O tener uñas de vidrio?",
            "¿Preferirías vivir sin internet por un año O vivir sin hablar con nadie por un mes?",
            "¿Preferirías tener un perro con cara de humano O un humano con cara de perro como mascota?",
            "¿Preferirías siempre sentir que tienes algo en el ojo O siempre sentir que tienes comezón en la espalda donde no alcanzas?",
            "¿Preferirías ser el villano que gana O el héroe que muere?",
            "¿Preferirías tener que cazar tu propia comida O comer solo comida de bebé?",
            "¿Preferirías ser un maestro de todas las armas O un maestro de todas las artes marciales?",
            "¿Preferirías que tu vida tenga subtítulos O que tu vida tenga música de fondo?",
            "¿Preferirías orinar jugo de uva O sudar Gatorade?",
            "¿Preferirías tener manos por pies O pies por manos?",
            "¿Preferirías vivir en un apocalipsis zombie (lento) O en una invasión alienígena?",
            "¿Preferirías poder borrar recuerdos dolorosos O poder crear recuerdos falsos felices?",
            "¿Preferirías tener la fuerza de Hulk pero su inteligencia O la inteligencia de Tony Stark pero sin dinero?",
            "¿Preferirías que nadie vaya a tu funeral O que vaya gente que te odia a burlarse?",
            "¿Preferirías tener un mayordomo robot O tener una mascota clonada de un dinosaurio?",
            "¿Preferirías despertarte siempre a las 3 AM y no dormir más O dormirte siempre a las 5 PM?",
            "¿Preferirías tener una cabeza gigante O un cuerpo diminuto?",
            "¿Preferirías comer solo cosas crudas O comer solo cosas quemadas?",
            "¿Preferirías ser temido por todos O ser ignorado por todos?",
            "¿Preferirías encontrar 100 dólares en el suelo cada día O encontrar 50 mil dólares una sola vez?",
            "¿Preferirías que te salga un anuncio de YouTube de 30 segundos cada vez que abras los ojos O tener lag mental cada vez que te preguntan algo?",
            "¿Preferirías tener el pelo de Donald Trump O la risa de Bob Esponja?",
            "¿Preferirías ser un pez en una pecera gigante O un pájaro en una jaula pequeña?",
            "¿Preferirías que tu crush lea tu mente O leer la mente de tu crush y que te odie?",
            "¿Preferirías tener dedos magnéticos (todo se pega) O tener dedos resbalosos (todo se cae)?",
            "¿Preferirías vivir en la Antártida O vivir en el desierto del Sahara?",
            "¿Preferirías tener un tatuaje en la cara que diga 'Tonto' O tener 'Tonto' legalmente en tu nombre?",
            "¿Preferirías poder hablar con las plantas O que las plantas te juzguen en silencio?",
            "¿Preferirías tener una voz de narrador de tráiler de cine O tener voz de ardilla?",
            "¿Preferirías que todos tus dientes se caigan y vuelvan a crecer una vez al año O que tus uñas nunca dejen de crecer?",
            "¿Preferirías pelear contra un zombie con una cuchara O pelear contra un caballero medieval con un teclado?",
            "¿Preferirías tener Wi-Fi gratis donde sea pero lento O Wi-Fi ultra rápido pero pagando carísimo?",
            "¿Preferirías ser un vampiro (chupas sangre) O ser un hombre lobo (te llenas de pulgas)?",
            "¿Preferirías tener que bailar cada vez que caminas O cantar cada vez que hablas?",
            "¿Preferirías comer un ladrillo O beber un litro de pintura?",
            "¿Preferirías tener una alfombra hecha de Legos O zapatos hechos de cactus?",
            "¿Preferirías ver el mundo en blanco y negro O ver el mundo al revés?",
            "¿Preferirías ser el dueño de Apple O ser el presidente del mundo?",
            "¿Preferirías que tu única forma de transporte sea un burro O un monociclo?",
            "¿Preferirías tener un botón para explotar la Luna O un botón para apagar el Sol por 5 segundos?",
            "¿Preferirías ser un fantasma y ver a todos O reencarnar en un gato doméstico gordo?",
            "¿Preferirías nunca más tener que bañarte (siempre hueles bien) O nunca más tener que limpiar tu casa (se limpia sola)?",
        ]

        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Tabla de estado general
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estado_turing (
                id INTEGER PRIMARY KEY,
                indice_actual INTEGER DEFAULT 0,
                ultima_semana INTEGER DEFAULT 0,
                ultimo_anio INTEGER DEFAULT 0,
                msg_id INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('INSERT OR IGNORE INTO estado_turing (id, indice_actual, ultima_semana, ultimo_anio, msg_id) VALUES (1, 0, 0, 0, 0)')
        
        # Tabla de votos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votos_turing (
                user_id INTEGER,
                pregunta_idx INTEGER,
                PRIMARY KEY (user_id, pregunta_idx)
            )
        ''')
        conn.commit()
        conn.close()

    async def dar_xp_via_niveles(self, user_id, amount=200):
        """Da XP usando el sistema central de Niveles para triggerear subidas"""
        niveles_cog = self.bot.get_cog('Niveles')
        if niveles_cog:
            # Necesitamos el objeto Member, no solo el ID
            for guild in self.bot.guilds:
                member = guild.get_member(user_id)
                if member:
                    await niveles_cog.add_xp(member, amount, source="turing")
                    return
            print(f"⚠️ No se encontró al miembro {user_id} en ningún servidor.")
        else:
            print("⚠️ Cog 'Niveles' no encontrado para dar XP.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id: return
        if payload.channel_id != self.CHANNEL_ID: return

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute('SELECT msg_id FROM estado_turing WHERE id = 1')
            data = cursor.fetchone()
            
            if not data:
                return
                
            msg_id_actual = data[0]

            if payload.message_id == msg_id_actual:
                cursor.execute('SELECT 1 FROM votos_turing WHERE user_id = ?', (payload.user_id,))
                ya_voto = cursor.fetchone()
                
                if not ya_voto:
                    cursor.execute('INSERT INTO votos_turing (user_id, pregunta_idx) VALUES (?, 1)', (payload.user_id,))
                    conn.commit()
                    await self.dar_xp_via_niveles(payload.user_id, 200)
        finally:
            conn.close()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_weekly_post.is_running():
            self.check_weekly_post.start()

    async def publicar_pregunta(self, channel, titulo_extra=""):
        """Lógica compartida para publicar una pregunta de Turing"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Obtener y borrar mensaje anterior
            cursor.execute('SELECT msg_id FROM estado_turing WHERE id = 1')
            data = cursor.fetchone()
            old_msg_id = data[0] if data else 0

            if old_msg_id != 0:
                try:
                    old_msg = await channel.fetch_message(old_msg_id)
                    await old_msg.delete()
                except discord.NotFound:
                    pass
                except discord.HTTPException:
                    pass

            # Limpiar votos
            cursor.execute('DELETE FROM votos_turing')
            
            # Elegir pregunta al azar
            pregunta_texto = random.choice(self.preguntas)
            opcion_a = pregunta_texto
            opcion_b = "N/A"

            if " O " in pregunta_texto:
                partes = pregunta_texto.split(" O ")
                opcion_a = partes[0].replace("¿", "").replace("?", "").strip()
                opcion_b = (" O ".join(partes[1:])).replace("?", "").strip().capitalize()

            titulo = f"🧠 TEST DE TURING | Secuencia {titulo_extra}" if titulo_extra else "🧠 TEST DE TURING | Secuencia Semanal"
            embed = discord.Embed(
                title=titulo,
                description="*Analice las variables y seleccione su realidad preferente.*",
                color=0x11806A
            )
            embed.add_field(name="🔵 Opción Primaria", value=f"{opcion_a}", inline=False)
            embed.add_field(name="\u200b", value="`— PROCESANDO DIVERGENCIA —`", inline=False)
            embed.add_field(name="🔴 Opción Secundaria", value=f"{opcion_b}", inline=False)
            embed.set_footer(text="Participar otorga: 200 XP")

            mencion_rol = f"<@&{self.ROL_LUDICA_ID}>"
            
            msg = None
            try:
                file = discord.File("pregunta.png", filename="pregunta.png")
                embed.set_thumbnail(url="attachment://pregunta.png")
                msg = await channel.send(content=mencion_rol, file=file, embed=embed)
            except FileNotFoundError:
                msg = await channel.send(content=mencion_rol, embed=embed)

            await msg.add_reaction("🔵")
            await msg.add_reaction("🔴")
            
            # Guardar estado
            now = datetime.datetime.now()
            anio_actual, semana_actual, _ = now.isocalendar()
            cursor.execute('UPDATE estado_turing SET ultima_semana = ?, ultimo_anio = ?, msg_id = ? WHERE id = 1',
                           (semana_actual, anio_actual, msg.id))
            conn.commit()
            return msg
        finally:
            conn.close()

    @tasks.loop(hours=1)
    async def check_weekly_post(self):
        now = datetime.datetime.now()
        if now.weekday() != self.DIA_PUBLICACION: return
        if now.hour < self.HORA_PUBLICACION: return

        anio_actual, semana_actual, _ = now.isocalendar()
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT ultima_semana, ultimo_anio FROM estado_turing WHERE id = 1')
            data = cursor.fetchone()
            last_week, last_year = data
            
            if semana_actual == last_week and anio_actual == last_year:
                return
        finally:
            conn.close()

        channel = self.bot.get_channel(self.CHANNEL_ID)
        if channel:
            await self.publicar_pregunta(channel)
        else:
            print("❌ Error: Canal de Turing no encontrado.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def forzar_turing(self, ctx):
        channel = self.bot.get_channel(self.CHANNEL_ID)
        if channel:
            await self.publicar_pregunta(channel, titulo_extra="(FORZADO)")
        else:
            await ctx.send("❌ Canal de Turing no encontrado.")

async def setup(bot):
    await bot.add_cog(TestTuring(bot))