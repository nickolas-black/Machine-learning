# -*- coding: utf-8 -*-
"""Recommender Systems In Python.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-FdZmbTzDRx3AtNnal9mGEckLBCEemRW

# Разработка рекомендательной системы на Python

_Примечание: в контексте данной работы единицами рекомендаций будут являвляться фильмы, т.к. использование этого термина будет удобно с точки зрения используемого датасета._

Можно выделить два основных типа рекомендательных систем.

**Content-based**

* Пользователю рекомендуются фильмы, похожие на те, которые он уже посмотрел.
* Похожести оцениваются по признакам содержимого объектов.
* Сильная зависимость от предметной области, полезность рекомендаций ограничена.

Коллаборативная фильтрация (**Collaborative Filtering**)

* Для рекомендации используется история оценок как самого пользователя, так и других пользователей.
* Более универсальный подход, часто дает лучший результат.
* Есть свои проблемы (например, холодный старт).

В большинстве случаев алгоритмы коллаборативной фильтрации (CF) показывают лучший результат, чем content-based системы. В данной работе будут рассматриваться два типа CF: **Memory-Based Collaborative Filtering** и **Model-Based Collaborative filtering**.

## Датасет

В данной работе используется MovieLens Dataset (Small). Посмотреть информацию или скачать датасет можно [отсюда](https://grouplens.org/datasets/movielens/).

https://www.kaggle.com/grouplens/movielens-20m-dataset
"""

import numpy as np
import pandas as pd

# загружаем датасет
df = pd.read_csv('data/ratings.csv')

# смотрим на структуру
df[:100]

# выводим количество пользователей и фильмов
n_users = df['userId'].unique().shape[0]
n_items = df['movieId'].unique().shape[0]

print('Users: {}, Items: {}'.format(n_users, n_items))

# чтобы можно было удобно работать дальше, необходимо отмасштабировать 
# значения в колонке movieId (новые значения будут в диапазоне от 1 до
# количества фильмов)
input_list = df['movieId'].unique()

def scale_movie_id(input_id):
    return np.where(input_list == input_id)[0][0] + 1

df['movieId'] = df['movieId'].apply(scale_movie_id)

from sklearn.model_selection import train_test_split

# делим данные на тренировочный и тестовый наборы
train_data, test_data = train_test_split(df, test_size=0.20)

"""## Memory-Based Collaborative Filtering

Memory-Based Collaborative Filtering подходы можно разделить на две части: **user-item filtering** and **item-item filtering**.

В user-item filtering мы:

1. Берём исходного пользователя
2. Находим группу пользователей, которая максимально похожа на него (основываясь, например, оценках) и узнаём, какие фильмы понравились этой группе.
3. Нашему исходному пользователю рекомендуем фильмы, которые нравятся найденной группе пользователей.

На входе пользователь, на выходе – рекомендация фильмов для данного пользователя.

В item-item filtering мы:
    
1. Берём какой-либо фильм
2. Находим пользователей, которым нравится этот фильм
3. Смотрим на фильмы, которые нравятся найденным пользователям и выводим их в качестве рекомендации к исходному товару

На входе фильм, на выходе – рекомендация в виде похожих фильмов.

* Item-Item Collaborative Filtering: "Пользователям, которым нравится данный фильм, может так же понравиться это ..."
* User-Item Collaborative Filtering: "Похожим на вас пользователям нравится это ..."

В обоих случаях нам необходимо создать user-item матрицу, которая будет выглядеть следующим образом:

|       | Item1 | Item2 | Item3 |
|-------|-------|-------|-------|
| User1 |   5   |   3   |   4   |
| User2 |   4   |   0   |   0   |
| User3 |   0   |   0   |   0   |

В ячейках матрицы будет записана информация об оценке фильма $m$ пользователя $n$.
"""

# создаём две user-item матрицы – для обучения и для теста
train_data_matrix = np.zeros((n_users, n_items))

for line in train_data.itertuples():
    train_data_matrix[line[1] - 1, line[2] - 1] = line[3]  

test_data_matrix = np.zeros((n_users, n_items))

for line in test_data.itertuples():
    test_data_matrix[line[1] - 1, line[2] - 1] = line[3]

train_data_matrix.shape

train_data_matrix[0]

test_data_matrix.shape

