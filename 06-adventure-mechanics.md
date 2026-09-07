# 06 — Cơ chế phiêu lưu

Chương nặng nhất về code. Thứ tự làm: **Autoload → Dialog → Inventory → Interactable → Flags → Save → Chuyển màn**. Làm xong từng phần rồi test, đừng viết hết mới chạy.

---

## 6.1 Nền tảng: Autoload singleton

Autoload = node tồn tại suốt game, không bị xóa khi đổi scene. Đây là chỗ giữ state.

Đăng ký ở `Project Settings → Globals → Autoload` (tên trong Godot 4 có thể là tab **Globals**):

| Tên (Node Name) | Path | Vai trò |
|---|---|---|
| `GameState` | `res://scripts/autoload/game_state.gd` | Flags, inventory, dữ liệu tiến trình |
| `SceneRouter` | `res://scripts/autoload/scene_router.gd` | Chuyển màn, fade, spawn point |
| `Dialogue` | `res://scripts/autoload/dialogue.gd` | Chạy hội thoại |
| `SaveSystem` | `res://scripts/autoload/save_system.gd` | Ghi/đọc file save |
| `Audio` | `res://scripts/autoload/audio.gd` | BGM/SFX (chương 08) |
| `HUD` | `res://scenes/ui/hud.tscn` | Prompt, tiêu đề khu vực (autoload cả scene được) |

**Thứ tự autoload quan trọng**: `GameState` phải trước `SceneRouter` và `SaveSystem` vì chúng phụ thuộc nó. Kéo thả để sắp thứ tự trong danh sách.

> Nguyên tắc chống rối: **chỉ `GameState` giữ dữ liệu. Các autoload khác chỉ có hành vi.** Nếu bạn thấy mình lưu tiến trình ở 3 chỗ khác nhau → sẽ có bug save/load. Một nguồn sự thật duy nhất.

### `game_state.gd`

```gdscript
# scripts/autoload/game_state.gd
extends Node

## ─── Signals: hệ thống khác lắng nghe để phản ứng ────────────────────
signal flag_changed(flag_name: String, value: bool)
signal inventory_changed
signal input_lock_changed(locked: bool)

## ─── Dữ liệu tiến trình (tất cả những gì cần SAVE) ───────────────────
## Cờ cốt truyện. Không tồn tại trong dict = false.
var flags: Dictionary = {}

## Inventory: { item_id: số lượng }
var inventory: Dictionary = {}

## Level hiện tại + spawn point, để save/load quay đúng chỗ.
var current_level_path: String = ""
var current_spawn: String = "spawn_default"

## Tổng thời gian chơi (giây) — hiện ở màn save.
var playtime: float = 0.0

## Đếm số nguồn đang khóa input (thoại + cutscene có thể trùng nhau).
var _lock_count: int = 0


func _process(delta: float) -> void:
	playtime += delta


## ─── Flags ───────────────────────────────────────────────────────────

func set_flag(flag_name: String, value: bool = true) -> void:
	var old: bool = flags.get(flag_name, false)
	if old == value:
		return
	if value:
		flags[flag_name] = true
	else:
		flags.erase(flag_name)     # không lưu false -> file save gọn
	flag_changed.emit(flag_name, value)


func has_flag(flag_name: String) -> bool:
	return flags.get(flag_name, false)


## Kiểm tra nhiều flag cùng lúc. Tiền tố "!" = phải KHÔNG có flag đó.
## Ví dụ: has_all_flags(["has_fish", "!gave_fish"])
func has_all_flags(required: Array) -> bool:
	for f in required:
		var name_str := String(f)
		if name_str.begins_with("!"):
			if has_flag(name_str.substr(1)):
				return false
		elif not has_flag(name_str):
			return false
	return true


## ─── Inventory ───────────────────────────────────────────────────────

func add_item(item_id: String, amount: int = 1) -> void:
	if amount <= 0:
		return
	inventory[item_id] = inventory.get(item_id, 0) + amount
	inventory_changed.emit()


## Trả về true nếu bỏ được đủ số lượng. False = không đủ, KHÔNG bỏ gì.
func remove_item(item_id: String, amount: int = 1) -> bool:
	var have: int = inventory.get(item_id, 0)
	if have < amount:
		return false
	if have == amount:
		inventory.erase(item_id)
	else:
		inventory[item_id] = have - amount
	inventory_changed.emit()
	return true


func has_item(item_id: String, amount: int = 1) -> bool:
	return inventory.get(item_id, 0) >= amount


func get_item_count(item_id: String) -> int:
	return inventory.get(item_id, 0)


## ─── Khóa input ──────────────────────────────────────────────────────
## Dùng đếm thay vì boolean: nếu cutscene và dialog cùng khóa,
## dialog kết thúc không được mở khóa khi cutscene còn chạy.

func push_input_lock() -> void:
	_lock_count += 1
	if _lock_count == 1:
		input_lock_changed.emit(true)


func pop_input_lock() -> void:
	_lock_count = maxi(0, _lock_count - 1)
	if _lock_count == 0:
		input_lock_changed.emit(false)


func is_input_locked() -> bool:
	return _lock_count > 0


## ─── Serialize cho save (chương 6.7) ─────────────────────────────────

func to_dict() -> Dictionary:
	return {
		"flags": flags.duplicate(),
		"inventory": inventory.duplicate(),
		"level": current_level_path,
		"spawn": current_spawn,
		"playtime": playtime,
	}


func from_dict(data: Dictionary) -> void:
	flags = data.get("flags", {})
	inventory = data.get("inventory", {})
	current_level_path = data.get("level", "")
	current_spawn = data.get("spawn", "spawn_default")
	playtime = float(data.get("playtime", 0.0))
	inventory_changed.emit()


## Reset khi bắt đầu game mới.
func reset() -> void:
	flags.clear()
	inventory.clear()
	current_level_path = ""
	current_spawn = "spawn_default"
	playtime = 0.0
	_lock_count = 0
	inventory_changed.emit()
	input_lock_changed.emit(false)
```

---

## 6.2 Dữ liệu item bằng `Resource`

Dùng custom `Resource` thay vì Dictionary hardcode: có type checking, sửa được trong Inspector, AI đọc hiểu dễ hơn.

```gdscript
# scripts/systems/item_data.gd
class_name ItemData
extends Resource

@export var id: String = ""                     # khóa duy nhất, ví dụ "rusty_key"
@export var display_name: String = ""           # "Chìa Khóa Rỉ"
@export_multiline var description: String = ""  # mô tả trong inventory
@export var icon: Texture2D                     # icon 16x16
@export var stackable: bool = false
@export var max_stack: int = 1
@export var usable: bool = false                # có nút "Dùng" trong inventory không
@export var quest_item: bool = false            # không bỏ được
```

Tạo file `.tres` trong `data/items/`:

| File | id | display_name |
|---|---|---|
| `fish.tres` | `fish` | Cá Nục Tươi |
| `rusty_key.tres` | `rusty_key` | Chìa Khóa Rỉ |
| `salt_fire_1.tres` | `salt_fire_1` | Lửa Muối (viên thứ nhất) |
| `salt_fire_2.tres` | `salt_fire_2` | Lửa Muối (viên thứ hai) |
| `salt_fire_3.tres` | `salt_fire_3` | Lửa Muối (viên thứ ba) |
| `lantern.tres` | `lantern` | Đèn Dầu Cũ |

Bảng tra item (autoload phụ hoặc static):

