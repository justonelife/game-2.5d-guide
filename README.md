# Làm Game Phiêu Lưu 2.5D Phong Cách 8-bit bằng Godot 4

> Bộ tài liệu tiếng Việt, dành cho người mới bắt đầu, nhưng đi tới mức **build được một game thật**.
> Định hướng "thời đại AI": bạn học cách dùng AI (Claude Code, tool sinh asset) như một **thành viên trong team**, không phải như phép thuật.

---

## Phong cách chốt sẵn của tài liệu này

| Trục | Lựa chọn |
|---|---|
| **Kỹ thuật** | Engine 3D thật (Godot 4, `Node3D`, `Camera3D`) |
| **Art** | Pixel art 2D đặt trong không gian 3D (`Sprite3D` / `AnimatedSprite3D`) — kiểu HD-2D / Octopath Traveler / Live A Live remake |
| **Retro level** | 8-bit: palette giới hạn, tilemap, animation frame-by-frame, chiptune |
| **Genre** | Phiêu lưu: đi lại, hội thoại NPC, inventory, giải đố, chương/màn, save point. **Không** phải action nặng |

---

## Mục lục

| # | File | Nội dung | Đọc khi |
|---|---|---|---|
| 00 | [00-to-doc.md](00-to-doc.md) | Tổng quan tài liệu, lộ trình học, giới thiệu game mẫu "Ngọn Đèn Cá Nục" | Đọc đầu tiên |
| 01 | [01-setup.md](01-setup.md) | Cài Godot 4.x, cấu hình project, pixel-perfect, cấu trúc thư mục | Ngày 1 |
| 02 | [02-25d-concepts.md](02-25d-concepts.md) | Hiểu 2.5D trong Godot 4: Sprite3D, billboard, camera, trục, collision | Ngày 1–2 |
| 03 | [03-pixel-art-ai.md](03-pixel-art-ai.md) | Pixel art pipeline + dùng AI sinh asset (thật thà về giới hạn) | Song song |
| 04 | [04-player-character.md](04-player-character.md) | Nhân vật điều khiển: CharacterBody3D, input, animation, camera follow | Ngày 2–3 |
| 05 | [05-world-diorama.md](05-world-diorama.md) | Dựng thế giới diorama 3D: lớp sâu, GridMap, ánh sáng, sprite đứng | Ngày 3–5 |
| 06 | [06-adventure-mechanics.md](06-adventure-mechanics.md) | Hội thoại, inventory, cổng khóa, trigger, flags, save/load, chuyển màn | Ngày 5–10 |
| 07 | [07-story-design.md](07-story-design.md) | Thiết kế adventure, câu đố hay, pacing, viết dialog + design đầy đủ game mẫu | Đọc trước khi code màn |
| 08 | [08-audio-8bit.md](08-audio-8bit.md) | Chiptune, SFX, tích hợp Godot, bản quyền + AI gen nhạc | Ngày 10+ |
| 09 | [09-ai-workflow.md](09-ai-workflow.md) | **Chương dày nhất**: workflow thực dụng với Claude Code/Cursor, prompt mẫu, bẫy, `AGENTS.md` template | Đọc sớm, dùng liên tục |
| 10 | [10-publish.md](10-publish.md) | Export desktop/web/mobile, optimize, itch.io, roadmap sau MVP | Cuối |

---

## Cách dùng tài liệu

1. Đọc `00` để biết mình sẽ build cái gì.
2. Làm `01` → `02` → `04` để có nhân vật chạy được trong world 3D. Đây là mốc "game bắt đầu có hồn".
3. Đọc `09` **sớm** (không để cuối) — vì bạn sẽ dùng AI ở mọi chương sau đó.
4. `06` là chương nặng nhất về code. Chia nhỏ: dialog → inventory → flags → save.
5. `07` đọc bất cứ lúc nào bạn bí ý tưởng.

**Nguyên tắc xuyên suốt**: mỗi chương có `Khái niệm → Code/scene chạy được → Bài tập → Lỗi thường gặp`.

---

## Trung thực trước

Tài liệu này **không** hứa "AI làm hết". Những chỗ AI hiện làm kém (animation pixel nhiều frame nhất quán, kiến trúc game dài hạn, level design có cảm giác) đều được nói thẳng ở chương 03 và 09, kèm cách xử lý.

Godot phát triển nhanh. Tài liệu viết theo **Godot 4.3–4.5**. Chỗ nào tên property/API có thể đã đổi, tài liệu ghi rõ *"kiểm tra lại trên bản Godot bạn dùng"* — hãy tra trong panel **Inspector** và **Editor Help (F1)** thay vì tin tuyệt đối vào giấy.
