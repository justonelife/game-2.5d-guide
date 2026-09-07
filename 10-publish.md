# 10 — Build & phát hành

---

## 10.1 Trước khi export: checklist làm sạch

Làm hết trước khi export lần đầu. Bỏ bước nào cũng sẽ quay lại tốn thời gian.

```
□ Tắt debug menu / cheat (đảm bảo bọc trong OS.is_debug_build())
□ Tắt hết print() ồn ào (dùng Dbg.ENABLED = false hết, chương 09)
□ Xóa scene test khỏi build (hoặc để export filter loại trừ)
□ Kiểm Output khi chạy: KHÔNG còn warning/error
□ Set icon game (Project Settings → Application → Config → Icon, PNG 256x256)
□ Set tên game + version (Application → Config → Name, và Version)
□ Set Main Scene đúng (Application → Run → Main Scene)
□ Test full playthrough từ đầu tới ending, không dùng cheat
□ Test save/load ít nhất 3 lần ở các điểm khác nhau
□ Kiểm mọi asset đã có license rõ ràng → CREDITS.md
□ Tạo màn hình credits trong game (không chỉ file .md)
□ Đảm bảo có cách THOÁT game (Esc → menu → Thoát). Web export thì bỏ nút thoát
□ Test với gamepad (nếu hỗ trợ)
□ Test ở resolution khác (kéo cửa sổ, fullscreen Alt+Enter)
□ git commit + tag: git tag v0.1.0
```

### Quan trọng: kiểm `ItemDB` sau export

Chương 06 mục 6.2 có cảnh báo: `DirAccess.get_files()` trên `res://` **có thể** không liệt kê được `.tres` trong file PCK đã export.

**Test cụ thể**: export → chạy bản export → nhặt item → mở túi đồ. Nếu icon trống / tên item trống → đúng lỗi này.

Cách sửa chắc chắn: tạo một resource database thay vì quét thư mục.

```gdscript
# scripts/systems/item_database.gd
class_name ItemDatabase
extends Resource

## Gán tay tất cả ItemData vào đây trong Inspector.
## Cách này an toàn 100% khi export vì nó là tham chiếu resource thật,
## không phụ thuộc DirAccess quét thư mục trong PCK.
@export var items: Array[ItemData] = []
```

Tạo `data/item_database.tres`, kéo 6 item vào. Rồi:

```gdscript
# scripts/systems/item_db.gd — bản an toàn cho export
class_name ItemDB
extends RefCounted

const DB_PATH := "res://data/item_database.tres"

static var _cache: Dictionary = {}

static func _ensure_loaded() -> void:
	if not _cache.is_empty():
		return
	var db: ItemDatabase = load(DB_PATH)
	if db == null:
		push_error("Không load được %s" % DB_PATH)
		return
	for item in db.items:
		if item != null and item.id != "":
			_cache[item.id] = item

static func get_item(id: String) -> ItemData:
	_ensure_loaded()
	return _cache.get(id, null)

static func all_items() -> Array[ItemData]:
	_ensure_loaded()
	var out: Array[ItemData] = []
	for v in _cache.values():
		out.append(v)
	return out
```

Nhược điểm: phải kéo item vào database bằng tay. Ưu điểm: **chắc chắn hoạt động sau export**. Với 6 item thì đây là đánh đổi đúng.

---

## 10.2 Export templates

`Editor → Manage Export Templates → Download and Install`.

Kích thước ~1GB, tải một lần cho mỗi bản Godot. Nếu bạn nâng Godot 4.4 → 4.5, **phải tải lại templates**.

> Nếu tải qua editor bị lỗi/chậm: tải file `.tpz` từ trang download của Godot rồi `Install from File`.

---

## 10.3 Export desktop (Windows / Linux / macOS)

`Project → Export → Add... → Windows Desktop`

### Setting quan trọng

| Mục | Setting | Giá trị |
|---|---|---|
| Options | `Binary Format → Embed PCK` | `On` nếu muốn **1 file .exe duy nhất**; `Off` cho `.exe` + `.pck` (nhỏ hơn khi patch) |
| Options | `Binary Format → Architecture` | `x86_64` |
| Resources | `Export Mode` | `Export all resources in the project` |
| Resources | `Filters to exclude` | `scenes/tests/*, docs/*, *.aseprite, *.xcf, *.psd, *.md` |
| Features | `Custom (comma-separated)` | để trống |

