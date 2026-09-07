# 08 — Âm thanh 8-bit

Âm thanh là thứ có **tỉ lệ hiệu quả/công sức cao nhất** trong game indie. Một game blockout xám có nhạc tốt cảm giác hay hơn một game art đẹp mà im lặng.

---

## 8.1 Bạn cần bao nhiêu

Cho MVP 5 phút:

| Loại | Số lượng | Độ dài |
|---|---|---|
| BGM làng (đêm, buồn, ấm) | 1 | 45–90s có loop |
| BGM hầm (tối, căng) | 1 | 45–90s có loop |
| BGM đỉnh/ending (sáng, giải thoát) | 1 | 30–60s |
| SFX | 10–14 | 0.1–1s |
| Ambience (sóng biển, gió) | 1–2 | loop 10s |

**Tổng: 3 nhạc + ~12 SFX.** Đó là tất cả. Đừng làm 12 bài nhạc cho game 5 phút.

Danh sách SFX cần (khớp code chương 06):

| Tên | Dùng ở | Mô tả âm |
|---|---|---|
| `text_blip` | Typewriter hộp thoại | Xung vuông rất ngắn, cao, nhẹ |
| `menu_move` | Chọn ô inventory | Blip thấp hơn |
| `menu_confirm` | Chọn lựa chọn thoại | 2 note lên |
| `menu_cancel` | Đóng túi | 2 note xuống |
| `pickup` | Nhặt item | Arpeggio 3 note lên, tươi |
| `locked` | Cổng khóa | Tiếng "cạch" thấp, noise ngắn |
| `gate_open` | Mở cổng | Noise dài + tiếng đá nghiến |
| `torch_light` | Thắp đuốc | Noise burst + rise |
| `puzzle_fail` | Đuốc sai | 3 note xuống, buồn |
| `puzzle_solved` | Đuốc đúng | 4-5 note lên, fanfare ngắn |
| `save` | Lưu game | Chime ấm, 2 note |
| `footstep` | Bước chân (tùy chọn) | Noise rất ngắn, ngẫu hóa cao độ |
| `crate_push` | Đẩy thùng | Noise ma sát, loop khi đang đẩy |
| `lighthouse_lit` | Ending | Fanfare dài, hoành tráng nhất game |

---

## 8.2 Công cụ (đều free)

### SFX — 15 phút là có đủ 12 tiếng

| Tool | Loại | Ghi chú |
|---|---|---|
| **jsfxr** (web, tìm "jsfxr") | Trình sinh SFX 8-bit | Bấm "Pickup/Coin", "Hurt", "Explosion" → ra ngay. Export `.wav`. **Nhanh nhất** |
| **ChipTone** (web, SFBGames) | Sinh SFX chi tiết hơn | Nhiều tham số hơn jsfxr, vẫn dễ |
| **rFXGen** (desktop, raylib) | Bản desktop của sfxr | Offline, có batch |
| **sfxr / bfxr** | Bản gốc | Kinh điển |
| **Audacity** | Chỉnh sửa | Cắt, fade, normalize, đổi cao độ |

Quy trình SFX thực tế:

1. Mở jsfxr
2. Bấm preset gần nhất (ví dụ "Pickup/Coin" cho `pickup`)
3. Bấm "Mutate" 5–10 lần, nghe, chọn cái thích
4. Kéo slider `Sustain`/`Decay` cho ngắn lại (SFX game nên **rất ngắn**)
5. Export `.wav` → `audio/sfx/pickup.wav`
6. Lặp lại

**12 SFX trong 15–20 phút.** Không cần AI, không cần kỹ năng.

### Nhạc chiptune

| Tool | Loại | Độ khó | Ghi chú |
|---|---|---|---|
| **Bosca Ceoil Blue** | Sequencer đơn giản | ⭐ Rất dễ | Làm cho người không biết nhạc. Có preset chip. **Bắt đầu ở đây** |
| **BeepBox** (web) | Sequencer web | ⭐ Rất dễ | Chia sẻ bằng URL, export `.wav`/`.mid` |
| **Furnace Tracker** | Tracker đa chip | ⭐⭐⭐ Khó | Chuẩn xác nhất: emulate NES 2A03, GB, SID... Chất 8-bit **thật** |
| **FamiTracker / 0CC-FamiTracker** | Tracker NES | ⭐⭐⭐ Khó | Đúng chuẩn NES. Windows |
| **LMMS** | DAW free | ⭐⭐ Trung bình | Linh hoạt, không chuyên chip |
| **DefleMask** | Tracker | ⭐⭐⭐ | Trả phí |

