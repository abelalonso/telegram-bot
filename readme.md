# Bot Telegram

1. [Introducción](#intro)
2. [Crear el bot en telegram](#telegram)
3. [Creación del Dockerfile](#dockerfile)
4. [Librerías necesarias](#plugins)
5. [Punto de entrada](#app)
6. [Construcción de la imagen de docker](#docker-build)
7. [Configuración de la lambda](#lambda)
8. [Configuración de API Gateway](#apigateway)


<hr>

<a name="intro"></a>

## 1. Introducción

Vamos a crear un bot de telegram sencillo que simplemente repetirá lo que le escribamos. La aplicación se va a desplegar en un contenedor en los servicios de Amazon.

## 2. Crear el bot en telegram

En telegram accedemos al bot **Botfather** y creamo un nuevo bot con el comando:
~~~
/newbot
~~~

Después de darle un nombre y username (terminado en "_bot") tendremos un token que almacenamos en un .env

<hr>

<a name="dockerfile"></a>

## 3. Creación del Dockerfile

Creamos un nuevo Dockerfile con el siguiente contenido.

~~~docker
FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY src/* ./

CMD ["app.handler"]
~~~

<hr>

<a name="plugins"></a>

## 4. Librerias necesarias

Creamos el archivo **requirements.txt** con las librerías de python necesarias para el proyecto:

~~~
python-telegram-bot==13.1
~~~

<hr>

<a name="app"></a>

## 5. Punto de entrada

Creamos la carpeta /src y en su interior el archivo app.py

~~~py
import os
import json
from telegram import (
  Bot,
  Update
)
from telegram.ext import (
  Dispatcher,
  MessageHandler,
  Filters,
  CallbackContext
)


def echo(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(update.message.text)


def handler(event, context):
  print(event)
  bot = Bot(os.environ["BOT_TOKEN"])
  dispatcher = Dispatcher(bot, None, workers=0)
  dispatcher.add_handler(MessageHandler(Filters.text, echo))
  dispatcher.process_update(Update.de_json(json.loads(event["body"]), bot))
~~~

<hr>

<a name="docker-build"></a>

## 6. Construcción de la imagen de docker

Generamos la imagen de docker con el comando:

~~~
docker build -t telegram-bot .
~~~

## 7. Despliegue en Amazon

Nos creamos un profile en nuestro *~/.aws/credentials* con el **access key ID** y el **secret access key**.

Desplegamos la imagen de docker usando el comando que se indica en ECR en el apartado "push commands":

~~~
aws ecr get-login-password --region us-east-1 --profile bot-telegram | docker login --username AWS --password-stdin 433909495486.dkr.ecr.us-east-1.amazonaws.com
~~~

Este comando permite logar nuestro docker dentro de AWS en el repositorio que hemos creado.

Ahora debemos taguear la imagen correctamente:

~~~
docker tag telegram-bot:latest 433909495486.dkr.ecr.us-east-1.amazonaws.com/telegram-bot:latest
~~~

Y subirla al repositorio:

~~~
docker push 433909495486.dkr.ecr.us-east-1.amazonaws.com/telegram-bot:latest
~~~

Copiamos la URI del repositorio que vamos a necesitarla posteriormente.

<hr>

<a name="lambda"></a>

## 8. Configuración de la lambda

Nos vamos al servicio lambda de AWS y creamos una nueva función como **container image**, utilizando la URI que hemos copiado anteriormente.

Configuramos las variables de entorno de la lambda para añadir el token del bot que tenemos almacenado en el .env.

<hr>

<a name="apigateway"></a>

## 9. Configuración de API Gateway

- En el servicio API Gateway creamos una API HTTP. Con integracióo hacia la lambda que hemos creado.

- Configuramos el método POST hacia /bot
- Copiamos la URL de invocación 
- Desde una terminal ejecutamos un curl para asociar la url de invocación de la lambda al bot de télegram.

~~~
curl -F "url=<url de invocación>" https://api.telegram.org/bot<bot-token>/setWebhook
~~~