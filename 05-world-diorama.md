# 05 — Dựng thế giới: diorama 3D với art 2D

Mục tiêu: từ sandbox trống → **Làng Cá Nục** có nhà, cây, bến tàu, chiều sâu, ánh sáng đêm.

---

## 5.1 Triết lý dựng level 2.5D

Nghĩ về level như một **mô hình sân khấu** (diorama), không phải một map 2D.

```
        ┌─── Lớp 4: SKY / xa nhất (z ≈ -60)   trời, mặt trăng, đường chân trời
        │    ┌─── Lớp 3: BACKDROP (z ≈ -30)   núi, biển, hải đăng nhìn từ xa
        │    │    ┌─── Lớp 2: SET DRESSING     nhà, cây to, đá (có collision hoặc không)
        │    │    │    ┌─── Lớp 1: PLAYFIELD    sàn đi được, prop tương tác, NPC, player
CAMERA ◄┼────┼────┼────┤
        │    │    │    └─── Lớp 0: FOREGROUND   cỏ cao, cột, khung cửa che trước mặt player
```

- **Lớp 1 (playfield)** là nơi gameplay diễn ra. Giữ nó **phẳng và đơn giản**. Người chơi phải đọc được đường đi trong 1 giây.
- **Lớp 2–4** chỉ để đẹp. Không collision, không logic. Đây là chỗ bạn "mua" cảm giác thế giới lớn rẻ nhất.
- **Lớp 0 (foreground)** che một phần playfield → tạo chiều sâu mạnh nhất. Dùng ít, đúng chỗ (khung cửa hầm, tàng lá góc khung hình).

Quy tắc vàng: **nếu người chơi không đi lên nó và không tương tác với nó, nó không cần collision và nên rẻ nhất có thể.**

---

## 5.2 Blockout trước, art sau

Đây là kỷ luật quan trọng nhất chương này. Dựng level bằng hình hộp xám trước, chơi thử, sửa layout, **rồi** mới thay art.

```
Town_Blockout (Node3D)
├── Ground (StaticBody3D)
│   ├── CSGBox3D  size (30, 0.5, 30)      ← CSG rất tiện để blockout, xóa sau
│   └── CollisionShape3D
├── House1_Block (StaticBody3D)  CSGBox3D (6, 5, 5)   position (-8, 2.5, -6)
├── House2_Block (StaticBody3D)  CSGBox3D (5, 4, 5)   position ( 6, 2,  -4)
├── Pier_Block   (StaticBody3D)  CSGBox3D (4, 0.4, 12) position (0, 0.2, 12)
├── GateBlock    (StaticBody3D)  CSGBox3D (3, 4, 0.5) position (0, 2, -14)
└── NPC_Markers (Node3D)
    ├── Marker_Bay   (Marker3D)  position (-6, 0, -2)
    ├── Marker_Tam   (Marker3D)  position ( 5, 0,  2)
    └── Marker_Fish  (Marker3D)  position ( 0, 0, 10)
```

Chơi blockout và tự trả lời:

- [ ] Từ điểm spawn tới cổng hầm mất bao nhiêu giây? (Mục tiêu: 15–25s cho thị trấn nhỏ)
- [ ] Có chỗ nào người chơi bị kẹt/không biết đi đâu?
- [ ] 3 NPC có nằm trên đường đi tự nhiên không, hay phải cố ý tìm?
- [ ] Camera có bị nhà chắn tầm nhìn không?

Sửa xong mới vẽ art. **Tiết kiệm được nhiều tuần.**

> Lỗi kinh điển: vẽ 40 asset đẹp rồi phát hiện thị trấn quá to, đi bộ nhàm chán → phải bỏ nửa số asset. Blockout ngăn chuyện đó.

---

## 5.3 Sàn và tường: 3 cách

| Cách | Mô tả | Ưu | Nhược | Dùng cho |
|---|---|---|---|---|
| **A. Mesh phẳng + texture tile** | 1 `PlaneMesh` lớn, material lặp texture | Cực rẻ, 1 draw call | Không đa dạng, khó làm cao độ | Sàn thị trấn, sàn hầm |
| **B. GridMap** | Tilemap 3D thật, cần `MeshLibrary` | Dựng nhanh bằng chuột, collision tự động, dungeon rất phù hợp | Phải làm MeshLibrary trước, hơi rườm | Dungeon, hầm nhiều phòng |
| **C. Node thủ công** | Đặt từng `MeshInstance3D`/`CSGBox3D` | Kiểm soát tuyệt đối | Chậm, scene tree phình | Chi tiết đặc biệt, blockout |

