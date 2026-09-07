# 04 — Nhân vật điều khiển

Mục tiêu chương: nhân vật pixel art đi 4 hướng trong world 3D, animation đổi theo hướng, camera đi theo mượt, đụng tường thì dừng.

---

## 4.1 Chọn node gốc: `CharacterBody3D` hay `CharacterBody2D`?

Câu hỏi này quan trọng vì nó khóa toàn bộ kiến trúc.

| | `CharacterBody3D` | `CharacterBody2D` (trong world 3D) |
|---|---|---|
| Vị trí | `Vector3` — dùng trực tiếp trong scene 3D | `Vector2` — phải tự map sang 3D mỗi frame |
| Va chạm | Physics 3D thật, va với mesh/GridMap/StaticBody3D | Physics 2D riêng biệt; **không** va được với collider 3D |
| Gravity/nhảy/dốc | Có sẵn: `is_on_floor()`, `floor_max_angle`, `apply_floor_snap()` | Phải tự viết trục cao độ |
| Che khuất (occlusion) tự nhiên | ✅ depth buffer lo hộ | ❌ phải tự tính Y-sort/render_priority |
| Raycast tương tác | `RayCast3D`, `Area3D` — cùng không gian với world | Phải viết 2 hệ toạ độ song song |
| Debug | Xem được collider trong viewport 3D | Collider 2D không hiện trong viewport 3D |
| Độ phức tạp ban đầu | Trung bình | Thấp lúc đầu, **cao về sau** |
| Phù hợp | ✅ Diorama 2.5D có chiều sâu thật | Game 2D thuần chỉ mượn nền 3D |

**Chốt: `CharacterBody3D`.**

Lý do quyết định: bạn muốn *chiều sâu thật* (đó là toàn bộ điểm của 2.5D). Dùng `CharacterBody2D` trong scene 3D nghĩa là bạn phải maintain **hai** hệ toạ độ và **hai** hệ collision không nói chuyện được với nhau. Nó chỉ hợp lý nếu gameplay của bạn hoàn toàn 2D và 3D chỉ là hình nền — không phải trường hợp này.

> Cách "sai nhưng phổ biến": dùng `Node2D` + tự tính `y = f(z)` để giả chiều sâu. Nó hoạt động cho game rất nhỏ, nhưng khi thêm cầu thang/nhiều tầng/cây che nhau thì sụp. Đừng đi đường này.

---

## 4.2 Cây scene `player.tscn`

```
Player (CharacterBody3D)                    ← scripts/actors/player.gd
│   collision_layer = 2 (player)
│   collision_mask  = 1 (world) | 8 (props solid)
├── Collider (CollisionShape3D)
│   └── CapsuleShape3D  radius 0.35, height 1.6
│   position.y = 0.8                        ← để đáy capsule ở y = 0 (chân)
├── Visual (Node3D)
│   position.y = 0.0
│   └── Sprite (AnimatedSprite3D)
│       sprite_frames = art/characters/hero.tres
│       pixel_size = 0.0625
│       billboard = Fixed Y
│       alpha_cut = Discard
│       texture_filter = Nearest
│       shaded = false
│       offset = (0, 16)                    ← sprite 32px cao -> đẩy lên 16px để chân ở gốc
├── InteractZone (Area3D)                   ← vùng phát hiện vật tương tác
│   collision_layer = 0
│   collision_mask  = 4 (interactable)
│   position = (0, 0.8, 0)
│   └── CollisionShape3D
│       └── SphereShape3D radius 1.2
├── ShadowSprite (Sprite3D)                 ← bóng giả: ellipse mờ nằm ngang
│   texture = art/vfx/blob_shadow.png
│   billboard = Disabled
│   rotation.x = -90                        ← úp xuống, nằm trên mặt đất
│   position.y = 0.02
│   modulate.a = 0.45
└── SpawnMarker (Marker3D)                  ← tiện cho debug
```

### Vì sao cần `ShadowSprite`

Sprite billboard "đứng" trong 3D dễ trông như **dán lơ lửng**. Một vệt bóng ellipse mờ nằm phẳng dưới chân là mẹo rẻ nhất để mắt tin nhân vật đang chạm đất. Đây là kỹ thuật HD-2D dùng thật. Làm 1 file `blob_shadow.png` 32×16 hình ellipse đen mờ là đủ.

