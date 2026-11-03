# Narration style, visual pacing and sound design for narrated football history documentaries (YouTube, 2025-2026)

Context: Spanish-language channel "LOS 11". Videos are built from still photos plus some clips, assembled with ffmpeg, and narrated by the ElevenLabs voice "Sebastián" (Latin American Spanish). First video: the 2005 Istanbul final, Liverpool vs Milan.

Note on the state of the tools: as of November 2026, the official ElevenLabs docs list an **Eleven v4** model (`eleven_v4`) and recommend it over v3 for most users. The brief asked about v3 vs multilingual_v2, so v4 has to be considered too.

## Narration writing (sentence length, tone, writing for the ear, context, numbers, storytelling, Spanish variant)

### Takeaway
Write the way you would speak: short sentences, plain words, active voice. Listeners cannot reread, so each line has to be clear the first time. Build suspense through clear stakes, which can be personal, sporting or historical. Write the script so it describes the images you have. Use neutral Latin American Spanish for reach across the region, and Rioplatense only if the channel wants a deliberately Argentine identity.

### Cited Findings
- Keep sentences short and vocabulary simple so listeners can follow. — [Univ. of Delaware, Voices Workshop handout](https://udel.edu/content/dam/udelImages/cas/documents/center-for-political-communication/Voices-Workshop-Handout_chk.pdf) (via search snippet)
- "Writing for the ear is more informal than writing to be read. Imagine you are speaking to someone while you are writing." — [SNO Sites, Writing for Video](https://support.snosites.com/hc/en-us/articles/360052035833-Writing-for-Video) (via search snippet)
- "Readers can re-read the copy, but listeners cannot, unless they have some means to rewind the video." — [UF/IFAS EDIS WC124](https://edis.ifas.ufl.edu/publication/WC124) (via search snippet; the full page failed to load because of a redirect loop)
- Read the script aloud and time it against the target length. — [Teleprompter.com, how to write a video script](https://www.teleprompter.com/blog/how-to-write-a-video-script) (via search snippet)
- Suggested video-essay structure: Hook → Context → Thesis → Argument → Complication → Synthesis → Conclusion. — [Leadde, video essay script](https://leadde.ai/blog/video-essay-script) (via search snippet)
- "It is easier to write words to describe your images, rather than trying to find photos/video to match your words." — [SNO Sites](https://support.snosites.com/hc/en-us/articles/360052035833-Writing-for-Video) (via search snippet)
- Suspense comes from conflict, and conflict comes from personal, social or ethical stakes. Strong documentaries mix external stakes with philosophical ones (values at risk). Higher stakes make the audience care more about the outcome. — [Documentary Film Academy, How to Build Suspense](https://docfilmacademy.com/blog/how-to-build-suspense-in-a-documentary)
- "Neutral Spanish" is not a dialect anyone speaks at home. It is a register that is readable in Mexico City, Bogotá and Buenos Aires. — [Strommen Inc.](https://strommeninc.com/?p=37241) (via search snippet). A La Nación column criticizes it as a commercial label of Mexican origin. — [La Nación, "Neutro a la mexicana"](https://www.lanacion.com.ar/opinion/neutro-a-la-mexicana-nid661089/)
- Rioplatense markers are voseo, sheísmo (ll/y pronounced /ʃ/) and Italian-influenced intonation. One TTS vendor recommends a neutral LatAm voice for maximum reach and Rioplatense for regional audiences. — [SpeechGen, TTS Spanish Argentina](https://speechgen.io/es/tts-spanish-argentina/)
- A casting guide warns against Rioplatense in multi-country LatAm campaigns, because voseo and sheísmo send a regional signal you cannot control. — [VoiceArchive, Agency Guide to Spanish Voiceovers](https://www.voicearchive.com/the-full-agency-guide-to-spanish-voiceovers/)

### Inferences
These are actionable rules derived from the findings above plus standard broadcast practice. They are not separately sourced.
- **Sentence length:** aim for about 8 to 18 words per sentence, with one idea each. Vary the rhythm: two medium sentences, then a very short one for impact ("Tres a cero. En cuarenta y cuatro minutos."). Avoid stacked subordinate clauses. The TTS voice also handles short sentences more cleanly.
- **Tone:** conversational but authoritative. Address the viewer as "tú" or a generic "usted", not "vos", if the voice is neutral. Mixing voseo with a neutral-accent voice like "Sebastián" would sound off. If you want a Rioplatense flavour, do it through vocabulary and attitude, not grammar, or pick a Rioplatense voice.
- **Context for newcomers:** for each new character, say who they are, what they want and what they stand to lose, in one or two sentences. Example: "Rafa Benítez, un técnico español en su primera temporada en Liverpool." For Istanbul 2005, set the stakes before the match: Liverpool had not won the European Cup since 1984, and Milan had Maldini, Kaká, Shevchenko and Pirlo. State plainly why the match matters: it is the greatest comeback in a Champions League final.
- **Numbers and dates:** one number per sentence at most. Round where precision does not matter. Always give the score before naming the scorer, and say the minute in words ("en el minuto cincuenta y cuatro"). Repeat the score after each goal so viewers who joined late can follow. Put the exact numbers on screen as text instead of loading the narration.
- **Rhetorical questions:** use them sparingly, mainly at act transitions, to open a loop that the next section answers ("¿Cómo se remonta un tres a cero en una final?"). This follows the stakes and suspense principle above. I found no specific source on open loops (see Gaps).
- **Concrete details beat adjectives.** Show it with specifics, for example a halftime scene in the dressing room, the "You'll Never Walk Alone" chant heard through the walls, or Dudek's "spaghetti legs" in the penalty shootout, instead of calling something "increíble".
- **Structure for a match story:** hook (the comeback, 3-0 to 3-3, shown in the first 15 seconds) → context (who, where, why it mattered) → first half (the collapse) → halftime (the low point, a moment of silence) → the six-minute comeback → extra time and Shevchenko's double save by Dudek → penalties → legacy.

### Gaps
- I found no 2023-2026 primary sources analysing the script style of Tifo Football, Footballers' Stories or Kings of Football. Searches returned only general profiles; Tifo is described as making complex data easily digestible ([Storybench](https://www.storybench.org/?p=12205)).
- I found no audience data comparing neutral and Rioplatense Spanish on YouTube.
- I found no sourced, specific advice on "open loops" for YouTube history channels.
- I found no sourced words-per-minute target for Spanish narration. A common industry rule of thumb is roughly 150 wpm, but it is unverified here.

## AI voice (ElevenLabs): models, audio tags, punctuation, settings, chunking, numbers, pitfalls

### Takeaway
As of November 2026, ElevenLabs' docs list `eleven_v4` (10,000 characters per request, more than 90 languages, "perfect for long-form narration") and recommend it over v3. `eleven_multilingual_v2` is still described as the "most stable on long-form generations". v3 and v4 support audio tags but not SSML `<break>`; pauses come from ellipses and text structure. Recommended starting settings are stability about 50, similarity about 75 and style 0.

### Cited Findings
- **Models.**
  - `eleven_v4`: 10,000 chars (~10 min), 90+ languages, suited to audiobooks and "Perfect for long-form narration".
  - `eleven_v3`: 5,000 chars (~5 min), 70+ languages.
  - `eleven_multilingual_v2`: 10,000 chars, 29 languages, "Most stable on long-form generations".
  - `eleven_flash_v2_5`: 40,000 chars; numbers are not normalized by default.
  - For highest quality the docs suggest v4 or Multilingual v2.
  - Source: [ElevenLabs Models](https://elevenlabs.io/docs/models)
- The docs recommend Eleven v4 over v3 for most users. Professional Voice Clones "are not fully optimized for Eleven v3, resulting in potentially lower clone quality", so the docs recommend v4 for PVCs and Voice Library voices. — [ElevenLabs, Prompting controls](https://elevenlabs.io/docs/best-practices/prompting/controls); [ElevenLabs, Prompting](https://elevenlabs.io/docs/best-practices/prompting)
- The prompting techniques for v4 also apply to v3. — [ElevenLabs, Prompting](https://elevenlabs.io/docs/best-practices/prompting)
- **Audio tags (v4/v3).**
  - Voice and emotion: `[laughs]`, `[whispers]`, `[sighs]`, `[exhales]`, `[sarcastic]`, `[curious]`, `[excited]`, `[crying]`, `[mischievously]`.
  - Sound effects: `[applause]`, `[clapping]`, `[gunshot]`, `[explosion]`.
  - Experimental: `[strong X accent]`, `[sings]`.
  - Tags work best when the delivery is already in the voice's training data.
  - A tag can be read as a sound-effect request, so describe the voice quality clearly (e.g. "[low, gravelly voice]").
  - Multiple tags can be combined.
  - The long-form narration examples use descriptive tags such as "[Quiet, reflective narration]".
  - Source: [ElevenLabs v3/v4 prompting](https://elevenlabs.io/docs/best-practices/prompting/eleven-v3); [ElevenLabs, Prompting](https://elevenlabs.io/docs/best-practices/prompting)
- A serious voice may not suit playful tags such as `[giggles]`, and a hyped voice will not whisper convincingly. Match tags to the voice. — [ElevenLabs v3 prompting](https://elevenlabs.io/docs/best-practices/prompting/eleven-v3)
- **Punctuation.** Ellipses add pauses and weight. Capital letters increase emphasis. Standard punctuation gives natural rhythm. — [ElevenLabs v3 prompting](https://elevenlabs.io/docs/best-practices/prompting/eleven-v3)
- **Pauses.**
  - v4 and v3 do not support SSML `<break>`. Use ellipses, audio tags and text structure instead.
  - Older models accept `<break time="x.xs" />` up to 3 seconds, but "too many break tags in a single generation can cause instability".
  - Dashes and ellipses are an alternative, but less consistent.
  - Source: [ElevenLabs, Prompting controls](https://elevenlabs.io/docs/best-practices/prompting/controls)
- **v3 stability modes.**
  - Creative: more emotional and expressive, but prone to hallucinations.
  - Natural: closest to the original voice, balanced and neutral.
  - Robust: highly stable but less responsive to directional prompts, similar to v2.
  - Creative or Natural give the most expressive audio tags.
  - Source: [ElevenLabs Prompting v3 (alpha), via search snippet](https://elevenlabs.io/docs/best-practices/prompting). The docs pages fetched today no longer contain this text, so it may be outdated.
  - A third-party guide gives approximate numeric ranges (Creative 0.3–0.5, Natural 0.5–0.7, Robust 0.7–1.0) and notes that higher stability reduces tag responsiveness. — [Runware, directing with audio tags](https://runware.ai/docs/models/elevenlabs-v3/guides/directing-with-audio-tags.md). This is unofficial.
- **General voice settings.**
  - "The most common setting is stability around 50, similarity around 75, and keeping style at 0."
  - Low stability can produce "odd performances that are overly random". High stability can make the voice "monotonous".
  - Style exaggeration: "we recommend keeping this setting at 0 at all times".
  - Similarity and Speaker Boost are not available on v3.
  - Style and Speed sliders are not available on v4.
  - Speed ranges from 0.7 to 1.2 (default 1.0), and extreme values degrade quality.
  - Output is non-deterministic, so generate a few takes and pick the best.
  - Source: [ElevenLabs TTS playground guide](https://elevenlabs.io/docs/product-guides/playground/text-to-speech)
- Pacing is strongly influenced by the voice's source audio; longer continuous samples avoid unnaturally fast speech. — [ElevenLabs, Prompting controls](https://elevenlabs.io/docs/best-practices/prompting/controls)
- **Numbers.**
  - Text normalization is on by default.
  - Smaller models misread numbers: Flash v2.5 reads "$1,000,000" as "one thousand thousand dollars", while Multilingual v2 reads it correctly.
  - Mitigations: expand abbreviations, preprocess with regular expressions, and specify date formats ("01/02/2023" is ambiguous).
  - Source: [ElevenLabs, Prompting controls](https://elevenlabs.io/docs/best-practices/prompting/controls)
- **Pronunciation.**
  - v4 reads IPA between slashes.
  - Multilingual v2 does not support phoneme tags, so use alias tags or phonetic respelling instead.
  - Pronunciation dictionaries are case-sensitive, and only the first match is used.
  - Source: [ElevenLabs, Prompting controls](https://elevenlabs.io/docs/best-practices/prompting/controls); [v3 prompting](https://elevenlabs.io/docs/best-practices/prompting/eleven-v3)
- Emotional guidance text in the prompt may be spoken aloud, so remove it in post. — [ElevenLabs, Prompting controls](https://elevenlabs.io/docs/best-practices/prompting/controls)
- For long v3 narration, split the script into sensible sections because of the 5,000-character limit. Tags are suggestions, not deterministic commands. — [Runware guide](https://runware.ai/docs/models/elevenlabs-v3/guides/directing-with-audio-tags.md) (third-party)

### Inferences
- **Model choice for "Sebastián":**
  - Test `eleven_v4` first (current official recommendation, long-form oriented, supports tags).
  - Fall back to `eleven_multilingual_v2` if v4 drifts in accent or tone across a 10-15 minute video. v2 is documented as the most stable for long-form, but it has no tags.
  - Use v3 only if v4 is unavailable on your plan or API.
  - Run an A/B test on the same 3-4 paragraphs, including one goal-climax passage.
- **Chunking:**
  - Generate per paragraph or beat, about 300-1,200 characters, not per sentence. Per-sentence generation tends to reset intonation, so every sentence sounds like a new start and the prosody across the paragraph is lost.
  - Do not send whole acts either, because errors are costly to regenerate.
  - Insert pauses in ffmpeg between chunks rather than relying on the model: about 0.3-0.5 s between sentences inside a beat, about 0.8-1.5 s between beats, and 2-3 s of silence at dramatic turns.
  - This is my inference. ElevenLabs' API also offers request stitching (`previous_text`/`next_text`) for continuity on some models, but I did not verify that against the docs fetched in this session.
- **Numbers in words:** spell out scores, minutes, years and ages in Spanish in the script ("tres a cero", "dos mil cinco", "minuto cincuenta y cuatro"). This avoids normalization surprises such as "3-0" being read as "tres menos cero" or "2005" being read digit by digit. Write player names phonetically if the voice mispronounces them (e.g. "Shevchenko", "Dudek", "Gerrard" may need respelling such as "Yérrard").
- **Tags:** use them sparingly. Put at most one tag on the few peak lines (e.g. `[excited]` on the goals, `[whispers]` or a "quiet, tense" tag before the penalties), and leave most lines untagged. A serious documentary voice may resist playful tags.
- **Emphasis:** use CAPITALS on a single key word occasionally, and ellipses for suspense ("Y entonces... Gerrard."). Do not overuse either.
- **Settings:**
  - Start at stability ~0.5, similarity ~0.75, style 0, speed 1.0. Use 0.95 for calm passages if the voice rushes.
  - On v3, use Natural, or Creative only for climax chunks, then regenerate if it hallucinates.
- **QA:** always listen to every chunk before assembly. Check for mispronounced names, English words read with a Spanish accent and vice versa ("Liverpool", "Anfield"), and spoken tag text.

### Gaps
- The official numeric ranges for v3 stability presets are not published. The ranges above come from a third-party guide.
- I did not confirm the current official docs on request stitching and `previous_text` for v4/v3.
- I found no official ElevenLabs guidance specific to Spanish (e.g. how "3-0" or Spanish dates are normalized). Test it.

## Visual pacing with stills (seconds per shot, motion, letterboxing, on-screen text, maps, lower thirds)

### Takeaway
Plan for one visual change every ~4-7 s in documentary narration. That works out to roughly 12-20 scene changes per minute in faceless long-form. Faster cuts (2-4 s) suit the hook and action moments. Hold longer (6-12 s) on key photos, maps and score graphics. The best single rule is to change the visual when its meaning has been absorbed, not on a fixed timer. Animate stills (push, pan, crop, highlight) instead of always adding new images.

### Cited Findings
- **Suggested ranges:**
  - Fast hook: 2-4 s.
  - Standard faceless narration: 3-5 s.
  - Documentary storytelling: 4-7 s.
  - Important photograph or evidence: 6-10+ s.
  - Chart or diagram the viewer must read: 5-12+ s.
  - Emotional pause: "as long as the moment earns".
  - History channels specifically: action 2-4 s, standard narration 4-6 s, evidence or maps 6-10 s.
  - Source: [Overseeros, How often should visuals change](https://www.overseeros.com/blog/how-often-should-visuals-change-youtube-video)
- **Dataset (33 long-form faceless videos, 4,412 scenes, 3-20 min):**
  - Median scene length was 3.62-3.70 s; the middle half of videos ran 3.30-4.32 s.
  - 81.2% of scenes were under 6 s, and only 1.3% ran 12 s or longer.
  - The intro (first 30 s) median was 3.20 s, against 3.70 s afterwards.
  - Planning range: about 12-20 scenes per minute.
  - The article says this "does not prove" retention gains; it describes production practice, not viewer outcomes.
  - Source: [Overseeros](https://www.overseeros.com/blog/how-often-should-visuals-change-youtube-video)
- "Change the visual when the viewer has extracted what they need from the current one." Sentence boundaries are grammatical, not visual. A scene change is not the same as a visual change: push, pan, parallax, animated text, highlights or crops can carry a long passage on one image. Add motion before adding assets. — [Overseeros](https://www.overseeros.com/blog/how-often-should-visuals-change-youtube-video)
- One retention checklist suggests adding a zoom or pan to any still held longer than about 4 s. Another suggests no frame should exceed about 30 s. — [Fluxnote, faceless retention 2026](https://fluxnote.io/guides/faceless-shorts-retention-tips-2026); [skills.sh retention editing](https://skills.sh/thecraighewitt/skills/retention-editing)
- Retention statistics such as "82% retention for 2-3 s changes" come from a single unverified blog about Shorts and should not be applied to long-form. — the search summary flagged this (source: [Pixflow](https://pixflow.net/blog/?p=93140))
- Visual variety and pacing are the main retention drivers for faceless long-form documentaries. — [Fluxnote, faceless documentary style 2026](https://fluxnote.io/guides/faceless-documentary-style-videos-2026)

### Inferences
These are practical rules for an ffmpeg and stills pipeline.
- **Pacing by section:**
  - Hook (0-30 s): 2-4 s per image.
  - Context and background: 5-7 s.
  - Goal and comeback sequences: 2-3 s, or real clips.
  - Halftime "low point": 8-12 s holds with slow motion.
  - Penalties: alternate faces of the takers and Dudek at 3-4 s, then hold on Shevchenko's miss.
  - For a 12-minute video, budget about 150-200 visual events (images plus motion or text changes). An event does not have to be a new photo.
- **Motion on every still:** use a slow Ken Burns move, for example 3-6% zoom over the shot with the ffmpeg `zoompan` filter at an upscaled source to avoid jitter. Alternate the direction (in, out, pan left, pan right) so consecutive shots do not repeat. Keep movement slow for calm passages and slightly faster for tension.
- **Vertical or small images:** do not pillarbox on black. Use a blurred, darkened copy of the same image as the 16:9 background, scaled to fill with `boxblur` and a brightness reduction, and overlay the original image sharp in the centre. Black letterboxing is acceptable for archival authenticity, but it reduces screen energy.
- **On-screen text:**
  - Show a lower third the first time each key person appears (name plus role, e.g. "Steven Gerrard · capitán del Liverpool"), for about 3-4 s.
  - Use a persistent or recurring scoreboard element ("LIV 0-3 MIL · 45'") whenever the score changes.
  - Show date and place title cards at act starts ("25 de mayo de 2005 · Estadio Olímpico Atatürk, Estambul").
  - Put the numbers on screen so the narration can stay light.
  - Use the same font and colour system throughout.
- **Maps and graphics:** use a simple animated map (Liverpool → Istanbul) and a formation or lineup graphic, and hold each for 6-10 s so it can be read. A simple 3-0 → 3-3 timeline graphic is very effective for this story.
- **Clips:** use short real clips (5-10 s) only at peak moments. They are the most precious "pattern interrupt", but rights-cleared match footage is a separate copyright issue. UEFA footage is likely to be Content ID-claimed.

### Gaps
- I found no source that measures retention for still-image versus video documentaries specifically. The pacing data is production practice, not outcomes.
- I found no specific source on letterboxing vertical photos or on lower-third duration. The rules above are standard editing practice, not cited.

## Sound design (music level vs voice, silence, SFX, music per act, risers/hits, safe music sources)

### Takeaway
Master to about -14 LUFS integrated with true peaks under -1 dBTP. Keep music about 15-20 dB below the voice during narration, and bring it up in the gaps. Use restraint: too much music is a more common problem than bad music. Use silence or a near-silent layer after big reveals. For music, the YouTube Audio Library is the lowest-risk free source for YouTube-only use. Third-party "royalty-free" tracks can still trigger Content ID.

### Cited Findings
- **Mixing targets:**
  - Duck music roughly 15-20 dB below the voice during speech, and raise it only in gaps.
  - Use sidechain ducking or manual automation.
  - Master to about -14 LUFS integrated with true peaks under -1 dBTP. YouTube turns down louder uploads, so mixing hotter gains nothing.
  - Place SFX so they punctuate a scene without startling the viewer.
  - Source: [IRPR Sound, How to mix audio for YouTube](https://sounddesign.irpr.agency/guides/how-to-mix-audio-for-youtube/)
- **Silence:**
  - When dialogue or music drops out, viewers listen more closely, so silence heightens tension.
  - Silence after a reveal can be powerful.
  - Keeping a faint sub-audible layer preserves emotional weight.
  - Source: [Documentary Film Academy, suspense](https://docfilmacademy.com/blog/how-to-build-suspense-in-a-documentary) and [Krotos, no sound in sound design](https://krotos.studio/blog/no-sound-in-sound-design) (via search summary)
- **Music:**
  - "Most films don't suffer from bad music; they often suffer from too much music."
  - Avoid generic music used only to fill silence.
  - Music should not force an emotion the script and visuals cannot support.
  - Source: [GLCoverage, use of silence in film](https://glcoverage.com/blog/use-of-silence-in-film/) / [Toronto Youth Shorts, Let's keep it quiet](https://www.torontoyouthshorts.ca/blog/lets-keep-it-quiet) (via search summary)
- A documentary script typically marks ambient sound, music and SFX cues, and cues should be marked early. — (search summary of documentary script guides; low-quality PDF sources, so treat as weak)
- **Music licensing:**
  - Tracks downloaded from YouTube Studio's Audio Library are described as copyright-safe and not claimed by Content ID, but only for use on YouTube.
  - Third-party "royalty-free" music can still trigger Content ID if rights holders uploaded reference files.
  - For monetized work, use a Content ID-cleared paid catalog and keep proof of license.
  - Source: [Foximusic, YouTube Audio Library 2026 guide](https://www.foximusic.com/blog/?p=546); [Foximusic, background music 2026](https://www.foximusic.com/blog/what-background-music-can-i-use-on-youtube-guide/)
  - Caveat: Foximusic sells music; I did not fetch YouTube's own help page.

### Inferences
- **Levels for an ffmpeg pipeline:**
  - Normalize the voice to about -16 to -14 LUFS.
  - Set the music bed about 18 dB below the voice under narration. In practice that is roughly -30 to -32 LUFS for the bed alone, or `volume≈0.12-0.18` relative to a full-scale track.
  - Swell the music by about 6-10 dB in pauses and act breaks.
  - Use `sidechaincompress` (voice as key) or manual `volume` envelopes.
  - Finish with `loudnorm=I=-14:TP=-1.5:LRA=11`. TP -1.5 gives margin for lossy encoding.
- **Music per act** (Istanbul example):
  - Cold open: tense pulse.
  - Pre-match context: hopeful or epic.
  - First half (0-3): dark, low strings.
  - Halftime: drop to near-silence, with only a distant crowd singing "You'll Never Walk Alone" (use a generic stadium chant or crowd ambience, not the copyrighted recording).
  - Comeback: rising percussion build.
  - Extra time and Dudek's save: suspended tension.
  - Penalties: heartbeat or minimal pulse, then full release on the final save.
  - Change tracks at act boundaries, not mid-sentence. Crossfade over 1-2 s, or hard-cut on a "hit".
- **Risers and hits:** use a riser of 2-4 s leading into a reveal or act title, and an impact or hit on the cut. Limit them to act transitions and the 3-6 biggest moments per video, or they become noise.
- **SFX:** use a low crowd-ambience bed (about -30 dB below the voice) under match sections, a referee whistle at kick-off, halftime and full time, and a crowd roar swell under each goal. Use camera shutter or flash sounds for photo-montage moments sparingly. Sources: YouTube Audio Library sound effects or a licensed SFX pack.
- **Silence:** drop all music for 1.5-3 s before the key line ("Y entonces, en seis minutos... todo cambió.") and after Dudek's final save, before the celebration audio.

### Gaps
- I found no authoritative 2023-2026 source that gives a precise music LUFS level under VO for YouTube documentaries. The 15-20 dB range comes from one mixing guide.
- I did not fetch YouTube's official Audio Library help page to confirm current licensing terms (e.g. attribution requirements for some tracks).
- I found no sourced breakdown of the sound design used by specific football documentary channels.