```gdscript
# scripts/systems/item_db.gd
class_name ItemDB
extends RefCounted

const ITEM_DIR := "res://data/items/"

static var _cache: Dictionary = {}

## Nạp tất cả item .tres một lần, cache theo id.
static func _ensure_loaded() -> void:
	if not _cache.is_empty():
		return
	var dir := DirAccess.open(ITEM_DIR)
	if dir == null:
		push_error("Không mở được %s" % ITEM_DIR)
		return
	for file_name in dir.get_files():
		# Bản export sẽ đổi .tres -> .res, xử lý cả hai.
		if not (file_name.ends_with(".tres") or file_name.ends_with(".res")):
			continue
		var res: Resource = load(ITEM_DIR + file_name)
		if res is ItemData and res.id != "":
			_cache[res.id] = res

static func get_item(id: String) -> ItemData:
	_ensure_loaded()
	return _cache.get(id, null)

static func all_items() -> Array:
	_ensure_loaded()
	return _cache.values()
```

> **Bẫy export**: khi export game, Godot có thể chuyển `.tres` → `.res` và `DirAccess.get_files()` trên `res://` **có thể không liệt kê được file trong PCK** ở một số cấu hình. Cách an toàn hơn cho bản release: giữ một `Array[ItemData]` `@export` trong một resource "ItemDatabase.tres" và load nó. Nếu bạn thấy inventory trống sau khi export → đây là nguyên nhân. **Kiểm tra lại khi export lần đầu (chương 10).**

---

## 6.3 Hệ thống hội thoại

### 6.3.1 Dữ liệu dialog

Dùng JSON — dễ viết, dễ nhờ AI sinh, dễ sửa không cần mở Godot.

`data/dialogs/npc_bay.json`:

```json
{
  "start": {
    "conditions": [],
    "next": "bay_first_meet"
  },

  "bay_first_meet": {
    "conditions": ["!met_bay"],
    "speaker": "Ông Bảy",
    "portrait": "res://art/ui/portraits/bay.png",
    "lines": [
      "Đêm nay đèn không sáng, cháu à.",
      "Ba đêm rồi. Thuyền ngoài kia không thấy đường về."
    ],
    "set_flags": ["met_bay"],
    "next": "bay_ask_fish"
  },

  "bay_ask_fish": {
    "conditions": ["!gave_fish"],
    "speaker": "Ông Bảy",
    "lines": [
      "Ta giữ chìa khóa cổng hầm.",
      "Nhưng bụng ta lép kẹp. Mang cho ta một con cá nục, ta đưa chìa."
    ],
    "next": ""
  },

  "bay_give_fish": {
    "conditions": ["has_fish", "!gave_fish"],
    "speaker": "Ông Bảy",
    "lines": ["Cá nục! Cháu ngoan."],
    "choices": [
      {
        "text": "Đưa cá cho ông Bảy",
        "require_item": "fish",
        "consume_item": "fish",
        "give_item": "rusty_key",
        "set_flags": ["gave_fish", "has_rusty_key"],
        "next": "bay_after_fish"
      },
      { "text": "Thôi, để lát nữa", "next": "" }
    ]
  },

  "bay_after_fish": {
    "speaker": "Ông Bảy",
    "lines": [
      "Cổng ở phía bắc làng. Chìa hơi rỉ, xoay mạnh tay.",
      "Trong hầm tối. Cẩn thận cái bệ đá ở phòng thứ hai."
    ],
    "next": ""
  },

  "bay_default": {
    "conditions": ["gave_fish"],
    "speaker": "Ông Bảy",
    "lines": ["Đi đi cháu. Trời sắp sáng."],
    "next": ""
  }
}
```

Cấu trúc mỗi node:

| Khóa | Ý nghĩa |
|---|---|
| `conditions` | Mảng flag phải thỏa (tiền tố `!` = phải không có). Rỗng = luôn thỏa |
| `speaker` | Tên hiện ở hộp tên |
| `portrait` | Đường dẫn ảnh chân dung (tùy chọn) |
| `lines` | Mảng câu, mỗi câu 1 lần bấm |
| `choices` | Mảng lựa chọn. Nếu có, hiện menu chọn sau khi hết `lines` |
| `set_flags` | Flag được set khi node này chạy xong |
| `give_item` / `consume_item` / `require_item` | Tác động inventory |
| `next` | id node tiếp theo. `""` = kết thúc thoại |

### 6.3.2 Cây scene hộp thoại

`scenes/ui/dialogue_box.tscn`:

```
DialogueBox (Control)                    ← scripts/ui/dialogue_box.gd
│   anchors: bottom-wide, offset_top = -70
│   visible = false
│   mouse_filter = Ignore (cho phần Control ngoài)
├── Panel (NinePatchRect)                ← khung viền 8-bit
│   texture = art/ui/dialog_frame.png
│   patch_margin_left/top/right/bottom = 8
│   texture_filter = Nearest (trên CanvasItem)
├── Portrait (TextureRect)               ← 48x48, bên trái, expand_mode Keep Size
├── SpeakerLabel (Label)                 ← font pixel, trên khung
├── Text (RichTextLabel)
│   bbcode_enabled = true
│   fit_content = false
│   scroll_active = false
├── NextArrow (TextureRect)              ← mũi tên "bấm tiếp", nhấp nháy
└── Choices (VBoxContainer)              ← các Button lựa chọn, visible = false
```

Về font: dùng **bitmap font pixel** (`.ttf` pixel như `m5x7`, `Determination Mono`, hoặc `BitmapFont` tự làm). Với font `.ttf` pixel, trong Inspector của font resource: bật `Antialiasing = None`, `Hinting = None`, `Subpixel Positioning = Disabled`, và đặt `font_size` là **đúng bội số** kích thước gốc của font (ví dụ font thiết kế cho 8px → dùng 8, 16, 24). Sai bước này chữ sẽ mờ/lệch.

### 6.3.3 Script hội thoại (đầy đủ)

