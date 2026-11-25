#set text(lang:"es",region:"MX")
#set par(justify: true)
#show heading.where(level: 1): it => { pagebreak(weak: true); it }
#show heading.where(level: 2): it => { pagebreak(weak: true); it }
#outline()



= Resumen

= Introducción

= Planteamiento del Problema

= Objetivos

= Marco Teórico

= Estado del Arte

= Metodología

= Diseño de la Solución
== Arquitectura General
== Casos de Uso
== Diseño de Interfaces
== Diseño de Escenarios
== Diseño de Recursos Gráficos

= Implementación

Durante la implementación utilicé distintas herramientas y tecnologías, que elegí
tras investigar las ventajas de cada una. El criterio principal fue seleccionar
aquellas que implicaran un reto técnico razonable, para afianzar los conocimientos
adquiridos durante el semestre.

== Herramientas Utilizadas

=== Blender

El proyecto requería objetos modelados en 3D. Decidí usar _Blender_ @blender en
lugar de construir la geometría por código con _moderngl_, ya que esto último
implicaría una inversión considerable de tiempo sin aportar al objetivo del
proyecto. En _Blender_ modelé el cilindro del túnel y el plano que funciona como
suelo, y exporté ambos en el archivo `cilindro.obj`.

Su uso implicó una curva de aprendizaje: modelar, trasladar objetos, desenvolver
las coordenadas UV y corregir la orientación de las caras. Durante el desarrollo
me encontré con dos problemas relevantes.

*Orientación de las caras.* Al implementar la iluminación, el resultado no era el
esperado aunque el código parecía correcto. Para aislar el problema desactivé
temporalmente las restricciones físicas del mundo y así observé que se iluminaban
las caras exteriores del cilindro, cuando la lógica de `fragment.glsl` está
diseñada para iluminar únicamente la superficie interior. Tras investigar,
identifiqué que la causa era la orientación de las caras.

Internamente, la orientación de una cara está definida por el orden en que se
recorren sus vértices, y de ese orden se deriva su vector normal. Una cara con
la orientación invertida tiene, por lo tanto, la normal apuntando hacia el lado
contrario, y como el cálculo de iluminación depende del producto punto entre la
normal y la dirección hacia la lámpara, el resultado se invierte. Al voltear las
caras en _Blender_
se invierte el orden de los vértices y, con ello, las normales exportadas en
`cilindro.obj`, lo que corrigió la iluminación.

*Diferencia de ejes.* _Blender_ usa el eje Z como altura, mientras que mi
programa, siguiendo la convención de OpenGL, usa el eje Y como altura y deja el
Z para la profundidad. Al principio coloqué la cámara en lo que creí era el
centro del cilindro, pero estaba desplazada en Z. Como aún no tenía el manejo
del teclado, pensé que la importación del objeto era incorrecta; más tarde
identifiqué la diferencia de ejes y ajusté el modelo.


#figure(
    table(
    columns: (auto, auto, 1fr),
    align: (left, center, left),
    stroke: none,
    table.hline(y: 0),
    table.header([*Herramienta*], [*Licencia / Enfoque*], [*Observaciones*]),
    table.hline(y: 1),
    [Blender], [GPL / Integral], [Modelado poligonal, UV, renderizado y soporte nativo en Linux.],
    [Autodesk Maya], [Comercial / Educ.], [Estándar en animación y *rigging*; licencia de pago/educativa.],
    [Autodesk 3ds Max], [Comercial / Educ.], [Fuerte en visualización arquitectónica; enfocado en Windows.],
    table.hline(),
    ),
    caption: [Comparación de herramientas para modelado 3D.]
)


=== GIMP

Utilicé _GIMP_ @gimp para construir `atlas.png`, la imagen que contiene todas las
texturas del proyecto. Las texturas base empleadas son:

- Textura difusa de concreto @ref-concreto
- Pared crema @ref-crema
- Banda amarilla @ref-banda
- Hemisferio celeste sur @ref-cielo

Opté por un atlas de 2048 × 2048 píxeles dividido en tres regiones:

