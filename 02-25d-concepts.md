# 02 — Hiểu 2.5D trong Godot 4

## 2.1 "2.5D" nghĩa là gì (và không là gì)

Có ít nhất 4 thứ bị gọi chung là 2.5D. Chốt rõ để không lẫn:

| Kiểu | Cách làm | Ví dụ | Có phải cái ta làm? |
|---|---|---|---|
| Isometric 2D | Vẽ sprite giả 3D, world thật là 2D | Diablo 1, Stardew (top-down) | ❌ |
| 2D gameplay trên nền 3D | Nhân vật đi trên trục 2D, hậu cảnh 3D | Trine, Ori (một phần) | ❌ |
| **HD-2D / Diorama** | **World 3D thật, actor là sprite billboard** | **Octopath Traveler, Live A Live remake** | ✅ **Đây** |
| 3D low-poly + texture pixel | Mọi thứ là mesh, texture pixel | Cruelty Squad, một số PSX-style | ❌ |

Cái ta làm: **`Node3D` root, camera 3D góc nghiêng, nhân vật/NPC/cây/thùng là `Sprite3D` pixel art đứng thẳng trong không gian, mặt đất và tường có thể là mesh hoặc GridMap.**

Lợi ích thật:

- Chiều sâu thật → che khuất (occlusion) tự nhiên: đi sau cái nhà thì bị nhà che, không cần code Y-sort thủ công
- Ánh sáng, sương mù, depth-of-field áp lên sprite → vibe "diorama đồ chơi"
- Camera có thể zoom, xoay nhẹ, tilt → cinematic mà art vẫn 2D
- Vẽ ít hơn: 1 cái cây dùng lại được ở mọi góc nhìn (nếu billboard)

Chi phí thật:

- Debug khó hơn 2D (toạ độ 3 trục, gimbal, depth sorting)
- Alpha blending + depth buffer = nguồn bug số 1 (mục 2.6)
- Sprite billboard xoay theo camera có thể trông "phẳng dán" nếu góc camera thay đổi nhiều

---

## 2.2 Hệ trục Godot 3D — học một lần cho khỏi lú

```
        +Y  (lên trời — độ cao)
         │
         │
         └────── +X  (sang phải)
        ╱
      +Z  (về phía camera / "xuống dưới" màn hình khi nhìn top-down)
```

- **+Y là lên.** Nhân vật đứng trên mặt phẳng `Y = 0`.
- **Mặt đất là mặt phẳng XZ.** Đi lại = thay đổi `x` và `z`. Nhảy = thay đổi `y`.
- **-Z là "phía trước" mặc định** của mọi `Node3D` (camera nhìn theo `-Z` của chính nó).
- Rotation trong Inspector là **độ**, trong code là **radian** → dùng `deg_to_rad()` / `rad_to_deg()`.

Quy ước tỉ lệ (chọn 1 và giữ nguyên cả project):

> **1 world unit = 1 mét = 16 pixel art.**

Nghĩa là nhân vật cao 32px → cao 2 unit. Ô tile 16×16px → 1×1 unit. Cực dễ tính, và khớp với vật lý/gravity mặc định của Godot.

---

## 2.3 `Sprite3D` — trái tim của 2.5D

`Sprite3D` (và `AnimatedSprite3D`) là một quad phẳng trong không gian 3D mang texture. Các property quan trọng:

| Property | Ý nghĩa | Giá trị cho ta |
|---|---|---|
| `texture` / `sprite_frames` | ảnh / bộ animation | |
| `pixel_size` | 1 pixel texture = bao nhiêu world unit | `0.0625` (= 1/16) |
| `axis` | quad nằm vuông góc trục nào | `Vector3.AXIS_Z` (mặc định) → sprite "đứng" |
| `billboard` | có quay mặt theo camera không | xem 2.4 |
| `shaded` | có nhận ánh sáng không | `false` để giữ palette; `true` để hòa vào ánh sáng scene |
| `texture_filter` | lọc texture | `Nearest` |
| `alpha_cut` | xử lý vùng trong suốt | `Discard` (xem 2.6) |
| `double_sided` | thấy được từ mặt sau | `true` nếu không billboard |
| `render_priority` | thứ tự vẽ khi cùng depth | dùng để fix chồng lấp khó |
| `offset` | dịch sprite trong mặt phẳng của nó | dùng để "đặt chân" sprite xuống đất |
| `centered` | gốc ở giữa sprite hay góc trên-trái | `true` + dùng `offset` |

