# 07 — Cốt truyện & thiết kế game phiêu lưu

Chương này không có code. Nó là chương quyết định game của bạn **có vui hay không**.

---

## 7.1 Adventure game hay dựa trên cái gì

Không phải đồ họa, không phải cốt truyện dài. Ba thứ này:

1. **Người chơi luôn biết mục tiêu tiếp theo** — không nhất thiết biết *cách*, nhưng phải biết *cái gì*.
2. **Mọi câu đố giải được bằng thông tin đã cho** — không đoán mò, không thử-sai vô nghĩa.
3. **Khoảnh khắc "à!"** — cảm giác tự nghĩ ra, không phải bị dắt tay.

Ba thứ này đối lập nhau: quá rõ ràng thì mất "à!", quá mờ thì kẹt. Cả chương này là về việc cân bằng đó.

---

## 7.2 Cấu trúc chương — công thức 3 nhịp

Game adventure ngắn tốt gần như luôn theo nhịp này:

| Nhịp | Vai trò | Trong "Ngọn Đèn Cá Nục" |
|---|---|---|
| **1. Thiết lập** | Dạy điều khiển, giới thiệu thế giới, gieo mục tiêu | Làng Cá Nục ban đêm. Đèn tắt. NPC nói về cha bạn |
| **2. Thử thách** | Đưa ra khóa, người chơi tự giải | Hầm hải đăng: 3 câu đố |
| **3. Trả nghĩa** | Trả lời câu hỏi đã gieo ở nhịp 1, kết | Đỉnh hải đăng. Thắp đèn. Thấy thuyền |

Quy tắc thời lượng cho MVP 5 phút:

| Nhịp | Thời lượng | Tại sao |
|---|---|---|
| Thiết lập | 1.5 phút | Đủ để hiểu, không đủ để nhàm |
| Thử thách | 2.5 phút | Phần lớn game ở đây |
| Trả nghĩa | 1 phút | Kết nhanh, để lại dư vị |

**Nguyên tắc**: mọi thứ bạn gieo ở nhịp 1 phải được dùng ở nhịp 2 hoặc trả ở nhịp 3. Nếu bà Tám hát một bài mà bài đó không dùng vào đâu → cắt bà Tám hoặc cho bài hát thành manh mối. Không có chi tiết trang trí thuần trong game ngắn.

---

## 7.3 Bản đồ: thiết kế không gian để dẫn đường

### Nguyên tắc dẫn hướng không cần mũi tên

| Kỹ thuật | Cách làm | Trong game mẫu |
|---|---|---|
| **Ánh sáng dẫn đường** | Chỗ cần đi sáng hơn chỗ khác | Cổng hầm có 2 đuốc; các ngõ khác tối |
| **Đường hội tụ** | Mọi đường mòn đều dẫn về 1 điểm | 3 lối trong làng đều về quảng trường |
| **Landmark cao** | Vật cao nhìn thấy từ xa | Hải đăng thấy từ mọi chỗ trong làng |
| **Chặn mềm** | Không dùng tường vô hình; dùng vật hợp lý | Lưới cá chắn lối, đá lở, nước sâu |
| **Chuyển động** | Mắt bị hút bởi thứ động | Cờ bay ở cổng hầm, lửa nhấp nháy |
| **Tương phản màu** | Vật quan trọng dùng màu không xuất hiện ở nơi khác | Chỉ item quan trọng có màu vàng-cam sáng |

### Layout Làng Cá Nục

```
                    ┌──────────────┐
                    │  CỔNG HẦM    │  ← khóa, cần rusty_key
                    │  (2 đuốc)    │
                    └──────┬───────┘
                           │
        ┌──────────┬───────┴───────┬──────────┐
        │          │  QUẢNG TRƯỜNG │          │
   [Nhà bà Tám]    │   (hội tụ)    │    [Nhà ông Bảy]
   NPC: bài hát    │               │    NPC: giữ chìa
   → manh mối đuốc └───────┬───────┘    → cần cá
                           │
                    ┌──────┴───────┐
                    │   BẾN TÀU     │  ← SPAWN
                    │  [Giỏ cá]     │  → item: fish
                    └──────────────┘
                           │
                     (biển, backdrop)
```

Đọc bản đồ này người chơi thấy gì:

- Spawn ở bến → thứ đầu tiên thấy là **giỏ cá** (nhặt ngay, học cơ chế nhặt)
- Đi lên là quảng trường → thấy **hải đăng tối** ở phía bắc (mục tiêu)
- Hai nhà hai bên → tự nhiên ghé cả hai
- Cổng hầm ở cuối, có đuốc sáng → biết là chỗ cần đến

**Không cần bản đồ mini, không cần marker quest.** Layout tự dạy.

### Layout Hầm Hải Đăng

```
   ┌─────────────────────────┐
   │   P3: LÕI ĐÈN            │  ← cần torch_puzzle_done
   │   [3 đuốc: Sea/Moon/     │
   │    Stone]  [thang lên]   │
   └───────────┬─────────────┘
               │ cửa đá (mở bởi puzzle 3)
   ┌───────────┴─────────────┐
   │   P2: PHÒNG BỆ           │
   │   [bệ đá]  [đèn dầu] ←── item lantern ở đây
   │   [SAVE POINT]           │
   └───────────┬─────────────┘
               │ cửa (mở bởi crate_on_plate)
   ┌───────────┴─────────────┐
   │   P1: KHO CÁ MUỐI        │  ← vào từ làng
   │   [thùng cá đẩy được]    │
   └─────────────────────────┘
```

Chú ý thứ tự thông tin:

1. P1 có **thùng** nhưng chưa biết dùng làm gì
2. P2 có **bệ đá** → "à, đẩy thùng lên đây"
3. P2 cũng có **đèn dầu** → cần để thắp đuốc ở P3
4. P3 có 3 đuốc → cần **manh mối** đã nghe từ làng

Đây là **information gating** — người chơi nhận thông tin trước khi cần dùng nó, nhưng không quá sớm để quên.

---

## 7.4 Thiết kế câu đố hay

### Ba loại câu đố (và mức khó viết)

| Loại | Cơ chế | Dễ làm? | Cảm giác |
|---|---|---|---|
| **Fetch quest** ("mang X cho Y") | Inventory + dialog điều kiện | ⭐ Rất dễ | Nhàm nếu đứng một mình. Cần *lý do* |
| **Vật lý / không gian** (đẩy, đè, mở lối) | Physics + trigger | ⭐⭐ Trung bình | Thỏa mãn cao, dạy bằng thử |
| **Thông tin** (mật mã, thứ tự, ai nói dối) | Flags + state machine | ⭐⭐ Trung bình | "À!" mạnh nhất. Cần gieo manh mối cẩn thận |

Game mẫu dùng **đúng một cái mỗi loại**. Đây là công thức tốt: đa dạng loại quan trọng hơn số lượng.

### Checklist "câu đố này có hay không"

Cho từng câu đố, trả lời:

- [ ] **Người chơi biết mình đang cố làm gì?** (mục tiêu rõ, không phải "thử nút xem sao")
- [ ] **Manh mối có tồn tại trong game?** (chỉ ra được nó nằm chính xác ở đâu)
- [ ] **Manh mối có thể bị bỏ sót?** Nếu có → cần cách nhận lại (NPC nhắc lại được, ghi vào sổ tay)
- [ ] **Giải sai có feedback không?** (không được im lặng)
- [ ] **Có thể vào trạng thái không giải được không?** (dead state = lỗi thiết kế nghiêm trọng)
- [ ] **Giải xong có thay đổi thấy được không?** (cửa mở, nhạc đổi, ánh sáng đổi)
- [ ] **Giải bằng cách khác được không?** (nếu có, chấp nhận — đó là điểm tốt, không phải bug)

### Ba câu đố game mẫu, mổ xẻ

#### Đố 1 — Đổi cá lấy khóa

| Yếu tố | Nội dung |
|---|---|
| Mục tiêu người chơi | Vào hầm |
| Rào cản | Cổng khóa |
| Manh mối | Ông Bảy nói thẳng: "mang cho ta một con cá nục" |
| Nơi có giải pháp | Giỏ cá ở bến — chỗ **người chơi đã đi qua lúc spawn** |
| Feedback khi sai | Nhấn cổng chưa có chìa → toast "Cổng bị khóa. Có ổ khóa rỉ nặng." |
| Vì sao không nhàm | Cá được đặt **trước** khi biết cần nó → người chơi nhớ ra "à mình có cá rồi" thay vì phải đi lấy. Nhịp thỏa mãn ngay |