- *Región inferior:* concreto, para el suelo.
- *Región superior izquierda:* cielo estrellado del Túnel de la Ciencia.
- *Región superior derecha:* pared crema y banda amarilla, que reproducen los
  pasillos del metro de la CDMX para la entrada y salida.

==== Tabla comparativa de herramientas para manipulación de imágenes

#figure(
    table(
    columns: (auto, auto, 1fr),
    align: (left, center, left),
    stroke: none,
    table.hline(y: 0),
    table.header([*Herramienta*], [*Licencia / Enfoque*], [*Observaciones*]),
    table.hline(y: 1),
    [GIMP], [GPL / Edición raster], [Libre y multiplataforma; útil para ajustes, recortes y atlas UV sin depender de suscripciones.],
    [Adobe Photoshop], [Comercial / Edición raster], [Amplio estándar en la industria, pero sujeto a suscripción de pago.],
    [Krita], [GPL / Arte digital], [Excelente para pintura digital e ilustración; menos centrado en retoque técnico.],
    table.hline(),
    ),
    caption: [Comparación de herramientaspara manipulación de imágenes.]
)


Elegí *Blender* con base en tres criterios: 
- licencia libre, que permite usarlo sin costo durante y después del curso.
- soporte nativo en GNU/Linux, sistema en el que desarrollé y probé el proyecto.
- exportación directa al formato OBJ, junto con herramientas de desenvolvimiento
UV y edición de normales, que fueron necesarias para este proyecto. Las alternativas
comerciales ofrecen funciones avanzadas de animación que el proyecto no requiere.

La razón por la que elegí *GIMP* fue debido a que es una herramienta con la que
ya me encuentro familiarizado además de su soporte nativo en GNU/Linux.


== Tecnologías Empleadas

=== Python

Elegí _Python_ @python como lenguaje principal. La razón de mayor peso fue que es
uno de los lenguajes que mejor domino, lo que me permitió dedicar el tiempo a los
conceptos de la materia (transformaciones, iluminación, texturizado y cámara) y no
a aprender un lenguaje nuevo. Aunque la decisión fue práctica, durante el
desarrollo pude comprobar ventajas concretas:

- *Memoria automática.* Lenguajes como _C_ o _C++_ ofrecen acceso directo a OpenGL
  y podrían ser más rápidos y eficientes, pero exigen manejo manual de memoria y
  más código para el mismo resultado. Con _Python_ me concentré en la lógica
  gráfica.
- *Ecosistema de librerías.* Cada etapa del proyecto se resolvió con una librería
  ya existente: _NumPy_ para los arreglos de la geometría y su conversión a bytes
  para los buffers de la GPU, _Pillow_ para leer `atlas.png`, _PyGLM_ para las
  operaciones con matrices, y _glfw_ y _moderngl_ para la ventana y OpenGL.
- *Depuración.* Los mensajes de error del intérprete indican archivo y línea, lo
  que me permitió ubicar fallas con rapidez.
  En diversas ocasiones llegué a mezclar métodos de diferentes librerías como lo fue
  `tobytes()` de _Pillow_ con `to_bytes()` de _PyGLM_ y el interprete de python me 
  hizó notar el error.
- *Reproducibilidad.* Un entorno virtual (`venv`) junto con `requirements.txt`
  permite instalar las mismas versiones de las dependencias sin conflictos, de modo
  que el proyecto pueda ejecutarse en cualquier distribución de GNU/Linux.

La principal desventaja es el rendimiento: _Python_ es interpretado y más lento que
_C++_. En este proyecto la limitación es poco relevante, porque el trabajo pesado
lo realizan la GPU y librerías implementadas en _C_, y la escena genera pocas
llamadas de dibujo por cuadro; alrededor de 22 render por frame, con estas pocas 
llamadas logré un desempeño promedio de 1000 FPS.

#figure(
  image("recursos/metrica.png", width: 75%),
  caption: [Métrica de FPS en el título],
) <fig:fachada-tunel>

=== Moderngl

