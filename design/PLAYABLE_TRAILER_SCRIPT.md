# La partida pendiente — guion del tráiler jugable

> **Versión:** vertical slice para la Epic AI MegaJam  
> **Duración jugable:** 12–18 minutos  
> **Formato:** Unreal Engine, tercera persona, Windows  
> **Regla narrativa:** la fábrica es el presente; los dragones, la guerra y el acantilado son cortes vividos de una misma imaginación, no universos paralelos.

---

## 1. Qué estamos haciendo

Un tráiler jugable es una experiencia breve donde el jugador controla los momentos que normalmente solo vería en el tráiler de un juego grande: una persecución bajo lluvia, un dragón, una guerra, un vuelo, un paisaje inmenso y un final íntimo.

La diferencia es que cada momento espectacular no está puesto al azar. Todos forman el **Director’s Cut** de la protagonista: material que la historia oficial de la fábrica había dejado fuera.

### La versión oficial

Una guardia del grupo protector persigue a una intrusa dentro de una fábrica abandonada para recuperar un objeto robado.

### La versión Director’s Cut

La guardia ha imaginado historias desde niña. La intrusa apareció en esas historias una y otra vez bajo distintos papeles. Al seguirla, la protagonista revive los cortes que escondían esa conexión y termina decidiendo protegerla.

---

## 2. Pilares que no se negocian

1. **La protagonista sabe dónde está.** Su vida real y la ciudad imaginaria son diferentes; entrar a la ciudad es una decisión nocturna.
2. **Los cortes se viven.** Cuando empieza uno, la protagonista adulta se asusta; no “abre un álbum de recuerdos”.
3. **La fábrica siempre es el eje.** Se sale de ella brevemente mediante cortes y se regresa a ella para avanzar.
4. **El espectáculo tiene función.** Dragón, espada, acantilado y vuelo desbloquean rutas, no son decoración.
5. **Solo una mecánica nueva.** El Corte de Continuidad, acompañado por un único impulso reutilizable.
6. **La visitante no es villana.** Es directa, urgente y difícil de leer; no da monólogos ni pide perdón.
7. **El ajedrez es diálogo.** La protagonista habla con decisiones, distancia, mirada y piezas.

---

## 3. Guion completo con tiempo, cámara y gameplay

Los tiempos son estimados. Los cortes de cámara sirven como guía para Sequencer; no tienen que bloquear todo el control salvo durante 1–3 segundos.

### 00:00–00:45 — PRÓLOGO REAL: “La puerta”

**Lugar:** habitación pequeña, madrugada. Lluvia real contra una ventana.  
**Objetivo del jugador:** llegar a los audífonos junto a la cama/mesa.

| Tiempo | Imagen / cámara | Acción del jugador | Audio | Información sin texto |
|---|---|---|---|---|
| 00:00 | Plano jugable al hombro. Llaves, chaqueta y una taza sobre una mesa. | Camina por su habitación. | Lluvia, refrigerador lejano, ciudad real. | Tiene una vida cotidiana; acaba de volver. |
| 00:15 | El jugador ve una lámpara circular y un caballo de ajedrez gastado. | Se acerca a los audífonos. | Un motivo de cinco notas entra casi imperceptible. | El caballo importa, pero aún no sabemos por qué. |
| 00:30 | Interacción. Primer plano de su mano colocando un audífono. | Mantiene `Interactuar`. | La música sube, la lluvia cambia de tratamiento. | Ella elige entrar. |
| 00:38 | La luz de la habitación coincide con una lámpara industrial. Match cut. | Sin control por 2 segundos. | Golpe de metal suave. | No se teletransporta al azar: la realidad se enlaza visualmente. |
| 00:45 | Cámara vuelve al hombro: fábrica nocturna bajo lluvia. | Recupera control. | Metal, lluvia musical, maquinaria distante. | Ya está dentro de su ciudad. |

### 00:45–02:20 — FÁBRICA I: “La intrusa”

**Lugar:** acceso exterior de una fábrica textil abandonada. Máquinas cubiertas de telas, ventanas rotas, luces azules y una lámpara ámbar.

**Objetivo:** seguir a la visitante sin que las patrullas del grupo las vean juntas.

