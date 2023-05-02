### Preview Crawler
[Test for [Python Developer](https://ods.ai/jobs/34de3d16-9dce-4f9b-a063-147f16b13e0f) position]

Crawler implements next specification:
```
openapi: 3.0.2

info:
  title: CrawlerAPI
  version: "1.0"

paths:
  /content/parse:
    post:
      description: |
        Принцип работы как у превью ссылок в телеграме или другом мессенджере.
        Принимает на вход урл любой страницы в Интернете, отдает на выход заголовок, описание и картинку страницы.
        Необходимо обеспечить стабильную работу для как можно большего числа страниц.
      responses:
        "200":
          description: Страница успешно спарсилась
          content:
            application/json:
              schema:
                type: object
                required:
                  - data
                properties:
                  data:
                    type: object
                    required:
                      - title
                    properties:
                      title:
                        type: string
                      description:
                        type: string
                      imageUrl:
                        type: string
                        format: uri
        "4XX":
          description: Ошибка
          content:
            application/json:
              schema:
                type: object
                required:
                  - error
                properties:
                  error:
                    type: object
                    required:
                      - message
                    properties:
                      message:
                        type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - url
              properties:
                url:
                  type: string
                  format: uri

```

Run crawler (Python 3.8):
```
flask run
```