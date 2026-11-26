import re
from dataclasses import dataclass, replace
from string import Formatter
from unicodedata import combining, normalize

from auto_registration_system.command import Command


@dataclass(frozen=True)
class GuideText:
    english: str
    vietnamese: str
    chinese: str
    values: tuple[str | int, ...] = ()

    def with_values(self, *values: str | int) -> "GuideText":
        return replace(self, values=values)

    def render(self, language: str, translations: dict[str, str]) -> str:
        if language == "vi":
            template = self.vietnamese
        elif language == "zh":
            template = self.chinese
        else:
            template = translations.get(self.english, self.english)
        return template.format(*self.values)


def fold_accents(text: str) -> str:
    folded = normalize("NFD", text.casefold().replace("đ", "d"))
    return "".join(char for char in folded if not combining(char))


def question_language(question: str) -> str:
    folded = " ".join(fold_accents(question).split())
    if re.match(
            r"(?:please )?(?:i (?:want|would)|how|what|who|when|where|show|register|sign me up|join|"
            r"reserve|remove|deregister|cancel|rename|change my|set my)\b", folded,
    ):
        return "en"
    if re.search(
            r"\b(?:toi muon|minh muon|lam sao|lam the nao|dang k[yi]|danh sach|khung gio|"
            r"biet danh|choi cau|danh cau|du bi|cac suat|vao slot|con cho|xin chao|rut ten|"
            r"xoa ten|xem aka|doi aka|doi ten|sua ten|lam admin|tro thanh admin)\b", folded,
    ):
        return "vi"
    if re.search(r"[\u3400-\u9fff]", question) and not re.search(r"[\u3040-\u30ff\uac00-\ud7af]", question):
        return "zh"
    return "en"


def validate_translations(templates: list[str], translations: object) -> dict[str, str]:
    if not isinstance(translations, list) or len(translations) != len(templates):
        raise ValueError("Unexpected number of guide translations")

    results = {}
    formatter = Formatter()
    for source, translation in zip(templates, translations):
        if not isinstance(translation, str) or not translation.strip() or len(translation) > max(80, 4 * len(source)):
            raise ValueError("Invalid guide translation")
        fields = [field for _, field, _, _ in formatter.parse(source) if field is not None]
        translated_parts = list(formatter.parse(translation))
        translated_fields = [field for _, field, _, _ in translated_parts if field is not None]
        if sorted(translated_fields) != sorted(fields) or any(spec or conversion for _, _, spec, conversion in translated_parts):
            raise ValueError("Translation changed guide placeholders")
        if re.search(r"/[a-zA-Z][a-zA-Z0-9_]*", translation):
            raise ValueError("Translation introduced a command")
        results[source] = translation.strip()
    return results


