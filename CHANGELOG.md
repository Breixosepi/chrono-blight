# Changelog - Chrono Blight

Todos los cambios notables realizados en el proyecto **Chrono Blight** (Plataformas de Acción / Mini-Metroidvania en Gale y Pygame) están documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [0.18.0] - 2026-09-18

### Añadido
- **Estandarización de Tipografías Pixel-Art (`settings.FONTS` y `assets/fonts/`)**:
  - Configuración del conjunto oficial de fuentes en `settings.FONTS`: `hud` (10pt), `hud_small` (9pt), `ui` (10pt), `title` (18pt) con `golden-apple.ttf`, y `main-title` (24pt) con `Undaunted-DEMO.otf`.
  - Establecimiento del umbral mínimo de tamaño de fuente en 9pt (`hud_small`), garantizando máxima nitidez pixel-art y legibilidad en resolución virtual retro ($320 \times 180$).
- **Soporte de Texto Multilínea y Clamping Perimetral en `_crisp_render_text` (`settings.py`)**:
  - Soporte nativo para saltos de línea (`\n`) con cálculo dinámico de espaciado vertical proporcional (`font.get_linesize()`), evitando glifos no imprimibles.
  - Clamping perimetral automático a los límites de superficie (`clamp_to_surface=True`): contención de textos y números flotantes de combate dentro de los márgenes visibles de la pantalla ($X \in [2, W-3]$, $Y \in [2, H-3]$), impidiendo que alertas o popups se corten fuera de la ventana.
- **Documentación Técnica de Arquitectura (`ARCHITECTURE.md`)**:
  - Creación del documento técnico arquitectónico en la raíz del proyecto detallando módulos, subsistemas desacoplados (FSM, StateStack, Command Pattern), pipeline de renderizado, topología del mundo y diagramas Mermaid.

### Cambiado / Mejorado
- **Prevención de Desbordamiento y Maquetación en Menú de Pausa (`src/states/game/PauseState.py`)**:
  - Ampliación del ancho del pergamino a `BOARD_W = 264` px para dar margen visual holgado en la resolución de 320 px.
  - Reorganización de la subpantalla `CONTROLES Y FORMAS` en dos columnas limpias (`tecla` en `bx + 12`, `descripción` en `bx + 84`).
  - Adopción de la fuente `hud_small` (9pt) y síntesis de descripciones de habilidades, eliminando el corte que ocurría con frases largas como `"Mago: Orbe | Cab: Espada | Morph: Rodar"`.
- **Reestructuración Anticolisión en el Mapa del Mundo (`src/states/game/MapState.py`)**:
  - Sustitución de la descripción de sala inexplorada: condensada de `"Niebla densa. Explora este sector para descubrir su contenido."` (283 px, excedía la pantalla por 17 px) a `"Niebla densa. Sector aun sin explorar."` en `hud_small` (146 px).
  - Reorganización total del pie de página del mapa: separación limpia entre controles a la izquierda (`[M] Cerrar [FLECHAS] Explorar`) y el porcentaje de exploración con barra de progreso a la derecha, erradicando la triple colisión visual anterior y dejando 58 px de separación.
- **Ajustes de Márgenes en Ranuras de Guardado (`src/states/game/SlotSelectState.py`)**:
  - Incremento del ancho de las tarjetas a `card_w = 236` px.
  - Aplicación de `hud_small` (9pt) en detalles de guardado, tiempo de juego, porcentaje de exploración y texto de ranura vacía, asegurando más de 50 px de margen de seguridad frente al borde de la tarjeta.
- **Calibración Visual del HUD (`src/ui/HUD.py`)**:
  - Ajuste de las dimensiones del contenedor a $88 \times 36$ px para albergar cómodamente los indicadores.
  - Reubicación vertical de los rótulos de formas activas a `row_forms_y = 20`, evitando que sobrepasen el borde inferior del marco.

### Corregido
- **Solapamiento de Barra vs Dígitos en HUD (`src/ui/HUD.py`)**:
  - Reducción del ancho de las barras de HP y MP a 26 px (`bar_w = 26`, finaliza en $X=63$), erradicando la superposición gráfica de la barra sobre los dígitos de vida cuando el jugador supera los 100 HP (3 dígitos, inicio en $X=70$).

### Eliminado
- **Depuración de Tipografía Obsoleta (`assets/fonts/Minimal4.ttf`)**:
  - Eliminación del archivo de fuente anterior tras completar la migración hacia `golden-apple.ttf`.

---

## [0.17.0] - 2026-09-18

### Añadido
- **Pantalla de Victoria (`VictoryState`)**:
  - Implementación de pantalla cinemática de victoria tras vencer al jefe final The Harvester en la Gran Pirámide (`big_room`).
  - Animación de ascensión y levitación del protagonista con rótulo de victoria y destello ceremonial en `UnlockState`.
  - Tarjeta de estadísticas finales con tiempo total de juego (`playtime`), porcentaje de exploración del mapa (`exploration`) y retorno limpio al menú principal con `[ENTER]`.
  - Guardado de punto de control automático al completar la partida.

### Cambiado / Mejorado
- **Interfaz y Metadatos de Ranuras de Guardado (`SlotSelectState.py` y `PlayState.py`)**:
  - Desempaquetado correcto de metadatos de Gale (`extra["metadata"]`) para visualizar información real de partida en lugar de valores por defecto (12% y 00m 00s).
  - Rediseño de las etiquetas de ranura: ahora se exhibe el nombre formal de la zona (`Zona Central`, `Abismo Oeste`, `Santuario Pasado`, `Gran Piramide`, etc.), cantidad de formas activas (`Formas: X/3`), tiempo acumulado de juego y porcentaje real de exploración.
  - Compatibilidad hacia atrás mediante resolución de datos guardados para saves creados previamente.
- **Optimización de Peligro de Lava (`RisingHazard.py`)**:
  - El indicador HUD de escape de lava ahora se muestra exclusivamente en el mapa vertical (`subida`), ocultándose en zonas con estanques estáticos de magma como `sala_past`.

### Corregido
- **Ciclo Residual del Sonido de Lava (`LavaShower.py` y `ArenaManager.py`)**:
  - Corrección del bucle infinito de audio de `lava-shower` (`lava_boss.wav`) que sonaba periódicamente cada 2-3 segundos durante toda la partida.
  - `LavaShower` ahora inicia en estado inactivo y no reprograma temporizadores fuera de la batalla del sacerdote cultista.
  - Detención segura y limpieza de timers y canales de sonido de lava al vencer a los jefes y en las transiciones de sala (`PlayState.change_room`).

---

## [0.16.0] - 2026-09-17

