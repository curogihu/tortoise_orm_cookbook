"""
This example demonstrates how you can use transactions with tortoise
"""
from tortoise import Tortoise, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model
from tortoise.transactions import atomic, in_transaction


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    class Meta:
        table = "event"

    def __str__(self):
        return self.name


async def run():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    try:
        async with in_transaction() as connection:
            event = Event(name="Test")
            await event.save(using_db=connection)

            # .using_db(connection)の有無で違いがありそう
            # async def bound_to_fall()の時はついていないので。
            await Event.filter(id=event.id).using_db(connection).update(name="Updated name")
            saved_event = await Event.filter(name="Updated name").using_db(connection).first()
            await connection.execute_query("SELECT * FROM non_existent_table")
    except OperationalError:
        pass
    saved_event = await Event.filter(name="Updated name").first()
    print("function name: run-first, ", saved_event)

    '''
    You can wrap your function with this decorator to run it into one transaction. If error occurs transaction will rollback.
    1. 処理1
    2. bound_to_fallで名前を変える
    3. わざと例外を発生させる
    4. ロールバックにより、bound_to_fallでの名前変更が反映されていない
    '''
    @atomic()
    async def bound_to_fall():
        event = await Event.create(name="Test")
        await Event.filter(id=event.id).update(name="Updated name")
        saved_event = await Event.filter(name="Updated name").first()
        print("function name: bound_to_fall, ", saved_event.name)
        raise OperationalError()

    try:
        await bound_to_fall()
    except OperationalError:
        pass
    saved_event = await Event.filter(name="Updated name").first()
    print("function name: run-second, ", saved_event)


if __name__ == "__main__":
    run_async(run())