**Lộ trình khuyến nghị**: BeepBox hoặc Bosca Ceoil → làm được 3 bài trong 1 ngày. Nếu bạn thấy thích thì sang Furnace.

### Nhạc chiptune trong 30 phút với BeepBox (không cần biết nhạc)

1. Chọn `Scale: Minor` (buồn) hoặc `Major` (sáng)
2. Chọn `Key: A` (hoặc bất kỳ)
3. `Tempo`: 90 cho làng đêm, 110 cho hầm, 130 cho ending
4. **Kênh 1 (bass)**: chọn instrument `square wave`, đặt 4 note thấp lặp lại — đây là "vòng hòa âm". Ví dụ: A - F - C - G, mỗi note 1 ô
5. **Kênh 2 (melody)**: chọn `triangle`/`square`, viết melody chỉ dùng note trong scale. Quy tắc: đi lên rồi đi xuống, đừng nhảy quá xa
6. **Kênh 3 (drum)**: pattern noise đơn giản — kick ở nhịp 1 và 3
7. Loop 4–8 ô, export `.wav`

Cái này thật sự làm được trong 30 phút với 0 kiến thức nhạc lý. Nghe không xuất sắc, nhưng **có nhạc tốt hơn không nhạc rất nhiều**.

---

## 8.3 AI gen nhạc — nói thẳng

### Tình hình

| Loại tool | Chất lượng cho chiptune 8-bit | Vấn đề |
|---|---|---|
| **AI text-to-music** (Suno, Udio, Stable Audio...) | ⭐⭐ Nghe được nhưng **không phải chiptune thật** | Ra bản "nhạc game điện tử" full-band, có reverb, có bass thật. Không phải 3 kênh xung vuông |
| **AI gen MIDI** | ⭐⭐⭐ Khá hữu ích | Lấy MIDI về, import vào Furnace/BeepBox, gán instrument chip → **chiptune thật** |
| **AI viết pattern tracker** (nhờ Claude sinh code/dữ liệu) | ⭐⭐ Được cho ý tưởng | Không tool nào nhận trực tiếp; phải nhập tay |

**Kết luận trung thực**: AI text-to-music **không** cho ra chiptune 8-bit đúng chất. Nó cho ra "nhạc game orchestral/synth" — nghe hay nhưng lệch phong cách bạn đã chốt ở chương 00.

**Cách dùng AI cho nhạc hiệu quả nhất**: nhờ AI (Claude) viết **cấu trúc bài** và **chuỗi hợp âm + melody dạng note**, rồi bạn nhập vào BeepBox/Furnace bằng tay. Đây là cách AI thật sự giúp: nó giải quyết phần "tôi không biết nhạc lý", còn bạn giải quyết phần "phải ra đúng chất chip".

Prompt mẫu:

```
Tôi làm nhạc chiptune 8-bit cho game phiêu lưu, dùng BeepBox (3 kênh:
bass square, melody triangle, drum noise).

Bài cần: BGM cho một làng chài ban đêm, ngọn hải đăng đã tắt.
Cảm xúc: buồn, ấm, hơi lo lắng. Loop 8 ô nhạc, tempo 90.

Cho tôi:
1. Scale và key nên dùng (giải thích ngắn tại sao)
2. Chuỗi hợp âm 4 hợp âm (viết dạng tên hợp âm + note cụ thể)
3. Bass line: note theo từng ô (16 bước/ô)
4. Melody: note theo từng ô, độ dài mỗi note
5. Drum pattern đơn giản

Viết dạng bảng để tôi nhập tay vào BeepBox. Chỉ dùng note trong scale.
Giữ melody trong khoảng 1.5 octave để nghe được trên loa nhỏ.
```

Kết quả từ prompt này **thực sự dùng được** — nó là lý thuyết nhạc, không phải audio, nên AI làm tốt.

### Bản quyền nhạc AI — kiểm kỹ

| Vấn đề | Trạng thái | Bạn nên làm |
|---|---|---|
| Quyền thương mại của output | **Khác nhau theo tool và theo gói.** Nhiều tool chỉ cho dùng thương mại ở gói trả phí | Đọc ToS đúng tool + đúng gói. Lưu ảnh chụp điều khoản kèm ngày |
| Nhạc AI có bản quyền không | Tương tự ảnh AI: nhiều nơi coi output thuần AI là **không** được bảo hộ | Đừng dựa vào việc "sở hữu" bài nhạc AI |
| Nguy cơ giống bài có bản quyền | Có thật với model train trên nhạc thương mại | Nghe kỹ; nếu thấy quen quá thì bỏ |
| Steam / itch.io | Cần khai báo nội dung AI | Khai báo trung thực |
| YouTube Content ID | Nhạc AI có thể bị claim | Nếu game có streamer chơi, đây là rủi ro thật cho họ |

