from app import app
from extensions import db
from models import Listing, Bid
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        # Add test cars
        # listings = [
        #     Listing(
        #         name="2023 Luxury Sedan",
        #         description="A beautiful luxury sedan in perfect condition",
        #         make="Toyota",
        #         model="Camry",
        #         year=2023,
        #         mileage=10000,
        #         starting_bid=50000.00,
        #         seller_id=1,
        #         image_url="https://images.unsplash.com/photo-1555215695-3004980ad54e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        #         end_datetime=datetime.now(datetime.UTC) + timedelta(days=30)
        #     ),
        #     Listing(
        #         name="Classic Sports Car",
        #         description="A rare classic sports car with low mileage",
        #         make="Honda",
        #         model="Civic",
        #         year=2017,
        #         mileage=10000,
        #         starting_bid=75000.00,
        #         seller_id=1,
        #         image_url="https://images.unsplash.com/photo-1503376780353-7e6692767b70?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        #         end_datetime=datetime.now(datetime.UTC) + timedelta(days=30)
        #     ),
        #     Listing(
        #         name="Vintage Collection",
        #         description="A stunning vintage car collection",
        #         make="Toyota",
        #         model="Camry",
        #         year=2023,
        #         mileage=10000,
        #         starting_bid=100000.00,
        #         seller_id=1,
        #         image_url="https://images.unsplash.com/photo-1553440569-bcc63803a83d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        #         end_datetime=datetime.now(datetime.UTC) + timedelta(days=30)
        #     )
        # ]
        
        # # Add cars to database
        # for car in listings:
        #     db.session.add(car)
        bids = [
            Bid(
                amount=100000.00,
                user_id=1,
                listing_id=1
            )
        ]
        for bid in bids:
            db.session.add(bid)
        # Commit changes
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 

