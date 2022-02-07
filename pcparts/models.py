from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    create_engine,
    Column,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

try:
    from pcparts import settings as settings
except ImportError:
    import settings

DeclarativeBase = declarative_base()


def db_connect():
    url = URL.create(**settings.DATABASE)
    return create_engine(url)


def create_all_metadata(engine):
    DeclarativeBase.metadata.create_all(engine)


class Category(DeclarativeBase):
    __tablename__ = "Category"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __str__(self):
        return f"{self.id}: {self.name}"


class Store(DeclarativeBase):
    __tablename__ = "Store"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)

    def __str__(self):
        return f"{self.id}: {self.name} ({self.url})"


class Part(DeclarativeBase):
    __tablename__ = "Part"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    url = Column(String)
    imageUrl = Column(String)
    recently_scraped = Column(Boolean)
    store = Column(Integer, ForeignKey("Store.id"))
    category = Column(Integer, ForeignKey("Category.id"))


def check_if_item_exists(item, session):
    part = (
        session.query(Part)
        .filter(Part.name == item["name"])
        .filter(Part.store == item["store"])
        .filter(Part.category == item["category"])
        .filter(Part.price == item["price"])
        .first()
    )
    return part is not None


def get_store_id(store_name, store_url, session):
    store = session.query(Store).filter(Store.name == store_name).first()
    if store is None:
        store = Store(name=store_name, url=store_url)
        session.add(store)
        session.commit()
    return store.id


def get_category_id(category_name, session):
    category = session.query(Category).filter(Category.name == category_name).first()
    if category is None:
        category = Category(name=category_name)
        session.add(category)
        session.commit()
    return category.id


def get_all_categories(session):
    categories = session.query(Category).all()
    return {category.name: category.id for category in categories}


def get_all_stores(session):
    stores = session.query(Store).all()
    return {store.name: store.id for store in stores}


def insert_new_item(item, session):
    part = Part(
        name=item["name"],
        price=item["price"],
        url=item["url"],
        imageUrl=item["imageUrl"],
        store=item["store"],
        category=item["category"],
    )
    session.add(part)
    session.commit()


if __name__ == "__main__":
    engine = db_connect()
    create_all_metadata(engine)
    Session = sessionmaker(engine)
    session = Session()
