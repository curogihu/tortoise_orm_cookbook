from tortoise import Tortoise, fields, run_async
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)


Tournament_Pydantic = pydantic_model_creator(Tournament)
print(Tournament_Pydantic.schema_json(indent=4))


async def run():
    # # 公式と比較してmemoryの前にコロン(:)がない
    # await Tortoise.init(db_url='sqlite//:memory:', modules={'models': ['__main__']})
    # await Tortoise.generate_schemas()

    # tournament = await Tournament.create(name='New tournament')
    # tourpy = await Tournament_Pydantic.from_tortoise_orm(tournament)

    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    # Create object
    tournament = await Tournament.create(name="New Tournament")
    # Serialise it
    tourpy = await Tournament_Pydantic.from_tortoise_orm(tournament)

    print('=' * 30)
    print(tourpy.dict())

    print('=' * 30)
    print(tourpy.json(indent=4))


if __name__ == '__main__':
    run_async(run())