### Nguồn nhạc/SFX miễn phí hợp lệ (an toàn hơn)

| Nguồn | Giấy phép | Ghi chú |
|---|---|---|
| **OpenGameArt.org** | CC0 / CC-BY / GPL — **đọc từng asset** | Kho lớn nhất cho game indie |
| **Freesound.org** | CC0 / CC-BY | SFX thực; cần lọc |
| **Kenney.nl** | CC0 | Gói SFX/UI chất lượng, dùng thoải mái |
| **itch.io asset packs** | Theo từng tác giả | Nhiều pack chiptune giá $0–5 |
| **incompetech (Kevin MacLeod)** | CC-BY | Cần ghi credit |

> **Quy tắc CC-BY**: bạn **phải** ghi credit đúng cách (tên tác giả + link + license). Làm file `CREDITS.md` trong game ngay từ asset đầu tiên bạn tải — nhớ lại sau 3 tháng là không thể.

---

## 8.4 Định dạng & import vào Godot

| Định dạng | Dùng cho | Lý do |
|---|---|---|
| **`.ogg`** (Vorbis) | **Nhạc nền** | Nén tốt, hỗ trợ loop tốt, Godot đọc native |
| **`.wav`** | **SFX ngắn** | Không nén → không delay khi phát, file nhỏ vì âm ngắn |
| `.mp3` | Tránh nếu được | Godot hỗ trợ, nhưng có gap khi loop |

Chuyển đổi bằng Audacity: `File → Export → Export as OGG` (quality 5–6 là đủ cho chiptune).

### Cài loop cho nhạc `.ogg`

Chọn file `.ogg` trong FileSystem → tab **Import**:

- `Loop`: **On**
- `Loop Offset`: giây bắt đầu loop (0 nếu loop toàn bài; đặt số khác nếu bài có đoạn intro không loop)
- Bấm **Reimport**

Với `.wav` (SFX): `Loop Mode: Disabled`, `Force → 8 Bit: off` (bật nếu muốn ép chất lượng chip thô hơn — thử xem thích không).

### Normalize âm lượng — làm sớm

Trước khi import, normalize hết file về cùng mức (Audacity: `Effect → Normalize → -3 dB`). Không làm bước này bạn sẽ có tiếng nhặt item to gấp 5 lần nhạc nền, và mất cả buổi đi tune `volume_db` từng chỗ.

Mức gợi ý:

| Loại | Peak |
|---|---|
| BGM | -6 dB |
| SFX thường | -6 dB |
| SFX quan trọng (puzzle solved) | -3 dB |
| `text_blip`, `footstep` (phát rất nhiều) | -18 dB |

---

## 8.5 Audio bus — thiết lập 1 lần

Mở panel **Audio** (dưới cùng editor, cạnh Output/Debugger). Tạo bus:

```
Master
├── BGM        ← nhạc nền
├── SFX        ← hiệu ứng
└── Ambience   ← sóng biển, gió
```

Lưu layout: `Audio panel → Save As... → default_bus_layout.tres`, rồi set ở `Project Settings → Audio → Buses → Default Bus Layout`.

Vì sao cần bus: người chơi cần **slider âm lượng riêng cho nhạc và SFX**. Nếu bạn không tách bus từ đầu, thêm sau phải sửa mọi node.

Thêm effect vào bus `BGM`: `Reverb` nhẹ cho hầm (bật/tắt theo level) — hiệu ứng "trong hầm" cực rẻ.

---

## 8.6 Autoload `Audio`

