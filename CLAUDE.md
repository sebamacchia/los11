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
- `elevenlabs.musica(prompt, segundos, destino)` — genera música instrumental (ElevenLabs Music) a `musica/`
- `reports/Retención YouTube documentales fútbol.md` — investigación de reglas de YouTube (hook, ritmo, copyright, IA)
- `.env` — `ELEVENLABS_API_KEY=...` (no compartir)

## Flujo
1. Material a `proyectos/<nombre>/material/`; mirarlo (hoja de contacto con Pillow).
2. Escribir `guion.json`. `/usr/bin/python3 herramientas/armar.py proyectos/<nombre> --solo-audio` genera voz/sfx y la duración
   (usar `/usr/bin/python3`: el `python3` de Homebrew no tiene Pillow).
3. Render: sin flags (final) o `--borrador`.

## Dirección del usuario (respetar)
- Fotos enteras, con negro a los costados si son verticales. Nada de Ken Burns automático; desde 14/11 SÍ zoom/paneo con intención (hacia el detalle que se nombra) con el tipo "doc" (herramientas/documental.py).
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