```gdscript
# scripts/autoload/dialogue.gd
extends Node

signal dialogue_started
signal dialogue_finished

## UI được DialogueBox tự đăng ký khi _ready.
var _ui: Node = null
var _running: bool = false

func register_ui(ui: Node) -> void:
	_ui = ui

func is_running() -> bool:
	return _running


## Điểm vào chính. Gọi: await Dialogue.start("res://data/dialogs/npc_bay.json")
func start(json_path: String, entry_id: String = "") -> void:
	if _running:
		return
	if _ui == null:
		push_error("Dialogue: chưa có UI đăng ký")
		return

	var graph := _load_graph(json_path)
	if graph.is_empty():
		return

	_running = true
	GameState.push_input_lock()
	dialogue_started.emit()

	# Nếu không chỉ định entry, chọn node đầu tiên thỏa điều kiện.
	var node_id := entry_id if entry_id != "" else _pick_entry(graph)

	while node_id != "" and graph.has(node_id):
		node_id = await _run_node(graph, node_id)

	_ui.hide_box()
	_running = false
	GameState.pop_input_lock()
	dialogue_finished.emit()


func _load_graph(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("Dialogue: không thấy file %s" % path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(text)
	if parsed is not Dictionary:
		push_error("Dialogue: JSON sai định dạng ở %s" % path)
		return {}
	return parsed


## Chọn node vào: ưu tiên node có nhiều condition nhất mà vẫn thỏa
## -> node đặc thù ("bay_give_fish") thắng node chung ("bay_default").
func _pick_entry(graph: Dictionary) -> String:
	var best_id := ""
	var best_specificity := -1
	for id in graph.keys():
		var node: Dictionary = graph[id]
		var conds: Array = node.get("conditions", [])
		if not GameState.has_all_flags(conds):
			continue
		if conds.size() > best_specificity:
			best_specificity = conds.size()
			best_id = String(id)
	return best_id


## Chạy 1 node, trả về id node tiếp theo ("" = hết).
func _run_node(graph: Dictionary, node_id: String) -> String:
	var node: Dictionary = graph[node_id]

	_ui.set_speaker(String(node.get("speaker", "")))
	_ui.set_portrait(String(node.get("portrait", "")))
	_ui.show_box()

	# Hiện từng câu, chờ người chơi bấm.
	for line in node.get("lines", []):
		await _ui.show_line(String(line))

	# Áp dụng hiệu ứng của node.
	_apply_effects(node)

	# Nếu có choices -> hiện menu và chờ chọn.
	var choices: Array = node.get("choices", [])
	if not choices.is_empty():
		var available := _filter_choices(choices)
		if available.is_empty():
			return String(node.get("next", ""))
		var picked_index: int = await _ui.show_choices(available)
		var chosen: Dictionary = available[picked_index]
		_apply_effects(chosen)
		return String(chosen.get("next", ""))

	return String(node.get("next", ""))


## Bỏ lựa chọn mà người chơi chưa đủ điều kiện (thiếu item / thiếu flag).
func _filter_choices(choices: Array) -> Array:
	var out: Array = []
	for c in choices:
		var choice: Dictionary = c
		var req_item := String(choice.get("require_item", ""))
		if req_item != "" and not GameState.has_item(req_item):
			continue
		if not GameState.has_all_flags(choice.get("conditions", [])):
			continue
		out.append(choice)
	return out


## Dùng chung cho node và choice: set flag, cho/lấy item.
func _apply_effects(data: Dictionary) -> void:
	for f in data.get("set_flags", []):
		GameState.set_flag(String(f), true)
	for f in data.get("clear_flags", []):
		GameState.set_flag(String(f), false)

	var consume := String(data.get("consume_item", ""))
	if consume != "":
		GameState.remove_item(consume, int(data.get("consume_amount", 1)))

	var give := String(data.get("give_item", ""))
	if give != "":
		GameState.add_item(give, int(data.get("give_amount", 1)))

	var sfx := String(data.get("sfx", ""))
	if sfx != "":
		Audio.play_sfx_by_name(sfx)
```

### 6.3.4 Script UI hộp thoại (typewriter + choices)

```gdscript
# scripts/ui/dialogue_box.gd
extends Control

## Số ký tự hiện mỗi giây.
@export var chars_per_second: float = 40.0

@onready var panel: NinePatchRect = $Panel
@onready var text_label: RichTextLabel = $Text
@onready var speaker_label: Label = $SpeakerLabel
@onready var portrait: TextureRect = $Portrait
@onready var next_arrow: TextureRect = $NextArrow
@onready var choices_box: VBoxContainer = $Choices

var _line_done := false


func _ready() -> void:
	visible = false
	Dialogue.register_ui(self)
	next_arrow.visible = false
	choices_box.visible = false


func show_box() -> void:
	visible = true


func hide_box() -> void:
	visible = false
	text_label.text = ""
	choices_box.visible = false


func set_speaker(speaker_name: String) -> void:
	speaker_label.text = speaker_name
	speaker_label.visible = speaker_name != ""


func set_portrait(path: String) -> void:
	if path == "" or not ResourceLoader.exists(path):
		portrait.visible = false
		portrait.texture = null
		return
	portrait.texture = load(path)
	portrait.visible = true


## Hiện 1 câu theo kiểu typewriter, chờ người chơi bấm mới trả về.
## Bấm giữa lúc đang chạy chữ -> hiện hết câu ngay (skip), bấm lần 2 mới sang câu sau.
func show_line(line: String) -> void:
	next_arrow.visible = false
	text_label.text = line
	text_label.visible_characters = 0
	_line_done = false

	var total := text_label.get_total_character_count()
	var shown := 0.0

	while shown < float(total):
		shown += chars_per_second * get_process_delta_time()
		text_label.visible_characters = int(shown)
		# Tiếng "tíc" mỗi vài ký tự -> cảm giác 8-bit.
		if int(shown) % 3 == 0:
			Audio.play_sfx_by_name("text_blip")
		if _consume_advance_press():
			break                          # skip: hiện hết câu
		await get_tree().process_frame

	text_label.visible_characters = -1     # -1 = hiện toàn bộ
	next_arrow.visible = true
	_line_done = true

	# Chờ bấm để sang câu tiếp.
	while true:
		if _consume_advance_press():
			break
		await get_tree().process_frame

	next_arrow.visible = false


## Đọc và "tiêu thụ" 1 lần bấm nút tiến.
func _consume_advance_press() -> bool:
	if Input.is_action_just_pressed("interact") or Input.is_action_just_pressed("ui_accept"):
		return true
	return false


## Hiện danh sách lựa chọn, trả về index đã chọn.
func show_choices(choices: Array) -> int:
	# Dọn button cũ.
	for child in choices_box.get_children():
		child.queue_free()

	var result := {"index": -1}

	for i in choices.size():
		var choice: Dictionary = choices[i]
		var btn := Button.new()
		btn.text = String(choice.get("text", "..."))
		btn.focus_mode = Control.FOCUS_ALL
		# Bind index để biết nút nào được bấm.
		btn.pressed.connect(func() -> void:
			result["index"] = i
		)
		choices_box.add_child(btn)

	choices_box.visible = true
	next_arrow.visible = false

	# Focus nút đầu để chơi được bằng bàn phím/gamepad.
	if choices_box.get_child_count() > 0:
		(choices_box.get_child(0) as Button).grab_focus()

	while result["index"] < 0:
		await get_tree().process_frame

	choices_box.visible = false
	Audio.play_sfx_by_name("menu_confirm")
	return int(result["index"])
```

> **Ghi chú kỹ thuật**: đọc `Input.is_action_just_pressed` trong vòng lặp `await process_frame` hoạt động vì mỗi lần `await` là qua 1 frame mới. Cách "sạch" hơn là dùng signal + `await`, nhưng bản này dễ đọc cho người mới và chạy đúng. Nếu bạn thấy bấm 1 lần mà nhảy 2 câu → do cả `interact` và `ui_accept` map cùng phím Space/Enter; bỏ 1 trong 2 khỏi điều kiện.

---

## 6.4 Interactable: NPC, item, cửa

### 6.4.1 NPC

```gdscript
# scripts/actors/npc.gd
class_name NPC
extends Interactable

@export var npc_name: String = "NPC"
@export_file("*.json") var dialog_file: String = ""

## Nếu set, NPC chỉ tương tác được khi thỏa các flag này.
@export var required_flags: Array[String] = []

@onready var sprite: AnimatedSprite3D = $Visual/Sprite


func _ready() -> void:
	super._ready()
	prompt_text = "Nói chuyện"
	if sprite and sprite.sprite_frames and sprite.sprite_frames.has_animation("idle_down"):
		sprite.play("idle_down")


func interact(by: Node3D) -> void:
	if not GameState.has_all_flags(required_flags):
		return
	if dialog_file == "":
		push_warning("NPC %s chưa gán dialog_file" % npc_name)
		return
	_face_player(by)
	await Dialogue.start(dialog_file)
	interacted.emit(by)


## Cho NPC "quay mặt" về phía người chơi — chi tiết nhỏ nhưng nâng cảm giác nhiều.
func _face_player(by: Node3D) -> void:
	if sprite == null or sprite.sprite_frames == null:
		return
	var to_player := by.global_position - global_position
	var anim := "idle_down"
	if absf(to_player.x) > absf(to_player.z):
		anim = "idle_side"
		sprite.flip_h = to_player.x < 0.0
	else:
		anim = "idle_down" if to_player.z > 0.0 else "idle_up"
	if sprite.sprite_frames.has_animation(anim):
		sprite.play(anim)
```

