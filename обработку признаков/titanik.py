# -*- coding: utf-8 -*-
"""ML_Homework_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RBGzUzSRebwp47HpHa6bNVZIu_fn5blL
"""

# импортируем необходимые библиотеки
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

# читаем данные
train = pd.read_csv("titanic_train.csv")
test = pd.read_csv("titanic_test.csv")

# создаем новые датасеты, в них
# удаляем стобцы, которые физически не могут влиять на выживание
data_train = train.drop(['PassengerId', 'Name', 'Ticket'], axis=1)
data_test = test.drop(['PassengerId', 'Name', 'Ticket'], axis=1)

# смотрим информацию о датасете для выполнения преобразования данных
# необходимо избавиться от категориальных признаков и пустых значений
data_train.info()

"""### Label encoder"""

# определяем где в датасете категориальные признаки
list(data_train.select_dtypes(include=['object']).columns)

# смотрим варианты значений категориального признака пол (Sex)
train['Sex'].value_counts()

# переводим категориальный признак Sex в дискретный
Sex_embarked_mapping = {'male':0,'female':1}
data_train['Sex'] = data_train['Sex'].map(Sex_embarked_mapping)

# со столбцом каюта (Cabin) можно выполнить некоторые преобразования
# каждая каюта находится на какой-то палубе и чем ниже палуба, тем меньше шансов выжить
# собственно все было вот так:
from IPython.display import Image
Image(url= "http://data.cyclowiki.org/images/3/38/Titanic_palyb.jpeg")

# столбец Cabin мало где заполнен, распределим пассажиров

# "отправляем" всех невыживших пассажиров 3-го класса на палубу G
data_train['Cabin'].loc[(data_train['Pclass']==3) & (data_train['Survived']==0)] = 'G'

# "отправляем" всех выживших пассажиров 3-го класса на палубу F
data_train['Cabin'].loc[(data_train['Pclass']==3) & (data_train['Survived']==1)] = 'F'

# "отправляем" всех невыживших пассажиров 2-го класса на палубу E
data_train['Cabin'].loc[(data_train['Pclass']==2) & (data_train['Survived']==0)] = 'E'

# "отправляем" всех выживших пассажиров 2-го класса на палубу D
data_train['Cabin'].loc[(data_train['Pclass']==2) & (data_train['Survived']==1)] = 'D'

# "отправляем" всех невыживших пассажиров 1-го класса на палубу C
data_train['Cabin'].loc[(data_train['Pclass']==1) & (data_train['Survived']==0)] = 'C'

# "отправляем" всех выживших мужчин 1-го класса на палубу B
data_train['Cabin'].loc[(data_train['Pclass']==1) & (data_train['Survived']==1) & (data_train['Sex']==0)] = 'B'
 
# "отправляем" всех выживших женщин 1-го класса на палубу A
data_train['Cabin'].loc[(data_train['Pclass']==1) & (data_train['Survived']==1) & (data_train['Sex']==1)] = 'A'