"""После того, как мы построим данную матрицу, на её основе необходимо будет рассчитать две новые матрицы с коэффициентами сходства (похожести, близости) для пользователей и для фильмов.

В качестве метрики близости в данной работе используется косинусное расстояние между векторами пользователей (фильмов).

Формула для пользователей:

$$ s_{u}^{cos}(u_k, u_a) = \frac{u_k \cdot  u_a}{\left \| u_k \right \| \left \| u_a \right \|} = \frac{\sum x_{k,m} x_{a,m}}{\sqrt{\sum x_{k,m}^2 \sum x_{a,m}^2}} $$

Формула для фильмов:

$$ s_{u}^{cos}(i_m, i_b) = \frac{i_m \cdot  i_b}{\left \| i_m \right \| \left \| i_b \right \|} = \frac{\sum x_{a,m} x_{a,b}}{\sqrt{\sum x_{a,m}^2 \sum x_{a,b}^2}} $$
"""

from sklearn.metrics.pairwise import pairwise_distances

# считаем косинусное расстояние для пользователей и фильмов
user_similarity = pairwise_distances(train_data_matrix, metric='cosine')


item_similarity = pairwise_distances(train_data_matrix.T, metric='cosine')

user_similarity.shape

item_similarity.shape

"""Матрица "похожести" для пользователей имеет следующий вид (аналогичную структуру имеет и матрицы для фильмов):

|       | User1 | User1 | User3 |
|-------|-------|-------|-------|
| User1 |   0   | 0.87  | 0.99  |
| User2 |   123   |   0   |   123123   |
| User3 |   123   |   123   |   0  |

Для предсказания в user-based CF необходимо применить следующую формулу:

$$ \hat{x}_{k,m} = \overline{x}_k + \frac{\sum_{u_a} sim_u(u_k, u_a)(x_{a,m} - \overline{x}_{u_a})}{\sum_{u_a} \left | sim_u(u_k, u_a) \right |} $$

Для item-based CF:

$$ \hat{x}_{k,m} = \frac{\sum_{i_b} sim_i(i_m, i_b)(x_{k,b})}{\sum_{i_b} \left | sim_i(i_m, i_b) \right |} $$
"""

def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis]) 
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    
    elif type == 'item':
        
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])     
    return pred

item_prediction = predict(train_data_matrix, item_similarity, type='item')

user_prediction = predict(train_data_matrix, user_similarity, type='user')

item_prediction.shape

user_prediction.shape

"""Для оценки качества предсказания используем метрику RMSE (Root Mean Square Error, cреднеквадратичная ошибка):

$$ RMSE = \sqrt{\frac{1}{N}\sum (x_i - \hat{x}_i)^2} $$
"""

from sklearn.metrics import mean_squared_error
from math import sqrt

def rmse(prediction, ground_truth):
    prediction = prediction[ground_truth.nonzero()].flatten()
    
    ground_truth = ground_truth[ground_truth.nonzero()].flatten()
    
    return sqrt(mean_squared_error(prediction, ground_truth))

print('User-based CF RMSE: ' + str(rmse(user_prediction, test_data_matrix)))
print('Item-based CF RMSE: ' + str(rmse(item_prediction, test_data_matrix)))

"""## Model-based Collaborative Filtering

Model-based Collaborative Filtering основана на разложении матрицы. В данной работе используется метод разложения, который называется **singular value decomposition** (SVD, cингулярное разложение). Смысл этого разложения в том, что исходную матрицу $X$ мы разбиваем на произведение ортогональных матриц $U$ и $V^T$ и диагональной матрицы $S$.

$$ X = UV^TS $$

В нашем случае $X$ – разреженная (состоящая преимущественно из нулей) user-item матрица. Разложив её на компоненты, мы можем их вновь перемножить и получить "восстановленную" матрицу $\hat{X}$. Матрица $\hat{X}$ и будет являться нашим предсказанием – метод SVD сделал сам за нас всё работу и заполнил пропуски в исходной матрице $X$

$$ UV^TS \approx \hat{X}$$
"""

import scipy.sparse as sp
from scipy.sparse.linalg import svds

# делаем SVD
u, s, vt = svds(train_data_matrix, k=10)

s_diag_matrix = np.diag(s)

s

s.shape

s_diag_matrix.shape

# предсказываем
X_pred = np.dot(np.dot(u, s_diag_matrix), vt)

X_pred.shape

# выводим метрику
print('User-based CF MSE: ' + str(rmse(X_pred, test_data_matrix)))

"""## Hybrid Recommender Systems

Пару слов стоит сказать о наиболее эффективной на практике гибридной рекомендательной системе. Его суть заключается в том, чтобы комбинировать в себе сontent-based модели и сollaborative filtering. Используя дополнительную информацию о фильмах (жанр, теги, год выпуска и т.д.) и мощь алгоритмов коллаборативной фильтрации, можно добиться впечатляющего результата.
"""