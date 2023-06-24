# Recomendador_Peliculas_Final

## Indicaciones para poder ejecutarlo correctamente📦

_Primero debemos asegurarnos de subir todos los archivos a las dos máquinas virtuales y si se puede en la misma ruta.
En esta rute github también se encuentran los archivos del dataset. De preferencia descargar todos juntos._

## Colab 🛠️

_Para acceder al Colab puede dar click al siguiente enlace:_

* [Colab](https://colab.research.google.com/drive/115FMVkoSl0Ufjk5E44Dxku9y37pz6Rv3?usp=sharing)

## Procedimiento para ejecutar 🖇️

Primero se configuran las máquinas virtuales con spark.

Segundo inicializamos spark en el nodo master escribiendo en la terminal `start-master.sh` y en el nodo worker `start-worker.sh spark://192.168.100.53:7077`(en este caso pongo esa ip ya que mi nodo master tiene la ip 192.168.100.53).

Luego se suben los archivos mencionados a las máquinas virtuales, luego se accede a la carpeta misma donde se encuentran los archivos en el nodo master y se ejecuta el siguiente comando: `spark-submit recomendador.py`

## Gestión de Errores 

Puede ser que como a mi me pasó al inicio salgan errores de que no se encuentran los archivos en ese caso y para solucionar eso se tiene la indicación de tener los archivos en las dos máquinas y si se puede en la misma ubicación, por ejemplo en la carpeta Downloads donde se descarga por defecto.

En caso igual no lo lea ingrese al archivo recomendador.py y cambie las líneas de la 22 a la 27 de la siguiente manera:

```
RUTA_FICHERO_PUNTUACION = '/ubicación completa del directorio/u.data'
RUTA_FICHERO_USUARIO = '/ubicación completa del directorio/u.user'
RUTA_FICHERO_ITEM = '/ubicación completa del directorio/u.item'
RUTA_FICHERO_GENERO = '/ubicación completa del directorio/u.genre'
SEPARADOR_TABULADOR = '\t'
SEPARADOR_PIPE = '|'
```

Ya que según estuve leyendo a veces spark no ubica bien los archivos y para ayudar a simplificar las cosas lo mejor sería colocándole toda la ruta y no sólo el nombre del archivo.

## Desafíos Enfrentados y Nuevas Perspectivas

El primero fue el construir el recomendador de películas ya que a pesar de tener el Spark y ya todo configurado lo que importa es que el recomendador funcione y sea entrenado correctamente.

Luego de haberlo hecho y haber configurado el Spark en las máquinas virtuales, salió el error de que no encontraba el archivo y fue el cuál se lo consulté en la clase. Pero después de indagar y leer línea por línea la ejecución me di cuenta que al inicio había una primera vez en la que sí leía bien el archivo y luego ya no entonces concluí que el que no encontraba el archivo era el nodo trabajador. Entonces lo que hice fue poner los archivos también en el nodo worker y terminó funcionando correctamente.

También Averiguando un poco vi que también estos modelos de recomandación no sólo los usan para eso, al ser NLP se puede utilizar para la clasificación de películas, ver las películas con más o menos puntuación, etc. Sería interesante poder hacer algo así también.

## Autores ✒️

* **Jose Alfredo Grados Chuquitaype** - *Recomendador de Películas* - [Jose Grados](#jose-grados)