| Tiempo | Imagen / cámara | Gameplay | Diálogo / pista |
|---|---|---|---|
| 00:50 | Una figura con abrigo oscuro cruza una pasarela. | Seguir luces, huellas húmedas o telas movidas; no hay minimapa. | Ningún diálogo todavía. |
| 01:15 | Una patrulla ilumina el suelo; la visitante se esconde tras telares. | Pasa por cobertura simple o espera 3 segundos detrás de una máquina. | Radio incomprensible: solo presión, sin exposición. |
| 01:35 | La visitante mira atrás, como si supiera que la siguen. | El jugador se acerca. | Visitante: «Llegaste antes de lo que esperaba.» |
| 01:50 | Ella salta una barrera imposible hacia una zona alta. | Ruta bloqueada: el jugador encuentra una lámpara circular. | La lámpara reproduce las cinco notas. |
| 02:10 | Primer plano muy breve del rostro adulto de la protagonista: miedo real, reflejo naranja sobre los ojos. | Mantiene `Corte`. | Un rugido entra por encima de la música. |

### 02:20–03:45 — CORTE I: “El dragón que no recordaba”

**Función:** espectáculo temprano y tutorial de `Cut Boost`.  
**Regla:** no vuelo libre. Es un vuelo guiado sobre una ruta/spline con control lateral y tres impulsos.

| Tiempo | Imagen / cámara | Gameplay | Revelación |
|---|---|---|---|
| 02:20 | Corte seco. La protagonista se aferra al lomo de un dragón entre nubes y restos de una fortaleza. | Recupera control tras 2 segundos. | Ella no esperaba llegar ahí. |
| 02:30 | Camino aéreo claro: tres corrientes luminosas delante. | Mover izquierda/derecha y usar `Cut Boost` para atravesar corriente. | El jugador aprende el impulso sin un tutorial textual. |
| 02:55 | El dragón se inclina; un arco flotante se derrumba. | Esquivar y usar otro impulso. Fallo = checkpoint cercano, no muerte larga. | No hay combate ni barra de vida. |
| 03:15 | A lo lejos, sobre una torre, hay una silueta pequeña con el mismo color ámbar de la visitante. | Llegar a la tercera corriente. | La presencia ya existía en una historia infantil. |
| 03:30 | Durante un relámpago, la silueta se vuelve una versión más joven de la protagonista extendiendo la mano. | El dragón atraviesa una grieta de luz. | Muestra crecimiento sin decir edad. |
| 03:42 | Match cut: garra/escama se convierte en estructura de metal oxidado. | Regresa a la fábrica. | La protagonista cae de rodillas un instante y se recompone. |

### 03:45–05:10 — FÁBRICA II: “Ruta alta”

**Objetivo:** usar la comprensión del corte para llegar a la pasarela alta.

- El jugador descubre que una grúa y sus cables forman la misma silueta que las alas/vuelo del dragón.
- Activa un montacargas o puente de mantenimiento con el mismo `Cut Boost` usado para alcanzar corrientes.
- Desde arriba escucha una frase de la visitante, sin verla:

> «Tu grupo puso guardia en el puente.»

- Una patrulla cierra una puerta metálica. La visitante atraviesa por otra zona y deja una señal en L hecha con piezas de tela y luz.

### 05:10–06:35 — CORTE II: “La guerra de los estandartes”

**Función:** sensación de misión, espada y mecanismo; reutiliza el mismo impulso técnico.

| Tiempo | Imagen / cámara | Gameplay | Revelación |
|---|---|---|---|
| 05:10 | La señal en L lleva a una válvula/estandarte atrapado. Primer plano: protagonista adulta mira su mano y oye trompetas. | Mantener `Corte`. | El corte nace de una forma, no de un portal de multiverso. |
| 05:20 | Corte a un campo de guerra medieval construido sobre la estructura de fábrica: vigas son murallas, telas son estandartes, vapor es niebla. | Cámara vuelve tras 2 segundos. | La fábrica sigue siendo ADN del lugar. |
| 05:30 | La protagonista tiene una espada ceremonial. | Ataque único/interacción: cortar tres cuerdas o barreras marcadas. No hay combate contra enemigos. | La espada es un rol imaginado, no un sistema de combate. |
| 05:50 | Proyectiles lejanos derriban parte del camino. | `Cut Boost` se ve como dash de espada para cruzar huecos. | Misma habilidad, nuevo lenguaje visual. |
| 06:05 | Llega a un faro de guerra/interruptor gigantesco. | Girar palanca durante 2 segundos; protegerse de un último derrumbe. | La versión adolescente de la protagonista se ve a lo lejos siguiendo a alguien entre banderas. |
| 06:25 | El faro se enciende. | Fin del corte. | La luz forma por un segundo el rostro/silueta de la visitante. |
| 06:35 | Corte a fábrica: el faro es una lámpara industrial y la puerta tiene energía. | Retorno seguro. | El jugador entiende qué activó. |

