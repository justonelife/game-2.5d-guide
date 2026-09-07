# 00 — Tổng quan tài liệu & Game mẫu

## 0.1 Bạn sẽ có gì sau khi đọc hết

Một game phiêu lưu 2.5D chơi được 3–5 phút, export ra `.exe` / web, có:

- Nhân vật pixel art đi lại trong thế giới 3D thật (có chiều sâu, có che khuất, có ánh sáng)
- 1 thị trấn + 1 dungeon ngắn
- Hội thoại NPC kiểu 8-bit (typewriter, hộp thoại viền, chọn câu trả lời)
- Inventory nhặt/dùng vật phẩm
- 3 câu đố có logic thật
- Save/load, chuyển màn giữ nguyên tiến trình
- Nhạc + SFX chiptune

Và quan trọng hơn: **một workflow làm game với AI** mà bạn tái dùng cho project sau.

---

## 0.2 Bản đồ kiến thức (đọc theo thứ tự này)

```
01 Setup ──► 02 Hiểu 2.5D ──► 04 Nhân vật ──► 05 Thế giới
                  │                                 │
                  ▼                                 ▼
            03 Pixel art + AI              06 Cơ chế phiêu lưu
                                                    │
                    07 Story design ◄───────────────┤
                                                    ▼
                                             08 Audio ──► 10 Publish

            09 AI Workflow ── dùng ở MỌI bước phía trên
```

**Mốc kiểm tra tiến độ** (nếu tới mốc mà chưa chạy được thì đừng đi tiếp):

| Mốc | Tiêu chí "xong" |
|---|---|
| M1 | Project mở được, cửa sổ 320×180 scale lên, không blur |
| M2 | Có 1 `Sprite3D` pixel art đứng trên mặt đất, camera ortho nhìn nghiêng |
| M3 | Điều khiển được nhân vật 4 hướng, animation đổi theo hướng, camera đi theo |
| M4 | Nói chuyện được với 1 NPC |
| M5 | Nhặt được 1 item, mở được 1 cửa khóa |
| M6 | Đi từ thị trấn sang dungeon, quay lại, item còn nguyên |
| M7 | Save → tắt game → load → đúng chỗ cũ |
| M8 | Export ra file chạy được trên máy khác |

---

## 0.3 Game mẫu xuyên suốt: **"Ngọn Đèn Cá Nục"**

Đây là "con cá nục" của tài liệu — mọi ví dụ code đều thuộc game này, nên bạn học xong là có game thật, không phải 12 demo rời rạc.

### Logline

> Ngọn hải đăng của làng Cá Nục tắt ba đêm liền. Thuyền cha bạn chưa về. Bạn phải vào hầm hải đăng, tìm lại ba viên **Lửa Muối** và thắp đèn trước khi trời sáng.

### Cấu trúc (3–5 phút chơi)

| Khu | Tên | Vai trò |
|---|---|---|
| Màn 1 | **Làng Cá Nục** (thị trấn) | Học điều khiển, gặp 3 NPC, nhặt item đầu tiên, mở đường vào hầm |
| Màn 2 | **Hầm Hải Đăng** (dungeon 3 phòng) | 3 câu đố, 1 save point, phòng lõi đèn |
| Màn 3 | **Đỉnh Hải Đăng** (ending) | Thắp đèn, cutscene ngắn, credits |

### 3 câu đố (chi tiết ở chương 07)

1. **Đổi cá lấy khóa** — Ông Bảy giữ chìa khóa cổng hầm, chỉ đổi khi bạn mang cho ông một con cá nục. Cá nằm trong giỏ ở bến. → dạy *inventory + dialog có điều kiện*.
2. **Bệ trọng lượng** — Cửa phòng 2 chỉ mở khi có vật nặng đè lên bệ đá. Đẩy thùng cá muối từ phòng 1 sang. → dạy *vật lý nhẹ + Area3D + flag*.
3. **Thứ tự ba đuốc** — Ba đuốc phải bật theo thứ tự "**biển – trăng – đá**". Manh mối nằm trong câu hát của bà Tám ở làng (màn 1). → dạy *state machine nhỏ + kiến thức từ màn trước*.

### Danh sách flags (dùng suốt tài liệu)

```gdscript
# GameState.flags — mọi tiến trình cốt truyện nằm ở đây
"met_bay"            # đã nói chuyện ông Bảy lần đầu
"has_fish"           # đã nhặt cá nục
"gave_fish"          # đã đưa cá cho ông Bảy
"has_rusty_key"      # có chìa khóa rỉ
"gate_open"          # cổng hầm đã mở
"heard_song"         # đã nghe bà Tám hát (manh mối đuốc)
"crate_on_plate"     # thùng cá đã nằm trên bệ
"torch_puzzle_done"  # đã bật đuốc đúng thứ tự
"lighthouse_lit"     # đã thắp đèn — ending
```

Chỉ 9 flag. Một game advention nhỏ **không cần** hệ thống quest phức tạp — bạn cần 9 boolean và một cây dialog. Đừng over-engineer ở MVP.

---

## 0.4 Ngân sách thực tế (nói thẳng)

| Hạng mục | Người mới, làm một mình, có AI hỗ trợ |
|---|---|
| Học Godot cơ bản | 1–2 tuần (2h/ngày) |
| Code hết cơ chế chương 06 | 1–2 tuần |
| Art (nếu tự vẽ pixel từ đầu) | 2–4 tuần |
| Art (AI gen + tự sửa) | 1–1.5 tuần — tiết kiệm thật, nhưng **không** về 0 |
| Audio | 2–4 ngày |
| Polish + export | 1 tuần |

Tổng ~6–10 tuần cho MVP 5 phút. AI cắt được khoảng **30–50%** thời gian ở phần boilerplate code và concept art — **không** cắt được thời gian ở game feel, level design, và debug. Chương 09 giải thích tại sao.

---

## 0.5 Chuẩn bị trước khi sang chương 01

- [ ] Máy: RAM ≥ 8GB, GPU hỗ trợ Vulkan (hoặc dùng renderer Compatibility)
- [ ] Tài khoản GitHub (để version control — bắt buộc, kể cả làm một mình)
- [ ] Cài Git
- [ ] Chọn editor pixel art: Aseprite (~$20) hoặc Pixelorama / LibreSprite (free)
- [ ] Có Claude Code / Cursor / một AI coding tool

---

## 0.6 Bài tập

1. Viết logline game **của bạn** (1 câu, ≤ 30 từ). Nếu không viết được 1 câu thì scope còn mơ hồ.
2. Liệt kê tối đa 10 flag cho game của bạn. Nếu quá 15 → cắt scope.
3. Vẽ tay bản đồ 2 khu vực trên giấy. Đánh dấu: điểm bắt đầu, 3 chỗ có đố, cửa khóa, save point.

---

## 0.7 Lỗi thường gặp (ở giai đoạn ý tưởng)

| Lỗi | Hậu quả | Cách sửa |
|---|---|---|
| Scope quá lớn ("open world, 20 giờ chơi") | Bỏ dở sau 3 tuần | Ép giới hạn: 2 map, 5 NPC, 3 đố |
| Làm art trước, code sau | Art không khớp gameplay, vẽ lại | Blockout hình hộp trước, art sau (chương 05) |
| Học engine bằng cách đọc hết docs | Không bao giờ bắt đầu | Học theo mốc M1–M8 ở trên |
| Copy code AI mà không hiểu | Bug không sửa được ở tuần thứ 4 | Quy tắc "đọc trước khi dán" (chương 09) |
| Không dùng Git | Mất 2 ngày làm khi scene corrupt | `git init` ngay hôm nay |