```gdscript
# scripts/autoload/audio.gd
extends Node

## ─── Cấu hình ───────────────────────────────────────────────────────
const SFX_DIR := "res://audio/sfx/"
const SFX_POOL_SIZE := 12          # số SFX phát cùng lúc tối đa
const BGM_FADE_TIME := 0.8

## ─── Node nội bộ ────────────────────────────────────────────────────
var _bgm_a: AudioStreamPlayer
var _bgm_b: AudioStreamPlayer
var _bgm_using_a := true

var _sfx_pool: Array[AudioStreamPlayer] = []
var _sfx_next := 0

var _ambience: AudioStreamPlayer

## Cache stream SFX theo tên để không load lại mỗi lần phát.
var _sfx_cache: Dictionary = {}

## Chống spam: cùng 1 SFX không phát lại trong khoảng này (giây).
const SFX_MIN_INTERVAL := 0.03
var _last_played: Dictionary = {}


func _ready() -> void:
	# Hai player BGM để crossfade khi đổi nhạc.
	_bgm_a = _make_player("BGM")
	_bgm_b = _make_player("BGM")
	_ambience = _make_player("Ambience")

	for i in SFX_POOL_SIZE:
		_sfx_pool.append(_make_player("SFX"))


func _make_player(bus_name: String) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.bus = bus_name
	add_child(p)
	return p


## ─── BGM ────────────────────────────────────────────────────────────

## Đổi nhạc với crossfade. Gọi lại cùng bài -> không làm gì.
func play_bgm(stream: AudioStream, fade: float = BGM_FADE_TIME) -> void:
	if stream == null:
		return
	var current := _bgm_a if _bgm_using_a else _bgm_b
	var next := _bgm_b if _bgm_using_a else _bgm_a

	if current.stream == stream and current.playing:
		return          # đã phát bài này rồi

	next.stream = stream
	next.volume_db = -40.0
	next.play()

	var tw := create_tween().set_parallel(true)
	tw.tween_property(next, "volume_db", 0.0, fade)
	if current.playing:
		tw.tween_property(current, "volume_db", -40.0, fade)
		tw.chain().tween_callback(current.stop)

	_bgm_using_a = not _bgm_using_a


func stop_bgm(fade: float = BGM_FADE_TIME) -> void:
	var current := _bgm_a if _bgm_using_a else _bgm_b
	if not current.playing:
		return
	var tw := create_tween()
	tw.tween_property(current, "volume_db", -40.0, fade)
	tw.tween_callback(current.stop)


## ─── SFX ────────────────────────────────────────────────────────────

## Phát SFX theo tên file (không cần đuôi): play_sfx_by_name("pickup")
func play_sfx_by_name(sfx_name: String, volume_db: float = 0.0, pitch_variation: float = 0.06) -> void:
	if sfx_name == "":
		return

	# Chống spam cùng một tiếng trong 1 frame (typewriter, footstep).
	var now := Time.get_ticks_msec() / 1000.0
	if _last_played.has(sfx_name) and now - float(_last_played[sfx_name]) < SFX_MIN_INTERVAL:
		return
	_last_played[sfx_name] = now

	var stream := _get_sfx(sfx_name)
	if stream == null:
		return

	var p := _sfx_pool[_sfx_next]
	_sfx_next = (_sfx_next + 1) % _sfx_pool.size()

	p.stream = stream
	p.volume_db = volume_db
	# Đổi cao độ ngẫu nhiên chút -> nghe không "máy móc" khi phát liên tục.
	p.pitch_scale = 1.0 + randf_range(-pitch_variation, pitch_variation)
	p.play()


func _get_sfx(sfx_name: String) -> AudioStream:
	if _sfx_cache.has(sfx_name):
		return _sfx_cache[sfx_name]

	# Thử cả .wav và .ogg.
	for ext in [".wav", ".ogg"]:
		var path := SFX_DIR + sfx_name + ext
		if ResourceLoader.exists(path):
			var s: AudioStream = load(path)
			_sfx_cache[sfx_name] = s
			return s

	push_warning("Audio: không tìm thấy SFX '%s' trong %s" % [sfx_name, SFX_DIR])
	_sfx_cache[sfx_name] = null       # cache cả kết quả null -> không warn lặp
	return null


## ─── Ambience ───────────────────────────────────────────────────────

func play_ambience(stream: AudioStream, volume_db: float = -12.0) -> void:
	if _ambience.stream == stream and _ambience.playing:
		return
	_ambience.stream = stream
	_ambience.volume_db = volume_db
	_ambience.play()


func stop_ambience() -> void:
	_ambience.stop()


## ─── Âm lượng (cho menu settings) ───────────────────────────────────

## linear 0.0..1.0 -> dB. Dùng linear cho slider vì tai người nghe theo log.
func set_bus_volume(bus_name: String, linear: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx < 0:
		push_warning("Audio: không có bus '%s'" % bus_name)
		return
	if linear <= 0.001:
		AudioServer.set_bus_mute(idx, true)
	else:
		AudioServer.set_bus_mute(idx, false)
		AudioServer.set_bus_volume_db(idx, linear_to_db(linear))


func get_bus_volume(bus_name: String) -> float:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx < 0:
		return 0.0
	if AudioServer.is_bus_mute(idx):
		return 0.0
	return db_to_linear(AudioServer.get_bus_volume_db(idx))
```

