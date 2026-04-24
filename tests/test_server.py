"""Minimal Flask test server for pamfilico-admin-auth integration tests.

Exposes:
  GET  /health
  POST /api/v1/admin/login
  GET  /api/v1/admin/users

Mirrors flask-collection's test-server pattern: own User model + seed data + a
blueprint built via ``build_admin_blueprint``.
"""

import os
from datetime import datetime

from flask import Flask
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from pamfilico_flask_core import init_errors

from pamfilico_admin_auth import build_admin_blueprint

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://test:test@localhost:5498/testdb"
)
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


SEED_USERS = [
    User(id=1, email="alice@example.com", name="Alice", created_at=datetime(2025, 1, 1, 9, 0)),
    User(id=2, email="bob@example.com", name="Bob", created_at=datetime(2025, 2, 1, 9, 0)),
    User(id=3, email="carol@example.com", name="Carol", created_at=datetime(2025, 3, 1, 9, 0)),
    User(id=4, email="dave@elsewhere.org", name="Dave", created_at=datetime(2025, 3, 15, 9, 0)),
]


def seed_db():
    Base.metadata.create_all(engine)
    session = Session()
    try:
        if session.query(User).count() == 0:
            session.add_all(SEED_USERS)
            session.commit()
    finally:
        session.close()


app = Flask(__name__)
init_errors(app)


@app.route("/health")
def health():
    return {"status": "ok"}


app.register_blueprint(
    build_admin_blueprint(user_model=User, get_db_session=Session),
    url_prefix="/api/v1/admin",
)

seed_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
