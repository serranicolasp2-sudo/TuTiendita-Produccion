# Letra de la canción: formulario y plantilla para Claude

## 1. Preguntas para el cliente (por WhatsApp o en el formulario de la web)

Copiá y pegá:

```
¡Gracias por tu pedido! 🎵 Para escribir la canción necesito que me cuentes:

1. ¿Para quién es? Su nombre y cómo le dicen (y cómo se pronuncia, si es raro).
2. ¿Qué es para vos? (mamá, pareja, abuela, amiga…) ¿Desde cuándo se conocen?
3. ¿Cuál es la ocasión? (Día de la Madre, cumpleaños, aniversario, porque sí)
4. Contame 2 o 3 recuerdos o anécdotas con esa persona. Cuanto más concretos, mejor (un lugar, una comida, una frase que siempre dice).
5. ¿Cómo es? Tres palabras que la describan.
6. ¿Qué le querés decir que nunca le dijiste o que querés repetirle?
7. ¿Qué música le gusta? (balada, cumbia, cuarteto, folklore, rock nacional, bolero, pop, tango…) ¿Voz de hombre o de mujer?
8. ¿Hay algo que NO querés que aparezca? (un tema delicado, alguien que no está)
9. ¿Otros nombres para incluir? (hijos, nietos, mascotas)
```

Guardá las respuestas en `C:\Pedidos\TC\Pendientes\<pedido>\1-datos\respuestas.txt`.

## 2. Instrucción para la IA (letra + estilo para Suno)

El bot la usa sola (Codex escribe y Claude revisa). Si lo hacés a mano, pegale esto a Claude con las respuestas al final:

```
Escribí la letra de una canción personalizada para regalar, para cantar en Suno.

LETRA
- Español rioplatense con voseo ("vos sabés", "me enseñaste"). Cálido y concreto, sin frases hechas ni cursilerías ("sos mi luz", "ángel del cielo"). Usá los detalles reales de las respuestas: lugares, comidas, frases, apodos.
- No inventes hechos que el cliente no contó ni cambies los que contó.
- El nombre o el apodo de la persona va en el estribillo, como mínimo dos veces.
- Estructura con estas etiquetas de Suno, una por renglón y entre corchetes:
  [Intro] (instrumental, sin letra)
  [Verse 1] 4 a 6 versos
  [Pre-Chorus] 2 a 4 versos
  [Chorus] 4 versos, fácil de recordar
  [Verse 2] 4 a 6 versos, con otra anécdota
  [Chorus]
  [Bridge] 2 a 4 versos, lo que nunca le dijo
  [Final Chorus]
  [Outro] 1 o 2 versos
- Duración según lo que eligió el cliente. Corta (unos 2 minutos): sin [Pre-Chorus] ni [Bridge]. Normal (unos 3 minutos): la estructura completa. Larga (unos 4 minutos): sumá un [Verse 3] antes del [Bridge] y un [Instrumental Break].
- Versos cortos (de 6 a 10 sílabas), rima asonante o consonante simple y métrica pareja dentro de cada sección, para que se pueda cantar.
- Podés sumar etiquetas de arreglo entre corchetes que ayuden al género, en su propio renglón: [Guitar Solo], [Instrumental Break], [Soft], [Build-up], [Big Finish]. Nunca escribas acotaciones entre paréntesis: Suno las canta.
- Pronunciación: escribí los números en letras. Si un nombre se puede leer mal (acentos, nombres extranjeros, apodos), escribilo como se pronuncia (por ejemplo "Yénifer" en vez de "Jennifer") y anotalo en las fonéticas.
- En la letra se puede nombrar a quien sea: personas, artistas, bandas, lugares y lo que contó el cliente (si fueron a ver a Almafuerte, va "Almafuerte"). Nada de lo que el cliente pidió que no aparezca.

ESTILO (campo "Style of Music" de Suno), en inglés
- Etiquetas cortas separadas por comas, no frases. Entre 6 y 10, en este orden, porque Suno les da más peso a las primeras:
  1. género y subgénero, con la época si ayuda ("80s thrash metal", "2000s Argentine rock", "romantic bolero")
  2. tempo en bpm, y el compás si no es 4/4 ("6/8")
  3. ánimo ("nostalgic", "festive", "tender")
  4. dos o tres instrumentos concretos ("palm-muted electric guitars", "bombo legüero", "accordion")
  5. la voz: género, timbre y forma de cantar ("raspy male vocals", "warm female alto, intimate"). Si el cliente eligió "Me da igual", la que mejor le quede al género.
  6. la producción ("live room drums", "warm analog mix", "polished modern mix")
  Si el género es argentino o latino (cuarteto, cumbia, zamba, chacarera, tango, rock nacional), nombralo así y agregá "Argentine Spanish vocals".
- Nada contradictorio ("calm" con "aggressive", "acoustic" con "EDM"). Sin nombres de artistas ni de canciones: Suno los rechaza. Si el cliente dio una canción de referencia (link o nombre), buscala en internet y traducí cómo suena a etiquetas: género, época, tempo, instrumentos, voz, producción, y cómo crece (por ejemplo "slow clean-guitar intro building to heavy double-kick finale").
- Máximo 400 caracteres.

EXCLUIR (campo "Exclude styles" de Suno, en Más opciones): de 0 a 4 cosas que no tienen que sonar ("autotune, english vocals, EDM drops"). Vacío si no hace falta.

Entregá: título (corto, con el nombre o el apodo), letra (con las etiquetas, lista para pegar en Suno modo Custom), estilo, excluir y fonéticas (los nombres que escribiste como se pronuncian, o vacío).

Respuestas del cliente:
[PEGAR ACÁ]
```

