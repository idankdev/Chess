# Chess
Chess Engine Powered by Deep Learning

## Quick Install
### Prerequisites
* Docker
#### Linux

Login to docker with your docker credentials: `$ sudo docker login -u <username> -p <password> docker.io`
```
$ sudo docker pull idankash/chess && sudo docker run --net=host --name chess -i -t chess -d
```
open ```http://localhost``` in your browser.

#### Windows

Start Powershell as administrator.
Login to docker with your docker credentials: `$ docker login -u <username> -p <password> docker.io`
```
$ docker pull idankash/chess && sudo docker run --net=host --name chess -i -t chess -d
```
open ```http://localhost``` in your browser.