Cây scene `scenes/actors/npc.tscn`:

```
NPC (Area3D)                          ← npc.gd, collision_layer = 4
├── CollisionShape3D                  CylinderShape3D r=0.6 h=2
├── Visual (Node3D)
│   └── Sprite (AnimatedSprite3D)     billboard Fixed Y, alpha_cut Discard
├── Shadow (Sprite3D)
└── Exclamation (Sprite3D)            ← dấu "!" nhấp nhô trên đầu khi có việc mới
    visible = false
```

### 6.4.2 Item pickup

```gdscript
# scripts/props/item_pickup.gd
class_name ItemPickup
extends Interactable

@export var item: ItemData
@export var amount: int = 1

## Flag được set khi nhặt — để item không hồi sinh sau khi load lại level.
@export var pickup_flag: String = ""

## Câu hiện ra khi nhặt. Để trống -> tự sinh "Nhận được X".
@export var pickup_message: String = ""

@onready var sprite: Sprite3D = $Sprite


func _ready() -> void:
	super._ready()
	prompt_text = "Nhặt"
	# Nếu đã nhặt rồi (theo flag) thì tự xóa mình khi level load.
	if pickup_flag != "" and GameState.has_flag(pickup_flag):
		queue_free()
		return
	_start_bob()


## Nhấp nhô nhẹ cho item dễ thấy.
func _start_bob() -> void:
	if sprite == null:
		return
	var base_y := sprite.position.y
	var tw := create_tween().set_loops()
	tw.tween_property(sprite, "position:y", base_y + 0.12, 0.7) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(sprite, "position:y", base_y, 0.7) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func interact(by: Node3D) -> void:
	if item == null:
		push_warning("ItemPickup ở %s chưa gán item" % get_path())
		return

	GameState.add_item(item.id, amount)
	if pickup_flag != "":
		GameState.set_flag(pickup_flag, true)

	Audio.play_sfx_by_name("pickup")

	var msg := pickup_message
	if msg == "":
		msg = "Nhận được [b]%s[/b]%s." % [
			item.display_name,
			(" x%d" % amount) if amount > 1 else ""
		]
	await HUD.show_toast(msg)

	interacted.emit(by)
	queue_free()
```

### 6.4.3 Cổng khóa

```gdscript
# scripts/props/locked_gate.gd
class_name LockedGate
extends Interactable

## Item cần để mở. Để trống -> chỉ cần flag.
@export var required_item_id: String = "rusty_key"

## Có tiêu thụ item khi mở không (chìa khóa thường giữ lại).
@export var consume_item: bool = false

## Flag đánh dấu cổng đã mở — để load lại level cổng vẫn mở.
@export var open_flag: String = "gate_open"

@export var locked_message: String = "Cổng bị khóa. Có ổ khóa rỉ nặng."
@export var unlock_message: String = "Chìa khóa vừa khít. Cổng mở ra."

@onready var body: StaticBody3D = $Body
@onready var sprite: Sprite3D = $Sprite
@onready var anim: AnimationPlayer = $AnimationPlayer


func _ready() -> void:
	super._ready()
	prompt_text = "Mở cổng"
	if GameState.has_flag(open_flag):
		_set_open(true, false)     # đã mở từ trước -> mở ngay, không animation


func interact(_by: Node3D) -> void:
	if GameState.has_flag(open_flag):
		return

	if required_item_id != "" and not GameState.has_item(required_item_id):
		await HUD.show_toast(locked_message)
		Audio.play_sfx_by_name("locked")
		return

	if consume_item and required_item_id != "":
		GameState.remove_item(required_item_id)

	GameState.set_flag(open_flag, true)
	await HUD.show_toast(unlock_message)
	Audio.play_sfx_by_name("gate_open")
	_set_open(true, true)


func _set_open(is_open: bool, play_anim: bool) -> void:
	# Tắt collision -> đi qua được.
	body.collision_layer = 0 if is_open else 4
	# Tắt tương tác -> không hiện prompt "Mở cổng" nữa.
	set_active(not is_open)

	if play_anim and anim and anim.has_animation("open"):
		anim.play("open")
	else:
		sprite.visible = not is_open
```

Cây scene `scenes/props/locked_gate.tscn`:

```
LockedGate (Area3D)                   ← locked_gate.gd, collision_layer = 4
├── CollisionShape3D                  BoxShape3D (3, 2, 1.5)  ← vùng tương tác (rộng hơn cổng)
├── Body (StaticBody3D)               collision_layer = 4     ← vật cản thật
│   └── CollisionShape3D              BoxShape3D (3, 4, 0.4)
├── Sprite (Sprite3D)                 texture gate_48x64.png
└── AnimationPlayer
    animation "open": Sprite:modulate:a 1 → 0, Sprite:position:y 0 → 0.5 (0.5s)
```

---

## 6.5 Trigger vùng (Area3D)

Vùng vô hình gây sự kiện khi player bước vào: chuyển màn, cutscene, hiện gợi ý, autosave.

```gdscript
# scripts/systems/area_trigger.gd
class_name AreaTrigger
extends Area3D

enum TriggerAction {
	SET_FLAG,        # chỉ set flag
	SHOW_TOAST,      # hiện chữ
	START_DIALOG,    # chạy hội thoại (cutscene nhẹ)
	CHANGE_LEVEL,    # chuyển màn
	AUTOSAVE,
}

@export var action: TriggerAction = TriggerAction.SET_FLAG

## Điều kiện để trigger hoạt động.
@export var required_flags: Array[String] = []

## Chỉ chạy 1 lần? (Dùng kèm once_flag để nhớ qua save.)
@export var once: bool = true
@export var once_flag: String = ""

## Tham số cho từng action.
@export var flag_to_set: String = ""
@export var toast_text: String = ""
@export_file("*.json") var dialog_file: String = ""
@export_file("*.tscn") var target_level: String = ""
@export var target_spawn: String = "spawn_default"

var _fired := false


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2                     # chỉ dò player (bit 2)
	monitoring = true
	body_entered.connect(_on_body_entered)
	if once and once_flag != "" and GameState.has_flag(once_flag):
		_fired = true


func _on_body_entered(body: Node3D) -> void:
	if _fired:
		return
	if not body.is_in_group("player"):
		return
	if not GameState.has_all_flags(required_flags):
		return

	if once:
		_fired = true
		if once_flag != "":
			GameState.set_flag(once_flag, true)

	match action:
		TriggerAction.SET_FLAG:
			if flag_to_set != "":
				GameState.set_flag(flag_to_set, true)

		TriggerAction.SHOW_TOAST:
			await HUD.show_toast(toast_text)

		TriggerAction.START_DIALOG:
			if dialog_file != "":
				await Dialogue.start(dialog_file)

		TriggerAction.CHANGE_LEVEL:
			if target_level != "":
				SceneRouter.goto_level(target_level, target_spawn)

		TriggerAction.AUTOSAVE:
			SaveSystem.save_game(0)        # slot 0 = autosave
			await HUD.show_toast("Đã lưu.")
```

> `body_entered` chỉ bắn khi `monitoring = true` và **mask** của Area3D chứa **layer** của body. Đây là nguyên nhân số 1 của "trigger không chạy". Kiểm tra: Area3D mask phải chứa bit của player layer.

### Save point