_Moderngl_ @moderngl-intro es la librería que comunica el programa con la tarjeta
gráfica: crea el contexto de OpenGL 3.3 core, compila los shaders, administra los
buffers de vértices y la textura, y ejecuta las llamadas de dibujo. Elegí esta
librería porque expone OpenGL moderno con una interfaz sencilla desde _Python_,
y porque su núcleo está implementado en código nativo, por lo que el costo de
usar _Python_ recae principalmente en la lógica de la escena y no en el
renderizado.

Su principal limitación para mí fue desconocer su sintaxis, así que tuve que
aprender desde cero, apoyado en _LearnOpenGL_ @learnopen y en la documentación
oficial de la librería (ver la sección de metodología).


=== glfw

_glfw_ @glfw se encarga de la ventana y del contexto de OpenGL, y de recibir los
eventos del sistema. En el proyecto la utilicé para:

- Solicitar un contexto de OpenGL 3.3 en perfil _core_ con `glfw.window_hint` y
  crear la ventana de 960 × 540 píxeles.
- Leer el teclado (W, A, S, D, `SPACE` y `ESC`) consultando el estado de cada tecla
  en cada cuadro con `glfw.get_key`.
- Capturar el mouse: con `glfw.CURSOR_DISABLED` el cursor queda oculto y atrapado
  en la ventana, y un _callback_ (`set_cursor_pos_callback`) recibe el
  desplazamiento que rota la cámara.
- Proveer el tiempo (`glfw.get_time`), que alimenta el parpadeo de las lámparas, y
  actualizar el título de la ventana con los FPS.
- Presentar cada cuadro con `swap_buffers`; desactivé la sincronización vertical
  con `swap_interval(0)` para poder medir el rendimiento sin tope.

=== PyGLM

_PyGLM_ @pyglm es una implementación en _Python_ de _GLM_, la librería de
matemáticas para gráficos. La utilicé para todas las transformaciones del
proyecto:

- `glm.perspective` para la matriz de proyección (campo de visión de 45° y planos
  de recorte de 0.1 y 1000).
- `glm.lookAt` para la matriz de vista, a partir de la posición de la cámara y su
  dirección.
- `glm.translate` y `glm.scale` para construir la matriz de modelo de cada copia
  del túnel. Las copias impares se escalan con `(1, 1, -1)`, lo que las refleja
  sobre el eje Z para que las uniones sean continuas.
- `glm.vec3`, `glm.normalize` y `glm.cross` para el movimiento de la cámara, por
  ejemplo, el vector lateral al desplazarse con A y D.

Una ventaja es que las matrices de _GLM_ usan el mismo orden por columnas que
_GLSL_, por lo que se envían a los _uniforms_ sin transponerlas.

=== Pillow

_Pillow_ @pillow lee el archivo `atlas.png`. El flujo en `abrirAtlas` es:
abrir la imagen con `Image.open`, voltearla verticalmente, convertirla a RGB y
obtener sus bytes con `tobytes()` para crear la textura en _moderngl_.

El volteo vertical (`FLIP_TOP_BOTTOM`) es necesario porque las imágenes guardan su
origen en la esquina superior izquierda, mientras que las coordenadas de textura de
OpenGL tienen su origen en la esquina inferior izquierda; sin él, el atlas aparecería
invertido. La conversión a RGB garantiza tres canales por píxel,
que es el formato con el que se declara la textura.

=== NumPy

_NumPy_ @numpy aporta los arreglos con los que se prepara la geometría para la GPU.
En el proyecto cumple tres funciones:

- Almacenar posiciones, normales y coordenadas UV leídas del OBJ como arreglos de
  tipo `float32` (`'f4'`), el formato que espera la tarjeta gráfica, y convertirlos
  a bytes con `tobytes()` para crear los buffers.
- Calcular las medidas del cilindro con `min` y `max` por eje, de donde se obtienen
  su centro, radio y largo; estos valores definen la colisión y el espaciado de las
  copias.
- Obtener el valor absoluto del índice de cada copia (`np.abs`) para decidir cuáles
  corresponden a la entrada y salida del túnel.

Su uso en el proyecto es acotado. Pudo hacerse con listas de _Python_ y el módulo
`array`, pero con más código y menor rendimiento al operar sobre los vértices.

=== GLSL

