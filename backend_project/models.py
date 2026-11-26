from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    role = db.Column(
        db.String(20),
        nullable=False,
        default="user",
        server_default="user",
    )

    trails = db.relationship("Trail", back_populates="owner", lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, candidate_password):
        return check_password_hash(self.password_hash, candidate_password)

    def __repr__(self):
        return f"<User {self.email}>"

class Trail(db.Model):
    __tablename__ = "trails"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=True)
    distance_miles = db.Column(db.Float, nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(
        db.Boolean, nullable=False, default=False, server_default=db.false()
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    owner = db.relationship("User", back_populates="trails")

    def __repr__(self):
        return f"<Trail {self.name}>"