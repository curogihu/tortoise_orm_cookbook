from tortoise import Tortoise, fields, run_async
from tortoise.models import Model
from tortoise.query_utils import Prefetch


class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    events: fields.ReverseRelation["Event"]

    def __str__(self):
        return self.name

# Event     - Tournament
# Event(M)  - Team(M)
class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    # 外部キー
    tournament: fields.ForeignKeyRelation[Tournament] = fields.ForeignKeyField(
        "models.Tournament", related_name="events"
    )
    
    # 多対多モデル
    participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    # 多対多モデルの時に設定が必要
    events: fields.ManyToManyRelation[Event]

    def __str__(self):
        return self.name


async def run():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    # トーナメントを1つ作成
    tournament = await Tournament.create(name="tournament")

    # トーナメントに紐づくイベントを2つ作成
    await Event.create(name="First", tournament=tournament)
    await Event.create(name="Second", tournament=tournament)


    tournament_with_filtered = (
        await Tournament.all()
        # Laravelでいう、Tournament::with('events')->where('name', 'First')
        .prefetch_related(Prefetch("events", queryset=Event.filter(name="First")))
        .first()
    )

    # Prefetchの説明
    # Sometimes it is required to fetch only certain related records. You can achieve it with Prefetch object:

    # tournament
    # tournament
    print(tournament_with_filtered)
    print(await Tournament.first().prefetch_related("events"))

    tournament_with_filtered_to_attr = (
        await Tournament.all()
        .prefetch_related(
            # to_attrで別名にできる
            Prefetch("events", queryset=Event.filter(name="First"), to_attr="to_attr_events_first"),
            Prefetch(
                "events", queryset=Event.filter(name="Second"), to_attr="to_attr_events_second"
            ),
        )
        .first()
    )

    # [<Event: 1>]
    # [<Event: 2>]
    print(tournament_with_filtered_to_attr.to_attr_events_first)
    print(tournament_with_filtered_to_attr.to_attr_events_second)


if __name__ == "__main__":
    run_async(run())