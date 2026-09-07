# 03 — Pixel art pipeline + dùng AI sinh asset

## 3.1 Chọn công cụ

| Tool | Giá | Đánh giá |
|---|---|---|
| **Aseprite** | ~$20 (Steam/itch), free nếu tự build từ source | Chuẩn công nghiệp. Onion skin, tag animation, export sheet + JSON. Nên mua |
| **Pixelorama** | Free, open source (làm bằng Godot) | Rất khá, đủ dùng cho game này. Có animation timeline |
| **LibreSprite** | Free (fork Aseprite bản cũ) | Ổn, UI hơi cũ, ít tính năng mới |
| **Piskel** | Free, web | Chỉ nên dùng để thử nghiệm nhanh |
| **GraphicsGale** | Free | Cổ nhưng animation tools tốt |
| **Photoshop/GIMP** | — | Làm được nhưng workflow pixel dở hơn hẳn. Không khuyến nghị |

Khuyến nghị: **Aseprite** nếu bỏ được $20, **Pixelorama** nếu không.

Cài thêm plugin Godot: **Aseprite Wizard** (AssetLib) — import trực tiếp `.aseprite` thành `SpriteFrames`, không cần export tay mỗi lần sửa. Tiết kiệm rất nhiều thời gian.

---

## 3.2 Chọn "spec" art — chốt trước khi vẽ

Ba con số này quyết định toàn bộ art của game. Đổi sau = vẽ lại hết.

| Spec | Giá trị chọn | Lý do |
|---|---|---|
| Base resolution | 320×180 | Chương 01 |
| Pixels per unit | 16 | Chương 02 |
| Nhân vật cao | **32 px** (2 unit) | Đủ chi tiết để nhận diện mặt, đủ nhỏ để vẽ nhanh |
| Canvas sprite nhân vật | **32×32 px** mỗi frame | Chừa chỗ cho tay/vũ khí vươn ra |
| NPC | 32×32 | Cùng chuẩn để đỡ lệch tỉ lệ |
| Tile sàn/tường | 16×16 | |
| Prop nhỏ (thùng, đuốc) | 16×32 hoặc 32×32 | |
| Prop lớn (nhà, cây to) | 64×64 hoặc 64×96 | |
| Icon inventory | 16×16 | |
| Palette | **32 màu** cho toàn game | Xem 3.3 |

> Với nhân vật 32px trong viewport 180px cao → nhân vật chiếm ~18% chiều cao màn hình. Tỉ lệ này giống Zelda: A Link to the Past. Rất hợp adventure.

### Cấu trúc sprite sheet nhân vật

Adventure 2.5D với billboard `FIXED_Y` cần bao nhiêu hướng?

| Số hướng | Số frame phải vẽ | Đánh giá |
|---|---|---|
| **4 hướng** (up/down/left/right), lật ngang tái dùng left↔right → thực tế vẽ 3 | idle 4 + walk 16 ≈ 20 frame | ✅ **Chọn cái này cho MVP** |
| 8 hướng | ~40 frame | Mượt hơn, gấp đôi công. Để bản sau |
| 1 hướng (chỉ mặt trước) | ~6 frame | Rất nhanh, nhưng cảm giác kỳ khi đi lên |

Layout sheet đề nghị (mỗi ô 32×32, đọc theo hàng):

```
Hàng 0: idle_down    (4 frame)
Hàng 1: idle_up      (4 frame)
Hàng 2: idle_side    (4 frame)   ← lật ngang để ra left/right
Hàng 3: walk_down    (6 frame)
Hàng 4: walk_up      (6 frame)
Hàng 5: walk_side    (6 frame)
Hàng 6: interact     (3 frame)   ← động tác với/nhặt
Hàng 7: hurt / carry (2-4 frame)
```

Tổng: **~35 frame** cho nhân vật chính. Đây là con số thực tế cho MVP. Đừng vẽ combat animation nếu game không có combat.

---

## 3.3 Palette — thứ làm nên "8-bit thật"

Cái phân biệt pixel art tốt và pixel art "AI-ish" nhiều nhất **không phải độ phân giải, mà là palette**. AI thường xuất ảnh có hàng nghìn màu → trông sạch nhưng "không phải 8-bit".

### Chọn palette

Vào **lospec.com/palette-list** và chọn 1 palette dựng sẵn:

| Palette | Số màu | Vibe |
|---|---|---|
| **NES (chuẩn)** | 54 | 8-bit chính hiệu, hơi khó phối |
| **PICO-8** | 16 | Dễ phối, rất nhận diện, hơi "indie jam" |
| **Endesga 32 / EDG32** | 32 | ✅ Khuyến nghị — cân bằng, đủ sắc độ để làm ánh sáng |
| **AAP-64** | 64 | Nhiều lựa chọn, dễ mất kỷ luật |
| **Sweetie 16** | 16 | Tươi, phù hợp game nhẹ nhàng |

Game mẫu "Ngọn Đèn Cá Nục": biển đêm + hải đăng → cần xanh lam đậm, xanh lục biển, cam-vàng lửa, xám đá. **Endesga 32** phủ tốt.

Tải file `.gpl` / `.pal` → Aseprite: `Palette → Load Palette`. Rồi **bật `Edit → Preferences → ... chỉ dùng màu trong palette`** (hoặc luôn pick màu từ palette panel, không dùng color picker tự do).

### Quy tắc phối nhanh cho người mới

- Mỗi vật thể: **3 sắc độ** (shadow / base / highlight). 4 nếu quan trọng.
- Nguồn sáng **một hướng, nhất quán toàn game** (ví dụ: trên-trái). Vẽ mũi tên lên tờ giấy dán màn hình.
- Dùng **hue shift**: vùng tối không chỉ tối hơn mà còn dịch màu về xanh/tím; vùng sáng dịch về vàng/cam. Đây là mẹo làm pixel art trông "có nghề" nhanh nhất.
- Outline: chọn 1 kiểu và giữ — `outline đen toàn bộ` (rõ, cartoon), `outline màu đậm của chính vật` (mềm hơn), hoặc `selective outline` (chỉ viền phần cần tách khỏi nền).
- **Không** dùng anti-aliasing tự động. Nếu cần làm mềm cạnh, đặt tay từng pixel trung gian.

---

## 3.4 Dùng AI sinh pixel art — nói thật trước

### AI hiện làm TỐT

| Việc | Mức độ dùng được |
|---|---|
| Concept art / mood board (không phải asset cuối) | ⭐⭐⭐⭐⭐ Rất tốt. Dùng để chốt màu, chốt vibe trong 10 phút |
| Tile sàn/tường/texture lặp | ⭐⭐⭐⭐ Tốt, cần chỉnh seam |
| Prop tĩnh đơn lẻ (thùng, chum, bụi cỏ, đá) | ⭐⭐⭐⭐ Tốt sau khi quantize palette |
| Background xa (núi, mây, biển) | ⭐⭐⭐⭐ Tốt — ở xa nên lỗi khó thấy |
| Icon inventory 16×16 | ⭐⭐⭐ Được, thường phải vẽ lại 50% pixel |
| Portrait NPC (ảnh chân dung hộp thoại) | ⭐⭐⭐ Được, cần quantize mạnh |
| Sprite nhân vật 1 frame idle | ⭐⭐ Tạm, gần như luôn phải sửa tay |
| **Animation nhiều frame nhất quán** | ⭐ **Kém.** Đây là điểm yếu lớn nhất |
| **Nhân vật cùng một danh tính qua 4 hướng** | ⭐ **Kém.** Áo đổi màu, tóc đổi kiểu giữa các hướng |

### Vì sao animation kém

Model sinh ảnh không có khái niệm "cùng một nhân vật, khác một chút". Mỗi lần gen là một mẫu độc lập. Kết quả: frame 1 tóc 3 pixel, frame 2 tóc 4 pixel → animation "nhảy giật". Với pixel art 32px, sai 1 pixel là thấy ngay.

Các tool chuyên dụng (PixelLab, Retro Diffusion) đã cải thiện đáng kể bằng cách train riêng cho pixel + có chế độ "animate from single sprite", nhưng **vẫn cần bạn sửa tay**. Đừng lên kế hoạch dự án dựa trên giả định "AI làm animation xong".

### Kết luận thực dụng

> **AI làm concept + prop + tile + background. Bạn vẽ tay nhân vật chính và animation của nó.**

Nhân vật chính là ~35 frame 32×32. Một người mới vẽ được trong 3–5 ngày. Đó là 3–5 ngày đáng bỏ ra vì nhân vật chính là thứ người chơi nhìn 100% thời gian.

---

## 3.5 Tool AI sinh pixel art (tình hình hiện tại)

