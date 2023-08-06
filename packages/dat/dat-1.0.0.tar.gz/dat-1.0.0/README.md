# Dat
### A thin orm-ish wrapper for pymongo

Check out the docs at [readthedocs.org](http://dat.readthedocs.org/en/latest/).

# Examples

### Schema and saving instances to the database

dat is inspired by Django's ORM and as such defining the model schema is quite
similar. However,

    from dat.models import Model
    from dat.fields import List, Int, Float, Char, TimeStamp

    class Person(Model):

        collection_name = 'my_custom_collection_name'

        created = TimeStamp(default=datetime.utcnow)
        age = Int()
        name = Char(index=TEXT)
        parents = List()
        height = Float()

    bob = Person(name='bob', age=30, parents=['Mary', 'John'], height=1.7)
    bob.save()

### Get and Filter

    bob = Person.get({'name': 'bob'})
    print bob.parents
    print type(bob)
        => ["Mary", "John"]
        => __main__.Person

    queryset = Person.filter({'name': 'bob'})
    print queryset
        => '<QuerySet(Person, {'name': 'bob'}, None, None, None, limit=None)>'
    # returns an instance of QuerySet that can be iterated over, extended by
    # chaining on another filter or can be updated using the "update" method
