import asyncio
import json
import os
from aiohttp import web
import aiohttp
import discord
from discord.ext import commands
from discord.ui import Button, Modal, TextInput, View

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "typing_delay": 1.0,
    "msg_delay": 0.5,
    "vc_reconnect_delay": 3.0,
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "typing_delay": float(data.get("typing_delay", DEFAULT_SETTINGS["typing_delay"])),
                    "msg_delay": float(data.get("msg_delay", DEFAULT_SETTINGS["msg_delay"])),
                    "vc_reconnect_delay": float(data.get("vc_reconnect_delay", DEFAULT_SETTINGS["vc_reconnect_delay"])),
                }
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(cfg: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


config = load_settings()

# Danh sách câu mẫu
MESSAGES = [
    "sao m rụng ngay khi anh đến r",
    "mồ côi thắp hương cha mẹ trc khi chửi chưa",
    "mồ côi không cha mẹ đổ thừa cay bố m kìa",
    "tao thánh chửi mà :))",
    "tây tạng béo mỡ cha chọc chết tươi rồi😹",
    "m còn trò j thể hiện nhanh lên ơ kìa",
    "óc chó ko trình lên đây sủa mạnh mẽ lên anh chơi mày cả ngày mà😹",
    "ơ hay óc chó ơi m sủa mạnh mẽ lên sao lại bị dập rồi",
    "lêu lêu thằng ngu không làm gì được cay anh kìa",
    "haha óc chó gà bị chửi cay cú ớt mẹ rồi: )))",
    "óc chó ngu nghèo cay cha bán mạng đi chửi cha má kìa: ))))",
    "m chạy đâu v con chó ngu ơi không được chạy mà: (((",
    "ai đụng gì óc chó để nó sợ rồi chạy thục mạng kìa",
    "culi ngu bị anh chửi té tát nước vô mặt m kìa: )))",
    "culi bị chửi mất xác kìa😹😹😹",
    "thằng nguuu giết cha bóp cổ má để cầu win anh à 😏 👉",
    "hi vọng làm dân war của con ngu bị t dập tắt từ khi nó sủa điên trước mặt t ae=)))",
    "bà nội m loạn luân vs bố m còn ông ngoại m loạn luân vs mẹ m mà thg não cún =)) 🤪",
    "Cn thú mại dâm bán dâm mà như bán trinh hoa hậu v🤣",
    "con ngu nứng quá đến cả con mom nó gần u60 r nó vẫn ko tha=))",
    "Mẹ mày làm con chó canh cửa cho nhà t mà🤣",
    "đáp ngôn nhanh hơn tý đc k tk ngu xuẩn🌬 🤢🤢",
    "bắt quả tang con chó chạy bố nè",
    "não cún chỉ biết âm thầm seen và ôm gối khóc mà huhuh 👈😜",
    "con cave này adr 16gb đg kiếm tiền mua ip đk🤣🤣",
    "Vào 1 hôm bỗng con đĩ mẹ nhà m die thì lúc đó cha làm bá chủ sàn mẹ r :))",
    "con đĩ mẹ mày bất lực vì bị tao chửi mà chỉ biết câm lặng:))",
    "mẹ mày bị t đụ đột quỵ ngoài nhà nghỉ kìa đem hòm ra nha",
    "đem hai cái mày với con mẹ m luôn nha",
    "thời gian trôi qua để cảm nhận nỗi đau đi ửa à",
    "nhai t chặt đầu con đĩ má m ra đó",
    "thằng ngu lgbt da đen sủa lẹ ai cko mày câm",
    "thằng sex thú đang cố làm cha cay hả thằng bại não",
    "tao miễn nhiễm mà thằng ngu",
    "Anh Bá Vcl Lỡ Đá Chết Mẹ mày Rồi  😝 👎",
    "Mẹ Mày Bị Cha Đụ Từ Nam Vào Đến Bắc Mà 🤪 👊",
    "Mẹ Mày Banh Háng Cho Khách Đụ Kìa Thằng Óc",
    "Tao Lỡ Cho Mẹ Mày Bú Cu Tao Rồi Sướng Vãi Cặc🧐 🤙",
    "Lêu Lêu Nhìn Cha Đụ Mẹ Mày Ko Làm Được Gì À Đừng Có Cay Cha Nha 😝 👎",
    "bị tao khủng bố quá nát mẹ cái hộp sọ với não luôn rồi à =))",
    "m là con đĩ đầu đinh giết má để loạn luân với bố mà con khốn",
    "văn thơ anh lai láng để con mẹ m dạng háng mỗi đêm =)))",
    "qua sông thì phải bắc cầu kiều con mẹ mày muốn làm đĩ phải yêu chiều các anh mà 🤣👈",
    "con lồn ngu này hay đạp xe đạp ngang nhà tao bị tao chọi đá về méc mẹ mà🤣",
    "thằng ngu này đang đi bộ bị t đánh úp nó về mách mẹ mà ae 🤣🤣",
    "thằng này ăn và khen chubin anh singu khen ngon quá=))",
    "thằng đầu đinh ở nhà lá mà ae nó mơ ước dc ở biệt thự như tui:))",
    "cả họ nhà mày phải xếp hàng lần lượt bú dái t mà🤣🤣",
    "thằng ảo war bị tao chửi cố gắng phản kháng nhưng nút home k cho phép mày cay quá đập cmn máy 🤣👈",
    "Sống như 1 con chó ngu dốt như lũ phèn ói chợ búa cầm dao múa kiếm",
    "Cha mày hóa thân thành hắc bạch vô thường cha mày bắt hồn đĩ mẹ mày xuống chầu diêm vương",
    "Nghèo bần hèn bị cha mày đứng trên đạp đầu lũ đú chúng mày cha đi lên",
    "Đú má mày tới tháng xịt nước máu kinh cho thk cha mày uống",
    "mày đi học bị bạn bè chê xài nút home mày cay quá về đánh đập bà già kiu bả làm đĩ để có tiền mua dt mới đi sĩ với bạn bè =))",
    "Con điếm phò mã bị cha mày cầm cái cây chà bồn cầu cha chà nát lồn mày nè",
    "Đừng có lên mạng xã hội tạo nét mà bị anh hành là mếu máo đi cầu cứu ngay",
    "mày thấy anh chửi thấm quá và nghĩ trong đầu là : anh này bá vcl đéo chửi lại nó đâu:)))",
    "thằng này đang ăn bị t đứng trên nóc nhà nó t ỉa trúng bát cơm nó luôn mà ae",
    "mày bí ngôn tới nỗi phải lên gg ghi : những câu chửi nhau hay nhất để phản kháng tao mà🤣👈",
    "mày thấy a chửi hay quá nên xin làm đệ của anh để được kéo làm hw:)))",
    "mày bị chửi tới nỗi tăng huyết áp phải cầu xin anh tha thứ:)))",
    "người yêu nó bị t đụ rên ư ử khen ku a  to và dài thế:))))",
    "mẹ nó khen cặk t to chấp nhận bỏ ba nó vì ông ấy ysl:)))",
    "cha nó ôm hận t lắm chỉ biết đứng ôm cặk khóc trong vô vọng:)))",
    "mẹ nó bị t đụ chán chê xong bị t trap t yêu người mẫu mà 🤣👈",
    "con bướm trâu bị gái có cu yêu qua mạng trap=)))Gbao w kayros",
    "trăng kia ai vẽ mà tròn loz con mẹ m bị ai địt mà mòn 1 bên 🤣",
    "mẹ m có phải còn búp bê tình dục để a lục đục mỗi đêm k 😏?",
    "mẹ m thì xóc lọ cho t còn người ta thì kính lão đắc thọ",
    "m tin bố lấy yamaha bố đề số 3 bố tông vào loz cn đĩ mẹ m k",
    "m gặp các anh đây toàn đấng tối cao a cầm con dao a đâm a thọc a chọc vào cái lỗ loz cn mẹ m mà 🤣👈",
    "cha m lấy gạch ống chọi nát cái đầu mu lồn mẹ mày giờ con bẻm đú",
    "con mồ côi mày mà rớt là tao lấy chiếc xe rùa t cán lòi mu lồn mẹ m đó gán trụ nha",
    "cú đấm sấm sét của anh mtrung đấm nát cái lồn mẹ thằng chó đú nhây như mày🤣👈",
    "cú đá cuồng phong đá bung cái lồn mẹ mày nè thằng não cặc🤣👈",
    "anh lấy cái ô tô anh đâm thẳng dô cái lồn con gái mẹ thằng súc vật như m",
    "hôm nay anh sẽ thay trời hành đạo anh cạo nát cái lông lồn con gái mẹ mày đó nghe chưa",
    "anh đẹp trai hai mái quay qua bên trái đái nát dô cái bàn thờ gái mẹ nghe hong con dog=))",
    "con đĩ eo di bi ti bị mẹ mày hành cho tới đột quỵ k có tiền lo tang lễ phải quỳ qua háng tao van xin tao cho tiền đúng kh",
    "thằng cặc chứng kiến cái cảnh mẹ nó bị t cầm bật lửa đốt từng cộng lông bướm:)))",
    "Anh gõ chết con đĩ mẹ mày giờ mày sủa ngôn có st tý coi em nhìn em phèn dạ anh mày chửi luôn ông bà mày đái lên mặt mày nhé con sút vật yếu kém",
    "thằng óc cặc bị tao ném xuống ao nhưng béo quá bị chết chìm🐕",
    "mày bị tao hành hung cho sắp đột tử rồi kìa kêu con đĩ mẹ mày qua cứu vãn mày lẹ đi không là tao cho mày nằm quan tài gào khóc thảm thiết trong đó liền ngay 3s nè con đĩ phế",
    "nhanh lên con chó lồn khai khắm=))",
    "con gái mẹ mày die dưới tay bọn anh kìa",
    "thằng bẻm bị t thọc cặc lên ổ cứng phát não rớt ra ngoài=)))",
    "cạn bã của XH mà tưởng mình hay hã con thú🤣💨",
    "thằng óc dái khi nghe tin cha nó chết kiểu: úi úi thằng già này cuối cùng cũng chết r vui vl=))",
    "thằng lồn ảo anime bật gear 5 lên địt con già nó trước bàn thờ tổ tiên=))",
    "anh cha dượng của bọn mày mà tụi bú cứt 🤣",
    "đây là suy nghĩ của con ngu sau khi nó bị tao sỉ nhục trong đầu nó bây giờ kiểu: quân tử trả thù 10 năm chưa muộn :)))))",
    "thằng ngu bị tao áp đảo từ phút 1 tới giờ nó k có cơ hội để sủa luôn ae=)))",
    "thằng đú bot mời ae nó sang nhà đụ bà già nó free vì hôm nay là ngày vui vì cha nó mới qua đời=))",
    "thằng cặc bị tao hạ đo ván sau 1 cú sút ngoạn mục đến từ vị trí anh trung hw=)))",
    "thằng óc cặc đòi va anh và cái kết bị anh chửi chạy khắp nơi=))",
    "mẹ mày bị t địt rách màn trinh mà🤪",
    "🤭🤭Mày bê đê ngũ sắc dell công khai bị tao chọc quá máu cặc mày dồn lên não choa mày chết hả",
    "nhà thằng đú này nghèo không có tiền chơi gái nên phải loạn luân luôn với mẹ nó để giải khát cơn thèm thuồng",
    "thằng cầm thú loạn luân some với mẹ ruột và ba ruột còn quay clip",
    "m bị óc cứt hay sao z hả mà t nói m dell hiểu hay bố phải nhét cứt vào đầu m thì m mới thông hả con óc lồn ơi",
    "Một lũ xam cu lên đây đú ửa ngôn thì nhạt như cái nước lồn của con đỉ mẹ cm v hăng lên đi con mẹ mày bị t xé rách mu sao chối ????",
    "bà già mày bị tao treo cổ lên trên trần nhà mà?",
    "thằng bất tài vô dụng sủa mạnh lên đi",
    "cố gắng để win tao nhá",
    "tao bất bại mà thằng ngu?",
    "mẹ mày bị t đầu độc đến chết mà",
    "mày đàn ông hay đàn bà yếu đuối vậy",
    "con chó đầu đinh bị anh cầm cái đinh ba a thọc vào lỗ nhị nó mà ae =))",
    "thằng như mày xứng đáng ăn cứt tao á",
    "Mấy Con Thú Sài Tool Cha Đòi Bem Cha À",
    "Nghe Cha Chửi Con Gái Mẹ Mày Nè Con Ngu",
    "Mẹ Mày Bị Tao Lấy Phóng Lợn Chọt Dô Mu Lồn Khi Đang Đi Làm Gái Ở Ngã 3 Trần Duy Hưng🤣👈",
    "con mẹ m nghe tin m loạn luân vs bố m nên lấy dao cắt cổ tự tử r kìa con ngu :))",
    "m tìm câu nào sát thương tí được k thằng nghịch tử đâm bố đụ mẹ :)) 🤣",
    "óc chó bị anh chửi nhớ cha nhớ mẹ nhớ kiếp trước kìa😹😹😹",
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

active_spam_tasks: list[asyncio.Task] = []
active_vc_tasks: list[asyncio.Task] = []
view_registered = False


# ---------------------------------------------------------
# Tiến trình Spam
# ---------------------------------------------------------
async def run_spam_task(tokens: list[str], channels: list[str], mention_ids: list[str], typing_delay: float, msg_delay: float):
    headers_list = [
        {"Authorization": t.strip(), "Content-Type": "application/json"}
        for t in tokens
        if t.strip()
    ]
    channel_list = [c.strip() for c in channels if c.strip()]
    if not headers_list or not channel_list or not MESSAGES:
        return

    mention_text = " ".join([f"<@{uid.strip()}>" for uid in mention_ids if uid.strip()])
    semaphore = asyncio.Semaphore(5)
    msg_index = 0
    step = 0

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            while True:
                headers = headers_list[step % len(headers_list)]
                channel_id = channel_list[step % len(channel_list)]
                msg = MESSAGES[msg_index % len(MESSAGES)]
                full_msg = f"{mention_text} {msg}".strip() if mention_text else msg

                typing_url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
                send_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

                try:
                    async with semaphore:
                        if typing_delay > 0:
                            async with session.post(typing_url, headers=headers) as resp:
                                if resp.status == 429:
                                    retry_after = (await resp.json()).get("retry_after", 1.0)
                                    await asyncio.sleep(float(retry_after))
                            await asyncio.sleep(typing_delay)

                        async with session.post(send_url, json={"content": full_msg}, headers=headers) as resp:
                            if resp.status == 429:
                                try:
                                    data = await resp.json()
                                    retry_after = float(data.get("retry_after", 2.0))
                                except Exception:
                                    retry_after = 2.0
                                await asyncio.sleep(retry_after)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass

                msg_index += 1
                step += 1
                await asyncio.sleep(max(0.0, msg_delay))
    except asyncio.CancelledError:
        pass


# ---------------------------------------------------------
# Tiến trình Treo Room Voice (Watchdog + Session Keep-Alive)
# ---------------------------------------------------------
async def keep_alive_voice(token: str, channel_id: str):
    ws_url = "wss://gateway.discord.gg/?v=10&encoding=json"
    headers = {"Authorization": token.strip(), "Content-Type": "application/json"}

    while True:
        guild_id = None
        last_seq = None
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(f"https://discord.com/api/v10/channels/{channel_id}", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        guild_id = data.get("guild_id")

                if not guild_id:
                    await asyncio.sleep(max(1.0, config["vc_reconnect_delay"]))
                    continue

                async with session.ws_connect(ws_url, heartbeat=None) as ws:
                    await ws.send_json({
                        "op": 2,
                        "d": {
                            "token": token.strip(),
                            "capabilities": 509,
                            "properties": {
                                "os": "Android",
                                "browser": "Discord Android",
                                "device": "Android",
                            },
                        },
                    })

                    await ws.send_json({
                        "op": 4,
                        "d": {
                            "guild_id": guild_id,
                            "channel_id": channel_id,
                            "self_mute": True,
                            "self_deaf": True,
                        },
                    })

                    heartbeat_interval = 41.25

                    async def sender(websocket):
                        try:
                            while not websocket.closed:
                                await asyncio.sleep(heartbeat_interval)
                                await websocket.send_json({"op": 1, "d": last_seq})
                        except Exception:
                            pass

                    send_task = asyncio.create_task(sender(ws))

                    try:
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = msg.json()
                                if data.get("s") is not None:
                                    last_seq = data.get("s")
                                op = data.get("op")
                                if op == 10:
                                    heartbeat_interval = data["d"].get("heartbeat_interval", 41250) / 1000.0
                                elif op == 7 or op == 9:
                                    break
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                break
                    finally:
                        send_task.cancel()

        except asyncio.CancelledError:
            break
        except Exception:
            pass

        await asyncio.sleep(max(1.0, config["vc_reconnect_delay"]))


async def run_vc_task(tokens: list[str], channel_id: str):
    for token in tokens:
        task = asyncio.create_task(keep_alive_voice(token.strip(), channel_id.strip()))
        active_vc_tasks.append(task)


# ---------------------------------------------------------
# Modal Setting Delay
# ---------------------------------------------------------
class DelaySettingsModal(Modal, title="Cài Đặt Delay Hệ Thống"):
    typing_delay_input = TextInput(
        label="Delay giả typing (giây)",
        style=discord.TextStyle.short,
        default=str(config["typing_delay"]),
        required=True,
    )
    msg_delay_input = TextInput(
        label="Delay giữa mỗi tin nhắn (giây)",
        style=discord.TextStyle.short,
        default=str(config["msg_delay"]),
        required=True,
    )
    vc_reconnect_input = TextInput(
        label="Delay chờ kết nối lại Voice (giây)",
        style=discord.TextStyle.short,
        default=str(config["vc_reconnect_delay"]),
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            t_delay = max(0.0, float(self.typing_delay_input.value.strip()))
            m_delay = max(0.0, float(self.msg_delay_input.value.strip()))
            v_delay = max(1.0, float(self.vc_reconnect_input.value.strip()))
        except ValueError:
            await interaction.response.send_message(
                "❌ Vui lòng nhập số hợp lệ (ví dụ: `0.5`, `1.0`, `2.5`).",
                ephemeral=True,
            )
            return

        config["typing_delay"] = t_delay
        config["msg_delay"] = m_delay
        config["vc_reconnect_delay"] = v_delay
        save_settings(config)

        await interaction.response.send_message(
            f"✅ **Đã lưu cài đặt delay:**\n"
            f"• Delay giả typing: `{t_delay}s`\n"
            f"• Delay giữa tin nhắn: `{m_delay}s`\n"
            f"• Delay reconnect voice: `{v_delay}s`",
            ephemeral=True,
        )


# ---------------------------------------------------------
# Modal Spam
# ---------------------------------------------------------
class SpamModal(Modal, title="Cấu hình Spam Discord"):
    tokens_input = TextInput(
        label="Token (Ngăn cách bằng dấu phẩy)",
        style=discord.TextStyle.paragraph,
        placeholder="token1, token2...",
        required=True,
    )
    channels_input = TextInput(
        label="ID Kênh (Ngăn cách bằng dấu phẩy)",
        style=discord.TextStyle.short,
        placeholder="id_kenh_1, id_kenh_2...",
        required=True,
    )
    tags_input = TextInput(
        label="ID Tag (Để trống nếu không tag)",
        style=discord.TextStyle.short,
        required=False,
    )
    delay_input = TextInput(
        label="Delay giả typing / tin nhắn (vd: 1.0, 0.5)",
        style=discord.TextStyle.short,
        default=f"{config['typing_delay']}, {config['msg_delay']}",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        tokens = [t.strip() for t in self.tokens_input.value.split(",") if t.strip()]
        channels = [c.strip() for c in self.channels_input.value.split(",") if c.strip()]
        mention_ids = [m.strip() for m in self.tags_input.value.split(",") if m.strip()]

        raw_delays = [d.strip() for d in self.delay_input.value.split(",") if d.strip()]
        try:
            typing_delay = max(0.0, float(raw_delays[0])) if len(raw_delays) >= 1 else config["typing_delay"]
            msg_delay = max(0.0, float(raw_delays[1])) if len(raw_delays) >= 2 else config["msg_delay"]
        except ValueError:
            typing_delay = config["typing_delay"]
            msg_delay = config["msg_delay"]

        await interaction.response.send_message(
            f"⚡ **Đã kích hoạt Spam!** (Typing: `{typing_delay}s` | Msg delay: `{msg_delay}s`) — Gõ `!stopsp` để dừng.",
            ephemeral=True,
        )
        task = asyncio.create_task(run_spam_task(tokens, channels, mention_ids, typing_delay, msg_delay))
        active_spam_tasks.append(task)


# ---------------------------------------------------------
# Modal Treo Room
# ---------------------------------------------------------
class VoiceModal(Modal, title="Cấu hình Treo Room Voice 24/7"):
    tokens_input = TextInput(
        label="Token tài khoản (Ngăn cách bằng dấu phẩy)",
        style=discord.TextStyle.paragraph,
        placeholder="token1, token2...",
        required=True,
    )
    channel_id_input = TextInput(
        label="ID Phòng Voice",
        style=discord.TextStyle.short,
        placeholder="Nhập ID Phòng Voice...",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        tokens = [t.strip() for t in self.tokens_input.value.split(",") if t.strip()]
        channel_id = self.channel_id_input.value.strip()

        await interaction.response.send_message(
            f"🎧 **Đã bật Treo Room cho {len(tokens)} tài khoản!** (Reconnect delay: `{config['vc_reconnect_delay']}s`) — Gõ `!stoprom` để dừng.",
            ephemeral=True,
        )
        await run_vc_task(tokens, channel_id)


# ---------------------------------------------------------
# Persistent View
# ---------------------------------------------------------
class MenuView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Cấu Hình & Chạy Spam", style=discord.ButtonStyle.green, custom_id="btn_spam_persistent")
    async def spam_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SpamModal())

    @discord.ui.button(label="🎧 Cấu Hình & Treo Room", style=discord.ButtonStyle.blurple, custom_id="btn_voice_persistent")
    async def voice_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(VoiceModal())

    @discord.ui.button(label="⚙️ Cài Đặt Delay", style=discord.ButtonStyle.gray, custom_id="btn_delay_persistent")
    async def delay_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(DelaySettingsModal())


# ---------------------------------------------------------
# Lệnh Bot
# ---------------------------------------------------------
@bot.event
async def on_ready():
    global view_registered
    if not view_registered:
        bot.add_view(MenuView())
        view_registered = True
    print(f"=== Bot đã sẵn sàng dưới tên {bot.user} ===")


@bot.command(name="menu")
async def menu_command(ctx):
    embed = discord.Embed(
        title="🌊 TOOL QUẢN LÝ DISCORD 🌊",
        description=(
            f"• **Delay giả typing**: `{config['typing_delay']}s`\n"
            f"• **Delay giữa tin nhắn**: `{config['msg_delay']}s`\n"
            f"• **Delay reconnect voice**: `{config['vc_reconnect_delay']}s`"
        ),
        color=discord.Color.purple(),
    )
    embed.add_field(
        name="📘 Hướng dẫn sử dụng",
        value=(
            "• Bấm **🚀 Cấu Hình & Chạy Spam** để chạy spam.\n"
            "• Bấm **🎧 Cấu Hình & Treo Room** để treo voice.\n"
            "• Bấm **⚙️ Cài Đặt Delay** để chỉnh delay mặc định.\n"
            "• Lệnh dừng spam: `!stopsp` | Dừng voice: `!stoprom`"
        ),
        inline=False,
    )
    await ctx.send(embed=embed, view=MenuView())


@bot.command(name="stopsp")
async def stop_spam(ctx):
    global active_spam_tasks
    if not active_spam_tasks:
        await ctx.send("⚠️ Không có tiến trình spam nào đang chạy!")
        return
    count = len(active_spam_tasks)
    for task in active_spam_tasks:
        task.cancel()
    active_spam_tasks.clear()
    await ctx.send(f"🛑 **Đã dừng thành công {count} tiến trình Spam!**")


@bot.command(name="stoprom")
async def stop_room(ctx):
    global active_vc_tasks
    if not active_vc_tasks:
        await ctx.send("⚠️ Không có tài khoản nào đang treo room!")
        return
    count = len(active_vc_tasks)
    for task in active_vc_tasks:
        task.cancel()
    active_vc_tasks.clear()
    await ctx.send(f"🛑 **Đã ngắt kết nối và dừng treo room cho {count} tài khoản!**")


# ---------------------------------------------------------
# Web Server cho Render Web Service
# ---------------------------------------------------------
async def start_web_server():
    app = web.Application()

    async def handle_root(request):
        return web.Response(text="OK - Service is running")

    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_root)

    port = int(os.getenv("PORT", "10000"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"=== Web server đang chạy tại cổng {port} ===")


async def main():
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Thiếu biến môi trường BOT_TOKEN!")

    await start_web_server()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
