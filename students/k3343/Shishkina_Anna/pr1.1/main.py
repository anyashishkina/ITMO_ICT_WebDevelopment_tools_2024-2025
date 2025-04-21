from fastapi import FastAPI, HTTPException
from typing import List, Dict
from models import *

app = FastAPI()

temp_bd = [
{
    "id": 1,
    "race": "director",
    "name": "Мартынов Дмитрий",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    "skills":
        [{
            "id": 1,
            "name": "Купле-продажа компрессоров",
            "description": ""

        },
        {
            "id": 2,
            "name": "Оценка имущества",
            "description": ""

        }]
},
{
    "id": 2,
    "race": "worker",
    "name": "Андрей Косякин",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    },
    "skills": []
},
]

@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd

@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]

@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}

@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}

@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd

@app.get("/professions", response_model=List[Profession])
def get_professions():
    professions = []
    seen_ids = set()
    for warrior in temp_bd:
        prof = warrior["profession"]
        if prof["id"] not in seen_ids:
            professions.append(prof)
            seen_ids.add(prof["id"])
    return professions

@app.get("/profession/{profession_id}", response_model=Profession)
def get_profession(profession_id: int):
    for warrior in temp_bd:
        if warrior["profession"]["id"] == profession_id:
            return warrior["profession"]
    raise HTTPException(status_code=404, detail="Profession not found")

@app.post("/profession", response_model=Profession)
def create_profession(profession: Profession):
    for warrior in temp_bd:
        if warrior["profession"]["id"] == profession.id:
            raise HTTPException(status_code=400, detail="Profession ID already exists")
    new_warrior = {
        "id": max(w["id"] for w in temp_bd) + 1,
        "race": "worker",
        "name": "New Warrior",
        "level": 1,
        "profession": profession.dict(),
        "skills": []
    }
    temp_bd.append(new_warrior)
    return profession

@app.put("/profession/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, profession: Profession):
    updated = False
    for warrior in temp_bd:
        if warrior["profession"]["id"] == profession_id:
            warrior["profession"] = profession.dict()
            updated = True
    if not updated:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession

@app.delete("/profession/{profession_id}")
def delete_profession(profession_id: int):
    profession_exists = any(
        warrior["profession"]["id"] == profession_id 
        for warrior in temp_bd
    )
    
    if not profession_exists:
        raise HTTPException(status_code=404, detail="Profession not found")
    
    for warrior in temp_bd:
        if warrior["profession"]["id"] == profession_id:
            warrior["profession"] = None
    
    return {"status": 200, "message": "Profession removed from all warriors"}