### 06:35–08:10 — FÁBRICA III: “No todo lo que protegen”

**Objetivo:** abrir el archivo de máquinas y seguir la señal ámbar.

- La puerta energizada permite entrar al archivo de máquinas.
- La visitante está detrás de una reja o al otro lado de una máquina; no es captura ni conversación larga.
- Ella mueve una torre de ajedrez en una mesa oxidada y dice:

> «No todo lo que protegen merece seguir guardado.»

- Antes de que el jugador llegue, una luz ámbar cruza telas colgantes y la visitante se va por una puerta lateral.
- En el suelo queda una pieza blanca incompleta o un brillo que conduce al siguiente ancla.

### 08:10–09:35 — CORTE III: “El acantilado de la luz ámbar”

**Función:** belleza, silencio y preparación emocional para el tablero.

| Tiempo | Imagen / cámara | Gameplay | Revelación |
|---|---|---|---|
| 08:10 | La protagonista toca una tela/luz y aparece, sin aviso, al borde de un acantilado inmenso sobre nubes claras. | Tras 2 segundos, control. | El cambio de tono sorprende: no todo es lluvia o guerra. |
| 08:25 | Un aura ámbar se desplaza entre rocas y puentes rotos. | Seguir aura; al mirar correctamente los huecos, plataformas invisibles se revelan. | La aura guía sin flechas UI. |
| 08:55 | Viento fuerte apaga temporalmente el aura. | Usar `Cut Boost` para cruzar el salto largo antes de que desaparezca la plataforma. | El jugador domina la misma herramienta. |
| 09:15 | El aura se queda suspendida sobre un pedestal. | Interactuar. | Forma un caballo blanco; detrás, una niña y otra niña juegan fuera de foco. |
| 09:30 | La protagonista adulta da un paso atrás; la música queda casi sola. | Fin del corte. | El caballo conecta todos los papeles. |
| 09:35 | Vuelve a la fábrica con el caballo blanco en la mano. | Retorno seguro. | Ahora puede abrir la nave central. |

### 09:35–11:10 — FÁBRICA IV: “La primera partida”

**Objetivo:** llegar al tablero secreto antes de que la patrulla cierre el área.

- El caballo se coloca en una ranura/tablero de pared y abre la nave central.
- El jugador atraviesa pasarelas ya conocidas; esta vez las luces y la música muestran que todo estaba conectado.
- Breve proyección/reflejo junto a una ventana: hospital cálido, dos niñas, tablero. No se convierte en un cuarto nivel.
- La visitante espera junto a la mesa bajo la lámpara de la imagen principal.

La visitante dice:

> «Hay alguien esperando que vuelva. No pienso regresar con las manos vacías.»

La protagonista mira un punto vacío, procesa, y solo después se sienta.

### 11:10–12:40 — PARTIDA: “El idioma compartido”

**Mecánica:** no ajedrez completo. Tres piezas o tres casillas se iluminan; el jugador elige una jugada. Todas llevan a la despedida, pero cambian la mirada de la visitante o la pausa posterior.

| Elección | Subtexto | Resultado visual |
|---|---|---|
| Mover el caballo para bloquear la salida | “No quiero que te vayas todavía.” | La visitante sonríe apenas antes de mover una torre. |
| Abrir una diagonal | “No te entrego, pero no sé si te entiendo.” | La visitante observa a la protagonista con cuidado. |
| Dejar una pieza expuesta | “Confío en que volverás.” | La visitante mira el caballo y baja la voz. |

Diálogo final de la visitante:

> «Sigues pensando demasiado antes de moverlo.»

