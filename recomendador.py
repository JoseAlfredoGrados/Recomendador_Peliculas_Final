# -*- coding: utf-8 -*-
import re
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.recommendation import ALS, ALSModel

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext

conf = SparkConf().setAppName("MyApp")
sc = SparkContext(conf=conf)
sqlc = SQLContext(sc)

# Rutas y nombres de los ficheros y separador por defecto que utiliza
RUTA_FICHERO_PUNTUACION = 'u.data'
RUTA_FICHERO_USUARIO = 'u.user'
RUTA_FICHERO_ITEM = 'u.item'
RUTA_FICHERO_GENERO = 'u.genre'
SEPARADOR_TABULADOR = '\t'
SEPARADOR_PIPE = '|'

# Variables con información de las columnas de los ficheros:
#    - posicion 0: nombre de la columna en el fichero
#    - posicion 1: posicion de la columna en el fichero
#    - posicion 2: tipo dataframe
#    - posicion 3: True si la columna puede ser nullable. Se utilizara al convertir de RDD a dataframe.
# Se crea también una lista con ellos dentro por si se quiere iterar
# Fichero puntuaciones
COL_PUNTUACION_USERID = ('userid', 0, IntegerType(), True)
COL_PUNTUACION_ITEMID = ('itemid', 1, IntegerType(), True)
COL_PUNTUACION_RATING = ('rating', 2, FloatType(), True)
COL_PUNTUACION_TIMESTAMP = ('timestamp', 3, IntegerType(), True)
COL_PUNTUACION_PREDICTION = ('prediction', None, None, None)
COL_PUNTUACION_NUMEROPUNTUACIONES = ('numero_puntuaciones', None, None, None)
COLS_PUNTUACION = (
    COL_PUNTUACION_USERID,
    COL_PUNTUACION_ITEMID,
    COL_PUNTUACION_RATING,
    COL_PUNTUACION_TIMESTAMP)
# Fichero usuario
COL_USUARIO_ID = ('user_userid', 0, IntegerType(), True)
COL_USUARIO_AGE = ('age', 1, IntegerType(), True)
COL_USUARIO_GENDER = ('gender', 2, StringType(), True)
COL_USUARIO_OCCUPATION = ('occupation', 3, StringType(), True)
COL_USUARIO_ZIPCODE = ('zipcode', 4, StringType(), True)
COLS_USUARIO = (
    COL_USUARIO_ID,
    COL_USUARIO_AGE,
    COL_USUARIO_GENDER,
    COL_USUARIO_OCCUPATION,
    COL_USUARIO_ZIPCODE)
# Fichero genero
COL_GENERO_NAME = ('name', 0, StringType(), False)
COL_GENERO_ID = ('genre_genreid', 1, IntegerType(), False)
COLS_GENERO = (
    COL_GENERO_NAME,
    COL_GENERO_ID)
# Fichero item
COL_ITEM_ID = ('item_itemid', 0, IntegerType(), False)
COL_ITEM_TITLE = ('title', 1, StringType(), False)
COL_ITEM_RELEASEDATE = ('releasedate', 2, StringType(), False)
COL_ITEM_VIDERELEASEDATE = ('videoreleasedate', 3, StringType(), False)
COL_ITEM_IMDBURL = ('imdburl', 4, StringType(), False)
COL_ITEM_UNKNOWN = ('unknown', 5, IntegerType(), False)
COL_ITEM_ACTION = ('action', 6, IntegerType(), False)
COL_ITEM_ADVENTURE = ('adventure', 7, IntegerType(), False)
COL_ITEM_ANIMATION = ('animation', 8, IntegerType(), False)
COL_ITEM_CHILDRENS = ('childrens', 9, IntegerType(), False)
COL_ITEM_COMEDY = ('comedy', 10, IntegerType(), False)
COL_ITEM_CRIME = ('crime', 11, IntegerType(), False)
COL_ITEM_DOCUMENTARY = ('documentary', 12, IntegerType(), False)
COL_ITEM_DRAMA = ('drama', 13, IntegerType(), False)
COL_ITEM_FANTASY = ('fantasy', 14, IntegerType(), False)
COL_ITEM_FILMNOIR = ('filmnoir', 15, IntegerType(), False)
COL_ITEM_HORROR = ('horror', 16, IntegerType(), False)
COL_ITEM_MUSICAL = ('musical', 17, IntegerType(), False)
COL_ITEM_MYSTERY = ('mystery', 18, IntegerType(), False)
COL_ITEM_ROMACE = ('Romance', 19, IntegerType(), False)
COL_ITEM_SCIFI = ('scifi', 20, IntegerType(), False)
COL_ITEM_THRILLER = ('thriller', 21, IntegerType(), False)
COL_ITEM_WAR = ('war', 22, IntegerType(), False)
COL_ITEM_WESTERN = ('western', 23, IntegerType(), False)
COL_ITEM_GENEROS = ('generos', None, ArrayType(StringType()), False)
COL_ITEM_GENERO = ('genero', None, None, None)
COLS_ITEM = (
    COL_ITEM_ID,
    COL_ITEM_TITLE,
    COL_ITEM_RELEASEDATE,
    COL_ITEM_VIDERELEASEDATE,
    COL_ITEM_IMDBURL)
