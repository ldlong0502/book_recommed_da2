import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
from faker import Faker
import numpy as np
from datetime import datetime, timezone

from google.cloud.firestore_v1.base_query import FieldFilter, BaseCompositeFilter

cred = credentials.Certificate('uniwave-824e9-firebase-adminsdk-nse8l-56b8f7f2a0.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()
fake = Faker()


def get_table(collection_name): 
    return  db.collection(collection_name).stream()

def get_ebook_data_and_create_matrix():
    collection_ref = db.collection('ebook')
    documents = collection_ref.stream()
    matrix = []

    for doc in documents:
        data = doc.to_dict()
        user_id = data.get('id', 0)
        view_count = data.get('view', 0)
        matrix.append([user_id, view_count])

    matrix = np.array(matrix)
    return matrix


def get_user_ratings(collection_name, user_id):
    # Lấy đánh giá của người dùng từ Firestore
    filter = FieldFilter('user_id', '==', user_id)
    user_ratings_ref = db.collection(collection_name).where(filter = filter)
    user_ratings = {doc.to_dict()['book_id']: doc.to_dict()['rate'] for doc in user_ratings_ref.stream()}
    return user_ratings

def get_all_user_ratings(collection_name):
    # Lấy tất cả đánh giá từ Firestore
    all_user_ratings = {}
    ratings_ref = db.collection(collection_name).stream()
    for doc in ratings_ref:
        user_id = doc.to_dict()['user_id']
        book_id = doc.to_dict()['book_id']
        rating = doc.to_dict()['rate']

        if user_id not in all_user_ratings:
            all_user_ratings[user_id] = {}

        all_user_ratings[user_id][book_id] = rating

    return all_user_ratings
def update_comments():
    # Tham chiếu đến bảng audiobook_comments
    comments_ref = db.collection('audiobook_comments')

    # Lấy tất cả các documents trong bảng
    all_comments = comments_ref.stream()

    # Cập nhật các documents với giá trị book_id ngẫu nhiên từ 1 đến 4
    for comment in all_comments:
        new_book_id = random.randint(1, 4)
        comment.reference.update({'book_id': new_book_id})

        print(f'Cập nhật document có ID {comment.id} với book_id mới: {new_book_id}')

    print('Đã cập nhật các documents thành công.')