> Thị trường này đổi rất nhanh. Danh sách dưới đây đúng theo hiểu biết đến giữa 2026 — **hãy tự kiểm tra tool nào còn hoạt động, giá bao nhiêu, và điều khoản bản quyền trước khi dựa vào nó cho game thương mại.**

| Tool | Loại | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| **Retro Diffusion** | Model + plugin Aseprite | Train riêng cho pixel, xuất ảnh sát grid, có palette control | Trả phí, style hơi đặc trưng |
| **PixelLab** | Plugin Aseprite / web | Có tính năng gen animation, rotate character, inpaint pixel | Animation vẫn cần sửa; trả phí |
| **Scenario** | Web, train LoRA riêng | Train được style của bạn → nhất quán tốt nhất trong nhóm | Cần dataset, tốn thời gian setup |
| **Stable Diffusion / Flux + LoRA pixel-art** (local, ComfyUI/A1111) | Self-host | Free, kiểm soát tuyệt đối, không giới hạn lượt | Cần GPU + học ComfyUI |
| **Midjourney** | Web | Concept art xuất sắc | Không ra pixel grid thật; chỉ dùng cho concept |
| **Claude / GPT (image gen)** | Chat | Tiện, tốt cho concept/mood | Không ra pixel grid thật |
| **Layer.ai** | Web, game asset | Có tính năng tách sheet, palette | Trả phí |

**Lộ trình khuyến nghị theo ngân sách:**

- **$0**: Midjourney free-tier/Claude cho concept → tự vẽ Pixelorama. Hoặc SD local nếu có GPU.
- **~$20–30/tháng**: PixelLab hoặc Retro Diffusion + Aseprite. Đây là combo hiệu quả nhất cho solo dev.
- **Nghiêm túc, cần nhất quán style**: Scenario với LoRA train từ 20–50 sprite bạn tự vẽ.

---

## 3.6 Prompt mẫu (copy được)

### 3.6.1 Concept art / mood board

```
Concept art for a 2.5D HD-2D pixel art adventure game.
Scene: a small fishing village at night on a rocky coast, a tall stone
lighthouse with its light extinguished, wooden piers, fishing nets,
oil lanterns as the only light source.
Mood: melancholic, mysterious, cozy-but-tense.
Color palette: deep navy blue, teal, warm amber/orange lantern glow,
cold grey stone. Limited palette, high contrast.
Style: diorama, isometric-ish 3/4 view, painterly concept (NOT final pixel art).
```

Dùng output này làm **tham chiếu màu và bố cục**, không dùng làm asset.

### 3.6.2 Tile sàn / texture lặp

```
16x16 pixel art tileset, top-down 3/4 view, seamless tileable.
Subject: wet cobblestone dock planks, dark wood with salt stains.
Strict constraints:
- exactly 16x16 pixels, 1:1 pixel grid, no anti-aliasing
- maximum 6 colors
- palette: #1a1c2c #333c57 #566c86 #94b0c2 #b13e53 #ef7d57
- no outline on edges (must tile seamlessly)
- flat lighting, no gradient, no blur
Output as a single tile, no grid lines, no watermark, no text.
```

### 3.6.3 Prop tĩnh

```
Pixel art game asset, single object on transparent background.
Subject: a wooden crate of salted fish, rope handle, slightly weathered.
Constraints:
- canvas 32x32 pixels, object fills ~28x28
- 3/4 top-down view, light source from upper-left
- maximum 8 colors, hue-shifted shadows (shadows shift toward blue)
- hard 1px dark outline
- NO anti-aliasing, NO gradient, NO dithering
- style reference: SNES-era JRPG props (Zelda: A Link to the Past)
Output: object only, transparent background, no grid, no text, no shadow on ground.
```

### 3.6.4 Sprite nhân vật (1 frame, để bạn sửa tay)

```
Pixel art character sprite, single idle frame, front-facing (facing camera).
Character: a teenage fisher girl, short dark bob haircut, patched blue
raincoat, yellow rubber boots, carrying a small lantern.
Constraints:
- canvas 32x32 pixels, character height exactly 30px
- 3/4 top-down JRPG perspective (you see the top of the head slightly)
- maximum 12 colors
- 1px dark outline, readable silhouette at 100% zoom
- NO anti-aliasing, NO blur, sharp pixel edges
Output: sprite only, transparent background, centered, feet at bottom edge.
```

### 3.6.5 Portrait hộp thoại

