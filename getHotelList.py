import json
from datetime import datetime, timedelta
from tqdm import tqdm
from playwright.sync_api import sync_playwright
import multiprocessing


def _fetchHotels(args):
    """
    单个进程抓取一页数据
    """
    pageIndex, cityId = args
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        response_data = {}
        
        def handle_response(response):
            if "fetchHotelList" in response.url and response.status == 200:
                try:
                    response_data['json'] = response.json()
                except:
                    pass
        
        page.on("response", handle_response)
        
        # 构造URL
        check_in = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        check_out = (datetime.now() + timedelta(days=2)).strftime("%Y%m%d")
        list_url = f"https://hotels.ctrip.com/hotels/{cityId}/p{pageIndex}?checkin={check_in}&checkout={check_out}"
        
        page.goto(list_url, wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        browser.close()
        
        # 解析数据
        if 'json' not in response_data:
            return {}
        
        try:
            data = response_data['json'].get("data", {}).get("hotelList", [])
        except:
            return {}
        
        page_hotels = {}
        for item in data:
            try:
                hotelInfo = item["hotelInfo"]
                hotelId = hotelInfo["summary"]["hotelId"]
                hotelName = hotelInfo["nameInfo"]["name"]
                # hotelImages = hotelInfo["hotelImages"]["multiImgs"]
                # hotelImgURLs = [get_original_image_url(img["url"]) for img in hotelImages]
                hotelStar = hotelInfo["hotelStar"]["star"]
                
                page_hotels[hotelId] = {
                    "hotelName": hotelName,
                    # "hotelImages": hotelImages,
                    "hotelStar": hotelStar
                }
            except Exception as e:
                continue
        
        return page_hotels

def fetchHotels(cityId, numPages=10, savePath="hotels.json", max_workers=3):
    """
    主函数：使用多进程并发抓取
    """
    hotels = {}
    
    # 准备参数
    args_list = [(pageIndex, cityId) for pageIndex in range(1, numPages + 1)]
    
    # 使用进程池
    with multiprocessing.Pool(processes=max_workers) as pool:
        results = list(tqdm(
            pool.imap(_fetchHotels, args_list),
            total=numPages,
            desc="Fetching Hotels"
        ))
    
    # 合并结果
    for page_hotels in results:
        hotels.update(page_hotels)
    
    # 保存
    with open(savePath, "w", encoding="utf-8") as f:
        json.dump(hotels, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 完成，共获取 {len(hotels)} 家酒店")
    return hotels

if __name__ == "__main__":
    # Windows 需要这个保护
    multiprocessing.freeze_support()
    fetchHotels(cityId=2, numPages=5, savePath="hotels.json", max_workers=3)