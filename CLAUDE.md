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
- `herramientas/clips.py` — buscar/bajar videos de YouTube (yt-dlp con cookies de Chrome, autorizado por el usuario), hoja de contacto con tiempos, detectar cortes. Fuentes en `material/fuentes/` (+ `fuentes.txt`)
- `herramientas/graficos.py` — intro animada del canal, placas de texto, marcador animado, zócalos (Pillow)
- `herramientas/armar.py` — arma el video (ver docstring para todos los tipos de visual)
- `reports/Retención YouTube documentales fútbol.md` — investigación de reglas de YouTube (hook, ritmo, copyright, IA)
- `.env` — `ELEVENLABS_API_KEY=...` (no compartir)

## Flujo
1. Material a `proyectos/<nombre>/material/`; mirarlo (hoja de contacto con Pillow).
2. Escribir `guion.json`. `python3 herramientas/armar.py proyectos/<nombre> --solo-audio` genera voz/sfx y la duración.
3. Render: sin flags (final) o `--borrador`.

## Dirección del usuario (respetar)
- Fotos FIJAS, enteras, con negro a los costados si son verticales. Nada de zoom/Ken Burns.
- No abrir con goles: empezar con el entretiempo, la tensión y las tribunas.
- Hook primero (cold open, sin saludo), DESPUÉS la intro animada del canal (~3 s).
- Narración natural, frases cortas, explicar el contexto para quien no conoce la historia.

## Video de partidos (pedido del usuario: más video, menos foto)
- Usar clips de goles/festejos/hinchas: `{"archivo": "material/fuentes/x.mp4", "desde": seg, "velocidad": 0.5, "zocalo": ...}`.
- Ubicar momentos con `clips.py hoja` (cada 5 s, luego cada 1 s en los goles) y `clips.py cortes`; no pasarse de un corte de plano.
- Evitar planos de entrevistas/subtítulos en inglés; no poner zócalo donde el video ya trae el nombre. No tapar/quitar el logo UEFA.
- Riesgo asumido por el usuario: Content ID de UEFA. Audio original siempre muteado.
- `--reusar` re-dibuja solo las piezas cuyo visual cambió.

## Reglas de guion (de la investigación)
- 0-25 s: arrancar en el momento de máxima tensión, prometer el "cómo", sin "bienvenidos".
- Cambio visual cada 4-7 s (placas, marcador, zócalos compensan la falta de movimiento).
- Reenganche al cambiar de acto (cada 1-2 min); clímax a los ~2/3; final seco con gancho a otra historia.
- Números, años y minutos ESCRITOS EN LETRAS en `texto` (la voz los lee mejor); en placas van con cifras.
- Silencio/sin música antes de la frase clave (`retardo` y `pausa` largos).
- Cronometrar con `"en": "@frase"` (SFX y cambios del marcador) = cuando el narrador dice esa frase.
- Copyright: evitar video de transmisiones UEFA/FIFA; fotos de Commons con crédito; subir oculto primero y revisar Content ID.
- Verificar los datos (fechas, minutos, goleadores) antes de generar la voz.

## Voz del canal
Sebastián - Deep and Reliable (Voice Library, español latino): `bml6kfu9aNiHKYxhtGuS`, modelo `eleven_v4`
(elegido por el usuario frente a v3 y multilingual_v2). Es el default en armar.py. Plan ElevenLabs: Creator.

## Limitaciones técnicas
- El ffmpeg instalado NO tiene `subtitles` ni `drawtext`: todo texto en pantalla se dibuja con Pillow (graficos.py),
  y los subtítulos salen como .srt aparte.
- Fuentes: DIN Condensed Bold / DIN Alternate Bold (no tienen "·": graficos.py lo cambia por "|").