```gdscript
# scripts/props/save_point.gd
class_name SavePoint
extends Interactable

@export var slot: int = 1

func _ready() -> void:
	super._ready()
	prompt_text = "Lưu game"

func interact(_by: Node3D) -> void:
	await Dialogue.start("res://data/dialogs/save_point.json")
	if GameState.has_flag("_save_confirmed"):
		GameState.set_flag("_save_confirmed", false)   # flag tạm, dọn ngay
		SaveSystem.save_game(slot)
		Audio.play_sfx_by_name("save")
		await HUD.show_toast("Đã lưu tiến trình.")
```

`data/dialogs/save_point.json`:

```json
{
  "ask": {
    "speaker": "",
    "lines": ["Một ngọn lửa nhỏ cháy trong hốc đá. Nơi này an toàn."],
    "choices": [
      { "text": "Lưu game", "set_flags": ["_save_confirmed"], "next": "" },
      { "text": "Đi tiếp", "next": "" }
    ]
  }
}
```

> Mẹo: flag bắt đầu bằng `_` là **flag tạm**, dùng để truyền tín hiệu từ dialog về code. Đặt quy ước này và **lọc chúng ra khi save** để file save sạch.

---

## 6.6 Inventory UI

```
InventoryUI (Control)                    ← scripts/ui/inventory_ui.gd
│   visible = false, anchors full rect
├── Dim (ColorRect)                      color #000000aa
├── Panel (NinePatchRect)
│   ├── Title (Label)                    "TÚI ĐỒ"
│   ├── Grid (GridContainer)             columns = 5
│   │   └── (ItemSlot được sinh runtime)
│   └── Detail (VBoxContainer)
│       ├── DetailName (Label)
│       ├── DetailDesc (RichTextLabel)
│       └── UseButton (Button)
```

`scenes/ui/item_slot.tscn`:

```
ItemSlot (Button)                        ← 20x20, custom_minimum_size
├── Icon (TextureRect)                   16x16, stretch Keep, filter Nearest
└── Count (Label)                        góc dưới phải, font nhỏ
```

```gdscript
# scripts/ui/inventory_ui.gd
extends Control

const SLOT_SCENE := preload("res://scenes/ui/item_slot.tscn")
const MIN_SLOTS := 20                     # luôn hiện đủ ô trống cho gọn mắt

@onready var grid: GridContainer = $Panel/Grid
@onready var detail_name: Label = $Panel/Detail/DetailName
@onready var detail_desc: RichTextLabel = $Panel/Detail/DetailDesc
@onready var use_button: Button = $Panel/Detail/UseButton

var _selected_id: String = ""


func _ready() -> void:
	visible = false
	GameState.inventory_changed.connect(_refresh)
	use_button.pressed.connect(_on_use_pressed)
	_clear_detail()


func _unhandled_input(event: InputEvent) -> void:
	# Không mở túi khi đang thoại.
	if event.is_action_pressed("inventory"):
		if Dialogue.is_running():
			return
		toggle()
		get_viewport().set_input_as_handled()
	elif visible and event.is_action_pressed("cancel"):
		close()
		get_viewport().set_input_as_handled()


func toggle() -> void:
	if visible:
		close()
	else:
		open()


func open() -> void:
	_refresh()
	visible = true
	GameState.push_input_lock()
	# Focus ô đầu để chơi được bằng gamepad.
	for child in grid.get_children():
		if child is Button and (child as Button).disabled == false:
			(child as Button).grab_focus()
			break


func close() -> void:
	visible = false
	_clear_detail()
	GameState.pop_input_lock()


func _refresh() -> void:
	for child in grid.get_children():
		child.queue_free()

	var ids := GameState.inventory.keys()
	ids.sort()                            # thứ tự ổn định, không nhảy loạn

	for id in ids:
		var item := ItemDB.get_item(String(id))
		var slot := SLOT_SCENE.instantiate()
		grid.add_child(slot)
		var count: int = GameState.get_item_count(String(id))

		if item:
			(slot.get_node("Icon") as TextureRect).texture = item.icon
			slot.tooltip_text = item.display_name
		var count_label := slot.get_node("Count") as Label
		count_label.text = str(count) if count > 1 else ""

		slot.pressed.connect(_on_slot_pressed.bind(String(id)))

	# Ô trống cho đủ lưới.
	for i in maxi(0, MIN_SLOTS - ids.size()):
		var empty := SLOT_SCENE.instantiate()
		grid.add_child(empty)
		(empty as Button).disabled = true


func _on_slot_pressed(item_id: String) -> void:
	_selected_id = item_id
	var item := ItemDB.get_item(item_id)
	if item == null:
		_clear_detail()
		return
	detail_name.text = item.display_name
	detail_desc.text = item.description
	use_button.visible = item.usable
	Audio.play_sfx_by_name("menu_move")


func _clear_detail() -> void:
	_selected_id = ""
	detail_name.text = ""
	detail_desc.text = ""
	use_button.visible = false


func _on_use_pressed() -> void:
	if _selected_id == "":
		return
	var item := ItemDB.get_item(_selected_id)
	if item == null or not item.usable:
		return
	# Ví dụ: đèn dầu -> set flag để world biết bật sáng.
	match _selected_id:
		"lantern":
			GameState.set_flag("lantern_on", not GameState.has_flag("lantern_on"))
			await HUD.show_toast(
				"Đèn sáng lên." if GameState.has_flag("lantern_on") else "Đèn tắt."
			)
		_:
			await HUD.show_toast("Chưa dùng được ở đây.")
	close()
```

---

## 6.7 Save / Load

### So sánh 3 cách lưu

| Cách | Ưu | Nhược | Khi nào |
|---|---|---|---|
| **`ConfigFile`** | Đơn giản, dạng INI dễ đọc/sửa tay | Kém với dữ liệu lồng nhau | Settings (âm lượng, phím), không phải save game |
| **JSON (`FileAccess` + `JSON`)** | Dễ debug (mở bằng text editor), portable, dễ nhờ AI xử lý, không rủi ro code execution | Phải tự convert type (Vector3 → array), mất type chặt | ✅ **Save game của ta** |
| **`Resource` + `ResourceSaver`** | Giữ nguyên type Godot (Vector3, Texture), tiện nhất | ⚠️ Load `.tres` từ file người dùng có thể thực thi code → **rủi ro bảo mật với save chia sẻ**. Đổi cấu trúc resource dễ làm save cũ vỡ | Dữ liệu nội bộ (item, dialog), không dùng cho save file |

> **Rủi ro bảo mật của `Resource` save**: file `.tres`/`.res` có thể chứa tham chiếu script. Nếu người chơi tải save của người khác về, load nó có thể chạy code. Nếu bạn vẫn muốn dùng Resource, hãy dùng `ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE)` với cờ an toàn phù hợp và **kiểm tra tài liệu bản Godot bạn dùng** về tham số bỏ qua script. Cách đơn giản và an toàn: **dùng JSON**.

### `save_system.gd`