_GLSL_ @glsl es el lenguaje en el que se escriben los _shaders_, programas que se
ejecutan en la GPU. En el perfil _core_ de OpenGL 3.3 no existe el pipeline de
función fija, por lo que los _shaders_ son obligatorios.

El proyecto usa dos etapas:

- *Vertex shader* (`vertex.glsl`): recibe posición, normal y UV de cada vértice
  (`in_posicion`, `in_normales`, `in_uvs`) y los transforma con las matrices de
  modelo, vista y proyección.
- *Fragment shader* (`fragment.glsl`): calcula el color final de cada píxel,
  combinando la textura con la iluminación (ambiente, difuso con atenuación,
  especular y parpadeo con fase por copia).

El programa en _Python_ se comunica con los _shaders_ mediante _uniforms_:
`matriz_vista`, `matriz_proyeccion`, `matriz_traslacion`, `lampara_1`,
`posicion_camara`, `tiempo`, `fase`, `emisivo` y `textura`. El detalle de cada uno
se explica en el apartado de módulos.

== Recursos Gráficos
== Módulos Implementados

=== modelo.py

Una vez modelados los objetos en _Blender_, los exporté en el archivo
`cilindro.obj`. Para poder abrirlo y manipularlo en _Python_ desarrollé este
módulo, que fue el primero en implementarse.

==== Estructura del archivo OBJ

Un archivo OBJ es un formato de texto en el que cada línea comienza con un
prefijo que indica su tipo:

- `o`: nombre del objeto que se describe a continuación.
- `v`: posición de un vértice.
- `vn`: vector normal.
- `vt`: coordenada UV de la textura.
- `f`: cara, formada por referencias a los datos anteriores.

Las caras tienen la forma `f 5/5/2 7/6/2 8/7/2 6/8/2`. Cada grupo tiene el
formato `v/vt/vn` e indica el índice del vértice, de la coordenada UV y de la
normal que corresponden a ese punto de la cara. Los índices empiezan en 1 y son
globales a todo el archivo, es decir, no se reinician en cada objeto. Por ello, al
leerlos en _Python_, se les resta 1 ya que este comienza a contar desde 0.

==== Lectura del archivo

El módulo recorre el archivo línea por línea con un bucle `for` y, según el
prefijo, guarda cada dato en la lista correspondiente. Para `v` se compara con
`"v "` (con espacio) y así no se confunde con `vn` ni `vt`.

#figure(
  ```python
  posiciones, normales, vt = [], [], [] 
  out_pos, out_nor, out_vt = [], [], []
  ```,
  caption: [Listas de entrada y de salida.],
)

Como _Blender_ escribe los vértices, normales y UV de un objeto antes de sus caras,
al llegar a una línea `f` ya se cuenta con todo lo necesario para armarla.

==== Armado de los triángulos

OpenGL dibuja triángulos, pero una cara del OBJ puede tener cuatro o más vértices.
Por ello, cada cara se divide en triángulos que parten del primer vértice: una cara
de $n$ vértices genera $n - 2$ triángulos. El ejemplo anterior, de cuatro vértices,
genera los triángulos `5 7 8` y `5 8 6`.

#figure(
  ```python
  for i in range(1, len(cara) - 1):
      for k in (0, i, i + 1):
          v = cara[k]
          out_pos.append(posiciones[int(v[0]) - 1])
          if objeto == "Cylinder":
              cilindro.append(posiciones[int(v[0]) - 1])
          out_vt.append(vt[int(v[1]) - 1])
          out_nor.append(normales[int(v[2]) - 1])
  ```,
  caption: [Triangulación de las caras y copia de sus datos.],
)

Para cada vértice de cada triángulo se copian su posición, UV y normal a las listas
de salida. Esto repite datos, pero es necesario porque el OBJ usa un índice distinto
para cada tipo de dato, mientras que OpenGL espera un solo conjunto de datos por
vértice. Además, los vértices del objeto `Cylinder` se guardan aparte en la lista
`cilindro`, que se usa más adelante para calcular su centro, radio y largo.

Al terminar de procesar el archivo, las listas de salida se convierten con
_NumPy_ en arreglos de tipo `float32`, listos para crear los buffers de la GPU.

==== Rangos de cada objeto

