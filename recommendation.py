import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from firebase_utils import get_table
def recommend_ebooks_by_views(user_views, data_array):
    similarity_scores = cosine_similarity([user_views], data_array[:, 1].reshape(1, -1)).flatten()
    top_users = similarity_scores.argsort()[:-4:-1]
    
    average_views = np.mean(data_array[top_users, 1])
    unviewed_books = np.where(user_views == 0)[0]
    if not top_users:
       popular_books = np.argsort(data_array[:, 1])[::-1]
       return popular_books[:3]

    average_views = np.mean(data_array[top_users, 1])

    unviewed_books = np.where(user_views == 0)[0]

    # Kiểm tra nếu không có sách chưa xem
    if not unviewed_books:
        return []
    recommended_books = unviewed_books[np.argsort(average_views[unviewed_books])[:-4:-1]]
    return recommended_books


def recommend_ebooks_by_ratings(user_ratings, data_array):
    # Tính độ tương đồng giữa người dùng và tất cả người dùng khác
    similarity_scores = cosine_similarity([user_ratings], data_array[:, 2].reshape(1, -1)).flatten()

    # Sắp xếp và lấy top 3 người dùng có độ tương đồng cao nhất
    top_users = similarity_scores.argsort()[:-4:-1]

    # Tính trung bình đánh giá của các người dùng tương đồng
    average_ratings = np.mean(data_array[top_users, 2])

    # Lọc ra các cuốn sách mà người dùng chưa đánh giá
    unrated_books = np.where(user_ratings == 0)[0]

    # Sắp xếp và lấy top 3 cuốn sách đề xuất
    recommended_books = unrated_books[np.argsort(average_ratings[unrated_books])[:-4:-1]]

    return recommended_books


def recommend_top_ebooks():
    rate_count_by_book = {}

    # Truy vấn Firestore để lấy số lượng đánh giá của mỗi cuốn sách
    comments = get_table('ebooks_comments')
    for comment in comments:
        book_id = comment.get("book_id")
        rate_count_by_book[book_id] = rate_count_by_book.get(book_id, 0) + 1
    print(rate_count_by_book)
    # Sắp xếp cuốn sách theo rateCount giảm dần
    top_books = sorted(rate_count_by_book.items(), key=lambda x: x[1], reverse=True)[:5]

    # Trả về top 5 sách có rateCount cao nhất
    response = [{"book_id": book_id, "rateCount": rate_count} for book_id, rate_count in top_books]
    return response


def recommend_top_audiobooks():
    rate_count_by_book = {}

    # Truy vấn Firestore để lấy số lượng đánh giá của mỗi cuốn sách
    comments = get_table('audiobook_comments')
    for comment in comments:
        book_id = comment.get("book_id")
        rate_count_by_book[book_id] = rate_count_by_book.get(book_id, 0) + 1
    print(rate_count_by_book)
    # Sắp xếp cuốn sách theo rateCount giảm dần
    top_books = sorted(rate_count_by_book.items(), key=lambda x: x[1], reverse=True)[:5]

    # Trả về top 5 sách có rateCount cao nhất
    response = [{"book_id": book_id, "rateCount": rate_count} for book_id, rate_count in top_books]
    return response

def recommend_books_cosine(user_id, user_ratings, all_user_ratings):
    books = set(user_ratings.keys())
    for other_user_id in all_user_ratings:
        books.update(all_user_ratings[other_user_id].keys())
    unique_books = list(set(books))

    R = np.zeros((len(all_user_ratings), len(unique_books)))

    for i, other_user_id in enumerate(all_user_ratings):
        other_user_ratings_dict = all_user_ratings[other_user_id]
        for j, book_id in enumerate(unique_books):
            R[i, j] = other_user_ratings_dict.get(book_id, 0)

    # Loại bỏ cuốn sách không có ai đánh giá
    non_zero_columns = np.sum(R, axis=0) > 0
    R = R[:, non_zero_columns]
    unique_books = list(np.array(unique_books)[non_zero_columns])

    # Tính toán cosine similarity
    user_ratings_array = np.array([list(user_ratings.get(book_id, 0) for book_id in unique_books)])

    cosine_similarities = cosine_similarity(user_ratings_array, R).flatten()
    print(cosine_similarities.shape)
    # Sắp xếp người dùng theo độ tương tự giảm dần
    similar_users = np.argsort(cosine_similarities)[::-1]
    print(similar_users.shape)
    # Lấy danh sách sách từ những người dùng tương tự
    recommended_books = set()
    for other_user_index in similar_users[1:]:
        print(other_user_index)  # Bỏ qua người dùng hiện tại
        other_user_id = list(all_user_ratings.keys())[other_user_index]
        print(other_user_id)
        other_user_ratings = all_user_ratings[other_user_id]
        print(other_user_ratings)
        for book_id in other_user_ratings:
            print(book_id)
            if book_id not in user_ratings:
                recommended_books.add(book_id)

    return list(recommended_books)