### Añadido
- **Integración Integral del Paisaje Sonoro (Efectos de Sonido y Pistas en `settings.SOUNDS`)**:
  - **Interfaz y Navegación**:
    - Efectos `change` y `enter` para navegación interactiva y confirmación en menús (`TitleState`, `GameOverState`, `SlotSelectState`).
    - Efectos táctiles de pergamino `paper-unfold` (`unfold_map.mp3`) y `paper-fold` (`fold_map.wav`) al abrir y cerrar la interfaz de papel en `MapState` y `PauseState`.
  - **Habilidades y Estados del Jugador**:
    - `jump`: Sonido de impulso al despegar en salto (`jump.wav`).
    - `morph-dash`: Efecto sonoro aerodinámico al ejecutar el impulso de la forma Morph (`dash_morph.mp3` en `DashState`).
    - `change-skin`: Efecto de transformación mágica al alternar entre formas (`change_skin.mp3` en `Player.change_skin`).
    - `on-land`: Contacto e impacto con el suelo al aterrizar tras saltar o caer (`on_land.mp3` en `Player.on_land`).
    - `sword` y `slash-hit`: Efecto de balanceo de espada y corte de impacto contra carne al golpear enemigos (`AttackState`, `combat.py`).
    - `sword-dash`: Desplazamiento sónico al rematar con el ataque especial de espada (`sword_dash.wav` en `AttackSpecialState`).
    - `mage-attack` y `mage-special`: Disparo de proyectil mágico e invocación de pilares de llamas arcanas (`AttackState`, `AttackSpecialState`).
    - `morph-fire` y `morph-power`: Ataque básico y explosión ígnea de la forma Morph.
    - `phase_shift_past` y `phase_shift_future`: Efectos temporales al alternar entre la era del Pasado y del Futuro (`PhaseShiftState`).
    - `player-death`: Agonía sonora al perecer el jugador en `DeathState`.
    - `hit-player`: Sonido de impacto al recibir daño el protagonista.
    - `heart`: Tintineo curativo al recolectar orbes de vida en el mundo (`HealthOrb.py`).
    - `unlock-state`: Sonido cinemático ceremonial al adquirir una nueva forma (`UnlockState.py`).
  - **Enemigos y Jefes**:
    - `enemy-hurt`: Reacción auditiva de dolor al recibir daño regular (`EnemyHitState.py`).
    - `enemy-death`: Disolución y destrucción de enemigos comunes.
    - `shield-active`: Rebote metálico al golpear enemigos o jefes protegidos por barreras invulnerables (`combat.py`).
    - `boss-wind-spell`: Efecto místico de viento para los ataques mágicos del Lurker (`LurkerAttackState.py`).
    - Bandas sonoras temáticas de jefes: `boss_survive` (desafío de supervivencia en `sala_past`), `giant_boss` (combate contra el Gólem Raíz) y `final_boss` (batalla climática contra el Sumo Sacerdote Cultista en `sala_future`).
    - `arena-cleared`: Fanfarria triunfal (`arena_fanfare.mp3`) al superar una arena de combate o prueba de supervivencia (`ArenaManager.py`).
  - **Mundo y Mecánicas de Entorno**:
    - `save`: Resonancia mística al sintonizar un altar de guardado (`Altar.py`).
    - `open` y `close`: Apertura y cierre de compuertas en el sistema de ascensores (`Elevator.py`).
    - `rock-crack` y `rock-smash`: Crujido de advertencia y colapso demoledor en las trampas de roca (`FallingTrap.py`).
    - `lava` y `lava-shower`: Borboteo y caída de magma en peligros ascendentes y cascadas (`RisingHazard`, `LavaShower`).
    - `saw-hazard`: Corte al ser impactado por sierras mecánicas (`SawHazard.py`).

### Cambiado / Refactorizado
- **Rediseño de Fin de Partida con Carga de Partidas (`GameOverState.py` y `SlotSelectState.py`)**:
  - Sustitución de la opción *"Continuar desde el ultimo altar"* por *"Cargar partida"*.
  - Navegación fluida hacia `SlotSelectState` en modo carga (`from_game_over=True`), permitiendo al jugador seleccionar cualquiera de sus 3 ranuras de guardado con lectura de metadatos (sala, aspecto, salud y fecha/hora).
  - Soporte para cancelar y volver a la pantalla de Game Over mediante la tecla `[P]` o `[Backspace]` (`self.state_machine.pop()`).
  - Limpieza exhaustiva de la pila de estados (`while len(self.state_machine.states) > 0: self.state_machine.pop()`) al cargar o iniciar partida, erradicando estados zombis (`GameOverState` y `PlayState` residual) y previniendo fugas de memoria.

### Corregido
- **Detención Inmediata de Peligros de Lava al Morir (`DeathState.py` y `settings.py`)**:
  - Corte forzado inmediato de los sonidos en bucle `lava`, `lava-shower` y `saw-hazard` en `DeathState.enter()`, evitando que el magma siga sonando durante la animación de muerte del personaje.
  - Parada segura del sonido `lava` al entrar en `InactiveState` y de `lava-shower` al reiniciar la trampa en `LavaShower.reset()` y `settings.stop_all_music()`.
- **Corte Limpio de Música al Regresar al Menú Principal (`TitleState.py`, `GameOverState.py`, `ChronoBlight.py`)**:
  - Detención automática de cualquier canal de música activo (`game-over`, `ambient`, música de jefes) y peligros ambientales persistentes al entrar en `TitleState.enter()` o al reiniciar la pila con `_reset_to_title()`, erradicando la superposición de bandas sonoras con el tema de inicio (`intro`).

---

## [0.15.0] - 2026-09-17

### Añadido
- **Sistema de UI de Papel Moderno y Animado (Humble Gift - Paper UI System v1.1)**:
  - **Animación de Despliegue y Plegado Táctil (`PauseState` y `MapState`)**:
    - Efecto de desenrollado y apertura vertical con rebote suave mediante interpolación `out_back` en apertura (0.24s) y anticipación `in_back` en cierre (0.16s).
    - Proyección dinámica de sombra de papel (*paper drop shadow*) que escala y modula su opacidad según el progreso de la animación.
    - Ocultamiento y revelado nítido del contenido interior cuando el pergamino alcanza un umbral de apertura adecuado ($progress \ge 0.6$).
  - **Niebla Animada Viva en el Mapa (`MapState`)**:
    - Las salas no exploradas cuentan con una niebla difusa en movimiento continuo mediante ondas senoidales (`math.sin` / `math.cos`) y líneas de trama flotantes que simulan vapor o bruma viva en tiempo real.
    - Signo de interrogación (`?`) con suave levitación flotante en cada sala misteriosa.
  - **Faro con Ondas de Radar en el Jugador (`MapState`)**:
    - Marcador de posición del jugador enriquecido con anillos de radar concéntricos expansivos que se difuminan progresivamente al alejarse del centro.
  - **Cursor Suave Deslizante (`lerp`)**:
    - Marco de selección que se desliza fluidamente entre habitaciones en el Mapa del Mundo con velocidad proporcional `dt * 20.0`.
    - Cursor indicador interactivo con transición suave en el Menú de Pausa.
  - **Menú de Pausa Rediseñado con Botones Interactivos y Subpantalla**:
    - Opciones interactivas enmarcadas: `REANUDAR`, `MAPA DEL MUNDO`, `CONTROLES Y FORMAS` y `MENU PRINCIPAL`.
    - Subpantalla detallada `CONTROLES Y FORMAS` con guía de botones para todas las transformaciones (Mago, Caballero, Morph Ball) y mecánicas de cambio de fase temporal.
    - Acceso directo al Mapa del Mundo desde el menú de pausa sin necesidad de reanudar el juego.

