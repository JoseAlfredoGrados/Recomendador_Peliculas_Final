# Recomendador_Peliculas_Final
Jose Alfredo Grados Chuquitaype
## Indicaciones para poder ejecutarlo correctamente📦

_Primero debemos asegurarnos de subir todos los archivos a las dos máquinas virtuales y si se puede en la misma ruta._

## Clab 🛠️

_Para acceder al Colab puede dar click al siguiente enlace:_

* [Colab](https://colab.research.google.com/drive/115FMVkoSl0Ufjk5E44Dxku9y37pz6Rv3?usp=sharing)

## Procedimiento para ejecutar 🖇️

Primero se configuran las máquinas virtuales con spark.

Segundo inicializamos spark en el nodo master escribiendo en la terminal `start-master.sh` y en el nodo worker `start-worker.sh spark://192.168.100.53:7077`(en este caso pongo esa ip ya que mi nodo master tiene la ip 192.168.100.53).

Luego se suben los archivos mencionados a las máquinas virtuales, luego se accede a la carpeta misma donde se encuentran los archivos en el nodo master y se ejecuta el siguiente comando: `spark-submit recomendador.py`

## Gestión de Errores 

Puede ser que como a mi me pasó al inicio salgan errores de que no se encuentran los archivos en ese caso y para solucionar eso se tiene la indicación de tener los archivos en las dos máquinas y si se puede en la misma ubicación, por ejemplo en la carpeta Downloads donde se descarga por defecto.

En caso igual no lo lea ingrese al archivo recomendador.py y cambie las líneas

## Autores ✒️

* **Jose Alfredo Grados Chuquitaype** - *Recomendador de Películas* - [Jose Grados](#jose-grados)