> Bài học thiết kế: **đặt item TRƯỚC khi tiết lộ nhu cầu.** Fetch quest chỉ nhàm khi bạn phải quay lại đi lấy. Nếu người chơi đã có sẵn, nó thành "à!".

#### Đố 2 — Bệ trọng lượng

| Yếu tố | Nội dung |
|---|---|
| Mục tiêu | Mở cửa sang P3 |
| Rào cản | Cửa đá không có ổ khóa, không có công tắc tay |
| Manh mối | Bệ đá lõm hình vuông + vết xước trên sàn kéo từ P1 sang |
| Nơi có giải pháp | Thùng cá muối ở P1 |
| Feedback | Đứng lên bệ → cửa hé ra rồi đóng lại khi bước xuống. **Đây là feedback dạy chơi hoàn hảo** — người chơi tự hiểu "cần vật nặng ở đây" |
| Không giải được? | Không. Thùng không thể bị đẩy vào chỗ kẹt vì P1 là phòng trống, và thùng có thể respawn (xem 7.6) |

> Bài học: **cho người chơi tự trở thành giải pháp tạm thời.** Đứng lên bệ → thấy cửa hé → hiểu ngay cần gì. Không cần một dòng chữ nào.

#### Đố 3 — Thứ tự ba đuốc

| Yếu tố | Nội dung |
|---|---|
| Mục tiêu | Mở cửa lên đỉnh hải đăng |
| Rào cản | 3 đuốc, 6 thứ tự có thể |
| Manh mối | Bài hát bà Tám (màn 1): *"Biển gọi trước, trăng đáp sau, đá nằm im cuối cùng."* |
| Nơi có giải pháp | Đuốc có ký hiệu khắc: sóng / trăng khuyết / vân đá |
| Feedback sai | Đuốc phụt tắt cùng lúc + toast + SFX. Reset ngay bước sai đầu tiên (không chờ hết 3) → người chơi biết bước nào sai |
| Bỏ sót manh mối? | **Có thể.** → Xử lý ở 7.5 |
| Brute force được? | 6 hoán vị → người chơi có thể mò. **Chấp nhận được**: mò 6 lần mất ~40s, không phá trải nghiệm. Nếu là 4 đuốc (24 hoán vị) thì phải chống mò |

> Bài học: **giữ không gian brute-force nhỏ.** 3 phần tử = 6 khả năng = mò được nhưng vẫn thỏa mãn khi biết đáp án. 5 phần tử = 120 khả năng = người chơi kẹt và tra Google.

---

## 7.5 Gợi ý mềm — chống kẹt mà không phá "à!"

Đây là kỹ thuật quan trọng nhất của adventure design hiện đại. Ba tầng:

### Tầng 1 — Manh mối bị động (luôn có)

- Vật trong world: ký hiệu khắc trên đuốc, vết xước trên sàn, tranh trên tường
- Không cần người chơi làm gì để thấy

### Tầng 2 — Nhắc lại theo yêu cầu (người chơi chủ động)

NPC phải **nhắc lại được** thông tin đã cho. Đây là chỗ hầu hết game indie làm sai — NPC nói 1 lần rồi chuyển sang "Chào bạn!" mãi mãi.

Thiết kế dialog NPC luôn có 3 tầng:

```json
{
  "tam_first": {
    "conditions": ["!heard_song"],
    "speaker": "Bà Tám",
    "lines": [
      "Cháu nghe bà hát nhé. Bài này ông nội cháu dạy bà.",
      "\"Biển gọi trước, trăng đáp sau, đá nằm im cuối cùng.\"",
      "Bà không hiểu nghĩa. Nhưng đèn hải đăng ngày trước sáng nhờ bài này."
    ],
    "set_flags": ["heard_song"],
    "next": ""
  },

  "tam_repeat": {
    "conditions": ["heard_song", "!torch_puzzle_done"],
    "speaker": "Bà Tám",
    "lines": [
      "Cháu muốn nghe lại à? \"Biển gọi trước, trăng đáp sau, đá nằm im cuối cùng.\""
    ],
    "next": ""
  },

  "tam_after": {
    "conditions": ["torch_puzzle_done"],
    "speaker": "Bà Tám",
    "lines": ["Đèn sáng rồi! Bà nghe tiếng còi thuyền ngoài kia."],
    "next": ""
  }
}
```

