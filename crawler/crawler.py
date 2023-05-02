import traceback
from logging import getLogger
from urllib.parse import urlparse, urlunparse, urljoin

import requests
from PIL import Image
from bs4 import BeautifulSoup, Tag

from configs.configuration import Configuration

configs = Configuration()
logger = getLogger(configs.logger_name)


class PreviewCrawler:
    def __init__(self, url: str):
        self.address = urlparse(url)

    def _get_img_url(self, url: str):
        url_parts = urlparse(url)
        new_url = url
        if len(url_parts.netloc) == 0:
            new_url = urljoin(self.address.geturl(), url)
        elif len(url_parts.scheme) == 0:
            new_url = urlunparse([self.address.scheme] + list(url_parts)[1:])

        return new_url

    def _extract_img(self, parser: BeautifulSoup, first_only: bool = True):
        max_area = 0
        biggest_img_url = None

        img_tags = parser.find_all('img')
        last_read = None
        for tag in img_tags:
            if tag.has_attr('src'):
                url = tag['src']
                try:
                    img_url = self._get_img_url(url)
                    response = requests.get(img_url, stream=True)
                    last_read = img_url
                    img = Image.open(response.raw)
                    width, height = img.size
                    area = width*height
                    if area > max_area:
                        max_area = area
                        biggest_img_url = img_url

                    if first_only:
                        break
                except (TypeError, Exception) as err:  # pylint: disable=broad-except
                    logger.debug(f'{type(err).__name__} Could not get image from {url} \n'
                                 f'{str(traceback.format_exc())}')
                    # ignore this image
                    continue

        if biggest_img_url is None:
            biggest_img_url = last_read

        return biggest_img_url

    def _trim_text(self, text: str, limit: int):
        str_end = '...'
        if len(text) <= limit:
            return text
        if not (text[limit - 1].isalpha() or text[limit - 1].isnumeric()):
            return text[:limit]

        end_idx = text[:limit].rfind(' ')

        if (end_idx > -1) and (end_idx + len(str_end) < len(text)):
            return text[:end_idx] + str_end

        return text[:(limit - len(str_end))] + str_end

    def _get_max_text_from_children(self, element: Tag) -> str:
        """
        Recursively walks through DOM elements and looks for leaves with biggest text.
        :param element: DOM element
        :return: text of first DOM element (according to text size and specified threshold)
        """
        max_text = ''
        child_count = 0

        for child in element.children:
            child_count += 1

            if isinstance(child, Tag):
                text = self._get_max_text_from_children(child)
            else:
                text = str(child)

            text = text.strip()
            if len(text) > len(max_text):
                max_text = text

            if len(max_text) >= configs.text_size_threshold:
                break

        if (child_count == 0) or (max_text == ''):
            max_text = element.get_text().strip()

        return max_text

    def crawl(self):
        logger.info(f'Crawling of {self.address.geturl()}...')
        headers = {"User-Agent": "Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/31.0.1650.0 Safari/537.36"}
        data = requests.get(self.address.geturl(), headers=headers)
        parser = BeautifulSoup(data.text, 'html.parser')

        title = parser.title.get_text()
        text = self._get_max_text_from_children(parser.find("body"))
        text = self._trim_text(text, configs.text_size_limit)
        img_url = self._extract_img(parser, configs.extract_first_img_only)
        logger.info(f'Crawling of {self.address.geturl()} has finished.')

        return {'title': title, 'description': text, 'imageUrl': img_url}
