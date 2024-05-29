from pprint import pprint
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from db_client import create_table, insert_flat

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

URL = 'https://realt.by/sale/flats/'

PARAM_PATTERN = {
    "Количество комнат": "room",
    "Площадь общая": "square",
    "Год постройки": "year",
    "Этаж / этажность": "floor",
    "Тип дома": "type_house",
    "Область": "region",
    "Населенный пункт": "city",
    "Улица": "street",
    "Район": "district",
    "Координаты": "coordinate",
}


def get_response(url: str):
    response = requests.get(url, headers=HEADERS)
    return response


def get_last_page() -> int:
    response = get_response(URL)

    soup = BeautifulSoup(response.text, 'lxml')
    page = soup.find_all('a',
                         class_='focus:outline-none sm:focus:shadow-10bottom cursor-pointer select-none inline-flex font-normal text-body min-h-[2.5rem] min-w-[2.5rem] py-0 items-center !px-1.25 justify-center mx-1 hover:bg-basic-200 rounded-md disabled:text-basic-500')
    page = page[-1].text
    page = int(page)
    return page


def get_flats_links(last_page: int) -> list:
    links = []
    for page in tqdm(range(1, last_page + 1), desc='PAGE: '):
        resp = get_response(f'{URL}?page={page}')

        soup = BeautifulSoup(resp.text, 'lxml')
        cards = soup.find_all('div', {'data-index': True})

        for card in cards:
            try:
                price = card.find('span',
                                  class_='flex items-center md:mr-1 mr-2 md:mb-1 mb-0.5').text
            except Exception as e:
                print(f'ERROR! {resp.url}')
                continue

            price = price.replace(' р.', '').replace(' ', '')
            if price.isdigit():
                link = card.find('a', href=True)['href']
                links.append(f'https://realt.by{link}')
    return links


def get_flat_data(url: str) -> dict:
    flat = {
        "room": "",
        "square": "",
        "year": "",
        "floor": "",
        "type_house": "",
        "region": "",
        "city": "",
        "street": "",
        "district": "",
        "coordinate": "",
        "flat_id": url.split('/')[-2],
    }

    resp = get_response(url)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'lxml')

        try:
            title = soup.find('h1',
                              class_='order-1 mb-0.5 md:-order-2 md:mb-4 block w-full !inline-block lg:text-h1Lg text-h1 font-raleway font-bold flex items-center').text
        except Exception as e:
            title = ''

        price = soup.find('h2',
                          class_='!inline-block mr-1 lg:text-h2Lg text-h2 font-raleway font-bold flex items-center').text
        price = price.replace(' р.', '').replace(' ', '')
        price = int(price)

        try:
            image = soup.find('div', class_='swiper-wrapper').find_all('img')[1]['src']
        except Exception as e:
            image = ''

        try:
            discription = soup.find('div', class_=['description_wrapper__tlUQE']).text
        except Exception as e:
            discription = ''

        params = soup.find_all('li', class_='relative py-1')
        for param in params:
            key = param.find('span', class_='text-basic sm:flex-shrink-0 mr-2').text
            value = param.find(['p', 'a']).text.replace(' м²', '').replace('\xa0', '')
            if key not in PARAM_PATTERN:
                continue
            flat[PARAM_PATTERN[key]] = value

        flat['title'] = title
        flat['price'] = price
        flat['image'] = image
        flat['discription'] = discription
        return flat

    else:
        print(f'{resp.status_code} | {url}')


def run():
    create_table()
    links = get_flats_links(3)
    for link in tqdm(links, desc='FLAT DATA: '):
        data = get_flat_data(link)
        if data:
            insert_flat(data)


if __name__ == '__main__':
    run()
