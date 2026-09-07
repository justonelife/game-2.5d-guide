# 09 — Workflow làm game Godot với AI

> Chương dày nhất của tài liệu. Đọc **sớm**, dùng **liên tục**.
>
> Mục tiêu: bạn dùng AI như một **lập trình viên junior nhanh, kiến thức rộng, không có ký ức, và đôi khi tự tin sai**. Nếu bạn quản lý được một người như vậy, bạn sẽ đi rất nhanh. Nếu không, bạn sẽ có 3000 dòng code không ai hiểu và một game không chạy.

---

## 9.1 Mô hình tư duy đúng về AI trong làm game

### AI **không** phải cái gì

| Ngộ nhận | Thực tế |
|---|---|
| "AI làm game hộ tôi" | AI viết được từng hệ thống. Nó **không** biết game của bạn có vui hay không |
| "Tôi không cần học Godot" | Bạn cần đủ hiểu để **đọc** code và **biết nó sai chỗ nào**. Không cần viết từ đầu, cần đọc được |
| "AI biết Godot 4 rất rõ" | AI biết Godot rất rộng nhưng **trộn lẫn Godot 3 và 4**, và trộn cả API của các bản 4.x khác nhau |
| "Code AI chạy tức là đúng" | Code chạy ≠ đúng thiết kế. Đây là loại bug đắt nhất |
| "Prompt càng dài càng tốt" | Prompt **cụ thể** tốt hơn prompt **dài** |

### AI **là** cái gì

Một cộng sự có đặc tính rất cụ thể:

| Đặc tính | Hệ quả cho workflow |
|---|---|
| **Rất nhanh ở boilerplate** | Giao nó viết inventory/save/dialog/UI — những thứ đã có mẫu chuẩn trên đời |
| **Không có ký ức giữa các session** | Bạn phải viết context ra file (`AGENTS.md`). Đây là việc quan trọng nhất chương này |
| **Không chạy được game của bạn** | Nó **không thấy** game bị lag, sprite bị mờ, cảm giác điều khiển nặng. Bạn là mắt và tay của nó |
| **Tự tin ngay cả khi sai** | Bạn phải verify. Không có cách nào bỏ bước này |
| **Rất giỏi giải thích** | Dùng nó để **học**: "giải thích tại sao `move_and_slide` cần gọi cuối `_physics_process`" |
| **Xu hướng over-engineer** | Nó sẽ đề nghị state machine 5 class cho một cái cửa. Bạn phải nói "đơn giản hơn" |
| **Đọc file rất nhanh** | Trong Claude Code, hãy để nó **đọc code hiện có** trước khi viết. Đừng dán code vào chat |

### Chia việc theo "ai giỏi cái gì"

```
        AI GIỎI                          BẠN GIỎI
   ┌──────────────────┐            ┌──────────────────┐
   │ Boilerplate      │            │ Game feel        │
   │ Cấu trúc dữ liệu │            │ Level design     │
   │ Parse JSON       │            │ Cân bằng độ khó  │
   │ UI layout code   │            │ Cái gì VUI       │
   │ Refactor máy móc │            │ Ưu tiên scope    │
   │ Giải thích API   │            │ Nghệ thuật       │
   │ Viết test        │            │ Quyết định cuối  │
   │ Sinh dữ liệu     │            │ Test thật        │
   └──────────────────┘            └──────────────────┘
              │                             │
              └──────────► GAME ◄───────────┘
```

**Ranh giới cứng**: mọi quyết định về *cảm giác* và *thiết kế* là của bạn. Mọi việc *thi công theo spec* giao được cho AI.

---

## 9.2 Ba chế độ làm việc — biết chọn đúng chế độ

| Chế độ | Cách làm | Dùng cho | Rủi ro |
|---|---|---|---|
| **Autopilot** — giao task, để nó tự làm nhiều file | "Viết cả hệ thống inventory theo AGENTS.md" | Boilerplate đã có spec rõ, code mới hoàn toàn | Cao: có thể đi lệch kiến trúc, sinh nhiều file khó review |
| **Copilot** — giao 1 file, 1 hàm | "Trong `player.gd`, thêm hàm `_push_bodies()` như spec dưới" | Sửa code đã có, thêm tính năng nhỏ | Thấp |
| **Pair** — hỏi/thảo luận trước, code sau | "Có 2 cách làm save system. Phân tích trade-off, đừng viết code" | Quyết định kiến trúc, debug khó, học | Rất thấp, chậm hơn |

### Luật chọn chế độ

```
Code mới, spec rõ, ít ràng buộc với code cũ   → Autopilot
Sửa code đã chạy được                          → Copilot
Chưa biết nên làm thế nào                      → Pair TRƯỚC, rồi Autopilot/Copilot
Đang có bug không hiểu                         → Pair
Sắp đổi kiến trúc                              → Pair (bắt buộc)
```

Lỗi phổ biến nhất của người mới: dùng **Autopilot khi chưa biết mình muốn gì**. Kết quả là AI quyết định kiến trúc thay bạn, và bạn phát hiện điều đó 2 tuần sau.

---

## 9.3 Thiết lập Claude Code cho project Godot

### 9.3.1 Cấu trúc file context

```
project-root/
├── AGENTS.md              ← context chính (mẫu ở 9.4). CLAUDE.md cũng được nhận
├── docs/
│   ├── DESIGN.md          ← design doc (bảng thi công chương 07)
│   ├── ARCHITECTURE.md    ← sơ đồ hệ thống + quy ước
│   └── TASKS.md           ← task đang làm, đã xong (thay cho ký ức của AI)
└── ...
```

Claude Code tự đọc `AGENTS.md` / `CLAUDE.md` ở gốc project mỗi session. Đây là cách bạn "cấp ký ức" cho nó.

### 9.3.2 Những gì AI **không** làm được với Godot (giới hạn cứng)

Nói thẳng trước để bạn không mất thời gian:

| Việc | Vì sao không |
|---|---|
| **Mở editor Godot, kéo thả node** | Không có GUI |
| **Chạy game và xem kết quả** | Không thấy hình ảnh game |
| **Cảm nhận game feel** | Không chơi được |
| **Sửa file `.tscn` an toàn** | `.tscn` là text nhưng có `id` tham chiếu chéo — sửa tay dễ **hỏng scene**. ⚠️ Xem 9.3.3 |
| **Import asset** | Import là hành động trong editor |
| **Debug lỗi runtime không có log** | Cần bạn dán log |

Vì vậy vòng lặp thực tế **luôn** là: **AI viết code → bạn dựng scene trong editor → bạn chạy → bạn dán kết quả → AI sửa.**

### 9.3.3 Quy tắc về file `.tscn` và `.tres`

Đây là bẫy nghiêm trọng, cần luật rõ:

| File | AI được làm gì |
|---|---|
| `.gd` (script) | ✅ Đọc, viết, sửa tự do |
| `.json` (dialog, data) | ✅ Đọc, viết, sửa tự do |
| `.md` (docs) | ✅ Tự do |
| `.tres` (Resource dữ liệu như ItemData) | ⚠️ **Chỉ được tạo mới**, không sửa file có sẵn (dễ làm hỏng `[ext_resource]` id) |
| `.tscn` (scene) | ❌ **KHÔNG sửa.** Thay vào đó: AI **mô tả cây scene** bằng text, bạn dựng trong editor |
| `project.godot` | ❌ Không sửa trực tiếp. AI **liệt kê setting cần đổi**, bạn đổi trong Project Settings |
| `.godot/` | ❌ Tuyệt đối không |

> Vì sao không cho sửa `.tscn`: format có dòng `[ext_resource type="Script" uid="uid://xxxx" path="..." id="1_abc"]`. Các `id` và `uid` tham chiếu chéo nhau. AI sửa tay rất dễ tạo scene mở lên là mất node, hoặc Godot báo "Failed loading resource". Rủi ro cao, lợi ích thấp — **cấm luôn cho gọn**.
>
> Ngoại lệ: nếu bạn cần AI sinh scene, hãy để nó viết một **script `@tool` tạo node bằng code** rồi bạn chạy script đó trong editor. An toàn hơn nhiều.

### 9.3.4 Permission / allowlist gợi ý

Cho phép AI chạy các lệnh đọc mà không phải hỏi mỗi lần (giảm ma sát rất nhiều):

```
Cho phép:  git status, git diff, git log, git show
           grep, rg, find, ls, cat, head, tail, wc
           godot --headless --check-only <file>      (kiểm tra syntax GDScript)

Hỏi trước: git commit, git push, git checkout
           rm, mv (bất kỳ)
           ghi vào .tscn / .tres / project.godot
```

Lệnh kiểm syntax cực hữu ích, cho AI tự verify:

```bash
# Kiểm syntax 1 script mà không mở editor
godot --headless --check-only --script scripts/actors/player.gd

# Import lại project + kiểm mọi thứ (chậm hơn, dùng khi đổi nhiều file)
godot --headless --quit
```

> **Kiểm tra lại**: cờ CLI của Godot đổi giữa các bản (`--check-only`, `--script`, `--quit-after`). Chạy `godot --help` trên bản bạn dùng để lấy cờ đúng, rồi ghi lệnh đúng đó vào `AGENTS.md`.

---

## 9.4 `AGENTS.md` — template đầy đủ (copy thẳng)

Đây là tài sản có giá trị nhất trong chương này. Nó là "bộ nhớ dài hạn" của AI về project bạn.

````markdown
# AGENTS.md — Ngọn Đèn Cá Nục

## 0. Đọc cái này trước khi viết bất kỳ dòng code nào

