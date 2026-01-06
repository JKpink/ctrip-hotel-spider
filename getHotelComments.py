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
        # 步骤3：构造原图URL
        return f"https://{domain}/images/{image_id}.{match.group(4)}"
    else:
        return thumb_url  # 如果不匹配，返回原始URL


def fetchComments(hotelId, pageIndex, ratingLimit=4.5):

    url = "https://m.ctrip.com/restapi/soa2/33278/getHotelCommentList"
    headers = {
        "Content-type": "application/json",
        "Origin": "https://hotels.ctrip.com",
        "Referer": "https://hotels.ctrip.com",
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    }

    formData = {
        "hotelId": hotelId,
        "pageIndex": pageIndex,
        "pageSize": 10,
        "repeatComment": 1,
        "needStaticInfo": False,
        "functionOptions": ["integratedTopComment", "ctripIntegratedExpediaTaList"],
        "filterInfo": [{"id": 4, "filterType": 1}],
        "orderBy": 1,  # 1: by time
        "head": {
            "platform": "PC",
            "cver": "0",
            "cid": "",
            "bu": "HBU",
            "group": "ctrip",
            "aid": "",
            "sid": "",
            "ouid": "",
            "locale": "zh-CN",
            "timezone": "8",
            "currency": "CNY",
            "pageId": "102003",
            "vid": "",
            "guid": "",
            "isSSR": False,
        },
    }

    # 发起网络请求
    r = requests.post(url, json=formData, headers=headers)
    r.raise_for_status()
    r.encoding = "utf-8"

    if not r.text.strip():
        print("Error: Empty response from server.")
        return []

    try:
        data = json.loads(r.text)["data"]["commentList"]

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON response.")
        return []

    commentList = []
    for item in data:
        content = item["content"]
        rating = item["rating"]
        # if "imageList" not in item:
        #     continue
        # imageURLs = item["imageList"]
        createDate = item["createDate"]

        # for i in range(len(imageURLs)):
        #     imageURLs[i] = get_original_image_url(imageURLs[i])

        if rating < ratingLimit:
            continue

        commentList.append(
            {
                "content": content,
                "rating": rating,
                # "imageURLs": imageURLs,
                "createDate": createDate,
            }
        )

    return commentList


def fetchHotelComments(hotelId, numPages=10, ratingLimit=4.5):
    allComments = []

    def fetch_page(pageIndex):
        return fetchComments(hotelId, pageIndex, ratingLimit)

    with ThreadPoolExecutor(max_workers=configs.NUMWORKERS) as executor:
        results = executor.map(fetch_page, range(1, numPages + 1))
        for comments in results:
            allComments.extend(comments)
    return allComments


# just for testing
if __name__ == "__main__":
    allComments = fetchHotelComments(9532016, numPages=10)
    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(allComments, f, ensure_ascii=False, indent=4)
