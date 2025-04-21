from fastapi import FastAPI, HTTPException
from typing import Optional, List
from models import *
from typing_extensions import TypedDict
from connection import *
from sqlmodel import select


app = FastAPI()

# temp_bd = [
# {
#     "id": 1,
#     "race": "director",
#     "name": "Мартынов Дмитрий",
#     "level": 12,
#     "profession": {
#         "id": 1,
#         "title": "Влиятельный человек",
#         "description": "Эксперт по всем вопросам"
#     },
#     "skills":
#         [{
#             "id": 1,
#             "name": "Купле-продажа компрессоров",
#             "description": ""

#         },
#         {
#             "id": 2,
#             "name": "Оценка имущества",
#             "description": ""

#         }]
# },
# {
#     "id": 2,
#     "race": "worker",
#     "name": "Андрей Косякин",
#     "level": 12,
#     "profession": {
#         "id": 1,
#         "title": "Дельфист-гребец",
#         "description": "Уважаемый сотрудник"
#     },
#     "skills": []
# },
# ]

@app.on_event("startup")
def on_startup():
    init_db()

# @app.get("/warriors_list")
# def warriors_list() -> List[Warrior]:
#     return temp_bd


# @app.get("/warrior/{warrior_id}")
# def warriors_get(warrior_id: int) -> List[Warrior]:
#     return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]

@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior

# @app.post("/warrior")
# def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
#     warrior_to_append = warrior.model_dump()
#     temp_bd.append(warrior_to_append)
#     return {"status": 200, "data": warrior}

@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}

@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


# @app.put("/warrior{warrior_id}")
# def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
#     for war in temp_bd:
#         if war.get("id") == warrior_id:
#             warrior_to_append = warrior.model_dump()
#             temp_bd.remove(war)
#             temp_bd.append(warrior_to_append)
#     return temp_bd

@app.patch("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

# профессии

@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Profession}):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}
