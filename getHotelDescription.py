import requests
import json
from concurrent.futures import ThreadPoolExecutor
import configs
import re


"""
<div class="hotelOverview_hotelOverview-container__XwS4Z">
                                        <div class="">
                                            大理全海景无弦苍海云居位于洱海天域别墅区，坐落于大理洱海公园内，倚山靠海而建，环境优美，风景秀丽，不仅有“水月空明泉”、“逍遥台”巧夺天工的人居环境，更有大自然天赐的苍海美景。<br/>
                                            <br/>
                                            这里有拥有十余间客房，面朝苍山洱海，风景如画；海风海韵、日落光影打造一个惬意的休憩空间。<br/>
                                            <br/>同时，这里还集海景，民族特色，美食于一体，配有大堂吧、棋牌室、茶室、餐厅、书吧、露台、多功能宴会厅等公共活动空间，管家式服务提供全方位的呵护。
                                        </div>
                                    </div>
"""


def get_hotel_description_strict(hotelId):
    """使用 requests 获取酒店描述"""
    url = f"https://hotels.ctrip.com/hotels/{hotelId}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html_content = response.text

            # 修复正则表达式：使用更宽松的匹配
            match = re.search(
                r'<div class="hotelOverview_hotelOverview-container__\w+">\s*<div class="">(.*?)</div>\s*</div>',
                html_content,
                re.DOTALL,
            )

            if match:
                description_html = match.group(1)

                # 替换 <br/> 和 <br> 为换行符
                description_text = re.sub(r"<br\s*/?>", "\n", description_html)

                # 移除其他 HTML 标签
                description_text = re.sub(r"<.*?>", "", description_text)

                # 清理多余的空白和换行
                description_text = re.sub(
                    r"\n\s*\n\s*\n+", "\n\n", description_text
                )  # 多个连续换行变为两个
                description_text = re.sub(
                    r"[ \t]+", " ", description_text
                )  # 多个空格变为一个

                return description_text.strip()
            else:
                print(f"未找到匹配的酒店描述内容")
                return ""
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return ""
    except Exception as e:
        print(f"获取酒店描述失败: {e}")
        return ""


def get_hotel_description_relaxed(hotelId):
    """备用方法：更宽松的正则匹配"""
    url = f"https://hotels.ctrip.com/hotels/{hotelId}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html_content = response.text

            # 使用更宽松的正则：匹配整个容器内的内容
            match = re.search(
                r"hotelOverview_hotelOverview-container__\w+[^>]*>(.*?)</div>\s*</div>",
                html_content,
                re.DOTALL,
            )

            if match:
                description_html = match.group(1)

                # 提取所有 div 内的文本
                inner_divs = re.findall(
                    r"<div[^>]*>(.*?)</div>", description_html, re.DOTALL
                )
                if inner_divs:
                    description_html = inner_divs[0]

                # 清理 HTML 标签
                description_text = re.sub(r"<br\s*/?>", "\n", description_html)
                description_text = re.sub(r"<.*?>", "", description_text)
                description_text = re.sub(r"\n\s*\n+", "\n\n", description_text)
                description_text = re.sub(r"[ \t]+", " ", description_text)

                return description_text.strip()
            else:
                return ""
    except Exception as e:
        print(f"获取失败: {e}")
        return ""


if __name__ == "__main__":
    hotel_id = 9532016

    print("方法1:")
    description1 = get_hotel_description_strict(hotel_id)
    print(description1)
    print("\n" + "=" * 50 + "\n")

    print("方法2:")
    description2 = get_hotel_description_relaxed(hotel_id)
    print(description2)
