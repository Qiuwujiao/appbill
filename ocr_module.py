import base64
import os
import requests
import re
from datetime import datetime

API_URL = "https://n1fbx6kdqa79p4n9.aistudio-app.com/layout-parsing"
TOKEN = "3c27c202bc1094a5fd316a252454fb3d29fb92bc"

def ocr_bill_list(image_path):
    try:
        with open(image_path, "rb") as file:
            file_bytes = file.read()
            file_data = base64.b64encode(file_bytes).decode("ascii")

        headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/json"
        }

        required_payload = {
            "file": file_data,
            "fileType": 1,
        }

        optional_payload = {
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
        }

        payload = {**required_payload, **optional_payload}
        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            print("❌ OCR识别失败")
            return []

        result = response.json()["result"]

        all_lines = []
        for res in result["layoutParsingResults"]:
            text = res["markdown"]["text"]
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            all_lines.extend(lines)

        all_times = []
        for line in all_lines:
            time_match = re.search(
                r'(\d{1,2}月\d{1,2}日|\d{2}-\d{2}|\d{4}\.\d{2}\.\d{2})\s*(\d{1,2}:\d{2})?',
                line
            )
            if time_match:
                date_part = time_match.group(1)
                time_part = time_match.group(2) or "00:00"
                all_times.append((date_part, time_part))

        amount_list = []
        for i, line in enumerate(all_lines):
            amount_match = re.search(r'(-\d+\.\d{2})', line)
            if amount_match:
                amount_str = amount_match.group(1)
                amount = float(amount_str)
                if amount < 0:
                    amount_list.append((i, line, amount))

        bills = []
        for (i, line, amount) in amount_list:
            # 商户名修复：去掉金额、末尾的0、无关词
            shop = line.replace(str(amount), "").strip()
            shop = re.sub(r'-\d+\.\d{2}|0$|日用百货|母婴亲子|餐饮美食|文化休闲', '', shop).strip()
            shop = shop if shop else "未知商户"

            matched_time = None
            for j in range(len(all_times)):
                date_part, time_part = all_times[j]
                matched_time = (date_part, time_part)
                all_times.pop(j)
                break

            formatted_time = ""
            if matched_time:
                date_part, time_part = matched_time
                try:
                    if "月" in date_part:
                        month, day = map(int, re.findall(r'\d+', date_part))
                    elif "-" in date_part:
                        month, day = map(int, date_part.split("-"))
                    else:
                        month, day = map(int, date_part.split(".")[1:])
                    year = datetime.now().year
                    formatted_date = f"{year}.{month:02d}.{day:02d}"
                    formatted_time = f"{formatted_date} {time_part}"
                except:
                    formatted_time = ""

            bills.append({
                "shop": shop,
                "time": formatted_time,
                "amount": abs(amount),
                "category": "未分组"
            })

        print(f"✅ 识别完成，共 {len(bills)} 条支出记录")
        return bills

    except Exception as e:
        print(f"❌ 识别出错：{e}")
        return []