Filter loại trừ rất quan trọng: file `.aseprite` gốc có thể nặng gấp 10 lần PNG export, và người chơi không cần chúng.

### Windows: icon và metadata

Để `.exe` có icon riêng, Godot cần công cụ `rcedit`:

1. Tải `rcedit-x64.exe`
2. `Editor Settings → Export → Windows → Rcedit` → trỏ tới file đó
3. Trong export preset, mục `Application`: set `Icon` (file `.ico`), `File Version`, `Product Name`, `Company Name`

Không có `rcedit` thì `.exe` dùng icon Godot mặc định — không sai, chỉ trông thiếu chuyên nghiệp.

### macOS

- Export ra `.dmg` hoặc `.zip`
- **Chưa code-sign** → người dùng macOS sẽ thấy cảnh báo "không mở được vì không rõ nhà phát triển". Họ phải chuột phải → Open, hoặc vào System Settings → Privacy & Security → Open Anyway.
- Code-sign đúng cách cần Apple Developer account ($99/năm). **Cho game jam / itch.io miễn phí thì bỏ qua**, chỉ cần ghi hướng dẫn mở trong trang game.
- Export cho macOS từ Windows/Linux được, nhưng notarization thì cần máy Mac.

### Linux

- Export ra file thực thi (không đuôi) hoặc `.x86_64`
- Nhắc người dùng `chmod +x` nếu tải zip
- Nên đóng gói cả `.pck` cùng thư mục nếu không embed

### Test bản export

**Bắt buộc**: copy sang **máy khác** (hoặc ít nhất thư mục khác, không phải thư mục project) và chạy. Rất nhiều lỗi chỉ xuất hiện ở bản export:

- Đường dẫn `res://` viết hoa/thường sai (Windows không phân biệt, Linux có)
- File không được include vì filter
- `DirAccess` quét thư mục không hoạt động
- Script `@tool` chạy sai khi không có editor

---

## 10.4 Export Web (HTML5) — quan trọng nhất cho itch.io

Web là cách **dễ nhất** để người ta thử game của bạn (không cần tải, click là chơi). Nhưng cũng khó nhất về kỹ thuật.

### Điều kiện

| Yêu cầu | Ghi chú |
|---|---|
| Renderer | **Compatibility** cho tương thích tốt nhất. Forward+/Mobile cần WebGPU — hỗ trợ browser chưa đồng đều |
| Export template | Web template (tải cùng bộ templates) |
| Hosting | Phải qua HTTP(S) server, **không** mở file `.html` trực tiếp bằng browser |

### Setting export Web

| Mục | Setting | Giá trị |
|---|---|---|
| Options | `Variant → Extensions Support` | `Off` (trừ khi bạn dùng GDExtension) |
| Options | `Variant → Thread Support` | Xem bảng dưới |
| Options | `VRAM Texture Compression → For Desktop` | `On` |
| Options | `VRAM Texture Compression → For Mobile` | `On` nếu muốn chơi trên điện thoại |
| Progressive Web App | `Enabled` | `Off` cho đơn giản |
| Resources | Filters to exclude | như desktop |

**Thread Support** — đây là chỗ hay vướng:

| Thread Support | Cần gì | Đánh giá |
|---|---|---|
| `On` | Server phải gửi header `Cross-Origin-Opener-Policy: same-origin` và `Cross-Origin-Embedder-Policy: require-corp` (để bật `SharedArrayBuffer`) | Hiệu năng tốt hơn, nhưng **không chạy** nếu host không set header |
| `Off` | Không cần header đặc biệt | Tương thích rộng nhất, hiệu năng thấp hơn chút |

**Khuyến nghị**: bắt đầu với `Thread Support = Off`. Nó chạy ở mọi chỗ. Nếu game lag, thử `On` và kiểm host có hỗ trợ header không.