**Cho game này**: thị trấn dùng **A** (sàn phẳng lớn) + **C** (prop). Hầm hải đăng dùng **B** (GridMap).

### 5.3.1 Sàn mesh + texture lặp (cách A)

```
Ground (StaticBody3D)               collision_layer = 1
├── MeshInstance3D
│   mesh = PlaneMesh, size (40, 40)
│   material_override = StandardMaterial3D:
│       albedo_texture = art/tiles/sand_16.png
│       uv1_scale = (40, 40, 1)     ← lặp 40 lần trên 40 unit -> 1 tile/unit
│       texture_filter = Nearest
│       shading_mode = Unshaded (hoặc Per-Pixel nếu muốn nhận ánh sáng)
│       cull_mode = Back
└── CollisionShape3D
    shape = BoxShape3D (40, 0.5, 40), position.y = -0.25
```

Texture `sand_16.png` phải **tileable** (mép trên khớp mép dưới). Import: `Repeat = Enabled`, `Filter = Nearest`, `Mipmaps = off`.

> `uv1_scale`: nếu tile của bạn là 16×16 px và bạn muốn 1 tile = 1 world unit thì `uv1_scale = (kích_thước_plane, kích_thước_plane, 1)`. Với plane 40×40 → `(40, 40, 1)`.

Muốn nhiều loại sàn (cát / gỗ bến / đá): dùng nhiều `MeshInstance3D` nhỏ hơn ghép lại, hoặc 1 texture atlas lớn vẽ tay cả khu (cách "vẽ nguyên bản đồ như một tấm ảnh" — rất hiệu quả cho thị trấn nhỏ, đây là cách nhiều game HD-2D indie làm).

### 5.3.2 GridMap cho dungeon (cách B)

Bước 1 — tạo `MeshLibrary`:

1. Tạo scene mới `art/tiles/dungeon_meshlib_source.tscn`, root `Node3D`
2. Thêm các node con, **mỗi node con = 1 tile**:
   ```
   Root (Node3D)
   ├── FloorStone (MeshInstance3D)      BoxMesh (1, 0.2, 1), material đá
   │   └── StaticBody3D
   │       └── CollisionShape3D          BoxShape3D (1, 0.2, 1)
   ├── WallStone (MeshInstance3D)        BoxMesh (1, 2, 1)
   │   └── StaticBody3D
   │       └── CollisionShape3D          BoxShape3D (1, 2, 1)
   └── StairStone (MeshInstance3D)       ...
   ```
   Tên node = tên tile trong palette. Collision **phải** là con của MeshInstance3D dưới dạng `StaticBody3D`.
3. `Scene → Export As... → MeshLibrary...` → lưu `art/tiles/dungeon.meshlib`

Bước 2 — dùng:

```
Dungeon01 (Node3D)
└── GridMap
    mesh_library = art/tiles/dungeon.meshlib
    cell_size = (1, 1, 1)              ← khớp 1 unit = 16px
    collision_layer = 1
```

Vẽ bằng chuột trong viewport 3D. Phím tắt hữu ích khi GridMap được chọn: giữ chuột trái để vẽ, `Shift` + kéo để vẽ hình chữ nhật, `Ctrl` + trái để xóa, `S`/`A` để xoay tile. (Phím tắt có thể khác giữa các bản — xem panel GridMap ở dưới viewport.)

> **Kiểm tra lại**: cách export MeshLibrary có thể đổi nhẹ giữa các bản Godot 4. Nếu không thấy menu, tìm `Scene → Export As`.

### 5.3.3 Tường "sprite" cho hầm 8-bit

Muốn hầm trông pixel hơn nữa: tường là `Sprite3D` (`billboard = Disabled`, `double_sided = true`) thay vì mesh, còn collision là `StaticBody3D` + `BoxShape3D` riêng. Cách này cho bạn vẽ tường bằng pixel art thật (có rêu, có vết nứt vẽ tay) thay vì texture lặp trên box.