### Tính `pixel_size`

Muốn 1 texel = 1/16 unit (khớp quy ước 2.2): `pixel_size = 1.0 / 16.0 = 0.0625`.

Sprite nhân vật 32×48 px → trong world: 2 unit rộng × 3 unit cao.

### "Đặt chân xuống đất"

Mặc định `Sprite3D` lấy tâm quad làm gốc → nửa sprite chìm dưới đất. Hai cách:

**Cách A (khuyến nghị)** — dùng `offset`, giữ `centered = true`:

```gdscript
# Sprite cao 48px, muốn gốc node trùng bàn chân → đẩy sprite lên nửa chiều cao.
sprite.offset = Vector2(0, 48.0 / 2.0)   # offset tính theo PIXEL, không phải unit
```

**Cách B** — bọc sprite trong một `Node3D` con và dịch node đó:

```
Player (CharacterBody3D)        ← gốc ở chân, y = 0
└── Visual (Node3D)             ← position.y = 1.5
    └── AnimatedSprite3D
```

Cách B dễ hiểu hơn và cho bạn chỗ để tween "squash & stretch", nghiêng khi chạy. Tài liệu này dùng **cách B**.

---

## 2.4 Billboard mode — chọn cái nào

| Mode | Hành vi | Dùng cho |
|---|---|---|
| `BILLBOARD_DISABLED` | Sprite cố định hướng, camera xoay thì thấy nó xéo/mỏng | Sàn, biển hiệu treo tường, sprite nằm ngang |
| `BILLBOARD_ENABLED` | Quay cả 3 trục theo camera, luôn đối diện hoàn toàn | Particle, item lơ lửng, hiệu ứng |
| `BILLBOARD_FIXED_Y` | **Chỉ quay quanh trục Y** — luôn đứng thẳng, mặt hướng camera | ✅ **Nhân vật, NPC, cây, thùng** |

`BILLBOARD_FIXED_Y` là lựa chọn của HD-2D: nhân vật luôn hướng mặt về camera nhưng vẫn "đứng" trên đất, không bị lật ngửa khi camera tilt.

Set trong code:

```gdscript
sprite.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
```

> **Quan trọng**: nếu camera của bạn **không bao giờ xoay** (camera ortho khóa cứng 1 góc, kiểu top-down 45°), bạn có thể để `BILLBOARD_DISABLED` và tự xoay sprite theo camera một lần lúc `_ready()`. Kết quả nét hơn (không có sai số quay từng frame) và rẻ hơn. Đây là lựa chọn tốt cho game này.

```gdscript
# scripts/util/face_camera_once.gd — gắn vào Node3D "Visual"
extends Node3D

func _ready() -> void:
	# Camera khóa cứng → chỉ cần xoay sprite khớp yaw camera một lần.
	var cam := get_viewport().get_camera_3d()
	if cam:
		rotation.y = cam.global_rotation.y
```

---

## 2.5 Camera — góc nào đẹp cho pixel

### 2.5.1 Orthographic vs Perspective

| | Orthographic | Perspective |
|---|---|---|
| Pixel giữ nguyên kích thước ở mọi độ sâu | ✅ | ❌ (xa thì nhỏ → pixel không đều) |
| Cảm giác | Sạch, giống 2D isometric | Có chiều sâu, cinematic |
| HD-2D thật (Octopath) dùng | — | ✅ perspective + tilt-shift |
| Dễ cho người mới | ✅ | Trung bình |

**Khuyến nghị: bắt đầu với Orthographic.** Pixel luôn cùng size = không bao giờ bị "pixel nhỏ pixel to" trong cùng khung hình. Đây là lỗi thẩm mỹ khó cứu nhất của pixel-3D.

Khi đã quen, thử Perspective với `fov` thấp (~25–35°) đặt camera xa — trông giống ortho nhưng có tí chiều sâu, rất "diorama".

### 2.5.2 Tính `size` của camera ortho cho pixel-perfect

Camera ortho có property `size` = **chiều cao vùng nhìn tính theo world unit**.

Công thức:

```
size = viewport_height_px / pixels_per_unit
```

Với viewport 320×180 và 16 px/unit:

```
size = 180 / 16 = 11.25
```

