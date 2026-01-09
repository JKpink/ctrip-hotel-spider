import pipline

if __name__ == "__main__":
    print("请输入酒店ID：")
    hotel_id = input().strip()
    print("请确认酒店ID为：" + hotel_id + "，是否继续？(y/n)")
    confirm = input().strip().lower()
    if confirm == "y":
        pipline.pipline(hotel_id)
    else:
        print("操作已取消。")