La protagonista no contesta. Hace una jugada y mira la pieza.

### 12:40–13:30 — DESPEDIDA Y EPÍLOGO REAL

| Tiempo | Imagen / cámara | Audio |
|---|---|---|
| 12:40 | Alarmas/luz de patrulla cruzan la pasarela. La visitante se pone de pie. | Lluvia, pasos sobre concreto; el tema de cinco notas completo. |
| 12:52 | La visitante se aleja por la salida lateral. | Visitante, sin girarse: «No muevas esa pieza. Quiero saber exactamente dónde la dejé.» |
| 13:05 | Plano de la protagonista: mira ligeramente por encima del hombro de la visitante, sonríe apenas y vuelve al tablero. | La lluvia baja de volumen. |
| 13:15 | Match cut del caballo a la lámpara de su habitación real, mañana. | Audio real: buses, agua, una alarma. |
| 13:25 | La protagonista se prepara para salir. El tablero no está físicamente allí. | La historia no confunde mundos. |
| 13:30 | Texto mínimo opcional: `La partida pendiente`. Fundido. | Última nota del motivo. |

---

## 4. Diseño de juego: hacerlo divertido sin crecer el alcance

### La habilidad universal: Cut Boost

Una sola habilidad técnica reutilizada en todo el juego.

| Estado | Lectura visual | Uso |
|---|---|---|
| Fábrica | Impulso breve, chispas de luz/metal | Cruzar un hueco, alcanzar montacargas, evadir obstáculo. |
| Dragón | Corriente de aire o aleteo de energía | Estabilizar el vuelo y atravesar anillos de luz. |
| Guerra | Dash de espada y tela movida | Cruzar escombros o cortar una cuerda marcada. |
| Acantilado | Salto impulsado por viento/aurora | Llegar a una plataforma temporal. |

No crear cuatro controles distintos. Un botón, el mismo cooldown, el mismo chequeo de colisión y efectos distintos por escena.

### El esquema de cada corte

1. **Sorpresa:** 1–3 segundos de reacción facial adulta.
2. **Lectura:** el jugador ve inmediatamente el objetivo por composición, luz y ruta.
3. **Dominio:** usa el Cut Boost una o dos veces.
4. **Peligro:** un obstáculo único; nada de enemigos con vida.
5. **Imagen:** aparece la versión joven/silueta del momento de crecimiento.
6. **Retorno:** match cut claro a una solución física de la fábrica.

### Fallos agradables

- Caer: reaparecer 3–5 segundos antes en el mismo corte.
- Perder una corriente: dragón reacomoda la ruta y se reinicia el microtramo.
- Llegar tarde a una patrulla: la luz se apaga y obliga a usar cobertura cercana; no devuelve al inicio.
- Nunca poner una pantalla `Game Over`.

---

## 5. Arquitectura Unreal simple y segura

### Mapas

```text
Content/
  Maps/
    M_RealRoom
    M_FactoryHub
    M_Cut_Dragon
    M_Cut_Siege
    M_Cut_Cliff
```

Usar tres mapas de bolsillo pequeños para los cortes y teletransporte seguro. El Sequence Manager oculta la carga con un plano corto de cámara, oscuridad, sonido y VFX. Visualmente se vive como una transformación; técnicamente es más estable que intentar cambiar todo el mapa al mismo tiempo.

### Blueprints mínimos

```text
Content/Blueprints/
  BP_PlayerCharacter
  BP_CutAnchor
  BP_CutSequenceManager
  BP_CutBoostComponent
  BP_VisitorDirector
  BP_GameProgress
  BP_PatrolLight
  BP_ChessFinal
  BP_Checkpoint
```

| Blueprint | Sólo debe hacer esto |
|---|---|
| `BP_CutAnchor` | Detectar al jugador, mostrar una pista visual, aceptar Interactuar y pedir abrir un CutId. |
| `BP_CutSequenceManager` | Bloquear input por 1–3 s, reproducir entrada, cargar/teletransportar, guardar retorno. |
| `BP_CutBoostComponent` | Impulso con cooldown, VFX/SFX intercambiables y protección contra atravesar paredes. |
| `BP_VisitorDirector` | Mover visitante por hitos fijos según progreso; no Navigation AI compleja. |
| `BP_GameProgress` | Tres booleans/enum de cortes, puertas abiertas y checkpoint actual. |
| `BP_ChessFinal` | Iluminar tres opciones, disparar animación/cámara correspondiente y terminar partida. |