### Collision layer — chốt bảng ngay từ đầu

Đặt tên layer trong `Project Settings → Layer Names → 3D Physics`:

| Bit | Tên | Dùng cho |
|---|---|---|
| 1 | `world` | Sàn, tường, địa hình |
| 2 | `player` | Nhân vật |
| 3 | `interactable` | NPC, item, cửa, công tắc (Area3D) |
| 4 | `solid_prop` | Thùng, đá đẩy được — chắn đường |
| 5 | `trigger` | Vùng chuyển màn, vùng cutscene |
| 6 | `enemy` | (nếu có sau) |

Đặt tên layer là việc 5 phút, tiết kiệm hàng giờ debug "sao nó không va".

---

## 4.3 Script nhân vật (đầy đủ, chạy được)

```gdscript
# scripts/actors/player.gd
class_name Player
extends CharacterBody3D

## ─── Thông số điều khiển ──────────────────────────────────────────────
@export var walk_speed: float = 4.0        # world unit/giây (~64 px/s ở 16px/unit)
@export var acceleration: float = 40.0     # tăng tốc — cao = phản hồi gắt, thấp = trơn trượt
@export var friction: float = 50.0         # giảm tốc khi nhả phím
@export var gravity: float = 24.0          # nặng hơn 9.8 cho cảm giác "game" chắc tay

## ─── Node tham chiếu ─────────────────────────────────────────────────
@onready var sprite: AnimatedSprite3D = $Visual/Sprite
@onready var visual: Node3D = $Visual
@onready var interact_zone: Area3D = $InteractZone

## ─── Trạng thái ──────────────────────────────────────────────────────
enum Facing { DOWN, UP, LEFT, RIGHT }
var facing: Facing = Facing.DOWN

## Khi true, player không nhận input (đang thoại, đang cutscene, đang chuyển màn).
var input_locked: bool = false

## Cache camera để không gọi get_camera_3d() mỗi frame.
var _cam: Camera3D = null


func _ready() -> void:
	_cam = get_viewport().get_camera_3d()
	# GameState phát signal khi hội thoại bắt đầu/kết thúc -> khóa/mở input.
	if GameState:
		GameState.input_lock_changed.connect(func(locked: bool) -> void:
			input_locked = locked
			if locked:
				velocity.x = 0.0
				velocity.z = 0.0
		)


func _physics_process(delta: float) -> void:
	_apply_gravity(delta)
	var wish := _read_move_input()
	_apply_horizontal_movement(wish, delta)
	move_and_slide()
	_update_animation(wish)


## Trọng lực: chỉ áp khi đang bay. Trên sàn thì zero để không tích lũy.
func _apply_gravity(delta: float) -> void:
	if is_on_floor():
		velocity.y = 0.0
	else:
		velocity.y -= gravity * delta


## Đọc input và chuyển từ "hướng màn hình" sang "hướng world" theo camera.
## Trả về vector đơn vị trên mặt phẳng XZ (y = 0).
func _read_move_input() -> Vector3:
	if input_locked:
		return Vector3.ZERO

	# get_vector(neg_x, pos_x, neg_y, pos_y): lên = y âm, xuống = y dương.
	var raw := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if raw == Vector2.ZERO:
		return Vector3.ZERO

	if _cam == null:
		_cam = get_viewport().get_camera_3d()
	if _cam == null:
		# Không có camera (test riêng lẻ) -> dùng trục world thẳng.
		return Vector3(raw.x, 0.0, raw.y).normalized()

	# Lấy hướng "trước" và "phải" của camera, dẹt xuống mặt phẳng ngang.
	var basis := _cam.global_transform.basis
	var cam_forward := -basis.z
	cam_forward.y = 0.0
	cam_forward = cam_forward.normalized()

	var cam_right := basis.x
	cam_right.y = 0.0
	cam_right = cam_right.normalized()

	# raw.y âm (phím lên) -> đi về phía trước camera -> nhân với -raw.y
	return (cam_right * raw.x + cam_forward * (-raw.y)).normalized()


## Tăng/giảm tốc mượt thay vì set velocity thẳng -> cảm giác có quán tính nhẹ.
func _apply_horizontal_movement(wish: Vector3, delta: float) -> void:
	var horiz := Vector3(velocity.x, 0.0, velocity.z)
	if wish != Vector3.ZERO:
		horiz = horiz.move_toward(wish * walk_speed, acceleration * delta)
	else:
		horiz = horiz.move_toward(Vector3.ZERO, friction * delta)
	velocity.x = horiz.x
	velocity.z = horiz.z


## Đổi animation + hướng sprite.
## Chú ý: hướng sprite tính theo INPUT MÀN HÌNH, không theo hướng world —
## người chơi bấm "lên" thì mong thấy lưng nhân vật, bất kể camera xoay thế nào.
func _update_animation(wish: Vector3) -> void:
	var raw := Input.get_vector("move_left", "move_right", "move_up", "move_down") \
		if not input_locked else Vector2.ZERO

	var moving := wish != Vector3.ZERO

	if moving:
		if absf(raw.x) > absf(raw.y):
			facing = Facing.RIGHT if raw.x > 0.0 else Facing.LEFT
		else:
			facing = Facing.DOWN if raw.y > 0.0 else Facing.UP

	var prefix := "walk" if moving else "idle"
	var anim_name := "%s_%s" % [prefix, _facing_suffix()]

	# flip_h: dùng chung sheet "side" cho cả left và right.
	sprite.flip_h = (facing == Facing.LEFT)

	if sprite.animation != anim_name and sprite.sprite_frames.has_animation(anim_name):
		sprite.play(anim_name)
	elif not sprite.is_playing():
		sprite.play()


func _facing_suffix() -> String:
	match facing:
		Facing.UP:
			return "up"
		Facing.LEFT, Facing.RIGHT:
			return "side"
		_:
			return "down"


## Hướng nhìn dạng vector world — dùng cho raycast tương tác, đặt item xuống...
func get_facing_vector() -> Vector3:
	match facing:
		Facing.UP:
			return Vector3(0, 0, -1)
		Facing.DOWN:
			return Vector3(0, 0, 1)
		Facing.LEFT:
			return Vector3(-1, 0, 0)
		_:
			return Vector3(1, 0, 0)
```