→ Set `Camera3D.size = 11.25`. Khi đó 1 texel của sprite = **đúng 1 pixel** trên viewport 320×180. Đây là con số làm pixel art của bạn nét như 2D thật.

> Nếu bạn dùng base 384×216: `size = 216 / 16 = 13.5`.

**Nhưng**: camera nghiêng (tilt) làm pixel không còn map 1:1 tuyệt đối theo chiều dọc — sprite billboard vẫn nét, nhưng mesh sàn sẽ hơi méo pixel. Đây là trade-off cố hữu của 2.5D, không phải bug. Cách giảm: giữ tilt ở góc "đẹp" (30°, 45°) và làm texture sàn ít chi tiết.

### 2.5.3 Cây camera rig

```
CameraRig (Node3D)                  ← script camera_rig.gd, đi theo player
└── Yaw (Node3D)                    ← rotation.y = 45  (hoặc 0)
    └── Pitch (Node3D)              ← rotation.x = -30 (nhìn chúc xuống)
        └── Camera3D                ← position.z = 20 (lùi xa), ortho size 11.25
```

Tách `Yaw`/`Pitch` ra node riêng giúp bạn xoay/tilt độc lập bằng tween mà không phá vị trí follow.

Các góc gợi ý:

| Pitch (x) | Yaw (y) | Cảm giác | Dùng cho |
|---|---|---|---|
| `-90°` | `0°` | Top-down thuần | Bản đồ, dungeon crawler |
| `-45°` | `45°` | Isometric cổ điển | Diablo-like, sàn tile rõ |
| `-30°` | `0°` | ¾ view, thấy mặt nhân vật rõ | ✅ **Game này** — adventure JRPG |
| `-25°` | `20°` | HD-2D, hơi lệch, cinematic | Cutscene, boss room |
| `-15°` | `0°` | Gần side-view, thấy hậu cảnh nhiều | Thị trấn có kiến trúc cao |

Tài liệu này dùng **pitch -30°, yaw 0°** cho gameplay. Yaw 0 nghĩa là trục world X = "phải" trên màn hình, trục Z = "xuống" — làm code di chuyển cực đơn giản (mục 04).

---

## 2.6 Vấn đề số 1 của 2.5D: transparency & depth sorting

Sprite pixel art có vùng trong suốt. Trong 3D, transparency + depth buffer là chỗ mọi người dính bug.

### Cơ chế

- Vật thể **opaque** được vẽ trước, ghi vào depth buffer → che khuất đúng.
- Vật thể **transparent** được vẽ sau, **sắp xếp theo khoảng cách tâm object tới camera**, và (mặc định) **không ghi depth**.
- → Hai sprite transparent giao nhau có thể vẽ sai thứ tự, hoặc sprite "biến mất" sau kính/nước.

### `alpha_cut` — vũ khí chính

`Sprite3D.alpha_cut` (thuộc `SpriteBase3D`):

| Giá trị | Cách hoạt động | Kết quả |
|---|---|---|
| `ALPHA_CUT_DISABLED` | transparency blend bình thường | ❌ Dễ sort sai |
| `ALPHA_CUT_DISCARD` | pixel có alpha < ngưỡng bị **loại bỏ**, phần còn lại là **opaque** | ✅ **Dùng cái này** — sort đúng như mesh thường |
| `ALPHA_CUT_OPAQUE_PREPASS` | vẽ 2 lượt: prepass ghi depth, rồi blend | Dùng khi cần cạnh mềm (khói, bóng) |
| `ALPHA_CUT_HASH` | dither alpha (nếu bản Godot của bạn có) | Hiệu ứng tan biến |

**Quy tắc: mọi sprite nhân vật/prop → `ALPHA_CUT_DISCARD`.** Pixel art vốn không có alpha nửa vời (hoặc 0 hoặc 255), nên discard không mất gì mà giải quyết 90% bug sorting.

```gdscript
sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
sprite.transparent = true          # vẫn cần bật để alpha channel có tác dụng
sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
sprite.shaded = false              # giữ màu palette nguyên bản
sprite.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
```

> Tên enum của `texture_filter` trên `SpriteBase3D` có thể là `BaseMaterial3D.TEXTURE_FILTER_NEAREST`. **Kiểm tra lại trên bản Godot bạn dùng** — cách chắc chắn nhất là set trong Inspector rồi bấm phải property → `Copy Property Path` / xem docs F1.