> `linear_to_db` / `db_to_linear` là hàm global trong Godot 4. Ở Godot 3 chúng tên `linear2db`/`db2linear` — nếu thấy lỗi tên hàm, bạn đang đọc tài liệu Godot 3.

---

## 8.7 Âm thanh 3D (`AudioStreamPlayer3D`)

Dùng cho tiếng phát ra từ **một vị trí trong world**: đuốc cháy, sóng vỗ ở bến, tiếng nước nhỏ giọt trong hầm.

```
Torch (Interactable)
├── Sprite
├── Light (OmniLight3D)
└── Sound (AudioStreamPlayer3D)
    stream = audio/sfx/fire_loop.ogg    (Loop = On khi import)
    unit_size = 3.0                      ← khoảng cách mà âm bắt đầu nhỏ đi
    max_distance = 12.0                   ← xa hơn thì không nghe
    attenuation_model = Inverse Distance
    bus = "Ambience"
    autoplay = true
```

Với camera **orthographic ở xa** (như game của ta), `AudioStreamPlayer3D` tính khoảng cách từ **camera**, mà camera đứng cách 20 unit → mọi tiếng đều rất nhỏ.

Hai cách xử lý:

1. Tăng `unit_size` và `max_distance` lên tương ứng (ví dụ ×3)
2. **Khuyến nghị**: đặt một `AudioListener3D` ở vị trí **player** thay vì camera:

```
Player (CharacterBody3D)
└── AudioListener3D          ← position (0, 1, 0)
```

Trong script player: `$AudioListener3D.make_current()` ở `_ready()`. Từ đó âm thanh 3D tính theo tai nhân vật — đúng trực giác hơn.

> **Kiểm tra lại**: tên node là `AudioListener3D` trong Godot 4 (Godot 3 gọi `Listener`). Nếu không thấy trong danh sách Add Node, tra F1.

---

## 8.8 Cắm âm thanh vào game

Điểm cắm cho từng hệ thống (khớp code chương 04–06):

| Chỗ | Gọi gì |
|---|---|
| `level_base.gd::_ready` | `Audio.play_bgm(bgm)` |
| `dialogue_box.gd` typewriter | `Audio.play_sfx_by_name("text_blip")` mỗi 3 ký tự |
| `dialogue_box.gd::show_choices` | `Audio.play_sfx_by_name("menu_confirm")` |
| `item_pickup.gd::interact` | `Audio.play_sfx_by_name("pickup")` |
| `locked_gate.gd` khóa / mở | `"locked"` / `"gate_open"` |
| `torch.gd::interact` | `"torch_light"` |
| `torch_puzzle.gd` | `"puzzle_fail"` / `"puzzle_solved"` |
| `save_point.gd` | `"save"` |
| `inventory_ui.gd` chọn ô | `"menu_move"` |
| `player.gd` bước chân | AnimationPlayer track "Call Method" ở frame chân chạm đất |

### Bước chân đúng nhịp

Đừng dùng timer. Dùng `AnimationPlayer` gọi method ở đúng frame animation chân chạm đất:

```
Animation "walk_down" (AnimationPlayer, không phải AnimatedSprite3D):
  track "Call Method" trên node Player:
    @ 0.15s  →  play_footstep()
    @ 0.45s  →  play_footstep()
```

```gdscript
## Thêm vào player.gd
func play_footstep() -> void:
	# pitch_variation cao -> mỗi bước nghe khác nhau, đỡ máy móc.
	Audio.play_sfx_by_name("footstep", -14.0, 0.15)
```

Cách này làm bước chân **khớp** với animation ở mọi tốc độ — timer thì không.

---

## 8.9 Menu âm lượng

```
SettingsMenu (Control)
├── BGMSlider (HSlider)       min 0, max 1, step 0.05
├── SFXSlider (HSlider)
└── AmbSlider (HSlider)
```