```gdscript
# scripts/autoload/save_system.gd
extends Node

const SAVE_DIR := "user://saves/"
const SAVE_VERSION := 1

signal save_completed(slot: int)
signal load_completed(slot: int)


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(SAVE_DIR)


func _slot_path(slot: int) -> String:
	return "%ssave_%d.json" % [SAVE_DIR, slot]


func has_save(slot: int) -> bool:
	return FileAccess.file_exists(_slot_path(slot))


## Ghi state hiện tại ra file. slot 0 = autosave.
func save_game(slot: int) -> bool:
	var state := GameState.to_dict()

	# Lọc flag tạm (tiền tố "_") để file save sạch và không tái hiện tín hiệu cũ.
	var clean_flags: Dictionary = {}
	for k in state["flags"].keys():
		if not String(k).begins_with("_"):
			clean_flags[k] = state["flags"][k]
	state["flags"] = clean_flags

	var payload := {
		"version": SAVE_VERSION,
		"saved_at": Time.get_datetime_string_from_system(true),
		"state": state,
	}

	var f := FileAccess.open(_slot_path(slot), FileAccess.WRITE)
	if f == null:
		push_error("Không ghi được save slot %d: %s" % [slot, FileAccess.get_open_error()])
		return false
	# "\t" = pretty print, dễ đọc khi debug. Đổi thành "" cho file nhỏ hơn.
	f.store_string(JSON.stringify(payload, "\t"))
	f.close()

	save_completed.emit(slot)
	return true


## Đọc file save và áp vào GameState + chuyển tới level đã lưu.
func load_game(slot: int) -> bool:
	var path := _slot_path(slot)
	if not FileAccess.file_exists(path):
		push_warning("Không có save ở slot %d" % slot)
		return false

	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Không đọc được save slot %d" % slot)
		return false
	var text := f.get_as_text()
	f.close()

	var parsed: Variant = JSON.parse_string(text)
	if parsed is not Dictionary:
		push_error("Save slot %d hỏng (JSON sai)" % slot)
		return false

	var payload: Dictionary = parsed
	var version := int(payload.get("version", 0))
	if version != SAVE_VERSION:
		payload = _migrate(payload, version)
		if payload.is_empty():
			push_error("Save version %d không tương thích" % version)
			return false

	var state: Dictionary = payload.get("state", {})
	GameState.from_dict(state)

	var level: String = GameState.current_level_path
	if level == "" or not ResourceLoader.exists(level):
		push_error("Save trỏ tới level không tồn tại: %s" % level)
		return false

	SceneRouter.goto_level(level, GameState.current_spawn)
	load_completed.emit(slot)
	return true


## Nâng cấp save cũ. Viết từng bước version -> version+1.
func _migrate(payload: Dictionary, from_version: int) -> Dictionary:
	# Ví dụ khi bạn lên SAVE_VERSION = 2:
	# if from_version == 1:
	#     payload["state"]["new_field"] = default_value
	#     from_version = 2
	if from_version == SAVE_VERSION:
		return payload
	return {}     # không migrate được -> trả rỗng để caller báo lỗi


## Metadata để hiển thị ở menu chọn slot (không load game).
func get_slot_info(slot: int) -> Dictionary:
	if not has_save(slot):
		return {}
	var f := FileAccess.open(_slot_path(slot), FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is not Dictionary:
		return {}
	var state: Dictionary = parsed.get("state", {})
	var seconds := int(state.get("playtime", 0.0))
	return {
		"saved_at": parsed.get("saved_at", ""),
		"level": state.get("level", ""),
		"playtime_text": "%02d:%02d" % [seconds / 3600, (seconds % 3600) / 60],
		"item_count": (state.get("inventory", {}) as Dictionary).size(),
	}


func delete_save(slot: int) -> void:
	if has_save(slot):
		DirAccess.remove_absolute(_slot_path(slot))
```

Đường dẫn `user://` thật nằm ở:

| OS | Đường dẫn |
|---|---|
| Windows | `%APPDATA%\Godot\app_userdata\<tên project>\` |
| macOS | `~/Library/Application Support/Godot/app_userdata/<tên project>/` |
| Linux | `~/.local/share/godot/app_userdata/<tên project>/` |
| Web | IndexedDB của browser (không thấy file thật) |

Mở nhanh trong editor: `Project → Open User Data Folder`.

### Điều gì KHÔNG được lưu (quan trọng)

Hệ thống trên chỉ lưu `flags` + `inventory` + `level` + `spawn`. Nó **không** lưu:

- Vị trí chính xác của player trong level (chỉ lưu spawn point)
- Vị trí thùng gỗ đã đẩy
- Cửa nào đã mở (trừ khi bạn dùng flag)
- HP, thời gian trong ngày

**Đây là lựa chọn có ý thức, không phải thiếu sót.** Save-tại-điểm (save point) rồi respawn ở đó là mô hình của phần lớn game 8-bit/JRPG — nó đơn giản hơn nhiều so với "lưu toàn bộ world state" và ít bug hơn hẳn.

Nếu bạn cần lưu chi tiết hơn, mẫu mở rộng: mỗi node cần lưu implement 2 hàm và tự đăng ký:

```gdscript
# Interface: node nào cần lưu thì có 2 hàm này + ở group "persist"
func save_data() -> Dictionary:
	return {"pos": [global_position.x, global_position.y, global_position.z]}

func load_data(d: Dictionary) -> void:
	var p: Array = d.get("pos", [0, 0, 0])
	global_position = Vector3(p[0], p[1], p[2])
```

Rồi trong `save_game()`: quét `get_tree().get_nodes_in_group("persist")`, lưu theo `get_path()` làm khóa. **Chỉ làm cái này khi thật cần** — nó sinh ra cả một lớp bug mới (node path đổi, node không tồn tại khi load...).

---

## 6.8 Chuyển màn giữ nguyên state

```gdscript
# scripts/autoload/scene_router.gd
extends Node

signal level_loaded(level: Node)

const FADE_TIME := 0.3

var _world_holder: Node3D = null
var _fade_rect: ColorRect = null
var _current_level: Node = null
var _busy := false


func register_world_holder(holder: Node3D) -> void:
	_world_holder = holder