> itch.io có tùy chọn bật `SharedArrayBuffer` cho project HTML (trong phần cài đặt upload). Nếu bạn export với threads, phải bật nó. **Kiểm tra lại trên trang itch.io hiện tại** — tên tùy chọn có thể đổi.

### Tên file export

Đặt tên file export là **`index.html`**. Nhiều host (itch.io) yêu cầu file này ở gốc zip.

```
Export Path: build/web/index.html
```

Sau export bạn có: `index.html`, `index.js`, `index.wasm`, `index.pck`, `index.audio.worklet.js`, `index.icon.png`...

### Test local

Không mở `index.html` trực tiếp (browser chặn vì CORS). Dùng server local:

```bash
# Cách 1: Godot làm sẵn — sau khi export, bấm nút "Remote Debug → Run in Browser"
#         (biểu tượng browser trên toolbar, khi platform đang là Web)

# Cách 2: Python
cd build/web
python3 -m http.server 8000
# rồi mở http://localhost:8000

# Cách 3: nếu có Node
npx serve build/web
```

### Giới hạn thật của web export

Nói thẳng để bạn không mất buổi debug:

| Giới hạn | Chi tiết | Cách xử lý |
|---|---|---|
| **Audio không tự phát** | Browser chặn audio tới khi user tương tác | Bắt đầu bằng màn hình "Bấm để chơi" — bắt buộc, không phải tùy chọn |
| **`user://` là IndexedDB** | Save nằm trong browser storage. Xóa cache = mất save. Chế độ ẩn danh không giữ | Ghi cảnh báo trên trang game |
| **Không có fullscreen tự động** | Chỉ vào fullscreen sau user gesture | Nút fullscreen trong game |
| **Load lần đầu chậm** | Phải tải wasm + pck (10–50MB) | Tối ưu size (10.6). Thêm loading screen |
| **Hiệu năng thấp hơn desktop** | ~50–70% | Game pixel 2.5D thường vẫn dư sức |
| **Một số hiệu ứng không có** | SDFGI, volumetric fog, một số compute shader | Dùng Compatibility ngay từ đầu để biết giới hạn sớm |
| **Mobile browser hay lỗi** | Bộ nhớ hạn chế, iOS Safari khó tính | Test thật trên điện thoại; có thể phải giảm texture |
| **Gamepad không ổn định** | Tùy browser | Đảm bảo bàn phím chơi được đủ |

---

## 10.5 Export Mobile (Android / iOS) — nói thật về công sức

### Android

Cần cài thêm:

1. **JDK 17** (hoặc bản Godot yêu cầu — kiểm trong docs bản bạn dùng)
2. **Android SDK** (qua Android Studio hoặc command-line tools)
3. Cài `Android Build Template` trong Godot: `Project → Install Android Build Template`
4. Tạo **debug keystore** (Editor Settings → Export → Android → Debug Keystore)
5. Cho release: tạo **release keystore** riêng, giữ cẩn thận (mất là không update app được nữa)

Setting quan trọng:

| Mục | Giá trị |
|---|---|
| `Architectures` | `arm64-v8a` (bắt buộc cho Play Store), thêm `armeabi-v7a` nếu muốn máy cũ |
| `Package → Unique Name` | `com.tenban.ngondencanuc` |
| `Gradle Build → Use Gradle Build` | `On` (cần cho nhiều tính năng) |
| Renderer | `Mobile` hoặc `Compatibility` |

### Vấn đề thiết kế nghiêm trọng: điều khiển cảm ứng

Game của bạn thiết kế cho bàn phím/gamepad. Trên mobile bạn **phải** làm:

- Virtual joystick (hoặc tap-to-move)
- Nút tương tác lớn (≥ 48dp)
- UI to hơn (font pixel 8px trên điện thoại là không đọc được)
- Bỏ prompt "[E] Nhặt" → đổi thành icon

Đây **không** phải việc export, mà là **redesign UI**. Ước lượng 1–2 tuần.

**Khuyến nghị thật lòng**: với MVP, **bỏ mobile**. Làm desktop + web trước. Thêm mobile ở bản sau nếu game có người chơi.

### iOS

