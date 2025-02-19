import bs4
import requests
import re
import html
from urllib.parse import urljoin
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import parse_qs
import argparse
import tqdm

URL_TEMPLATE = "https://kazneb.kz/ru/bookView/view?brId={}&simple=true"

parser = argparse.ArgumentParser(
    prog="Kazneb book downloader",
    description="A small script to download a book from kazneb.kz, since they do not provide such option.",
)

parser.add_argument("book_url", help="a link to the book")
parser.add_argument(
    "-o", "--out_dir", help="specify output directory, defaults to book id"
)
args = parser.parse_args()

# standardize url
book_id = re.search("[0-9]+", args.book_url).group(0)
book_url = URL_TEMPLATE.format(book_id)

# get page urls
page = requests.get(book_url)
soup = bs4.BeautifulSoup(page.content, "html.parser")
scripts = "".join([x.text for x in soup.findAll("script")])
page_urls = [html.unescape(x) for x in re.findall(r'pages.push\("(.*)"\);', scripts)]
book_data = re.sub("\n+", "\n", soup.find("table").text).split("200%")[0]

# save imgs
print(book_data)
out_dir = Path(args.out_dir if args.out_dir else book_id)
out_dir.mkdir(exist_ok=True)
for image_url in tqdm(page_urls):
    file_name = image_url.rsplit("/")[-1].split("?")[0]
    img_data = requests.get(urljoin(args.book_url, image_url)).content
    with open(out_dir / file_name, "wb") as handler:
        handler.write(img_data)