Al leer una línea `o`, el módulo guarda en un diccionario el nombre del objeto y
la posición, dentro de los arreglos de salida, donde comienzan sus vértices:

#figure(
  ```python
  Objetos = {
      "nombre": len(out_pos)   # índice del primer vértice del objeto
  }
  ```,
  caption: [Diccionario con el inicio de cada objeto.],
)

Con ese valor se calcula, para cada objeto, su inicio y su cantidad de vértices:
la cantidad es la diferencia con el inicio del siguiente objeto, o con el total
de vértices en el caso del último. Estos dos datos son los que recibe cada llamada
de dibujo (`first` y `vertices`) y permiten renderizar por separado el cilindro, la
entrada y salida, y el plano al generar las copias.

==== Medidas del cilindro

Con los vértices del objeto `Cylinder`, guardados en la lista `cilindro`, el módulo
calcula con _NumPy_ el mínimo y el máximo en cada eje. De ellos se obtienen tres
medidas que usa el resto del programa:

- `centro`: punto medio entre el mínimo y el máximo de cada eje.
- `radio`: distancia en el eje X entre el centro y el máximo, es decir, la mitad
  del ancho del cilindro. Se mide en X porque la sección circular del túnel está en
  el plano XY.
- `largo`: diferencia entre el máximo y el mínimo en Z, que es la longitud del túnel.

#figure(
  ```python
  minimos = cilindro.min(axis=0)
  maximos = cilindro.max(axis=0)
  centro  = (minimos + maximos) / 2
  radio   = np.abs(centro[0] - maximos[0])
  largo   = maximos[2] - minimos[2]
  ```,
  caption: [Cálculo de las medidas del cilindro.],
)

==== Copias del túnel y límites en Z

El túnel completo se forma colocando copias del cilindro una tras otra a lo largo de
Z. La lista `lista` contiene el índice de cada copia: se agregan `i` y `-i` para
cada valor de `i` en `range(config.TUNELES)` y se eliminan duplicados con `set`.
Con `TUNELES = 6` resultan los índices de $-5$ a $5$, es decir, 11 copias, y la copia
$i$ se desplaza $i dot L$ unidades en Z, donde $L$ es `largo`.

Estos índices también definen hasta dónde puede avanzar el personaje: desde el
inicio de la primera copia hasta el final de la última, con un margen de 2 unidades
para que la cámara nunca llegue a los extremos abiertos del túnel:

$ z_"inf" = i_"min" dot L - L / 2 + 2 quad quad z_"sup" = i_"max" dot L + L / 2 - 2 $

Para 11 copias, el personaje recorre $11 L - 4$ unidades en Z. // TODO: confirma que el cilindro está centrado en el origen en Z (la fórmula lo supone)s

=== camara.py

Este módulo concentra todo lo relacionado con el personaje: orientación de la
cámara en primera persona, desplazamiento con el teclado, gravedad, salto y
colisiones. Recibe los eventos del mouse y el teclado (vía _glfw_) y entrega a
`main.py` dos datos para construir la matriz de vista: la posición de la cámara
(`v2`) y hacia dónde mira (`direccion`). El vector `v1` es el vector "arriba" del
mundo, `(0, 1, 0)`.

==== Estado de la cámara

El módulo guarda su estado en variables globales: los ángulos `yaw` y `pitch`, la
última posición del mouse, la `direccion`, la posición `v2` (inicia en
`(0, 1.5, 0)`), la velocidad horizontal (`velocidad = 3.0`), la velocidad vertical
`velo_y` y la gravedad (`grav = 7.2`).

==== Orientación con el mouse

La función `mouseCallback` se registra en _glfw_ y se ejecuta cada vez que el mouse
se mueve. Calcula cuánto se desplazó respecto a la posición anterior y suma ese
desplazamiento, multiplicado por la sensibilidad `SENS`, a los ángulos `yaw`
(giro horizontal) y `pitch` (giro vertical). Tres detalles de la implementación:

- El desplazamiento vertical se calcula como `last_y - ypos` porque en la pantalla
  la coordenada Y crece hacia abajo.
