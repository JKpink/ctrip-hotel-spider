import os
import re
import requests
import json
import getHotelImages as GHI
import configs
import getHotelComments as GHC
import getHotelDescription as GHD
import concurrent.futures
import shutil
from PIL import Image


def recive_name(html_str: str) -> str:
    match = re.search(
        r'<span class="crumbSEO_crumb_content__ikbTo">(.*?)</span>', html_str
    )
    return match.group(1).strip() if match else "未知酒店"


def get_hotel_name(hotel_id):
    hotel_name = ""
    url = f"https://hotels.ctrip.com/hotels/{hotel_id}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        hotel_name = recive_name(response.text)
    return hotel_name


def save_json(hotel_id):
    """获取酒店图片路径并保存为json文件"""
    # 创建json存储目录
    json_dir = os.path.join(configs.HOTEL_INFOS_DIR, f"{hotel_id}.json")
    if not os.path.exists(configs.HOTEL_INFOS_DIR):
        os.makedirs(configs.HOTEL_INFOS_DIR, exist_ok=True)
    # 读取数据并写入json文件
    hotel_name = get_hotel_name(hotel_id)
    hotel_images, user_images, hotel_top_images = GHI.get_hotel_list(hotel_id)
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelName": hotel_name,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "hotel_images": hotel_images,
                "user_images": user_images,
                "hotel_top_images": hotel_top_images,
            },
            f,
            ensure_ascii=False,
            indent=4,
        )


def save_images(hotel_id):
    """下载并保存图片到本地文件夹"""
    # 创建酒店图片存储目录
    hotel_name = get_hotel_name(hotel_id)
    hotel_dir = os.path.join(configs.HOTEL_IMAGES_DIR, f"{hotel_name}_{hotel_id}")
    if not os.path.exists(hotel_dir):
        os.makedirs(hotel_dir, exist_ok=True)

    # 读取json文件
    json_path = os.path.join(configs.HOTEL_INFOS_DIR, f"{hotel_id}.json")
    if not os.path.exists(json_path):
        print(f"JSON file for hotel ID {hotel_id} does not exist.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        hotel_json_data = json.load(f)

    # 收集所有下载任务
    download_tasks = []
    
    for category in ["hotel_images", "user_images", "hotel_top_images"]:
        category_dir = os.path.join(hotel_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir, exist_ok=True)

        for img_info in hotel_json_data.get(category, []):
            category_name = img_info.get("categoryName", "无分类")
            category_subdir = os.path.join(category_dir, category_name)
            if not os.path.exists(category_subdir):
                os.makedirs(category_subdir, exist_ok=True)
            
            for idx, img in enumerate(img_info.get("imgUrlList", {})):
                if isinstance(img, dict):
                    img_url = img.get("link", "")
                elif isinstance(img, str):
                    img_url = img
                else:
                    print(f"Unknown image format: {img}")
                    continue
                    
                if not img_url:
                    continue
                img_ext = os.path.splitext(img_url)[1].split("?")[0]
                img_filename = f"{category_name}_{idx + 1}{img_ext}"
                img_path = os.path.join(category_subdir, img_filename)
                
                download_tasks.append((img_url, img_path))
    
    # 并行下载图片
    def download_image(task):
        img_url, img_path = task
        try_times = 3
        
        for attempt in range(try_times):
            try:
                response = requests.get(img_url, timeout=10)
                response.raise_for_status()
                with open(img_path, "wb") as img_file:
                    img_file.write(response.content)
                print(f"Saved image: {img_path}")
                return True
            except Exception as e:
                print(f"Attempt {attempt + 1} failed to download image {img_url}: {e}")
                if attempt == try_times - 1:
                    print(f"Failed to download image after {try_times} attempts: {img_url}")
                    return False
        return False
    
    # 使用线程池并行下载，max_workers可以根据需要调整
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_image, download_tasks))
    
    success_count = sum(results)
    print(f"Downloaded {success_count}/{len(download_tasks)} images successfully")



def save_comments(hotel_id, ratingLimit=4.5):
    """获取酒店评论图片并保存为json文件"""
    # 创建json存储目录,跟图片放同一级{hotel_name}_{hotel_id}，然后再创建一个文件夹 存评论json
    # json_dir = os.path.join(configs.HOTEL_IMAGES_DIR, f"{hotel_id}_comments.json")
    comments_dir = os.path.join(
        configs.HOTEL_IMAGES_DIR, f"{get_hotel_name(hotel_id)}_{hotel_id}"
    )
    sub_dir = os.path.join(comments_dir, "comments_and_descriptions")
    json_dir = os.path.join(sub_dir, f"{hotel_id}_comments.json")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir, exist_ok=True)
    # 读取数据并写入json文件
    all_comments = GHC.fetchHotelComments(
        hotel_id, numPages=50, ratingLimit=ratingLimit
    )
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "comments": all_comments,
            },
            f,
            ensure_ascii=False,
            indent=4,
        )


