from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships
    listings = db.relationship('Listing', backref='seller', lazy=True)
    bids = db.relationship('Bid', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    # Car details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    mileage = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    colour = db.Column(db.String(50), nullable=False)
    
    # Auction details
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    starting_bid = db.Column(db.Numeric(10,2), nullable=False)
    reserve_price = db.Column(db.Numeric(10,2))
    start_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    
    # Define relationship to bids
    bids = db.relationship('Bid', backref='listing', lazy=True)

class Bid(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CarImage(db.Model):
    __tablename__ = 'car_images'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Listing
    listing = db.relationship('Listing', backref=db.backref('images', lazy=True))

    def __repr__(self):
        return f'<CarImage {self.image_url}>'

