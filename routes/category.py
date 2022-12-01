from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from config.db import conn
from models.category import categories
from schemas.schemas import Category
from schemas.schemas import Category_Update
import crawl as crawler


category = APIRouter()


def get_categories():
    return conn.execute(categories.select()).fetchall()


def get_category(id: int):
    return conn.execute(categories.select().where(categories.c.id == id)).first()


def get_youngest_child_categories():
    return conn.execute(categories.select().where(categories.c.id.notin_(categories.select().with_only_columns(categories.c.parent_category)))).fetchall()


def create_category(category: Category):
    new_category = {"id": category.id,
                    "name": category.name,
                    "path": category.path,
                    "title": category.title,
                    "description": category.description,
                    "keywords": category.keywords,
                    "parent_category": category.parent_category}
    result = conn.execute(categories.insert().values(new_category))
    return conn.execute(categories.select().where(categories.c.id == result.lastrowid)).first()


def update_category(id: int, category: Category_Update):
    conn.execute(categories.update().values(name=category.name,
                                            path=category.path,
                                            title=category.title,
                                            description=category.description,
                                            keywords=category.keywords,
                                            parent_category=category.parent_category).where(categories.c.id == id))
    return conn.execute(categories.select().where(categories.c.id == id)).first()


def delete_category(id: int):
    category = get_category(id)
    result = conn.execute(categories.delete().where(categories.c.id == id))
    return category


@category.get("/categories", tags=["Category"], response_model=list[Category])
def get_categories_endpoint():
    result = get_categories()
    # result = get_youngest_child_categories()
    return result


@category.get("/categories/{id}", tags=["Category"], response_model=Category)
def get_category_endpoint(id: int):
    result = get_category(id)
    return result


@category.post("/categories", tags=["Category"], response_model=list[Category])
def create_categories_endpoint(categories: list[Category]):
    if not categories:
        return JSONResponse(status_code=404, content={"message": "Category details not found"})
    else:
        categories_list = []
        for category in categories:
            if (get_category(category.id) is None):
                # return get_category(category.id)
                db_category = create_category(category)
                category_json = category.dict()
                categories_list.append(category_json)
    return JSONResponse(content=categories_list)


@category.put("/categories/{id}", tags=["Category"], response_model=Category)
def update_category_endpoint(id: int, category: Category_Update):
    result = update_category(id, category)
    return result


@category.delete("/categories/{id}", tags=["Category"], status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(id: int):
    result = delete_category(id)
    return result


@category.get("/youngest_categories", tags=["Category"], response_model=list[Category])
def get_youngest_categories_endpoint():
    result = get_youngest_child_categories()
    return result


old_categories = get_categories()
new_categories = []
all_cate_ids = [2]

def get_cate(data):
    _id, parent_id = data
    df = crawler.get_data_from_api(crawler.data_url + str(_id), 'children_categories')
    if(not 'id' in df.columns):
        return  
    
    new_cate = crawler.get_data_from_api(crawler.data_url + str(_id),'category')
    new_cate['parent_category'] = _id
    new_cate['id'] = int(new_cate['id'])
    new_cate in old_categories and new_categories.append(new_cate)
    # print(len(all_cate_ids))
    cur_cate_ids = df['id'].values.tolist()
    new_cate_ids = [i for i in cur_cate_ids if i not in all_cate_ids]
    
    if(new_cate_ids == []):
        return 
    all_cate_ids.extend(new_cate_ids)
    next_cate = [[i, _id] for i in new_cate_ids]
    crawler.runner(next_cate, get_cate)
            
# def crawl_categories():
#     get_cate([2, 2])

@category.get("/crawl-categories")
def crawl_categories_endpoint():
    get_cate([2, 2])
    # return get_categories()
    return new_categories