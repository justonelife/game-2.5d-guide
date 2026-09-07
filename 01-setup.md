# 01 — Thiết lập dự án Godot 4 cho pixel 2.5D

## 1.1 Tải Godot bản nào

| Bản | Dùng khi |
|---|---|
| **Godot 4.4 / 4.5 (stable)** | Mặc định. Tài liệu này viết theo dòng 4.3–4.5 |
| Godot 4.x **.NET (C#)** | Chỉ khi bạn đã giỏi C#. Với người mới: **chọn bản thường (GDScript)** |
| Godot 3.6 | Không. Node 3D/2.5D và renderer khác hẳn, mọi code ở đây sai |
| Bản dev/beta | Không, trừ khi bạn cần fix cụ thể |

Tải tại **godotengine.org/download**. Godot là 1 file thực thi, ~100MB, không cần installer.

> **Kiểm tra lại**: Godot ra bản mới rất nhanh. Mở `Help → About` để biết bản chính xác bạn đang chạy, và khi AI đưa code lạ thì tra `F1` (Editor Help) trong đúng bản đó.

Tải luôn **Export Templates** (`Editor → Manage Export Templates → Download and Install`) — cần cho chương 10. Làm sớm cho khỏi quên.

---

## 1.2 Tạo project

`New Project`:

- **Project Name**: `ngon-den-ca-nuc`
- **Renderer**:

| Renderer | Nên chọn khi |
|---|---|
| **Forward+** | Desktop, muốn ánh sáng/hậu kỳ đẹp nhất. Mặc định tốt để học |
| **Mobile** | Nhắm mobile, ít hậu kỳ |
| **Compatibility** | Nhắm **web (HTML5)** hoặc máy yếu. Ổn định nhất cho itch.io |

Với game pixel 8-bit, bạn **không cần** hiệu ứng nặng. Khuyến nghị: **Compatibility** nếu mục tiêu chính là web/itch.io; **Forward+** nếu chỉ desktop và muốn thử `glow`/`SDFGI` cho vibe HD-2D.

Đổi renderer sau vẫn được (`Project Settings → Rendering → Renderer`) nhưng có thể phải chỉnh lại vài hiệu ứng — chọn sớm đỡ mệt.

- **Version Control Metadata**: chọn `Git` → Godot tự tạo `.gitignore` hợp lý.

---

## 1.3 Cấu trúc thư mục chuẩn

Tạo đúng cấu trúc này **ngay từ đầu**. Godot lưu đường dẫn trong file `.tscn`, đổi thư mục sau sẽ đau (Godot có sửa được nhờ `.uid`/dependency fix, nhưng vẫn đau).

```
res://
├── addons/                 # plugin (Aseprite importer, Dialogic... nếu dùng)
├── art/
│   ├── characters/         # sprite sheet nhân vật, NPC
│   ├── props/              # cây, đá, thùng, đuốc
│   ├── tiles/              # texture đất/tường cho GridMap / mesh
│   ├── ui/                 # khung hộp thoại, icon item, font
│   └── vfx/                # hiệu ứng
├── audio/
│   ├── bgm/                # nhạc nền .ogg
│   └── sfx/                # tiếng .wav
├── data/                   # Resource dữ liệu: item, dialog, bảng
│   ├── items/
│   └── dialogs/
├── scenes/
│   ├── actors/             # player.tscn, npc_base.tscn
│   ├── props/              # crate.tscn, torch.tscn, door.tscn
│   ├── levels/             # town.tscn, dungeon_01.tscn
│   ├── ui/                 # dialogue_box.tscn, inventory_ui.tscn
│   └── main.tscn           # scene gốc chạy game
├── scripts/
│   ├── autoload/           # game_state.gd, scene_router.gd, audio.gd
│   ├── actors/
│   ├── systems/            # inventory.gd, save_system.gd, dialogue.gd
│   └── util/
└── AGENTS.md               # file context cho AI (chương 09)
```

Quy ước đặt tên (nhất quán quan trọng hơn "đúng"):

- File & thư mục: `snake_case` → `player_controller.gd`, `dungeon_01.tscn`
- Node trong scene: `PascalCase` → `AnimatedSprite3D`, `InteractZone`
- Class/Resource: `PascalCase` → `class_name ItemData`
- Biến/hàm GDScript: `snake_case`; constant: `SCREAMING_SNAKE`

---

## 1.4 Cấu hình pixel-perfect (phần quan trọng nhất chương này)

Vào `Project → Project Settings`. Bật **Advanced Settings** (toggle góc trên phải) mới thấy hết mục.

### 1.4.1 Kích thước cửa sổ

`Display → Window`:

| Setting | Giá trị | Vì sao |
|---|---|---|
| `Size → Viewport Width` | `320` | Base resolution 8-bit-ish (tỉ lệ 16:9) |
| `Size → Viewport Height` | `180` | 320×180 × 6 = 1920×1080 → scale nguyên chẵn |
| `Size → Window Width Override` | `1280` | Cửa sổ thật khi chạy editor (320×4) |
| `Size → Window Height Override` | `720` | |
| `Stretch → Mode` | `viewport` | Render cả 2D **và 3D** ở 320×180 rồi phóng to |
| `Stretch → Aspect` | `keep` | Giữ 16:9, thêm viền đen nếu cần |
| `Stretch → Scale Mode` | `integer` | **Bắt buộc cho pixel art** — chỉ scale ×2, ×3... không ×2.37 |

Vài lựa chọn base resolution phổ biến:

| Base | Scale ×N tới 1080p | Cảm giác |
|---|---|---|
| 320×180 | ×6 | Rất chunky, NES-ish. Ít không gian hiển thị |
| 384×216 | ×5 | Cân bằng tốt — khuyến nghị nếu 320 thấy chật |
| 480×270 | ×4 | Thoáng, gần SNES/HD-2D hiện đại hơn |
| 640×360 | ×3 | Pixel nhỏ, nhiều chi tiết, art tốn công hơn |

> Chọn **một** rồi khóa lại. Đổi base resolution giữa dự án = vẽ lại UI + tính lại camera.

### 1.4.2 Khác biệt `stretch mode`

| Mode | 2D | 3D | Dùng cho |
|---|---|---|---|
| `disabled` | render full res | full res | Không phù hợp pixel |
| `canvas_items` | render ở low-res logic nhưng scale phần tử 2D | **3D vẫn full res** | Game 2D thuần |
| `viewport` | render toàn bộ ở 320×180 rồi phóng | **3D cũng bị hạ xuống 320×180** | ✅ Game 2.5D của ta |

Đây là mấu chốt: `stretch mode = viewport` là cách đơn giản nhất để 3D của bạn **trông như 8-bit**. Không có nó, mesh 3D sẽ mịn còn sprite thì răng cưa → lệch phong cách.

**Cách khác (linh hoạt hơn)**: tự dựng `SubViewportContainer` + `SubViewport` 320×180 chứa world 3D, còn UI vẽ ở full res (UI nét, world pixel). Xem 1.6.

### 1.4.3 Texture filter — chống mờ

`Rendering → Textures`:

| Setting | Giá trị |
|---|---|
| `Canvas Textures → Default Texture Filter` | `Nearest` |

Cái này chỉ áp cho **2D/CanvasItem**. Với 3D bạn còn phải set từng chỗ:

- `Sprite3D` / `AnimatedSprite3D`: property **`Texture Filter` = `Nearest`** (trong Inspector, mục Flags/Base — tên chính xác có thể là `texture_filter`; kiểm tra lại trên bản Godot bạn dùng).
- `StandardMaterial3D` cho mesh: `Sampling → Filter = Nearest`.
- Trên chính file ảnh: chọn file `.png` trong FileSystem → tab **Import** → `Detect 3D` → đặt Compress Mode `Lossless`, tắt `Mipmaps`, đặt Filter `Nearest` → **Reimport**.

> Bẫy kinh điển: Godot có tính năng "Detect 3D" tự đổi import setting của texture khi bạn lần đầu dùng nó trong 3D → ảnh bỗng bị mờ/nén. Vào Project Settings → `Import → Texture → Detect 3D` (hoặc set từng texture) để kiểm soát. Nếu sprite đột nhiên mờ, kiểm tra chỗ này trước.

### 1.4.4 Chống rung pixel (jitter)

`Rendering → 2D → Snap`:

- `Snap 2D Transforms to Pixel`: `On`
- `Snap 2D Vertices to Pixel`: `On`

Cho 3D, không có snap tự động. Cách xử lý ở chương 04 (snap vị trí camera theo bước pixel).

### 1.4.5 Anti-aliasing — tắt hết

`Rendering → Anti Aliasing`:

- `Quality → MSAA 3D`: `Disabled`
- `Quality → Screen Space AA`: `Disabled`
- `Quality → Use TAA`: `Off`

TAA/FXAA sẽ làm nhòe cạnh pixel → mất chất 8-bit.

### 1.4.6 Input map

`Project Settings → Input Map`. Tạo trước các action sau (dùng suốt tài liệu):

| Action | Key gợi ý | Gamepad |
|---|---|---|
| `move_left` | A, ← | D-pad Left / Stick X- |
| `move_right` | D, → | D-pad Right |
| `move_up` | W, ↑ | D-pad Up |
| `move_down` | S, ↓ | D-pad Down |
| `interact` | Space, E, Enter | A / Cross |
| `cancel` | Esc, X | B / Circle |
| `inventory` | I, Tab | Y / Triangle |
| `pause` | Esc | Start |

---

## 1.5 Scene gốc `main.tscn`

Cây scene tối thiểu, tạo ngay để có chỗ chạy:

```
Main (Node)                          ← scripts/main.gd
├── WorldHolder (Node3D)             ← level được add vào đây khi runtime
├── UILayer (CanvasLayer)
│   ├── DialogueBox (Control)        ← chương 06
│   ├── InventoryUI (Control)        ← chương 06
│   └── FadeRect (ColorRect)         ← dùng khi chuyển màn
└── AudioHolder (Node)
```

`scripts/main.gd`:

```gdscript
extends Node

# Level đầu tiên khi bắt đầu game mới.
const FIRST_LEVEL := "res://scenes/levels/town.tscn"

@onready var world_holder: Node3D = $WorldHolder

func _ready() -> void:
	# SceneRouter là autoload (chương 06) — nó cần biết chỗ để nhét level vào.
	SceneRouter.register_world_holder(world_holder)
	SceneRouter.goto_level(FIRST_LEVEL, "spawn_default")
```

Đặt scene chạy mặc định: `Project Settings → Application → Run → Main Scene = res://scenes/main.tscn`.

> Ở chương 01 bạn chưa có `SceneRouter`. Tạm thời comment 2 dòng đó lại, hoặc load level trực tiếp:
> ```gdscript
> func _ready() -> void:
> 	var level := load(FIRST_LEVEL).instantiate()
> 	$WorldHolder.add_child(level)
> ```

---

## 1.6 (Tùy chọn) Kiến trúc SubViewport: world pixel, UI nét

Nếu bạn muốn chữ UI **không** bị pixel hóa (đọc dễ hơn nhiều trên màn hình lớn), đừng dùng `stretch mode = viewport`. Thay vào đó:

`Project Settings`: `Stretch Mode = canvas_items`, `Viewport = 1280×720` (hoặc để full).

```
Main (Node)
├── WorldView (SubViewportContainer)      ← stretch = true, texture_filter = Nearest
│   └── SubViewport                        ← size 320×180, render_target_update_mode = Always
│       └── WorldHolder (Node3D)           ← level 3D nằm trong đây
└── UILayer (CanvasLayer)                  ← vẽ ở full res, chữ nét
```

`scripts/util/world_view.gd`:

```gdscript
extends SubViewportContainer

const BASE_SIZE := Vector2i(320, 180)

@onready var vp: SubViewport = $SubViewport

func _ready() -> void:
	stretch = true                                     # phóng nội dung SubViewport cho vừa container
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST # không làm mờ khi phóng
	vp.size = BASE_SIZE
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	get_window().size_changed.connect(_on_window_resized)
	_on_window_resized()

func _on_window_resized() -> void:
	# Tính scale nguyên lớn nhất còn vừa cửa sổ → giữ pixel vuông tuyệt đối.
	var win := get_window().size
	var s: int = maxi(1, mini(win.x / BASE_SIZE.x, win.y / BASE_SIZE.y))
	var target := BASE_SIZE * s
	size = target
	position = (Vector2i(win) - target) / 2   # canh giữa, viền đen quanh
```

| Cách | Ưu | Nhược |
|---|---|---|
| `stretch mode = viewport` | Cấu hình 1 lần, xong. UI cùng phong cách world | Chữ UI chunky, khó đọc text dài; input toạ độ UI thô |
| SubViewport thủ công | UI nét, linh hoạt (thêm shader post-process riêng cho world) | Nhiều node hơn, phải tự tính scale, chuột→world cần convert |

**Khuyến nghị cho người mới**: bắt đầu bằng `stretch mode = viewport` (mục 1.4). Chuyển sang SubViewport khi bạn thực sự thấy chữ khó đọc. Đừng làm phức tạp trước khi gặp vấn đề.

---

## 1.7 Git ngay từ hôm nay

```bash
cd ngon-den-ca-nuc
git init
git add -A
git commit -m "chore: khởi tạo project Godot 4, cấu hình pixel-perfect"
```

`.gitignore` (Godot tự tạo nếu bạn chọn Git metadata; nếu không, tự thêm):

```gitignore
# Godot 4
.godot/
/android/
export_presets.cfg   # chứa đường dẫn máy bạn; bỏ dòng này nếu làm team và muốn share preset
*.translation
```

> `.godot/` là cache — **không** commit. Nếu bạn commit nó, project sẽ conflict liên tục.

---

## 1.8 Bài tập

1. Tạo project, set đủ mục 1.4, tạo `main.tscn`. Chạy F5 → thấy cửa sổ 1280×720 màu xám.
2. Thả một `Sprite2D` với ảnh pixel 16×16 vào `UILayer`. Nếu nó mờ → quay lại 1.4.3 tìm nguyên nhân.
3. Đổi `Stretch Scale Mode` từ `integer` sang `fractional`, chạy lại, kéo cửa sổ méo. Nhìn kỹ pixel bị biến dạng. Hiểu vì sao `integer` quan trọng, rồi đổi lại.
4. Commit Git lần đầu.

---

## 1.9 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Sprite bị mờ/nhòe | Texture filter Linear, hoặc "Detect 3D" đã đổi import setting | Set `Nearest` ở cả Project Settings, node, và tab Import → Reimport |
| Pixel to nhỏ không đều nhau | `Stretch Scale Mode = fractional` | Đổi thành `integer` |
| 3D nét, sprite răng cưa (lệch style) | `Stretch Mode = canvas_items` | Đổi `viewport`, hoặc dùng SubViewport (1.6) |
| Cạnh vật thể lung linh khi di chuyển | TAA/MSAA đang bật | Tắt hết ở 1.4.5 |
| Chạy F5 báo "No main scene" | Chưa set Main Scene | Project Settings → Application → Run |
| Chữ UI vỡ, không đọc được | Font vector bị scale ở low-res | Dùng **bitmap font pixel** (chương 06), hoặc kiến trúc SubViewport (1.6) |
| Project mở lại thì thiếu texture | Đã đổi tên/di chuyển file bằng Finder thay vì trong FileSystem của Godot | Luôn rename/move **trong Godot** để nó cập nhật tham chiếu |
