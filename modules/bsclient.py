import logging,requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urljoin

def get_soup(url:str, params:dict={}) -> BeautifulSoup|None:

    s = requests.Session()
    retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 403, 500, 502, 503, 504 ])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = s.get(
            url=url,
            params=params,
        )
        if response.status_code == 200:
            html = response.content.decode(response.apparent_encoding)
            soup = BeautifulSoup(html, 'html.parser')
            meta_refresh = soup.find("meta",attrs={"http-equiv":"refresh"})
            if meta_refresh:
                _, text = meta_refresh["content"].split(";")
                if text.strip().lower().startswith("url="):
                    redirect_path = text.strip()[4:]
                    new_url = urljoin(url, redirect_path)
                    return get_soup(new_url)
            return soup
        else:
            logging.warning(f"Request HTML error url: {url} response: {response}")
            return None
    except requests.exceptions.RequestException as e:
        logging.warning(f"{url} Request HTML failed: url: {url} exception: {e}")
        return None

# def extract_new_videos_from_list_pages(url:str, base_params:dict={}, blacklist_tags:list=[], whitelist_tags:list=[]) -> list[dict]:
#     all_movies = []
#     i = 1
#     while True:
#         base_params["page"] = i
#         soup = get_html_bs(url, base_params)
#         if soup == None:
#             continue
#         movies = soup.select("div.g-main-grid > article > a")
#         for movie in movies:
#             info_url = movie.get("href")
#             oreno_id = info_url.replace('https://oreno3d.com/movies/', '')
#             author = movie.select_one("div.box-text1 > div.box-text-in").text
#             title = movie.select_one("h2").text
#             tags = movie.select_one("div.box-text2 > div.box-text-in").text.strip().split()

#             # タグの中に、ブラックリストのタグがある、もしくはホワイトリストのタグがない場合はスルーする
#             if len(set(tags) & set(blacklist_tags)) != 0:
#                 logging.debug("  skip(BlackList): {author}: {title}".format(author=author, title=title))
#                 continue
#             elif len(set(tags) & set(whitelist_tags)) == 0:
#                 logging.debug("  skip(ExciteLess): {author}: {title}".format(author=author, title=title))
#                 continue

#             # 残ったものを本採用リストに追加
#             all_movies.append({"author": author, "title": title, "oreno_id": oreno_id})
#         if len(movies) == 0:
#             break
#         i = i + 1
#     return all_movies