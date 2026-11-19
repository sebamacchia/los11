# LOS 11 — canal de YouTube

Claude arma los videos: el usuario pasa material (videos/fotos) y un tema; Claude escribe el guion,
genera voz, efectos y música con ElevenLabs y monta todo con ffmpeg + Pillow. Responder en español.

## Estructura
- `proyectos/<nombre-video>/material/` — fotos y videos (+ `creditos.txt` con licencias para la descripción)
- `proyectos/<nombre-video>/guion.json` — guion por escenas (lo escribe Claude). Ejemplo completo: `proyectos/estambul-2005/guion.json`
- `proyectos/<nombre-video>/salida/` — video final + `subtitulos.srt` + `capitulos.txt` (para la descripción de YouTube)
- `musica/` — música generada con ElevenLabs Music (uso comercial incluido en el plan)
- `herramientas/elevenlabs.py` — voz + efectos, con caché en `.cache/` (no se cobra dos veces el mismo texto)
- `herramientas/fotos.py` — busca/baja fotos libres de Wikimedia Commons y anota créditos (Commons limita con 429 si se baja mucho seguido)
- `herramientas/imagenes.py` — buscador "tipo Google" (DuckDuckGo Imágenes, sin clave) que baja candidatas a `material/candidatas/<búsqueda>/`,
  arma hoja de contacto y marca cada foto como AGENCIA (Getty/Alamy: marca de agua, licencia paga) / PRENSA / LIBRE / OTRA.
  Correr con `herramientas/.venv/bin/python` (tiene ddgs + Pillow). `elegir` copia las elegidas y anota el origen en creditos.txt
- **Manual del canal (v2, 09/11)**: TODO lo que el canal es y puede hacer. Versión para mostrar (con imágenes de cada animación): https://claude.ai/artifact/GZDu5cr8CXi6t5DMQipFDS (fuente `identidad/manual-web/`; republicar con el tool Artifact y esa url).
  Web: `identidad/manual-de-estilo.html` · Drive: Google Doc "Manual del canal — LOS 11 (v2)" en la carpeta LOS11. Leerlo antes de un video nuevo.
- **Catálogo de planos (14/11)**: estilos con nombre en clave (MESA, ZOOM, REVISTA, TITULO, MAQUINA, DIAGRAMA, CANCHA, MARCA,
  JUGADA, FOTO, RELATO; nuevos: ARMADO, RECORTE, RUTA, DOCUMENTO, CLASIFICACION, PROFUNDIDAD) que usan los editores para pedir:
  https://claude.ai/artifact/NvL4sptavQcKLFGSEQ8VDF (fuente `identidad/catalogo-planos/`). Motor: `herramientas/documental.py` (tipo "doc").