- La bandera `primerMouse` evita el salto brusco de la cámara en el primer evento,
  cuando aún no existe una posición anterior.
- El `pitch` se limita a $plus.minus 89$ grados. Así la cámara no da una vuelta
  completa hacia arriba o abajo y la dirección nunca queda paralela al vector
  "arriba", situación en la que la matriz de vista deja de estar bien definida.

La dirección a la que mira la cámara se obtiene con ángulos de Euler @learnopen:
// TODO: confirma que usaste esta fuente para la cámara

$ d_x = cos(theta) cos(phi) quad quad d_y = sin(theta) quad quad d_z = cos(theta) sin(phi) $

donde $theta$ es el `pitch` y $phi$ el `yaw`. El valor inicial `yaw = -90` hace que
la cámara mire hacia $-Z$, a lo largo del túnel.

==== Desplazamiento

La función `movimientoPersonaje` se llama una vez por cuadro. El desplazamiento
sigue estas reglas:

- *Movimiento sobre el suelo.* W y S avanzan y retroceden según la dirección de la
  cámara proyectada sobre el plano horizontal y normalizada. Así, mirar hacia
  arriba o abajo no cambia la velocidad ni permite "volar". (Como el `pitch` se
  limita a 89°, esa proyección nunca es el vector cero.)
- *Movimiento lateral.* A y D se desplazan con el vector perpendicular a la
  dirección y al vector "arriba", calculado con el producto cruz y normalizado.
- *Independencia de la velocidad del equipo.* Cada desplazamiento se multiplica por
  `dt`, el tiempo transcurrido entre cuadros, de modo que el personaje avanza la
  misma distancia por segundo sin importar los FPS.
- `ESC` solicita el cierre de la ventana.

==== Gravedad y salto

La gravedad se simula integrando por pasos de tiempo: en cada cuadro se resta
`grav * dt` a la velocidad vertical y se suma `velo_y * dt` a la altura. Si la
altura cae por debajo de `config.SUELO`, se corrige al nivel del suelo y la
velocidad vertical se anula. Si en ese momento el personaje está sobre el suelo y
se presiona `SPACE`, la velocidad vertical se fija en `config.SALTO` (3.6).
Con esos valores la altura máxima del salto es:

$ h = v^2 / (2 g) = 3.6^2 / (2 dot 7.2) = 0.9 $

en unidades de la escena. // TODO: indica si tomaste 7.2 por ser menor a la gravedad real o por ajuste visual

==== Colisiones

Antes de aplicar el movimiento se calcula una posición candidata
(`posición actual + desplazamiento`) y se verifica que siga dentro del cilindro:

- *Ejes X e Y.* Se calcula la distancia en el plano XY entre la posición candidata y
  el `centro` del cilindro. Si es menor que el `radio`, el movimiento se acepta. Si
  no, se descartan los cambios en X e Y, pero se conserva el avance en Z: el
  personaje se desliza a lo largo de la pared en lugar de quedar atascado.
- *Eje Z.* La coordenada Z de la candidata se limita siempre entre `limite_z_inferior`
  y `limite_z_superior`, calculados en `modelo.py`.

#figure(
  ```python
  posicion_candidata = v2 + vec_mov
  distancia = math.sqrt((modelo.centro[0] - posicion_candidata.x)**2 +
                        (modelo.centro[1] - posicion_candidata.y)**2)
  posicion_candidata.z = max(modelo.limite_z_inferior,
                             min(posicion_candidata.z, modelo.limite_z_superior))
  if distancia < modelo.radio:
      v2 = posicion_candidata
  else:
      v2 = glm.vec3(v2.x, v2.y, posicion_candidata.z)
  ```,
  caption: [Verificación de colisiones con el cilindro.],
)

=== main.py

Es el módulo principal: crea la ventana y el contexto, prepara los datos para la
GPU, ejecuta el bucle de renderizado y genera las copias del túnel. Utiliza los
otros tres módulos: `config.py` para las constantes, `modelo.py` para la geometría
y `camara.py` para el personaje.

==== Inicialización

1. Se inicia _glfw_ y se solicita un contexto de OpenGL 3.3 en perfil _core_.
2. Se crea la ventana y se desactiva la sincronización vertical
   (`swap_interval(0)`) para medir el rendimiento sin tope de FPS.