### Ghi chú thiết kế

- **`Input.get_vector` bị gọi 2 lần mỗi frame** (trong `_read_move_input` và `_update_animation`). Với 1 player thì vô hại; nếu muốn sạch hơn, cache vào biến `_raw_input` ở đầu `_physics_process`. Đây là ví dụ tốt cho việc "code AI viết chạy được nhưng có thể gọn hơn" — chương 09.
- **Camera-relative movement** làm sẵn để khi bạn xoay camera (cutscene, phòng đặc biệt) điều khiển vẫn tự nhiên. Nếu camera của bạn khóa cứng `yaw = 0` thì `cam_right = (1,0,0)`, `cam_forward = (0,0,-1)` → hàm cho ra đúng `Vector3(raw.x, 0, raw.y)`. Không mất gì.
- **`walk_speed = 4.0`** ≈ 64 px/giây. Với viewport 320px rộng, băng ngang màn hình mất 5 giây. Đó là tốc độ adventure hợp lý. Nếu thấy chậm, tăng lên 5.0–5.5; đừng vượt 7 vì pixel sẽ "trượt".

---

## 4.4 Camera follow

Godot có `Camera2D.position_smoothing` nhưng **`Camera3D` không có smoothing sẵn**. Phải tự viết (hoặc dùng addon `PhantomCamera` từ AssetLib nếu muốn nhiều tính năng).

`scenes/actors/camera_rig.tscn`:

```
CameraRig (Node3D)                  ← scripts/actors/camera_rig.gd
└── Yaw (Node3D)                    rotation.y = 0
    └── Pitch (Node3D)              rotation.x = -30
        └── Camera3D                position.z = 20, Orthogonal, size 11.25
```