Ba trạng thái: **lần đầu / nhắc lại / sau khi xong**. Mỗi NPC quan trọng phải có đủ 3. Tốn thêm 10 dòng JSON mỗi NPC, cứu người chơi khỏi kẹt.

### Tầng 3 — Gợi ý tự động khi kẹt lâu (an toàn cuối)

Đo thời gian người chơi ở trong 1 phòng mà không đổi flag nào. Quá ngưỡng → gợi ý mềm.

```gdscript
# scripts/systems/hint_system.gd (autoload hoặc node trong level)
extends Node

## Sau bao lâu không tiến triển thì gợi ý (giây).
@export var idle_threshold: float = 90.0

## Gợi ý theo flag hiện tại: điều kiện -> câu gợi ý.
## Cái ĐẦU TIÊN thỏa điều kiện sẽ được dùng -> xếp từ cụ thể tới chung.
var _hints: Array[Dictionary] = [
	{"cond": ["!has_fish", "!gave_fish"], "text": "Có tiếng cá quẫy phía bến tàu."},
	{"cond": ["has_fish", "!gave_fish"], "text": "Ông Bảy chắc đang đói."},
	{"cond": ["gave_fish", "!gate_open"], "text": "Chìa khóa nằm trong túi. Cổng ở phía bắc."},
	{"cond": ["gate_open", "!crate_on_plate"], "text": "Bệ đá cần một vật nặng hơn cháu."},
	{"cond": ["crate_on_plate", "!heard_song"], "text": "Bà Tám ngoài làng biết một bài hát cũ."},
	{"cond": ["heard_song", "!torch_puzzle_done"], "text": "Biển... trăng... rồi đá."},
]

var _timer: float = 0.0
var _last_flag_count: int = -1


func _ready() -> void:
	GameState.flag_changed.connect(func(_n: String, _v: bool) -> void: _timer = 0.0)
	GameState.inventory_changed.connect(func() -> void: _timer = 0.0)


func _process(delta: float) -> void:
	if GameState.is_input_locked():
		return          # đang thoại/cutscene -> không tính là "kẹt"
	_timer += delta
	if _timer < idle_threshold:
		return
	_timer = 0.0
	_show_hint()


func _show_hint() -> void:
	for hint in _hints:
		if GameState.has_all_flags(hint["cond"]):
			# Gợi ý dạng "cảm giác của nhân vật", không phải chỉ dẫn thẳng.
			HUD.show_toast("[i]%s[/i]" % hint["text"], 3.0)
			return
```

**Cách viết gợi ý mềm đúng:**

| ❌ Đừng | ✅ Nên |
|---|---|
| "Hãy đi đến bến tàu và nhặt con cá" | "Có tiếng cá quẫy phía bến tàu." |
| "Đẩy thùng lên bệ đá" | "Bệ đá cần một vật nặng hơn cháu." |
| "Thứ tự là Biển-Trăng-Đá" | "Biển... trăng... rồi đá." |

Gợi ý mềm **hướng chú ý**, không **đưa đáp án**. Người chơi vẫn giữ được khoảnh khắc "à!".

---

## 7.6 Chống dead state (trạng thái không thể thắng)

Đây là lỗi nghiêm trọng nhất trong adventure game. Người chơi save vào một state không thể hoàn thành game.

| Nguy cơ | Trong game mẫu | Phòng thế nào |
|---|---|---|
| Item quan trọng bị bỏ/dùng sai | Cá đưa cho NPC sai | `quest_item = true` → không bỏ được; cá chỉ dùng được với ông Bảy |
| Thùng đẩy bị kẹt vào góc | P1 có góc hẹp | Làm P1 không có góc hẹp; thêm "reset thùng" |
| Save sau khi vào chỗ không ra được | Save point ở P2, cửa P1→P2 một chiều | Đảm bảo mọi cửa **hai chiều**; save point chỉ đặt ở chỗ có đường ra |
| Item duy nhất bị phá | — | Không thiết kế item phá được |
| Bán/mất item cho NPC | Không có shop | Nếu thêm shop: không cho bán quest item |

