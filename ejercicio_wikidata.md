# Ejercicios de curl sobre Wikidata 

## Ejemplo 1 — Busqueda de entidades en Wikidata
**Consigna:** Realizar una busqueda de la palabra "zelda" en español
**Comando curl:**
`curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=zelda&language=es&format=json" | python3 -m json.tool`


* El valor de searchinfo.search es: [zelda]
* Su id es [Q12395], su LABEL es [The Legend of Zelda] su description es: [1986 action-adventure video game]

## Ejemplo 2 — Obtener una entidad por ID
**Consigna:** Obtener los datos de la entidad Q12395
**Comando curl:**
`curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q12395&format=json&props=labels|descriptions" | python3 -m json.tool`


* Dentro de labels, el valor para español (es) es [The Legend of Zelda] y para ingles (en) es [The Legend of Zelda].
* La descripcion en español es: [videojuego de 1986].

## Ejemplo 3 — Busqueda con lomite
**Consigna:** Buscar la palabra "mario" limitando a 5 resultados.
**Comando curl:**
`curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=mario&language=es&limit=5&format=json" | python3 -m json.tool`

*La lista search tiene exactamente 5 elementos
* El primer resultado tiene el id [Q12379] y su descripcion es [fictional character in the Mario video game franchise].

## Ejercicio Propio 4 — [Modificar comando]
**Consigna:** [maximo 2 resultados y Wikidata tiene que traer exactamente eso: primero el videojuego original de 2011 y segundo la franquicia entera de medios].
**Comando curl:**
`[curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=minecraft&language=en&limit=2&format=json" | python3 -m json.tool]`

* La lista devolvio 2 elementos. El videojuego de 2011 tiene el id Q49740 y su descripcion en ingles es "2011 video game".
* El segundo resultado corresponde a la franquicia de medios, con el id Q25445348 y descripcion "media franchise".