Trade-off: nhiều node hơn, và tường chỉ đẹp ở một góc camera. Vì camera của ta khóa cứng → chấp nhận được.

---

## 5.4 Prop là sprite đứng

Cây, nhà, thùng, đuốc: tạo mỗi loại 1 scene tái dùng.

`scenes/props/tree_pine.tscn`:

```
TreePine (StaticBody3D)              collision_layer = 4 (solid_prop)
├── Sprite (Sprite3D)                ← script pixel_sprite_3d.gd (chương 02)
│   texture = art/props/tree_pine_64.png
│   sprite_height_px = 96
│   billboard = Fixed Y
│   alpha_cut = Discard
├── Collider (CollisionShape3D)
│   shape = CylinderShape3D radius 0.5, height 1.5
│   position.y = 0.75                ← chỉ chắn phần gốc, tán cây cho đi xuyên
└── Shadow (Sprite3D)                rotation.x = -90, y = 0.02
```

**Mẹo thiết kế quan trọng**: collision của cây/nhà chỉ nên bao **phần gốc**, không bao cả sprite. Người chơi mong đi được "sau" tán cây. Bao cả sprite làm nhân vật bị chặn ở khoảng không → cảm giác tệ.

### Bảng prop cho Làng Cá Nục

| Prop | Kích thước sprite | Collision | Ghi chú |
|---|---|---|---|
| Nhà tranh | 96×112 | Box (5, 3, 4) ở gốc | Có thể chia thành 2 sprite: thân + mái để sort tốt hơn |
| Cây thông | 64×96 | Cylinder r=0.5 h=1.5 | Chỉ gốc |
| Cột đèn dầu | 16×48 | Cylinder r=0.15 h=2 | Có `OmniLight3D` con |
| Thùng cá | 32×32 | Box (1,1,1) | Đẩy được → `RigidBody3D` (5.7) |
| Lưới cá phơi | 48×32 | Không | Trang trí |
| Bến gỗ | mesh | Box | Là sàn, không phải prop |
| Cổng hầm | 48×64 | Box (3, 4, 0.5) | Bật/tắt collision theo flag |
| Đuốc tường | 16×32 | Không | Có `OmniLight3D` + particle |

### Rải prop nhanh bằng script (tùy chọn)

Dựng 50 cây bằng chuột rất mệt. Dùng script `@tool` rải theo path:

```gdscript
# scripts/util/prop_scatter.gd
# Gắn vào một Node3D. Nhấn nút "Scatter" trong Inspector để rải prop.
@tool
extends Node3D

@export var prop_scene: PackedScene
@export var count: int = 20
@export var area_size: Vector2 = Vector2(20, 20)
@export var min_distance: float = 1.5
@export var random_seed: int = 12345

## Bấm để rải lại (Godot hiển thị checkbox; tick rồi nó tự bỏ tick).
@export var scatter_now: bool = false:
	set(value):
		if value and Engine.is_editor_hint():
			_scatter()

func _scatter() -> void:
	if prop_scene == null:
		push_warning("Chưa gán prop_scene")
		return

	# Xóa prop cũ do script tạo (giữ node đặt tay bằng cách check tên tiền tố).
	for child in get_children():
		if child.name.begins_with("Scattered_"):
			child.queue_free()

	var rng := RandomNumberGenerator.new()
	rng.seed = random_seed          # cùng seed -> cùng kết quả, có thể tái tạo
	var placed: Array[Vector3] = []
	var attempts := 0

	while placed.size() < count and attempts < count * 30:
		attempts += 1
		var p := Vector3(
			rng.randf_range(-area_size.x * 0.5, area_size.x * 0.5),
			0.0,
			rng.randf_range(-area_size.y * 0.5, area_size.y * 0.5)
		)
		# Bỏ điểm quá gần prop đã đặt -> tránh chồng lấp.
		var too_close := false
		for other in placed:
			if p.distance_to(other) < min_distance:
				too_close = true
				break
		if too_close:
			continue

		placed.append(p)
		var inst := prop_scene.instantiate()
		add_child(inst)
		inst.name = "Scattered_%d" % placed.size()
		inst.position = p
		# owner phải set để node được LƯU vào file .tscn khi chạy ở editor.
		inst.owner = get_tree().edited_scene_root
```