### Khi vẫn sort sai

1. Bật `no_depth_test = false` (mặc định) — nếu ai đó bật `true`, sprite sẽ vẽ đè lên mọi thứ.
2. Dùng `render_priority` (−128..127): số cao vẽ sau (đè lên). Dùng cho UI-trong-world như bong bóng thoại.
3. Sprite quá cao đứng sát tường: tâm quad ở giữa nên bị coi là "xa hơn" tường → tách prop lớn thành nhiều sprite nhỏ, hoặc chuyển prop đó thành mesh thật.

---

## 2.7 Collision: đi bộ trên `Y=0` hay 3D thật?

| Cách | Mô tả | Ưu | Nhược |
|---|---|---|---|
| **A. Sàn phẳng `Y=0`, không gravity** | Tự set `velocity.y = 0`, di chuyển chỉ XZ, tường là `StaticBody3D` dạng box | Đơn giản nhất, không bao giờ rơi khỏi map, dễ debug | Không có cao độ, không nhảy, không cầu thang |
| **B. Sàn mesh + gravity thật** | `CharacterBody3D` có gravity, `is_on_floor()`, sàn là `StaticBody3D`/`GridMap` có collision | Có bậc thang, dốc, nhảy, hố | Phải lo `floor_max_angle`, rơi xuyên sàn, nhân vật trượt |
| **C. Hybrid** | Gravity bật nhưng khóa cao độ bằng nhiều mặt phẳng "tầng" | Dungeon nhiều tầng gọn | Code phức tạp hơn |

**Khuyến nghị cho adventure 8-bit: cách B, nhưng làm sàn đơn giản (mặt phẳng + bậc thang box).** Lý do: bạn sẽ muốn có bậc thang trong hầm hải đăng, cây cầu, hố nước. Gravity của Godot rẻ và ổn định; giới hạn ở cách A sẽ khiến bạn phải viết lại ở tuần thứ 3.

Nếu game bạn **chắc chắn** một tầng phẳng (kiểu Zelda 1 top-down) thì cách A tiết kiệm thời gian thật.

### Hình dạng collision cho nhân vật

| Shape | Đánh giá |
|---|---|
| `CapsuleShape3D` | ✅ Mặc định tốt: trượt qua góc mượt, không kẹt |
| `CylinderShape3D` | Tốt cho top-down, không "leo" lên tường như capsule |
| `BoxShape3D` | Hay kẹt ở góc, tránh cho actor di chuyển |
| `SphereShape3D` | Lăn tuột trên dốc |

Cho game này: **CapsuleShape3D**, `radius = 0.35`, `height = 1.6` (nhân vật cao ~2 unit = 32px).

---

## 2.8 Scene mẫu chạy được: "sprite đứng trên sàn, camera ortho"

Tạo `scenes/levels/sandbox.tscn`:

```
Sandbox (Node3D)
├── WorldEnvironment                    ← Environment mới, Background = Color
├── DirectionalLight3D                  ← rotation x -50, y -35
├── Floor (StaticBody3D)
│   ├── MeshInstance3D                  ← BoxMesh size (30, 0.5, 30), position y = -0.25
│   └── CollisionShape3D                ← BoxShape3D size (30, 0.5, 30), position y = -0.25
├── Dummy (Node3D)                      ← position (0, 0, 0)
│   └── Visual (Node3D)                 ← position.y = 1.0
│       └── Sprite3D                    ← texture = art/characters/hero_idle.png
└── CameraRig (Node3D)
    └── Yaw (Node3D)                    ← rotation.y = 0
        └── Pitch (Node3D)              ← rotation.x = -30
            └── Camera3D                ← position.z = 20, projection Orthogonal, size 11.25
```

Script cấu hình sprite bằng code (đảm bảo không quên setting nào):

