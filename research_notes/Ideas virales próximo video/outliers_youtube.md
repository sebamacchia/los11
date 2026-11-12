# Outliers de YouTube en documentales/historias de fútbol (ES + EN), 2025-2026

**Método y advertencias sobre los datos.** Casi todos los números salen de los datos públicos de YouTube, bajados el 10/11/2026 con `yt-dlp` desde la pestaña `/videos` de cada canal. Esa pestaña muestra solo videos largos: los Shorts quedan afuera.
- **Cuántos videos se leyeron.** Se tomaron hasta los últimos 400 de cada canal. En los canales con más de 400 videos, "histórico" quiere decir "lo mejor dentro de los últimos 400".
- **Cómo se mide un outlier.** "Nx" = vistas del video ÷ mediana de vistas de los últimos 30 videos largos del canal.
- **Vistas.** Las del listado vienen redondeadas por YouTube (p. ej. "1,4M"). Las cifras exactas (p. ej. 1.756.117) se tomaron del video, una por una, junto con la fecha de subida.
- **Títulos.** Los títulos en español marcados *(trad.)* son la traducción automática al inglés que devolvió YouTube, no el título original. Los títulos sin marca son los originales, recuperados con `lang=es`.
- **Edad del canal.** Para los canales chicos se usa la fecha del video largo más antiguo como aproximación. Puede haber Shorts o videos borrados anteriores.
- **Dónde están los datos crudos.** Quedaron en el scratchpad: `/private/tmp/claude-501/-Users-sebastianmacchia-dev-los11/fb5f1c4d-5b15-4320-85a5-40e6c01cac50/scratchpad/yt/` (`c_<canal>.txt` = listados, `fechas.txt` = fechas y títulos originales).
- **Fuente de cada cifra.** La fuente es la URL del video (`https://www.youtube.com/watch?v=ID`) o la del canal.

## 1. Canales en español: videos más vistos de 2025-2026 y outliers históricos

### Takeaway
Las dos fórmulas que más rinden en español son dos.
- **"El día que…"**: un partido o momento concreto con un verbo fuerte (HUMILLÓ, SE VENGÓ, ARREGLARON), en 8-11 minutos. Así trabajan El Futbol del Alma (México) y Pablo Carrozza (Argentina). Sacan entre 3 y 30 millones de vistas, de 15 a 350 veces su mediana.
- **El "película/historia completa"** de un ídolo o de un título, en 20-55 minutos, con Memorias del Fútbol y EmmaHavokOscuro.

En 2025-2026 los outliers en español son más chicos: 0,5-2 millones. Giraron alrededor del Mundial 2026, Argentina y las humillaciones entre selecciones latinoamericanas, y además aparecieron algunas historias rarísimas de jugadores desconocidos, como Vozinha.