> Dòng `inst.owner = get_tree().edited_scene_root` là bắt buộc trong script `@tool`, không có nó node sẽ biến mất khi bạn lưu scene. Đây là bẫy mà AI hay quên — nhớ kiểm.

---

## 5.5 Lớp sâu (parallax 2.5D thật)

Trong 2D bạn phải code parallax. Trong 3D **nó miễn phí**: đặt vật ở `z` xa hơn, camera di chuyển → nó tự dịch chậm hơn.

Nhưng với **camera orthographic thì KHÔNG** — ortho không có phối cảnh, vật xa dịch đúng bằng vật gần. Đây là một trade-off thật của việc chọn ortho.

Ba cách xử lý:

| Cách | Mô tả | Đánh giá |
|---|---|---|
| **1. Perspective camera** | Đổi sang `PROJECTION_PERSPECTIVE`, `fov` 25–35°, camera lùi xa | Có parallax thật, pixel hơi không đều ở vật xa. Nhiều game HD-2D chọn cái này |
| **2. Backdrop dịch theo camera có hệ số** | Giữ ortho; script cho lớp xa di chuyển 0.3× camera | Kiểm soát tuyệt đối, pixel luôn đều. ✅ Khuyến nghị |
| **3. Backdrop tĩnh hoàn toàn** | Trời/núi đứng yên như tranh vẽ | Rẻ nhất, vẫn ổn với map nhỏ |

Script cho cách 2:

```gdscript
# scripts/util/parallax_layer_3d.gd
# Gắn vào Node3D chứa lớp hậu cảnh (núi, biển, mây).
extends Node3D

## 0 = đứng yên hoàn toàn; 1 = dính chặt camera (không parallax).
@export_range(0.0, 1.0, 0.05) var follow_factor: float = 0.3

## Nếu để trống, tự tìm camera hiện hành.
@export var camera: Camera3D

var _origin: Vector3
var _cam_origin: Vector3
var _ready_done := false

func _ready() -> void:
	_origin = global_position
	if camera == null:
		camera = get_viewport().get_camera_3d()
	if camera:
		_cam_origin = camera.global_position
		_ready_done = true

func _process(_delta: float) -> void:
	if not _ready_done:
		return
	# Camera dịch bao nhiêu -> lớp này dịch theo follow_factor lần bấy nhiêu.
	var cam_delta := camera.global_position - _cam_origin
	global_position = _origin + Vector3(cam_delta.x, 0.0, cam_delta.z) * follow_factor
```

Gợi ý `follow_factor`:

| Lớp | z | follow_factor |
|---|---|---|
| Trời / mặt trăng | -80 | `0.95` (gần như dính camera) |
| Đường chân trời, biển | -50 | `0.7` |
| Núi xa | -35 | `0.45` |
| Hải đăng nhìn từ xa | -22 | `0.25` |
| Playfield | 0 | không script (0) |
| Foreground | +6 | `-0.1` (dịch ngược, chiều sâu mạnh) |

---

## 5.6 Ánh sáng: giữ chất 8-bit mà vẫn đẹp

Đây là chỗ 2.5D thắng 2D thuần rõ rệt nhất — và cũng là chỗ dễ phá phong cách nhất.

### 5.6.1 Hai triết lý

| Triết lý | `Sprite3D.shaded` | Kết quả |
|---|---|---|
| **A. Sprite tự phát sáng** (unshaded) | `false` | Màu pixel hiện đúng như bạn vẽ. Ánh sáng chỉ ảnh hưởng mesh (sàn/tường). Palette được bảo toàn 100% |
| **B. Sprite nhận sáng** (shaded) | `true` | Nhân vật tối trong hầm, sáng dưới đèn → immersive hơn, nhưng màu lệch khỏi palette |

**Khuyến nghị: A cho nhân vật/NPC (giữ đọc được), B cho prop môi trường (cây, nhà) để chúng hòa vào scene.**

Hoặc cách trung dung: `shaded = false` nhưng dùng `modulate` để tint nhân vật theo vùng (script vùng ánh sáng đổi `sprite.modulate` khi player vào Area3D). Cách này giữ pixel sạch mà vẫn có cảm giác chuyển vùng.

### 5.6.2 `WorldEnvironment` cho đêm bên biển