def save_descriptions(hotel_id):
    """获取酒店描述信息并保存为json文件"""
    # 创建路径跟图像片放同一级{hotel_name}_{hotel_id}，然后再创建一个文件夹 存描述json
    descriptions_dir = os.path.join(
        configs.HOTEL_IMAGES_DIR, f"{get_hotel_name(hotel_id)}_{hotel_id}"
    )
    sub_dir = os.path.join(descriptions_dir, "comments_and_descriptions")
    json_dir = os.path.join(sub_dir, f"{hotel_id}_description.json")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir, exist_ok=True)
    # 用宽松的函数
    description = GHD.get_hotel_description_relaxed(hotel_id)
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "description": description,
            },
            f,
            ensure_ascii=False,
            indent=4,
        )

# 从下载的图片里选择可以用的图片
# 从下载的图片里选择可以用的图片
def pick_images(hotel_id, strategy="balanced"):
    """
    从已下载的图片中筛选精选图片
    
    策略:
    - balanced: 平衡策略，每个分类按比例选取
    - top_rated: 优先选择高评分用户上传的图片
    - quality: 基于图片质量(分辨率、大小)筛选
    - diverse: 多样化策略，确保各类型图片都有
    """
    hotel_name = get_hotel_name(hotel_id)
    hotel_dir = os.path.join(configs.HOTEL_IMAGES_DIR, f"{hotel_name}_{hotel_id}")
    picked_dir = os.path.join(hotel_dir, "picked_images")
    
    if not os.path.exists(picked_dir):
        os.makedirs(picked_dir, exist_ok=True)
    
    # 定义每个分类的优先级和选取数量
    category_config = {
        "hotel_images": {
            "外观": {"priority": 10, "count": 3},
            "大堂": {"priority": 8, "count": 2},
            "客房": {"priority": 10, "count": 5},
            "餐饮": {"priority": 7, "count": 2},
            "康体娱乐": {"priority": 6, "count": 2},
            "周边": {"priority": 5, "count": 1},
        },
        "user_images": {
            "客房": {"priority": 9, "count": 3},
            "餐饮": {"priority": 7, "count": 1},
            "其他": {"priority": 5, "count": 1},
        },
        "hotel_top_images": {
            "推荐": {"priority": 10, "count": 5},
        }
    }
    
    picked_images = []
    
    for category in ["hotel_images", "user_images", "hotel_top_images"]:
        category_dir = os.path.join(hotel_dir, category)
        if not os.path.exists(category_dir):
            continue
            
        for subcategory in os.listdir(category_dir):
            subcategory_path = os.path.join(category_dir, subcategory)
            if not os.path.isdir(subcategory_path):
                continue
            
            # 获取该分类的配置
            config = category_config.get(category, {}).get(subcategory, {"priority": 5, "count": 1})
            pick_count = config["count"]
            
            # 获取该分类下的所有图片
            images = []
            for img_file in os.listdir(subcategory_path):
                img_path = os.path.join(subcategory_path, img_file)
                if os.path.isfile(img_path) and img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    # 获取图片质量信息
                    try:
                        with Image.open(img_path) as img:
                            width, height = img.size
                            file_size = os.path.getsize(img_path)
                            quality_score = (width * height) / 1000000 + file_size / 1000000
                            images.append({
                                "path": img_path,
                                "width": width,
                                "height": height,
                                "size": file_size,
                                "quality": quality_score,
                                "category": category,
                                "subcategory": subcategory
                            })
                    except Exception as e:
                        print(f"Error reading image {img_path}: {e}")
            
            # 根据策略排序并选择
            if strategy == "quality":
                images.sort(key=lambda x: x["quality"], reverse=True)
            elif strategy == "balanced" or strategy == "diverse":
                # 按质量排序，确保选择高质量图片
                images.sort(key=lambda x: x["quality"], reverse=True)
            
            # 选取指定数量的图片
            selected = images[:min(pick_count, len(images))]
            picked_images.extend(selected)
    
    # 复制精选图片到目标文件夹
    for idx, img_info in enumerate(picked_images):
        src_path = img_info["path"]
        file_ext = os.path.splitext(src_path)[1]
        dest_filename = f"{img_info['subcategory']}_{idx + 1}{file_ext}"
        dest_path = os.path.join(picked_dir, dest_filename)
        
        shutil.copy2(src_path, dest_path)
        print(f"Picked: {dest_filename} ({img_info['width']}x{img_info['height']}, {img_info['size']/1024:.2f}KB)")
    
    print(f"\nTotal picked images: {len(picked_images)}")
    print(f"Saved to: {picked_dir}")
    
    # 生成精选图片信息JSON
    picked_json_path = os.path.join(picked_dir, "picked_info.json")
    with open(picked_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "hotelId": hotel_id,
            "hotelName": hotel_name,
            "strategy": strategy,
            "totalPicked": len(picked_images),
            "images": [
                {
                    "filename": os.path.basename(img["path"]),
                    "category": img["category"],
                    "subcategory": img["subcategory"],
                    "resolution": f"{img['width']}x{img['height']}",
                    "size": img["size"]
                }
                for img in picked_images
            ]
        }, f, ensure_ascii=False, indent=4)
    
    return picked_images
    

if __name__ == "__main__":
    hotel_id = 9532016
    # hotel_name = get_hotel_name(hotel_id)
    # print(f"Hotel Name: {hotel_name}")
    # save_json(hotel_id)
    # save_images(hotel_id)
    # save_comments(hotel_id, ratingLimit=4.5)
    # save_descriptions(hotel_id)
    pick_images(hotel_id, strategy="balanced")