Cơ chế reset thùng (an toàn cuối):

```gdscript
# scripts/props/pushable_crate.gd — thêm vào scene thùng
extends RigidBody3D

## Vị trí gốc để reset khi thùng bị kẹt hoặc rơi khỏi map.
var _home: Vector3

## Nếu rơi xuống dưới mức này -> tự về chỗ cũ.
@export var fall_limit: float = -5.0

func _ready() -> void:
	_home = global_position

func _physics_process(_delta: float) -> void:
	if global_position.y < fall_limit:
		reset_position()

## Cho phép Interactable "bàn thờ đá" / NPC gọi để reset.
func reset_position() -> void:
	global_position = _home
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
```

Thêm một `Interactable` nhỏ trong P1: "Vết xước trên sàn" → khi tương tác, gọi `reset_position()` trên thùng và toast "Cháu kéo thùng về chỗ cũ." Vừa hợp lý trong truyện, vừa là van an toàn.

> **Nguyên tắc**: mỗi puzzle vật lý phải có một cách reset **trong game**, không bắt người chơi load save.

---

## 7.7 Viết dialog 8-bit: ngắn, súc tích, có giọng

### Ràng buộc kỹ thuật quyết định văn phong

Hộp thoại 320px rộng, font pixel 8px → khoảng **32–36 ký tự/dòng**, **2–3 dòng/khung**. Nghĩa là **~70–100 ký tự mỗi lần bấm**.

Đó là khoảng **1–2 câu tiếng Việt ngắn**. Không hơn.

### Quy tắc viết

| Quy tắc | ❌ Sai | ✅ Đúng |
|---|---|---|
| **1 ý mỗi khung** | "Đèn tắt ba đêm rồi và ta nghĩ có thể là do mấy viên Lửa Muối trong hầm đã bị ai lấy đi, cháu nên xuống đó kiểm tra" | Khung 1: "Đèn tắt ba đêm rồi."<br>Khung 2: "Lửa Muối trong hầm... có kẻ lấy mất." |
| **Cắt lời chào** | "Xin chào! Ta là ông Bảy, người trông coi..." | "Đêm nay đèn không sáng, cháu à." |
| **Giọng riêng cho mỗi NPC** | Mọi NPC nói giống nhau | Ông Bảy: cụt, gọi "cháu". Bà Tám: hát, nói vòng. Thằng bé: nhanh, nhiều "á" |
| **Thông tin ở câu đầu** | "Ừm... để ta nghĩ đã... à phải rồi, chìa khóa..." | "Ta giữ chìa khóa cổng hầm." |
| **Không giải thích cơ chế game** | "Nhấn E để nhặt vật phẩm nhé!" | Đặt item ở chỗ dễ thấy, để prompt UI làm việc đó |
| **Dùng khoảng lặng** | Nhồi chữ | Một khung chỉ có "..." **rất** hiệu quả |

### Ví dụ: cùng một NPC, 3 cách viết

**Bản nháp (tệ)** — 1 khung, 210 ký tự:

> "Xin chào cháu bé! Ta là ông Bảy, người canh giữ hải đăng của làng này đã hơn bốn mươi năm. Hiện tại ngọn đèn đã tắt ba đêm liền vì có kẻ đã đánh cắp ba viên Lửa Muối trong hầm bên dưới, và ta cần cháu giúp lấy lại."

**Bản 2 (khá)** — 3 khung:

> "Đèn tắt ba đêm rồi."
> "Có kẻ lấy Lửa Muối dưới hầm."
> "Cháu xuống lấy lại được không?"

**Bản 3 (tốt)** — 3 khung, có giọng, có cảm xúc, gieo mục tiêu gián tiếp:

> "Đêm nay đèn không sáng, cháu à."
> "Ba đêm rồi. Thuyền ngoài kia không thấy đường về."
> "..." *(khoảng lặng — người chơi tự nghĩ đến cha mình)*

Bản 3 **ít thông tin hơn** nhưng gây ấn tượng mạnh hơn. Thông tin chi tiết (Lửa Muối ở đâu, cần bao nhiêu) để dành cho lần nói chuyện thứ hai, hoặc để người chơi tự phát hiện trong hầm.