```
WorldEnvironment
└── Environment (tạo mới, lưu ra data/env_night.tres để tái dùng)
    background_mode = Color
    background_color = #0b1026            ← xanh navy rất tối
    ambient_light_source = Color
    ambient_light_color = #2a3a6b         ← xanh lạnh, ánh trăng
    ambient_light_energy = 0.6
    tonemap_mode = Filmic                 ← hoặc Linear nếu muốn màu "phẳng" hơn
    glow_enabled = true
    glow_intensity = 0.5
    glow_bloom = 0.1
    glow_hdr_threshold = 0.9              ← chỉ chỗ rất sáng mới glow (đèn, lửa)
    fog_enabled = true
    fog_light_color = #16204a
    fog_density = 0.015
    fog_sky_affect = 0.0
```

> `glow` là hiệu ứng "đắt xắt ra miếng" cho pixel art: ngọn đuốc và hải đăng sẽ tỏa sáng nhìn rất ăn tiền. Nhưng đừng để `glow_hdr_threshold` thấp — sẽ nhòe toàn bộ sprite và mất chất 8-bit.
>
> Trên renderer **Compatibility** (nhắm web), một số hiệu ứng như SDFGI/SSAO/volumetric fog **không** khả dụng, và glow có thể khác. **Kiểm tra lại trên renderer bạn dùng** trước khi thiết kế art dựa vào hiệu ứng.

### 5.6.3 Đèn

| Đèn | Dùng cho | Setting gợi ý |
|---|---|---|
| `DirectionalLight3D` | "Ánh trăng" chung | `energy 0.4`, màu `#7f95d1`, rotation (-50, -35, 0), `shadow_enabled = true` |
| `OmniLight3D` | Đuốc, đèn dầu, cửa sổ nhà | `range 6`, `energy 2.5`, màu `#ffa64d`, `shadow_enabled = false` (rẻ) |
| `SpotLight3D` | Chùm sáng hải đăng | `range 40`, `spot_angle 15`, quét bằng tween |

Số lượng đèn: **giữ ≤ 8 đèn động cùng lúc trong tầm camera.** Pixel game không cần nhiều, và Compatibility renderer có giới hạn.

Đèn nhấp nháy (đuốc) — mẹo cực rẻ, hiệu quả cao:

```gdscript
# scripts/props/torch_flicker.gd
extends OmniLight3D

@export var base_energy: float = 2.5
@export var flicker_amount: float = 0.5
@export var flicker_speed: float = 8.0

var _t: float = 0.0
var _noise_offset: float = 0.0

func _ready() -> void:
	# Offset ngẫu nhiên -> nhiều đuốc không nhấp nháy đồng bộ (rất lộ nếu đồng bộ).
	_noise_offset = randf() * 100.0

func _process(delta: float) -> void:
	_t += delta * flicker_speed
	# Ghép 2 sin lệch tần -> trông "tự nhiên" hơn 1 sin đơn.
	var n := sin(_t + _noise_offset) * 0.6 + sin(_t * 2.3 + _noise_offset) * 0.4
	light_energy = base_energy + n * flicker_amount
```

### 5.6.4 Bóng đổ

`DirectionalLight3D` với `shadow_enabled = true` sẽ đổ bóng — **nhưng sprite billboard đổ bóng trông rất lạ** (bóng của một tấm giấy). Hai lựa chọn:

- Tắt shadow cho sprite: `Sprite3D` → `cast_shadow = SHADOW_CASTING_SETTING_OFF` (thuộc `GeometryInstance3D`)
- Dùng `blob shadow` giả như ở chương 04

**Khuyến nghị: tắt shadow thật cho tất cả sprite, dùng blob shadow.** Mesh (nhà, tường) thì cho đổ bóng thật.

---

## 5.7 Prop đẩy được (cho câu đố 2)

Thùng cá phải đẩy được lên bệ đá.

`scenes/props/pushable_crate.tscn`:

```
PushableCrate (RigidBody3D)
│   mass = 20.0
│   collision_layer = 4 (solid_prop)
│   collision_mask  = 1 | 2 | 4
│   axis_lock_angular_x = true          ← không cho lật
│   axis_lock_angular_z = true
│   linear_damp = 6.0                    ← dừng nhanh, không trượt như trên băng
│   angular_damp = 10.0
├── Collider (CollisionShape3D)  BoxShape3D (1, 1, 1), position.y = 0.5
└── Sprite (Sprite3D)            texture crate_32.png, billboard Fixed Y, offset (0,16)
```