### Assets necesarios: lista cerrada

**Personajes:** protagonista adulta, visitante adulta, silueta infantil/juvenil reutilizable, una patrulla genérica.  
**Escenario:** un kit de fábrica, telas, lámparas, grúa, pasarelas, tablero, habitación.  
**Cortes:** dragón lejano con ruta spline, tres anillos/corrientes, faro/interruptor, espada ceremonial, estandartes, acantilado/rocas/puentes, aura ámbar.  
**Cinemáticas:** cuatro animaciones de personaje como mínimo: reacción, sentarse, mover pieza, levantarse/alejarse.

---

## 6. Plan de cuatro días

### Día 1 — El corte funciona

**Meta:** desde fábrica se puede activar el corte de dragón, completar una ruta fea pero jugable y regresar a fábrica con una puerta abierta.

1. Crear proyecto Third Person y configurar control de versiones.
2. Graybox de `M_FactoryHub`, `M_Cut_Dragon` y una habitación mínima.
3. Programar `BP_CutSequenceManager`, `BP_CutAnchor` y `BP_CutBoostComponent`.
4. Crear visitante placeholder por hitos.
5. Construir el dragón como spline/cámara guiada y tres objetivos de corriente.
6. Empaquetar una build de prueba antes de cerrar el día.

### Día 2 — El juego tiene principio y final

**Meta:** los tres cortes, el retorno a fábrica y el tablero funcionan con placeholders.

1. Duplicar el framework para `M_Cut_Siege` y `M_Cut_Cliff`.
2. Implementar cada uno con una ruta de 60–90 segundos y checkpoint.
3. Conectar las recompensas con puertas/rutas de fábrica.
4. Implementar la interacción de tres jugadas de ajedrez.
5. Añadir final de placeholder y retorno a habitación.
6. Jugar la experiencia completa sin usar el editor.

### Día 3 — Ahora parece el juego

**Meta:** personajes, luz, audio y cámara sostienen la emoción.

1. Sustituir protagonista y visitante por sus modelos finales; verificar cabello corto rizado.
2. Aplicar una paleta y materiales por corte, manteniendo señales industriales de fábrica.
3. Crear las reacciones faciales/corporales de entrada y salida con Sequencer.
4. Integrar lluvia, sonido de dragón, faro, viento, piezas y tema de cinco notas.
5. Ajustar iluminación de la fábrica y cinemática de ajedrez.

### Día 4 — Pulido y entrega

**Meta:** build estable, comprensible sin explicación y video listo.

1. Quitar bloqueos, errores de retorno, caídas sin checkpoint y colisiones malas.
2. Confirmar que cada corte enseña su objetivo sin texto.
3. Bajar calidad donde haga falta para mantener fluidez.
4. Empaquetar temprano y probar desde cero.
5. Grabar 30–60 segundos: el dragón/corte debe verse antes del segundo 5.
6. Preparar créditos, licencias, herramientas y declaración de trabajo pre-jam.

---

## 7. Prompt maestro para Claude Code + Unreal MCP

Pegar al comenzar la jam:

