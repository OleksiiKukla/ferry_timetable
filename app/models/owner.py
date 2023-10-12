from app.db.session import Base
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class Owner(Base):
    __tablename__ = "owners"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))

    ferries = relationship("Ferry", back_populates="owner")