Guardá la letra en `2-letra\letra-v1.txt`. Si piden un cambio, guardá `letra-v2.txt` y así sucesivamente, y anotalo con `python cancion.py cambio <pedido> "qué cambió"`.
**En un cambio se toca solo lo que el cliente pidió.** "Está buena la letra pero quiero que suene como tal tema" cambia el estilo y deja la letra igual.

## 3. Estilos de base ("Style of Music")

| Pedido | Estilo para Suno |
|---|---|
| Balada | emotional Spanish pop ballad, 70 bpm, heartfelt, felt piano, acoustic guitar, soft strings, warm female vocals, intimate, polished modern mix |
| Cumbia | Argentine cumbia, 95 bpm, cheerful, accordion, güira, groovy bass, bright male vocals, Argentine Spanish vocals, dance-floor mix |
| Cuarteto | cuarteto cordobés, 120 bpm, festive, piano tumbao, accordion, bright brass, energetic male vocals, Argentine Spanish vocals |
| Folklore | Argentine zamba, 6/8, tender, criolla guitar, bombo legüero, tender female vocals, Argentine Spanish vocals, warm acoustic room |
| Rock nacional | 2000s Argentine rock, 110 bpm, nostalgic, electric and acoustic guitars, live drums, raspy male vocals, Argentine Spanish vocals, warm analog mix |
| Bolero | romantic bolero, 80 bpm, intimate, nylon guitar, requinto, soft bongos, smooth male vocals, Spanish vocals, vintage warmth |
| Tango | modern Argentine tango, 2/4, dramatic, bandoneón, violin, piano, expressive male vocals, Argentine Spanish vocals |
| Infantil | playful children's song, 110 bpm, joyful, ukulele, claps, glockenspiel, bright female vocals, Spanish vocals |

## 4. Antes de grabar la vista previa
- Escuchala entera: ¿dice bien los nombres? ¿se entiende la letra?
- Suno genera 2 versiones por intento: elegí la mejor. **Escuchar no gasta descargas.**
- `python cancion.py previa <pedido>` y le das play desde el principio.