```gdscript
# scripts/util/pixel_sprite_3d.gd
# Gắn script này vào Sprite3D/AnimatedSprite3D để tự chuẩn hóa mọi setting pixel.
@tool
extends Sprite3D

## Số pixel art tương ứng 1 world unit. Giữ đồng bộ toàn project.
const PIXELS_PER_UNIT := 16.0

## Chiều cao sprite tính bằng pixel — dùng để đẩy chân sprite xuống đất.
@export var sprite_height_px: int = 48
@export var anchor_at_feet: bool = true

func _ready() -> void:
	_apply_pixel_settings()

func _apply_pixel_settings() -> void:
	pixel_size = 1.0 / PIXELS_PER_UNIT           # 1 texel = 1/16 unit
	texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	transparent = true
	alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD   # loại pixel trong suốt -> sort đúng
	shaded = false                                # giữ nguyên màu palette
	double_sided = true
	billboard = BaseMaterial3D.BILLBOARD_FIXED_Y # luôn đứng thẳng, mặt hướng camera
	centered = true
	if anchor_at_feet:
		offset = Vector2(0.0, sprite_height_px * 0.5)  # offset tính theo pixel
```

`@tool` để setting áp luôn trong editor, bạn thấy kết quả ngay không cần chạy game.

> Nếu Godot báo lỗi tên enum, xóa dòng đó, set thủ công trong Inspector, rồi dùng `Copy Property Path` để lấy tên chính xác. Đây là cách nhanh nhất để tự kiểm chứng API.

Camera setup bằng code (dễ tính lại khi đổi base resolution):

```gdscript
# scripts/util/pixel_camera.gd
extends Camera3D

const PIXELS_PER_UNIT := 16.0

func _ready() -> void:
	projection = Camera3D.PROJECTION_ORTHOGONAL
	# size = chiều cao vùng nhìn (world unit) = số pixel dọc / px-per-unit
	var vp_height: float = float(get_viewport().get_visible_rect().size.y)
	size = vp_height / PIXELS_PER_UNIT
	near = 0.1
	far = 200.0
```

> Lưu ý: nếu dùng `stretch mode = viewport`, `get_visible_rect().size` trả về **320×180** (kích thước logic) chứ không phải kích thước cửa sổ thật — đúng cái ta muốn.

---

## 2.9 Bài tập

1. Dựng `sandbox.tscn` như 2.8. Chạy → sprite đứng trên sàn, không chìm, không mờ.
2. Đặt thêm 3 `Sprite3D` cây ở các `z` khác nhau (`z = -4, 0, 4`). Di chuyển `Dummy` qua giữa chúng bằng cách sửa `position.x` trong Inspector khi game đang chạy (Remote tab). Xác nhận cây gần **che** nhân vật, cây xa **bị** nhân vật che.
3. Đổi `alpha_cut` sang `Disabled` cho tất cả sprite. Chạy lại. Quan sát viền đen/thứ tự vẽ sai. Đổi lại `Discard`.
4. Đổi camera sang `Perspective` với `fov = 30` và `position.z = 30`. So sánh cảm giác. Ghi lại bạn thích cái nào.
5. Đổi `billboard` giữa `Disabled` / `Fixed Y` / `Enabled`, đồng thời xoay `Yaw` sang `45°`. Quan sát khác biệt.

---

## 2.10 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Sprite chìm nửa dưới đất | Chưa `offset`/chưa dịch `Visual` | Mục 2.3 |
| Sprite có viền đen quanh pixel | Texture import không phải lossless, hoặc bilinear filter | Import: Compress `Lossless`, Filter `Nearest`, tắt Mipmaps |
| Sprite biến mất khi đi sau vật khác dù đứng trước | Depth sorting với transparent | `alpha_cut = Discard` |
| Sprite quá nhỏ / quá to | `pixel_size` sai hoặc scale node ≠ 1 | Đặt `pixel_size = 1/16`, giữ mọi `scale = (1,1,1)` |
| Pixel không đều (chỗ to chỗ nhỏ) | Camera perspective, hoặc scale node ≠ 1 | Dùng Orthographic; không bao giờ scale node để resize sprite |
| Sprite tối đen | `shaded = true` mà không có đèn | `shaded = false`, hoặc thêm `DirectionalLight3D` + ambient |
| Camera không thấy gì | `far` quá ngắn, hoặc camera đứng trong lòng vật thể | Set `far = 200`, lùi camera ra |
| Sprite nhấp nháy (z-fighting) | 2 sprite trùng chính xác cùng mặt phẳng | Lệch `z` một chút (0.01), hoặc dùng `render_priority` |
| Xoay camera thì cây trông mỏng như tờ giấy | `billboard = Disabled` | Chuyển `BILLBOARD_FIXED_Y` |
| Nhân vật rơi xuyên sàn | Sàn không có `CollisionShape3D`, hoặc collision layer lệch | Thêm shape; kiểm tra Layer/Mask |
