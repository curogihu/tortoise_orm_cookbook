"""
Pydantic tutorial 1

Here we introduce:
* Creating a Pydantic model from a Tortoise model
* Docstrings & doc-comments are used
* Evaluating the generated schema
* Simple serialisation with both .dict() and .json()
"""
from tortoise import Tortoise, fields, run_async
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Tournament(Model):
    """
    This references a Tournament
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    #: The date-time the Tournament record was created at
    created_at = fields.DatetimeField(auto_now_add=True)


Tournament_Pydantic = pydantic_model_creator(Tournament)

# Print JSON-schema
print(Tournament_Pydantic.schema_json(indent=4))
'''
{
    "title": "Tournament",
    "description": "This references a Tournament",
    "type": "object",
    "properties": {
        "id": {
            "title": "Id",
            "minimum": 1,
            "maximum": 2147483647,
            "type": "integer"
        },
        "name": {
            "title": "Name",
            "maxLength": 100,
            "type": "string"
        },
        "created_at": {
            "title": "Created At",
            "description": "The date-time the Tournament record was created at",
            "readOnly": true,
            "type": "string",
            "format": "date-time"
        }
    },
    "required": [
        "id",
        "name",
        "created_at"
    ],
    "additionalProperties": false
}
'''


async def run():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    # Create object
    tournament = await Tournament.create(name="New Tournament")
    # Serialise it
    tourpy = await Tournament_Pydantic.from_tortoise_orm(tournament)

    # As Python dict with Python objects (e.g. datetime)
    # print(tourpy.dict())
    '''
    {'id': 1, 'name': 'New Tournament', 'created_at': datetime.datetime(2021, 2, 24, 4, 50, 3, 384475, tzinfo=<UTC>)}
    '''

    # As serialised JSON (e.g. datetime is ISO8601 string representation)
    # print(tourpy.json(indent=4))
    '''
    {
        "id": 1,
        "name": "New Tournament",
        "created_at": "2021-02-24T04:50:47.010833+00:00"
    }
    '''


if __name__ == "__main__":
    run_async(run())