TEXT = {
    "available_places": GuideText(
        "Shows open places in the registration group.",
        "Xem các slot còn chỗ trong nhóm đăng ký.",
        "查看报名群里还有空位的场次。",
    ),
    "full_list": GuideText(
        "Shows all slots, players, and reserves.", "Xem tất cả các slot, người chơi và người dự bị.",
        "查看所有场次、已报名球员和候补名单。",
    ),
    "register_players": GuideText(
        "Send in the registration group. Separate multiple names with commas. "
        "If the slot is full, players join the pending waitlist and move up as places open.",
        "Gửi lệnh trong nhóm đăng ký. Nếu đăng ký nhiều người, hãy phân cách tên bằng dấu phẩy. "
        "Nếu slot đã đầy, người chơi sẽ vào danh sách chờ và được đưa lên khi có chỗ trống.",
        "在报名群发送此命令。为多人报名时，用逗号分隔姓名。场次已满时，球员进入候补队列，有空位时依次递补。",
    ),
    "reserve_players": GuideText(
        "Adds regular reserves in the registration group. An admin can move them into the lineup.",
        "Thêm người vào danh sách dự bị trong nhóm đăng ký. Quản trị viên có thể chuyển họ vào danh sách chính.",
        "在报名群添加普通候补。管理员可以将他们加入正式名单。",
    ),
    "deregister_players": GuideText(
        "Removes a player from the slot or its waitlist. You can also use the player's position in the lineup.",
        "Xóa người chơi khỏi slot hoặc danh sách chờ. Bạn cũng có thể dùng số thứ tự của người chơi trong danh sách chính.",
        "将球员从该场次或候补名单移除。也可以使用球员在正式名单中的序号。",
    ),
    "view_alias": GuideText("Shows your current alias.", "Xem biệt danh hiện tại của bạn.", "查看你当前的别名。"),
    "set_alias": GuideText(
        "Sets the alias the bot uses for future commands.",
        "Đặt biệt danh mà bot sẽ dùng cho các lệnh sau này.",
        "设置机器人在后续命令中使用的别名。",
    ),
    "rename_existing_registration": GuideText(
        "Use this to find a bot admin. Ask them to correct your name in the active list and repost it with {0}. "
        "{1} changes the alias you use for future commands.",
        "Dùng lệnh này để tìm quản trị viên của bot. Hãy nhờ họ sửa tên bạn trong danh sách hiện tại và đăng lại bằng {0}. "
        "{1} đổi biệt danh dùng cho các lệnh sau này.",
        "用此命令查找机器人管理员。请他们修正当前名单中的姓名，再用 {0} 重新发布。{1} 修改后续命令使用的别名。",
        values=(f"/{Command.COMMAND_NEW}", f"/{Command.COMMAND_AKA}"),
    ),
    "registration_status": GuideText(
        "Shows whether registration is locked, whether the list has slots, and the next release.",
        "Xem đăng ký có bị khóa không, danh sách có slot hay không và thời điểm mở đăng ký tiếp theo.",
        "查看报名是否锁定、名单是否有场次，以及下次开放报名的时间。",
    ),
    "create_or_stage_list": GuideText(
        "Admins can send this in the registration group to replace the active list or in a direct message to stage it.",
        "Quản trị viên có thể gửi lệnh trong nhóm để thay danh sách hiện tại hoặc nhắn riêng cho bot để chuẩn bị danh sách mới.",
        "管理员可以在报名群发送此命令来替换当前名单，或者私聊机器人来预先准备新名单。",
    ),
    "schedule_once": GuideText(
        "Schedules a one-time release. Admins should stage the list first and enter a future Singapore time.",
        "Hẹn giờ mở đăng ký một lần. Quản trị viên cần chuẩn bị danh sách trước và nhập thời điểm trong tương lai theo giờ Singapore.",
        "安排一次开放报名。管理员需先准备名单，再输入一个未来的新加坡时间。",
    ),
    "schedule_weekly": GuideText(
        "Schedules a weekly release. Admins should stage the list first and enter a future Singapore time.",
        "Hẹn giờ mở đăng ký hằng tuần. Quản trị viên cần chuẩn bị danh sách trước và nhập thời điểm trong tương lai theo giờ Singapore.",
        "安排每周开放报名。管理员需先准备名单，再输入一个未来的新加坡时间。",
    ),
    "schedule_test": GuideText(
        "Schedules test releases every 5 minutes. Admins should stage the list first and enter a future Singapore time.",
        "Hẹn giờ mở đăng ký thử nghiệm mỗi 5 phút. Quản trị viên cần chuẩn bị danh sách trước và nhập giờ Singapore trong tương lai.",
        "安排每 5 分钟开放一次测试报名。管理员需先准备名单，再输入一个未来的新加坡时间。",
    ),
    "cancel_once": GuideText(
        "Turns off the one-time release schedule. Admin only.",
        "Tắt lịch mở đăng ký một lần. Dành cho quản trị viên.",
        "关闭单次开放报名的计划。仅限管理员。",
    ),
    "cancel_weekly": GuideText(
        "Turns off the weekly schedule. Admin only.", "Tắt lịch mở đăng ký hằng tuần. Dành cho quản trị viên.",
        "关闭每周开放报名的计划。仅限管理员。",
    ),
    "cancel_test": GuideText(
        "Turns off the test schedule. Admin only.", "Tắt lịch mở đăng ký thử nghiệm. Dành cho quản trị viên.",
        "关闭测试计划。仅限管理员。",
    ),
    "cancel_unknown_mode": GuideText(
        "Check the active release mode first. An admin can cancel it by sending that scheduling command by itself.",
        "Kiểm tra chế độ hẹn giờ đang dùng. Quản trị viên có thể hủy bằng cách gửi riêng lệnh hẹn giờ tương ứng.",
        "先查看当前的开放报名模式。管理员可以单独发送对应的排程命令来取消计划。",
    ),
    "lock_registration": GuideText(
        "Locks registration. Admin only.", "Khóa đăng ký. Dành cho quản trị viên.", "锁定报名。仅限管理员。",
    ),
    "unlock_registration": GuideText(
        "Opens registration. Admin only.", "Mở đăng ký. Dành cho quản trị viên.", "开放报名。仅限管理员。",
    ),
    "reset_active_list": GuideText(
        "Clears the active list. Admin only.", "Xóa danh sách hiện tại. Dành cho quản trị viên.", "清空当前名单。仅限管理员。",
    ),
    "promote_all_reserves": GuideText(
        "Moves all regular reserves onto the pending waitlist and fills open places. Admin only.",
        "Chuyển tất cả người dự bị vào danh sách chờ và lấp các chỗ trống. Dành cho quản trị viên.",
        "将所有普通候补移入候补队列并填补空位。仅限管理员。",
    ),
    "activity_history": GuideText(
        "Retrieves the activity history. Admin only.",
        "Xem lịch sử hoạt động. Dành cho quản trị viên.",
        "查看活动记录。仅限管理员。",
    ),
    "admin_list": GuideText("Shows who the admins are.", "Xem danh sách quản trị viên của bot.", "查看机器人管理员名单。"),
    "request_admin_access": GuideText(
        "Use this to find a bot admin and ask for access. The bot operator grants access by adding your "
        "Telegram username to {0} in {1} and restarting the bot.",
        "Dùng lệnh này để tìm quản trị viên và xin quyền. Người vận hành bot cấp quyền bằng cách thêm tên người dùng "
        "Telegram của bạn vào {0} trong {1} rồi khởi động lại bot.",
        "用此命令查找机器人管理员并申请权限。机器人运营者会将你的 Telegram 用户名添加到 {1} 中的 {0}，然后重启机器人。",
        values=("Config.admins", "config.py"),
    ),
    "command_help": GuideText("Shows the bot's command guide.", "Xem hướng dẫn các lệnh của bot.", "查看机器人命令指南。"),
    "outside_scope": GuideText(
        "That question is outside this bot's scope. I can help with badminton registration commands.",
        "Câu hỏi này nằm ngoài phạm vi của bot. Tôi có thể hướng dẫn bạn dùng các lệnh đăng ký cầu lông.",
        "这个问题超出了机器人的服务范围。我可以帮助你使用羽毛球报名命令。",
    ),
    "unavailable": GuideText(
        "I can only help with using this registration bot. AI help is unavailable right now.",
        "Tôi chỉ có thể hướng dẫn bạn dùng bot đăng ký. Tính năng hỗ trợ AI hiện không hoạt động.",
        "我只能帮助你使用这个报名机器人。AI 帮助暂时不可用。",
    ),
    "busy": GuideText(
        "AI help is busy. Try again later.", "Tính năng hỗ trợ AI đang bận. Vui lòng thử lại sau.",
        "AI 帮助正忙，请稍后再试。",
    ),
    "usage": GuideText(
        "Ask how to use the bot. Questions that need AI are sent to Cloudflare Workers AI.",
        "Hãy hỏi cách dùng bot. Các câu hỏi cần AI sẽ được gửi đến Cloudflare Workers AI.",
        "你可以询问如何使用机器人。需要 AI 的问题会发送给 Cloudflare Workers AI。",
    ),
    "question_length": GuideText(
        "Keep your question to {0} characters or fewer.",
        "Vui lòng giới hạn câu hỏi trong {0} ký tự.",
        "请将问题控制在 {0} 个字符以内。",
    ),
    "multiple_matching_slots": GuideText(
        "Several active slots share that name or label. Check the list in the registration group.",
        "Có nhiều slot hiện tại trùng tên hoặc mã. Hãy kiểm tra danh sách trong nhóm đăng ký.",
        "当前有多个场次使用这个名称或编号。请查看报名群中的名单。",
    ),
    "unknown_slot": GuideText(
        "I couldn't find that slot. Check the active list in the registration group.",
        "Tôi không tìm thấy slot đó. Hãy kiểm tra danh sách hiện tại trong nhóm đăng ký.",
        "找不到该场次。请查看报名群中的当前名单。",
    ),
    "no_signup": GuideText(
        "I couldn't find an active signup or reserve under your current name. "
        "Check the list if you registered under another name.",
        "Tôi không thấy tên hiện tại của bạn trong danh sách đăng ký hoặc dự bị. "
        "Nếu bạn đã đăng ký bằng tên khác, hãy kiểm tra danh sách.",
        "在当前报名或候补名单中找不到你的现用姓名。如果你用了其他名字报名，请查看名单。",
    ),
    "shared_slot_label": GuideText(
        "Some slots share a label. Ask a bot admin to identify the slot you want to leave.",
        "Một số slot trùng mã. Hãy nhờ quản trị viên xác định slot bạn muốn rút tên.",
        "有些场次共用编号。请向机器人管理员确认你要退出的场次。",
    ),
    "many_signups": GuideText(
        "You have several entries. Find the slot label in the list and include it in your request.",
        "Bạn có nhiều lượt đăng ký. Hãy tìm mã slot trong danh sách và ghi rõ mã đó trong câu hỏi.",
        "你报名了多个场次。请在名单中找到场次编号，并在问题中注明。",
    ),
    "leave_slot": GuideText(
        "Removes your entry from slot {0} ({1}).", "Rút tên bạn khỏi slot {0} ({1}).", "取消你在场次 {0}（{1}）的报名。",
    ),
    "choose_slot": GuideText(
        "Choose the slot you want to leave.", "Chọn slot bạn muốn rút tên.", "请选择你要退出的场次。",
    ),
    "replace_placeholders": GuideText(
        "Replace the placeholders before sending.", "Điền thông tin thật vào mẫu lệnh trước khi gửi.", "发送前请替换命令模板中的占位内容。",
    ),
    "copy_command": GuideText("Copy {0}", "Sao chép {0}", "复制 {0}"),
    "copy_template": GuideText("Copy {0} template", "Sao chép mẫu {0}", "复制 {0} 模板"),
    "copy_leave_slot": GuideText("Copy {0} for slot {1}", "Sao chép {0} cho slot {1}", "复制场次 {1} 的 {0}"),
}
