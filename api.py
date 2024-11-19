import json
from typing import Optional
from datetime import datetime
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
spider_params_db = redis.Redis(decode_responses=True, db=0)
crawled_data_db = redis.Redis(db=1)


@app.post('/')
async def add_group(group: str, from_date: Optional[str] = None):
    try:
        if from_date:
            datetime.strptime(from_date, '%Y-%m-%d')
            spider_params = {'group': group, 'from_date': from_date}
        else:
            spider_params = {'group': group}
        await spider_params_db.hmset(group, spider_params)
        return spider_params
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.get('/{group}')
async def reed_results(group: str):
    data = await crawled_data_db.get(group)
    if data:
        return json.loads(data)
    else:
        raise HTTPException(status_code=404, detail='group not found')


@app.put('/{group}')
async def update_group(group: str, from_date: str):
    data = await spider_params_db.hgetall(group)
    if data:
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            data['from_date'] = from_date
            await spider_params_db.hmset(group, data)
            return data
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))
    else:
        raise HTTPException(status_code=404, detail='group not found')


@app.delete('/{group}')
async def delete_group(group: str):
    data = await spider_params_db.hgetall(group)
    if data:
        await spider_params_db.delete(group)
        await crawled_data_db.delete(group)
        return data
    else:
        raise HTTPException(status_code=404, detail='group not found')


@app.get('/')
async def list_groups():
    keys = await spider_params_db.keys()
    return [await spider_params_db.hgetall(key) for key in keys]
