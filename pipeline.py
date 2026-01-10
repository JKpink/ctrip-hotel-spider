import saveInfo as SI
import commentFilter


def pipeline(hotel_id, save_nums=15, isSimpleRank=True):
    print(f"Start pipeline for hotel ID: {hotel_id}")
    SI.save_json(hotel_id)
    print("JSON data saved.")
    print("Saving images...")
    SI.save_images(hotel_id)
    print("Images saved.")
    SI.save_comments(hotel_id, ratingLimit=4.5)
    print("Comments saved.")
    comment_deduplicator = commentFilter.SemanticDeduplicator(hotel_id, threshold=0.90)
    comment_deduplicator.pipeline(save_nums=save_nums, isSimpleRank=isSimpleRank)
    SI.save_descriptions(hotel_id)
    print("Descriptions saved.")
    SI.pick_images(hotel_id, strategy="balanced")
    print("Image picking completed.")