```
Pixel art dialogue portrait, bust shot, facing slightly left.
Character: an old fisherman, weathered face, thick grey beard,
knit cap, pipe. Expression: gruff but kind.
Constraints:
- canvas 48x48 pixels
- maximum 16 colors from this palette: [dán mã hex palette của bạn]
- hard shading in 3 tones per material, no soft gradient
- 1px outline
Output: portrait only, transparent background.
```

### Mẹo prompt cho pixel art

| Nên viết | Vì sao |
|---|---|
| Ghi **kích thước canvas cụ thể** | Model không hiểu "small", hiểu "32x32" tốt hơn (dù vẫn không chính xác) |
| Ghi **số màu tối đa** | Ép model giảm màu, dễ quantize hậu kỳ hơn |
| **Dán mã hex palette** | Hiệu quả bất ngờ với model mới |
| `NO anti-aliasing, NO gradient, NO blur` | Ba lỗi phổ biến nhất |
| Ghi **hướng nguồn sáng** | Giữ nhất quán giữa các asset |
| Ghi **game tham chiếu** ("Zelda ALTTP", "Chrono Trigger") | Model đã học style này, rất hiệu quả |
| `transparent background`, `no grid lines`, `no text`, `no watermark` | Model hay thêm rác |
| Ghi **view/perspective** | "top-down 3/4" vs "side view" cho ra thứ hoàn toàn khác |

| Đừng làm | Vì sao |
|---|---|
| Prompt dài 500 từ | Model bỏ qua phần giữa. Ngắn + cụ thể tốt hơn |
| Kỳ vọng ra đúng grid pixel | Gần như không bao giờ. Luôn có bước hậu kỳ (3.7) |
| Gen 4 hướng nhân vật bằng 4 prompt riêng | Chắc chắn không nhất quán. Gen 1 hướng rồi vẽ tay 3 hướng còn lại |
| Gen animation bằng prompt "walking animation sprite sheet" | Ra sheet trông giống sheet nhưng frame không liên tục |

---

## 3.7 Hậu kỳ — bước KHÔNG được bỏ

Ảnh AI thô gần như luôn: quá to (1024×1024), quá nhiều màu (2000+), có anti-aliasing, pixel không vuông đều. Quy trình sửa:

### Bước 1 — Downscale về đúng grid

Ảnh AI ra 1024×1024 nhưng "pixel" của nó là block ~32×32 thật → tức là ảnh 32×32 bị phóng 32×.

Trong Aseprite:
1. `Sprite → Sprite Size` → đặt 32×32 → **Interpolation: `Nearest neighbor`** (tuyệt đối không dùng bilinear)
2. Nếu block không đều (pixel lệch nửa ô), phóng to xem và cắt lại (`Sprite → Canvas Size`) sao cho block đều rồi mới downscale.

> Nếu AI ra ảnh mà "pixel" không đều nhau → bỏ ảnh đó, gen lại. Sửa ảnh lệch grid tốn thời gian hơn vẽ mới.

### Bước 2 — Quantize về palette của bạn

Aseprite:
1. `Sprite → Color Mode → Indexed`
2. Chọn `Palette: [palette của bạn]`, `Dithering: None`, `Algorithm: Nearest color` (không "ordered dithering" — dither làm nhiễu pixel art nhỏ)
3. Kiểm tra kết quả. Chỗ nào màu sai lệch → sửa tay bằng bucket fill.

Pixelorama có chức năng tương tự trong `Image → ...` (tên menu có thể khác — kiểm tra bản bạn dùng).

### Bước 3 — Clean up bằng tay (30–70% công việc thật ở đây)

Checklist:

- [ ] Xóa pixel lẻ (single stray pixel) không thuộc hình
- [ ] Sửa outline: phải liền mạch 1px, không chỗ 2px chỗ 0px
- [ ] Sửa silhouette: nhìn ở 100% zoom, có nhận ra vật đó không? Nếu không → làm rõ đường viền
- [ ] Xóa "banding" (dải pixel chéo song song trông như cầu thang lỗi)
- [ ] Nền phải trong suốt thật, không có halo màu quanh viền
- [ ] Đối chiếu hướng nguồn sáng với các asset khác
- [ ] Kiểm tra vật thể "nằm" đúng: đáy vật phải phẳng để đặt trên sàn

### Bước 4 — Tính lại thời gian

Thực tế trung bình cho 1 prop 32×32:

| Cách | Thời gian |
|---|---|
| Tự vẽ từ đầu (người mới) | 30–60 phút |
| Tự vẽ từ đầu (có kinh nghiệm) | 10–20 phút |
| AI gen + hậu kỳ (người mới) | 15–30 phút, **nhưng** cần 3–8 lần gen để có ảnh dùng được |
| AI gen + hậu kỳ (có kinh nghiệm) | 5–15 phút |

→ AI **có** tiết kiệm thời gian cho prop/tile, nhưng chỉ khoảng 2× chứ không phải 20×. Và **với sprite nhân vật có animation, AI thường chậm hơn tự vẽ.**

Nói thẳng: nếu bạn thấy mình gen ảnh lần thứ 9 cho một cái thùng gỗ, **dừng lại và vẽ tay**. Cái thùng 32×32 chỉ có ~900 pixel; vẽ tay 20 phút là xong.

---

## 3.8 Cách tránh "AI look"

Người chơi nhận ra asset AI qua các dấu hiệu này. Sửa hết là hết bị nhận ra:

| Dấu hiệu "AI look" | Cách sửa |
|---|---|
| Quá nhiều màu, gradient mượt | Quantize về ≤ 8–16 màu/vật (3.7 bước 2) |
| Pixel không đều (chỗ 1px chỗ 1.3px) | Downscale đúng grid, hoặc vẽ lại |
| Anti-aliasing tự động ở mọi cạnh | Xóa pixel trung gian; chỉ AA thủ công ở chỗ cần |
| Chi tiết vô nghĩa (đường nét không mô tả gì) | Xóa. Pixel art 32px không có chỗ cho chi tiết trang trí |
| Nguồn sáng lung tung giữa các asset | Chốt 1 hướng, sửa hết |
| Outline không nhất quán (có/không, dày/mỏng) | Chốt 1 kiểu outline toàn game |
| Style khác nhau giữa asset (cái cartoon, cái realistic) | Gen lại cùng seed/cùng prompt base, hoặc train LoRA |
| Silhouette lộn xộn | Test: chuyển sprite thành đen tuyền — vẫn nhận ra vật gì không? |

**Test rẻ nhất**: xếp tất cả asset của bạn cạnh nhau trong một ảnh, xem ở 100% và 300%. Cái nào "lạc đàn" thì sửa hoặc bỏ.

---

## 3.9 Vấn đề bản quyền & pháp lý (đọc kỹ)

Đây là phần dễ gây rắc rối thật, không phải lo xa.

| Vấn đề | Tình hình | Bạn nên làm gì |
|---|---|---|
| **Ảnh AI có được bảo hộ bản quyền?** | Ở nhiều nước (đáng chú ý là Mỹ), tác phẩm do AI sinh **không** có bản quyền nếu không có đóng góp sáng tạo đáng kể của con người | Sửa tay đáng kể → tăng khả năng phần đóng góp của bạn được bảo hộ. Đừng dựa vào việc "sở hữu" ảnh AI thuần |
| **Điều khoản của tool** | Mỗi tool khác nhau: một số cho dùng thương mại tự do, một số chỉ ở gói trả phí, một số giữ quyền | **Đọc ToS của đúng tool bạn dùng, đúng thời điểm bạn dùng.** Lưu screenshot điều khoản |
| **Steam** | Yêu cầu **khai báo** nội dung AI khi submit game | Chuẩn bị mô tả: dùng AI ở đâu, mức nào |
| **itch.io** | Có tag/khai báo nội dung AI | Tag trung thực — cộng đồng itch khá nhạy cảm chuyện này |
| **Asset store / game jam** | Nhiều jam **cấm** asset AI | Đọc rule trước khi tham gia |
| **Bắt chước style của một nghệ sĩ cụ thể** | Rủi ro đạo đức + có thể pháp lý | Đừng prompt tên nghệ sĩ đang sống. Prompt style thời kỳ/hệ máy ("SNES-era") thay vì tên người |

**Lời khuyên thực tế**: dùng AI cho concept và prop phụ, tự làm (hoặc mua/thuê) art chủ đạo. Cách này an toàn pháp lý, tốt về đạo đức, và cho ra game trông đồng nhất hơn.

---

## 3.10 Import vào Godot

### Cách A — Export sheet từ Aseprite (thủ công)