3. Se crea el contexto de _moderngl_ sobre el contexto de _glfw_, se activa la
   prueba de profundidad (`DEPTH_TEST`) y se compila el programa con el código de
   los dos shaders, leídos desde `shaders/`.
4. Se registra el _callback_ del mouse y se oculta el cursor
   (`CURSOR_DISABLED`).

==== Buffers, textura y VAO

La posición, la normal y la coordenada UV de cada vértice se almacenan en tres
buffers (`vbo`, `vbo_normales` y `uv_buffer`) creados a partir de los arreglos de
`modelo.py`. El _vertex array object_ (VAO) asocia cada buffer con el atributo del
shader que lo recibe: `in_posicion`, `in_normales` e `in_uvs`.

La textura se crea con los bytes que entrega `abrirAtlas`. Se generan _mipmaps_ y se
usa el filtro `LINEAR_MIPMAP_LINEAR` al reducir (objetos lejanos) y `LINEAR` al
ampliar. Con `repeat_x` y `repeat_y` desactivados, las coordenadas fuera de
$[0, 1]$ no repiten la imagen. La textura se asigna a la unidad 0 y se informa al
shader con el _uniform_ `textura`.

==== Bucle de renderizado

En cada cuadro se ejecutan, en orden, los siguientes pasos:

+ *Tiempo.* Se calcula `dt` y se limita a `LIMITE_DT`, para evitar saltos grandes
  del personaje si el programa se detiene un instante (por ejemplo, al mover la
  ventana). Cada `INTER_FPS` segundos se calculan los FPS y se muestran en el
  título.
+ *Entrada.* `glfw.poll_events()` procesa los eventos y `movimientoPersonaje`
  actualiza al personaje.
+ *Cámara.* Se construye la matriz de vista con `glm.lookAt` a partir de la posición
  y la dirección. La matriz de proyección se calcula una sola vez antes del bucle,
  porque el campo de visión, la proporción y los planos de recorte no cambian.
+ *Uniforms.* Se envían al shader las matrices, la posición de la cámara y el tiempo
  (`glfw.get_time`).
+ *Dibujo.* Se limpia la pantalla con un color violeta oscuro y el búfer de
  profundidad, y se dibujan las copias con `generarTuneles`.
+ *Presentación.* `swap_buffers` muestra el cuadro terminado.

==== Generación de las copias

La función `generarTuneles` recorre los índices de `modelo.lista`. Para cada copia
$i$ construye la matriz de modelo

$ M_i = T(0, 0, i dot L) dot S_i quad quad S_i = cases("diag"(1, 1, 1) & "si" i "es par", "diag"(1, 1, -1) & "si" i "es impar") $

donde $T$ es la traslación y $S_i$ refleja las copias impares sobre el eje Z. Al
reflejar copias vecinas, los extremos de dos cilindros contiguos coinciden y la
unión es continua. Esta matriz se envía en el _uniform_ `matriz_traslacion`
(que contiene la matriz de modelo completa, traslación y escala).

Para cada copia también se envían:

- `lampara_1`: posición de la lámpara, centrada en la copia
  (`centro + desplazamiento`), de modo que cada copia tiene su propia luz.
- `fase`: valor `i * FASE`, que desfasa el parpadeo de cada copia.
- `emisivo`: bandera que distingue los objetos que emiten luz propia.
  // TODO: explica qué efecto controla en fragment.glsl

Las copias con $|i| >=$ el índice máximo, es decir, las dos de los extremos,
usan el objeto `Cylinder.001`, que representa la entrada y salida del túnel; las
demás usan `Cylinder`. Después de cada cilindro se dibuja el plano del suelo. Como
cada llamada de dibujo recibe el `first` y la cantidad de vértices del objeto
(calculados en `modelo.py`), se dibujan 22 objetos por cuadro: 11 cilindros y 11
planos.

=== config.py

Reúne las constantes y las rutas del proyecto, para modificar los parámetros en un
solo lugar. Las rutas de los shaders se construyen con `pathlib` a partir de la
ubicación del archivo.

