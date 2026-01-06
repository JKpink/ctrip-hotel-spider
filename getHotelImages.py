import requests
import json
from concurrent.futures import ThreadPoolExecutor
import configs
import re
from playwright.sync_api import sync_playwright


def get_original_image_url(thumb_url):
    """通用携程图片URL转原图"""
    if not thumb_url:
        return ""

    # 步骤1：移除协议和域名，提取路径部分
    # e.g. images/0235o12000qus0hb0F039_R_150_150_R5_Q70_D.jpg
    path = thumb_url.split("://", 1)[-1].split("/", 1)[-1]

    # 步骤2：提取图片ID（去掉所有 _R_ 开头的参数部分）
    # 修正正则：匹配 images/目录/图片ID_R_参数.jpg/png/
    match = re.match(r"(.+/)?([^/_]+)(_R_.+)?\.(jpg|png|jpeg|webp)", path)
    if match:
        image_id = match.group(2)
        domain = thumb_url.split("://")[1].split("/")[0]
        appendix = match.group(4)
        # 步骤3：构造原图URL
        return f"https://{domain}/images/{image_id}.{appendix}"
    else:
        return thumb_url  # 如果不匹配，返回原始URL


"""
browser = p.chromium.launch(
    headless=False,
    channel="chrome"
)
context = browser.new_context(
    user_agent="你真实浏览器 UA"
)

"""


# 使用playwright抓取酒店图片
def get_hotel_list(hotel_id):
    hotel_images = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(
            storage_state="ctrip_state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            locale="zh-CN",
        )
        page = context.new_page()

        def handle_response(resp):
            if "getHotelRoomPopInfoPCOnline" in resp.url:
                data = resp.json()
                for room in data.get("data", {}).get("roomPopInfo", []):
                    tmp = data["data"]["roomPopInfo"][room]["pictureInfo"]
                    hotel_images.extend(tmp)

        page.on("response", handle_response)

        page.goto(f"https://hotels.ctrip.com/hotels/{hotel_id}.html")

        page.wait_for_timeout(500)

        browser.close()

    return hotel_images


if __name__ == "__main__":
    hotel_id = 9532016
    ret = get_hotel_list(hotel_id)
    # 存进去,按照
    """
        pictureInfo: [
            "xxx",
            ...,
            ]
    """

    with open("test.json", "w", encoding="utf-8") as f:
        # 写下访问的原URL
        # f"https://hotels.ctrip.com/hotels/{hotel_id}.html"
        json.dump(
            {"hotelId": hotel_id, "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html", "pictureInfo": ret}, f, ensure_ascii=False, indent=2
        )
