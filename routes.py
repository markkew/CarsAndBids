from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Bid, Listing, CarImage
from extensions import db
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os


def init_routes(app):
    # Add this configuration for file uploads
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @app.route('/')
    def index():
        cars =  Listing.query.all()  # Get all cars from the database
        print(f"Found {len(cars)} cars in the database")  # Debug print
        for car in cars:
            print(f"Car: {car.name}, Starting Bid: {car.starting_bid}")  # Debug print
        return render_template('index.html', cars=cars)

    @app.route('/auctions')
    def auctions():
        # Get all listings with their associated images
        listings = (
            db.session.query(Listing)
            .all()
        )
        
        # Get only the first image for each listing
        for listing in listings:
            listing.image_urls = (
                db.session.query(CarImage)
                .filter(CarImage.listing_id == listing.id)
                .order_by(CarImage.created_at)  # Orders by upload time
                .first()  # Gets only the first image
            )
        
        return render_template('auctions.html', listings=listings)
    
    @app.route('/auctions/<int:listing_id>' , methods=['GET'])
    def auction_details(listing_id):
        listing = Listing.query.get(listing_id)
        images = CarImage.query.filter_by(listing_id=listing_id).all()
        # get seller username
        seller = (
            db.session.query(User.username)
            .filter(User.id == listing.seller_id)
            .first()
        )
        
        # get latest bid amount
        latest_bid = (
            db.session.query(Bid.amount)
            .filter(Bid.listing_id == listing_id)
            .order_by(Bid.timestamp.desc())
            .first()
        )
        latest_bid = latest_bid if latest_bid is not None else 0.00

         # Calculate time remaining
        current_time = datetime.now()
        time_left = listing.end_datetime - current_time
        days_left = time_left.days

        return render_template('auction_details.html',
            listing=listing,
            images=images,
            seller=seller,
            latest_bid=latest_bid,
            days_left=days_left,
        )
    
    @app.route('/past-results')
    def past_results():
        return render_template('past_results.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        try:
            # Get current time for comparison
            current_time = datetime.utcnow()
            print(current_time)

            # Get number of active bids for current user
            bid_count = (db.session.query(Bid)
                .join(Listing, Bid.listing_id == Listing.id)
                .filter(
                    Bid.user_id == current_user.id,
                    Listing.end_datetime > current_time
                    
                ).count())
            print(bid_count)

            # Get user's active bids with listing details
            user_bids = (
                db.session.query(Bid, Listing)
                .join(Listing, Bid.listing_id == Listing.id)
                .filter(
                    Bid.user_id == current_user.id,
                    Listing.end_datetime > current_time
                )
                .order_by(Listing.end_datetime)  # Order by ending soonest
                .all()
            )
            print("User bids:", user_bids)

            # Get number of active listings for current user
            user_listings_count = (
                db.session.query(Listing)
                .filter(
                    Listing.seller_id == current_user.id,
                    Listing.end_datetime > current_time
                ).count()
            )
            print("User listings count:", user_listings_count)

            user_listings = (
                db.session.query(Listing)
                .filter(
                    Listing.seller_id == current_user.id,
                    Listing.end_datetime > current_time
                ).all()
            )
            print("User listings:", user_listings)

            # Get total amount of all bids
            total_amount = (
                db.session.query(func.sum(Bid.amount))
                .join(User, Bid.user_id == User.id)
                .filter(Bid.user_id == current_user.id)
                .scalar()
            )
            total_amount = total_amount if total_amount is not None else 0.0
            print(total_amount)
    
            # Format the bid information
            bids_info = [{
                'amount': bid.amount,
                'timestamp': bid.timestamp,
                'listing': listing,
                'time_left': listing.end_datetime - current_time  # Add time remaining
            } for bid, listing in user_bids]
            
            return render_template('dashboard.html', bids=bids_info, bid_count=bid_count, user_listings_count=user_listings_count, user_listings=user_listings, total_amount=total_amount)
        except Exception as e:
            print(f"Error in dashboard: {e}")
            flash('Error loading dashboard data', 'danger')
            return render_template('dashboard.html', bids=[], bid_count=0)

    @app.route('/delete_listing/<int:listing_id>', methods=['POST'])
    @login_required
    def delete_listing(listing_id):
        try:
            listing = Listing.query.get(listing_id)
            if listing and listing.seller_id == current_user.id:
                db.session.delete(listing)
                db.session.commit()
                flash('Listing deleted successfully', 'success')
        except Exception as e:
            flash('Error deleting listing', 'danger')
            print(f"Error in delete_listing: {e}")
        return redirect(url_for('dashboard'))
        

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
                
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/sell')
    @login_required
    def sell():
        return render_template('sell.html')

    @app.route('/sell', methods=['POST'])
    @login_required
    def sell_post():
        try:
            # Debug prints
            print("Files received:", request.files)
            images = request.files.getlist('images')
            print("Number of images:", len(images))
            
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            year = request.form.get('year')
            make = request.form.get('make') 
            model = request.form.get('model')
            mileage = request.form.get('mileage')
            colour = request.form.get('colour')
            starting_bid = request.form.get('starting_bid')
            reserve_price = request.form.get('reserve_price')
            end_datetime = request.form.get('end_datetime')

            # Create a new listing
            listing = Listing(
                seller_id=current_user.id,
                name=name,
                description=description,
                year=year,
                make=make,
                model=model,
                mileage=mileage,
                colour=colour,
                starting_bid=starting_bid,
                reserve_price=reserve_price,
                end_datetime=end_datetime,
            )
            db.session.add(listing)
            db.session.commit()

            # Debug print
            print("Listing created with ID:", listing.id)

            # Process and save images
            for image in images:
                if image and image.filename:
                    print("Processing image:", image.filename)  # Debug print
                    filename = secure_filename(image.filename)
                    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    print("Saving to:", image_path)  # Debug print
                    image.save(image_path)
                    
                    car_image = CarImage(
                        listing_id=listing.id,
                        image_url=f"uploads/{unique_filename}"
                    )
                    db.session.add(car_image)
                    print("Added image to database:", unique_filename)  # Debug print
            
            db.session.commit()
            flash('Car listed successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in sell_post: {e}")  # This will show the actual error
            flash('Error listing car', 'danger')
            return redirect(url_for('sell'))
            
    # continue tomorrow
    @app.route('/bid/<int:listing_id>', methods=['POST'])
    @login_required
    def bid(listing_id):
        try:
            listing = Listing.query.get(listing_id)
            if not listing:
                flash('Listing not found', 'danger')
                return redirect(url_for('auctions'))
            
            amount = request.form.get('amount')
            if not amount:
                flash('Bid amount is required', 'danger')
                return redirect(url_for('auction_details', listing_id=listing_id))
            
            # Check if the bid amount is greater than the current highest bid
            current_highest_bid = (
                db.session.query(func.max(Bid.amount))
                .filter(Bid.listing_id == listing_id)
                .scalar()
            )
            current_highest_bid = current_highest_bid if current_highest_bid is not None else 0.00
            
            if float(amount) <= current_highest_bid:
                flash('Bid amount must be greater than the current highest bid', 'danger')
            

        except Exception as e:
            flash(f'Error placing bid: {e}', 'danger')
            return redirect(url_for('auction_details', listing_id=listing_id))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

            if not username or not password:
                flash('Username and password are required', 'danger')
                return redirect(url_for('register'))
            
            elif user:
                flash('Username already exists', 'danger')
                return redirect(url_for('register'))
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')# do
    
