import urllib.request
import zipfile
import os

def download_uie_model():
    """手动下载UIE模型"""
    url = "https://bj.bcebos.com/paddlenlp/taskflow/information_extraction/uie-base/uie-base.zip"
    zip_path = "model/uie-base.zip"
    extract_path = "model"
    
    # 创建目录
    os.makedirs("model", exist_ok=True)
    
    print("正在下载UIE模型...")
    urllib.request.urlretrieve(url, zip_path)
    print("下载完成，正在解压...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    print("解压完成！")
    os.remove(zip_path)
    print(f"模型已保存到: {os.path.abspath(extract_path)}/uie-base")

if __name__ == "__main__":
    download_uie_model()