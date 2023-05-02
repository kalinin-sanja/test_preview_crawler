import logging

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask
from flask import request

from configs.configuration import Configuration
from crawler.crawler import PreviewCrawler
from schema import preview_scheme
from validation.validate_json import validate_json

configs = Configuration()


def set_logger(level=logging.INFO):
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    console.setFormatter(formatter)
    logger = logging.getLogger(configs.logger_name)
    logger.addHandler(console)
    logger.setLevel(level)


set_logger(configs.logger_level)

spec = APISpec(
    title="CrawlerAPI",
    version="1.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

app = Flask(__name__)


@app.route('/content/parse', methods=['POST'])
@validate_json(request_schema=preview_scheme.PreviewParameter,
               response_schema=preview_scheme.PreviewSchema,
               methods='POST')
def parse():
    """
    Gets preview of web page.
    ---
    post:
      responses:
        200:
          description: Page has parsed successfully.
          content:
            application/json:
              schema: PreviewSchema
        4XX:
          description: Error
          content:
            application/json:
              schema: ErrorScheme
    """
    data = request.json

    crawler = PreviewCrawler(data['url'])
    result = crawler.crawl()

    return {'data': result}


with app.test_request_context():
    spec.path(view=parse)
    # print(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    app.run()