### Bảng giọng nhân vật (điền trước khi viết dòng nào)

| NPC | Nói gì | Nói kiểu gì | Từ đặc trưng | Không bao giờ |
|---|---|---|---|---|
| Ông Bảy | Chìa khóa, cảnh báo hầm | Cụt, chậm, dứt câu | "cháu à", "đi đi" | Không giải thích dài |
| Bà Tám | Bài hát manh mối | Vòng vo, hay hát | "hồi đó", "bà không hiểu" | Không nói trực tiếp đáp án |
| Thằng Út (bé 8 tuổi) | Tin vặt, hài | Nhanh, ngắt câu | "á!", "chị ơi" | Không nói gì buồn |
| Nhân vật chính | (không thoại) | — | — | **Im lặng hoàn toàn** |

> **Nhân vật chính im lặng** là lựa chọn tốt cho game ngắn: người chơi tự lấp cảm xúc vào, và bạn không phải viết thêm 100 dòng thoại. Đây là kỹ thuật của Zelda, không phải cắt góc.

---

## 7.8 Pacing: nhịp của 5 phút

| Phút | Người chơi làm gì | Cảm xúc | Kỹ thuật |
|---|---|---|---|
| 0:00–0:20 | Spawn ở bến đêm, nhạc buồn, hải đăng tối phía xa | Tò mò, hơi lo | Landmark ngay khung đầu. Không tutorial text |
| 0:20–0:40 | Đi lên, nhặt cá (prompt dạy cơ chế) | "Ok, mình biết chơi" | Item đầu tiên nằm ngay đường đi |
| 0:40–1:30 | Nói chuyện 2–3 NPC, biết mục tiêu | Có việc để làm | Bà Tám gieo manh mối **trước** khi cần |
| 1:30–1:45 | Mở cổng hầm bằng chìa | Thỏa mãn nhỏ đầu tiên | Payoff nhanh cho đố dễ nhất |
| 1:45–2:15 | P1: tối, nhạc đổi, thấy thùng | Căng lên | Đổi nhạc = đổi chương. Rất rẻ, rất hiệu quả |
| 2:15–3:00 | P2: đứng bệ → hé cửa → đẩy thùng | "À!" lần 1 | Feedback tự dạy |
| 3:00–3:15 | Nhặt đèn dầu, save point | Nghỉ, an toàn | Save point = nhịp thở, đặt trước đoạn khó nhất |
| 3:15–4:15 | P3: 3 đuốc, thử, sai, nhớ bài hát | "À!" lần 2 (mạnh nhất) | Manh mối từ màn 1 → cảm giác thông minh |
| 4:15–4:45 | Leo lên đỉnh, thắp đèn | Cao trào | Nhạc lên, glow bùng, camera pull-back |
| 4:45–5:00 | Thấy đèn thuyền ngoài biển. Fade. Credits | Trả nghĩa | Trả lời câu hỏi gieo ở phút 0:40 |

Quy luật nhịp: **một "à!" mỗi 60–90 giây.** Ít hơn → nhàm. Nhiều hơn → mệt.

### Ba công cụ pacing rẻ nhất

1. **Đổi nhạc khi đổi khu vực** — hiệu quả nhất trên mỗi đồng bỏ ra
2. **Đổi ánh sáng/palette khi đổi khu vực** — làng xanh lạnh, hầm nâu cam, đỉnh trắng vàng
3. **Save point trước đoạn khó** — vừa là cơ chế, vừa là tín hiệu "sắp có chuyện"

---

## 7.9 Từ design tới build: bảng thi công

Dịch design thành checklist thi công. Đây là file bạn dán cho AI (chương 09).

