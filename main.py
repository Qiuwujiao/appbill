from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import TwoLineListItem, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.switch import MDSwitch
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy import platform
import json
import os

# ----------- 相册选图依赖 -----------
from plyer import filechooser  # 跨平台文件选择器
if platform == "android":
    from android.permissions import request_permissions, Permission  # 安卓权限

# 直接导入你已经写好的底层逻辑
from db_helper import *
from ocr_module import ocr_bill_list

init_db()

# 主题配置文件（保存深色/浅色模式）
CONFIG_FILE = "app_config.json"
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"dark_mode": False}, f)

def load_theme():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("dark_mode", False)

def save_theme(dark_mode):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"dark_mode": dark_mode}, f)

# 底部 Tab
class Tab(MDFloatLayout, MDTabsBase):
    pass

# 主界面
class MainLayout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dark_mode = load_theme()
        Clock.schedule_once(self.after_init, 0.1)

        # ----------- 安卓动态申请存储权限 -----------
        if platform == "android":
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

    def after_init(self, dt):
        self.ids.theme_switch.active = self.dark_mode
        self.refresh_bill_list()

    def switch_theme(self, is_active):
        save_theme(is_active)
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if is_active else "Light"

    # ----------- 安卓相册选图 + OCR -----------
    def start_ocr(self):
        # 调用系统相册选图
        filechooser.open_file(
            title="选择账单图片",
            filters=[("图片文件", "*.jpg", "*.jpeg", "*.png")],
            on_selection=self.on_image_selected
        )

    def on_image_selected(self, selection):
        if not selection:
            return
        path = selection[0]
        # 调用你原来的OCR
        bills = ocr_bill_list(path)
        self.ids.bill_result.clear_widgets()
        for b in bills:
            self.ids.bill_result.add_widget(
                OneLineListItem(text=f"{b['shop']} | {b['time']} | {b['amount']}")
            )

    # 保存账单
    def save_bill(self):
        t = self.ids.bill_time.text.strip()
        a = self.ids.bill_amount.text.strip()
        c = self.ids.bill_category.text.strip()
        s = self.ids.bill_shop.text.strip()
        if not t or not a or not c or not s:
            return
        add_bill({
            "time": t,
            "amount": -float(a),
            "type": "支出",
            "category": c,
            "shop": s,
            "remark": "APP录入"
        })
        self.refresh_bill_list()

    # 刷新账单列表
    def refresh_bill_list(self):
        self.ids.bill_list.clear_widgets()
        for b in query_all_bill():
            self.ids.bill_list.add_widget(
                TwoLineListItem(
                    text=f"[{b[4]}] {b[5]}  ￥{abs(b[2]):.2f}",
                    secondary_text=b[1]
                )
            )

# APP 主程序
class BillApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark" if load_theme() else "Light"
        return MainLayout()

if __name__ == "__main__":
    BillApp().run()