```gdscript
# scripts/actors/camera_rig.gd
extends Node3D

## Node được đi theo. Để trống thì rig tự tìm Player trong scene.
@export var target: Node3D

## Cao hơn = camera bám gắt hơn. 6-10 là khoảng dễ chịu cho adventure.
@export var follow_speed: float = 8.0

## Nâng tâm ngắm lên ngực nhân vật thay vì bàn chân -> khung hình cân hơn.
@export var target_offset: Vector3 = Vector3(0.0, 1.0, 0.0)

## Bật để camera nhảy theo bước pixel -> hết hiện tượng sprite "rung" subpixel.
@export var snap_to_pixel: bool = true
@export var pixels_per_unit: float = 16.0

## Giới hạn camera trong biên map (để không thấy ra ngoài level).
@export var use_limits: bool = false
@export var limit_min: Vector3 = Vector3(-50, 0, -50)
@export var limit_max: Vector3 = Vector3(50, 0, 50)


func _ready() -> void:
	if target == null:
		# Tìm player theo group để rig dùng lại được ở mọi level.
		var players := get_tree().get_nodes_in_group("player")
		if not players.is_empty():
			target = players[0]
	if target:
		global_position = target.global_position + target_offset


# Dùng _process (không phải _physics_process) để camera mượt theo framerate màn hình.
func _process(delta: float) -> void:
	if target == null:
		return

	var goal := target.global_position + target_offset

	# Lerp độc lập framerate: 1 - exp(-k*dt). Nếu dùng lerp(a,b,k*dt) trực tiếp
	# thì tốc độ bám sẽ đổi khi FPS đổi -> camera "khác cảm giác" giữa các máy.
	var t := 1.0 - exp(-follow_speed * delta)
	var new_pos := global_position.lerp(goal, t)

	if use_limits:
		new_pos.x = clampf(new_pos.x, limit_min.x, limit_max.x)
		new_pos.z = clampf(new_pos.z, limit_min.z, limit_max.z)

	if snap_to_pixel:
		new_pos = _snap(new_pos)

	global_position = new_pos


## Làm tròn vị trí về bội số của 1 pixel world (1/16 unit).
## Giảm rung subpixel — thủ phạm số 1 làm pixel art trông "bẩn" khi di chuyển.
func _snap(p: Vector3) -> Vector3:
	var step := 1.0 / pixels_per_unit
	return Vector3(
		roundf(p.x / step) * step,
		roundf(p.y / step) * step,
		roundf(p.z / step) * step
	)
```

Nhớ thêm `Player` vào group `player`: chọn node `Player` → panel **Node → Groups** → thêm `player`.

### Snap pixel — trung thực về giới hạn

Snap camera giúp nhiều nhưng **không** làm pixel-perfect tuyệt đối, vì:

- Camera nghiêng 30° → 1 pixel world theo trục Z không map thành đúng 1 pixel dọc màn hình.
- Bản thân nhân vật cũng di chuyển subpixel.

Muốn perfect hơn thì phải snap **cả** vị trí render của sprite, và/hoặc dùng shader post-process. Với game 8-bit adventure, snap camera thường là đủ — mắt không bắt được phần còn lại. Đừng đổ 3 ngày vào việc này ở MVP.

Nếu vẫn thấy rung: thử `snap_to_pixel = false` và so sánh. Có trường hợp snap gây "giật bước" khó chịu hơn là rung mượt. **Chọn theo mắt bạn, không theo lý thuyết.**

---

## 4.5 Tương tác: nhấn nút để nói chuyện / nhặt đồ

Cơ chế: `InteractZone` (Area3D) thu thập các vật tương tác đang ở gần; nhấn `interact` → gọi vật **gần nhất**.

Interface cho mọi vật tương tác được:

```gdscript
# scripts/systems/interactable.gd
class_name Interactable
extends Area3D

## Chữ hiện trên prompt: "Nói chuyện", "Nhặt", "Mở"...
@export var prompt_text: String = "Kiểm tra"

## Ưu tiên khi có nhiều vật cùng tầm — số lớn được chọn trước.
@export var priority: int = 0

signal interacted(by: Node3D)

func _ready() -> void:
	collision_layer = 4     # bit 3 = interactable
	collision_mask = 0      # không cần tự dò ai
	add_to_group("interactable")

## Lớp con override hàm này.
func interact(by: Node3D) -> void:
	interacted.emit(by)

## Cho phép tắt tạm thời (ví dụ NPC đã nói xong, cửa đã mở).
func set_active(active: bool) -> void:
	monitoring = active
	monitorable = active
	collision_layer = 4 if active else 0
```

Thêm vào `player.gd`:

