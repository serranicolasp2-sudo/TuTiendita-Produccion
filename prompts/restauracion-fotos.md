# Instrucciones para restaurar con Codex o ChatGPT

> **El bot ya no usa este archivo.** Desde el 09/10 arma la instrucción solo, foto por foto, con el análisis previo y las referencias de color (`tienda/herramientas/restauracion.py`, decisiones D-23 y D-24). Esto queda para restaurar a mano en ChatGPT.

Uso manual: subí la foto escaneada (o sacada con FotoScan) y pegá la instrucción que corresponda. **Una foto por conversación.** Si la cara cambia, no la corrijas pidiendo más: empezá una conversación nueva.

## Reglas comunes (van siempre al principio)

```
Restaurá esta fotografía antigua. Reglas estrictas, en este orden de prioridad:
1. NO cambies los rasgos de ninguna cara: misma forma de ojos, nariz, boca, cejas, orejas, mandíbula, arrugas, lunares, peinado y expresión. No rejuvenezcas, no embellezcas, no maquilles, no corrijas dientes ni la mirada. Si una parte de una cara está dañada, no inventes rasgos: dejala suave antes que crear algo que no se ve.
2. Mismo encuadre, misma pose, misma ropa, mismo fondo y misma cantidad de personas. No agregues ni saques objetos.
3. Quitá solamente el daño: rayas, dobleces, manchas, polvo, roturas, hongos y zonas descoloridas.
4. Mantené el grano y la textura de una foto de la época; que no parezca una imagen digital moderna ni una pintura.
5. Si una parte está perdida y no se puede deducir con certeza, reconstruila de la forma más simple y neutra posible.
```

## A. Mantener blanco y negro o sepia

```
[reglas comunes]
Dejala en blanco y negro (o en el mismo tono sepia que tiene). Recuperá el contraste y el rango de grises: negros profundos y blancos limpios, sin quemar las caras.
```

## B. Colorear con colores de la época

```
[reglas comunes]
Coloreala con los colores reales que tendría una foto en color de esa época en Argentina (década: [AÑOS 40 / 50 / 60 / 70]), con la paleta apagada y cálida de las copias de entonces, sin saturar. Pieles naturales y distintas para cada persona según su tono. Ropa y fondo con colores plausibles para la época y la clase social, sin inventar estampados.
[Si el cliente dio datos, agregalos: "el vestido era celeste", "ojos marrones", "pelo castaño".]
```

## C. Foto a color desteñida (años 70–90)

```
[reglas comunes]
Es una copia a color desteñida. Corregí la dominante (rojiza, amarilla o verdosa) y devolvele los colores originales, con el aspecto de una copia de laboratorio de esos años.
```

## D. Daño fuerte en una zona (no en la cara)

```
[reglas comunes]
La zona dañada es [describir: la esquina inferior derecha / el fondo detrás de la mujer]. Reconstruí solo esa zona siguiendo lo que se ve alrededor. El resto de la foto queda igual.
```

## Control antes de seguir (lo hacés vos)
- Abrí la **comparativa** que arma `fotos.py procesar` y mirá cara por cara: ojos, nariz, boca, orejas y forma de la cara.
- Si alguien "parece otra persona", se descarta y se rehace. Si la cara original está destruida, la foto no se toma (regla de la marca).
- Guardá la salida de Codex en `2-codex` **con el mismo nombre** que el original en `1-original`.
