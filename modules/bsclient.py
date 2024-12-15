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