Project này là game phiêu lưu 2.5D pixel art bằng **Godot 4.4** (GDScript, KHÔNG C#).
Trước khi sửa gì: đọc `docs/ARCHITECTURE.md` và file bạn định sửa. Đừng đoán nội dung file.

## 1. Ràng buộc kỹ thuật (KHÔNG được vi phạm)

- **Godot 4.4**, GDScript, renderer **Compatibility** (nhắm web).
  Nếu bạn không chắc một API có tồn tại ở 4.4, **nói ra** thay vì đoán.
- **Không dùng C#, không dùng GDNative/GDExtension.**
- **Không thêm addon/plugin bên thứ ba** mà không hỏi tôi trước.
- 1 world unit = 1 mét = **16 pixel art**.
- Base resolution **320×180**, stretch mode `viewport`, scale mode `integer`.
- Nhân vật là `CharacterBody3D`; sprite là `AnimatedSprite3D` billboard `FIXED_Y`,
  `alpha_cut = ALPHA_CUT_DISCARD`, `texture_filter = NEAREST`, `shaded = false`.
- Camera: `Camera3D` **orthographic**, `size = 11.25`, pitch -30°, yaw 0°.

## 2. Bạn ĐƯỢC và KHÔNG ĐƯỢC sửa file gì

| Được sửa | Không được sửa |
|---|---|
| `scripts/**/*.gd` | `**/*.tscn` — hãy MÔ TẢ cây scene bằng text, tôi dựng trong editor |
| `data/**/*.json` | `project.godot` — hãy LIỆT KÊ setting cần đổi |
| `docs/**/*.md` | `.godot/**` |
| Tạo mới `data/items/*.tres` | Sửa `.tres` đã có |

## 3. Kiến trúc — đây là hợp đồng, đừng phá

### Autoload (thứ tự đúng như liệt kê)
| Tên | File | Vai trò |
|---|---|---|
| `GameState` | `scripts/autoload/game_state.gd` | **Nguồn sự thật duy nhất** cho flags + inventory + level hiện tại |
| `SceneRouter` | `scripts/autoload/scene_router.gd` | Chuyển màn, fade, đặt player vào spawn |
| `Dialogue` | `scripts/autoload/dialogue.gd` | Chạy hội thoại từ file JSON |
| `SaveSystem` | `scripts/autoload/save_system.gd` | Ghi/đọc save JSON ở `user://saves/` |
| `Audio` | `scripts/autoload/audio.gd` | BGM crossfade + SFX pool |
| `HUD` | `scenes/ui/hud.tscn` | Prompt tương tác, toast, tiêu đề khu vực |

### Luật kiến trúc bất di bất dịch
1. **Chỉ `GameState` giữ dữ liệu tiến trình.** Không autoload nào khác được có state cần save.
2. **Mọi tiến trình cốt truyện là boolean flag** trong `GameState.flags`. Không tạo hệ quest riêng.
3. **Node không gọi trực tiếp node khác qua `get_node("../../X")`.** Dùng signal hoặc autoload.
4. **Mọi vật tương tác kế thừa `Interactable`** (`scripts/systems/interactable.gd`) và override `interact(by)`.
5. **Mọi level kế thừa `LevelBase`** và có node con `Spawns` chứa các `Marker3D`.
6. **Player nằm trong từng level** (không phải trong Main) — để test riêng level bằng F6 được.
7. **Khóa input dùng `GameState.push_input_lock()` / `pop_input_lock()`** (đếm, không phải boolean).
8. **Save chỉ lưu flags + inventory + level + spawn.** Không lưu vị trí chi tiết của world.

### Collision layer (3D Physics)
| Bit | Tên | Dùng cho |
|---|---|---|
| 1 | world | sàn, tường |
| 2 | player | nhân vật |
| 3 | interactable | Area3D của NPC/item/cửa |
| 4 | solid_prop | thùng, prop chắn đường |
| 5 | trigger | vùng chuyển màn |

## 4. Quy ước code

- File & thư mục: `snake_case`. Node: `PascalCase`. Class: `class_name PascalCase`.
- **Luôn dùng static typing**: `var x: int = 0`, `func f(a: String) -> void:`.
- `@export` cho mọi thứ designer cần tinh chỉnh (tốc độ, thời gian, đường dẫn file).
- **Comment bằng tiếng Việt**, giải thích **TẠI SAO** không phải **CÁI GÌ**.
  ✅ `# Đếm thay vì boolean: dialog + cutscene có thể khóa input cùng lúc`
  ❌ `# Tăng biến lock_count lên 1`
- Không dùng `get_node()` trong `_process`/`_physics_process`. Cache vào `@onready`.
- Không magic number. Đưa vào `const` hoặc `@export`.
- Signal đặt tên ở dạng quá khứ/sự kiện: `flag_changed`, `dialogue_finished`.
- Hàm private tiền tố `_`.

## 5. Cách trả lời tôi

Mặc định, khi tôi giao một task:
1. **Nếu task > 1 file hoặc > ~80 dòng: mô tả kế hoạch trước, chờ tôi OK.** Đừng viết code luôn.
2. Khi viết code: cho **đường dẫn file đầy đủ** ở đầu mỗi block.
3. Nếu task cần đổi scene: cho **cây scene dạng text** (tên node, kiểu node, property cần set).
4. Nếu task cần đổi Project Settings: **liệt kê** `mục → setting → giá trị`.
5. Kết thúc bằng **"Cách test"**: 3–5 bước cụ thể tôi làm trong editor để verify.
6. **Nêu rõ chỗ bạn không chắc** ("`alpha_cut` enum có thể tên khác ở 4.4, kiểm tra F1").

## 6. Nói KHÔNG với những thứ này

- ❌ Đề nghị đổi engine / đổi ngôn ngữ / thêm framework.
- ❌ Tạo abstraction cho thứ chỉ dùng 1 lần. Game này nhỏ; **thà lặp code còn hơn thêm 3 lớp trừu tượng**.
- ❌ Viết hệ thống tôi chưa yêu cầu ("tôi thêm luôn hệ combat cho bạn").
- ❌ Sửa file ngoài phạm vi task. Nếu thấy bug ở chỗ khác: **báo, đừng sửa**.
- ❌ Xóa comment của tôi.
- ❌ Refactor "cho đẹp" khi tôi chỉ hỏi thêm 1 tính năng.

## 7. Trạng thái hiện tại

Xem `docs/TASKS.md` để biết cái gì đã xong / đang làm.
Xem `docs/DESIGN.md` để biết game này là gì và 3 câu đố hoạt động thế nào.

## 8. Lệnh hữu ích

```bash
# Kiểm syntax 1 script (không mở editor)
godot --headless --check-only --script scripts/actors/player.gd

# Xem diff trước khi tôi commit
git diff --stat && git diff
```
(Cờ CLI có thể khác giữa bản Godot — nếu lỗi, chạy `godot --help`.)

## 9. Danh sách flag chính thức (đừng tự thêm flag mới mà không hỏi)

`met_bay`, `has_fish`, `gave_fish`, `has_rusty_key`, `gate_open`,
`heard_song`, `crate_on_plate`, `torch_puzzle_done`, `lighthouse_lit`

Flag tiền tố `_` là flag tạm (tín hiệu từ dialog về code), bị lọc khi save.
````

### Vì sao template này hiệu quả

| Mục | Giải quyết vấn đề gì |
|---|---|
| §1 Ràng buộc | AI đề xuất C#/Godot 3 API/addon lạ |
| §2 File được sửa | AI làm hỏng `.tscn` |
| §3 Kiến trúc | AI tạo hệ thống song song với hệ thống đã có |
| §4 Quy ước | Code AI trông "không cùng project" |
| §5 Cách trả lời | AI viết 400 dòng khi bạn chỉ muốn xem kế hoạch |
| §6 Nói KHÔNG | Over-engineering + scope creep |
| §7 Trạng thái | AI không có ký ức giữa session |
| §9 Flag list | AI tự bịa flag `player_has_key` khi đã có `has_rusty_key` |

**Cập nhật `AGENTS.md` khi kiến trúc đổi.** File này cũ đi thì nó bắt đầu gây hại thay vì giúp.

### `docs/TASKS.md` — bộ nhớ giữa các session

```markdown
# TASKS

## Đang làm
- [ ] Câu đố 3 (thứ tự đuốc) — đã có `torch.gd`, thiếu `torch_puzzle.gd`
      Ghi chú: đã quyết định reset ngay ở bước sai đầu tiên, không chờ hết 3.

## Xong
- [x] GameState + flags + inventory (commit a1b2c3)
- [x] Dialogue system + npc_bay.json (commit d4e5f6)
- [x] ItemPickup + InventoryUI (commit 789abc)
- [x] LockedGate + Portal town↔dungeon (commit def012)

## Quyết định đã chốt (đừng đề xuất lại)
- Save = JSON, KHÔNG dùng Resource (lý do: rủi ro code execution khi load save lạ)
- Player nằm trong từng level, không phải trong Main (lý do: test level bằng F6)
- Không có combat trong MVP
- Camera orthographic, không perspective (lý do: pixel đều)

## Bug đã biết, chưa sửa
- Đẩy thùng vào góc P1 thì hơi khó kéo ra (chấp nhận được, có nút reset)
- Toast và area title có thể chồng nhau nếu vào màn rồi nhặt item ngay
```

Mục **"Quyết định đã chốt"** cực kỳ quan trọng — nó ngăn AI đề xuất lại cùng một thứ bạn đã bác bỏ 3 lần.

---

## 9.5 Cách giao việc: giải phẫu một prompt tốt

### Công thức 6 phần

```
1. NGỮ CẢNH   — file nào, hệ thống nào, đang ở đâu trong project
2. MỤC TIÊU   — cái gì phải hoạt động sau khi xong (mô tả bằng hành vi)
3. RÀNG BUỘC  — không được làm gì, phải dùng gì có sẵn
4. ĐỊNH DẠNG  — muốn nhận gì: code / kế hoạch / cây scene / phân tích
5. TIÊU CHÍ   — làm sao biết là xong
6. KHÔNG CHẮC — chỗ nào bạn muốn nó nói ra thay vì đoán
```

### So sánh prompt

**❌ Prompt tệ:**

```
làm hệ thống inventory cho game godot
```

Vấn đề: không biết Godot mấy, không biết kiến trúc đã có, không biết UI thế nào, không biết item là gì. AI sẽ **bịa toàn bộ** và bạn nhận về code không khớp project.

**⚠️ Prompt tạm được:**

```
Làm hệ thống inventory cho game Godot 4.4 của tôi. Item lưu trong Dictionary.
Có UI dạng lưới. Đọc AGENTS.md trước.
```

Tốt hơn, nhưng vẫn thiếu: bao nhiêu ô? có dùng item không? ai gọi mở túi? lưu vào đâu?

**✅ Prompt tốt:**

```
NGỮ CẢNH
Đọc AGENTS.md và scripts/autoload/game_state.gd trước.
GameState đã có: inventory Dictionary {item_id: count}, các hàm add_item /
remove_item / has_item / get_item_count, và signal inventory_changed.
ItemData resource đã có ở scripts/systems/item_data.gd (id, display_name,
description, icon, usable, quest_item).

MỤC TIÊU
Viết UI túi đồ:
- Nhấn action "inventory" mở/đóng. Nhấn "cancel" đóng.
- Không mở được khi đang thoại (Dialogue.is_running()).
- Lưới 5 cột, luôn hiện tối thiểu 20 ô (ô trống là Button disabled).
- Click 1 ô -> panel bên phải hiện display_name + description.
- Nút "Dùng" chỉ hiện khi item.usable == true.
- Mở túi phải khóa input player (push_input_lock), đóng thì pop.
- Điều khiển được bằng bàn phím/gamepad (grab_focus ô đầu khi mở).

RÀNG BUỘC
- Chỉ tạo 1 file mới: scripts/ui/inventory_ui.gd
- KHÔNG sửa game_state.gd. Nếu bạn thấy cần sửa, nói ra thay vì tự sửa.
- Dùng preload cho scene ô item; không dùng get_node trong _process.
- Static typing đầy đủ, comment tiếng Việt giải thích tại sao.

ĐỊNH DẠNG
1. Cây scene dạng text cho inventory_ui.tscn và item_slot.tscn
   (tên node, kiểu node, property quan trọng cần set trong Inspector)
2. Code inventory_ui.gd đầy đủ
3. Cách test: 4-5 bước

TIÊU CHÍ XONG
Nhặt cá ở bến -> bấm I -> thấy icon cá + số lượng -> click -> thấy mô tả ->
bấm I lần nữa đóng -> di chuyển được lại.

CHỖ KHÔNG CHẮC
Nếu tên property/enum nào bạn không chắc ở Godot 4.4 (ví dụ TextureRect
stretch mode, GridContainer columns), ghi rõ "kiểm tra lại" thay vì đoán.
```

Prompt này dài, nhưng bạn viết **một lần** và nhận về code dùng được ngay. So với 4 vòng sửa qua lại thì nhanh hơn nhiều.

### Rút ngắn: dùng `AGENTS.md` làm chỗ chứa phần lặp

Sau khi có `AGENTS.md` tốt, prompt hằng ngày ngắn lại:

```
Đọc AGENTS.md.

Task: UI túi đồ (scripts/ui/inventory_ui.gd + cây scene).
Hành vi: [8 gạch đầu dòng như trên]
Tiêu chí xong: nhặt cá -> bấm I -> thấy icon -> click thấy mô tả -> đóng -> đi được.
```

Đây là lý do `AGENTS.md` đáng đầu tư 1 giờ: nó tiết kiệm 20 dòng trong **mọi** prompt sau đó.

### 6 prompt mẫu cho 6 hệ thống của game này

#### (a) Dialogue system

```
Đọc AGENTS.md + scripts/autoload/game_state.gd + data/dialogs/npc_bay.json.

Task: viết Dialogue autoload (scripts/autoload/dialogue.gd) chạy hội thoại từ JSON.

Format JSON (đã chốt, đừng đổi):
mỗi key là node id, value có: conditions[], speaker, portrait, lines[],
choices[], set_flags[], clear_flags[], give_item, consume_item, next.
"conditions" là mảng tên flag; tiền tố "!" nghĩa là phải KHÔNG có flag đó.

Hành vi:
- start(json_path, entry_id="") là async (await được từ ngoài).
- Nếu entry_id rỗng: chọn node thỏa điều kiện có NHIỀU condition nhất
  (để node đặc thù thắng node mặc định).
- Hiện từng dòng trong lines[], chờ người chơi bấm mới sang dòng tiếp.
- Sau lines[], nếu có choices[]: lọc bỏ choice thiếu require_item hoặc
  thiếu conditions, rồi hiện menu, chờ chọn.
- Áp dụng set_flags/give_item/consume_item cho cả node và choice đã chọn.
- Khóa input bằng GameState.push_input_lock/pop_input_lock.
- Phát signal dialogue_started / dialogue_finished.

RÀNG BUỘC
- UI tự đăng ký qua Dialogue.register_ui(node); Dialogue KHÔNG tự get_node UI.
- Xử lý lỗi: file không tồn tại, JSON sai, node id không tồn tại -> push_error,
  không crash, và PHẢI pop_input_lock trước khi return.

ĐỊNH DẠNG: code + interface mà UI phải implement (danh sách hàm + signature).
```

Chú ý dòng cuối của RÀNG BUỘC: *"PHẢI pop_input_lock trước khi return"*. Đây là loại chi tiết AI hay quên và gây bug "thoại xong không điều khiển được". **Nói trước rẻ hơn debug sau.**

#### (b) Save system

```
Đọc AGENTS.md + game_state.gd.

Task: SaveSystem autoload, format JSON ở user://saves/save_<slot>.json.

Quyết định đã chốt (đừng đề xuất Resource): dùng JSON vì load .tres từ file
người dùng có rủi ro thực thi code.

Hành vi:
- save_game(slot) -> bool. Ghi {version, saved_at, state} với state = GameState.to_dict().
- LỌC BỎ mọi flag có tiền tố "_" trước khi ghi (đó là flag tạm).
- load_game(slot) -> bool. Parse, check version, gọi GameState.from_dict,
  rồi SceneRouter.goto_level(level, spawn).
- get_slot_info(slot) -> Dictionary cho menu chọn slot: saved_at, level,
  playtime_text ("MM:SS"), item_count. KHÔNG load game.
- has_save(slot), delete_save(slot).
- _migrate(payload, from_version) -> Dictionary: hiện tại chỉ khung sẵn với
  comment hướng dẫn tôi thêm bước migrate về sau.

RÀNG BUỘC
- Mọi lỗi I/O -> push_error + return false, không crash.
- Tạo thư mục saves ở _ready.
- Không sửa game_state.gd.

ĐỊNH DẠNG: code + ví dụ file JSON output thật (dán nội dung mẫu).
```

Yêu cầu "ví dụ file JSON output thật" rất hữu ích: bạn đọc nó trong 5 giây và biết ngay logic có đúng không, không cần đọc hết code.

#### (c) Camera rig

```
Đọc AGENTS.md.

Task: scripts/actors/camera_rig.gd — camera follow cho pixel 2.5D.

Hành vi:
- @export target: Node3D. Nếu null, tìm node đầu tiên trong group "player".
- Follow trong _process (KHÔNG _physics_process) với lerp độc lập framerate:
  t = 1 - exp(-follow_speed * delta). Giải thích trong comment tại sao
  không dùng lerp(a, b, speed*delta).
- @export target_offset: Vector3 (mặc định (0,1,0)) để ngắm ngực không ngắm chân.
- @export snap_to_pixel: bool — làm tròn vị trí về bội số của 1/16 unit.
- @export use_limits + limit_min/limit_max: clamp x và z.

RÀNG BUỘC
- Không tự set rotation của rig (pitch/yaw do node con giữ, tôi set trong editor).
- Không tự tạo Camera3D bằng code.

ĐỊNH DẠNG: cây scene (CameraRig > Yaw > Pitch > Camera3D với property cụ thể)
+ code + giải thích ngắn về giới hạn của snap_to_pixel khi camera nghiêng 30°.
```

Câu cuối buộc AI nói ra **giới hạn** thay vì bán cho bạn giải pháp hoàn hảo không tồn tại.

#### (d) Puzzle (state machine nhỏ)

```
Đọc AGENTS.md + scripts/props/torch.gd.

Task: scripts/props/torch_puzzle.gd — câu đố thứ tự 3 đuốc.

Thiết kế đã chốt:
- Gắn vào Node3D cha có 3 node con kiểu Torch tên: TorchSea, TorchMoon, TorchStone.
- @export correct_order: Array[String] = ["TorchSea","TorchMoon","TorchStone"]
- Torch phát signal `lit` khi được thắp.
- Reset NGAY ở bước sai đầu tiên (không chờ đủ 3) — quyết định thiết kế,
  để người chơi biết chính xác bước nào sai.
- Sai: SFX "puzzle_fail" + toast + tắt cả 3 đuốc + xóa sequence.
- Đúng đủ 3: set flag "torch_puzzle_done", SFX "puzzle_solved", toast, mở door.
- @export door: Node3D. Nếu door có method open(animate: bool) thì gọi,
  không thì door.visible = false.
- Nếu flag đã có từ save: mở door ngay lúc _ready, KHÔNG connect signal.

RÀNG BUỘC
- Không sửa torch.gd.
- Dùng get_children() + check `is Torch`, không hardcode get_node("TorchSea").

ĐỊNH DẠNG: chỉ code. Ngắn gọn — file này không nên quá 60 dòng.
```

Dòng *"không nên quá 60 dòng"* là công cụ chống over-engineering rất hiệu quả.

#### (e) Refactor (dùng khi code đã chạy nhưng lộn xộn)

```
Đọc scripts/actors/player.gd.

Vấn đề: Input.get_vector đang bị gọi 2 lần mỗi frame (_read_move_input và
_update_animation). Muốn cache 1 lần.

Task: refactor CHỈ chuyện đó.
- Thêm biến _raw_input: Vector2, gán 1 lần ở đầu _physics_process.
- Hai hàm kia dùng biến đó.

RÀNG BUỘC TUYỆT ĐỐI
- KHÔNG đổi hành vi game. Kết quả chạy phải giống hệt trước.
- KHÔNG đổi tên hàm/biến khác.
- KHÔNG "cải tiến" thêm bất cứ thứ gì, kể cả nếu bạn thấy code khác dở.
- KHÔNG xóa comment.

ĐỊNH DẠNG: chỉ diff (dòng nào đổi thành gì). Đừng in lại cả file.
```

**"Chỉ diff"** là kỹ thuật quan trọng: nó khiến scope creep hiện ra ngay lập tức. Nếu diff có 40 dòng cho một task 5 dòng → AI đã tự ý làm thêm.

#### (f) Sinh dữ liệu / nội dung

```
Đọc docs/DESIGN.md phần "Bà Tám" + data/dialogs/npc_bay.json (làm mẫu format).

Task: viết data/dialogs/npc_tam.json.

Nội dung: bà Tám hát bài ca là manh mối cho câu đố đuốc.
Lời bài: "Biển gọi trước, trăng đáp sau, đá nằm im cuối cùng."

Cần ĐỦ 3 trạng thái:
1. Lần đầu (conditions: ["!heard_song"]) — hát bài, set flag heard_song
2. Nhắc lại (conditions: ["heard_song", "!torch_puzzle_done"]) — hát lại ngắn hơn
3. Sau khi xong (conditions: ["torch_puzzle_done"]) — vui, nói về thuyền về

RÀNG BUỘC VĂN PHONG
- Mỗi dòng trong "lines" tối đa 90 ký tự (hộp thoại 320px chỉ chứa được thế).
- Giọng bà Tám: vòng vo, hay hát, dùng "hồi đó", "bà không hiểu".
- KHÔNG cho bà Tám nói thẳng đáp án dạng "thắp Sea rồi Moon rồi Stone".
- KHÔNG có câu chào hỏi kiểu "Xin chào cháu!".
- Tiếng Việt tự nhiên, không dịch máy.

ĐỊNH DẠNG: chỉ nội dung JSON, valid JSON, không markdown fence bên trong.
```

Sinh nội dung là chỗ AI **rất mạnh** — và ràng buộc số ký tự làm output dùng được ngay không phải sửa.

---

## 9.6 Vòng lặp thực tế: Generate → Read → Test → Fix

Đây là quy trình bạn sẽ chạy hàng trăm lần. Học cho thuộc.

```
┌─────────────────────────────────────────────────────────────┐
│  1. PLAN      Bạn quyết định làm gì. Chia thành task ≤ 1 file│
│               (Nếu chưa rõ: chế độ Pair, hỏi trước)         │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GENERATE  AI viết code + cây scene + cách test          │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  3. READ      ⚠️ BẠN ĐỌC CODE. Không bỏ bước này.            │
│               Checklist ở 9.6.2                              │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  4. WIRE      Bạn dựng scene trong editor theo mô tả        │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  5. TEST      Chạy F5/F6. Làm đúng "Cách test". Ghi kết quả  │
└────────────────────────┬────────────────────────────────────┘
                         ▼
              ┌──────────┴──────────┐
        Chạy đúng?               Lỗi/sai?
              │                       │
              ▼                       ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│ 6. COMMIT            │  │ 6'. FIX — dán log + hành vi thực │
│    git commit ngay    │  │     tế + hành vi mong đợi        │
│    Cập nhật TASKS.md  │  │     → về bước 2                  │
└──────────────────────┘  └──────────────────────────────────┘
```

### 9.6.1 Vì sao "READ" là bước không thể bỏ

Ba loại bug chỉ phát hiện được bằng cách đọc:

| Loại | Ví dụ thật | Test có bắt được không? |
|---|---|---|
| **Đúng hành vi, sai kiến trúc** | AI tạo `var inventory = {}` trong `inventory_ui.gd` thay vì đọc `GameState.inventory` → UI hiển thị đúng, nhưng save không lưu | ❌ Chỉ phát hiện sau khi save/load — có thể 2 tuần sau |
| **Hoạt động trong trường hợp bạn test, sai ở trường hợp khác** | `remove_item` không check số lượng → trừ thành số âm khi dùng item không có | ❌ Test hạnh phúc-path không bắt được |
| **Đúng nhưng sẽ vỡ khi mở rộng** | Hardcode `get_node("../../Player")` → vỡ khi đổi cấu trúc level | ❌ |

Đọc code AI mất **2–5 phút**. Debug bug kiến trúc mất **2–5 giờ**. Tỉ lệ này không đổi.

### 9.6.2 Checklist đọc code AI (dùng mỗi lần)

**Vòng 1 — quét nhanh (30 giây):**

- [ ] Số dòng có hợp lý với task? (task nhỏ mà 300 dòng → đọc kỹ, có scope creep)
- [ ] Có file nào bị sửa mà không nằm trong task? (`git diff --stat`)
- [ ] Có import/preload gì lạ? (addon bạn không cài, class không tồn tại)
- [ ] Có `TODO` / `# implement this` bỏ dở?

**Vòng 2 — kiến trúc (2 phút):**

- [ ] Có tạo **state song song** với `GameState`? (biến giữ dữ liệu tiến trình ở chỗ khác)
- [ ] Có gọi `get_node("../..")` hay đường dẫn tuyệt đối cứng?
- [ ] Có bỏ qua class base có sẵn? (không kế thừa `Interactable`/`LevelBase`)
- [ ] Có thêm abstraction cho thứ dùng 1 lần?
- [ ] Signal có được disconnect ở chỗ cần? (node bị free mà signal còn nối → lỗi)
- [ ] `push_input_lock` có `pop` ở **mọi** đường return?

**Vòng 3 — API (2 phút):**

- [ ] Tên node/class có thật ở Godot 4? (`AnimatedSprite3D` ✓, `AnimatedSprite` ✗ — đó là Godot 3)
- [ ] Tên hàm: `move_and_slide()` **không tham số** ở Godot 4 (Godot 3 có tham số velocity)
- [ ] Signal connect: `signal.connect(callable)` (Godot 4), **không** `connect("signal", self, "method")` (Godot 3)
- [ ] `Tween`: `create_tween()` (Godot 4), **không** `Tween` node hay `interpolate_property` (Godot 3)
- [ ] `instance()` → phải là `instantiate()` ở Godot 4
- [ ] `OS.get_ticks_msec()` → `Time.get_ticks_msec()` ở Godot 4
- [ ] `yield` → `await` ở Godot 4
- [ ] `export var` → `@export var` ở Godot 4

**Vòng 4 — logic (3 phút):**

- [ ] Chia cho 0, index âm, mảng rỗng có được xử lý?
- [ ] `null` check ở chỗ node có thể chưa tồn tại?
- [ ] Vòng lặp `while` có điều kiện thoát đảm bảo?
- [ ] `await` trong `_ready` (làm `_ready` return sớm — thường là bug)?
- [ ] Số magic không giải thích?

### 9.6.3 Cách báo lỗi cho AI (quan trọng hơn bạn nghĩ)

**❌ Báo lỗi tệ:**

```
không chạy
```

AI sẽ đoán và bạn mất 3 vòng.

**✅ Báo lỗi tốt — công thức 5 phần:**

```
1. TÔI LÀM GÌ:      Bấm F5, đi tới NPC ông Bảy, nhấn E
2. MONG ĐỢI:        Hộp thoại hiện ra với dòng đầu
3. THỰC TẾ:         Hộp thoại hiện nhưng chữ hiện hết ngay lập tức,
                    không có typewriter. Nhấn E lần nữa thì đóng luôn
                    hộp thoại thay vì sang dòng 2.
4. LOG:             (dán nguyên văn từ panel Output/Debugger)
   E 0:00:03:0451   dialogue_box.gd:52 @ show_line(): Invalid access to
   property or key 'visible_characters' on a base object of type 'Nil'
     <C++ Source>   core/variant/variant_setget.cpp:XXX
     <Stack Trace>  dialogue_box.gd:52 @ show_line()
                    dialogue.gd:88 @ _run_node()
5. TÔI ĐÃ THỬ:      In ra text_label ở _ready thì thấy <null>.
                    Đường dẫn node trong scene của tôi là
                    DialogueBox/Panel/Text (không phải DialogueBox/Text).
```

Phần 5 thường là cái giải quyết vấn đề. Ở ví dụ trên, bug là `@onready var text_label = $Text` nhưng scene thật có `Text` nằm trong `Panel`. AI không thể biết điều này — **bạn** phải nói.

> **Luôn dán log nguyên văn.** Đừng viết lại bằng lời. Stack trace cho biết chính xác dòng nào, và AI đọc nó tốt.

### 9.6.4 Khi AI sửa 3 lần vẫn không được

Dấu hiệu: mỗi vòng nó sửa một chỗ khác, bug chuyển chỗ chứ không mất.

Nguyên nhân thường là **AI đang thiếu một thông tin cốt lõi** — thường là cấu trúc scene thật của bạn.

Cách phá vòng lặp:

```
Dừng sửa. Ta đang đoán vòng vòng.

Thay vì sửa tiếp, hãy làm 3 việc:
1. Liệt kê MỌI giả định bạn đang dựa vào về scene/code của tôi.
2. Với mỗi giả định, cho tôi 1 dòng code print() để tôi kiểm chứng.
3. Đừng viết fix nào cho tới khi tôi trả về kết quả print.
```

Prompt này gần như luôn tìm ra vấn đề trong 1 vòng. Nó buộc AI phơi ra giả định sai thay vì tiếp tục sửa mù.

Một biến thể hữu ích khác:

```
Giải thích cho tôi luồng chạy chính xác, từ lúc tôi nhấn E tới lúc chữ hiện
ra: hàm nào gọi hàm nào, ở frame nào. Đừng viết code. Tôi muốn tìm chỗ giả
định của bạn khác thực tế.
```

---

## 9.7 Việc nào giao AI, việc nào tự làm

Bảng này dựa trên trải nghiệm thực tế làm game Godot với AI. Đọc kỹ cột "Ghi chú" — đó là chỗ có giá trị.

| Việc | Giao AI? | Ghi chú |
|---|---|---|
| **Code — nên giao** | | |
| Inventory (logic + UI) | ✅ Rất tốt | Bài toán kinh điển, AI làm gần như hoàn hảo. Chỉ cần kiểm nó dùng `GameState` không tự giữ state |
| Save/load JSON | ✅ Rất tốt | Nhớ ràng buộc "lọc flag tạm" và "pop lock ở mọi return" |
| Dialogue system + parser JSON | ✅ Rất tốt | Cho nó format JSON trước, đừng để nó tự thiết kế format |
| UI menu, settings, slider | ✅ Rất tốt | Cây scene UI thì bạn phải dựng tay |
| Parse/validate dữ liệu | ✅ Rất tốt | |
| Boilerplate class (Interactable, LevelBase) | ✅ Tốt | |
| State machine nhỏ (puzzle) | ✅ Tốt | Giới hạn số dòng để nó không làm to |
| Refactor máy móc (đổi tên, tách hàm) | ✅ Tốt | Bắt buộc dùng "chỉ diff" |
| Viết test (GUT/GdUnit) | ✅ Tốt | Xem 9.13 |
| Debug logic (có log) | ✅ Tốt | Chất lượng phụ thuộc hoàn toàn vào log bạn dán |
| **Code — cẩn thận** | | |
| Camera feel (follow, shake, zoom) | ⚠️ Được, phải tự tune | AI viết đúng công thức; **con số** phải bạn tune bằng cách chơi |
| Player controller | ⚠️ Được, phải tự tune | Cùng lý do. `acceleration`, `friction` là quyết định cảm giác |
| Shader | ⚠️ Trung bình | AI viết shader chạy được nhưng hay sai chi tiết Godot 4 shading language. Test từng bước |
| Physics tuning | ⚠️ Trung bình | Nó không cảm nhận được "thùng đẩy nặng quá" |
| Tối ưu performance | ⚠️ Trung bình | Nó tối ưu chỗ không cần. **Đo trước** rồi mới giao |
| **Code — đừng giao** | | |
| Quyết định kiến trúc lớn | ❌ | Dùng chế độ Pair để **thảo luận**, nhưng bạn quyết |
| "Làm game hộ tôi" | ❌ | Không có spec = AI bịa spec = bạn nhận về game của nó |
| Sửa `.tscn` | ❌ | Xem 9.3.3 |
| **Asset** | | |
| Concept art / mood board | ✅ Rất tốt | Xem chương 03 |
| Prop / tile pixel art | ⚠️ Được, cần hậu kỳ | Xem 3.7 |
| Sprite nhân vật + animation | ❌ Kém | Tự vẽ. Xem 3.4 |
| Nhạc chiptune (audio) | ❌ Kém | Xem 8.3 |
| Lý thuyết nhạc (chord, melody dạng note) | ✅ Rất tốt | Xem 8.3 — đây là cách dùng AI cho nhạc |
| SFX | ❌ Không cần AI | jsfxr nhanh hơn, xem 8.2 |
| **Nội dung** | | |
| Dialog NPC (theo bảng giọng của bạn) | ✅ Rất tốt | Ràng buộc số ký tự + giọng nhân vật |
| Tên item, mô tả item | ✅ Rất tốt | |
| Sinh 20 câu thoại vặt cho NPC phụ | ✅ Rất tốt | Chỗ AI tiết kiệm thời gian rõ nhất |
| Cốt truyện chính | ⚠️ Được, làm với bạn | AI cho ra cốt truyện "trung bình an toàn". Ý tưởng gốc là của bạn |
| Thiết kế câu đố | ⚠️ Cẩn thận | AI đề xuất puzzle kinh điển; nó **không** biết puzzle của bạn có bị moon-logic không |
| Dịch sang tiếng Anh (localize) | ✅ Tốt | |
| **Tài liệu & quy trình** | | |
| Viết `docs/`, README, CREDITS | ✅ Rất tốt | |
| Commit message | ✅ Tốt | |
| Sinh checklist test | ✅ Tốt | |
| **Playtest** | | |
| Chơi game, đánh giá có vui không | ❌ Không thể | Việc này chỉ người làm được |

### Quy tắc rút ra

> **Giao AI những việc có "đúng/sai" rõ ràng. Tự làm những việc có "hay/dở".**

---

## 9.8 Bẫy thường gặp — catalog đầy đủ

Mỗi bẫy: dấu hiệu → nguyên nhân → cách phòng.

### Bẫy 1 — AI bịa API / trộn Godot 3 vào Godot 4

**Dấu hiệu**: code không compile, hoặc Godot báo `Invalid call. Nonexistent function`.

**Bảng đối chiếu Godot 3 → Godot 4** (những chỗ AI sai nhiều nhất):

| Godot 3 (AI hay viết) | Godot 4 (đúng) |
|---|---|
| `export var speed = 5` | `@export var speed: float = 5.0` |
| `onready var x = $X` | `@onready var x: Node = $X` |
| `yield(get_tree(), "idle_frame")` | `await get_tree().process_frame` |
| `connect("pressed", self, "_on_pressed")` | `pressed.connect(_on_pressed)` |
| `emit_signal("my_signal", a)` | `my_signal.emit(a)` (cách cũ vẫn chạy nhưng đừng dùng) |
| `PackedScene.instance()` | `PackedScene.instantiate()` |
| `move_and_slide(velocity)` | `velocity = ...` rồi `move_and_slide()` (không tham số) |
| `KinematicBody2D/3D` | `CharacterBody2D/3D` |
| `Spatial` | `Node3D` |
| `AnimatedSprite` | `AnimatedSprite2D` / `AnimatedSprite3D` |
| `Sprite` | `Sprite2D` |
| `OS.get_ticks_msec()` | `Time.get_ticks_msec()` |
| `OS.window_size` | `DisplayServer.window_get_size()` / `get_window().size` |
| `Tween` node + `interpolate_property` | `create_tween().tween_property(...)` |
| `linear2db` / `db2linear` | `linear_to_db` / `db_to_linear` |
| `File.new()` + `file.open()` | `FileAccess.open(path, FileAccess.READ)` |
| `Directory.new()` | `DirAccess.open()` |
| `JSON.parse(text).result` | `JSON.parse_string(text)` |
| `deg2rad` / `rad2deg` | `deg_to_rad` / `rad_to_deg` |
| `is_action_just_pressed` | (giống nhau — cái này an toàn) |
| `VisualServer` | `RenderingServer` |
| `.tscn` `instance` property | (khác hoàn toàn, đừng sửa tay) |

**Cách phòng:**

1. Ghi rõ bản Godot trong `AGENTS.md` (§1)
2. Thêm vào prompt: *"Nếu không chắc API tồn tại ở Godot 4.4, nói ra thay vì đoán."*
3. Cho AI chạy `godot --headless --check-only` để tự kiểm syntax
4. Bạn tra `F1` trong editor — **nguồn sự thật duy nhất là bản Godot bạn cài**

> Lưu ý: `--check-only` chỉ bắt **lỗi syntax**, không bắt "hàm không tồn tại" (đó là lỗi runtime trong GDScript). Nên vẫn phải chạy game.

### Bẫy 2 — Code chạy nhưng sai thiết kế

Đây là bẫy **đắt nhất**, vì test không bắt được.

**Ví dụ thật 1**: bạn nhờ làm inventory UI. AI viết:

```gdscript
# ❌ AI viết — chạy đúng, sai kiến trúc
var items: Dictionary = {}          # state riêng!

func add_to_display(id: String) -> void:
	items[id] = items.get(id, 0) + 1
	_refresh()
```

UI hiển thị đúng khi bạn test. Nhưng `GameState.inventory` không được cập nhật → **save không lưu item**. Bạn phát hiện 2 tuần sau khi test save/load.

**Cách phòng**: `AGENTS.md` §3 luật 1 (*"chỉ GameState giữ dữ liệu"*) + vòng 2 của checklist đọc code.

**Ví dụ thật 2**: cổng khóa mở đúng, nhưng AI không đọc flag trong `_ready` → quay lại màn thì cổng đóng lại. Test "mở cổng" pass, test "quay lại màn" không ai nghĩ tới.

**Cách phòng**: mỗi khi làm thứ có state, tự hỏi 3 câu:

- [ ] **Reload level** thì nó có giữ đúng trạng thái? (đọc flag trong `_ready`)
- [ ] **Save → load** thì nó có giữ đúng? (state có nằm trong `GameState.to_dict()`?)
- [ ] **Làm lại lần 2** thì có bị lặp? (item nhặt 2 lần, flag set 2 lần, signal nối 2 lần)

Ba câu này bắt được ~80% bug "chạy nhưng sai".

### Bẫy 3 — Scope creep im lặng

**Dấu hiệu**: bạn nhờ thêm 1 hàm, `git diff --stat` cho 6 file đổi.

**Ví dụ**: bạn nhờ *"thêm sprint cho player"*. AI trả về: sprint + hệ thống stamina + UI thanh stamina + hồi stamina khi đứng yên + SFX hết hơi. Bạn không yêu cầu 4 thứ sau.

Vấn đề không phải là nó dở — mà là bạn giờ có **4 hệ thống chưa test, chưa thiết kế**, và game của bạn có stamina mà design doc không nói gì về stamina.

**Cách phòng:**

1. `AGENTS.md` §6: *"Không viết hệ thống tôi chưa yêu cầu."*
2. Luôn chạy `git diff --stat` **trước** khi đọc code
3. Yêu cầu "chỉ diff" cho task nhỏ
4. Câu chốt trong prompt: *"Nếu bạn thấy nên làm thêm gì, LIỆT KÊ ở cuối, đừng làm."*

### Bẫy 4 — Over-engineering

**Dấu hiệu**: một cái cửa có 4 file: `door.gd`, `door_state.gd`, `door_state_machine.gd`, `i_openable.gd`.

AI được train trên codebase enterprise. Nó mang tư duy đó vào game 5 phút của bạn.

**Cách phòng:**

- Nói rõ quy mô: *"Game này ~15 file script tổng cộng. Đừng thêm abstraction."*
- Giới hạn dòng: *"File này không nên quá 60 dòng."*
- Câu thần chú trong `AGENTS.md`: *"Thà lặp code còn hơn thêm 3 lớp trừu tượng."*
- Khi nhận về thiết kế phức tạp: *"Làm lại đơn giản nhất có thể. Chấp nhận lặp code."*

**Ngưỡng thực tế**: nếu một abstraction chỉ có **1 người dùng**, nó chưa cần tồn tại. Chờ tới người dùng thứ 3 hãy trừu tượng hóa.

### Bẫy 5 — AI phá kiến trúc khi thêm tính năng

**Dấu hiệu**: nó thêm tính năng đúng, nhưng bằng cách tạo autoload mới / bypass hệ thống có sẵn.

**Ví dụ**: bạn nhờ *"thêm hệ thống đèn dầu hết dầu dần"*. AI tạo autoload `LanternManager` giữ `oil_amount` → giờ có **2** chỗ giữ state, và save không biết về `oil_amount`.

**Cách phòng — kỹ thuật "constraint prompting"**:

```
RÀNG BUỘC KIẾN TRÚC
- KHÔNG thêm autoload mới.
- Mọi state phải nằm trong GameState (thêm field vào GameState.to_dict/from_dict
  nếu cần, và NÓI CHO TÔI BIẾT bạn thêm field gì).
- Nếu bạn nghĩ cần autoload mới, DỪNG và giải thích tại sao trước khi code.
```

Câu cuối là quan trọng nhất: nó cho AI một **đường thoát hợp lệ** (hỏi) thay vì buộc nó tự quyết.

### Bẫy 6 — Xung đột version giữa các câu trả lời

**Dấu hiệu**: session 1 AI dùng `Tween`, session 2 dùng `AnimationPlayer`, session 3 dùng `lerp` trong `_process` — cho cùng loại hiệu ứng.

Không sai, nhưng codebase của bạn thành ba trường phái.

**Cách phòng**: ghi quyết định vào `AGENTS.md`:

```markdown
## Quy ước đã chốt về animation
- Chuyển động UI (fade, slide, scale): dùng `create_tween()`
- Animation frame sprite: dùng `AnimatedSprite3D` + `SpriteFrames`
- Chuỗi hành động phức tạp (cutscene, có SFX + di chuyển + đổi frame): `AnimationPlayer`
- Follow camera: `lerp` trong `_process` với `1 - exp(-k*dt)`
```

### Bẫy 7 — AI không biết cấu trúc scene thật của bạn

Đây là nguyên nhân **số 1** của bug "code đúng nhưng null reference".

AI viết `@onready var label: Label = $Text` vì đó là cây scene nó **đề xuất**. Bạn dựng scene hơi khác (`$Panel/Text`). Crash.

**Cách phòng — chủ động cung cấp cây scene thật:**

Trong Godot: chọn node root → chuột phải → **Copy Node Path** cho từng node cần. Hoặc nhanh hơn, dán cây scene bằng cách xuất từ script:

```gdscript
# scripts/util/dump_tree.gd — chạy tạm để lấy cây scene dán cho AI
extends Node

func _ready() -> void:
	_dump(self, 0)

func _dump(node: Node, depth: int) -> void:
	print("%s%s (%s)" % ["  ".repeat(depth), node.name, node.get_class()])
	for child in node.get_children():
		_dump(child, depth + 1)
```

Gắn tạm vào root level, chạy F6, copy output từ panel Output → dán vào chat. **30 giây, tiết kiệm 3 vòng debug.**

Hoặc thêm vào `AGENTS.md` một mục "cây scene hiện tại" và cập nhật khi đổi.

### Bẫy 8 — Signal nối nhiều lần

**Dấu hiệu**: hộp thoại hiện 2 lần, item cộng 2 lần, SFX phát trùng.

Nguyên nhân: `connect` được gọi mỗi lần `_ready` (level reload) mà không disconnect, hoặc AI nối signal trong `_process`.

**Cách phòng**:

```gdscript
# ✅ An toàn: kiểm tra trước khi nối
if not GameState.flag_changed.is_connected(_on_flag_changed):
	GameState.flag_changed.connect(_on_flag_changed)

# ✅ Hoặc dùng cờ ONE_SHOT khi chỉ cần 1 lần
some_signal.connect(_handler, CONNECT_ONE_SHOT)
```

Thêm vào checklist đọc code: *"signal nối ở đâu, có nối lặp được không?"*

### Bẫy 9 — `await` làm `_ready` trả về sớm

```gdscript
# ❌ Bug tinh vi
func _ready() -> void:
	await get_tree().process_frame     # _ready TRẢ VỀ ngay tại đây!
	setup_stuff()                       # chạy sau, node khác đã tưởng bạn ready xong
```

Node khác gọi hàm của bạn giữa lúc `setup_stuff()` chưa chạy → crash hoặc state sai.

**Cách phòng**:

```gdscript
# ✅ Tách ra
func _ready() -> void:
	_deferred_setup.call_deferred()

func _deferred_setup() -> void:
	await get_tree().process_frame
	setup_stuff()
```

AI hay viết bản sai. Đưa cái này vào checklist.

### Bẫy 10 — Context bị "loãng" trong session dài

**Dấu hiệu**: sau 2 giờ chat, AI bắt đầu quên ràng buộc, dùng lại API cũ, đề xuất thứ bạn đã bác bỏ.

**Cách phòng**:

- Session mới cho mỗi hệ thống lớn (dialog xong → session mới cho inventory)
- Cập nhật `docs/TASKS.md` **trước khi** kết thúc session
- Đầu session mới: *"Đọc AGENTS.md và docs/TASKS.md."*
- Trong session dài, nhắc lại ràng buộc quan trọng khi thấy nó bắt đầu lệch

### Bẫy 11 — Tin lời AI về performance

**Dấu hiệu**: AI nói *"cách này nhanh hơn"* mà không có số.

Với game 8-bit 2.5D trên máy hiện đại, bạn có **thừa** performance. Đừng để AI dụ bạn tối ưu sớm.

**Cách phòng**: chỉ tối ưu khi có số đo. Panel `Debugger → Monitors` khi chạy game cho FPS, draw call, object count, memory. **Đo trước, tối ưu sau, đo lại.**

### Bẫy 12 — Đọc tài liệu Godot bằng AI thay vì đọc docs

AI **rất** hay nhớ sai chi tiết property. Với câu hỏi *"property X có giá trị nào?"* thì `F1` trong editor **luôn** đúng và mất 10 giây.

Dùng AI để hỏi *"tại sao"* và *"làm thế nào"*. Dùng F1 để hỏi *"tên gì"* và *"tham số gì"*.

---

## 9.9 Kỹ thuật giữ kiến trúc: prompt patterns

Bộ công cụ để AI không phá code của bạn.

### Pattern 1 — "Explain before code"

```
Trước khi viết code, trả lời 3 câu:
1. Bạn sẽ sửa/tạo những file nào?
2. Bạn sẽ thêm state ở đâu? (nếu có)
3. Có hệ thống nào đã tồn tại làm việc tương tự mà ta nên dùng lại?

Chờ tôi OK rồi mới code.
```

Dùng cho: mọi task > 1 file. Chi phí: 1 vòng chat. Lợi: bắt được lệch kiến trúc **trước khi** có code phải bỏ.

### Pattern 2 — "Diff only"

```
Trả về CHỈ những dòng thay đổi, dạng:

scripts/actors/player.gd
  dòng 23: THÊM     var _raw_input: Vector2 = Vector2.ZERO
  dòng 45: THAY THẾ  var raw := Input.get_vector(...)
           BẰNG      # dùng _raw_input đã cache

Đừng in lại cả file.
```

Dùng cho: sửa file đã chạy được. Lợi: scope creep hiện ra ngay.

### Pattern 3 — "Constraint list"

Dán nguyên khối này vào cuối prompt khi làm việc trên code đã có:

```
RÀNG BUỘC
- Không thêm autoload mới.
- Không sửa file nào ngoài [danh sách file].
- Không đổi signature của hàm public đã có.
- Không xóa/đổi comment hiện có.
- Không thêm dependency/addon.
- Nếu cần vi phạm bất kỳ điều trên: DỪNG, giải thích, chờ tôi quyết.
```

### Pattern 4 — "Budget"

```
Ngân sách: file này tối đa 80 dòng, tối đa 5 hàm public.
Nếu vượt, nghĩa là thiết kế sai — nói cho tôi biết thay vì viết dài.
```

Cực hiệu quả chống over-engineering. Con số bạn đặt theo cảm giác; sai thì AI sẽ nói.

### Pattern 5 — "Adversarial review"

Sau khi có code (kể cả code bạn tự viết):

```
Review đoạn code này như một reviewer khó tính. Tìm:
1. Bug logic (input biên, null, mảng rỗng, chia 0)
2. Vi phạm kiến trúc trong AGENTS.md
3. State không được save
4. Signal có thể nối lặp
5. API có thể không tồn tại ở Godot 4.4

Với mỗi vấn đề: nêu dòng, giải thích tại sao sai, đề xuất fix.
Nếu không tìm thấy vấn đề nào ở một hạng mục, nói "không có".
Đừng khen. Đừng đề xuất refactor thẩm mỹ.
```

Đây là một trong những cách dùng AI **giá trị nhất**. Nó rất giỏi tìm lỗi trong code có sẵn — giỏi hơn viết code mới không lỗi.

Mẹo mạnh hơn: chạy pattern này ở **session mới** (không có context của lúc viết code). Nó review "lạnh", ít bị thiên vị bởi lý lẽ đã dùng khi viết.

### Pattern 6 — "Two options"

Khi bạn chưa biết nên làm thế nào:

```
Tôi cần [mô tả vấn đề].

Cho tôi ĐÚNG 2 phương án khả thi (không phải 5). Với mỗi phương án:
- Cách hoạt động (3-4 câu)
- Số file phải tạo/sửa
- Trade-off thật (không phải "cả hai đều tốt")
- Cái nào bạn chọn cho game 5 phút, 15 file script, và TẠI SAO

Đừng viết code.
```

Ép AI đưa **khuyến nghị** thay vì liệt kê. Bạn vẫn quyết, nhưng có phân tích.

### Pattern 7 — "Test-first spec"

```
Trước khi code, viết danh sách 6-10 trường hợp test cho tính năng này,
bao gồm cả trường hợp biên và trường hợp sai.

Tôi sẽ xem list đó để kiểm bạn có hiểu đúng yêu cầu không.
Sau khi tôi OK, viết code thỏa mọi case.
```

Cực hiệu quả: nếu AI hiểu sai yêu cầu, nó lộ ra ở test list (rẻ) thay vì ở code (đắt).

### Pattern 8 — "Naive first"

```
Viết bản NGÂY THƠ nhất có thể trước. Không tối ưu, không abstraction,
không xử lý trường hợp chưa xảy ra. Chỉ cần chạy đúng cho luồng chính.

Tôi sẽ chạy thử rồi ta cải tiến sau nếu cần.
```

Dùng khi bạn đang khám phá. Code ngây thơ dễ đọc, dễ sửa, và **thường là đủ**.

---

## 9.10 AI cho asset: workflow thực tế

Chương 03 và 08 đã nói về chất lượng. Ở đây là **workflow**.

### 9.10.1 Vòng lặp asset

```
1. AI/bạn viết PROMPT chuẩn (chương 03 mục 3.6)
2. Gen 4-8 biến thể
3. LỌC: bỏ ngay cái nào lệch grid pixel (không sửa được)
4. Hậu kỳ: downscale nearest → quantize palette → clean tay
5. Import Godot: Nearest, Lossless, no Mipmaps
6. Đặt vào game, xem CẠNH các asset khác
7. Nếu "lạc đàn" → sửa hoặc bỏ
```

Bước 6 là bước người ta hay bỏ. Asset trông đẹp một mình có thể trông sai trong game.

### 9.10.2 Dùng Claude Code để quản lý asset pipeline

Đây là chỗ AI coding thật sự giúp cho asset (khác với AI vẽ):

**Việc 1 — viết script kiểm tra asset:**

```
Viết script Python (chạy ngoài Godot) kiểm tra thư mục art/:
- Liệt kê file PNG nào có > 32 màu (nghi là chưa quantize)
- Liệt kê file nào có pixel alpha nửa vời (0 < a < 255) — sẽ gây viền xấu
- Liệt kê file nào kích thước không phải bội số của 16
- Xuất bảng: tên file, kích thước, số màu, có alpha nửa vời

Dùng Pillow. In dạng bảng dễ đọc.
```

Script này bắt được ~90% lỗi asset trước khi bạn import. Rất đáng 10 phút.

**Việc 2 — batch quantize:**

```
Viết script Python quantize mọi PNG trong art/props/ về palette đọc từ
art/palette.gpl (format GIMP palette).
- Nearest color, KHÔNG dithering
- Giữ alpha binary (a < 128 -> 0, else 255)
- Ghi ra art/props_quantized/, giữ nguyên tên file
- In ra file nào bị đổi nhiều nhất (số pixel đổi màu) để tôi kiểm tay
```

**Việc 3 — sinh `SpriteFrames` bằng code:**

Vì AI không sửa được `.tres` an toàn, cho nó viết script `@tool`:

```
Viết script @tool tạo SpriteFrames từ sprite sheet theo layout của tôi:
- Sheet 6 cột × 8 hàng, mỗi frame 32x32
- Hàng 0: idle_down (4 frame, 5 fps, loop)
- Hàng 1: idle_up (4 frame, 5 fps, loop)
- Hàng 2: idle_side (4 frame, 5 fps, loop)
- Hàng 3: walk_down (6 frame, 10 fps, loop)
- Hàng 4: walk_up (6 frame, 10 fps, loop)
- Hàng 5: walk_side (6 frame, 10 fps, loop)
- Hàng 6: interact (3 frame, 12 fps, KHÔNG loop)
- Hàng 7: hurt (2 frame, 8 fps, KHÔNG loop)

Script chạy trong editor, đọc art/characters/hero.png, dùng AtlasTexture cho
từng frame, lưu ra art/characters/hero_frames.tres bằng ResourceSaver.

Cho tôi cả hướng dẫn chạy nó (Tools menu hay @export button?).
```

Cách này an toàn (AI viết `.gd`, không sửa `.tres`) và tái dùng được cho mọi nhân vật.

### 9.10.3 Prompt cho asset: bảng nhanh

| Cần gì | Tool | Prompt mẫu ở |
|---|---|---|
| Mood board | Midjourney / Claude image | 3.6.1 |
| Tile lặp | Retro Diffusion / SD+LoRA | 3.6.2 |
| Prop tĩnh | PixelLab / Retro Diffusion | 3.6.3 |
| Sprite nhân vật (1 frame để sửa tay) | PixelLab | 3.6.4 |
| Portrait hội thoại | PixelLab / SD | 3.6.5 |
| Icon inventory 16×16 | Tự vẽ (nhanh hơn) | — |
| Chord + melody | Claude (text) | 8.3 |
| SFX | jsfxr (không AI) | 8.2 |

---

## 9.11 AI cho nội dung: dialog, tên, mô tả

Đây là chỗ AI cho **giá trị cao nhất trên mỗi phút bạn bỏ ra** — cao hơn cả code.

### 9.11.1 Sinh dialog hàng loạt

```
Đọc docs/DESIGN.md.

Task: sinh data/dialogs/npc_villagers.json — thoại vặt cho 5 dân làng phụ.

Mỗi NPC 1 node dialog, 1-2 dòng, KHÔNG có choices, KHÔNG set flag.
Mục đích: làm thế giới có cảm giác sống, KHÔNG mang thông tin gameplay.

RÀNG BUỘC
- Mỗi dòng ≤ 90 ký tự.
- Mỗi NPC phải nói về MỘT trong: biển, cá, ngọn đèn tắt, thời tiết, người mất tích.
- 1 trong 5 NPC phải hài (nhẹ, không phá tone buồn).
- KHÔNG nói thẳng manh mối câu đố (đó là việc của bà Tám).
- Giọng: dân chài miền biển Việt Nam, dùng "chú", "cô", "bây", "hử".
- KHÔNG dùng câu chào. Bắt đầu bằng nội dung.

ĐỊNH DẠNG: valid JSON, cùng format npc_bay.json.
```

Loại việc này AI làm trong 20 giây, chất lượng dùng được sau khi bạn sửa 2–3 câu. Tự viết mất 30 phút.

### 9.11.2 Sinh biến thể (rất hữu ích)

```
Đây là câu thoại của ông Bảy khi cổng còn khóa:
"Ta giữ chìa khóa cổng hầm."

Viết 6 biến thể cùng nội dung nhưng khác sắc thái:
1. Cụt hơn
2. Ấm hơn (thương cháu)
3. Nghi ngờ (không tin cháu)
4. Mệt mỏi
5. Có chút hài
6. Bí ẩn (như biết gì đó không nói)

Mỗi biến thể ≤ 90 ký tự. Tiếng Việt tự nhiên.
```

Bạn chọn cái khớp giọng nhân vật nhất. Đây là cách dùng AI để **cải thiện chất lượng viết**, không chỉ tăng số lượng.

### 9.11.3 Kiểm duyệt nội dung AI — checklist

Nội dung AI sinh có mấy bệnh cố hữu. Kiểm mỗi lần:

- [ ] **Quá lịch sự / quá "an toàn"** — nhân vật nào cũng tử tế, không có góc cạnh
- [ ] **Giải thích quá nhiều** — nhân vật nói ra điều họ không nên biết, hoặc kể lại cốt truyện
- [ ] **Dài quá giới hạn ký tự** — đếm lại, đừng tin
- [ ] **Tiếng Việt hơi "dịch"** — cấu trúc câu Anh-Việt ("Tôi cần bạn giúp tôi lấy lại nó")
- [ ] **Mọi NPC nói giống nhau** — dấu hiệu bạn chưa cho bảng giọng nhân vật
- [ ] **Sáo ngữ fantasy** — "định mệnh", "ánh sáng cuối cùng", "kẻ được chọn"
- [ ] **JSON không valid** — chạy qua validator hoặc để Godot báo
- [ ] **Flag/item id sai chính tả** — sẽ chạy nhưng không có tác dụng, cực khó debug

Bệnh cuối là nguy hiểm nhất. Prompt phòng ngừa:

```
Danh sách flag hợp lệ DUY NHẤT: met_bay, has_fish, gave_fish, has_rusty_key,
gate_open, heard_song, crate_on_plate, torch_puzzle_done, lighthouse_lit

Danh sách item id hợp lệ DUY NHẤT: fish, rusty_key, lantern, salt_fire_1,
salt_fire_2, salt_fire_3

Nếu bạn cần một flag/item không có trong danh sách, DỪNG và hỏi tôi.
Đừng bịa tên mới.
```

Hoặc tốt hơn — viết validator:

```
Viết script Python validate mọi file trong data/dialogs/:
1. JSON valid
2. Mọi "next" trỏ tới node id tồn tại trong CÙNG file (hoặc rỗng)
3. Mọi flag trong conditions/set_flags/clear_flags nằm trong danh sách hợp lệ
   (đọc từ docs/FLAGS.txt, mỗi dòng 1 flag)
4. Mọi give_item/consume_item/require_item nằm trong danh sách item id
   (đọc từ tên file trong data/items/*.tres)
5. Mọi dòng trong "lines" ≤ 90 ký tự
6. Mọi "portrait" path tồn tại thật trên đĩa

In lỗi dạng: file:node_id: vấn đề. Exit code 1 nếu có lỗi.
```

Script này chạy trong 1 giây và bắt được cả một lớp bug im lặng. **Đáng làm ngay khi bạn có > 3 file dialog.**

---

## 9.12 Debug với AI

### 9.12.1 Ba loại lỗi và cách xử lý khác nhau

| Loại | Ví dụ | AI hữu ích? | Cách làm |
|---|---|---|---|
| **Lỗi có stack trace** | `Invalid access to property 'x' on a base object of type 'Nil'` | ✅ Rất | Dán nguyên văn log + code file đó |
| **Lỗi im lặng** (chạy, không crash, hành vi sai) | Cổng không mở dù có chìa | ⚠️ Vừa | Bạn phải thêm `print()` để tạo dữ liệu |
| **Lỗi cảm giác** (game feel) | Điều khiển nặng, camera giật | ❌ Ít | Bạn tune. AI chỉ giúp giải thích tham số |

### 9.12.2 Debug lỗi im lặng: tạo dữ liệu trước, hỏi sau

Với lỗi im lặng, đừng hỏi *"tại sao cổng không mở?"* — AI sẽ đoán. Hãy **tạo dữ liệu**:

```
Cổng không mở dù tôi có chìa. Không có lỗi trong Output.

Trước khi sửa gì, cho tôi một danh sách print() để chèn vào, đủ để xác định
chính xác chỗ luồng đi sai. Với mỗi print, nói rõ:
- chèn vào file nào, hàm nào, dòng nào (trước/sau câu lệnh gì)
- in ra cái gì
- kết quả kỳ vọng nếu mọi thứ đúng

Đừng sửa code. Tôi sẽ chạy rồi dán output cho bạn.
```

Kết quả bạn nhận về sẽ dạng:

```gdscript
# 1. locked_gate.gd, đầu interact(), trước mọi thứ
print("[GATE] interact called, open_flag=%s, has_flag=%s" % [open_flag, GameState.has_flag(open_flag)])
# Kỳ vọng: open_flag="gate_open", has_flag=false

# 2. locked_gate.gd, trong interact(), trước check item
print("[GATE] required_item=%s, has_item=%s, count=%d" % [required_item_id, GameState.has_item(required_item_id), GameState.get_item_count(required_item_id)])
# Kỳ vọng: required_item="rusty_key", has_item=true, count=1

# 3. game_state.gd, cuối add_item()
print("[STATE] add_item %s -> inventory=%s" % [item_id, inventory])
# Kỳ vọng: thấy rusty_key xuất hiện khi bạn nhận chìa từ ông Bảy
```

Bạn chạy, dán output. Trong ví dụ thật này, output cho thấy:

```
[STATE] add_item rusty_key -> inventory={ "fish": 1, "rusty_key": 1 }
[GATE] interact called, open_flag=gate_open, has_flag=false
[GATE] required_item=rusty-key, has_item=false, count=0
```

Bug hiện ra ngay: `required_item_id` trong Inspector là `rusty-key` (gạch ngang) chứ không phải `rusty_key` (gạch dưới). AI không bao giờ đoán được điều này — nhưng với dữ liệu thì thấy trong 1 giây.

> **Bài học**: 80% thời gian debug với AI nên dành cho việc **tạo dữ liệu**, không phải hỏi giả thuyết.

### 9.12.3 Mẫu print debug hữu ích

Cho AI viết sẵn một bộ debug helper (dùng suốt project):

```gdscript
# scripts/util/dbg.gd — autoload tên "Dbg"
extends Node

## Bật/tắt từng nhóm log. Tắt hết khi export.
const ENABLED := {
	"gate": true,
	"dialog": true,
	"state": true,
	"save": true,
	"puzzle": true,
	"audio": false,
}

func log_msg(channel: String, msg: String) -> void:
	if not ENABLED.get(channel, false):
		return
	print("[%s] %.2f %s" % [channel.to_upper(), Time.get_ticks_msec() / 1000.0, msg])


## In toàn bộ state — gán vào phím F3, bạn sẽ dùng liên tục.
func dump_state() -> void:
	print("═══ GAME STATE ═══")
	print("Level: %s (spawn: %s)" % [GameState.current_level_path, GameState.current_spawn])
	print("Playtime: %.1fs" % GameState.playtime)
	print("Input locked: %s" % GameState.is_input_locked())
	print("Flags (%d):" % GameState.flags.size())
	var flag_keys := GameState.flags.keys()
	flag_keys.sort()
	for k in flag_keys:
		print("  ✓ %s" % k)
	print("Inventory (%d):" % GameState.inventory.size())
	for k in GameState.inventory.keys():
		print("  • %s x%d" % [k, GameState.inventory[k]])
	print("══════════════════")


func _unhandled_input(event: InputEvent) -> void:
	if OS.is_debug_build() and event is InputEventKey and event.pressed:
		if (event as InputEventKey).keycode == KEY_F3:
			dump_state()
```

`OS.is_debug_build()` đảm bảo debug key không hoạt động trong bản release.

### 9.12.4 Debug cheat: nhảy trạng thái

Khi test câu đố 3, bạn không muốn chơi lại 4 phút mỗi lần. Cho AI viết cheat menu:

```
Viết scripts/util/debug_menu.gd — chỉ hoạt động khi OS.is_debug_build().

Bấm F4 mở/đóng một panel với các nút:
- "Set: đã có cá" -> add_item fish
- "Set: đã có chìa" -> add_item rusty_key + set gave_fish
- "Set: mở cổng" -> set gate_open
- "Set: nghe bài hát" -> set heard_song
- "Set: có đèn dầu" -> add_item lantern
- "Set: xong đố 2" -> set crate_on_plate
- "Nhảy tới P3" -> SceneRouter.goto_level("res://scenes/levels/dungeon_01.tscn", "spawn_p3")
- "Nhảy tới đỉnh" -> goto lighthouse_top
- "Xóa hết state" -> GameState.reset()
- "Dump state" -> Dbg.dump_state()

RÀNG BUỘC
- Tự tạo UI bằng code (Button trong VBoxContainer trong CanvasLayer),
  KHÔNG cần tôi dựng scene.
- Panel phải nằm trên mọi UI khác (layer cao).
- Không hoạt động trong bản release.
```

**Đây là một trong những thứ AI làm hộ có ROI cao nhất.** 15 phút của AI tiết kiệm hàng giờ test lặp lại của bạn. Làm nó **sớm**, đừng để tới lúc gần xong.

---

## 9.13 Test tự động với AI

Game khó test tự động hơn web/backend, nhưng **phần logic** thì test được và rất đáng.

### 9.13.1 Cái gì test được, cái gì không

| Test được | Không test được (phải chơi) |
|---|---|
| `GameState` flags/inventory logic | Cảm giác điều khiển |
| Parse dialog JSON + chọn node theo condition | Camera có mượt không |
| Save → load → so sánh state | Puzzle có vui không |
| `ItemDB` load đúng item | Sprite có đẹp không |
| Validate dữ liệu dialog | Pacing |
| Logic puzzle (thứ tự đúng/sai) | Âm thanh có khớp không |

### 9.13.2 Framework

| Framework | Ghi chú |
|---|---|
| **GUT** (Godot Unit Test) | Phổ biến nhất, AssetLib, cú pháp giống xUnit |
| **GdUnit4** | Hiện đại, có fluent assertion, tích hợp CI tốt |
| **Tự viết** | Với game nhỏ, một scene `tests.tscn` chạy loạt hàm `assert` là đủ |

Với game 5 phút này, **tự viết là đủ** — đừng thêm dependency.

### 9.13.3 Prompt viết test

```
Đọc scripts/autoload/game_state.gd.

Task: viết scenes/tests/test_game_state.tscn (mô tả cây) + scripts/tests/test_game_state.gd.
Không dùng framework ngoài — tự viết assert đơn giản, in PASS/FAIL, đếm tổng.

Test cases cần có:
1. set_flag rồi has_flag -> true
2. set_flag(x, false) rồi has_flag -> false, và flag KHÔNG còn trong dict
3. set_flag 2 lần cùng giá trị -> signal flag_changed chỉ bắn 1 lần
4. has_all_flags(["a", "!b"]) đúng trong cả 4 tổ hợp a/b
5. add_item rồi get_item_count -> đúng số
6. add_item(x, 0) và add_item(x, -1) -> không đổi gì
7. remove_item nhiều hơn số có -> trả false VÀ không trừ gì
8. remove_item đúng số -> trả true, item bị erase khỏi dict
9. push_input_lock 2 lần + pop 1 lần -> vẫn locked
10. push 2 + pop 2 -> unlocked, signal bắn đúng 1 lần cho mỗi lượt đổi
11. to_dict -> from_dict roundtrip: state giống hệt
12. reset() -> mọi thứ rỗng

RÀNG BUỘC
- Mỗi test phải gọi GameState.reset() ở đầu để độc lập.
- In rõ test nào fail và giá trị mong đợi vs thực tế.
- Cuối cùng in "X/12 PASS".
```

Test #3, #7, #9, #10 là những case AI thường **không** nghĩ tới nếu bạn không liệt kê — và chúng là chỗ có bug thật.

### 9.13.4 Chạy test không cần GUI

```bash
# Chạy scene test rồi tự thoát
godot --headless --quit-after 300 scenes/tests/test_game_state.tscn
```

Thêm vào cuối script test:

```gdscript
func _finish() -> void:
	print("%d/%d PASS" % [_passed, _total])
	if _passed < _total:
		# Exit code khác 0 để CI biết fail
		OS.set_exit_code(1)
	get_tree().quit()
```

> **Kiểm tra lại**: `--quit-after` nhận số **frame** ở một số bản Godot. Chạy `godot --help` để xem đúng. Nếu không có, gọi `get_tree().quit()` trong script như trên là chắc chắn nhất.

### 9.13.5 Test hồi quy cho save

Test đáng giá nhất trong game này:

```
Viết test: save/load roundtrip toàn diện.

1. Reset state
2. Set 5 flag khác nhau + thêm 3 item với số lượng khác nhau
3. Set current_level_path và current_spawn
4. Thêm 1 flag tạm tên "_temp_signal"
5. SaveSystem.save_game(99)
6. GameState.reset()
7. Đọc lại bằng cách parse file JSON trực tiếp (KHÔNG dùng load_game vì nó
   sẽ đổi scene) rồi GameState.from_dict
8. Assert: 5 flag đúng, 3 item đúng số lượng, level/spawn đúng
9. Assert: flag "_temp_signal" KHÔNG có trong file save (đã bị lọc)
10. Xóa save slot 99

Test này phải chạy được headless.
```

Case 9 là loại test bảo vệ một quyết định thiết kế. Nếu ai đó (kể cả AI trong session tương lai) sửa `save_game` và bỏ bước lọc, test sẽ fail ngay.

---

## 9.14 Quản lý context & session

### 9.14.1 Khi nào bắt đầu session mới

| Tình huống | Session mới? |
|---|---|
| Xong một hệ thống, sang hệ thống khác | ✅ Nên |
| AI bắt đầu quên ràng buộc / dùng API cũ | ✅ Bắt buộc |
| Đã sửa 4 vòng không xong | ✅ Nên (kèm mô tả lại vấn đề từ đầu) |
| Muốn review code "lạnh" | ✅ Bắt buộc |
| Đang giữa một task, mới sửa 2 vòng | ❌ Giữ session |
| Vừa dán log lỗi | ❌ Giữ session |

### 9.14.2 Quy trình đóng session (5 phút, tiết kiệm rất nhiều)

Trước khi kết thúc:

```
Ta sắp dừng ở đây. Hãy cập nhật docs/TASKS.md:
1. Đánh dấu xong những gì đã xong (kèm mô tả 1 dòng)
2. Ghi rõ đang làm dở cái gì và dở ở bước nào
3. Ghi mọi quyết định ta chốt trong session này vào mục "Quyết định đã chốt"
4. Ghi bug đã biết chưa sửa

Chỉ sửa TASKS.md, đừng sửa gì khác.
```

Session sau bạn chỉ cần: *"Đọc AGENTS.md và docs/TASKS.md. Tiếp tục từ chỗ đang dở."*

### 9.14.3 Chia task đúng kích cỡ

| Kích cỡ task | Ví dụ | Đánh giá |
|---|---|---|
| **Quá nhỏ** | "Thêm dấu chấm phẩy" | Tự làm nhanh hơn |
| **Vừa** ✅ | "Viết `inventory_ui.gd`" (1 file, ~150 dòng, spec rõ) | Điểm ngọt |
| **Vừa** ✅ | "Sửa bug cổng không mở, đây là log" | Điểm ngọt |
| **Hơi lớn** ⚠️ | "Viết cả hệ thống dialog: autoload + UI + 3 file JSON" | Chia thành 3 task |
| **Quá lớn** ❌ | "Làm hết chương 06" | AI sẽ đi lệch, bạn không review được |

Nguyên tắc: **một task = một thứ bạn có thể test trong 2 phút.**

### 9.14.4 Kiểu prompt "làm nhiều task" — dùng cẩn thận

Đôi khi bạn muốn giao một loạt:

```
Đây là 4 task ĐỘC LẬP. Làm lần lượt, sau mỗi task DỪNG và chờ tôi OK
trước khi sang task sau.

TASK 1: [...]
TASK 2: [...]
TASK 3: [...]
TASK 4: [...]

Bắt đầu từ task 1.
```

Câu "DỪNG và chờ" là quan trọng. Không có nó, bạn nhận về 4 task cùng lúc và không review nổi.

---

## 9.15 Git discipline khi làm với AI

Đây là **van an toàn** của bạn. AI có thể ghi sai file, xóa code bạn cần, hoặc đơn giản là làm ra thứ bạn muốn bỏ.

### Quy tắc

1. **Commit trước khi giao task cho AI.** Working tree phải sạch. Không có ngoại lệ.
2. **`git diff` trước khi commit code AI.** Đọc từng dòng đổi.
3. **Commit nhỏ, thường xuyên.** Một task = một commit.
4. **Không để AI commit.** Bạn commit, sau khi đọc.
5. **Branch cho việc mạo hiểm.** Đổi kiến trúc → `git checkout -b refactor-save`.

### Vòng lặp Git thực tế

```bash
# TRƯỚC khi giao task
git status                    # phải sạch
git log --oneline -3          # biết mình đang ở đâu

# ... AI làm việc ...

# SAU khi AI xong, TRƯỚC khi test
git diff --stat               # có file nào lạ không? scope creep?
git diff                      # đọc từng dòng

# Nếu thấy sai hoàn toàn -> bỏ hết, làm lại prompt
git checkout -- .

# Nếu ổn -> test trong Godot -> nếu pass:
git add -A
git commit -m "feat: hệ thống túi đồ (UI + logic hiển thị)"
```

### Commit message — nhờ AI viết

```
Đây là git diff của tôi:
[dán output git diff]

Viết commit message theo Conventional Commits:
- Dòng đầu ≤ 60 ký tự, tiếng Việt
- Body chỉ khi cần giải thích TẠI SAO (không mô tả lại code)
- prefix: feat/fix/refactor/docs/chore
```

### Khi AI làm hỏng thứ gì

```bash
# Xem chính xác nó đổi gì so với commit cuối
git diff HEAD

# Bỏ thay đổi ở 1 file cụ thể
git checkout -- scripts/actors/player.gd

# Bỏ hết
git checkout -- .

# Đã commit rồi nhưng muốn bỏ (chưa push)
git reset --hard HEAD~1

# Đã commit và muốn giữ lịch sử
git revert HEAD
```

> Nếu bạn chưa từng dùng Git: học **4 lệnh** là đủ để an toàn — `git status`, `git diff`, `git add -A && git commit -m "..."`, `git checkout -- .`. Đó là 30 phút học đổi lấy sự an tâm hoàn toàn khi làm việc với AI.

---

## 9.16 Chi phí & thời gian thực tế

### 9.16.1 AI tiết kiệm bao nhiêu — số thật

Dựa trên các hệ thống trong tài liệu này:

| Hệ thống | Tự viết (người mới) | Với AI | Tiết kiệm |
|---|---|---|---|
| `GameState` (flags + inventory) | 3–4h | 40 phút | ~85% |
| Dialogue system + UI typewriter | 8–12h | 2–3h | ~75% |
| Inventory UI | 5–6h | 1–1.5h | ~75% |
| Save/load JSON | 4–5h | 1h | ~80% |
| SceneRouter + fade | 3h | 45 phút | ~75% |
| Audio autoload | 3h | 40 phút | ~80% |
| Player controller | 4h | 1.5h + **2h tune** | ~10% (tune không giảm) |
| Camera rig | 2h | 30 phút + **1h tune** | ~25% |
| Debug menu | 2h | 20 phút | ~85% |
| Test suite | 4h | 45 phút | ~80% |
| **Pixel art nhân vật (35 frame)** | 20–30h | 20–30h | **~0%** |
| **Level design (2 map)** | 10–15h | 10–15h | **~0%** |
| **Puzzle design** | 5h | 4h | ~20% |
| **Playtest + iterate** | 10h | 10h | **~0%** |

**Tổng cho MVP**: từ ~90h xuống ~55h. Tiết kiệm **~40%**.

### 9.16.2 Chỗ AI làm bạn CHẬM HƠN

Trung thực: có những chỗ AI làm bạn chậm hơn tự làm.

| Tình huống | Vì sao chậm hơn |
|---|---|
| **Task cực nhỏ** (đổi 1 số, thêm 1 dòng) | Viết prompt lâu hơn tự sửa |
| **Bạn chưa biết mình muốn gì** | AI code sai hướng, bạn bỏ, làm lại. 3 vòng = 1 giờ mất |
| **Tune game feel** | Mỗi vòng phải: đổi số → chạy → cảm nhận. AI không thêm được gì. Tự kéo slider trong Inspector nhanh hơn |
| **Sửa scene** | AI không làm được, bạn vẫn phải làm tay, cộng thời gian đọc mô tả |
| **Debug lỗi cảm giác** ("camera hơi trễ") | Không mô tả được thành text cho AI |
| **Vẽ pixel art nhân vật** | Gen 8 lần vẫn không dùng được = 40 phút mất |
| **Bạn không đọc code nó viết** | Nợ kỹ thuật tích lại, tuần thứ 4 bạn trả gấp 3 |

**Dấu hiệu bạn đang dùng AI sai**: bạn không hiểu code trong project của mình. Khi đó dừng lại, đọc, hỏi AI giải thích, rồi đi tiếp.

### 9.16.3 Nguyên tắc phân bổ

```
Task có spec rõ + code thuần logic     → AI (tiết kiệm 75-85%)
Task cần cảm nhận                       → Tự làm (AI không giúp)
Task chưa rõ                            → Pair TRƯỚC (làm rõ), rồi AI
Task < 5 phút tự làm                    → Tự làm
```

---

## 9.17 Checklist trước khi merge code AI

In ra dán màn hình. Dùng mỗi lần.

```
□ 1.  git diff --stat: chỉ có file trong phạm vi task?
□ 2.  Đọc hết diff. Hiểu MỌI dòng? (nếu không -> hỏi AI giải thích trước khi merge)
□ 3.  Có state nào nằm ngoài GameState mà cần save không?
□ 4.  Có get_node("../..") hoặc path cứng nào không?
□ 5.  Signal: có nối lặp được không? Có disconnect ở chỗ cần?
□ 6.  push_input_lock có pop ở MỌI đường return (kể cả return sớm khi lỗi)?
□ 7.  API: có tên nào là Godot 3? (đối chiếu bảng 9.8 bẫy 1)
□ 8.  await trong _ready?
□ 9.  Magic number không giải thích?
□ 10. Chạy game: luồng chính hoạt động?
□ 11. Chạy lại level (reload): state có đúng?
□ 12. Save -> thoát game -> load: state có đúng?
□ 13. Làm lại hành động lần 2: có bị lặp/nhân đôi?
□ 14. Nhấn linh tinh (spam E, mở túi lúc thoại, ESC giữa cutscene): có crash?
□ 15. Panel Output/Debugger: có warning/error nào mới?
□ 16. Cập nhật docs/TASKS.md
□ 17. git commit với message rõ ràng
```

Mục **11, 12, 13, 14** là bốn mục bắt được nhiều bug nhất. Đừng bỏ.

Mục 14 (nhấn linh tinh) đặc biệt hiệu quả với game có nhiều state UI — 30 giây spam nút bắt được bug mà 10 phút test "đúng cách" bỏ qua.

---

## 9.18 Ví dụ session hoàn chỉnh (từ đầu tới commit)

Đây là một session thật, rút gọn, để bạn thấy nhịp làm việc.

### Bối cảnh

Bạn đã có: `GameState`, `Interactable`, `Dialogue` chạy được. Giờ cần `ItemPickup`.

### Lượt 1 — bạn

```
Đọc AGENTS.md + scripts/systems/interactable.gd + scripts/systems/item_data.gd.

Task: scripts/props/item_pickup.gd — vật phẩm nhặt được trong world.

Hành vi:
- Kế thừa Interactable. prompt_text = "Nhặt".
- @export item: ItemData, @export amount: int = 1
- @export pickup_flag: String — set khi nhặt, để item không hồi sinh khi
  reload level. Nếu flag đã có ở _ready -> queue_free() ngay.
- @export pickup_message: String — nếu rỗng, tự sinh "Nhận được <tên>" (x<n> nếu >1)
- interact(): add_item -> set flag -> SFX "pickup" -> await HUD.show_toast(msg)
  -> emit interacted -> queue_free()
- Sprite nhấp nhô lên xuống liên tục (tween loop) để dễ thấy.

RÀNG BUỘC
- 1 file duy nhất. Tối đa 60 dòng.
- Không sửa interactable.gd, không sửa game_state.gd.
- Static typing, comment tiếng Việt giải thích tại sao.

ĐỊNH DẠNG
1. Cây scene item_pickup.tscn (tên + kiểu node + property cần set)
2. Code
3. Cách test (4 bước)
```

### Lượt 2 — AI trả về

Cây scene + code (bản như ở chương 06 mục 6.4.2) + cách test. Kèm ghi chú:

> *"Lưu ý: `create_tween()` mặc định bị hủy khi node bị free — điều đó là mong muốn ở đây. Tôi không chắc `Tween.TRANS_SINE` có tên đúng vậy ở 4.4, kiểm tra F1 nếu báo lỗi."*

Ghi chú cuối là dấu hiệu tốt — AI đang nói ra chỗ nó không chắc, đúng như `AGENTS.md` §5.6 yêu cầu.

### Lượt 3 — bạn đọc code (bước READ)

Bạn phát hiện 2 điều:

1. `_start_bob()` gọi `create_tween()` trong `_ready()`, nhưng nếu `queue_free()` đã được gọi ở dòng trên (khi flag đã có) thì `_ready` vẫn chạy tiếp → tween trên node đang bị free. Code AI **có** `return` sau `queue_free()` → OK, không phải bug.
2. `interact()` không kiểm `item == null`... thực ra **có** `push_warning`. OK.
3. Nhưng: `interact()` gọi `queue_free()` **sau** `await HUD.show_toast(msg)`. Trong 1.8 giây đó, người chơi có thể nhấn E lần nữa → nhặt 2 lần!

Bạn báo lại:

```
Code ổn, nhưng có 1 bug: giữa lúc await show_toast (1.8s), player nhấn E lần
nữa thì interact() chạy lại -> add_item 2 lần.

Sửa: vô hiệu hóa tương tác NGAY khi bắt đầu interact, trước await.

CHỈ sửa chuyện đó. Cho tôi diff.
```

### Lượt 4 — AI trả diff

```
scripts/props/item_pickup.gd

  Trong interact(), THÊM ngay dòng đầu tiên (sau check item == null):

+	# Vô hiệu hóa ngay để player không nhặt 2 lần trong lúc await toast.
+	set_active(false)

  Lý do đặt sau check null: nếu item chưa gán, ta muốn item vẫn tương tác
  được để bạn thấy warning lặp lại khi debug.
```

Tốt: diff 2 dòng, có giải thích lý do vị trí. Không sửa gì khác.

### Lượt 5 — bạn dựng scene + test

Bạn dựng `item_pickup.tscn` trong editor theo mô tả, gán `fish.tres`, `pickup_flag = "picked_fish_dock"`, đặt vào town.

Test:
- ✅ Nhặt được, toast hiện, item vào túi
- ✅ Spam E: chỉ nhặt 1 lần
- ✅ Reload level (F6): item không hồi sinh
- ❌ **Save → load: item hồi sinh!**

### Lượt 6 — bạn báo bug

```
1. TÔI LÀM: nhặt cá -> save ở save point -> thoát game -> chạy lại -> load
2. MONG ĐỢI: cá không xuất hiện lại ở bến
3. THỰC TẾ: cá xuất hiện lại, nhặt được lần 2 -> túi có 2 cá
4. LOG: không có lỗi
5. TÔI ĐÃ THỬ: nhấn F3 sau load -> Dbg.dump_state() in ra:
   Flags (3): gave_fish, met_bay, picked_fish_dock
   -> flag CÓ trong state.
   Nhưng cá vẫn hiện.
```

### Lượt 7 — AI phân tích

> Flag có trong state nhưng item vẫn hiện → nghĩa là `_ready()` của `ItemPickup` chạy **trước** khi `GameState.from_dict()` được gọi.
>
> Thứ tự thực tế trong `SaveSystem.load_game()`: `GameState.from_dict(state)` **rồi** `SceneRouter.goto_level(...)`. Vậy thứ tự đúng.
>
> Nhưng: `main.gd::_ready()` gọi `GameState.reset()` **rồi** `goto_level(FIRST_LEVEL)`. Nếu bạn load từ menu chính sau khi `main.gd` đã load town, thì town đã tồn tại với item, và `goto_level` mới sẽ tạo town **mới** — item mới đọc flag đúng...
>
> Cho tôi 2 print để xác định:
> 1. `item_pickup.gd::_ready()` đầu tiên: `print("[PICKUP] ready, flag=%s, has=%s" % [pickup_flag, GameState.has_flag(pickup_flag)])`
> 2. `save_system.gd::load_game()` sau `from_dict`: `print("[SAVE] state applied, flags=%s" % GameState.flags)`

Bạn chạy, dán:

```
[PICKUP] ready, flag=, has=false
[SAVE] state applied, flags={ "met_bay": true, "gave_fish": true, "picked_fish_dock": true }
```

`flag=` **rỗng!** → bạn quên gán `pickup_flag` trong Inspector cho instance ở town (bạn gán cho scene gốc `item_pickup.tscn` chứ không phải instance).

### Lượt 8 — kết thúc

Bạn gán lại trong Inspector. Test lại: pass hết.

```bash
git diff --stat
# 1 file changed, 58 insertions(+)
git add -A
git commit -m "feat: ItemPickup — nhặt item, chống nhặt lặp, nhớ qua save"
```

Rồi:

```
Cập nhật docs/TASKS.md: ItemPickup xong (commit vừa rồi).
Thêm vào mục "Bug đã biết": pickup_flag phải gán trên INSTANCE trong level,
không phải trên scene gốc — nếu quên, item hồi sinh sau save/load.
```

### Bài học từ session này

| Quan sát | Bài học |
|---|---|
| AI viết code đúng ~90% ngay lần đầu | Với spec rõ + `AGENTS.md`, chất lượng cao |
| Bug "nhặt 2 lần" do **bạn** đọc code phát hiện, không phải test | Bước READ không thể bỏ |
| Bug save/load do **bạn** cấu hình sai, không phải code sai | AI không thấy Inspector của bạn |
| Print debug tìm ra bug trong 1 lượt | Tạo dữ liệu > đoán giả thuyết |
| Toàn bộ session ~25 phút | Tự viết mất ~2h |

---

## 9.19 Bài tập

1. **Viết `AGENTS.md` cho project của bạn.** Copy template 9.4, sửa cho khớp. Dành 45 phút thật. Đây là bài tập giá trị nhất chương này.
2. Tạo `docs/TASKS.md` với đủ 4 mục (Đang làm / Xong / Quyết định đã chốt / Bug đã biết).
3. Lấy prompt 9.5(a) (Dialogue), chạy thật với AI. Đọc code nhận về theo checklist 9.6.2. **Ghi lại** bạn tìm được mấy vấn đề.
4. Chạy Pattern 5 (Adversarial review) trên một file code bạn **tự viết**. Ghi lại nó tìm được gì. (Thường sẽ có ít nhất 1 thứ thật.)
5. Nhờ AI viết `debug_menu.gd` theo 9.12.4. Dùng nó test câu đố 3 mà không chơi lại từ đầu.
6. Nhờ AI viết validator dialog JSON theo 9.11.3. Chạy trên các file dialog của bạn. Nếu nó tìm được lỗi → bạn vừa tiết kiệm một buổi debug.
7. Nhờ AI viết test suite cho `GameState` theo 9.13.3. Chạy headless. Đảm bảo 12/12 PASS.
8. **Bài tập tự nhận thức**: chọn một task bạn đã giao AI. Ước lượng tự làm mất bao lâu. So với thời gian thật đã bỏ ra (kể cả review + sửa). AI có thật sự nhanh hơn cho task đó không? Ghi lại kết luận để lần sau chọn đúng.
9. Cố tình giao AI một task mơ hồ ("làm hệ thống chiến đấu"). Xem nó bịa ra gì. Đây là bài học trực quan nhất về tầm quan trọng của spec.
10. Chạy Pattern 1 (Explain before code) cho một task lớn. So sánh với việc để nó code luôn. Ghi lại bạn thích cách nào.

---

## 9.20 Lỗi thường gặp (khi làm việc với AI)

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Code AI không compile | API Godot 3, hoặc bịa hàm | Bảng đối chiếu bẫy 1; ghi rõ bản Godot trong `AGENTS.md`; cho AI chạy `--check-only` |
| Code chạy nhưng save không lưu | AI tạo state riêng thay vì dùng `GameState` | Luật kiến trúc §3.1; checklist đọc code vòng 2 |
| Null reference ở `@onready` | Cây scene thật khác cây AI đề xuất | Dán cây scene thật (bẫy 7, script `dump_tree.gd`) |
| Sửa 5 vòng bug không hết | AI đang đoán, thiếu dữ liệu | Prompt "liệt kê giả định + cho tôi print" (9.6.4) |
| `git diff` có 8 file cho task 1 file | Scope creep | `AGENTS.md` §6; Pattern 2 "diff only"; Pattern 3 "constraint list" |
| Một cái cửa có 5 class | Over-engineering | Pattern 4 "budget"; câu "thà lặp code còn hơn 3 lớp trừu tượng" |
| AI đề xuất lại thứ bạn đã bác | Không có ký ức | Mục "Quyết định đã chốt" trong `TASKS.md` |
| Codebase có 3 trường phái code | Không có quy ước ghi lại | `AGENTS.md` §4 + mục quy ước animation (bẫy 6) |
| Hộp thoại hiện 2 lần | Signal nối lặp | Bẫy 8: `is_connected` check hoặc `CONNECT_ONE_SHOT` |
| Node chưa sẵn sàng dù `_ready` xong | `await` trong `_ready` | Bẫy 9: tách ra `call_deferred` |
| AI khăng khăng cách của nó đúng | Nó không chạy được game của bạn | Dán log/kết quả thật. Dữ liệu thắng lý lẽ |
| Bạn không hiểu code trong project mình | Bỏ bước READ nhiều lần | Dừng. Nhờ AI giải thích từng file. Đây là nợ phải trả sớm |
| Session dài, AI bắt đầu lệch | Context loãng | Session mới + đọc lại `AGENTS.md`/`TASKS.md` |
| AI nói "cách này nhanh hơn" không có số | Tối ưu sớm | Đo bằng `Debugger → Monitors` trước |
| AI làm hỏng scene | Nó sửa `.tscn` | `AGENTS.md` §2 cấm. `git checkout -- *.tscn` |
| Asset AI nhìn "lạc đàn" | Chưa quantize palette / lệch nguồn sáng | Chương 03 mục 3.7, 3.8 |
| Nhạc AI không ra chất chip | Bản chất tool text-to-music | Chương 08 mục 8.3: dùng AI cho lý thuyết nhạc, tự làm audio |
| Dialog AI dài quá hộp thoại | Không ràng buộc số ký tự | Thêm "mỗi dòng ≤ 90 ký tự" vào prompt |
| Flag/item id sai chính tả trong JSON | AI bịa tên | Dán danh sách hợp lệ vào prompt + viết validator (9.11.3) |
| Bạn mất 1 giờ cho task tự làm 10 phút | Dùng AI cho task quá nhỏ / cần cảm nhận | Bảng 9.7 + nguyên tắc 9.16.3 |

---

## 9.21 Tóm lại: 10 quy tắc

1. **Viết `AGENTS.md` trước khi viết dòng code đầu tiên.** Nó là bộ nhớ của AI.
2. **Luôn đọc code AI viết.** 3 phút đọc đổi 3 giờ debug.
3. **Chia task nhỏ**: một task = một thứ test được trong 2 phút.
4. **Dán log nguyên văn**, không kể lại bằng lời.
5. **Tạo dữ liệu (print) trước khi hỏi giả thuyết** khi debug.
6. **Commit trước khi giao task.** Git là van an toàn.
7. **AI làm việc có đúng/sai. Bạn làm việc có hay/dở.**
8. **Ghi mọi quyết định vào file**, không giữ trong đầu — AI không đọc được đầu bạn.
9. **Nói ra chỗ AI hay sai** (API version, kiến trúc, số ký tự) trong prompt, trước khi nó sai.
10. **Nếu bạn không hiểu project của mình nữa, dừng lại.** Đó là tín hiệu duy nhất cho biết bạn đang dùng AI sai cách.