Để `CharacterBody3D` đẩy được `RigidBody3D`, phải chủ động apply lực (physics của Godot **không** tự truyền lực từ `move_and_slide`):

```gdscript
## Thêm vào player.gd, gọi sau move_and_slide()
@export var push_force: float = 6.0

func _push_bodies() -> void:
	for i in get_slide_collision_count():
		var col := get_slide_collision(i)
		var body := col.get_collider()
		if body is RigidBody3D:
			# Đẩy theo phương ngang, tại điểm tiếp xúc.
			var dir := -col.get_normal()
			dir.y = 0.0
			if dir.length_squared() < 0.001:
				continue
			body.apply_impulse(
				dir.normalized() * push_force * get_physics_process_delta_time() * 60.0,
				col.get_position() - body.global_position
			)
```

Gọi `_push_bodies()` ngay sau `move_and_slide()` trong `_physics_process`.

> `RigidBody3D` cho puzzle đẩy hộp có nhược điểm: hộp có thể bị đẩy lệch, kẹt góc, hoặc trượt quá đà → puzzle "không bao giờ giải được". Nếu puzzle của bạn cần **chính xác**, dùng cách khác: hộp là `AnimatableBody3D` và bạn tự viết logic "đẩy 1 ô mỗi lần" (grid-based push, kiểu Sokoban). Với "Ngọn Đèn Cá Nục", bệ đá đủ rộng nên RigidBody chấp nhận được. **Đây là quyết định thiết kế, không phải kỹ thuật — cân theo cảm giác bạn muốn.**

---

## 5.8 Tổ chức level & tối ưu

### Cấu trúc level chuẩn

```
Town (Node3D)                             ← scripts/levels/level_base.gd
├── Environment (Node3D)
│   ├── WorldEnvironment
│   ├── Sun (DirectionalLight3D)
│   └── Backdrop (Node3D)                 ← script parallax_layer_3d.gd, factor 0.45
│       ├── Mountains (Sprite3D)
│       └── Sea (Sprite3D)
├── Terrain (Node3D)
│   ├── Ground (StaticBody3D)
│   └── Walls (Node3D)
├── Props (Node3D)                         ← trang trí, không logic
│   ├── Trees (Node3D)                     ← prop_scatter.gd
│   └── Buildings (Node3D)
├── Interactables (Node3D)                 ← có logic
│   ├── NPC_Bay (instance npc.tscn)
│   ├── NPC_Tam (instance npc.tscn)
│   ├── FishBasket (instance item_pickup.tscn)
│   └── DungeonGate (instance locked_gate.tscn)
├── Triggers (Node3D)
│   └── ToDungeon (instance level_portal.tscn)
├── Spawns (Node3D)
│   ├── spawn_default (Marker3D)
│   └── spawn_from_dungeon (Marker3D)
└── Foreground (Node3D)                    ← factor -0.1
    └── ForegroundLeaves (Sprite3D)
```

Tách `Props` (không logic) và `Interactables` (có logic) giúp bạn — **và AI** — tìm đúng chỗ khi sửa. Chương 09 nói rõ vì sao cấu trúc rõ ràng làm AI hữu ích hơn nhiều.

### Script level base

```gdscript
# scripts/levels/level_base.gd
class_name LevelBase
extends Node3D

## Nhạc nền của level này.
@export var bgm: AudioStream

## Tên hiển thị khi vào khu vực (hiện chữ giữa màn hình kiểu JRPG).
@export var display_name: String = ""

func _ready() -> void:
	if bgm:
		Audio.play_bgm(bgm)
	if display_name != "":
		HUD.show_area_title(display_name)


## SceneRouter gọi hàm này để đặt player vào đúng cửa vào.
func get_spawn_point(spawn_name: String) -> Marker3D:
	var spawns := get_node_or_null("Spawns")
	if spawns == null:
		push_warning("Level %s thiếu node Spawns" % name)
		return null
	var m := spawns.get_node_or_null(spawn_name) as Marker3D
	if m == null:
		push_warning("Không tìm thấy spawn '%s', dùng spawn đầu tiên" % spawn_name)
		for child in spawns.get_children():
			if child is Marker3D:
				return child
	return m
```