- **ESTUDIO (15/11)**: app local para trabajar los 99 estilos de `identidad/estilos-lemo` (web: https://claude.ai/artifact/NXH3kiGV5migZdE6mSWcAe)
  con material del proyecto: `/usr/bin/python3 herramientas/estudio.py` → http://localhost:8770. Cada pieza = `proyectos/<p>/estudio/<pieza>.json`
  (estilo, `T` nombre/título/cifra/año, `textos` original→nuevo, `imagenes` slot→{ruta, zoom, x, y}, `marca` original|mapa|paleta|duotono +
  fuentes, `tiempo` dur/hold, `pedidos` = lo que el usuario le pide a Claude, `codigo` = JS extra `(c,t,T,P)` dibujado encima en 960×540).
  Claude edita ese JSON y la app se recarga sola. Estilos nuevos del canal: `herramientas/estudio/estilos/*.js`.
  Exportar: botón o `estudio.py exportar <p> <pieza>` → `material/animaciones/<pieza>.mp4` (1920×1080, 30 fps) → `{"archivo": "material/animaciones/<pieza>.mp4"}`.
  Recortes sin fondo (rembg) → `estudio/recortes/`.
  **Capas** (`capas` en el JSON, herramientas/estudio/capas.js): texto, imagen, círculo, flecha, resaltador, `estilo` (otro de los 99 mezclado en
  una zona: ventana/achicado, máscara rect/elipse/pantalla, modo de fusión) y `pedido` = pin del usuario {x, y (960×540), desde, texto}.
  "Mirá los pedidos": leer los pins, hacer cada uno (agregando capas o código) y marcarlo `"hecho": true`.
- **MESA DE GUION (15/11)**: http://localhost:8770/mesa (mismo servidor). Conversación humano ↔ Claude escena por escena: narrador · imagen
  (miniaturas) · música y efectos · hilo de mensajes, con el video renderizado sincronizado (tiempos sacados del .srt). Mensajes en
  `proyectos/<p>/mesa/<guion>.json` + bandeja `.cache/mesa_bandeja.jsonl`. Claude escucha con un Monitor sobre la bandeja (y toca
  `.cache/mesa_escucha` para que la página muestre "Claude está escuchando"); responde con `estudio.py responder <p> <guion> <n|general> "texto"`,
  ve lo pendiente con `estudio.py pendientes`. Los "cambio de narración" son propuestas: aplicarlas en la FUENTE (p. ej. construir_intro.py
  genera guion_intro.json), regenerar/renderizar y responder. Ver herramientas/mesa.py.
  PENDIENTE (16/11): publicarla para compartir con el primo en sebastianmacchia.com/los11 (repo PÚBLICO `sebastianmacchiacom`,
  Hostinger con PHP): interfaz PHP + contraseña en Hostinger, material y renders SOLO en Hostinger fuera de git; la Mac
  sincroniza (baja mensajes, sube previews), no queda expuesta. Etapas: Mesa online → sala del director tipo Premiere
  (pistas V/narración/música/efectos/notas + bandeja de lo disponible) → piezas del Estudio. Falta que el usuario diga:
  cómo publica en Hostinger (git o FTP), una contraseña o una por persona, y si Claude contesta solo con límites.
- **VIBE EDITOR (17/11, antes "Sala")**: http://localhost:8770/vibe (mismo servidor del Estudio; /sala también anda). Sala de edición del director para los capítulos en
  carpeta, pensada para reemplazar FilmCraft en las correcciones: video + pistas sincronizadas (piezas con miniatura, narración
  palabra por palabra, música, cada SFX con su nombre y el elemento que lo dispara, notas, y cada capa de animación con nombre),
  stems Voz/Música/SFX para silenciar por separado. El usuario toca algo (o arrastra sobre palabras, o marca 📍 en la imagen),
  elige Guion / Cómo lo dice / Animación / Música / SFX y manda la nota → `proyectos/<p>/mesa/sala_<corte>.json` + bandeja
  (mismo Monitor que la Mesa). Responder: `estudio.py responder argentina-1986 sala_parte4 p4_2 "texto"` (hilo = pieza).
  Las notas traen `t`, `pista`, `elemento` (nombre de capa en carpeta_doc.py), `palabras`, `decir`, `x`/`y` (0..1 del cuadro).
  Desde 18/11 las notas se GUARDAN como borrador (`"borrador": true` en la conversación, no van a la bandeja) y el botón
  "Mandar todo a Claude" las manda juntas (mesa.enviar_borradores: llegan a la bandeja con corte, pieza y segundo).
  Cada corte necesita su manifiesto `<mezcla>.sala.json`: lo escribe `mezcla_parte2.py` (`--manifiesto` = sin re-mezclar);
  palabras con whisper cacheadas en `.cache/whisper_palabras/`. Código: `herramientas/sala.py` + `herramientas/estudio/sala.html`.
- `herramientas/clips.py` — buscar/bajar videos de YouTube (yt-dlp con cookies de Chrome, autorizado por el usuario), hoja de contacto con tiempos, detectar cortes. Fuentes en `material/fuentes/` (+ `fuentes.txt`)
- `herramientas/graficos.py` — intro animada del canal, placas de texto, marcador animado, zócalos (Pillow)
- `herramientas/armar.py` — arma el video (ver docstring para todos los tipos de visual)
- `herramientas/filmcraft.py` — pasa el video armado a un proyecto de FilmCraft (`salida/<archivo>.fcproj`) para editarlo a mano:
  V1 una pieza por visual, A1 voz, A2-A3 efectos, A4 música, C1 subtítulos. Se llama con `armar.py ... --filmcraft`
  (no pisa un .fcproj existente; `--forzar` lo rehace). FilmCraft está en /Applications y su CLI en `herramientas/filmcraft-cli/`
- **Efectos de edit sobre clips** (correr con `herramientas/.venv/bin/python`, que tiene rembg + numpy + scipy):
  - `herramientas/efecto_jugador.py` — JUGADOR (APROBADO 14/11): fondo gris, jugador en color, estela, pelota encendida,
    flash. Puntos de seguimiento a mano en `material/pistas_siglo.json` (`--pistas`).
  - `herramientas/efectos_edit.py <contorno|aura|estallido> <video> <desde> <dur> <salida>`: pruebas en
    `salida/prueba_{contorno,aura,estallido}.mp4` (el usuario aprobó una con "esa!!!!!" pero falta saber cuál).
  - `herramientas/efecto_dibujo.py` — DIBUJO (referencia Klickpin de Messi: fondo liso granate, Argentina pintados,
    rivales en contorno blanco, líneas de cancha dibujadas) para el gol del siglo en la escena 39 (relato de Víctor Hugo,
    `limpias/inglaterra_fifa.mp4` 267.5 + 14 s). Primera prueba automática `salida/prueba_dibujo_gol.mp4`: floja en
    planos abiertos; siguiente paso = puntos a mano por jugador como en JUGADOR.
  - `herramientas/efecto_anime.py` — ANIME (14/11, gol del siglo): filtro cel + tinta y clase `Cinta` (suciedad VHS: color
    corrido, grano, rayas, tracking, cortes rotos; `--suciedad 0..1.6`, `--tiempos 2|3`). Prueba `salida/prueba_anime_gol.mp4`.
  - `herramientas/comfy.py` — mismo pedido con Stable Diffusion local en ComfyUI (`herramientas/comfyui/`, fuera de git; levantar
    con `herramientas/comfyui/.venv/bin/python herramientas/comfyui/main.py --port 8188 --force-fp16`). `--seguir X,Y` sigue
    al jugador de azul; `primerplano` hace caras. En el M2 de 16 GB usar `--ancho 512` (más hace swap). Insertos de cara fija:
    rechazados ("horrible"). Siguiente: video a video en la nube (fal.ai, falta `FAL_KEY` en `.env`).
- **CARPETA (16/11)** `herramientas/carpeta.py`: collage analógico estilo carpeta escolar (recortes a tijera con borde suave,
  texturas de `identidad/texturas/` hechas con Higgsfield, todo se apila sobre lo anterior, sello, tiza, VHS). Intro de Argentina 86:
  `/usr/bin/python3 herramientas/carpeta.py 1986 proyectos/argentina-1986/salida/graficos/intro_1986.mp4 --capas`.
  **Entrega por CAPAS en FilmCraft** (pedido del usuario): `--capas` deja `<salida>_capas/` (una capa ProRes 4444 por elemento,
  `capas.json`, `sonidos/`) y `filmcraft.py capas <carpeta>` arma el .fcproj (una pista por elemento, voz, cada efecto suelto).
  Ante un cambio, rehacer SOLO esa capa: `--solo valderrama,pique`. Versiones nuevas del .fcproj (`_b`, `_c`...), nunca pisar.
  Estado (17/11): intro de Argentina 86 en carpeta, cuatro piezas encadenadas (cada una arranca sobre el último cuadro
  de la anterior): `intro_1986_c` (tramos 1-3) → `carpeta.py medio a` → `intro_1986_medio_a_v2` (24 selecciones,
  "sufriendo" = tribuna del Monumental vs Perú 1985 en B/N, Bilardo cuestionado, as bajo la manga = Diego) →
  `carpeta.py medio c` → `intro_1986_medio_c_v2` (camino/lado B/peluca) → `carpeta.py cierre` → `intro_cierre_f`
  (Bilardo en el DeLorean "M 1986", mano de Dios, bandera). Preview: `intro_1986_completa_v2_preview.mp4`.
  Sacado de la intro (17/11, va más adelante en el video): Maradona/Napoli/pibe de Fiorito/US$ 7.500.000 (pieza b) y el
  2-2 con Perú. El usuario quiere la intro caótica y "después limpiamos".
  Correcciones del Vibe Editor (17/11): sin tiza en toda la intro; "La sede: México" = globo 3D que baja del espacio y
  pinta México (`herramientas/globo.py`, elemento `fn` en `pila`); "el camino" = línea punteada por cada partido
  (`camino_animado` en carpeta.py); textos más cortos en medio a/c (voces en `VOCES_MEDIO`). Como cada pieza arranca
  sobre el último cuadro de la anterior, un cambio en una obliga a rehacer las siguientes (medio a → medio c → cierre)
  y re-mezclar con el comando aprobado. Versiones previas: `*_antes_globo`, `*_guion_largo`, `*_con_tiza`.
  Efectos sueltos para el .fcproj: `/usr/bin/python3 herramientas/sfx_capas.py <pieza>.mp4` (antes de `filmcraft.py capas`).
  Tiempos de palabra: whisper local (`whisper-cli -m .cache/whisper/ggml-large-v3-turbo-q5_0.bin -l es -ml 1`).
  En otra compu, el .fcproj trae rutas absolutas: cambiar `/Users/<usuario>/` (copia `_mac`).
  **Sonido de la intro APROBADO (17/11)**: `mezcla_intro.py --musica musica/intro86_ochentas_a.mp3 --mas-sfx --sfx 0.55
  --vol-musica 0.35 --stems` → `intro_1986_mezcla_80s_a2.mp4`; pasado a FilmCraft con `intro_filmcraft.py` (`<pieza>_capas_mezcla.fcproj`).
  (`sampler.py` + `jazz_intro.py` = jazz con muestras de ElevenLabs: rechazado.)
- **CARPETA DOC / "Vox" (17/11)** `herramientas/carpeta_doc.py` (correr con `herramientas/.venv/bin/python`): el resto del
  video en carpeta TRANQUILA: papel limpio (`identidad/texturas/papel_vox.png`), títulos con resaltador amarillo, citas en
  recortes de diario (`diario_recorte.png`), clips recortados a tijera (NUNCA a pantalla completa), cuadros CONGELADOS y
  agrandados con círculo rojo, trayectorias punteadas, palotes, sellos, lluvia de billetes, empuje lento de cámara.
  Ilustraciones de Higgsfield sobre blanco en `material/collage/` (billete_100, intestinos, moctezuma) → `sin_blanco()`.
  Cuadros congelados en `material/congelados/`. Clips con `src`/`rec` (recorte sin logos/relojes: `FB_REC` Football Flashback).
  - Capítulo 1 "Nadie creía" = `carpeta_doc.py todas --capas` → `p2_1..7` (+ placa `carpeta.py capitulo 1 ...`);
    capítulo 2 "El grupo" = `carpeta_doc.py todas --cap2 --capas` → `p3_1..4` (+ `carpeta.py capitulo 2 "El grupo" ... --antes p2_7.mp4`).
  - Voces: hash de caché en `VOCES` / `VOCES_C2`; textos nuevos en `construir_parte2.py` (precio del pase, enfermedad de Passarella).
    Tiempos de palabra con whisper; en el código `w(t)` = segundo de la palabra + 0.4.
  - Mezcla: `herramientas/.venv/bin/python proyectos/argentina-1986/mezcla_parte2.py --parte 2|3 --stems` →
    `parte2_carpeta.mp4` / `parte3_carpeta.mp4` (música `m86_parte2_80s.mp3` / `m86_cap2_80s.mp3`, tribuna/silbato en `PARTES`).
  - Capítulo 3 "Las camisetas" (17/11) = `carpeta_doc.py todas --cap3 --capas` → `p4_1..4` (voces de guion_j 16-19 en
    `VOCES_C3`; placa `carpeta.py capitulo 3 "Las camisetas" ... --antes p3_4.mp4`; mezcla `--parte 4`, música
    `m86_cap3_80s.mp3`). Ilustraciones Higgsfield nuevas en `material/collage/` (pesa_ton, termometro, plancha, aguja,
    camiseta_lisa, tienda, futbol_americano); congelados `uru_*`. Los cuadros `ing_*` traen el marcador 2-0 arriba:
    recortar SIEMPRE sin él (spoiler) — cajas `ING_ESCUDO`/`ING_NUMERO`.
  - Preview: `salida/argentina-1986_hasta_cap3.mp4` (intro + caps 1-3).
  - Capítulo 4 "La guerra" (18/11) = `carpeta_doc.py todas --cap4` → `p5_1..5` (guion_j 21-25, voces `VOCES_C4`; globo
    3D a Malvinas con la línea de 500 km; 74 palotes; 649/255 sin golpes de sello; Rattín congelado; «Animales»; Azteca;
    0-0 con Diego entre dos ingleses del partido completo `inglaterra_completo.mp4`, recorte `ING1_REC` sin marcador
    ni logo). Placa `carpeta.py capitulo 4 "La guerra" ... --antes p4_4.mp4`; mezcla `--parte 5`, música `m86_cap4_80s.mp3`.
  - Preview: `salida/argentina-1986_hasta_cap4.mp4` (intro + caps 1-4, 6:44).
  - Capítulos 5-9 (18/11) = `carpeta_doc.py todas --cap5..--cap9` → `p6_*` (mano), `p7_*` (gol del siglo), `p8_*`
    (Bélgica), `p9_*` (final), `p10_*` (Mundial de Diego). Jugadas con `jugada()`: tramos y congelados limpios de
    `animaciones/futbol/assets/iv_{mano,siglo,belg2,burru}_*` con círculos y tiras. Relatos reales en `.cache/relatos/`
    (vh_mano, vh_siglo_corto — el original termina en "gracias por ver el video" —, vh_final, tota) van como "voz" en
    `VOCES_C5..C9` (ruta en vez de hash; None = pieza muda, p9_10). Placas `capitulo5..9_1986` (rehacer.py PLACAS).
    Música: ElevenLabs Music no respondió el 18/11 → se reusan pistas viejas del video (`m86_inglaterra`,
    `m86_cap6_mix` = siglo+epica2, `m86_relato`, `m86_final`, `m86_cap9_mix` = gloria+epica2); la mezcla las repite si faltan.
    Si un efecto de ElevenLabs no llega, la mezcla usa `material/sonidos/hinchada_gol.mp3` (silbatos: se omiten).
    `pon()` ya no deja elementos cortados contra el borde. Sin flechas (trayecto sin punta) ni tiza en ningún lado.
  - **MODO TV (18/11, criterio del usuario para TODO el video)**: `modo_tv()` en carpeta_doc.py, se aplica solo al
    renderizar: clips y congelados casi a pantalla completa (900 px de alto, centrados), los gráficos ARRIBA del video
    (lo que estaba sobre el cuadro se muda con él; lo de al costado queda encima, achicado si es grande), el marcador
    como lo pondría la tele (`marcador_tv`: chico, arriba a la izquierda del video), SIN círculos rojos, nombres de los
    jugadores en tiras sobre los congelados (coordenadas revisadas a ojo en `jugada()`), zoom de cámara ≤ 1.05.
    Varios goles seguidos: `goles_juntos()` = mosaico (el primero ocupa todo, al llegar el segundo se achica a un costado y
    sigue corriendo; 3 goles: dos arriba y uno abajo). Grillas de varias fotos/videos a la vez: se respetan.
    `"chico": True` en un elemento lo deja fuera del modo TV; `escena.tv = False` lo apaga en una pieza.
  - PENDIENTE (18/11 noche): nota del Vibe Editor en p5_1 "que lo visual complemente al narrador — APLICÁ ESTO PARA
    TODO": reemplazar los `titulo(...)` que repiten la narración por imágenes (diarios de la época, fotos, clips).
    Detalle en memoria (argentina86-pendientes). Renders en paralelo: ProcessPoolExecutor desde un archivo .py.
  - VIDEO COMPLETO: `salida/argentina-1986_completo.mp4` (16:11, -14 LUFS) = intro + parte2..10 pegados con
    `ffmpeg -f concat -c copy` (lista `salida/graficos/.concat_completo.txt`). Falta la revisión del usuario en el Vibe Editor.
- **Sonidos libres** `herramientas/sonidos.py buscar|bajar` (Openverse, solo CC0 por defecto, crédito a creditos.txt) →
  `material/sonidos/`. Ubicación fina con la skill **real-sfx** (Clipwing, en ~/.claude/skills; hoja de cues de la intro en
  `salida/graficos/intro_1986.cues_realsfx.json`; `mix.py --voice-safe --export-clips <capas>/sonidos`) y **earshot**
  (`uv tool install`, para "escuchar"). En otra compu: reinstalar ambas (github.com/Clipwing/skills, github.com/Leonxlnx/earshot),
  `setup.py init --library main=<material/sonidos> --index`, y `herramientas/.venv` con `uv venv --python 3.11` +
  `uv pip install ddgs pillow numpy scipy "rembg[cpu,cli]" filetype` (rembg = recortes gratis, sin créditos de Higgsfield).
- `elevenlabs.musica(prompt, segundos, destino)` — genera música instrumental (ElevenLabs Music) a `musica/`
- `reports/Retención YouTube documentales fútbol.md` — investigación de reglas de YouTube (hook, ritmo, copyright, IA)
- `.env` — `ELEVENLABS_API_KEY=...` (no compartir)
- **Archivos grandes** (material, salida, música, caché): fuera de git, en Drive `LOS11/repo` con la misma estructura.
  `herramientas/archivos_grandes.py subir|bajar|faltan` (ver `ARCHIVOS_GRANDES.md`). ComfyUI no va: se reinstala.

## Flujo
1. Material a `proyectos/<nombre>/material/`; mirarlo (hoja de contacto con Pillow).
2. Escribir `guion.json`. `/usr/bin/python3 herramientas/armar.py proyectos/<nombre> --solo-audio` genera voz/sfx y la duración
   (usar `/usr/bin/python3`: el `python3` de Homebrew no tiene Pillow).
3. Render: sin flags (final) o `--borrador`.

## Dirección del usuario (respetar)
- **NOTA EDITORIAL DE LOS 11 (18/11, para todo):** el narrador dice algo y la imagen ACOMPAÑA con algo que lo complementa
  (diario de la época, foto, clip); no repetir en texto lo que dice, salvo un dato clave. Fotos variadas y reales de los
  jugadores (nada de `cara()` zoomeada y pixelada fuera de las alineaciones). Sellos de minuto chicos (tam 76).
- **Papel por capítulo (18/11)**: `TEMAS`/`TEMA_CAP` en carpeta_doc.py + `herramientas/marcos.py`: crema+tijera,
  cuadriculado+cinta, kraft+esquineros, cartulina oscura+dentado (Malvinas, la final; tinta crema), diario+copia de
  laboratorio. Propuesta aprobada: `proyectos/argentina-1986/salida/propuesta_papeles.jpg`.
- Fotos enteras, con negro a los costados si son verticales. Nada de Ken Burns automático; desde 14/11 SÍ zoom/paneo con intención (hacia el detalle que se nombra) con el tipo "doc" (herramientas/documental.py).
- Estambul (14/11): no abrir con goles; empezar con el entretiempo, la tensión y las tribunas.
- Hook primero (cold open, sin saludo), DESPUÉS la intro animada del canal (~3 s).
- Narración natural, frases cortas, explicar el contexto para quien no conoce la historia.

## Fotos (decisión del usuario, 14/11 — reemplaza la del 05/11)
- Se pueden usar fotos de prensa/archivo (no solo Commons) cuando la foto cuenta algo que no hay en libre: el usuario asume
  el riesgo ("lo hacen todos los youtubers"). Siempre TRANSFORMADAS al estilo doc (impresas sobre la mesa, recortadas, trama,
  zoom, comentario del narrador), nunca a pantalla completa tal cual, y acreditadas en la descripción.
- Nunca borrar marcas de agua (Getty/Alamy): si la única copia tiene marca, se busca otra foto. Primero Commons/libres.
- Cronología: la foto tiene que ser del momento que se narra (nada de trofeos posteriores, ver sin spoilers).

## Video de partidos (pedido del usuario: más video, menos foto)
- Usar clips de goles/festejos/hinchas: `{"archivo": "material/fuentes/x.mp4", "desde": seg, "velocidad": 0.5, "zocalo": ...}`.
- Ubicar momentos con `clips.py hoja` (cada 5 s, luego cada 1 s en los goles) y `clips.py cortes`; no pasarse de un corte de plano.
- Evitar planos de entrevistas/subtítulos en inglés; no poner zócalo donde el video ya trae el nombre.
- Logos de canal (UEFA, LFCTV...): SACARLOS todo lo posible (pedido del usuario, 09/11; antes era al revés). `armar.py`
  recorta el cuadro lo mínimo para que el logo quede afuera entero (nunca cortado a medias) — tabla `LOGO_ESQUINA`/`LOGO_FRANJA`
  para fuentes nuevas. Textos de la TV (goleador, nombres): enteros o afuera, NUNCA cortados — tabla `TEXTO_TV`.
  Los gráficos HyperFrames usan assets ya recortados (`animaciones/futbol/fondos.sh`).
- Cuando se nombra a un jugador, va su imagen: retratos en `material/retratos/` (cuadros congelados de la presentación
  de equipos, ver `retratos.json`); placas con `"foto"`, y `"tipo": "formacion"` para armar un equipo en la cancha.
- Riesgo asumido por el usuario: Content ID de UEFA. Audio original siempre muteado.
- `--reusar` re-dibuja solo las piezas cuyo visual cambió.

## Reglas de guion (de la investigación)
- Investigación nueva: `reports/Hook títulos y suscripciones YouTube.md` (título sin "| LOS 11" adelante, un solo pedido de
  suscripción a mitad de video, pantalla final de 15-20 s, Content ID de UEFA bloquea o monetiza clips aunque estén muteados).
- Duración de los videos: 9 minutos (decisión del usuario; desde 8 min YouTube habilita mid-rolls). Unas 1.300-1.400 palabras de narración.
- 0-25 s: arrancar en el momento de máxima tensión, prometer el "cómo", sin "bienvenidos".
- Cambio visual cada 4-7 s (placas, marcador, zócalos compensan la falta de movimiento).
- Reenganche al cambiar de acto (cada 1-2 min); clímax a los ~2/3; final seco con gancho a otra historia.
- Números, años y minutos ESCRITOS EN LETRAS en `texto` (la voz los lee mejor); en placas van con cifras.
- Silencio/sin música antes de la frase clave (`retardo` y `pausa` largos).
- Cronometrar con `"en": "@frase"` (SFX y cambios del marcador) = cuando el narrador dice esa frase.
- Copyright: evitar video de transmisiones UEFA/FIFA; fotos de Commons con crédito; subir oculto primero y revisar Content ID.
- Verificar los datos (fechas, minutos, goleadores) antes de generar la voz.

## Voz del canal
**LOS 11 - Narrador**: `3bwJ6wzKqreWHSoA0x43`, modelo `eleven_v4` (default en armar.py). Voz PROPIA del canal,
creada con Voice Design (porteño joven, canchero, calidad estudio): el usuario no quiere voces de la Voice Library
ni clones ajenos. Antes se usaba "Sebastián - Deep and Reliable" (`bml6kfu9aNiHKYxhtGuS`), descartada.
Plan ElevenLabs: Creator, límite 30 voces propias (cuenta llena: hay que borrar una para crear otra).
La API key no tiene permiso voices_write: borrar voces lo hace el usuario desde la web.

## Limitaciones técnicas
- El ffmpeg instalado NO tiene `subtitles` ni `drawtext`: todo texto en pantalla se dibuja con Pillow (graficos.py),
  y los subtítulos salen como .srt aparte.
- Fuentes (desde 08/11, estilo Técnica + Forest): JetBrains Mono y IBM Plex Sans (variables, en `animaciones/futbol/assets/fonts/`).
  Placas y marcador se dibujan sobre el clip del partido más cercano, desenfocado y teñido (o `"fondo": {...}` / `false`).

## Gráficos animados (graficos.py, tipos de visual en armar.py — ver docstring de armar.py)
intro · capitulo (separador con número y barra de progreso) · placa (+ "foto") · marcador · zócalo · formacion (equipo en la
cancha con retratos que aparecen al nombrarlos) · camino (llaves con ida/vuelta/global) · tabla (posiciones con barras,
destacado, línea de copa, distancia, cartel) · palmares (copas en línea de tiempo) · linea (tramos de años o minutos + contador)
· collage (estilo Vox desde 13/11, herramientas/collage.py: fotos sin borde + tags + títulos con resaltador
+ círculos/flechas sobre fondo desenfocado por tramos; reemplaza a las animaciones en Argentina 86 h, ver
proyectos/argentina-1986/construir_h.py) · cambio (sale/entra con fotos) · charla (citas con foto) · altura · mapa (Malvinas) · cifras · corto (camisetas 1-2,
subasta: mini cortometrajes animados) · golpe_estilo "fantasma" con flechas. Relatos reales: sfx con "archivo" en escena muda. Todo se sincroniza con `"en": "@frase"`. Estructura en capítulos con frases puente del narrador.
`--reusar` NO detecta cambios de código en graficos.py: borrar `tmp_*/pNNN_MM.*` de las piezas a rehacer.