- Cần **máy Mac** + Xcode
- Cần **Apple Developer account** ($99/năm) để chạy trên thiết bị thật và lên App Store
- Godot export ra Xcode project, bạn build từ đó
- Quy trình duyệt App Store nghiêm ngặt

**Khuyến nghị**: chỉ làm iOS khi game đã có doanh thu hoặc lượng người chơi thật.

---

## 10.6 Tối ưu cho pixel art game

Game 8-bit 2.5D vốn nhẹ. Nhưng vài thứ vẫn nên làm:

### 10.6.1 Kích thước build

| Kỹ thuật | Tiết kiệm |
|---|---|
| Filter loại trừ `.aseprite`/`.psd`/`docs` | Có thể 50%+ |
| Nhạc `.ogg` quality 4–5 thay vì `.wav` | 10× cho phần audio |
| Không bao gồm asset thử nghiệm không dùng | Tùy |
| Texture import: `Lossless` cho pixel art (đừng dùng VRAM compression cho sprite pixel!) | — |

> ⚠️ **Đừng** bật VRAM compression (S3TC/ETC/BPTC) cho **texture pixel art**. Nó là nén mất mát theo block → làm pixel art bị nhiễu màu, đặc biệt ở vùng màu phẳng. Với pixel art, `Lossless` (PNG) đã rất nhỏ rồi.
>
> Nhưng option `VRAM Texture Compression` trong export preset Web thì liên quan tới texture 3D — nếu bạn chỉ dùng sprite pixel, ảnh hưởng ít. Kiểm tra bằng mắt sau export.

Kiểm tra size:

```bash
ls -lh build/web/
du -sh build/windows/
```

Mục tiêu cho game 5 phút: **< 30MB** web, **< 60MB** desktop. Nếu vượt nhiều, xem file nào to:

```bash
# Xem file nào nặng nhất trong project
du -ah . --exclude=.godot --exclude=.git | sort -rh | head -20
```

### 10.6.2 Hiệu năng

Đo trước khi tối ưu. Chạy game (F5) → tab **Debugger → Monitors**:

| Chỉ số | Ngưỡng bình thường cho game này |
|---|---|
| FPS | 60 (hoặc bằng refresh rate) |
| `Draw Calls` (Rendering) | < 200 |
| `Objects` | < 2000 |
| `Static Memory` | < 200MB |

Nếu FPS thấp, thứ tự nghi phạm cho game pixel 2.5D:

1. **Quá nhiều đèn có shadow** → tắt `shadow_enabled` trên `OmniLight3D`
2. **Environment effect nặng** (SDFGI, SSAO, volumetric fog) → tắt hết, giữ `glow` nếu cần
3. **Quá nhiều node có `_process`** → tắt `_process` khi không cần: `set_process(false)`
4. **Sprite transparent chồng nhau nhiều** → dùng `alpha_cut = Discard` (đã làm, chương 02)
5. **Nhiều draw call vì nhiều texture riêng** → gộp atlas

### 10.6.3 Loading

Với web, thêm loading screen. Godot có sẵn màn hình boot (`Project Settings → Application → Boot Splash`):

- `Image`: PNG logo của bạn
- `Fullsize`: `Off` (giữ pixel nét)
- `Use Filter`: **`Off`** (quan trọng — bật thì logo pixel bị mờ)
- `BG Color`: khớp màu game

---

## 10.7 Đăng game

### itch.io — nơi nên bắt đầu

Lý do: miễn phí, cộng đồng indie thân thiện, hỗ trợ web build chạy trực tiếp, không cần duyệt.

Quy trình:

1. Tạo account → `Dashboard → Create new project`
2. **Kind of project**: `HTML` (nếu có web build) — cho phép chơi ngay trong trang
3. Upload:
   - Zip của `build/web/` (có `index.html` ở gốc zip) → tick **"This file will be played in the browser"**
   - Thêm `.zip` Windows/Linux/macOS → tick "downloadable"
4. **Embed options**: set viewport size. Với base 320×180, đặt `960 × 540` (×3) hoặc `1280 × 720` (×4). Tick `Fullscreen button`, `Enable scrollbars: off`
5. **Nếu export với Thread Support = On**: tick tùy chọn `SharedArrayBuffer support` (tên có thể khác — tìm trong phần cài đặt file HTML)
6. Điền metadata (10.8)
7. **Pricing**: `$0 or donate` cho game đầu tiên
8. **Visibility**: `Draft` → test kỹ → `Public`