#figure(
  table(
    columns: (auto, auto, 1fr),
    align: (left, center, left),
    stroke: none,
    table.hline(y: 0),
    table.header([*Constante*], [*Valor*], [*Función*]),
    table.hline(y: 1),
    [`ANCHO`, `ALTO`], [960 × 540], [Tamaño de la ventana en píxeles; `RATIO` es su proporción.],
    [`FOV`], [45°], [Campo de visión vertical de la cámara.],
    [`PLANO_1`, `PLANO_2`], [0.1, 1000], [Planos de recorte cercano y lejano de la proyección.],
    [`SENS`], [0.1], [Sensibilidad del mouse.],
    [`SALTO`], [3.6], [Velocidad vertical inicial del salto.],
    [`SUELO`], [1], [Altura mínima de la cámara sobre el suelo.],
    [`LIMITE_DT`], [0.05], [Tope del tiempo entre cuadros, en segundos.],
    [`INTER_FPS`], [0.5], [Intervalo de actualización del contador de FPS, en segundos.],
    [`TUNELES`], [6], [Define las copias: índices de $-5$ a $5$ (11 copias).],
    [`FASE`], [1.7], [Desfase del parpadeo entre copias consecutivas.], // TODO: unidades
    [`IMAGEN`], [`recursos/atlas.png`], [Ruta del atlas de texturas.],
    table.hline(),
  ),
  caption: [Constantes definidas en `config.py`.],
) <tab:config>

=== Shaders

El programa en _Python_ se comunica con los shaders mediante atributos de vértice y
_uniforms_. // TODO: tras pasarme los .glsl, completar la columna "Uso"

#figure(
  table(
    columns: (auto, auto, 1fr),
    align: (left, center, left),
    stroke: none,
    table.hline(y: 0),
    table.header([*Nombre*], [*Tipo*], [*Uso*]),
    table.hline(y: 1),
    [`in_posicion`, `in_normales`, `in_uvs`], [atributos], [Posición, normal y UV de cada vértice.],
    [`matriz_vista`, `matriz_proyeccion`], [`mat4`], [Cámara y proyección.],
    [`matriz_traslacion`], [`mat4`], [Matriz de modelo de cada copia.],
    [`posicion_camara`], [`vec3`], [Posición del observador (para el brillo especular).],
    [`lampara_1`], [`vec3`], [Posición de la lámpara de la copia.],
    [`fase`, `tiempo`], [`float`], [Parpadeo de la lámpara.],
    [`emisivo`], [`float`], [Indica si el objeto emite luz propia.],
    [`textura`], [`sampler2D`], [Atlas de texturas.],
    table.hline(),
  ),
  caption: [Interfaz entre el programa en _Python_ y los shaders.],
) <tab:uniforms>



==== _shaders_ 
Con esta sección @shaders conocí la sintaxis básica del _fragment shader_
la cual requiere de variables de entrada y salida, que se declaran de la
siguiente manera :

```glsl
in tipo nombre_variable;
out tipo nombre_variable;
```

Al igual en esta seccion descubrí los diferentes tipos de datos que existen en _GLSL_
entre los que destacan: `vec3,vec2,vec1 y vec4`. Específicamente utilice el tipo 
`vec3` para una variable de tipo `in` en el _fragment shader_ la cual fue para
las normales de los objetos, durante el desarrollo de este código me percate de
que el nombre de las variables `in,out` con el que se trabaja en _Python_ debe ser 
exactamente el mismo con el que se declaró en el código _GLSL_.

==== _textures_

_uniform_ son constantes en el código _GLSL_ el cual usé para
definir las texturas en el _fragment shader_, las cuales fueron un tipo de objeto
`sampler2D` utilicé el prefijo _2D_ debido a que las texturas provienen de una
imagen.

La sección _textures_ @textures me proporcionó una nueva herramienta de _GLSL_,
_mix_ con ayuda de esta funcion 
== Técnicas de Graficación Aplicadas

= Resultados

= Pruebas y Validación

= Discusión

= Conclusiones

= Trabajo Futuro

= Referencias Bibliográficas
#bibliography("refs.bib", style: "ieee")