import os
import re
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
# from paddlenlp import Taskflow
import saveInfo
import configs
import numpy as np

# 应该使用聚类方法来进行评论分类后在每一类中挑选出优质评论
# 正面评论池 → 去重 -> 评价权重指标


# 已经是正面评论了
def load_comments(hotel_id):
    """加载评论数据"""
    hotel_name = saveInfo.get_hotel_name(hotel_id)
    comments_file = f"{configs.HOTEL_IMAGES_DIR}/{hotel_name}_{hotel_id}/comments_and_descriptions/{hotel_id}_comments.json"
    with open(comments_file, "r", encoding="utf-8") as f:
        comments_data = json.load(f)

    return [c["content"] for c in comments_data["comments"]]


class SemanticDeduplicator:
    def __init__(self, hotel_id, model_name="model/Jerry0/m3e-base", threshold=0.90):
        """
        threshold: 相似度阈值，>此值视为重复
        0.85-0.90 适合保留相似但非重复，0.95 适合严格去重
        """
        self.hotel_id = hotel_id
        self.hotel_name = saveInfo.get_hotel_name(hotel_id)
        self.encoder = SentenceTransformer(model_name)
        # self.extractor = Taskflow("information_extraction", model="uie-nano")
        self.threshold = threshold

    def deduplicate(self, comments):
        """返回去重后的评论和分组信息"""
        if len(comments) < 2:
            self.dedup_comments = comments
            self.keep_indices = list(range(len(comments)))
            return comments, {0: comments}

        # 1. 编码
        embeddings = self.encoder.encode(comments, convert_to_tensor=True)

        # 2. 计算相似度矩阵
        sim_matrix = cosine_similarity(embeddings.cpu().numpy())

        # 3. 去重
        self.keep_indices = []
        self.groups = {}  # {保留索引: [相似评论索引列表]}
        removed = set()

        for i in range(len(comments)):
            if i in removed:
                continue

            # 保留当前评论
            self.keep_indices.append(i)

            # 找所有相似评论
            similar_idx = np.where(sim_matrix[i] > self.threshold)[0]
            similar_idx = [
                idx for idx in similar_idx if idx != i and idx not in removed
            ]

            self.groups[i] = [i] + similar_idx
            removed.update(similar_idx)

        # 4. 结果整理
        self.dedup_comments = [comments[i] for i in self.keep_indices]

        return self.dedup_comments, self.groups

    def simple_rank(self, method="length"):
        """极简排序策略"""
        if self.dedup_comments is None:
            raise ValueError("请先调用 deduplicate 方法进行去重")

        if method == "length":
            # 策略1：越长越好（通常信息量大）
            return sorted(self.dedup_comments, key=lambda x: len(x), reverse=True)
        elif method == "keyword":
            # 策略2：含关键词的优先
            keywords = {"但是", "建议", "如果", "对比", "不过", "比较"}

            def score(c):
                return sum(1 for k in keywords if k in c) + len(c) / 100

            return sorted(self.dedup_comments, key=score, reverse=True)

        elif method == "random":
            # 策略3：随机（适合 A/B 测试）
            import random

            random.shuffle(self.dedup_comments)
            return self.dedup_comments
        else:
            return self.dedup_comments

    def print_report(self, comments, groups):
        """打印去重报告"""
        print(f"\n{'='*50}")
        print(f"语义去重报告")
        print(f"原始评论: {len(comments)} 条")
        print(f"去重后: {len(groups)} 条")
        print(f"压缩率: {(1 - len(groups)/len(comments))*100:.1f}%")

        print("\n【分组详情】")
        for keep_idx, group in groups.items():
            print(f"\n保留评论 [{keep_idx}]: {comments[keep_idx][:40]}...")
            if len(group) > 1:
                print(f"  └─ 合并了 {len(group)-1} 条相似评论:")
                for idx in group[1:]:
                    print(f"     - [{idx}] {comments[idx][:40]}...")

    def save_as_json(self, save_nums=15, isSimpleRank=True):
        save_path = f"{configs.HOTEL_IMAGES_DIR}/{self.hotel_name}_{self.hotel_id}/pickup_comments/{self.hotel_id}_dedup_comments.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if isSimpleRank:
            self.dedup_comments = self.simple_rank(method="length")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "hotelId": self.hotel_id,
                    "hotelName": self.hotel_name,
                    "deduplicatedComments": self.dedup_comments[:save_nums],
                },
                f,
                ensure_ascii=False,
                indent=4,
            )

    # 整合流程
    def pipeline(self, save_nums=15, isSimpleRank=True):
        # 1. 加载数据
        comments = load_comments(self.hotel_id)
        print(f"加载 {len(comments)} 条评论")

        # 2. 去重
        self.deduplicate(comments)

        # 4. 保存结果
        self.save_as_json(save_nums=save_nums, isSimpleRank=isSimpleRank)


"""
读入json结构：
"hotelId": 9532016,
    "hotelURL": "https://hotels.ctrip.com/hotels/9532016.html",
    "comments": [
        {
            "content": "酒店风景非常棒，直面苍山洱海，美景毫无遮挡一览无遗，在下关区域的酒店里景色属于天花板级别了。老板也非常热情，有求必应，服务相当赞。酒店位于下关核心区域，交通很方便，无论去海东还是古城都很方便。总之相当棒！",
            "rating": 5,
            "createDate": "2025-10-02 23:03:16"
        },
"""

if __name__ == "__main__":
    # 1. 加载数据
    hotel_id = 9532016

    # 测试pipline
    deduplicator = SemanticDeduplicator(hotel_id, threshold=0.90)
    deduplicator.pipeline()