### Nơi khác

| Nền tảng | Chi phí | Phù hợp |
|---|---|---|
| **itch.io** | Free, chia doanh thu tùy bạn chọn | ✅ Game đầu tiên, jam, demo |
| **GameJolt** | Free | Cộng đồng game indie, nhiều người trẻ |
| **Newgrounds** | Free | Web game, cộng đồng lâu năm |
| **Steam** | **$100/game** (Steam Direct, hoàn lại sau $1000 doanh thu) | Game hoàn chỉnh, có ý định bán. Cần khai báo nội dung AI |
| **Epic Games Store** | Cần apply | Khó vào với game nhỏ |
| **Google Play** | $25 một lần | Nếu làm mobile |
| **App Store** | $99/năm | Nếu làm iOS |

**Lộ trình khuyến nghị**: itch.io (free) → thu feedback → nếu game có triển vọng thì mở rộng → Steam.

---

## 10.8 Trang game: những gì phải có

Trang game quyết định người ta có click chơi hay không. Đầu tư 2 giờ vào đây có giá trị hơn 2 giờ polish code.

```
□ TIÊU ĐỀ rõ ràng
□ MỘT CÂU mô tả game (logline chương 00). Không dùng "một game phiêu lưu
  thú vị nơi bạn sẽ..." — nói thẳng game về cái gì
□ GIF ANIMATION (quan trọng nhất!) — 5-10 giây gameplay thật, không phải
  title screen. Đây là thứ 90% người ta xem. Dùng ScreenToGif / Gifski / ffmpeg
□ 3-5 SCREENSHOT — chọn khung hình đẹp nhất, đủ 2 khu vực
□ Mô tả: game về cái gì, chơi bao lâu (nói rõ "5 phút"), có gì đặc biệt
□ ĐIỀU KHIỂN — liệt kê rõ ràng. Người chơi web không đọc được README
□ Nếu web: cảnh báo save lưu trong browser
□ Nếu macOS không sign: hướng dẫn mở (chuột phải → Open)
□ CREDITS: mọi asset + license + link tác giả
□ KHAI BÁO AI: nếu dùng asset/nhạc AI, nói rõ. Cộng đồng itch nhạy cảm chuyện
  này — trung thực được tôn trọng hơn bị phát hiện
□ Tags: godot, pixel-art, adventure, 2-5d, hd-2d, singleplayer, puzzle
□ Genre + platform đúng
□ Link liên hệ / social để nhận feedback
```

Làm GIF bằng ffmpeg:

```bash
# Quay video game trước (OBS), rồi:
ffmpeg -i gameplay.mp4 -vf "fps=15,scale=640:-1:flags=neighbor" -loop 0 preview.gif
```

`flags=neighbor` giữ pixel nét — quan trọng cho pixel art game. Nếu dùng `flags=bilinear` (mặc định) GIF sẽ mờ và game trông tệ hơn thực tế.

---

## 10.9 Sau khi phát hành: thu feedback

### Nơi tìm người chơi thử

| Nơi | Ghi chú |
|---|---|
| **r/godot** (Reddit) | Thân thiện với dev mới, thích thấy WIP |
| **r/IndieGaming**, **r/playmygame** | Người chơi thật |
| **Discord Godot chính thức** | Kênh `#showcase` |
| **itch.io community / jam** | Tham gia jam là cách nhanh nhất có người chơi |
| **Twitter/X, Bluesky** với `#screenshotsaturday`, `#godot` | Cần build audience lâu dài |
| **Bạn bè, đồng nghiệp** | Feedback thẳng thắn nhất, nhưng thiên vị |

### Cách hỏi feedback hữu ích

❌ *"Game mình hay không?"* → nhận về "hay lắm!" (vô ích)

✅ Hỏi cụ thể:

- "Bạn kẹt ở đâu, và trong bao lâu?"
- "Có chỗ nào bạn không biết phải làm gì tiếp?"
- "Bạn có đọc hết hội thoại hay bấm bỏ qua? Chỗ nào bấm bỏ qua?"
- "Điều khiển có cảm giác nặng/nhẹ/đúng?"
- "Bạn chơi hết bao lâu?"
- "Nếu bỏ dở, bỏ ở phút thứ mấy và vì sao?"

Tốt nhất: **ngồi cạnh và im lặng xem họ chơi.** Đừng gợi ý gì. Ghi lại mọi chỗ họ do dự. Dữ liệu này quý hơn 20 comment "cool game".

---

## 10.10 Roadmap sau MVP

Sau khi có game 5 phút chạy được và có feedback, thứ tự mở rộng theo giá trị/công sức:

### Tầng 1 — Polish (giá trị cao, công sức thấp) — làm trước

| Việc | Công sức | Tác động |
|---|---|---|
| Sửa các chỗ tester bị kẹt | 1–3 ngày | ⭐⭐⭐⭐⭐ |
| Thêm hiệu ứng feedback (screen shake nhẹ, particle khi nhặt, flash khi mở cửa) | 2 ngày | ⭐⭐⭐⭐ |
| Tinh chỉnh camera + tốc độ đi | 1 ngày | ⭐⭐⭐⭐ |
| Thêm ambience (sóng, gió) | Nửa ngày | ⭐⭐⭐⭐ |
| Cải thiện title screen | 1 ngày | ⭐⭐⭐ |
| Thêm `!` trên đầu NPC có việc mới | Nửa ngày | ⭐⭐⭐ |
| Chuyển màn có hiệu ứng đẹp hơn | Nửa ngày | ⭐⭐ |

### Tầng 2 — Nội dung (giá trị cao, công sức trung bình)

| Việc | Công sức |
|---|---|
| Thêm 1 khu vực mới (thị trấn thứ 2 / hầm sâu hơn) | 1–2 tuần |
| Thêm 2–3 câu đố | 1 tuần |
| Thêm 5 NPC có thoại thật | 3 ngày |
| Sổ tay ghi manh mối (giải quyết vấn đề "quên manh mối") | 3 ngày |
| Nhiều slot save + menu chọn slot | 2 ngày |
| Achievement / collectible | 3 ngày |

### Tầng 3 — Hệ thống (công sức cao, cân nhắc kỹ)

| Việc | Công sức | Có nên? |
|---|---|---|
| Localization (Việt/Anh) | 1 tuần | ✅ Nếu muốn khán giả quốc tế. Godot có `TranslationServer` + file CSV |
| Combat | 2–4 tuần | ⚠️ Đổi genre. Chỉ làm nếu playtest cho thấy game thiếu thứ này |
| Day/night cycle | 1 tuần | ⚠️ Đẹp nhưng ít tác động gameplay |
| Nhiều nhân vật chơi được | 2–3 tuần | ⚠️ Nhân đôi công art |
| Mobile port | 2 tuần | ⚠️ Cần redesign UI (10.5) |
| Steam release | 1–2 tuần + $100 | ✅ Nếu game đủ dài (≥ 1 giờ) và có người muốn mua |

### Nguyên tắc mở rộng

> **Đừng thêm hệ thống mới khi hệ thống hiện có chưa hoàn thiện.**

Một game 5 phút **hoàn chỉnh và mượt** tốt hơn một game 30 phút **rời rạc và đầy bug**. Người chơi tha thứ cho game ngắn; không tha thứ cho game vỡ.

### Khi nào nên dừng project này và làm cái mới

Dấu hiệu nên dừng (và đó là quyết định hợp lý, không phải thất bại):

- Bạn đã học được điều muốn học (Godot, 2.5D, workflow AI) → mục tiêu đã đạt
- Playtest cho thấy ý tưởng cốt lõi không vui (không phải "thiếu content", mà "cốt lõi không vui")
- Codebase đã rối tới mức thêm tính năng mất gấp 3 thời gian bình thường
- Bạn hết hứng thú và đã 2 tuần không mở project

Làm xong **một** game nhỏ và phát hành nó có giá trị hơn làm dở 5 game lớn. Nếu game này xong rồi, **hãy phát hành và làm cái tiếp theo** — game thứ hai của bạn sẽ tốt gấp nhiều lần.