COLS_ITEM_TODOSGENEROS = (
    COL_ITEM_UNKNOWN,
    COL_ITEM_ACTION,
    COL_ITEM_ADVENTURE,
    COL_ITEM_ANIMATION,
    COL_ITEM_CHILDRENS,
    COL_ITEM_COMEDY,
    COL_ITEM_CRIME,
    COL_ITEM_DOCUMENTARY,
    COL_ITEM_DRAMA,
    COL_ITEM_FANTASY,
    COL_ITEM_FILMNOIR,
    COL_ITEM_HORROR,
    COL_ITEM_MUSICAL,
    COL_ITEM_MYSTERY,
    COL_ITEM_ROMACE,
    COL_ITEM_SCIFI,
    COL_ITEM_THRILLER,
    COL_ITEM_WAR,
    COL_ITEM_WESTERN)

# Se carga las puntuaciones utilizando COLS_PUNTUACION y después se elimina el timestamp
esquemaPuntuacion = StructType()
for col in COLS_PUNTUACION:
    esquemaPuntuacion.add(StructField(col[0], col[2], col[3]))
dataframePuntuacion = sqlc.read.format('com.databricks.spark.csv'). \
                option('delimiter', SEPARADOR_TABULADOR). \
                option('header', 'false'). \
                load(RUTA_FICHERO_PUNTUACION, schema=esquemaPuntuacion)
cabecerasReducidas = list()
for col in COLS_PUNTUACION:
    if col[0] != COL_PUNTUACION_TIMESTAMP[0]:
        cabecerasReducidas.append(col[0])
dataframePuntuacion = dataframePuntuacion.select(cabecerasReducidas)

# Se carga los usuarios utilizando COLS_USUARIO
esquemaUsuario = StructType()
for col in COLS_USUARIO:
    esquemaUsuario.add(StructField(col[0], col[2], col[3]))
dataframeUsuario = sqlc.read.format('com.databricks.spark.csv'). \
                option('delimiter', SEPARADOR_PIPE). \
                option('header', 'false'). \
                load(RUTA_FICHERO_USUARIO, schema=esquemaUsuario)

# Se carga los items utilizando COLS_ITEM y COLS_ITEM_TODOSGENEROS
esquemaItem = StructType()
for col in COLS_ITEM:
    esquemaItem.add(StructField(col[0], col[2], col[3]))
for col in COLS_ITEM_TODOSGENEROS:
    esquemaItem.add(StructField(col[0], col[2], col[3]))
dataframeItem = sqlc.read.format('com.databricks.spark.csv'). \
                option('delimiter', SEPARADOR_PIPE). \
                option('header', 'false'). \
                load(RUTA_FICHERO_ITEM, schema=esquemaItem)
cabecerasReducidas = list()
for col in COLS_ITEM:
    if col[0] == COL_ITEM_ID[0] or col[0] == COL_ITEM_TITLE[0]:
        cabecerasReducidas.append(col[0])
for col in COLS_ITEM_TODOSGENEROS:
    cabecerasReducidas.append(col[0])
dataframeItem = dataframeItem.select(cabecerasReducidas)

# Se carga los géneros utilizando COLS_GENERO
esquemaGenero = StructType()
for col in COLS_GENERO:
    esquemaGenero.add(StructField(col[0], col[2], col[3]))
dataframeGenero = sqlc.read.format('com.databricks.spark.csv'). \
                option('delimiter', SEPARADOR_PIPE). \
                option('header', 'false'). \
                load(RUTA_FICHERO_GENERO, schema=esquemaGenero)

print(dataframePuntuacion.show(4))
print(dataframeUsuario.show(4))
print(dataframeItem.show(4))
print(dataframeGenero.show(4))

# Número de NAN y NULL en rating
print ('Número de filas con NAN en las puntuaciones en la columna rating: {0}', dataframePuntuacion.where(isnan(COL_PUNTUACION_RATING[0])).count())
print ('Número de filas con NULL en las puntuaciones en la columna rating: {0}', dataframePuntuacion.where(isnull(COL_PUNTUACION_RATING[0])).count())

# Join puntuaciones-usuarios-item
dataframePuntuacionUsuarioItem = dataframePuntuacion. \
                                  join(dataframeUsuario, dataframePuntuacion.userid==dataframeUsuario.user_userid, 'left_outer'). \
                                  join(dataframeItem, dataframePuntuacion.itemid==dataframeItem.item_itemid, 'left_outer')
# Se eliminan las columnas duplicadas
cabecerasReducidas = list()
for col in dataframePuntuacionUsuarioItem.columns:
    if col != COL_USUARIO_ID[0] and col !=COL_ITEM_ID[0] :
        cabecerasReducidas.append(col)
dataframePuntuacionUsuarioItem = dataframePuntuacionUsuarioItem.select(cabecerasReducidas)

print ('Columnas con el dataframe con joins: {0}', dataframePuntuacionUsuarioItem.columns)
print ('Número de filas: {0}', dataframePuntuacionUsuarioItem.count())

