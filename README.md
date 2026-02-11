## GitLab CI/CD наглядно

> Простой пример CI/CD с py приложением от hit push до деплоя на прод сервере по ssh, каждый может запустить у себя на лабе.<br>
> https://youtu.be/RuAxFTaP1Zc <br>

### Создать в GitLab проект/репо:
```graphql
- New Project → Blank project → 
Name: demo-ci-cd
Visibility: Private/Internal/Public
Project URL: http://192.168.0.119/ritchie/

```
### Включить Container Registry:
```graphql
- Settings → General → Visibility → Container Registry = ON
```

### Внести в репозиторий переменные
```graphql
Project → Settings → CI/CD → Variables
```
Примерs:
```text
- DOCKERHUB_PASS # на всякий пожарный (надо токен, пароль мовитон)
- DOCKERHUB_USER # тоже на всякий пожарный
- SSH_PRIVATE_KEY # для обеспечения доступа с контейнера на прод сервер (value = сожержимое private key).
```

### Нужен раннер, если его нет.

- Cкачать на сервер и установить
```bash
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt install gitlab-runner -y
```
- в GitLab создать новый runner
```graphql
Project → Settings → CI/CD → Runners → New Project Runer
```
- регистрировать раннер указав название, на чем крутиться будет (докер), токен предложенный во время создания раннера в админке
```bash
sudo gitlab-runner register
```
```graphql
URL: http://192.168.0.119/
Token: XXXX
Executor: docker
Image: docker:24
Privileged: true
```
- в конфиге (/etc/gitlab-runner/config.toml) указать 
```toml
[[runners]]
  executor = "docker"
  privileged = true

  [runners.docker]
    image = "docker:24"
    volumes = ["/cache"]
```
```bash
systemctl restart gitlab-runner
или
gitlab-runner restart
```

### Создать на прод сервере пользователя, и "ssh публичный ключ" в > /home/<user>/.ssh/authorized_keys. Проверить доступ извне.

User + PWD => docker GRP
```bash
sudo useradd -m -s /bin/bash deploy
sudo passwd deploy
sudo usermod -aG docker deploy
```
Проверка
```bash
su - deploy
docker ps
```
SSH KEY (Исп что есть, либо новый)
```bash
ssh-keygen -t ed25519	-f nopass
ssh-copy-id -i nopass.pub deploy@192.168.0.119
или содержимое nopass.pub:
>> /home/deploy/.ssh/authorized_keys
ssh deploy@Rocky
```
На Gitlab
- Project → Settings → CI/CD → Variables
```bash
| Name            | Value                          |
| --------------- | ------------------------------ |
| SSH_PRIVATE_KEY | (содержимое приватного nopass) |

```
Проверка в пайплайне:
```yaml
deploy:
  stage: deploy
  image: alpine
  before_script:
    - apk add --no-cache openssh
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/nopass
    - chmod 600 ~/.ssh/nopass
    - ssh-keyscan 192.168.0.119 >> ~/.ssh/known_hosts
```

### Ну и весь проект с Dockerfile, .gitlab-ci.yml, requirements, test.py, app.py
```bash
../demo-ci-cd/
├── app.py
├── Dockerfile
├── README.md
├── requirements.txt
└── test_app.py
```
> [!NOTE]
> git push orign dev -> deploy on DIND <br>
> git push origin main -> deploy onto real prod <br>



### Workaround

```bash
journalctl -u gitlab-runner -f
docker info
```
Debug
```yaml
debug:
  stage: build
  script:
    - docker info | grep -i mirror
    - env | grep CI_REGISTRY
    - docker info | grep -A5 -i insecure

```
Ошибка
```pgsql
Error logging in to endpoint
https://192.168.0.119:5050/v2/
http: server gave HTTP response to HTTPS client
```
Включаем `{ "insecure-registries": ["192.168.0.119:5050"], ...}` в блок COMMAND в `.gitlab-ci.yml`.
```yaml
services:
  - name: docker:dind
    command:
      - "--insecure-registry=192.168.0.119:5050"
      - "--registry-mirror=https://dockerhub.timeweb.cloud"
      - "--registry-mirror=https://mirror.gcr.io"
```


> [!CAUTION]
> CI_ переменные создаются и прокидываются в job автоматически

```objectivec
CI_REGISTRY
CI_REGISTRY_IMAGE
CI_REGISTRY_USER
CI_REGISTRY_PASSWORD
```
 