### Tối ưu (chỉ làm khi thấy chậm)

| Kỹ thuật | Khi nào |
|---|---|
| `MultiMeshInstance3D` cho cỏ/đá lặp nhiều | > 200 instance giống nhau |
| Gộp texture prop vào 1 atlas | Nhiều draw call vì nhiều texture khác nhau |
| `VisibleOnScreenNotifier3D` để tắt logic prop ngoài màn hình | Prop có `_process` chạy liên tục |
| Tắt `shadow_enabled` cho `OmniLight3D` | Nhiều đèn |
| `Occlusion Culling` (Project Settings) | Map lớn, nhiều tường |
| Giảm `Environment` effect | FPS thấp trên máy yếu / web |

**Đừng tối ưu trước khi đo.** Mở `Debug → Visible Collision Shapes` và panel **Monitor** khi chạy (F5 rồi tab Debugger → Monitors) để xem FPS, draw call, object count thật.

---

## 5.9 Bài tập

1. Blockout Làng Cá Nục theo 5.2. Chơi thử, đo thời gian đi từ spawn tới cổng hầm. Sửa nếu > 30s.
2. Thay sàn blockout bằng mesh + texture tile (5.3.1). Kiểm tra `uv1_scale` cho tile không bị kéo méo.
3. Làm `tree_pine.tscn` với collision chỉ ở gốc. Đặt 10 cây bằng `prop_scatter.gd`.
4. Set `WorldEnvironment` theo 5.6.2. So sánh ảnh chụp trước/sau.
5. Thêm 3 `OmniLight3D` đuốc có `torch_flicker.gd`. Xác nhận chúng nhấp nháy **không đồng bộ**.
6. Thêm lớp backdrop núi ở `z = -35` với `follow_factor = 0.45`. Đi bộ ngang map → xác nhận núi dịch chậm hơn.
7. Làm `pushable_crate.tscn` và đẩy được nó. Nếu nó lật/bay → kiểm tra `axis_lock_angular_*` và `mass`.
8. Dựng 1 phòng dungeon bằng GridMap (5.3.2).

---

## 5.10 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Texture sàn bị kéo giãn | `uv1_scale` sai | Đặt `uv1_scale = (size_x, size_z, 1)` |
| Texture sàn có đường kẻ ở mép tile | Filter Linear / Mipmaps / texture không tileable | Nearest, tắt Mipmaps, sửa mép texture |
| GridMap vẽ được nhưng player xuyên qua | MeshLibrary source chưa có `StaticBody3D` + `CollisionShape3D` | Thêm collision vào scene source rồi export lại MeshLibrary |
| GridMap tile lệch nửa ô | `cell_size` ≠ kích thước mesh, hoặc `cell_center_y` | Khớp `cell_size` với mesh; kiểm tra `cell_center_x/y/z` |
| Cây chắn cả tán, đi bị kẹt | Collision bao cả sprite | Thu collision về gốc cây |
| Prop `@tool` scatter biến mất khi lưu scene | Thiếu `inst.owner = get_tree().edited_scene_root` | Thêm dòng đó |
| Sprite hậu cảnh bị nhân vật che dù nó ở xa | `render_priority` bị đặt sai, hoặc `no_depth_test = true` | Reset `render_priority = 0`, tắt `no_depth_test` |
| Parallax không hoạt động | Camera là Orthographic | Dùng script 5.5 hoặc chuyển Perspective |
| Scene tối đen | `ambient_light_energy = 0`, không đèn, `shaded = true` | Tăng ambient hoặc đặt `shaded = false` |
| Glow làm mờ hết pixel | `glow_hdr_threshold` quá thấp | Tăng lên 0.9–1.1 |
| Bóng sprite trông như tấm bìa | Sprite đổ shadow thật | `cast_shadow = Off` + blob shadow |
| FPS tụt khi vào thị trấn | Quá nhiều đèn có shadow / draw call | Tắt shadow OmniLight, gộp atlas, đo bằng Monitors |
| Thùng đẩy bị bay/lật | `mass` thấp, `push_force` cao, chưa lock angular | Tăng `mass`, lock `angular_x/z`, tăng `linear_damp` |
| Thùng kẹt góc, puzzle không giải được | Bản chất RigidBody | Chuyển sang grid-based push (5.7) hoặc làm bệ rộng hơn |
