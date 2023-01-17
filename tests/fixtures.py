from typing import Any

import pytest
from sqlalchemy import FromClause
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import Engine
from sqlalchemy.future import create_engine
from sqlalchemy.orm import Session

from tests.models import Base
from tests.models import User


def create_query_params(
    column_names: list[str],
    search: str = '',
    regex: bool = False,
    start: int = 0,
    length: int = 10,
    order: [dict[int, str]] = None,
) -> dict[str, Any]:
    params = {
        'draw': '1',
        'start': str(start),
        'length': str(length),
        'search[value]': str(search),
        'search[regex]': 'true' if regex else 'false',
    }

    for i, _item in enumerate(column_names):
        cols: str = f'columns[{i}]'
        params[f'{cols}[data]'] = _item
        params[f'{cols}[name]'] = _item
        params[f'{cols}[searchable]'] = 'true'
        params[f'{cols}[orderable]'] = 'true'
        params[f'{cols}[search][value]'] = ''
        params[f'{cols}[search][regex]'] = 'false'

    for i, item in enumerate(order or [{'column': 0, 'dir': 'asc'}]):
        for key, value in item.items():
            params[f'order[{i}][{key}]'] = str(value)
    return params


users: dict[str, dict[str, Any]] = {
    'spongebob': {
        'username': 'spongebob',
        'fullname': 'Spongebob Squarepants',
        'email_address': 'spongebob@bikinibottom.org',
        'color': 'yellow',
    },
    'harold': {
        'username': 'harold',
        'fullname': 'Harold Squarepants',
        'email_address': 'harold@bikinibottom.org',
        'color': 'yellow',
    },
    'margaret': {
        'username': 'margaret',
        'fullname': 'Margaret Squarepants',
        'email_address': 'margaret@bikinibottom.org',
        'color': 'yellow',
    },
    'jelly': {'username': 'jelly', 'fullname': 'Jellyfish', 'email_address': 'jelly@bikinibottom.org', 'color': 'pink'},
    'patrick': {
        'username': 'patrick',
        'fullname': 'Patrick Star',
        'email_address': 'patrick@@bikinibottom.org',
        'color': 'pink',
    },
    'squidward': {
        'username': 'squidward',
        'fullname': 'Squidward Tentacles',
        'email_address': 'squidward@bikinibottom.org',
        'color': 'grey',
    },
    'gary': {
        'username': 'gary',
        'fullname': 'Gary the Snail',
        'email_address': 'gary@bikinibottom.org',
        'color': 'pinkgreen',
    },
    'larry': {
        'username': 'larry',
        'fullname': 'Larry the Lobster',
        'email_address': 'larry@bikinibottom.org',
        'color': 'red',
    },
    'krabs': {'username': 'krabs', 'fullname': 'Mr. Krabs', 'email_address': 'krabs@@krabshack.com', 'color': 'red'},
    'pearl': {
        'username': 'pearl',
        'fullname': 'Pearl Krabs',
        'email_address': 'pearl@@krabshack.com',
        'color': 'greypink',
    },
    'plankton': {
        'username': 'plankton',
        'fullname': 'Sheldon Plankton',
        'email_address': 'plankton@chumbucket.com',
        'color': 'green',
    },
    'karen': {
        'username': 'karen',
        'fullname': 'Karen Plankton',
        'email_address': 'karen@chumbucket.com',
        'color': 'metal',
    },
    'sandy': {
        'username': 'sandy',
        'fullname': 'Sandy Cheeks',
        'email_address': 'sandy@squirrelpower.org',
        'color': 'brown',
    },
    'mrspuff': {
        'username': 'mrspuff',
        'fullname': 'Mrs. Puff',
        'email_address': 'mrspuff@drivesafely.com',
        'color': 'greybluered',
    },
    'patchy': {
        'username': 'patchy',
        'fullname': 'Patchy the Pirate',
        'email_address': 'patchy@abovethesea.org',
        'color': 'mixed',
    },
    'potty': {
        'username': 'potty',
        'fullname': 'Potty the Parrot',
        'email_address': 'potty@abovethesea.org',
        'color': 'greenyellowred',
    },
    'mm': {'username': 'mm', 'fullname': 'Mermaid Man', 'email_address': 'mm@superhero.net', 'color': 'orange'},
    'bb': {'username': 'bb', 'fullname': 'Barnacle Boy', 'email_address': 'bb@superhero.net', 'color': 'redblack'},
    'dutchman': {
        'username': 'dutchman',
        'fullname': 'The Flying Dutchman',
        'email_address': 'dutchman@ghostship.org',
        'color': 'bluegrey',
    },
    'neptune': {
        'username': 'neptune',
        'fullname': 'King Neptune',
        'email_address': 'neptune@gods.net',
        'color': 'greenred',
    },
}


@pytest.fixture(scope='module')
def engine() -> Engine:
    engine = create_engine(url='sqlite://', connect_args={'check_same_thread': False})
    return engine


@pytest.fixture(scope='module', autouse=True)
def setup_db(engine) -> bool:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        try:
            for user_dict in users.values():
                user = User()
                for key, value in user_dict.items():
                    setattr(user, key, value)
                session.add(user)
            session.commit()
        except SQLAlchemyError:
            return False
    return True


@pytest.fixture(scope='function')
def column_names() -> list[str]:
    return ['id', 'username', 'email_address', 'fullname', 'color']


@pytest.fixture(scope='function')
def table() -> FromClause:
    return User.__table__