---

## [0.14.0] - 2026-09-16

### Añadido
- **Pantalla de Mapa del Mundo Completo (`src/states/game/MapState.py`)**:
  - Acceso instantáneo en cualquier momento mediante la tecla `[M]` (o salida con `[M]` / `[ESC]`).
  - **Estética de Pergamino Humble Gift**: Inspirado en `ps3Urw.gif` y `Frc_nf.gif`, con marco cálido de pergamino (`#eebd8a`), doble borde de tinta oscura (`#2c1e28`) y filigranas de diamantes en las esquinas.
  - **Niebla para Salas Inexploradas**: Las habitaciones no visitadas se proyectan como siluetas oscuras atenuadas con trama de niebla y un `?` central, manteniendo ocultos sus secretos y POIs.
  - **Salas Visitadas y Puntos de Interés (POIs)**: Las salas descubiertas se renderizan con contorno nítido y sus mini-iconos distintivos:
    - `middle`: Altar ancestral de guardado.
    - `abismo_fixed`: Bloque desmoronable de piedra.
    - `sala_past`: Cara del Gran Monstruo (y cruz `X` de victoria tras superarlo).
    - `sala_future`: Cara del Sumo Sacerdote Cultista (y cruz `X` de victoria tras derrotarlo).
    - `esquina_1` y `left_corner`: Monolitos/obeliscos con runa cian brillante.
    - `subida`: Gota / llama de lava fundida.
    - `big_room`: Calavera del clímax final.
  - **Faro de Posición del Jugador**: Marcador pulsante en tiempo real indicando en qué sala te encuentras.
  - **Tarjeta de Información Inferior (`INFO`)**: Caja de detalle que expone el icono enmarcado, título y descripción/estado de la sala seleccionada.
  - **Exploración Interactiva con Flechas**: Navegación con `[↑/↓/←/→]` para inspeccionar los detalles de cualquier sala conectada en el mapa.
- **Menú de Muerte y Game Over Interactivo (`src/states/game/GameOverState.py`)**:
  - Reemplazo del retorno automático al título por un menú de 2 opciones:
    1. *Continuar desde el último altar*: Restaura al jugador al 100% de vida y resucita todas las formas disponibles en el altar guardado, preservando en memoria el mapa de salas descubiertas.
    2. *Volver al menú principal*: Retorna limpiamente a la pantalla de título.
- **Persistencia de Exploración (`visited_rooms`)**:
  - Registro de salas exploradas en `PlayState` sincronizado con el sistema de guardado `SaveManager`.

---

## [0.13.0] - 2026-09-16

### Añadido
- **Bloqueadores de Puertas en Mapas Tiled (`assets/tilemaps/`)**:
  - `subida.json`: Bloqueador de entrada inferior ($X=0, Y=560$, $32 \times 48$ px) con `requires_event="subida_cleared"`.
  - `sala_past.json`: Bloqueador de arena de supervivencia ($X=608, Y=112$, $32 \times 64$ px) con `requires_event="survival_boss_defeated"`.
  - `sala_future.json`: Bloqueador de sala del jefe cultista ($X=0, Y=112$, $32 \times 64$ px) con `requires_event="boss_cultist_defeated"`.

### Cambiado / Refactorizado
- **Eliminación de Muros Invisibles y Barreras Procedurales Hardcodeadas**:
  - `ArenaManager.py`: Eliminación total del renderizado procedural de campos láser, lógica de pulsos, variables `barrier_active`, `barrier_rect` y empuje forzado del jugador.
  - `RisingHazard.py`: Eliminación de los barrotes de hierro procedurales descendentes, superficie y lógica de colisión vertical de compuerta.
  - `TriggeredState.py` y `InactiveState.py` / `MovingState.py`: Limpieza de referencias a `gate_current_y`, `gate_landed` y `drop_tween`.
  - `room_connections.py`: Desvinculación de la salida de `subida` de coordenadas internas de la compuerta eliminada.
  - `Room.py`: Inicialización de `solid_blockers` durante `__init__` e invocación reactiva en `ArenaManager.on_unlock_finished()` y `EscapedState.enter()` para apertura inmediata de puertas al superar los desafíos.

---

## [0.12.0] - 2026-09-16

### Añadido
- **Sistema de Progresión y Cinemática de Desbloqueo de Formas (`src/states/entity/player/UnlockState.py`)**:
  - Estado dedicado para la obtención de nuevas formas (`UnlockState`) con animación cinemática:
    - Levitación suave del personaje mediante curvas cúbicas de Gale (`gale.ease_functions.ease_out_cubic`).
    - Destello con halo resplandeciente, onda expansiva circular y emisión de partículas de polvo al alcanzar el clímax.
    - Caída al suelo y despliegue del banner superior estilizado indicando la forma obtenida.
  - Bloqueo de entrada/salida de sala durante la animación para garantizar la integridad cinemática.
- **Desbloqueo de Formas y Eventos en el Mundo**:
  - **Forma Caballero (`sword`)**: Desbloqueo al vencer la supervivencia en `sala_past`. Incorpora un retardo dramático tras el combate antes de iniciar la cinemática, revelando el ascensor de escape únicamente tras finalizar la transformación.
  - **Forma Morph (`morph`)**: Desbloqueo en la sala de la esquina (`middle`) tras superar con éxito la prueba de escape ascendente en `subida`.
- **Bloqueadores Dinámicos de Puertas y Pasajes (`src/world/Room.py`)**:
  - Sistema de barreras temporales mediante rectángulos en Tiled (`traps` / capas de objetos) con propiedades personalizadas `requires_event` / `event`.
  - Mosaico procedural automático con textura de bloques de piedra/ladrillo del juego (`destructible_block`), impidiendo el paso con colisiones AABB sólidas en 4 direcciones mientras el evento no esté superado.
  - Desaparición automática tanto visual como física al registrarse el evento en `cleared_events` (ej. derrota de jefes o superación de salas).

### Cambiado / Refactorizado
- **Centralización de Persistencia y Encapsulación (SRP)**:
  - Creación de `PlayState.save_game_checkpoint()` en `src/states/game/PlayState.py`, centralizando el empaquetado del estado de partida y metadatos.
  - Creación de `Player.restore_all_forms()` en `src/entities/Player.py`, desacoplando a `Altar.py` del acceso directo a diccionarios y propiedades internas del jugador.
  - Refactorización de `Altar.interact()` para delegar el guardado y restauración a sus respectivos responsables.