dataframePuntuacionUsuarioItem.cache()
# Se divide el dataframe en entrenamiento y test
dataframePuntuacionUsuarioItemDividido = dataframePuntuacionUsuarioItem.randomSplit([0.7, 0.3], 1234)
dataframePuntuacionUsuarioItemEntrenamiento = dataframePuntuacionUsuarioItemDividido[0]
dataframePuntuacionUsuarioItemTest = dataframePuntuacionUsuarioItemDividido[1]

# Evaluador y cross validation
evaluatorRegression = RegressionEvaluator(labelCol=COL_PUNTUACION_RATING[0])

als = ALS(userCol=COL_PUNTUACION_USERID[0], itemCol=COL_PUNTUACION_ITEMID[0], ratingCol=COL_PUNTUACION_RATING[0], coldStartStrategy='drop')
# als = ALS(userCol=COL_PUNTUACION_USERID[0], itemCol=COL_PUNTUACION_ITEMID[0], ratingCol=COL_PUNTUACION_RATING[0])
grid = ParamGridBuilder(). \
        addGrid(als.rank, [5, 10, 15, 20]). \
        addGrid(als.maxIter, [5, 10]). \
        addGrid(als.alpha, [1.0, 2.0]). \
        addGrid(als.regParam, [0.1, 0.5, 1.0]). \
        build()
# grid = ParamGridBuilder().addGrid(als.rank, [5, 20]).build()
crossValidator = CrossValidator(estimator=als, estimatorParamMaps=grid, evaluator=evaluatorRegression, numFolds=2)
crossValidatorModel = crossValidator.fit(dataframePuntuacionUsuarioItemEntrenamiento)

# Se obtiene la predicción para entrenamiento y test
dataframePuntuacionUsuarioItemEntrenamientoPrediccion = crossValidatorModel.bestModel.transform(dataframePuntuacionUsuarioItemEntrenamiento)
dataframePuntuacionUsuarioItemTestPrediccion = crossValidatorModel.bestModel.transform(dataframePuntuacionUsuarioItemTest)

# Se muestra el número de filas y las que son NAN en el conjunto de entrenamiento y de test
print ('Conjunto de entrenamiento predicción -> Número de filas: {0}, número con NAN en predicción: {1}'.format(dataframePuntuacionUsuarioItemEntrenamientoPrediccion.count(), dataframePuntuacionUsuarioItemEntrenamientoPrediccion.where(isnan(COL_PUNTUACION_PREDICTION[0])).count()))
print ('Conjunto de test predicción -> Número de filas: {0}, número con NAN en predicción: {1}'.format(dataframePuntuacionUsuarioItemTestPrediccion.count(), dataframePuntuacionUsuarioItemTestPrediccion.where(isnan(COL_PUNTUACION_PREDICTION[0])).count()))

# Describe método para rating y prediction
print (dataframePuntuacionUsuarioItemEntrenamientoPrediccion.select(COL_PUNTUACION_RATING[0], COL_PUNTUACION_PREDICTION[0]).describe().show())
print (dataframePuntuacionUsuarioItemTestPrediccion.select(COL_PUNTUACION_RATING[0], COL_PUNTUACION_PREDICTION[0]).describe().show())

# Se obtiene el RMSE sobre los dos conjuntos
rmseEntrenamiento = evaluatorRegression.evaluate(dataframePuntuacionUsuarioItemEntrenamientoPrediccion, {evaluatorRegression.metricName: 'rmse'})
rmseTest = evaluatorRegression.evaluate(dataframePuntuacionUsuarioItemTestPrediccion, {evaluatorRegression.metricName: 'rmse'})

print ('RMSE en training: {0}'.format(rmseEntrenamiento))
print ('RMSE en test: {0}'.format(rmseTest))

# Se crea la lista con la puntuación real y la predicha
xEntrenamiento, yEntrenamiento = list(), list()
for entrenamientoPrediccion in dataframePuntuacionUsuarioItemEntrenamientoPrediccion.collect():
    xEntrenamiento.append(entrenamientoPrediccion[COL_PUNTUACION_RATING[0]])
    yEntrenamiento.append(entrenamientoPrediccion[COL_PUNTUACION_PREDICTION[0]])
xTest, yTest = list(), list()
for testPrediccion in dataframePuntuacionUsuarioItemTestPrediccion.collect():
    xTest.append(testPrediccion[COL_PUNTUACION_RATING[0]])
    yTest.append(testPrediccion[COL_PUNTUACION_PREDICTION[0]])

# Se crea el gráfico y se muestra
plt.clf()
plt.xlim(-1, 6)
plt.ylim(-1, 6)
plt.xlabel('Puntuacion real')
plt.ylabel('Puntuacion segun el modelo')
plt.title('Puntuacion real vs prediccion')

plt.plot([0, 20], [0, 20], 'b')
# Se pasan los datos de entrenamiento y test al gráfico
plt.plot(xEntrenamiento, yEntrenamiento, 'go', label='Entrenamiento')
plt.plot(xTest, yTest, 'ro', label='Test')
plt.legend(loc='lower right')

plt.show()
display()
