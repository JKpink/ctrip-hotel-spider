import saveInfo as SI


def pipline(hotel_id):
    print(f"Start pipline for hotel ID: {hotel_id}")
    SI.save_json(hotel_id)
    print("JSON data saved.")
    print("Saving images...")
    SI.save_images(hotel_id)
    print("Images saved.")
    SI.save_comments(hotel_id, ratingLimit=4.5)
    print("Comments saved.")
    SI.save_descriptions(hotel_id)
    print("Descriptions saved.")
    SI.pick_images(hotel_id, strategy="balanced")
    print("Image picking completed.")
