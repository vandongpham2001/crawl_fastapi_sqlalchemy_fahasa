# -*- coding: utf-8 -*-
import pandas as pd
import json
import requests

data_url = 'https://www.fahasa.com/fahasa_catalog/product/loadCatalog?category_id='
api_url = 'http://127.0.0.1:8000/api/'
check_url1 = api_url + 'check-id?table_name={}&_id={}'
check_url2 = api_url + 'check-product-option?product_id={}&option_id={}'

# lấy dữ liệu từ api


def get_data_from_api(url, att):
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    response = requests.get(url, headers=headers)
    json = response.json()
    if(type(json[att]) == list):
        df = pd.DataFrame(json[att])
    else:
        df = pd.DataFrame(json[att], index=[0])
    return df


# check exists
def is_exists(url):
    res = requests.get(url)
    return json.loads(res.text)

# insert data

def insert(table_name, data):
    url = api_url + 'insert?table_name='+table_name
    res = requests.post(url, data=json.dumps(data))
    print(res.text)
    return json.loads(res.text)


# crawl categories
new_categories = []
all_category = ['2']
df = get_data_from_api(data_url + "2", 'category')
df['parent_category'] = '2'
if(not is_exists(check_url1.format('categories', '2'))):
    new_categories = [insert('categories', df.iloc[0].to_dict())]


def get_all_category(_id, all_category):
    df = get_data_from_api(data_url + _id, 'children_categories')
    if(not 'id' in df.columns):
        return
    children = df['id'].values.tolist()
    children_is_not_exists = [
        item for item in children if item not in all_category]

    if(children_is_not_exists == []):
        return all_category
    all_category.extend(children_is_not_exists)
    for _idCate in children_is_not_exists:
        if(not is_exists(check_url1.format('categories', _idCate))):
            df = get_data_from_api(data_url + _idCate, 'category')
            df['parent_category'] = _id
            new_categories.append(insert('categories', df.iloc[0].to_dict()))
        get_all_category(_idCate, all_category)


get_all_category(all_category[0], all_category)
print(new_categories)

# Crawl attributes
attributes = get_data_from_api(
    data_url+"2", 'attributes')[['id', 'code', 'label']]
new_attributes = [insert('attributes', row.to_dict()) for index, row in attributes.iterrows(
) if not is_exists(check_url1.format('attributes', row['id']))]
print(new_attributes)


# #Crawl options
new_options = []


def get_options(_id):
    attributes = get_data_from_api(data_url + _id, 'attributes')[['id', 'options']]
    for index, row in attributes.iterrows():
        options = pd.DataFrame(row['options'])[['id', 'label']]
        options['attribute_id'] = row['id']
        print(options)
        n = [insert('options', row.to_dict()) for index, row in options.iterrows() if not is_exists(check_url1.format('options', row['id']))]
        new_options.extend(n)


cate_ids = json.loads(requests.get(api_url + "cate-childlest-list").text)
[get_options(str(_id)) for _id in cate_ids]