- **Controles Canónicos de Transformación y HUD**:
  - Establecimiento del orden canónico para el ciclo de formas: `Mago -> Caballero -> Morph`.
  - Corrección de la orientación de teclas: `[Q]` rota hacia la izquierda (hacia el Mago) y `[E]` rota hacia la derecha (hacia Morph).
  - HUD adaptativo que lista dinámicamente las formas desbloqueadas en el orden canónico estricto.

### Optimizado (Rendimiento)
- **Eliminación de Doble Renderizado de Jugador**:
  - Supresión de la llamada redundante `self.player.render()` en `PlayState.render()`, delegando la renderización completa de entidades del mundo a `Room.render()`.
- **Prevención de Presión al Garbage Collector (Eliminación de Asignaciones en Bucle)**:
  - **Transición de Fase (`PhaseShiftState.py`)**: Pre-asignación y reutilización de la superficie de pantalla completa `_RING_SURF`, evitando la creación de superficies de $400 \times 225$ píxeles a 60 FPS.
  - **Partículas de Compuerta (`RisingHazard.py`)**: Pre-asignación de la superficie de partículas `_gate_p_surf` ($3 \times 3$ px), eliminando miles de asignaciones por segundo en el ciclo de dibujado.

### Corregido
- **Tope Estricto de Vida Máxima del Mago (`Player.py`)**:
  - Implementación de clamp estricto en los setters de `health` y `mana` vinculados a `self.MAX_HEALTH` y `self.MAX_MANA`.
  - Ajuste automático de salud al alternar formas (`change_skin`) para evitar que el Mago conserve la vida residual más alta de otras formas (ej. 80 HP de Caballero).
  - Corrección del orden de carga en `PlayState.enter()` para inicializar el skin antes de restaurar la vida.

---

## [0.11.0] - 2026-09-16

### Añadido
- **Altares de Guardado y Restauración (`src/world/Altar.py`)**:
  - Monumento ancestral interactivo con gráficos de obelisco animado.
  - Interacción mediante tecla `[↑]` con prompt visual situado directamente sobre la cabeza del jugador.
  - Al activarse: reproduce su animación de encendido, cura al 100% de HP y Maná a todas las formas, resucita a las formas caídas y guarda el estado en el slot activo mediante `SaveManager`.
- **Sistema de Ranuras de Guardado y Menú Principal (`src/states/game/SlotSelectState.py` y `TitleState.py`)**:
  - Menú interactivo en la pantalla de inicio con opciones: *Nueva Partida*, *Cargar Partida* y *Salir*.
  - Selector para 3 ranuras independientes (`slot_1`, `slot_2`, `slot_3`).
  - Muestra detalles de partida (sala, forma, vida y fecha/hora de guardado).
  - Soporte para iniciar nueva partida, cargar partidas previas, modal de confirmación para sobrescribir y borrado de partidas con tecla de ataque especial `[X]`.
- **Orbes de Vida Coleccionables (`src/world/HealthOrb.py`)**:
  - Drop con probabilidad de 25% al eliminar enemigos comunes.
  - Físicas con gravedad, rebote suave en el suelo y recuperación de +20 HP al contacto con texto flotante.
- **Persistencia de Eventos y Desafíos**:
  - Registro de eventos superados (`cleared_events`) en el archivo de guardado (`.sav`).
  - Desactiva reaparición de jefes derrotados (Sumo Sacerdote en `sala_future`) y trampas de parkour superadas (`subida`).

### Cambiado / Corregido
- **Mapeo de Entradas y Navegación en Menús**:
  - Incorporación de `KEY_DOWN` (`"down"`) y `KEY_BACKSPACE` (`"back"`) en `settings.py`.
  - Manejo jerárquico de `ESC` en `ChronoBlight.py` para permitir retroceder menús sin cerrar la aplicación de forma abrupta.
- **Reubicación Arquitectónica**:
  - Migración de `HealthOrb` de `src/entities/` a `src/world/` para respetar la separación entre actores con máquinas de estado y objetos coleccionables.
  - Reducción del tamaño del corazón a escala pixel art de 16x16 (1 tile).

---

## [0.10.0] - 2026-09-15

### Añadido
- **Sistema de Ascensores (`src/world/Elevator.py`)**: Ascensor interactivo con animaciones de puertas abiertas/cerradas. Traslada al jugador invisibilizándolo durante el viaje; entra en escena, suelta al jugador, espera 1 segundo con las puertas abiertas y desaparece por arriba permanentemente.
- **Módulo de Resolución de Combate (`src/world/combat.py`)**: Extracción completa de la lógica de evaluación de daño, impacto de ataques (cuerpo a cuerpo y magia) y daño por contacto desde `Room.py` a una clase `CombatResolver` independiente.

### Cambiado / Refactorizado
- **Refactorización Limpieza en `Room.py`**:
  - Eliminación de abundante código duplicado centralizando la lógica con `_parse_props` y `_spawn_enemy`.
  - Simplificación del mapeo de capas de colisión con diccionarios limpios a nivel de módulo (`_PHASE_LAYERS`).
  - Eliminación de argumentos y variables huérfanas en trampas y generadores.
- **Máquina de Estados de Jefes**:
  - Reestructuración del paquete de estados de los Jefes, moviendo ataques específicos a sus respectivas carpetas de entidad (ej: `boss/cultist/`) para un mejor desacoplamiento.

### Optimizado (Rendimiento)
- **Eliminación de Fugas de Memoria en Renderizado (Memory Thrashing)**:
  - **Proyectiles**: Pre-asignación de la superficie `_trail_surf` en memoria caché. Evita la creación destructiva de más de 3000 `pygame.Surface` por segundo al dibujar el rastro de las balas enemigas.
  - **Magia del Jugador**: Introducción del caché perezoso (`_flame_cache`) para las llamas del ataque de área del mago, evitando llamar a la intensiva operación `pygame.transform.scale` 60 veces por segundo.

---

## [0.9.0] - 2026-09-14

### Añadido
- **Sistema y Jerarquía de Jefes (`src/entities/Boss.py` y `src/states/entity/boss/`)**:
  - Creación de la clase dedicada `Boss` que extiende `Enemy`, encapsulando el manejo de fases, escudos arcanos, temporizadores de inmunidad y proyectiles especiales.
  - Implementación de la máquina de estados desacoplada para jefes: `BossBaseState`, `BossIdleState`, `BossChaseState` y `BossAttackState`.
  - Separación explícita de `BOSS_DEFS` y `ENEMY_DEFS` en `src/definitions/entity.py`.
- **Combate de Arena Multifase (`src/world/ArenaManager.py` y `src/world/LavaShower.py`)**:
  - Sistema de sala de arena con barrera mágica que sella la salida y lluvia de lava ambiental en el techo.
  - Gestión de 3 fases de combate con oleadas dinámicas de esbirros:
    - **Fase 1**: Jefe protegido por escudo lanzando ondas de choque terrestres mientras el jugador enfrenta esbirros.
    - **Fase 2 (70% HP)**: Desbloqueo del Orbe del Vacío con rastreo inteligente y nueva oleada de esbirros.
    - **Fase 3 (30% HP)**: Furia total combinando onda terrestre y orbe simultáneamente junto al Gólem Raíz.
  - Escudo protector activo mientras haya esbirros vivos; al eliminarlos, el escudo se rompe permitiendo dañar al jefe.