```gdscript
## ─── Tương tác ───────────────────────────────────────────────────────

func _unhandled_input(event: InputEvent) -> void:
	if input_locked:
		return
	if event.is_action_pressed("interact"):
		var target := _find_nearest_interactable()
		if target:
			target.interact(self)
			get_viewport().set_input_as_handled()


## Chọn vật tương tác gần nhất, ưu tiên vật nằm phía nhân vật đang nhìn.
func _find_nearest_interactable() -> Interactable:
	var best: Interactable = null
	var best_score: float = -INF
	var facing_vec := get_facing_vector()

	for area in interact_zone.get_overlapping_areas():
		if area is not Interactable:
			continue
		var it: Interactable = area
		var to_it := it.global_position - global_position
		var dist := to_it.length()
		if dist < 0.001:
			dist = 0.001

		# Điểm = ưu tiên thủ công + hướng nhìn khớp - khoảng cách.
		var dot := facing_vec.dot(to_it.normalized())
		var score := float(it.priority) * 10.0 + dot * 2.0 - dist

		if score > best_score:
			best_score = score
			best = it

	return best
```

> `area is not Interactable` là cú pháp GDScript của Godot 4.x. Nếu bản bạn dùng báo lỗi, viết `if not (area is Interactable): continue`. **Kiểm tra lại trên bản Godot bạn dùng.**

### Prompt "Nhấn E" hiện trên đầu vật

Thêm vào `player.gd` để cập nhật prompt mỗi frame (rẻ, chỉ vài vật):

```gdscript
func _process(_delta: float) -> void:
	var target := _find_nearest_interactable() if not input_locked else null
	# HUD là autoload hoặc node UI; hàm show_prompt/hide_prompt bạn viết ở chương 06.
	if target:
		HUD.show_prompt(target.prompt_text, target.global_position + Vector3.UP * 1.4)
	else:
		HUD.hide_prompt()
```

---

## 4.6 Animation: `AnimatedSprite3D` hay `AnimationPlayer`?

| | `AnimatedSprite3D` + `SpriteFrames` | `AnimationPlayer` |
|---|---|---|
| Đổi frame sprite | ✅ Sinh ra để làm việc này | Làm được (key vào `frame`) nhưng thủ công, mệt |
| Đồng bộ nhiều thứ (frame + SFX + spawn hitbox + tween scale) | ❌ | ✅ Track riêng cho từng property, gọi được method |
| Có `animation_finished` signal | ✅ | ✅ |
| Blend/transition | ❌ | Có (qua `AnimationTree`) |
| Độ phức tạp | Thấp | Trung bình |

**Khuyến nghị: dùng cả hai, phân vai rõ.**

- `AnimatedSprite3D` lo **frame pixel** (walk/idle/interact).
- `AnimationPlayer` lo **những gì không phải frame**: squash khi đáp đất, nhấp nháy khi bị thương, tween `Visual.position.y` khi nhảy, gọi SFX bước chân.

Ví dụ `AnimationPlayer` cho hiệu ứng "nhặt đồ" (tự tạo trong editor):

```
Animation "pickup" (0.4s):
  track 1: Visual:position:y      0.0 → 0.15 → 0.0      (nhún lên)
  track 2: Visual:scale           (1,1,1) → (0.9,1.1,1) → (1,1,1)
  track 3: Call Method  Audio.play_sfx("pickup")   @ 0.05s
  track 4: Call Method  Sprite.play("interact")    @ 0.0s
```

Gọi từ code:

```gdscript
func play_pickup_feedback() -> void:
	$AnimationPlayer.play("pickup")
	await $AnimationPlayer.animation_finished
```

---

## 4.7 Level test: `sandbox.tscn` có player

```
Sandbox (Node3D)
├── WorldEnvironment
├── DirectionalLight3D               rotation (-50, -35, 0)
├── Floor (StaticBody3D)             collision_layer = 1
│   ├── MeshInstance3D               PlaneMesh 40×40, material texture sàn (Nearest)
│   └── CollisionShape3D             BoxShape3D (40, 0.5, 40), y = -0.25
├── Walls (Node3D)
│   ├── WallN (StaticBody3D)         BoxShape3D (40, 4, 1), position (0, 2, -20)
│   ├── WallS (StaticBody3D)         position (0, 2, 20)
│   ├── WallE (StaticBody3D)         BoxShape3D (1, 4, 40), position (20, 2, 0)
│   └── WallW (StaticBody3D)         position (-20, 2, 0)
├── Player (instance player.tscn)    position (0, 0, 0), group "player"
└── CameraRig (instance camera_rig.tscn)
```