func register_fade_rect(rect: ColorRect) -> void:
	_fade_rect = rect
	_fade_rect.color = Color(0, 0, 0, 0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE


## Điểm vào chính. Chuyển tới level, đặt player ở spawn_name.
func goto_level(level_path: String, spawn_name: String = "spawn_default") -> void:
	if _busy:
		return
	if _world_holder == null:
		push_error("SceneRouter: chưa register_world_holder")
		return
	if not ResourceLoader.exists(level_path):
		push_error("SceneRouter: không tồn tại level %s" % level_path)
		return

	_busy = true
	GameState.push_input_lock()

	await _fade(1.0)

	# Xóa level cũ. free() ngay (không queue_free) để tránh 2 level cùng tồn tại
	# trong 1 frame -> tránh 2 player, 2 camera, signal bắn 2 lần.
	if _current_level != null and is_instance_valid(_current_level):
		_world_holder.remove_child(_current_level)
		_current_level.free()
		_current_level = null

	# Load + instantiate level mới.
	var packed: PackedScene = load(level_path)
	var level := packed.instantiate()
	_world_holder.add_child(level)
	_current_level = level

	# Ghi lại vị trí hiện tại vào GameState -> save biết chỗ nào.
	GameState.current_level_path = level_path
	GameState.current_spawn = spawn_name

	# Đợi 1 frame để _ready của mọi node trong level chạy xong.
	await get_tree().process_frame

	_place_player(level, spawn_name)

	level_loaded.emit(level)

	await _fade(0.0)
	GameState.pop_input_lock()
	_busy = false


## Đặt player vào spawn point tương ứng.
func _place_player(level: Node, spawn_name: String) -> void:
	var players := get_tree().get_nodes_in_group("player")
	if players.is_empty():
		push_warning("Level %s không có node trong group 'player'" % level.name)
		return
	var player: Node3D = players[0]

	var marker: Marker3D = null
	if level.has_method("get_spawn_point"):
		marker = level.get_spawn_point(spawn_name)

	if marker:
		player.global_position = marker.global_position
		# Nếu marker quay hướng nào, cho player nhìn hướng đó.
		if player is CharacterBody3D:
			(player as CharacterBody3D).velocity = Vector3.ZERO
	else:
		push_warning("Không tìm được spawn '%s' trong %s" % [spawn_name, level.name])


## Fade màn hình. target_alpha 1 = đen kín, 0 = trong suốt.
func _fade(target_alpha: float) -> void:
	if _fade_rect == null:
		return
	var tw := create_tween()
	tw.tween_property(_fade_rect, "color:a", target_alpha, FADE_TIME)
	await tw.finished
```

### Vì sao player nằm TRONG level, không phải trong `Main`?

Hai kiến trúc:

| Kiến trúc | Player ở đâu | Ưu | Nhược |
|---|---|---|---|
| **A. Player trong mỗi level** | Mỗi `.tscn` level có 1 instance `player.tscn` | Dựng/test level độc lập được (F6 chạy riêng level), dễ hiểu | Player bị xóa/tạo lại mỗi lần đổi màn → mọi state của player phải ở `GameState` |
| **B. Player trong `Main`, sống mãi** | 1 player duy nhất, level được swap dưới chân | Player giữ nguyên state, không cần re-init | Không chạy riêng level được; phải cẩn thận reset vị trí/velocity |

Code ở trên viết theo **A** (tìm player trong group sau khi load level). Đây là lựa chọn tốt cho người mới: **bạn có thể mở `dungeon_01.tscn` và bấm F6 để test ngay phòng đó** — cực kỳ tiết kiệm thời gian khi làm puzzle.

Điều kiện để A hoạt động: **mọi thứ cần giữ qua màn phải nằm trong `GameState`**, không nằm trong player. Code chương 04 đã tuân thủ điều này.

### `main.tscn` hoàn chỉnh

```
Main (Node)                              ← scripts/main.gd
├── WorldHolder (Node3D)
└── UILayer (CanvasLayer)                 layer = 10
    ├── HUD (instance hud.tscn)
    ├── DialogueBox (instance dialogue_box.tscn)
    ├── InventoryUI (instance inventory_ui.tscn)
    └── FadeRect (ColorRect)              anchors full, color #00000000, mouse_filter Ignore
```

```gdscript
# scripts/main.gd
extends Node

const FIRST_LEVEL := "res://scenes/levels/town.tscn"

@onready var world_holder: Node3D = $WorldHolder
@onready var fade_rect: ColorRect = $UILayer/FadeRect

func _ready() -> void:
	SceneRouter.register_world_holder(world_holder)
	SceneRouter.register_fade_rect(fade_rect)

	# Nếu có autosave -> hỏi tiếp tục; ở MVP thì cứ vào game mới.
	GameState.reset()
	SceneRouter.goto_level(FIRST_LEVEL, "spawn_default")
```

### Portal (cửa vào/ra giữa 2 màn)

```gdscript
# scripts/props/level_portal.gd
class_name LevelPortal
extends Area3D

@export_file("*.tscn") var target_level: String = ""
@export var target_spawn: String = "spawn_default"

## Cần flag gì mới đi qua được (ví dụ "gate_open").
@export var required_flags: Array[String] = []
@export var blocked_message: String = "Đường này chưa đi được."

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node3D) -> void:
	if not body.is_in_group("player"):
		return
	if not GameState.has_all_flags(required_flags):
		await HUD.show_toast(blocked_message)
		return
	SceneRouter.goto_level(target_level, target_spawn)
```

Cặp portal cho game mẫu:

| Portal | Ở level | target_level | target_spawn | required_flags |
|---|---|---|---|---|
| `ToDungeon` | town | `dungeon_01.tscn` | `spawn_from_town` | `["gate_open"]` |
| `ToTown` | dungeon_01 | `town.tscn` | `spawn_from_dungeon` | `[]` |
| `ToTop` | dungeon_01 | `lighthouse_top.tscn` | `spawn_default` | `["torch_puzzle_done"]` |

---

## 6.9 HUD: prompt + toast + tiêu đề khu vực

```gdscript
# scripts/ui/hud.gd  (autoload cả scene: scenes/ui/hud.tscn)
extends CanvasLayer

@onready var prompt: Control = $Prompt
@onready var prompt_label: Label = $Prompt/Label
@onready var toast: Control = $Toast
@onready var toast_label: RichTextLabel = $Toast/Label
@onready var area_title: Label = $AreaTitle

var _prompt_world_pos: Vector3 = Vector3.ZERO
var _prompt_active := false


func _ready() -> void:
	prompt.visible = false
	toast.visible = false
	area_title.visible = false


func _process(_delta: float) -> void:
	if not _prompt_active:
		return
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	# Vật ở sau camera -> ẩn prompt, nếu không nó hiện lộn chỗ.
	if cam.is_position_behind(_prompt_world_pos):
		prompt.visible = false
		return
	prompt.visible = true
	prompt.position = cam.unproject_position(_prompt_world_pos) - prompt.size * 0.5


func show_prompt(text: String, world_pos: Vector3) -> void:
	prompt_label.text = "[E] " + text
	_prompt_world_pos = world_pos
	_prompt_active = true


func hide_prompt() -> void:
	_prompt_active = false
	prompt.visible = false


## Hiện dòng chữ tạm ở giữa dưới. await được để chờ nó xong.
func show_toast(text: String, duration: float = 1.8) -> void:
	toast_label.text = text
	toast.visible = true
	toast.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(toast, "modulate:a", 1.0, 0.15)
	tw.tween_interval(duration)
	tw.tween_property(toast, "modulate:a", 0.0, 0.3)
	await tw.finished
	toast.visible = false


## Tên khu vực hiện ra khi vào map mới (kiểu JRPG).
func show_area_title(text: String) -> void:
	area_title.text = text
	area_title.visible = true
	area_title.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(area_title, "modulate:a", 1.0, 0.4)
	tw.tween_interval(1.6)
	tw.tween_property(area_title, "modulate:a", 0.0, 0.6)
	await tw.finished
	area_title.visible = false
```

> `unproject_position` cho toạ độ trong **viewport logic** (320×180 nếu dùng stretch mode `viewport`). Nếu prompt hiện lệch chỗ, khả năng cao là bạn đang trộn 2 hệ toạ độ (SubViewport vs màn hình). Xem lại chương 01 mục 1.6.

---

## 6.10 Câu đố 3: thứ tự ba đuốc (state machine nhỏ)

```gdscript
# scripts/props/torch_puzzle.gd
# Gắn vào một Node3D cha chứa 3 đuốc.
extends Node3D

## Thứ tự đúng, theo TÊN node đuốc. Manh mối nằm ở bài hát bà Tám (màn 1).
@export var correct_order: Array[String] = ["TorchSea", "TorchMoon", "TorchStone"]

## Flag set khi giải xong.
@export var success_flag: String = "torch_puzzle_done"

## Cửa mở ra khi giải xong.
@export var door: Node3D

var _sequence: Array[String] = []


func _ready() -> void:
	if GameState.has_flag(success_flag):
		_open_door(false)
		return
	# Kết nối signal từ từng đuốc con.
	for child in get_children():
		if child is Torch:
			(child as Torch).lit.connect(_on_torch_lit.bind(child.name))


func _on_torch_lit(torch_name: String) -> void:
	_sequence.append(torch_name)

	# Kiểm tra từng bước: sai ngay lập tức thì reset (feedback nhanh, không chờ hết 3).
	var idx := _sequence.size() - 1
	if _sequence[idx] != correct_order[idx]:
		await _fail()
		return

	if _sequence.size() == correct_order.size():
		await _succeed()


func _fail() -> void:
	Audio.play_sfx_by_name("puzzle_fail")
	await HUD.show_toast("Ba ngọn đuốc phụt tắt cùng lúc.", 1.2)
	_sequence.clear()
	for child in get_children():
		if child is Torch:
			(child as Torch).extinguish()