- **Efectos y Spritesheets de Habilidades (`assets/graphics/effects/` y `Boss.py`)**:
  - Integración de spritesheets dedicados para las habilidades del Sumo Sacerdote: `void_orb.png` y `ground_shockwave.png` (variante morada, fila 2).
  - Máquina de estados interna para proyectiles (`spawn`, `travel`, `despawn`) con volteo dinámico horizontal según dirección.
  - IA de rastreo activo (*homing*) para el Orbe del Vacío (duración de 5s con estela de partículas).
  - Hitboxes calibradas para permitir esquivar la onda rasante mediante saltos o plataformas superiores.

### Cambiado / Refactorizado
- **Reorganización Estructural de Assets (`assets/graphics/`)**:
  - Nueva taxonomía de carpetas siguiendo los estándares del motor Gale:
    - `player/{sword, morph, mage}/`
    - `entity/enemies/{goblin, monster2, monster3, monster_eyes, skeleton_sword, crown}/`
    - `entity/bosses/{cultist_priest, big_monster}/`
    - `effects/`
  - Actualización de `settings.TEXTURES` y generadores de recortes en `src/definitions/frames.py`.
- **Desacoplamiento de `Enemy.py`**:
  - Purga de lógica específica de jefes en `Enemy.py`, `EnemyAttackState.py` y `EnemyChaseState.py`, dejando los estados de enemigos regulares limpios y enfocados en su IA estándar.
  - Reparación y actualización de rutas de sprites para `SawHazard.py`.

---

## [0.8.0] - 2026-09-14

### Añadido
- **Sistema de Trampas que Caen (`src/world/FallingTrap.py`)**:
  - Implementación de peligros que caen vinculados a la fase temporal del jugador (`green` o `red`).
  - Detección de proximidad del jugador en el eje X con tiempo de advertencia/temblor (0.45s) antes de la caída por gravedad.
  - Soporte para renderizado directo de tiles del tileset mediante propiedades personalizadas en Tiled (`tile_col`, `tile_row`).
- **Sierras Giratorias y Shurikens (`src/world/SawHazard.py` y `assets/graphics/SawBladeSuriken.png`)**:
  - Obstáculo de daño por contacto con rotación animada continua.
  - Soporte de patrullaje configurable en ejes horizontal y vertical (`axis: "x" | "y"`), distancia (`patrol_dist`) y velocidad (`speed`) desde las capas de Tiled.
- **Spawneo Dinámico de Enemigos desde Tiled (`src/world/Room.py`)**:
  - Detección y creación automática de cualquier enemigo (`monster2`, `monster3`, `goblin`, `cultist_priest`, `skeleton_sword`, etc.) colocado en capas de objetos (`spawns`, `spwans`, `enemies`).
  - Asignación de colisión sólida multicapa para que los enemigos colisionen con las plataformas y paredes correspondientes a su fase temporal.

### Cambiado / Refactorizado
- **Limpieza de Código Muerto y Deduplicación**:
  - Eliminación de constantes no utilizadas (`PHASE_PAST`, `PHASE_FUTURE`, `TILE_COLS`, `TILE_ROWS`) y texturas huérfanas en `settings.py`.
  - Creación de `EntityBaseState.handle_buffered_inputs()` para unificar el manejo de buffers de ataque, ataque especial, dash y salto en `IdleState`, `WalkState`, `JumpState` y `FallState`.
  - Unificación de popups de daño (`_spawn_popup()`), resets a punto de spawn (`_reset_player_to_spawn()`) y tabla de masas de colisión de enemigos en `Room.py`.
- **Integración de Lava/Magma Ascendente (`src/world/RisingHazard.py` y `src/states/hazard/RisingState.py`)**:
  - Lectura de la posición inicial $Y$ del objeto `fire` desde las capas de Tiled.
  - Ajuste del límite superior de ascenso para detenerse a exactamente 2 tiles del techo del mapa.

---

## [0.7.0] - 2026-09-13

### Añadido
- **Sistema de Salas y Mapas Tiled (`assets/tilemaps/` y `src/world/Room.py`)**:
  - Integración nativa con mapas exportados desde Tiled en formato JSON mediante `gale.tilemap.load_tiled_map`, permitiendo crear niveles de dimensiones arbitrarias con capas multicapa de tiles y objetos.
  - Incorporación de 5 nuevas salas/niveles:
    - **`abismo_1.json`** (50x24 tiles / 800x384 px): Nivel vertical con fosas profundas, plataformas duales y zonas de trampas.
    - **`abismo_fixed.json`** (50x13 tiles / 800x208 px): Variante reestructurada del abismo con capas optimizadas, punto de spawn explícito y equilibrio de altura.
    - **`sala_past.json`** (40x13 tiles / 640x208 px): Sala horizontal ambientada en la era del Pasado con vegetación y estructuras verdes predominantes.
    - **`sala_future.json`** (40x13 tiles / 640x208 px): Sala horizontal ambientada en la era del Futuro con arquitecturas rojas y estética corrupta.
    - **`subida.json`** (20x40 tiles / 320x640 px): Nivel vertical de escalada y plataformeo ascendente con trampas y alternancia de fases temporales.
- **Sistema de Físicas y Colisiones Multicapa (`src/world/tile_collision.py`)**:
  - Nuevo subsistema de colisiones para Gale Tilemaps con soporte de fases temporales: `collision_type_in_layers()`, `move_and_collide_layers()` y `check_on_ground()`.
  - Detección precisa de barrido AABB en ejes desacoplados X e Y para azulejos sólidos (`solid`) y plataformas atravesables desde abajo (`platform`).
  - Capas activas dinámicas según la fase temporal del jugador: `["ground", "green_ground"]` en fase Pasado y `["ground", "red_ground"]` en fase Futuro.
- **Plataformas Fantasma (*Ghost Platforms*) y Renderizado por Fases (`src/world/Room.py`)**:
  - Renderizado semitransparente (`alpha = 75`) de las capas del plano temporal opuesto (ej. plataformas rojas visibles como fantasmas en la fase verde), permitiendo al jugador anticipar el terreno antes de realizar un *Phase Shift*.
  - Desempaquetado y soporte de rotaciones/volteos de Tiled (*flip flags* en bits 31, 30 y 29 para flips horizontal, vertical y diagonal) en `_preprocess_tilemap()`.
  - Culling de azulejos visibles mediante `_visible_tile_range()`, dibujando únicamente los tiles comprendidos dentro de la vista actual de la cámara.