```text
Actúa como director técnico de una game jam de cuatro días en Unreal Engine. Trabajamos en una aventura 3D de tercera persona para Windows titulada provisionalmente “La partida pendiente”. El objetivo es una build empaquetable, completa y pulida de 12–18 minutos. No aumentes el alcance.

CONCEPTO
La protagonista es una joven adulta callada, de cabello oscuro, corto y rizado, con volumen arriba y laterales cortos. Tiene una vida real normal y entra voluntariamente por las noches a una ciudad imaginaria mediante música. La fábrica abandonada es el presente de la ciudad: ella sigue a una visitante extrovertida que su grupo quiere detener. La visitante no es villana; busca un objeto importante y le resulta extrañamente familiar a la protagonista.

Cuando la protagonista encuentra objetos-ancla, entra en “cortes vividos”: escenas fantásticas que imaginó durante distintas etapas de su crecimiento. NO son multiversos. Son escenas eliminadas de una sola imaginación, vividas ahora por la protagonista adulta con miedo. Cada corte debe regresar a la fábrica y abrir la siguiente ruta.

TRES CORTES
1. Dragón: vuelo guiado por spline, tres corrientes de luz, esquivar obstáculos. Revela una silueta infantil de la protagonista y abre la pasarela alta de fábrica.
2. Guerra medieval: fábrica reinterpretada como fortaleza; espada de interacción, tres cuerdas/barreras y un faro. Revela una versión adolescente y energiza una puerta de fábrica.
3. Acantilado: seguir aura ámbar y revelar plataformas; obtiene caballo blanco y abre nave central.

MECÁNICAS
- BP_CutAnchor inicia cada corte.
- BP_CutSequenceManager hace una entrada de Sequencer de máximo 3 segundos, teletransporta/carga un mapa de bolsillo y devuelve al checkpoint de fábrica.
- BP_CutBoostComponent es una sola habilidad universal: dash/impulso; cambia VFX y animación según corte, pero no cambia la lógica.
- BP_VisitorDirector desplaza a la visitante por hitos fijos según progreso.
- Final: ajedrez dirigido con tres jugadas; no crear ajedrez completo ni IA.

ALCANCE PROHIBIDO
No combate completo, vuelo libre, enemigos con IA, mundo abierto, inventario, diálogos ramificados, procedural generation, multiversos, cuatro mapas grandes ni texto explicativo de la historia.

FLUJO DE TRABAJO
Antes de modificar, inspecciona el proyecto y propón máximo seis tareas pequeñas. Implementa una tarea, explica cómo probarla dentro de Unreal y espera mi validación antes de ampliar. Mantén CHANGELOG.md. Prioriza primero un flujo completo feo pero jugable, luego arte/cámara/audio.

PRIMERA TAREA
Crea sólo el graybox de fábrica, el primer BP_CutAnchor, el Cut Sequence Manager y una prueba fea pero completa del corte de dragón que abre una puerta al regresar. No crees arte final ni cinemáticas largas todavía.
```

---

## 8. Prompts de trabajo por fase

### Prompt: primer corte funcional

```text
Implementa BP_CutAnchor y BP_CutSequenceManager de forma reusable. Al mantener E dentro de un trigger, bloquea input por 1.5 s, reproduce una cámara/sonido de entrada, teletransporta de M_FactoryHub a M_Cut_Dragon, guarda un ReturnTransform y al completar el objetivo devuelve al jugador a M_FactoryHub. Al volver, activa una puerta específica usando CutId. No dependas de plugins externos. Dame pruebas manuales para: doble interacción, caída, volver sin retorno válido, recargar mapa y llegar al corte ya completado.
```

### Prompt: vuelo de dragón controlado

```text
Implementa un set piece de dragón sin vuelo libre. El jugador debe moverse lateralmente en una ruta guiada, atravesar tres trigger currents usando el mismo Cut Boost y esquivar dos obstáculos. Al caer o chocar, volver al último checkpoint de ese corte. El dragón puede ser un actor visual en spline; no necesita combate, navegación, daño ni física compleja. Especifica variables editables y cómo probar el flujo en menos de 90 segundos.
```

### Prompt: guerra medieval sin combate completo

```text
Implementa una escena de 60–90 segundos donde el jugador atraviesa tres obstáculos en un fuerte medieval. El arma no es un sistema de combate: Interactuar con espada sólo corta cuerdas/barreras marcadas. Cut Boost funciona como dash para cruzar dos huecos. El objetivo final es activar una palanca/faro y notificar a BP_GameProgress que abra la puerta de fábrica. Evita enemigos con salud, combos, inventario, pickups y navegación AI.
```

### Prompt: acantilado y aura

```text
Implementa una escena corta de plataformas donde un aura ámbar se mueve entre hitos. Cuando el jugador mira hacia una zona correcta o entra en un trigger, se activa una plataforma temporal. El jugador debe usar Cut Boost una vez para un salto largo. Al interactuar con el pedestal final, obtiene el caballo blanco, guarda progreso y vuelve a fábrica. Todo debe ser entendible por composición, luz y sonido, sin flechas de UI ni texto tutorial.
```

### Prompt: secuencia final de ajedrez