### Cited Findings
**El Futbol del Alma (@ElFutboldelAlma, México)**
- 1,55 M de suscriptores, mediana de 83.000 vistas y duración mediana de 9:11 — [canal](https://www.youtube.com/@ElFutboldelAlma/videos)
- Histórico: "El Día Que MEMO OCHOA HUMILLÓ a NEYMAR y a Toda La Selección Brasileña", 29.637.270 vistas, 10:13, 28/07/2020, unas 350 veces la mediana — [video](https://www.youtube.com/watch?v=PWNYKe-_uKA)
- Histórico: "El Día Que El CHUCKY LOZANO Hizo HISTORIA Y VENCIÓ a ALEMANIA En Un MUNDIAL", unos 15 M, 11:30 — [video](https://www.youtube.com/watch?v=wS9EUhGmmg0)
- Histórico: "El día que el Kun Agüero ganó en el último minuto la Premier League" *(trad.)*, unos 16 M, 8:25 — [video](https://www.youtube.com/watch?v=Y56YZnzBFgs)
- Histórico: "El día que CRISTIANO RONALDO se VENGÓ del ATLÉTICO de MADRID", unos 5,6 M — [video](https://www.youtube.com/watch?v=t-igz_R6_Ew)
- Histórico: "El Día Que CHILE HUMILLÓ A La Selección MEXICANA Por GOLEADA", unos 5,1 M, 7:21 — [video](https://www.youtube.com/watch?v=oetDsqVzhME)
- 2026: "La MAYOR HUMILLACIÓN en la HISTORIA de MÉXICO", 1.096.570 vistas, 9:30, 06/06/2026, unas 13 veces la mediana — [video](https://www.youtube.com/watch?v=zzwnKdS4VV0)
- 2026: "El día que RAPHINHA habló de MÁS y ARGENTINA lo HUMILLÓ", 634.848 vistas, 9:37, 17/10/2026 — [video](https://www.youtube.com/watch?v=cis-nQ7BhAg)
- 2026: "El día que ARGENTINA se quedó sin OXÍGENO y BOLIVIA los HUMILLÓ", 471.093 vistas, 8:49, 25/07/2026 — [video](https://www.youtube.com/watch?v=CZEEzJlA6Jg)

**Pablo Carrozza (@pablocarrozzaok, Argentina)**
- 435.000 suscriptores, 77 videos largos y mediana de 187.000 vistas. Su video largo más antiguo es del 08/06/2020 — [canal](https://www.youtube.com/@pablocarrozzaok/videos)
- Outliers evergreen, todos de 2020-2022:
  - "El día que Maradona y Cannigia nos dejaron sin voz | Argentina vs Brasil 1990", 7.752.504 vistas, 9:18, 29/11/2020, 41 veces la mediana — [video](https://www.youtube.com/watch?v=EFyUG8B6ClY)
  - "El día que Perú y Colombia arreglaron el empate para dejar a Chile afuera del mundial 2018", 5.534.416 vistas, 9:04 — [video](https://www.youtube.com/watch?v=bgWjdjPA2PU)
  - "El día que le tomaron el equipo a Sampaoli | Mundial 2018", 4.489.155 vistas, 21:36 — [video](https://www.youtube.com/watch?v=SkCY2xS7PfQ)
  - "El día que Chile humilló a México ante los ojos del mundo | México vs Chile (0-7)", 3.791.944 vistas, 10:43 — [video](https://www.youtube.com/watch?v=L3IvFoaKMA4)
  - "Lo que significó Madrid para Boca | Final Copa Libertadores 2018", unos 3,3 M, 32:51 — [video](https://www.youtube.com/watch?v=cf4blvCeVI0)
  - "Los 5 robos más escandalosos del fútbol argentino!!", 2.927.076 vistas — [video](https://www.youtube.com/watch?v=F0vY3F9EU-8)
  - "La verdadera historia del GAS PIMIENTA y el PANADERO | Boca - River 2015", 2.649.410 vistas — [video](https://www.youtube.com/watch?v=cF5-Lpt6rPI)
  - "Lo que nadie te contó sobre la pelea Maradona - Verón | Toda la verdad", 2.591.159 vistas — [video](https://www.youtube.com/watch?v=_7h2GYBUgJ4)

**Memorias del Fútbol (@MemoriasFutbol)**
- 1,78 M de suscriptores, mediana de 109.000 vistas y duración mediana de 18:19 — [canal](https://www.youtube.com/@MemoriasFutbol/videos)
- Histórico: "Las noches mágicas del Real Madrid hasta levantar la Decimocuarta" *(trad.)*, unos 19 M, 19:59 — [video](https://www.youtube.com/watch?v=_uFTLtFIBfI)
- Histórico: "Mundial Qatar 2022 (película completa) Argentina campeona" *(trad.)*, unos 18 M, 55:30 — [video](https://www.youtube.com/watch?v=yTfL1UFin_s)
- Histórico: "La Épica GUERRA de CLÁSICOS entre el REAL MADRID de MOURINHO y el BARÇA de GUARDIOLA (2011)", 10.573.440 vistas (lo devolvió una búsqueda de yt-dlp) — [YouTube](https://www.youtube.com/@MemoriasFutbol)
- Histórico: "El título más IMPOSIBLE de la historia del fútbol - LEICESTER CITY Campeón PREMIER LEAGUE", 6.146.551 vistas, 10:57 — [YouTube](https://www.youtube.com/@MemoriasFutbol)
- Histórico: "El mejor gol de cada Mundial (1954-2022)" *(trad.)*, unos 4,3 M, 10:05 — [video](https://www.youtube.com/watch?v=py3vK3sFUJ4)
- 2026: "ESPAÑA Campeona del Mundo 2026 🇪🇸 🏆⭐⭐ La Película de la Segunda Estrella", 1.996.392 vistas, 27:31, 02/08/2026, 17 veces la mediana — [video](https://www.youtube.com/watch?v=27VKumB17kE)
- 2026: "El día que HARRY KANE se puso de PORTERO y pasó ESTO…", 1.096.295 vistas, **2:15**, 27/10/2026 — [video](https://www.youtube.com/watch?v=5rLy5B_HrVI)
- 2026: "El ASCENSO de ESPAÑA 🇪🇸 La MEJOR SELECCIÓN del SIGLO XXI ⭐⭐", 813.159 vistas, 34:08 — [video](https://www.youtube.com/watch?v=QIosUc-Vncg)

**EmmaHavokOscuro (@EmmaHavokOscuro)**
- 2,75 M de suscriptores, mediana de 260.000 vistas y duración mediana de 11:37 — [canal](https://www.youtube.com/@EmmaHavokOscuro/videos)
- Histórico: "La Historia mas COMPLETA de Lionel Messi 1987 - 2023", unos 7,6 M, 42:23 — [video](https://www.youtube.com/watch?v=7ZPAe4uFM4U)
- Histórico: "EL PARTIDO MAS VIOLENTO DEL FÚTBOL | PORTUGAL VS HOLANDA 2006 HISTORIA", 6.009.737 vistas, 10:41 (de una búsqueda; no entra entre sus últimos 400 videos) — [YouTube](https://www.youtube.com/@EmmaHavokOscuro)
- Histórico: "Era el Técnico mas ODIADO y termino ganando el MUNDIAL | SCALONI HISTORIA", 2.632.898 vistas, 22:33, 2023 — [video](https://www.youtube.com/watch?v=FS9xwv0ofII)
- Histórico: "UN AUTOGOL LE COSTO LA VIDA | Andrés Escobar HISTORIA", 2.615.061 vistas, 11:30, 2023 — [video](https://www.youtube.com/watch?v=uWHuUMg4SwA)
- Histórico: "El Hombre que MURIÓ de Pié, la MENTIRA detrás de Roberto Baggio", 2.430.760 vistas — [video](https://www.youtube.com/watch?v=i5POojalVK4)
- Histórico: "Por esto Alemania 2006 fue el ULTIMO de los VERDADEROS Mundiales", unos 2,6 M — [video](https://www.youtube.com/watch?v=paapiMM3JPI)
- Histórico: "La DESGRACIA del FUTBOL | FALCAO la Maldición del TIGRE", unos 1,07 M (de una búsqueda) — [canal](https://www.youtube.com/@EmmaHavokOscuro)
- 2026: "VOZINHA: El Portero electricista de 40 AÑOS", 900.061 vistas, 10:53, 16/06/2026 — [video](https://www.youtube.com/watch?v=66jmceAZY_c)
- 2026: "La TRAICIÓN que Rompio al TRIDENTE mas Diabolico de la Historia", 743.331 vistas, 17:26, 07/09/2026 — [video](https://www.youtube.com/watch?v=1IAOcxJ1yLM)
- 2026: "El mas SALVAJE y EPICO de TODOS los Mundiales | BRASIL 2014 🇧🇷", 726.967 vistas, 27:20 — [video](https://www.youtube.com/watch?v=DeJocNrlUCg)

**Otros canales en español**
- **Retro Fútbol Español (@RetroFutbollEspanol):** 70.900 suscriptores y mediana de 50.500 vistas. Sus primeros videos, de 2023, son los outliers del canal — [canal](https://www.youtube.com/@RetroFutbollEspanol/videos)
  - "La Historia Del Mediocampista Que LITERALMENTE NO PODÍA Hacer Un Pase Normal", unos 2,3 M, 10:24
  - "Cómo Sergio Busquets Engañó a TODOS Haciéndonos Creer Que No Hace Nada", unos 2,2 M, 8:40
  - "La Vergonzosa Decadencia del Fútbol Brasileño", unos 2,0 M
  - "El Arquero Al Que SE LE OLVIDÓ Como Jugar Al Fútbol: Loris Karius", unos 951.000
  - "El CASI Mejor Mediocampista De La Historia: Mesut Ozil", 906.909 vistas (04/06/2023, su primer video largo)
- **Futbol Mítico (@FutbolMitico):** 93.000 suscriptores, mediana de 167.500 vistas y primer video largo del 01/07/2024 — [canal](https://www.youtube.com/@FutbolMitico/videos)
  - Fórmula en serie "Vi todos los partidos de X y descubrí…": "Vi todos los partidos de NICO PAZ y descubrí su nivel real...", 1.211.601 vistas, 23:26, 19/04/2026 — [video](https://www.youtube.com/watch?v=yheYMMQAJfY)
  - Otros videos de la serie: Lamine Yamal (unos 1,6 M), Endrick (unos 1,2 M) y Arda Güler (unos 1,1 M)
  - "El significado oculto de los festejos más famosos" *(trad.)*, unos 1,1 M
  - Camisetas: "¿Por qué estas selecciones NO USAN los COLORES de su BANDERA?", solo 64.719 vistas, 2024 — [video](https://www.youtube.com/watch?v=p6pdbJCHXM4)
- **El Negocio del Fútbol (@ElNegociodelFutbol):** 311.000 suscriptores, mediana de 266.000 vistas y primer video largo de noviembre de 2023. Hace explicadores de negocio y geopolítica — [canal](https://www.youtube.com/@ElNegociodelFutbol/videos)
  - "Cómo la FIFA traicionó a Panini" *(trad.)*, unos 2,6 M
  - "Por qué el sorteo del Mundial NO es aleatorio" *(trad.)*, unos 1,3 M
  - "El Mapa que la CONMEBOL NO QUIERE que Veas", unos 1,1 M
  - "Así se jugaba al fútbol antes… y era HORRIBLE" *(trad.)*, unos 1,1 M
  - "Por qué los clubes están OBSESIONADOS con las camisetas retro" *(trad.)*, 281.162 vistas
- **Diego Yudcovsky (@DiegoYudcovsky, Boca):** 287.000 suscriptores y mediana de 83.000 vistas. Mezcla noticias diarias de Boca con historia, y las piezas de historia ganan — [canal](https://www.youtube.com/@DiegoYudcovsky/videos)
  - "Desarmó el CABARET y armó el MEJOR equipo de la historia | La LIMPIEZA de Bianchi", 704.637 vistas, 32:06, 01/01/2026, 8,5 veces la mediana — [video](https://www.youtube.com/watch?v=hr7qDoERVik)
  - "El año que Boca fue el mejor equipo del mundo" *(trad.)*, unos 521.000
  - "La INTERNA que hundió a Uruguay: Bielsa contra TODOS", 245.521 vistas, 30/06/2026 — [video](https://www.youtube.com/watch?v=LsKAVrghNuA)
- **Las Crónicas de Joaqo (@LasCronicasDeJoaqo):** 1,19 M de suscriptores pero mediana de solo 39.000 vistas. Las "historias tristes" de jugadores le rinden más que las noticias — [canal](https://www.youtube.com/@LasCronicasDeJoaqo/videos)
  - "La HISTORIA de SANTI BELTRAN, el DELANTERO que pasó de ATAJAR sin INFERIORES a ser ÍDOLO en RIVER 😱", 235.861 vistas, 12:07, 01/05/2026, 6 veces la mediana — [video](https://www.youtube.com/watch?v=nG8zc-Ocxnw)
  - "La HISTORIA de BOCA JUNIORS, del ASCENSO por DECRETO y la POBREZA ABSOLUTA a la GLORIA MUNDIAL 😮", 449.461 vistas, 21:59 (de una búsqueda)
- **El Nuevo Sistema (@ElNuevoSistema, Argentina):** 35.300 suscriptores y primer video del 03/07/2024 — [canal](https://www.youtube.com/@ElNuevoSistema/videos)
  - "CELEBRIDADES DEL MUNDO: Argentina los Enamoró - Fútbol, Comida, Pasión", 760.595 vistas, 14:40, 11/06/2025, 22 veces la mediana — [video](https://www.youtube.com/watch?v=L0-zLKLUAaI)
  - "LA SCALONETA: El equipo que cambió nuestra historia (Documental Completo)", 340.051 vistas, 22:10, 03/01/2026 — [video](https://www.youtube.com/watch?v=Gjd3UBHP2P0)
- **Docs largos de canales generalistas:**
  - Dieck Docs (4,64 M de suscriptores): "¿El negocio más RENTABLE del mundo? | FIFA | Documental", 12.396.717 vistas, 49:41, 25/06/2026 — [video](https://www.youtube.com/watch?v=UOKgIdIMN7o)
  - Dieck Docs: Maradona "¿Lo que lo hizo GRANDE… lo DESTRUYÓ?", unos 6,77 M, 1:12:59
  - Farid Dieck: "Lo TACHARON de ARROGANTE | Cristiano Ronaldo | Documental", 23.123.614 vistas, 34:24 (de una búsqueda) — [canal](https://www.youtube.com/@FaridDieckOficial)
- **Cruce con true crime:**
  - Mafia e Historia | Jonah: "Cuando un futbolista fue ASES1NAD0 por un AUTOGOL" (Andrés Escobar), 6.453.819 vistas, 26:09 — [canal](https://www.youtube.com/@MafiaPorJonah)
  - Fusgo: "El Futbolista que DESTRUYÓ su VIDA por una FOTO - Caso Daniel Correa Freitas", 2.236.988 vistas, 29:05 — [canal](https://www.youtube.com/@FusgoHistorias)
- **Canales de opinión y actualidad (no de historia):**
  - La Media Inglesa: 458.000 suscriptores, mediana de 64.000 vistas y videos de unos 33 minutos. Su outlier es "TODA LA VERDAD SOBRE FABRIZIO ROMANO", 582.046 vistas, 03/09/2026 — [video](https://www.youtube.com/watch?v=ZV3htGmOtHM)
  - Mundo Maldini: 1,28 M de suscriptores y mediana de 49.000 vistas. Su máximo es de unos 442.000 (análisis de España campeona del Mundial 2026) — [canal](https://www.youtube.com/@MundoMaldini/videos)
  - Boser Salseo Futbolero (México, escándalos y "icebergs"): 1,15 M de suscriptores. Su máximo es "El Caso Omar Bravo Es PEOR de lo Que Pensábamos", unos 1,1 M — [canal](https://www.youtube.com/@bosersalseof/videos)

### Inferences
- **La fórmula "El día que [ídolo] [verbo fuerte] a [rival]".** Es un partido concreto, de 8 a 11 minutos y con una selección latinoamericana o un ídolo de por medio. Es la que más se repite entre los outliers en español: El Futbol del Alma y Pablo Carrozza tienen ocho o más videos de más de 3 M cada uno. Es justo el formato de LOS 11 (9 minutos, partidos históricos).
- **Las humillaciones y rivalidades entre selecciones latinoamericanas son el tema más rentable de la región.** Ejemplos: México-Chile 0-7, Argentina-Brasil 1990, Perú-Colombia 2018, Argentina-Bolivia en la altura, Ochoa contra Neymar. Despiertan el orgullo de un país y la burla del otro, y el video se comparte entre dos públicos.
- **Los formatos de más de 25 minutos funcionan sobre todo en canales ya grandes,** como Memorias, Dieck o EmmaHavok, y cuando el tema es una "película completa" de algo enorme: un Mundial, Messi, una Champions.
- **En 2025-2026 hay muy pocos canales de historia en español pensados para Argentina con producción propia.** Carrozza sube poco y Yudcovsky y Joaqo mezclan noticias. Es un hueco de mercado, aunque esto es una inferencia hecha a partir de la muestra.

### Gaps
- No encontré un canal llamado "Fútbol Retro" ni "Relatos de Fútbol" que haga documentales. "Relatos" devuelve QUEGOLAZO (@golazoargs), que hace compilados de relatos de los narradores.
- "Hablemos de Fútbol" es el programa de ESPN, no un canal de historia.
- Jijantes es el canal de Gerard Romero (actualidad del Barça y Kings League), no de historia.
- "Historias del Fútbol ES", "5 Minutos de Leyenda", "Crónicas Football Vintage" y "Archivo Futbolero" aparecieron en las búsquedas, pero no los analicé: no llegué a confirmar sus handles.
- No hay datos públicos de CTR ni de retención de ningún canal.

## 2. Canales en inglés: videos más vistos de 2025-2026 y outliers históricos

### Takeaway
En inglés, los outliers de 2025-2026 los están ganando canales **chicos y nuevos** de mini-documentales narrados de 10-17 minutos: Number 9, GALLEX, SombreroFlicks, Top Bins, The Football Narrative y Ahmed's Goal. Sacan entre 1,5 y 5 millones de vistas con 50.000-180.000 suscriptores. Los grandes (Tifo, The Athletic FC, HITC Sevens, Copa90) tienen techos más bajos en relación con su tamaño. Tifo, además, ahora sube sobre todo podcasts largos.

### Cited Findings
**Number 9 (@Number9nine)**
- 119.000 suscriptores, solo unos 41 videos largos (el primero del 28/02/2024) y mediana de 345.000 vistas — [canal](https://www.youtube.com/@Number9nine/videos)
- "Is This The Most Violent Match In Football?", 4.980.844 vistas, 12:20, 27/07/2024 — [video](https://www.youtube.com/watch?v=11Cx9boFjFc)
- "The Day Kylian Mbappé Made An Entire Country Shiver", 4.368.386 vistas, 13:03, 21/11/2024 — [video](https://www.youtube.com/watch?v=pSDzZXdJqo4)
- "The Magician Who Brought Street Football to the World's Biggest Stadiums", 3.579.519 vistas, 16:23, 08/07/2025 — [video](https://www.youtube.com/watch?v=ifodIYxyUtg)
- "When Mocking the Wrong Man Cost Atlético Everything", 3.326.609 vistas, 17:28, 22/10/2025 — [video](https://www.youtube.com/watch?v=kUxuVvPf9PE)
- "How Lampard's Ghost Goal Changed Football Forever", 3.380.020 vistas, 10:43 — [video](https://www.youtube.com/watch?v=5g0uJqW9Bbg)
- Otros:
  - "The Night Courtois Turned Into An Octopus", unos 1,5 M
  - "The Match That Nearly Killed Ronaldo Nazario", unos 1,5 M
  - "How a 16-Year-Old Kid Brought The Mighty France to Its Knees", unos 1,4 M
  - "The Day Football Lost Diego Maradona", 859.758 vistas

**GALLEX Football (@GallexFootball)**
- 69.500 suscriptores y mediana de 139.500 vistas. Empezó en 2022 con clips de Hagi en rumano y pasó al inglés con la fórmula "The Day…" — [canal](https://www.youtube.com/@GallexFootball/videos)
- "EVEN AT 45 YEARS OLD, RONALDINHO SHOCKED THE WORLD IN THIS LEGENDARY FUTSAL MATCH", 5.141.443 vistas, 10:26, 13/02/2026 — [video](https://www.youtube.com/watch?v=nLtTVtA32YM)
- "The Day Gheorghe Hagi DESTROYED Real Madrid", 2.428.312 vistas, 12:13, 04/08/2025 — [video](https://www.youtube.com/watch?v=ZbpS403qRdA)
- "The Day Turkey Made Brazil Suffer And Earned The World's Respect", 2.113.236 vistas, 13:53, 12/11/2025 — [video](https://www.youtube.com/watch?v=yjxORWwZKyQ)
- Otros:
  - "The Day Ronaldinho Left The World Speechless", unos 1,7 M, 8:13
  - "The Day Italy Faced The Biggest Scandal In Football History", 874.564 vistas

**SombreroFlicks (@SombreroFlicks)**
- 73.800 suscriptores y primer video del 15/08/2023. Es un nicho de un solo jugador: Messi — [canal](https://www.youtube.com/@SombreroFlicks/videos)
- Histórico: "When teenage Messi TERRORIZED Juventus and Fabio Capello", unos 5,4 M, 8:19 — [video](https://www.youtube.com/watch?v=DXp3-C2NT5M)
- "When Messi Walked Alone at Anfield", 3.949.520 vistas, 15:05, 21/06/2025 — [video](https://www.youtube.com/watch?v=uoSM16JZ4b0)
- "The day Lionel Messi ascended to Football Immortality", 2.073.267 vistas, 20:56, 17/03/2025 — [video](https://www.youtube.com/watch?v=ro9lARnnWjY)
- "The Night Prime Messi FORCED the Bernabéu Into SILENCE", 1.568.020 vistas, 16:47, 09/02/2026 — [video](https://www.youtube.com/watch?v=_DyLnv0HHIg)

**Top Bins (@TopBinsFootyy)**
- 178.000 suscriptores, primer video del 01/08/2023 y mediana de 72.500 vistas — [canal](https://www.youtube.com/@TopBinsFootyy/videos)
- "How Zidane's Real Madrid BROKE European Football", 3.281.677 vistas, 19:00, 10/2024 — [video](https://www.youtube.com/watch?v=qRLgwCXYVqc)
- "How A Sunday League Hooligan TOOK OVER The Premier League", 2.969.019 vistas, 14:15, 25/04/2025 — [video](https://www.youtube.com/watch?v=7v-lw_8DSlw)
- Otros:
  - "What Happened To The 21 Golden Boy Winners?", unos 2,3 M
  - "The Entire History Of Cheating In Football", unos 1,8 M
  - "How MSN Became Football's Greatest Trio", unos 1,9 M
- Serie 2026 "There Will Never Be Another X": Haaland 539.431 vistas (18/08/2026) y Messi unos 534.000 — [video](https://www.youtube.com/watch?v=EkAh6CRJau8)
- "Every 'Perfect' Performance In Football History", 620.842 vistas, 27/12/2025 — [video](https://www.youtube.com/watch?v=va-xUvc4K50)
- "What Happened To The 20 Most Expensive Football Players?", 669.540 vistas — [canal](https://www.youtube.com/@TopBinsFootyy)

**The Football Narrative (@footballnarrative24)**
- 63.400 suscriptores y primer video largo del 20/09/2024 — [canal](https://www.youtube.com/@footballnarrative24/videos)
- "How a Teenager With ZERO Experience Destroyed a $1 Billion+ Team", 1.428.780 vistas, 10:41, 14/08/2025 — [video](https://www.youtube.com/watch?v=jjp0iAKCQu8)
- "When Was Messi 'Actually' In His Prime?", unos 1,2 M
- "Why Nobody Can Fix Real Madrid", 875.482 vistas, 17:59, 22/09/2026 — [video](https://www.youtube.com/watch?v=cOxUmYBZuA8)
- OutlierKit lo describe así:
  - su grupo temático más grande, con 18 videos, es el de "X Warned Us N Years Ago" ("Guardiola Warned Us 7 Years Ago", 738.000; "Thomas Tuchel Warned Us 7 Years Ago", 445.000);
  - el 75 % de su contenido es evergreen;
  - repetir plantillas de título puede cansar a la audiencia.

  — [OutlierKit](https://outlierkit.com/channel/footballnarrative24)

**Ahmed's Goal (@AhmedsGoal)**
- 426.000 suscriptores. OutlierKit dice que el 99 % de su catálogo son Shorts, y la mediana de sus videos largos es de unas 31.500 vistas — [OutlierKit](https://outlierkit.com/channel/ahmedsgoal)
- "The African Cup Victory That Makes No Sense" (Zambia 2012, con la tragedia aérea de 1993 de fondo): 1.756.117 vistas, 13:51, 18/01/2026, unas 54 veces la mediana — [video](https://www.youtube.com/watch?v=-snmf9n6CX0)
- "The player who didn't deserve to be betrayed", 216.721 vistas, 12/10/2025 — [video](https://www.youtube.com/watch?v=eENklX7iGuU)
- Sus títulos que no rindieron: "The worst lie in football history" (unos 43.000) y "The most rigged World Cup run of all time" (unos 36.000) — [OutlierKit](https://outlierkit.com/channel/ahmedsgoal)

**Polyglot Sport (@PolyglotSport)**
- 53.000 suscriptores, primer video del 18/10/2023 y mediana de 155.500 vistas, muy por encima de su número de suscriptores — [canal](https://www.youtube.com/@PolyglotSport/videos)
- "The WORST World Cup of Each Winner", 1.084.732 vistas, 18:59 — [video](https://www.youtube.com/watch?v=_57an0f8wQI)
- "The WORST Player of Each World Cup Final", 875.633 vistas, 27/08/2026 — [video](https://www.youtube.com/watch?v=4_cxLolXAfw)
- Otros:
  - "The ENTIRE History of the 2014 World Cup (Every Round)", unos 1,1 M, 28:54
  - "The BIGGEST UNDERDOG of Each World Cup (1994 - 2022)", unos 814.000

**Tifo Football (@Tifo)**
- 1,83 M de suscriptores y mediana de 150.000 vistas. La duración mediana de sus últimos 30 videos es de 67 minutos, porque ahora sube podcasts — [canal](https://www.youtube.com/@Tifo/videos)
- Sus outliers históricos son explicadores de 4 a 7 minutos:
  - "Why are footballers addicted to Snus?", unos 1,6 M
  - "Why Original Ronaldo is so hard to compare", unos 1,5 M
  - "The story of Saddam Hussein's psychopath son", unos 1,2 M, 7:17
  - "Why did Italian football fall?", 770.104 vistas
- 2026: "How Barcelona beat Real Madrid to Rodri's transfer", 773.592 vistas, 6:41, 31/08/2026 — [video](https://www.youtube.com/watch?v=TPlm_LirWvI)

**Otros grandes**
- **Copa90:** 1,34 M de suscriptores y mediana de 106.000 vistas — [canal](https://www.youtube.com/@Copa90/videos)
  - Outliers sobre hinchadas y derbis peligrosos: "The World's Most Dangerous Game Of Football" (unos 3,9 M, 10:26), "The Indonesian Ultras Rewriting Football Fandom" (unos 3,3 M, 7:01), "They Beat Up Our Goalkeeper: HSV vs St Pauli's Dangerous Derby" (unos 1,7 M)
- **HITC Sevens:** 651.000 suscriptores, mediana de 88.500 vistas y videos de unos 22 minutos — [canal](https://www.youtube.com/@HITCSevens/videos)
  - "Why Hitler Hated Bayern Munich", unos 1,1 M
  - "Why Have Brazil Stopped Winning Everything?", unos 917.000
  - En 2026: "The World's 7 Most Right Wing Football Clubs", unos 494.000
- **The Athletic FC:** 710.000 suscriptores, mediana de 152.500 vistas y contenido táctico. Su máximo es "Why Brighton defenders put their studs on the ball", unos 778.000 — [canal](https://www.youtube.com/@TheAthleticFC/videos)
- **Contexto de mercado:** varios rankings 2025-2026 ponen a Copa90 y HITC Sevens como referentes del documental de fútbol. Son listicles, no analítica — [Storelli](https://storelli.com/blogs/the-storelli-blog/best-football-youtube-channels); [footyapps](https://footyapps.com/category/youtube-channels)

### Inferences
- **Estructura narrativa común de los outliers en inglés:**
  - un protagonista (jugador o selección);
  - un conflicto o antagonista ("the wrong man", "a $1 Billion team", "an entire country");
  - un momento concreto ("The Day", "The Night", "When").

  Cuentan "cómo pasó", no "qué pasó".
- **Messi da para un canal entero** (SombreroFlicks), y "Teenage/Prime Messi contra un gigante" se repite como plantilla.
- **El caso Ahmed's Goal muestra que el tema elegido pesa más que el canal.** Un solo título con misterio ("…That Makes No Sense") sobre una historia emotiva y poco conocida sacó 54 veces la mediana, mientras los títulos de "mentira/escándalo" genéricos fracasaron.

### Gaps
- No logré ubicar el handle de **Hand of Football (HoF)**: la búsqueda devuelve el Pro Football Hall of Fame. Tampoco "Brodie", "Ali Football", "Footballer Facts", Hayters ni 442oons. "Seb Football" resultó ser SebFUT, un canal de desafíos, no de documentales. Quedan sin datos.
- No conseguí análisis de Paddy Galloway sobre canales de fútbol. Su canal es de estrategia de YouTube en general y está casi inactivo según OutlierKit — [OutlierKit](https://alpha.outlierkit.com/resources/paddy-galloway-growth-strategy/)

## 3. Qué categorías de tema ganan

### Takeaway
Las categorías con más outliers son siete.
1. **"El día que…"**: humillación, venganza o hazaña en un partido concreto.
2. **Tragedias y muertes**: Andrés Escobar, Zambia, Correa Freitas.
3. **Escándalos, arreglos y robos.**
4. **Milagros de underdog**: Leicester, Zambia, Vozinha, Turquía.
5. **Del odio a la gloria (redención)**: Scaloni.
6. **Violencia**: los partidos más violentos.
7. **Ídolos absolutos**: Messi, Maradona, Ronaldinho, Cristiano.

Camisetas y estadios rinden poco como tema principal, salvo que se cuenten como dinero/negocio o peligro/hinchadas.

### Cited Findings
- **"El día que…" / humillación / venganza.** Ochoa contra Neymar (29,6 M), Maradona-Caniggia 1990 (7,75 M), México-Chile 0-7 (3,79 M), CR7 se vengó del Atlético (unos 5,6 M), Hagi destruyó al Real Madrid (2,43 M), Mbappé hizo temblar a un país (4,37 M) — [El Futbol del Alma](https://www.youtube.com/watch?v=PWNYKe-_uKA); [Carrozza](https://www.youtube.com/watch?v=EFyUG8B6ClY); [Carrozza](https://www.youtube.com/watch?v=L3IvFoaKMA4); [GALLEX](https://www.youtube.com/watch?v=ZbpS403qRdA); [Number 9](https://www.youtube.com/watch?v=pSDzZXdJqo4)
- **Tragedia y muerte.** Andrés Escobar aparece dos veces entre los outliers: 2,62 M (EmmaHavok) y 6,45 M (Mafia e Historia). Zambia 2012 suma 1,76 M y Correa Freitas 2,24 M — [EmmaHavok](https://www.youtube.com/watch?v=uWHuUMg4SwA); [Ahmed's Goal](https://www.youtube.com/watch?v=-snmf9n6CX0)
- **Muerte de un jugador en 2026 (Jesús de Miguel, Tenerife).** La muerte de Jesús de Miguel tras un choque en un partido generó videos explicativos con millones de vistas. Ejemplo: "Tenerife Footballer Dies After Collision - Doctor Explains Jesus de Miguel Tragedy", 2.155.371 vistas, del canal de Brian Sutterer MD (dato de una búsqueda de yt-dlp). Es noticia, no historia — [YouTube](https://www.youtube.com/@BrianSuttererMD)
- **Escándalo, arreglo o robo.** Perú-Colombia arreglaron el empate (5,53 M), "Los 5 robos más escandalosos del fútbol argentino" (2,93 M), el negocio de la FIFA (12,4 M), "Cómo la FIFA traicionó a Panini" (unos 2,6 M) — [Carrozza](https://www.youtube.com/watch?v=bgWjdjPA2PU); [Dieck Docs](https://www.youtube.com/watch?v=UOKgIdIMN7o); [El Negocio del Fútbol](https://www.youtube.com/@ElNegociodelFutbol/videos)
- **Underdog o milagro.** Leicester (6,15 M), Vozinha (900.000), "The Day Turkey Made Brazil Suffer" (2,11 M), "How a Teenager With ZERO Experience Destroyed a $1 Billion+ Team" (1,43 M). OutlierKit identifica "Underdog vs. giant" como grupo ganador en The Football Narrative — [EmmaHavok](https://www.youtube.com/watch?v=66jmceAZY_c); [GALLEX](https://www.youtube.com/watch?v=yjxORWwZKyQ); [OutlierKit](https://outlierkit.com/channel/footballnarrative24)
- **Redención, del odio a la gloria.** "Era el Técnico mas ODIADO y termino ganando el MUNDIAL | SCALONI HISTORIA", 2,63 M — [video](https://www.youtube.com/watch?v=FS9xwv0ofII)
- **Violencia.** "Is This The Most Violent Match In Football?" (4,98 M), Portugal-Holanda 2006 de EmmaHavok (6,0 M), "The Match That Started The Most Violent Era In Football History" (461.000), Copa90 "The World's Most Dangerous Game Of Football" (unos 3,9 M) — [Number 9](https://www.youtube.com/watch?v=11Cx9boFjFc); [OutlierKit](https://outlierkit.com/channel/footballnarrative24)
- **Ídolos y Argentina.**
  - SombreroFlicks vive solo de Messi y saca entre 1,5 y 5,4 M por video.
  - "La Historia mas COMPLETA de Lionel Messi", unos 7,6 M.
  - En El Nuevo Sistema, el orgullo argentino supera 22 veces su mediana.
  - Boca de Bianchi, 8,5 veces la mediana en Yudcovsky.
  - Gas pimienta Boca-River, 2,65 M.

  — [SombreroFlicks](https://www.youtube.com/@SombreroFlicks/videos); [Yudcovsky](https://www.youtube.com/watch?v=hr7qDoERVik); [Carrozza](https://www.youtube.com/watch?v=cF5-Lpt6rPI)
- **"Qué pasó con…" (what happened to).** Rinde en formato de lista colectiva: "What Happened To The 21 Golden Boy Winners?" (unos 2,3 M) y "…20 Most Expensive Players?" (669.540). En un solo jugador rinde menos: Dele Alli, de Fesify, 196.039 — [Top Bins](https://www.youtube.com/@TopBinsFootyy/videos)
- **Curiosidades y rarezas.** "The Night Courtois Turned Into An Octopus" (unos 1,5 M), "La Historia Del Mediocampista Que LITERALMENTE NO PODÍA Hacer Un Pase Normal" (unos 2,3 M), "El Arquero Al Que SE LE OLVIDÓ Como Jugar Al Fútbol: Loris Karius" (unos 951.000) — [Number 9](https://www.youtube.com/@Number9nine/videos); [Retro Fútbol Español](https://www.youtube.com/@RetroFutbollEspanol/videos)
- **Camisetas y estadios.**
  - "¿Por qué estas selecciones NO USAN los COLORES de su BANDERA?", 64.719 vistas.
  - Retro kits, desde el lado del negocio, 281.162.
  - "STADIUM TRAGEDIES That Changed Football History (Part 1)" (ElDiaQue), 387.898 vistas y 28:54, según la búsqueda.

  — [Futbol Mítico](https://www.youtube.com/watch?v=p6pdbJCHXM4); [ElDiaQue](https://www.youtube.com/@ElDiaQue)

### Inferences
- **Para LOS 11, los temas de más potencial son partidos históricos con conflicto,** que es exactamente lo que ya hace con Estambul 2005. Le siguen tragedias, escándalos e historias rarísimas.
- **Las camisetas y los estadios conviene contarlos como historias de personas, dinero, peligro o tragedia,** no como "la historia de la camiseta X". Por ejemplo: "El estadio donde…", "La camiseta que la FIFA prohibió".
- **Argentina-Brasil, Boca-River, Maradona, la Scaloneta y Riquelme tienen demanda probada en español.** Sobre Riquelme no encontré ningún outlier documental específico.

### Gaps
- Faltan datos específicos de "dueños locos" y de Riquelme como tema de documental en 2025-2026. No aparecieron en la muestra.
- Tampoco tengo una medición sistemática por categoría (vistas promedio por tema): las conclusiones salen de los outliers observados.

## 4. Patrones de título, duración y el papel de los Shorts

### Takeaway
**Títulos.** Los que ganan son:
- "El día que…", "Cuando…" o "Cómo…", con dos o tres palabras en MAYÚSCULAS y un verbo de conflicto;
- una promesa de verdad oculta ("Lo que nadie te contó", "La verdadera historia", "…That Makes No Sense");
- un superlativo ("la MAYOR HUMILLACIÓN", "el más IMPOSIBLE");
- un sufijo de contexto ("| Argentina vs Brasil 1990").

**Duración.** Los outliers de canales chicos se concentran entre 8 y 17 minutos. Los docs de 25 a 75 minutos funcionan en canales grandes o con temas gigantes.

**Shorts.** Ayudan al descubrimiento, pero no está probado que conviertan en vistas de videos largos. Ahmed's Goal tiene 426.000 suscriptores ganados con Shorts y una mediana de solo unos 31.500 vistas en sus videos largos.

### Cited Findings
- **Plantillas en español:**
  - "El día que [X] [VERBO] a [Y]": El Futbol del Alma y Carrozza, con más de 15 outliers de más de 3 M.
  - "La verdadera historia de…" y "Lo que nadie te contó sobre… | Toda la verdad": Carrozza, con 2,6 M.
  - "La HISTORIA de X, de la POBREZA… a ser ÍDOLO": Joaqo, 6 veces su mediana.
  - "Vi todos los partidos de X y descubrí…": Futbol Mítico, serie de más de 1 M.
  - "El CASI mejor…" y "…que LITERALMENTE NO PODÍA…": Retro Fútbol Español.

  — fuentes en las secciones 1 y 3
- **Plantillas en inglés:**
  - "The Day X…", "When [Mocking/Provoking] the Wrong Man Cost X Everything" y "How X BROKE / TOOK OVER…".
  - "X Warned Us N Years Ago", el grupo más grande de The Football Narrative.
  - "There Will Never Be Another X", "The [WORST/BIGGEST] X of Each Y" y "…That Makes No Sense".

  — [Number 9](https://www.youtube.com/@Number9nine/videos); [OutlierKit](https://outlierkit.com/channel/footballnarrative24); [Polyglot Sport](https://www.youtube.com/@PolyglotSport/videos)
- **Duraciones observadas en los outliers:**
  - El Futbol del Alma: mediana de 9:11, outliers de 7 a 11 minutos.
  - Carrozza: outliers top de 9 a 11 minutos, aunque también tiene de 21 y 32.
  - Number 9: 10 a 17 minutos. GALLEX: 8 a 14. Ahmed's Goal: 13:51. SombreroFlicks: 8 a 21.
  - Memorias: películas de 20 a 55 minutos. Dieck Docs: 35 a 75 minutos.

  — datos de yt-dlp, URLs en las secciones 1 y 2
- **Un video corto en la pestaña de videos largos.** Memorias del Fútbol sacó 1.096.295 vistas con un video de 2:15 ("El día que HARRY KANE se puso de PORTERO…"), publicado como video común y no como Short — [video](https://www.youtube.com/watch?v=5rLy5B_HrVI)
- **Shorts y videos largos (Metricool 2026, 799.718 videos):**
  - el feed de Shorts es la mayor fuente de vistas orgánicas;
  - los suscriptores aportan solo el 11 % de las vistas;
  - los canales que publican unos 5 Shorts por mes promediaron 8.789 vistas por video largo, contra 4.364 los que no publican Shorts. Es una correlación, no una causa.

  — [Tubefilter](https://www.tubefilter.com/2026/08/03/youtube-shorts-long-form-study-metricool/amp/)
- **AIR Media-Tech (18.000 canales, 03/2025-03/2026):** en la mayoría de los nichos, los canales que mezclan Shorts y videos largos tienen más suscriptores. En gaming es al revés: los que solo suben videos largos tienen un 85 % más — [AIR](https://air.io/en/audience-growth/do-youtube-shorts-help-your-long-form-videos-grow-data-from-18000-channels)
- **vidIQ (cohorte 2025):** según el resumen del buscador, los videos largos convierten suscriptores de forma más eficiente (alrededor de 1 suscriptor cada 106 vistas, contra unas 505 vistas por suscriptor en los Shorts). La cifra viene de un resumen secundario y conviene verificarla — [vidIQ](https://vidiq.com/research/youtube-first-10-videos-study/)
- **Little Dot (2026):** para 2025, el promedio de vistas por video se había emparejado entre formatos cortos, largos y ultra largos — [Tubefilter](https://tubefilter.com/2026/02/12/little-dot-youtube-video-length-whitepaper-viewer-habits-2026)
- **Ahmed's Goal:** 99 % de Shorts y 426.000 suscriptores, pero la mediana de sus últimos videos largos es de unas 31.500 vistas — [OutlierKit](https://outlierkit.com/channel/ahmedsgoal)

### Inferences
- **Los 9 minutos de LOS 11 caen en la franja ganadora de los canales chicos** (8-14 minutos).
- **Los Shorts conviene usarlos como recortes del momento clave de cada documental** (el gol, el giro), con un título que remita al video largo. Lo que no conviene es construir el canal sobre Shorts, porque los suscriptores que llegan por Shorts no parecen ver videos largos (caso Ahmed's Goal).
- **Mayúsculas.** En español, los títulos con dos o tres palabras en mayúsculas son la norma entre los outliers latinoamericanos. Igual habría que decidir si encajan con la estética "Técnica" del canal, porque Carrozza obtiene outliers con poca mayúscula.

### Gaps
- No hay datos públicos de CTR ni de retención por longitud de título.
- No encontré estudios específicos de Shorts en el nicho de historia del fútbol.

## 5. Canales chicos nuevos que despegaron rápido (2024-2026)

### Takeaway
Hay varios casos de canales que empezaron entre 2023 y 2024 y en 1-2 años tienen medianas de 50.000-350.000 vistas y outliers de 1,5-5 millones con menos de 200.000 suscriptores. El ratio vistas/suscriptor muy alto indica que el tráfico viene del algoritmo (Inicio/Sugeridos), no de la base de suscriptores.
- **En inglés:** Number 9, GALLEX, SombreroFlicks, The Football Narrative, Polyglot Sport y Top Bins.
- **En español:** Retro Fútbol Español, Futbol Mítico, El Nuevo Sistema y El Negocio del Fútbol.

### Cited Findings
**En inglés**
- **Number 9:**
  - primer video largo del 28/02/2024 y unos 41 videos;
  - 119.000 suscriptores y mediana de 345.000 vistas;
  - cinco videos de más de 3,3 M entre julio de 2024 y octubre de 2025.

  — [canal](https://www.youtube.com/@Number9nine/videos)
- **GALLEX Football:**
  - empezó en 2022 con contenido de Hagi en rumano (primer video: "3 Meciuri în care Ianis Hagi l-a Uimit pe Tatăl Său", 456.713 vistas);
  - con el giro al inglés y a "The Day…" logró 2,4 M (agosto de 2025), 2,1 M (noviembre de 2025) y 5,1 M (febrero de 2026), con 69.500 suscriptores.

  — [canal](https://www.youtube.com/@GallexFootball/videos)
- **SombreroFlicks:**
  - primer video del 15/08/2023 ("When Messi crushed the soul of Prime Manchester United", 1.211.584 vistas, 4:08);
  - 73.800 suscriptores;
  - 3,95 M en junio de 2025.

  — [video](https://www.youtube.com/watch?v=zNQI2pcPs-I)
- **The Football Narrative:**
  - primer video del 20/09/2024 (45.033 vistas);
  - unos 11 meses después, 1,43 M con "How a Teenager With ZERO Experience…";
  - 63.400 suscriptores.

  — [video](https://www.youtube.com/watch?v=jjp0iAKCQu8)
- **Polyglot Sport:** primer video del 18/10/2023 y 53.000 suscriptores, con una mediana de 155.500 vistas, unas 3 veces su número de suscriptores. Su formato son listas comparativas — [canal](https://www.youtube.com/@PolyglotSport/videos)
- **Top Bins:** primer video del 01/08/2023; llegó a 178.000 suscriptores, con 3,28 M en octubre de 2024 y 2,97 M en abril de 2025 — [canal](https://www.youtube.com/@TopBinsFootyy/videos)

**En español**
- **Retro Fútbol Español:** su primer video, del 04/06/2023, sacó 906.909 vistas, y los siguientes, más de 2 M. Pero la mediana actual es de 50.500: el canal despegó con sus primeros videos y después se estancó — [canal](https://www.youtube.com/@RetroFutbollEspanol/videos)
- **Futbol Mítico:** primer video del 01/07/2024; tiene 93.000 suscriptores con una mediana de 167.500 vistas, y su serie "Vi todos los partidos de X" pasa el millón — [canal](https://www.youtube.com/@FutbolMitico/videos)
- **El Nuevo Sistema (Argentina):** primer video del 03/07/2024; con 35.300 suscriptores, sacó 760.595 vistas en junio de 2025 — [video](https://www.youtube.com/watch?v=L0-zLKLUAaI)
- **El Negocio del Fútbol:** primer video de noviembre de 2023; tiene 311.000 suscriptores y una mediana de 266.000 vistas — [canal](https://www.youtube.com/@ElNegociodelFutbol/videos)

**Otros datos**
- OutlierKit estima que The Football Narrative factura entre 1.000 y 4.000 USD por mes. Es una estimación de un tercero — [OutlierKit](https://outlierkit.com/channel/footballnarrative24)
- Existe un estudio de vidIQ sobre los primeros 10 videos de los canales nuevos (julio de 2026), relevante para un lanzamiento. No llegué a leer el contenido completo — [vidIQ](https://vidiq.com/research/youtube-first-10-videos-study/)

### Inferences
- **El patrón común de los casos que despegaron:**
  - un nicho estrecho y repetible (un jugador, un formato de título o una serie);
  - entre 10 y 17 minutos de narración sobre imágenes de archivo;
  - y una plantilla de título que se repite hasta que se agota.
- **El primer outlier suele llegar en los primeros 10-40 videos.** Varios canales nuevos tuvieron sus mejores videos al principio: Retro Fútbol Español y SombreroFlicks. Que el primer video funcione con un tema bien elegido importa más que la frecuencia de subida.
- **Todos estos canales usan imágenes de partidos.** En su caso, el riesgo de Content ID (UEFA/FIFA) se asume o se gestiona. No hay datos de cómo lo manejan.

### Gaps
- No hay información de cómo monetizan estos canales chicos ni de si tuvieron reclamos de Content ID.
- No encontré entrevistas a sus creadores.
- Las fechas de inicio son aproximadas: se tomaron del video largo más antiguo que queda visible.
