from flask import Flask, request, jsonify

from firebase_utils import get_user_ratings, get_all_user_ratings
from recommendation import recommend_top_ebooks, recommend_top_audiobooks, recommend_books_cosine
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/top_ebooks', methods=['GET'])
def get_top_ebooks():
    return jsonify(recommend_top_ebooks())

@app.route('/top_audiobooks', methods=['GET'])
def get_top_audiobooks():
    return jsonify(recommend_top_audiobooks())



@app.route('/recommend-books', methods=['POST'])
def recommend_books():
    # Bước 3: Lấy dữ liệu từ Firebase
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Lấy đánh giá của người dùng hiện tại
    user_ratings = get_user_ratings('ebooks_comments',user_id)
   
    # # Lấy tất cả đánh giá từ Firestore
    all_user_ratings = get_all_user_ratings('ebooks_comments')
    # Bước 4: Tính toán độ tương tự và đề xuất sách


    recommended_books = recommend_books_cosine(user_id, user_ratings, all_user_ratings)
    return jsonify({"recommended_books": recommended_books})

@app.route('/recommend-audiobooks', methods=['POST'])
def recommend_audiobooks():
    # Bước 3: Lấy dữ liệu từ Firebase
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Lấy đánh giá của người dùng hiện tại
    user_ratings = get_user_ratings('audiobook_comments', user_id)
    print(user_ratings)
    # # Lấy tất cả đánh giá từ Firestore
    all_user_ratings = get_all_user_ratings('audiobook_comments')
    # Bước 4: Tính toán độ tương tự và đề xuất sách
    print(all_user_ratings)

    recommended_books = recommend_books_cosine(user_id, user_ratings, all_user_ratings)
    return jsonify({"recommended_books": recommended_books})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