1. Trong Aseprite: `File → Export Sprite Sheet`
2. `Sheet Type: By Rows` hoặc `Packed`; **bỏ tick** `Trim`; `Padding: 0`
3. `Output: art/characters/hero.png`, tick `JSON Data` → `art/characters/hero.json` (Array, Frame Tags)
4. Trong Godot: chọn `hero.png` → tab **Import**: `Compress Mode: Lossless`, `Mipmaps: off`, `Filter: Nearest` → **Reimport**
5. Trong `AnimatedSprite3D`: tạo `SpriteFrames` mới → `Add frames from sprite sheet` → chọn `hero.png`, set `Horizontal: 6, Vertical: 8` (theo layout 3.2) → chọn frame cho từng animation

### Cách B — Aseprite Wizard addon (khuyến nghị)

1. AssetLib → tìm `Aseprite Wizard` → Install → bật trong `Project Settings → Plugins`
2. Set đường dẫn tới binary `aseprite` trong `Editor Settings`
3. Chọn `AnimatedSprite3D` → panel Aseprite Wizard → trỏ file `.aseprite` → Import
4. Mỗi **tag** trong Aseprite trở thành **1 animation** trong `SpriteFrames`
5. Sửa file `.aseprite` → bấm re-import → animation cập nhật, không mất setting

Đặt tag trong Aseprite đúng tên bạn sẽ gọi trong code: `idle_down`, `walk_down`, `idle_up`, `walk_up`, `idle_side`, `walk_side`, `interact`.

### Kiểm tra sau import

```gdscript
# Chạy thử trong một script tạm để xác nhận animation có đủ
func _ready() -> void:
	var sf: SpriteFrames = $AnimatedSprite3D.sprite_frames
	for anim_name in sf.get_animation_names():
		print("%s: %d frame, %.1f fps, loop=%s" % [
			anim_name,
			sf.get_frame_count(anim_name),
			sf.get_animation_speed(anim_name),
			sf.get_animation_loop(anim_name),
		])
```

FPS gợi ý: `idle` 4–6 fps (chậm, thở), `walk` 8–10 fps, `interact` 12 fps.

---

## 3.11 Bài tập

1. Chọn 1 palette từ lospec, tải `.gpl`, load vào editor. Ghi lại 32 mã hex vào `art/PALETTE.md` — bạn sẽ dán nó vào prompt AI.
2. Vẽ tay 1 frame idle nhân vật 32×32, chỉ dùng palette đó, tối đa 12 màu. Bấm giờ xem mất bao lâu.
3. Dùng prompt 3.6.4 gen cùng nhân vật đó bằng AI. So sánh: cái nào dùng được nhanh hơn? Ghi lại kết luận cho **chính bạn**.
4. Gen 1 tile sàn bằng prompt 3.6.2 → hậu kỳ đủ 3 bước (3.7) → import vào Godot → dán làm texture sàn trong `sandbox.tscn`.
5. Vẽ tay đủ `idle_down` (4 frame) + `walk_down` (6 frame). Import qua Aseprite Wizard. Chạy được animation trong Godot.

---

## 3.12 Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Sprite import vào Godot bị mờ | Import filter Linear / Detect 3D đổi setting | Tab Import → Filter Nearest, Mipmaps off → Reimport |
| Animation "nhảy" giữa các frame | Frame không cùng canvas, hoặc đã bật `Trim` khi export | Export lại, **tắt Trim**, giữ padding 0 |
| Sprite bị cắt mất tay/vũ khí | Canvas quá chật | Vẽ trên canvas rộng hơn (32×32 cho nhân vật 30px) |
| Viền sprite có halo màu lạ | Export từ ảnh có anti-alias, hoặc alpha bán trong suốt | Ép alpha binary (0 hoặc 255); dùng `alpha_cut = Discard` |
| Tile ghép bị đường kẻ ở mép | Texture bleeding do filter/atlas padding | Filter Nearest, tắt Mipmaps; thêm 1px padding nếu dùng atlas |
| Asset AI trông "không cùng game" | Chưa quantize palette / lệch nguồn sáng | Mục 3.7, 3.8 |
| Gen AI 10 lần vẫn không được | Prompt thiếu ràng buộc, hoặc việc này AI làm dở | Thêm ràng buộc (3.6), hoặc **vẽ tay** |
| Sửa file `.aseprite` mà Godot không cập nhật | Đang dùng cách A (export thủ công) | Chuyển sang Aseprite Wizard |