| # | Việc | Chương | Phụ thuộc | Xong khi |
|---|---|---|---|---|
| 1 | Blockout town + dungeon 3 phòng | 05 | — | Đi được hết map, timing đúng 7.8 |
| 2 | 9 flag trong GameState | 06 | — | `debug_dump()` in ra đúng |
| 3 | 6 ItemData `.tres` | 06 | — | `ItemDB.get_item("fish")` trả về đúng |
| 4 | ItemPickup: cá (bến), đèn dầu (P2) | 06 | 3 | Nhặt được, không hồi sinh |
| 5 | NPC ông Bảy + dialog 3 trạng thái | 06 | 2 | Đủ 3 nhánh chạy đúng |
| 6 | NPC bà Tám + dialog 3 trạng thái | 06 | 2 | Nhắc lại được bài hát |
| 7 | NPC thằng Út (trang trí, 1 trạng thái) | 06 | 2 | — |
| 8 | LockedGate cổng hầm | 06 | 3,5 | Khóa → mở → giữ mở sau load |
| 9 | Portal town ↔ dungeon | 06 | 8 | Đi lại giữ inventory |
| 10 | PushableCrate + bệ + cửa P2 | 05,06 | 1 | Đẩy được, cửa mở, reset được |
| 11 | 3 Torch + TorchPuzzle | 06 | 4 | Sai → reset. Đúng → cửa mở |
| 12 | SavePoint P2 | 06 | 2 | Save→thoát→load đúng chỗ |
| 13 | HintSystem | 07 | 2 | Đứng im 90s → thấy gợi ý đúng |
| 14 | Level đỉnh hải đăng + ending | 05,06 | 11 | Thắp đèn → cutscene → credits |
| 15 | Nhạc 3 khu + 8 SFX | 08 | — | Đổi khu → đổi nhạc |
| 16 | Main menu + credits | 06 | 12 | Chơi mới / Tiếp tục |
| 17 | Export desktop + web | 10 | tất cả | Chạy trên máy khác |

---

## 7.10 Bài tập

1. Viết bảng giọng nhân vật (7.7) cho **3 NPC của bạn**. Mỗi ô 1 dòng.
2. Viết dialog lần-đầu cho 1 NPC theo đúng giới hạn 70–100 ký tự/khung. Đếm ký tự thật.
3. Chạy checklist 7.4 trên **một** câu đố của bạn. Nếu có ô nào không tick được → sửa design, đừng code.
4. Vẽ bảng pacing (7.8) cho game của bạn. Đánh dấu chỗ mỗi "à!". Nếu > 120s không có "à!" nào → thêm một cái.
5. Liệt kê mọi dead state có thể của game bạn. Với mỗi cái, viết cách phòng.
6. Đưa game (dù còn blockout) cho **một người chưa biết gì** chơi. **Không nói gì.** Ghi lại chính xác chỗ họ bị kẹt và họ nói gì. Đây là dữ liệu giá trị nhất bạn có thể có.

---

## 7.11 Lỗi thường gặp (thiết kế)

| Lỗi | Biểu hiện | Cách sửa |
|---|---|---|
| **Manh mối chỉ nói 1 lần** | Người tester kẹt, không biết tra lại đâu | Dialog 3 trạng thái cho mọi NPC quan trọng |
| **"Moon logic"** (logic chỉ tác giả hiểu) | Tester thử 20 thứ vô nghĩa | Đọc lại: giải pháp có suy ra được từ thông tin trong game không? |
| **Quá nhiều fetch quest** | Cảm giác làm việc nhà | Đa dạng loại đố (7.4) |
| **Dead state** | Tester phải load lại save | 7.6 |
| **Không có feedback khi sai** | Tester không biết mình đang làm đúng hướng | Mọi tương tác phải có phản hồi, kể cả phản hồi "không được" |
| **Dialog quá dài** | Tester bấm liên tục không đọc | Giới hạn 100 ký tự/khung, cắt 50% chữ |
| **Tutorial bằng chữ** | Tester bỏ qua rồi không biết chơi | Dạy bằng level design: item đầu tiên nằm chắn đường |
| **Map quá lớn** | Đi bộ nhiều, nhàm | Đo thời gian đi. > 30s giữa 2 điểm quan trọng = quá xa |
| **Không đổi gì khi giải xong đố** | Tester không chắc đã giải được | Cửa mở + SFX + nhạc + ánh sáng — dùng cả 4 |
| **Cốt truyện gieo mà không trả** | Cảm giác dở dang | Mọi câu hỏi gieo ở nhịp 1 phải trả ở nhịp 3 |
| **NPC không có việc gì làm** | Tester nói chuyện xong rồi bỏ qua | Cắt NPC đó, hoặc cho họ 1 manh mối/1 câu hài đáng nhớ |