```text
Planifica e implementa una interacción final de ajedrez dirigida, no un juego de ajedrez real. Ilumina tres casillas/jugadas con sus cámaras asociadas. Cualquier selección lleva a la misma despedida, con reacciones visuales distintas de la visitante. La protagonista no habla. La cinemática debe incluir: visitante se va por salida lateral, protagonista mira levemente por encima de su hombro, sonríe apenas y vuelve al tablero. Duración total: máximo 45 segundos.
```

---

## 9. Producción de arte y audio

### Regla de recursos

- **Fab:** todo lo modular, repetible y grande: fábrica, vigas, máquinas, pasarelas, telas, rocas, luces.
- **IA 3D:** sólo props que se miran de cerca: caballo blanco, objeto sellado, espada ceremonial.
- **MetaHuman/Character Creator:** dos protagonistas; no generar dos personajes completos con IA 3D a última hora.
- **Rokoko/iClone:** sólo reacción, tablero, mano, salida; locomoción normal para el resto.
- **PBR material:** cuatro materiales fuertes son suficientes: metal mojado, concreto, tela industrial, piedra/estandarte.

### Prompt de concepto visual

```text
Use case: stylized-concept.
Asset type: Unreal Engine 5 playable-cinematic game key art.
Scene: rainy abandoned textile factory, blue night light through broken windows, wet concrete, rusted machinery and hanging fabric. In the center, the industrial space is beginning to transform into a medieval fortress: factory beams become battlements, cloth becomes banners, and the shadow of an original dragon crosses the roof. A warm lamp illuminates a worn chessboard.
Characters: two young adult women. The protagonist is seen in three-quarter view with very short dense dark curly hair, volume on top and close sides, oversized black jacket and headphones. The visitor wears a structured dark coat with a subtle amber accent.
Mood: playable cinematic tension, mystery and recognition; fantastical but grounded, not multiverse, not horror.
Constraints: original designs only; no copyrighted characters, no logos, no text, no watermark, no long hair on protagonist, no gore.
```

### Prompt de caballo blanco para IA 3D

```text
Game-ready prop for Unreal Engine: a small worn white chess knight with a ceramic or carved-bone feel, slightly chipped base, years of handling, emotionally meaningful but not magical-looking. Clear silhouette at close range, clean quad topology, 2K PBR textures, no text, no logo, no pedestal.
```

### Búsquedas de audio

```text
ambient industrial rain melancholic piano minimal
wet factory ambience metal creaks distant machinery
dragon wing pass distant roar cinematic restrained
medieval siege distant horns fabric wind no battle vocals
high cliff wind soft piano mystery amber light
chess piece ceramic wood table close foley
```

### Motivo musical

Un tema de cinco notas, con piano apagado y una capa de cuerdas suaves:

- casi oculto en la fábrica;
- aireado durante el dragón;
- tocado como trompeta/piano grave en la guerra;
- limpio y cálido en el acantilado;
- completo, lento y mínimo en la partida final.

---

## 10. Checklist de la versión final

- [ ] En los primeros 60 segundos se entiende: habitación real → fábrica imaginaria → primer corte.
- [ ] La protagonista reacciona como adulta ante cada corte, aunque aparezcan versiones jóvenes como imagen/reflejo.
- [ ] Dragón, guerra y acantilado duran menos de 90 segundos cada uno.
- [ ] Cada corte abre una ruta concreta de fábrica.
- [ ] El jugador nunca debe leer para saber qué hacer.
- [ ] La protagonista conserva cabello corto rizado en gameplay y cinemáticas.
- [ ] No hay referencias, música ni diseños copiados de IP existente.
- [ ] Build Windows funciona desde cero y el jugador puede terminarla sin el editor.
- [ ] Video de 30–60 segundos muestra el Corte de Continuidad/dragón antes del segundo 5.
- [ ] Se registran créditos, licencias, herramientas IA y materiales preparados antes de la jam.

## 11. Pregunta para cortar alcance

Antes de agregar algo, preguntar:

> ¿Este elemento hace que el jugador avance, sobreviva a un corte o entienda por qué la visitante siempre estuvo en las historias de la protagonista?

Si no cumple una de esas tres funciones, se guarda para el juego completo.
