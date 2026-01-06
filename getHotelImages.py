import requests
import json
from concurrent.futures import ThreadPoolExecutor
import configs
import re
from playwright.sync_api import sync_playwright


def get_original_image_url(thumb_url):
    """通用携程图片URL转原图"""
    if not thumb_url or len(thumb_url) <= 0:
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


# 使用playwright抓取酒店图片
def get_hotel_list(hotel_id):
    hotel_name = ""
    hotel_images_list = []
    user_images_list = []
    hotel_top_images_list = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(
            storage_state="ctrip_state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            locale="zh-CN",
        )
        page = context.new_page()

        def handle_getHotelRoomPopInfoPCOnline(resp):
            if "getHotelRoomPopInfoPCOnline" in resp.url:
                data = resp.json()
                for room in data.get("data", {}).get("roomPopInfo", []):
                    tmp = data["data"]["roomPopInfo"][room]["pictureInfo"]
                    hotel_images_list.extend(tmp)

        # https://m.ctrip.com/restapi/soa2/28820/ctgethotelalbum
        def handle_gethotelalbum(resp):
            if "ctgethotelalbum" in resp.url:
                data = resp.json()
                # 区分酒店上传跟用户上传，这是两个group,标签是json里都弄好的，不用自己训练分类网络
                hotel_images = (
                    data.get("data", {})
                    .get("hotelImagePop", {})
                    .get("hotelProvide", {})
                    .get("imgTabs", [])
                )
                user_images = (
                    data.get("data", {})
                    .get("hotelImagePop", {})
                    .get("userProvide", {})
                    .get("imgTabs", [])
                )
                hotel_top_images = (
                    data.get("data", {}).get("hotelTopImage", {}).get("imgUrlList", [])
                )

                # 酒店上传图片并分类
                for img_tab in hotel_images:
                    imgs_config_dict = {
                        "categoryId": img_tab.get("categoryId", -1),
                        "categoryName": img_tab.get("categoryName", "None"),
                    }

                    # 图片再imgURLList里
                    sub_imgs_list = []
                    for img_info in img_tab.get("imgUrlList", []):
                        for sub_img_info in img_info.get("subImgUrlList", []):
                            sub_imgs_list.append(
                                {
                                    "imgTitle": sub_img_info.get("imgTitle", ""),
                                    "link": get_original_image_url(
                                        sub_img_info.get("link", "")
                                    ),
                                }
                            )
                    imgs_config_dict["imgUrlList"] = sub_imgs_list
                    hotel_images_list.append(imgs_config_dict)

                # 用户上传图片并分类
                for user_tab in user_images:
                    imgs_config_dict = {
                        "categoryId": user_tab.get("categoryId", -1),
                        "categoryName": user_tab.get("categoryName", "None"),
                    }

                    # 图片再imgURLList里
                    sub_imgs_list = []
                    for img_info in user_tab.get("subUserAlbumCommentInfo", []):
                        sub_imgs_list.append(
                            {
                                "link": get_original_image_url(
                                    img_info.get("picture", "")
                                ),
                            }
                        )
                    imgs_config_dict["imgUrlList"] = sub_imgs_list
                    user_images_list.append(imgs_config_dict)
                # 酒店展示图片
                for top_img in hotel_top_images:
                    print()
                    hotel_top_images_list.append(
                        {
                            "imgUrlList": {
                                "link": get_original_image_url(
                                    top_img.get("imgUrl", "")
                                )
                            }
                        }
                    )

        page.on("response", handle_gethotelalbum)
        page.goto(f"https://hotels.ctrip.com/hotels/{hotel_id}.html")

        page.wait_for_timeout(500)

        browser.close()

    return hotel_images_list, user_images_list, hotel_top_images_list


if __name__ == "__main__":
    hotel_id = 9532016
    # ret = get_hotel_list(hotel_id)
    hotel_images, user_images, hotel_top_images = get_hotel_list(hotel_id)
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "hotel_images": hotel_images,
                "user_images": user_images,
                "hotel_top_images": hotel_top_images,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
