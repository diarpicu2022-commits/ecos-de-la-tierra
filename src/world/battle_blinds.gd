class_name BattleBlinds
extends Control

## La persiana del contrato «Persiana» §3: franjas horizontales de BLIND_STRIP
## px en ASH_950 que cubren la pantalla al entrar en combate y la descubren al
## salir. Es la única transición con esta forma (repertorio §3.1).
##
## - La primera franja es la de la fila del monstruo; las demás la siguen
##   hacia arriba y hacia abajo, repartidas en BLIND_SPREAD.
## - Cada franja avanza en DUR_BATTLE_BLINDS - BLIND_SPREAD con `ease-out`, en
##   píxeles enteros. La última termina justo a DUR_BATTLE_BLINDS.
## - El lado del que avanzan dice quién empieza: el de Ilan, el del monstruo o
##   los dos a la vez hacia el centro.
## - Al abrir, cada franja se recoge hacia el borde del que salió.
## - Con movimiento reducido no hay animación: la pantalla queda cubierta (o
##   descubierta) en el primer cuadro y se espera lo mismo.
##
## Se cuenta en cuadros de física, como el fundido de zona, para que la prueba
## la mida cuadro a cuadro.

signal finished

enum Side { LEFT, RIGHT, BOTH }

## Ancho cubierto de cada franja, en píxeles. Lo lee la prueba.
var widths: PackedInt32Array = []
var side: int = Side.BOTH
var closing := true
var running := false

var _origin := 0
var _frame := 0
var _frames := 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	size = get_viewport_rect().size
	widths.resize(strip_count())
	widths.fill(0)


func strip_count() -> int:
	return ceili(get_viewport_rect().size.y / DesignTokens.BLIND_STRIP)


## Cierra la pantalla empezando por la franja de la fila `row_y` (píxel de
## pantalla), avanzando desde `from`.
func close(row_y: int, from: int) -> void:
	_origin = clampi(row_y / DesignTokens.BLIND_STRIP, 0, strip_count() - 1)
	side = from
	closing = true
	_start()


## Abre la pantalla desde la misma fila y hacia el mismo lado.
func open() -> void:
	closing = false
	_start()


func _start() -> void:
	_frame = 0
	_frames = roundi(DesignTokens.DUR_BATTLE_BLINDS * Engine.physics_ticks_per_second)
	running = true
	_update()


func _physics_process(_delta: float) -> void:
	if not running:
		return
	_frame += 1
	_update()
	if _frame >= _frames:
		running = false
		finished.emit()


func _update() -> void:
	var count := strip_count()
	var full := int(size.x)
	var reduced := DesignTokens.reduced_motion
	var spread := DesignTokens.BLIND_SPREAD / DesignTokens.DUR_BATTLE_BLINDS
	var farthest := maxi(_origin, count - 1 - _origin)
	for i in count:
		var delay := 0.0 if farthest == 0 else spread * absi(i - _origin) / farthest
		var t := clampf((float(_frame) / _frames - delay) / (1.0 - spread), 0.0, 1.0)
		if reduced:
			t = 1.0
		var eased := 1.0 - pow(1.0 - t, 3.0)    # ease-out
		var amount := eased if closing else 1.0 - eased
		widths[i] = roundi(amount * full)
	queue_redraw()


func _draw() -> void:
	var strip := DesignTokens.BLIND_STRIP
	var full := int(size.x)
	for i in widths.size():
		var w := widths[i]
		if w <= 0:
			continue
		var y := i * strip
		match side:
			Side.LEFT:
				draw_rect(Rect2(0, y, w, strip), DesignTokens.ASH_950)
			Side.RIGHT:
				draw_rect(Rect2(full - w, y, w, strip), DesignTokens.ASH_950)
			Side.BOTH:
				var half := ceili(w / 2.0)
				draw_rect(Rect2(0, y, half, strip), DesignTokens.ASH_950)
				draw_rect(Rect2(full - half, y, half, strip), DesignTokens.ASH_950)
