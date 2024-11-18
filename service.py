from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException

app = FastAPI()
spiders_params = dict()


@app.post('/')
async def add_group(group: str, from_date: Optional[str] = None):
    try:
        from_date = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
        spiders_params[group] = {'group': group, 'from_date': from_date}
        return {'group': group, 'from_date': from_date, 'status': 'created'}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.get('/{group}')
async def reed_results(group: str):
    if group in spiders_params:
        return {'group': group, 'data': None}
    else:
        raise HTTPException(status_code=404, detail='group not found')


@app.put('/{group}')
async def update_group(group: str, from_date: str):
    if group in spiders_params:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            spiders_params[group]['from_date'] = from_date
            return {'group': group, 'from_date': from_date, 'status': 'updated'}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))
    else:
        raise HTTPException(status_code=404, detail='group not found')


@app.delete('/{group}')
async def delete_group(group: str):
    if group in spiders_params:
        from_date = spiders_params[group]['from_date']
        del spiders_params[group]
        return {'group': group, 'from_date': from_date, 'status': 'deleted'}
    else:
        raise HTTPException(status_code=404, detail='group not found')


@app.get('/')
async def list_groups():
    return list(spiders_params.values())