- **Fondos Duales con Paralaje y Nuevos Tilesets (`settings.py` y `assets/`)**:
  - Carga y registro de texturas de fondo duales para cada sala en `settings.TEXTURES`: `abismo_1_past/future`, `abismo_past/future`, `sala_past/future` y `subida_past/future`.
  - Soporte para fondos con desplazamiento de paralaje continuo (*parallax scrolling* suave con factor `0.4` en X y repetición horizontal automática) en salas que superan el ancho del fondo.
  - Nuevos conjuntos de tilesets gráficos en `assets/graphics/tilesets/`: `InfernoTiles.png`, `Tilesetv3.png`, `Tile_green.png` y `Tile_red.png`.
- **Efectos de Partículas y Peligros de Caída (`src/world/Room.py`)**:
  - Sistema de partículas atmosféricas flotantes con deriva sinusoidal dependiente del viento que colorean el ambiente según la fase activa.
  - Sistema de partículas de polvo (`dust_particles`) en despegues de salto (`on_jump_effect`) y aterrizajes (`on_land`).
  - Mecánica de caída al abismo (`_handle_player_fall_hazard()`): detecta caídas en el umbral inferior del mapa (`MAP_HEIGHT - 24`), aplica 20 puntos de daño por pinchos con sacudida de pantalla y reubica al jugador en el punto de spawn.
- **Resolución Dinámica de Punto de Aparición (*Spawn Point*) (`Room._extract_spawn_point`)**:
  - Detección automática en cascada: parámetro explícito > objetos Tiled en capas `objectgroup` (`spawn`, `player_spawn`, `start`) > propiedades del mapa (`spawn_x`, `spawn_y`) > coordenadas por defecto.

### Cambiado / Refactorizado
- **Integración de Entidades con Tilemaps (`src/entities/Entity.py`)**:
  - Adición de los atributos `tilemap` y `active_collision_layers` a la clase base `Entity`.
  - Adaptación de `_apply_movement_and_collision()` para consultar el motor de colisión multicapa en lugar de depender únicamente de una altura fija de suelo (`floor_y`).
  - Rediseño de `render_outline()` con técnica de doble pasada: un halo exterior suave (alpha 65) con desplazamiento a 2 píxeles combinado con el contorno interior nítido, aumentando notablemente la legibilidad del personaje sobre fondos contrastados.
- **Ajustes Visuales y Paleta del Jugador (`src/entities/Player.py`)**:
  - Incremento del brillo y opacidad en los colores de contorno neón (`(255, 120, 130, 240)` para rojo y `(100, 255, 175, 240)` para verde).
- **Animación de Caída Dedicada (`FallState.py` y `src/definitions/entity.py`)**:
  - `FallState` ahora reproduce la animación específica `"fall"` en lugar de reutilizar el ciclo de `"jump"`.
  - Añadida la animación `"fall"` a la forma Mago en `_MAGE_ANIMATIONS`.

---

## [0.6.0] - 2026-09-12

### Añadido
- **Capa de Simulación del Mundo (`src/world/Room.py`)**:
  - Nueva clase `Room` inspirada en la arquitectura de `06-princess` (`Dungeon`/`Room`) y `05-super_martian` (`GameLevel`), encargada de encapsular la geometría del nivel (78x13 tiles / 1248x208 px), el renderizado ambiental (cielo con gradiente por fase, suelo, cuadrícula y paredes), el ciclo de vida y reaparición de los 8 enemigos (cola de 3s), y la física sólida de separación.
- **Efecto de Sacudida de Pantalla (*Screen Shake*) y Cámara Oficial de Gale (`gale.camera.Camera`)**:
  - Integración nativa de `gale.camera.Camera` con delimitación automática de límites del mapa (`bounds = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)`).
  - Activación de *Screen Shake* dinámico (`camera.shake(...)`) en impactos cuerpo a cuerpo, combos de espada, pilares de fuego del Mago y al recibir daño por contacto.
- **Pantalla de Fin de Partida (`src/states/game/GameOverState.py`)**:
  - Nuevo estado apilado sobre `StateStack` con oscurecimiento ambiental rojizo, activado automáticamente cuando el jugador pierde todas sus formas (`player.is_dead()`), permitiendo reiniciar limpiamente mediante la tecla `Enter`.
- **Máquina de Estados Desacoplada para Enemigos con Salto Inteligente (`src/states/entity/enemy/`)**:
  - Desacoplamiento de estados atómicos en Gale: `EnemyPatrolState`, `EnemyChaseState`, `EnemyAttackState`, `EnemyHitState` y `EnemyDeathState`.
  - Nueva mecánica de persecución 2D con salto inteligente: enemigos con capacidad de salto (`crown` y configurados con `can_jump`) saltan hacia el jugador si este se encuentra en una plataforma superior o en el aire.

### Cambiado / Refactorizado
- **Simplificación y Desacoplamiento Radical de `PlayState.py`**:
  - Reducción del archivo de más de 430 líneas a ~60 líneas, transformándolo en un orquestador de estados puro que solo gestiona entradas globales (pausa, cambio de fase, cambio de forma), transiciones a `GameOverState` y proyección del HUD.
- **Rediseño y Optimización de la Máquina de Estados del Juego (`src/states/game/`)**:
  - **`TitleState.py`**: Rediseño centrado con título sombreado en dorado, subtítulo estilizado, animación de parpadeo para *"Presiona ENTER para iniciar"* y leyenda completa de controles.
  - **`PauseState.py` y `PhaseShiftState.py`**: Pre-creación de superficies de superposición (`self.overlay`) en `enter()`, eliminando la creación de `pygame.Surface(..., pygame.SRCALPHA)` y fuentes a 60 FPS en `render()`. Corrección de coordenadas que situaban los textos fuera de pantalla (-40 px).
  - **`__init__.py`**: Exportación explícita de `TitleState`, `PlayState`, `PauseState`, `PhaseShiftState` y `GameOverState`.
- **Renderizado Nítido de Fuentes Pixel Art (*Pixel-Crisp Rendering*) (`settings.py`)**:
  - Configuración del helper de texto con `antialias=False` para la tipografía oficial de assets (`Minimal4.ttf`), erradicando el suavizado difuminado/borroso de FreeType en resolución nativa (320x180) y obteniendo bordes de píxel afilados y fieles al estilo retro.
- **Centralización del Movimiento Horizontal (`src/states/entity/EntityBaseState.py`)**:
  - Método `apply_horizontal_movement()` compartido entre `WalkState`, `JumpState`, `FallState` y `AttackState`, eliminando duplicaciones de código de aceleración y desaceleración.
- **Compatibilidad de Cámara (`src/world/Camera.py`)**:
  - Adaptación como extensión directa de `gale.camera.Camera` preservando retrocompatibilidad para `get_offset()`.

### Corregido
- **Animación Estática al Caminar (`Player.change_animation`)**:
  - Incorporación de cláusula de guarda para evitar reiniciar animaciones idénticas que ya se encuentren en reproducción a 60 FPS, permitiendo que las tres transformaciones (`mage`, `sword`, `morph`) caminen y corran fluidamente en ambas fases.