func _succeed() -> void:
	GameState.set_flag(success_flag, true)
	Audio.play_sfx_by_name("puzzle_solved")
	await HUD.show_toast("Tiếng đá nghiến vang lên từ phía sau.", 2.0)
	_open_door(true)


func _open_door(animate: bool) -> void:
	if door == null:
		return
	if door.has_method("open"):
		door.open(animate)
	else:
		door.visible = false
```

```gdscript
# scripts/props/torch.gd
class_name Torch
extends Interactable

signal lit

@export var is_lit: bool = false

@onready var flame: Sprite3D = $Flame
@onready var light: OmniLight3D = $Light


func _ready() -> void:
	super._ready()
	prompt_text = "Thắp đuốc"
	_apply_visual()


func interact(_by: Node3D) -> void:
	if is_lit:
		return
	# Cần có đèn dầu để thắp — buộc người chơi tìm đèn trước.
	if not GameState.has_item("lantern"):
		await HUD.show_toast("Cần một nguồn lửa.")
		return
	is_lit = true
	_apply_visual()
	Audio.play_sfx_by_name("torch_light")
	lit.emit()


func extinguish() -> void:
	is_lit = false
	_apply_visual()


func _apply_visual() -> void:
	flame.visible = is_lit
	light.visible = is_lit
	prompt_text = "" if is_lit else "Thắp đuốc"
	set_active(not is_lit)
```

---

## 6.11 Thứ tự làm & test từng bước

| Bước | Làm gì | Test bằng cách |
|---|---|---|
| 1 | `GameState` autoload | Trong `_ready` của player: `GameState.set_flag("test")` rồi `print(GameState.has_flag("test"))` |
| 2 | `Interactable` + 1 Area3D in `print` | Nhấn E gần nó thấy log |
| 3 | `HUD.show_toast` | Nhấn E → thấy chữ |
| 4 | `DialogueBox` + `Dialogue` với 1 file JSON 2 dòng | Nói chuyện xong quay lại điều khiển được |
| 5 | `ItemData` + `ItemPickup` | Nhặt → toast → item biến mất |
| 6 | `InventoryUI` | Bấm I → thấy item vừa nhặt |
| 7 | `LockedGate` | Chưa có chìa → toast "khóa". Có chìa → mở |
| 8 | Dialog có `choices` + `give_item` | Đưa cá → nhận chìa |
| 9 | `SceneRouter` + 2 level + portal | Đi qua đi lại, inventory còn nguyên |
| 10 | `SaveSystem` | Save → thoát game → chạy lại → load → đúng level, đúng item |
| 11 | `torch_puzzle` | Bật sai thứ tự → reset. Đúng → cửa mở |

**Đừng nhảy bước.** Mỗi bước là 1 commit Git.

---

## 6.12 Bài tập

1. Làm xong bước 1–4 ở 6.11. Viết `npc_bay.json` đầy đủ như 6.3.1 và nói chuyện được với ông Bảy qua đủ 3 trạng thái (chưa gặp / chưa có cá / đã đưa cá).
2. Thêm ItemData cho cả 6 item ở 6.2. Đặt `fish.tres` vào một `ItemPickup` ở bến tàu.
3. Thêm `SavePoint` vào phòng 1 dungeon. Save, thoát, load → xác nhận về đúng dungeon với đúng item.
4. Thêm dấu `!` trên đầu NPC khi có việc mới: `Exclamation.visible = GameState.has_all_flags(["has_fish", "!gave_fish"])`, cập nhật khi `GameState.flag_changed` bắn.
5. Làm câu đố 2 (bệ trọng lượng): `Area3D` bệ, `body_entered` kiểm tra body là `PushableCrate` → set flag `crate_on_plate` → mở cửa. Xử lý cả `body_exited` (đẩy hộp ra thì cửa đóng lại).
6. Thêm menu chính: `scenes/ui/main_menu.tscn` với "Chơi mới" / "Tiếp tục" (dùng `SaveSystem.get_slot_info(0)` để hiện thời gian chơi) / "Thoát".
7. **Nâng cao**: viết một hàm debug `GameState.debug_dump()` in ra toàn bộ flags + inventory. Gán vào phím F3. Bạn sẽ dùng nó liên tục.

---

## 6.13 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `GameState` báo null | Chưa đăng ký autoload, hoặc gõ sai tên (phân biệt hoa/thường) | Project Settings → Globals, tên phải khớp chính xác |
| Autoload báo lỗi khi khởi động | Thứ tự autoload sai (`SceneRouter` load trước `GameState`) | Kéo `GameState` lên trên |
| Nhấn E mở thoại 2 lần | Cả `_input` và `_unhandled_input` xử lý, hoặc `interact`+`ui_accept` cùng phím | `set_input_as_handled()`; bỏ 1 action khỏi điều kiện |
| Thoại xong không điều khiển được | `pop_input_lock` không được gọi (lỗi giữa đường, `await` treo) | Kiểm tra mọi nhánh return đều pop lock; dùng `_lock_count` đếm để debug |
| Typewriter nhảy hết chữ ngay | `is_action_just_pressed` còn true từ lần bấm mở thoại | Chờ 1 frame trước khi vào vòng lặp, hoặc dùng flag "đã nhả nút" |
| Chữ pixel bị mờ | Font `.ttf` bật antialiasing, hoặc `font_size` không phải bội số | Tắt Antialiasing/Hinting/Subpixel; dùng size là bội số của size gốc |
| Item nhặt rồi, load lại level lại thấy | Không dùng `pickup_flag` | Set `pickup_flag` cho mỗi ItemPickup, tên duy nhất |
| Cổng mở rồi, quay lại màn thấy đóng | Không đọc flag trong `_ready` | Xem `LockedGate._ready()` mục 6.4.3 |
| `body_entered` của Area3D không bắn | `collision_mask` Area không chứa layer của player; hoặc `monitoring = false` | Area mask = bit của player (2) |
| Trigger chuyển màn bắn liên tục (loop) | Spawn point nằm TRONG vùng trigger của portal ngược lại | Đặt spawn cách portal ≥ 2 unit |
| Chuyển màn xong player ở gốc (0,0,0) | Level thiếu node `Spawns` hoặc sai tên marker | Kiểm tra `get_spawn_point`; đọc warning trong Output |
| Chuyển màn xong có 2 camera | Level cũ chưa `free()` xong | Dùng `free()` thay `queue_free()` như code 6.8 |
| Save không có file | Chưa `make_dir_recursive_absolute` | Xem `_ready` của `SaveSystem`; mở `Project → Open User Data Folder` để kiểm |
| Load save cũ crash sau khi bạn sửa code | Cấu trúc dữ liệu đổi | Tăng `SAVE_VERSION` + viết `_migrate`, hoặc xóa save cũ khi đang dev |
| Save trên web không giữ | Browser IndexedDB — cần flush | Godot web tự flush, nhưng chế độ ẩn danh/xóa cache sẽ mất. Cảnh báo người chơi |
| Inventory trống sau khi export | `DirAccess` không liệt kê được `.tres` trong PCK | Xem cảnh báo ở 6.2 — dùng resource database `@export Array[ItemData]` |
| Puzzle đuốc: bật đúng vẫn fail | `correct_order` dùng tên node khác thực tế | In `child.name` ra để đối chiếu chính xác |
| `await` trong `_ready` làm node chưa sẵn sàng | `await` làm `_ready` trả về sớm | Tách logic async ra hàm riêng, gọi bằng `call_deferred` |