# переводим категориальный признак Cabin в дискретный
Cabin_embarked_mapping = {'A':0,'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6}
data_train['Cabin'] = data_train['Cabin'].map(Cabin_embarked_mapping)

# заполняем пустые значения столбца Embarked
data_train['Embarked'].loc[(data_train['Embarked'].isna())] ='S'

# переводим категориальный признак Embarked в дискретный
Embarked_embarked_mapping = {'S':0,'C':1,'Q':2}
data_train['Embarked'] = data_train['Embarked'].map(Embarked_embarked_mapping)

# заполняем пустые значения столбца Age
data_train['Age'].loc[(data_train['Age'].isna())] = data_train['Age'].mean()

# проверяем датасет на "избавление" от пустых значений и категориальных признаков
data_train.info()

# отделяем фичи от таргета
y = data_train.Survived
data_train = data_train.drop(['Survived'], axis=1)

# проводим стандартизацию исходных данных
scaler = preprocessing.StandardScaler()
data_train_ST = scaler.fit_transform(data_train)

# делим преобразованный pandas датасет на тренировочный и тестовый
X_train, X_test, y_train, y_test = train_test_split(data_train_ST, y, test_size=0.2, random_state=42)

# создаем параметры KNN для перебора в GridSearchCV
tuned_parameters_KNN = [{'n_neighbors': [1, 2, 5, 10, 50, 100], 'weights': ['distance', 'uniform'], 'metric': ['minkowski', 'euclidean']}]

# создаем модель на основее KNN и с помощью GridSearchCV
# подбираем оптимальные параметры и обучаем
titanic_model_KNN = GridSearchCV(KNeighborsClassifier(), tuned_parameters_KNN, cv=5)
titanic_model_KNN.fit(X_train,y_train)
titanic_model_KNN.best_params_

# Считаем accuracy KNN 
np.round(titanic_model_KNN.score(X_test,y_test), 2)

# создаем параметры GaussianNB для перебора в GridSearchCV
tuned_parameters_GaussianNB = [{'var_smoothing': [1e-30, 1e-20, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7]}]

# создаем модель на основее GaussianNB и с помощью GridSearchCV
# подбираем оптимальные параметры и обучаем
titanic_model_GaussianNB = GridSearchCV(GaussianNB(), tuned_parameters_GaussianNB, cv=5)
titanic_model_GaussianNB.fit(X_train,y_train)
titanic_model_GaussianNB.best_params_

# Считаем accuracy GaussianNB 
np.round(titanic_model_GaussianNB.score(X_test,y_test), 2)

"""## One-hot encoding"""

# создаем датасеты с ont-hot encoding для столбцов Sex, Cabin, Embarked
OHN_Sex = pd.get_dummies(data_train['Sex'], prefix="Sex", dummy_na=False)
OHN_Cabin = pd.get_dummies(data_train['Cabin'], prefix="Cabin", dummy_na=False)
OHN_Embarked = pd.get_dummies(data_train['Embarked'], prefix="Embarked", dummy_na=False)

# Собираем закодированные столбцы и исходные данные в один датасет
# удаляем категориальные признаки не в one-hot-encoding
data_train_OHN = pd.concat([data_train, OHN_Sex, OHN_Cabin, OHN_Embarked], axis=1)
data_train_OHN = data_train_OHN.drop(['Sex', 'Cabin', 'Embarked'], axis=1)

# проводим стандартизацию исходных данных
scaler_OHN = preprocessing.StandardScaler()
data_train_OHN_ST = scaler_OHN.fit_transform(data_train_OHN)

# делим преобразованный pandas датасет на тренировочный и тестовый
X_train_OHN, X_test_OHN, y_train_OHN, y_test_OHN = train_test_split(data_train_OHN_ST, y, test_size=0.2, random_state=42)

# создаем параметры KNN для перебора в GridSearchCV
tuned_parameters_KNN_OHN = [{'n_neighbors': [1, 2, 5, 10, 50, 100], 'weights': ['distance', 'uniform'], 'metric': ['minkowski', 'euclidean']}]

# создаем модель на основее KNN и с помощью GridSearchCV
# подбираем оптимальные параметры и обучаем
titanic_model_KNN_OHN = GridSearchCV(KNeighborsClassifier(), tuned_parameters_KNN_OHN, cv=5)
titanic_model_KNN_OHN.fit(X_train_OHN,y_train_OHN)
titanic_model_KNN_OHN.best_params_

# Считаем accuracy KNN 
np.round(titanic_model_KNN_OHN.score(X_test_OHN,y_test_OHN), 2)

# создаем параметры GaussianNB для перебора в GridSearchCV
tuned_parameters_GaussianNB_OHN = [{'var_smoothing': [1e-30, 1e-20, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7]}]

# создаем модель на основее GaussianNB и с помощью GridSearchCV
# подбираем оптимальные параметры и обучаем
titanic_model_GaussianNB_OHN = GridSearchCV(GaussianNB(), tuned_parameters_GaussianNB_OHN, cv=5)
titanic_model_GaussianNB_OHN.fit(X_train_OHN,y_train_OHN)
titanic_model_GaussianNB_OHN.best_params_

# Считаем accuracy GaussianNB 
np.round(titanic_model_GaussianNB_OHN.score(X_test_OHN,y_test_OHN), 2)