```gdscript
# scripts/ui/settings_menu.gd
extends Control

const CONFIG_PATH := "user://settings.cfg"

@onready var bgm_slider: HSlider = $BGMSlider
@onready var sfx_slider: HSlider = $SFXSlider
@onready var amb_slider: HSlider = $AmbSlider


func _ready() -> void:
	_load_settings()
	bgm_slider.value_changed.connect(_on_changed.bind("BGM"))
	sfx_slider.value_changed.connect(_on_changed.bind("SFX"))
	amb_slider.value_changed.connect(_on_changed.bind("Ambience"))


func _on_changed(value: float, bus_name: String) -> void:
	Audio.set_bus_volume(bus_name, value)
	_save_settings()


## ConfigFile rất phù hợp cho settings: dạng INI, dễ đọc, dễ sửa tay khi debug.
func _save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("audio", "bgm", bgm_slider.value)
	cfg.set_value("audio", "sfx", sfx_slider.value)
	cfg.set_value("audio", "ambience", amb_slider.value)
	cfg.save(CONFIG_PATH)


func _load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(CONFIG_PATH) != OK:
		# Chưa có file -> dùng mặc định.
		bgm_slider.value = 0.7
		sfx_slider.value = 0.8
		amb_slider.value = 0.5
	else:
		bgm_slider.value = cfg.get_value("audio", "bgm", 0.7)
		sfx_slider.value = cfg.get_value("audio", "sfx", 0.8)
		amb_slider.value = cfg.get_value("audio", "ambience", 0.5)

	Audio.set_bus_volume("BGM", bgm_slider.value)
	Audio.set_bus_volume("SFX", sfx_slider.value)
	Audio.set_bus_volume("Ambience", amb_slider.value)
```

> Đây là chỗ `ConfigFile` **đúng việc** — settings đơn giản, phẳng, người dùng có thể sửa tay khi cần. Còn save game thì dùng JSON (chương 06).

---

## 8.10 Bài tập

1. Làm đủ 12 SFX bằng jsfxr trong 30 phút. Normalize hết về -6 dB (trừ `text_blip` về -18 dB).
2. Làm 1 bài BGM cho làng bằng BeepBox theo hướng dẫn 8.2. Export `.ogg`, set Loop = On.
3. Thử prompt AI ở 8.3 → nhập kết quả vào BeepBox. So sánh với bài bạn tự làm ở bài 2. Cái nào hay hơn?
4. Dựng `Audio` autoload + 3 bus. Cắm `pickup` và `text_blip` theo bảng 8.8.
5. Thêm `AudioStreamPlayer3D` cho một ngọn đuốc. Đi lại gần/xa → nghe to/nhỏ. Nếu không nghe được → thêm `AudioListener3D` vào player.
6. Làm menu âm lượng. Kéo slider → nghe đổi ngay, tắt game mở lại → giữ nguyên.
7. Tạo `CREDITS.md` liệt kê mọi asset bạn dùng + license + link.

---

## 8.11 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Nhạc không loop, có khoảng lặng | `.mp3`, hoặc Loop = Off khi import | Dùng `.ogg`, tab Import → Loop On → Reimport |
| Nhạc restart mỗi lần vào level | Gọi `play_bgm` với stream mới mỗi lần | Code 8.6 đã check trùng — đảm bảo dùng **cùng resource** ở các level |
| SFX bị cắt giữa | Pool bị ghi đè (nhiều SFX cùng lúc) | Tăng `SFX_POOL_SIZE` |
| `text_blip` nghe như tiếng rè | Phát mỗi frame | Chỉ phát mỗi 3 ký tự + `SFX_MIN_INTERVAL` |
| SFX to hơn nhạc rất nhiều | Chưa normalize | Normalize hết ở Audacity |
| Không nghe gì | Bus bị mute, hoặc `volume_db` quá thấp, hoặc bus name gõ sai | Mở panel Audio khi chạy game, xem VU meter bus nào có tín hiệu |
| Âm thanh 3D quá nhỏ | Camera ở xa | Thêm `AudioListener3D` vào player + `make_current()` |
| Slider âm lượng đổi rất "giật" | Dùng `set_bus_volume_db(slider.value)` trực tiếp | Dùng `linear_to_db` như code 8.6 |
| Nhạc vẫn phát sau khi thoát ra menu | Chưa `stop_bgm()` | Gọi `Audio.stop_bgm()` khi về menu |
| Web export không có tiếng lúc đầu | Browser chặn autoplay tới khi có tương tác người dùng | Bắt đầu game bằng 1 nút "Bấm để chơi" — đây là hành vi bắt buộc của browser |
| File audio làm build phình to | `.wav` cho nhạc dài | Nhạc → `.ogg`; chỉ SFX ngắn dùng `.wav` |
| Nhạc AI bị Content ID claim | Bản chất nhạc AI | Xem 8.3; ưu tiên tự làm hoặc CC0 |