- **Sincronización de Ventanas de Daño y Hitboxes Activos (`Player.is_attack_active`)**:
  - Calibración exacta de frames de windup vs impacto real: el enemigo ya no recibe daño en el frame 0 al presionar el botón de ataque, sino cuando la espada o el báculo conectan visualmente con el objetivo.
  - Soporte de combo para el segundo golpe de espada con identificación de impacto independiente (`swing_id`) y aplicación de daño de remate (`hit2_damage: 20`).
- **Prevención de Fuga de Estados en Habilidades Interrumpidas**:
  - Limpieza forzada de `area_active` en `AttackSpecialState.exit()` si el Mago sufre daño o muere durante la canalización de llamas.
  - Anulación de velocidad en `DashState.exit()` ante interrupciones.

### Eliminado
- **Purga de Código Muerto y Archivos Duplicados**:
  - Eliminación de `PlayerCommands.py` (obsoleto tras la migración al Command Pattern de Gale).
  - Eliminación de 8 archivos duplicados/huérfanos en `src/states/entity/player/` (`PlayerWalkState.py`, `PlayerAttackState.py`, etc.).
  - Eliminación de métodos no utilizados en entidades: `Entity.heal()`, `Player.toggle_skin()`, `Player._get_anim_dict()`, `Entity._anim_idx` y superficies no utilizadas de enemigos.

---

## [0.5.0] - 2026-09-12

### Añadido
- **Sistema Integral de Enemigos e Inteligencia Artificial (`src/entities/Enemy.py` y `src/states/entity/enemy/`)**:
  - Implementación de la entidad base `Enemy` extendiendo `Entity` con detección de rango de visión, rango de des-aggro (abandono de persecución si el jugador se aleja) y cese de hostilidad cuando el jugador es derrotado (retorno al patrullaje).
  - Máquina de estados modular y desacoplada para enemigos:
    - **`EnemyBaseState.py`**: Clase base para los estados de IA de los enemigos.
    - **`EnemyPatrolState.py`**: Patrullaje horizontal delimitado, persecución reactiva al detectar al jugador y alternancia entre múltiples tipos de ataques (`attack` y `attack2`).
    - **`EnemyHitState.py`**: Reacción a impactos con aturdimiento temporal, efecto de flash visual y retroceso.
    - **`EnemyDeathState.py`**: Secuencia de muerte con animación específica, desactivación de colisiones de ataque y remoción limpia del escenario.
  - **Física de Separación entre Enemigos**: Sistema de colisión y repulsión horizontal mutua para evitar que múltiples enemigos se superpongan o atraviesen al agruparse.
- **Integración y Calibración de los 8 Tipos de Enemigos (`settings.py` y `src/definitions/entity.py`)**:
  - **`skeleton_sword` (Espadachín Esqueleto - Fase Pasado / Verde)**: 45 frames con canvas uniforme acolchado (100x65) y pies alineados en (39, 59). Dos ataques cuerpo a cuerpo (estocada y corte alto).
  - **`monster_eyes` (Creeper de Ojos - Fase Futuro / Rojo)**: Dos ataques (mordisco cercano y embestida con garras), patrulla y persecución con límite de rango.
  - **`goblin` (Goblin Scout - Fase Pasado / Verde)**: Animaciones de doble daga (corte rápido y puñalada baja).
  - **`crown` (Cuervo - Fase Pasado / Verde)**: Picotazo rápido, animación de salto y vuelo bajo.
  - **`big_monster` (Gólem Raíz / Mini-jefe - Fase Futuro / Rojo)**: Animación limpia de pisotón corporal (80x64) y sistema sincronizado de peligros en el suelo (`boss_vines` con variantes `2a`, `2b`, `2c` y `miss` de 48x48) según referencias visuales.
  - **`monster2` (Shadow Lurker - Fase Pasado / Verde)**: Extracción y calibración de frames desde `pack 2 m1.aseprite` (48x48) con dos variantes de ataque sombrío.
  - **`monster3` (Horned Imp - Fase Futuro / Rojo)**: Extracción y calibración de frames desde `pack 3 monster 1.aseprite` (64x64) con animaciones completas.
  - **`cultist_priest` (Sacerdote Cultista - Fase Futuro / Rojo)**: 26 frames individuales en 200x200 con anclaje de pies en `feet_y = 182`, animación de invocación/ataque, impacto y muerte.
  - Estandarización de la altura de suelo en `floor_y = 160.0` para todos los enemigos según su bounding box.
- **Comandos Oficiales con Gale (`src/commands.py`)**:
  - Implementación completa del Command Pattern utilizando `CommandBindings` de Gale.
  - Registro de comandos de acción y de estado: `JUMP`, `STOP_JUMP`, `MOVE_LEFT`, `STOP_MOVE_LEFT`, `MOVE_RIGHT`, `STOP_MOVE_RIGHT`, `LOOK_UP`, `STOP_LOOK_UP`, `RUN`, `STOP_RUN`, `ATTACK`, `SPECIAL_ATTACK`, `DASH`, `NEXT_FORM`, `PREV_FORM` y `SHIFT_PHASE`.
  - Mapeo de teclas limpio y desacoplado del bucle principal (`W/A/S/D` y flechas para movimiento, `Espacio` para salto, `J` para ataque, `K` para especial, `C` para dash, `Q`/`E` para cambio de forma, `LShift` para correr).
- **Pruebas Automatizadas de Físicas y Habilidades Aéreas**:
  - Suite de validación en entorno headless (`dummy` video driver) para verificar aislamiento de gravedad, bloqueo vertical de dash y transiciones entre estados.

### Cambiado
- **Ajustes de Combate e Invulnerabilidad del Jugador**:
  - El ataque especial del espadachín (`AttackSpecialState.py`) ahora otorga invulnerabilidad temporal durante su ejecución y un breve margen al concluir (similar al dash de Morph), impidiendo interrupciones por daño en medio del ataque.
  - Sincronización del frame de impacto: el daño y la animación de `HitState` del jugador ahora se ejecutan exactamente cuando el ataque enemigo impacta visualmente, eliminando el daño anticipado.
- **Depuración Visual de Cajas de Golpeo**:
  - Eliminación de los marcos de depuración visual que aparecían en pantalla al asestar golpes, dejando una presentación limpia de los efectos e impactos.

### Eliminado
- **Limpieza de Spritesheets Temporales Obsoletos**:
  - Eliminación de las hojas de sprites combinadas sintéticas (`big_monster.png`, `cultist_priest.png`, `skeleton_sword.png`) tras migrar toda la carga a los frames y tiras originales modulares en `assets/graphics/monsters/`.

### Corregido
- **Bloqueo de Altura Vertical en Dash Aéreo de Morph (`src/states/entity/player/DashState.py`)**:
  - Se forzó `vy = 0.0` al entrar y durante la actualización del dash. Se erradicó la inercia ascendente residual que provocaba elevaciones no deseadas al iniciar el dash en medio de un salto.
  - Al concluir la animación, el personaje pasa de forma limpia a `FallState` si sigue en el aire, reanudando la gravedad solo tras el dash.