Chạy F5. Checklist mốc **M3**:

- [ ] WASD/arrow di chuyển được
- [ ] Animation đổi giữa idle và walk
- [ ] Đi lên thấy lưng, đi xuống thấy mặt, đi ngang sprite lật đúng
- [ ] Camera bám theo, không giật
- [ ] Đụng tường thì dừng, không xuyên, không rung
- [ ] Bóng dưới chân đi theo
- [ ] Không rơi khỏi sàn

---

## 4.8 Bài tập

1. Dựng `player.tscn` + `camera_rig.tscn` + `sandbox.tscn`. Đạt hết checklist M3.
2. Đổi `follow_speed` giữa `2.0`, `8.0`, `30.0`. Ghi lại cảm giác. Chọn số bạn thích.
3. Thêm `sprint`: giữ Shift → `walk_speed * 1.6`, animation `walk` chạy nhanh hơn (`sprite.speed_scale`).
4. Thêm animation `interact`: nhấn E khi không có vật gì gần → nhân vật vẫn diễn động tác 1 lần rồi về idle. (Gợi ý: `await sprite.animation_finished`, và khóa `input_locked` trong lúc đó.)
5. Đặt một `Interactable` đơn giản (Area3D + script in ra `print("hello")`) trong sandbox. Nhấn E gần nó → thấy log.
6. Thêm biên camera: set `use_limits = true`, `limit_min/max` = ±16 → camera không thấy ra ngoài tường.

---

## 4.9 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Nhân vật không di chuyển | Chưa tạo Input action, hoặc gõ sai tên action | Kiểm tra Input Map; tên phải khớp chính xác chữ |
| Di chuyển nhưng trượt vô hạn | Không gọi `move_and_slide()`, hoặc `friction` = 0 | Gọi `move_and_slide()` cuối `_physics_process` |
| Nhân vật rơi mãi | Sàn không có collision, hoặc `collision_mask` player không chứa layer world | Kiểm tra Layer/Mask (mục 4.2) |
| Nhân vật "leo" lên tường | Capsule + `floor_max_angle` rộng | Giảm `floor_max_angle` (mặc định 45°), hoặc dùng `CylinderShape3D` |
| Nhân vật rung khi áp tường | `acceleration` quá cao + collision | Giảm `acceleration`, hoặc bật `floor_snap_length` |
| Animation không đổi | Tên animation trong `SpriteFrames` không khớp `"walk_down"`... | In ra `sprite.sprite_frames.get_animation_names()` để đối chiếu |
| Sprite lật ngược hướng | `flip_h` áp cho hướng sai | Đổi điều kiện `facing == Facing.LEFT` ↔ `RIGHT` theo hướng sheet bạn vẽ |
| Đi lên thì nhân vật đi xuống | Dấu của `raw.y` | Nhớ: phím **lên** cho `raw.y = -1`. `cam_forward * (-raw.y)` |
| Camera giật cục | Dùng `_physics_process` cho camera, hoặc `snap_to_pixel` với `follow_speed` thấp | Chuyển sang `_process`; hoặc tắt snap để so sánh |
| Camera bị "trễ" nhiều rồi vọt tới | `lerp` không độc lập framerate | Dùng công thức `1 - exp(-k*dt)` như trong code |
| Nhấn E không có gì xảy ra | `InteractZone.collision_mask` không chứa layer `interactable`, hoặc Interactable có `monitorable = false` | Mask = bit 3; kiểm tra `set_active(true)` |
| Nhấn E kích hoạt 2 vật | Cả `_unhandled_input` và `_input` đều xử lý | Gọi `get_viewport().set_input_as_handled()` |
| Bóng dưới chân "dựng đứng" | `ShadowSprite.billboard` đang bật | Set `Disabled` + `rotation.x = -90` |
| Bóng chìm trong sàn (z-fighting) | Cùng cao độ với sàn | `position.y = 0.02` |