---

## 10.11 Bài tập

1. Chạy hết checklist 10.1. Ghi lại bạn tìm được mấy vấn đề.
2. Export Windows (hoặc OS của bạn). Copy sang thư mục khác, chạy. Test full playthrough.
3. Export Web với `Thread Support = Off`. Test bằng `python3 -m http.server`. Kiểm: audio có phát? save có lưu sau F5 reload?
4. Kiểm cụ thể vấn đề `ItemDB` sau export (10.1). Nếu gặp → chuyển sang `ItemDatabase` resource.
5. Đo size build. Nếu > 60MB, tìm file nặng nhất và xử lý.
6. Làm GIF preview 8 giây bằng ffmpeg với `flags=neighbor`. So sánh với `flags=bilinear` để thấy khác biệt.
7. Tạo trang itch.io ở chế độ **Draft**, điền đủ checklist 10.8. Gửi link draft cho 1 người bạn xem trước.
8. Đưa game cho 3 người chơi. Ngồi cạnh, **im lặng**. Ghi lại mọi chỗ họ do dự > 10 giây.
9. Dựa trên feedback, viết roadmap tầng 1 của **chính bạn** — 5 việc, xếp theo giá trị/công sức.
10. Public game. Post lên r/godot. Trả lời mọi comment.

---

## 10.12 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Export báo "Export templates not found" | Chưa cài templates | `Editor → Manage Export Templates` |
| Bản export crash ngay khi mở | Main Scene sai, hoặc autoload lỗi | Chạy bản export từ terminal để thấy log: `./game.exe` trong cmd |
| Bản export thiếu asset | Filter loại trừ quá rộng, hoặc asset load bằng đường dẫn động | Kiểm `Filters to exclude`; dùng `preload`/tham chiếu resource thay vì string path |
| Inventory trống sau export | `DirAccess` quét `res://` trong PCK | Dùng `ItemDatabase` resource (10.1) |
| Chạy được ở editor, lỗi ở export: "file not found" | Viết hoa/thường đường dẫn | Đường dẫn phải khớp **chính xác** chữ. Linux/web phân biệt hoa thường |
| Web: trang trắng | Mở file trực tiếp thay vì qua HTTP server | Dùng `python3 -m http.server` |
| Web: lỗi `SharedArrayBuffer is not defined` | Export với threads nhưng host thiếu COOP/COEP header | Export lại với `Thread Support = Off`, hoặc bật tùy chọn tương ứng trên host |
| Web: không có tiếng | Browser chặn autoplay | Thêm màn hình "Bấm để chơi" |
| Web: save mất khi reload | Chế độ ẩn danh, hoặc browser xóa storage | Không sửa được — cảnh báo người chơi trên trang game |
| Web: load rất lâu | Build to | Loại trừ file thừa, nén nhạc, thêm loading screen |
| Web: lag trên điện thoại | Bộ nhớ/GPU hạn chế | Giảm số đèn, tắt glow, giảm kích thước texture |
| Pixel art bị mờ trên itch embed | Iframe scale không nguyên | Đặt embed size là bội số của base (960×540 hoặc 1280×720) |
| Boot splash logo bị mờ | `Use Filter` đang bật | Tắt `Use Filter` trong Boot Splash |
| macOS: "app bị hỏng, không mở được" | Chưa code-sign / notarize | Hướng dẫn chuột phải → Open; hoặc mua Developer account |
| `.exe` dùng icon Godot | Chưa cấu hình rcedit | Editor Settings → Export → Windows → Rcedit |
| Android build lỗi Gradle | JDK sai version, SDK thiếu | Kiểm đúng JDK version cho bản Godot bạn dùng; cài lại Android Build Template |
| Sprite pixel bị nhiễu màu sau export | VRAM texture compression | Đặt import Compress Mode `Lossless` cho sprite pixel |
| Game chạy 200 FPS, quạt kêu to | Không giới hạn FPS | `Engine.max_fps = 60` hoặc bật V-Sync trong Project Settings |
| Debug menu hiện trong bản release | Không bọc `OS.is_debug_build()` | Bọc lại, export lại |