- **Suspensión Aérea del Ataque Especial de la Espada (`src/states/entity/player/AttackSpecialState.py`)**:
  - Se configuró `has_gravity = False` y se fijó `vy = 0.0` durante la animación del ataque especial.
  - El espadachín ahora queda suspendido en el aire sin perder altura mientras carga y ejecuta el corte, ejecutando el impulso final (`_sword_special_finish`, 78 px) y pasando a `FallState` solo al terminar.
- **Prevención de Dash Involuntario al Cambiar a Morph**:
  - Consumo inmediato y descarte del flag `dash_requested` en todos los estados (`IdleState`, `WalkState`, `JumpState`, `FallState`) cuando la forma activa no tiene dash (Mago y Espadachín).
  - Limpieza explícita de todos los buffers de intención en `Player.change_skin()`.
- **Restauración del Ataque Especial del Mago**:
  - Reconexión de los callbacks `on_update` (`_mage_special_update`) y `on_finish` (`_mage_special_finish`) en `AttackSpecialState`, permitiendo el despliegue progresivo de los 3 círculos de llamas.
- **Sensibilidad y Altura del Salto Variable**:
  - Eliminación del recorte prematuro de velocidad vertical en `JumpState.py`, restaurando la parábola natural y completa de salto con soporte auténtico de salto variable vía `jump_held`.

---

## [0.4.0] - 2026-09-12

### Cambiado / Refactorizado
- **Arquitectura Base Inspirada en *Ultimate Fantasy* (`Entity` vs `Player`)**:
  - Desacoplamiento total entre la lógica física genérica y la lógica específica del jugador.
  - **`src/entities/Entity.py`**: Nueva clase base generalizada que gestiona posición (`x`, `y`), velocidades (`vx`, `vy`), bounding boxes (`hitbox`), máquina de estados (`StateMachine`), gravedad condicional (`apply_gravity`), temporizador de animaciones y colisiones con los límites del mapa y piso.
  - **`src/entities/Player.py`**: Subclase especializada en el protagonista. Administra transformaciones de piel (`sword`, `morph`, `mage`), fases cromáticas (`red`, `green`), estadísticas de HP/MP, cooldowns, combo buffers y el sistema de comandos.
- **Modularización de la Máquina de Estados Inspirada en *Super Martian***:
  - Sustitución del estado monolítico `PlayerAirborneState` por dos estados aéreos atómicos:
    - **`JumpState.py`**: Gestiona el impulso ascendente, salto variable y doble salto.
    - **`FallState.py`**: Gestiona la caída libre por gravedad, control direccional horizontal y aterrizaje.
  - Estandarización de nombres de archivos en `src/states/entity/player/` (`IdleState`, `WalkState`, `JumpState`, `FallState`, `DashState`, `AttackState`, `AttackSpecialState`, `HitState`, `DeathState`).
  - Cada estado ahora interactúa de manera limpia a través de intenciones (`jump_requested`, `attack_requested`, `dash_requested`, etc.).

---

## [0.3.0] - 2026-09-11

### Añadido
- **Interfaz de Usuario y HUD Permanente (`src/ui/HUD.py`)**:
  - Barras proporcionales de vida (`HP`) y maná (`MP`) con contornos y relleno dinámico.
  - Integración de tipografía pixel art personalizada (`assets/fonts/Minimal4.ttf`).
  - Indicador numérico de vida y maná alineado con las barras.
  - Avatar de la forma activa en el HUD con borde temático.
  - Indicador visual de enfriamiento (cooldown de 5 segundos) al cambiar de forma: medidor circular/aro radial de progreso alrededor del icono.
- **Paleta Cromática de Fase Verde (`green`)**:
  - Reemplazo de la variante azul original por la variante verde para sincronizar con la fase temporal del juego (`Mage_green.png`, `Morph_green.png`, `sword_green.png`, `flame_green.png`).
  - Soporte para renderizado de contornos destacados (`Entity.render_outline`) para maximizar visibilidad del personaje sobre fondos oscuros.
- **Sistema de Combos y Ataque Direccional**:
  - Ataque vertical hacia arriba (`is_looking_up` + botón de ataque).
  - Ventana de buffer de combo en `AttackState` para encadenar el segundo golpe de espada antes de que finalice la primera fase de la animación.

### Cambiado
- **Ajuste de Tiempos e Intervalos de Animación**:
  - Modificación de los intervalos de animación en `src/definitions/entity.py` para permitir mayor legibilidad visual en los ataques rápidos y combos de la espada.

---

## [0.2.0] - 2026-09-11

### Añadido
- **Mapeo Centralizado de Entidades (`src/definitions/entity.py`)**:
  - Extracción de todas las constantes, hitboxes, parámetros de física (`GRAVITY = 850.0`, `WALK_SPEED = 90.0`, `RUN_SPEED = 140.0`, `JUMP_VELOCITY = -320.0`) y diccionarios de animación fuera de `settings.py`.
  - Definición de estadísticas base por personaje (`health`, `max_health`, `mana`, `max_mana`, costos de maná y daño).
  - Callbacks modulares de acción: `_sword_special_finish`, `_mage_special_update`, `_mage_special_finish`, `_morph_dash`.
- **Estados Base de Entidad (`src/states/entity/EntityBaseState.py`)**:
  - Arquitectura estándar para estados de entidad que soporta flags por estado como `has_gravity`.
- **Estados de Daño y Muerte (`HitState`, `DeathState`)**:
  - Manejo de daño con retroceso y tiempo de recuperación.
  - Detección de vida en cero con transición al estado de muerte o rotación entre formas disponibles.

### Corregido
- **Detección de Fin de Animación**:
  - Implementación de `is_animation_finished()` con temporizador de respaldo (`fallback_duration`) para prevenir que las animaciones de un solo ciclo queden atascadas indefinidamente.
- **Movimiento y Volteo (`facing`)**:
  - Solución al sprite estático al desplazarse de izquierda a derecha; orientación dinámica de sprites según `move_direction`.
- **Ataques en el Aire e Inercia Horizontal**:
  - Permitir activar ataques básicos y dashes mientras se está en suspensión aérea sin detener el juego en seco.

---

## [0.1.0] - Inicio del Proyecto

### Añadido
- **Estructura Base del Juego con el Motor Gale**:
  - Configuración inicial de ventana en `main.py` y `settings.py` (resolución base 320x180, escalado a 1280x720).
  - Inicialización de `ChronoBlight.py` gestionando el ciclo de vida del juego.
  - Carga de texturas, hojas de sprites y recortes de frames (`assets/graphics/`).
  - Máquina de estados principal del juego (`PlayState`, `TitleState`, `PauseState`, `PhaseShiftState`).
  - Cámara de seguimiento suave del jugador (`src/world/Camera.py`).
  - Prototipo inicial de las tres transformaciones del jugador: Espada (`Sword`), Mago (`Mage`) y Forma Amorfa (`Morph`).

