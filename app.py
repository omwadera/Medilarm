import os
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, BooleanField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from bson.objectid import ObjectId
from forms import MedicineForm
from scheduler import start_scheduler
from datetime import datetime, time, timedelta
from bunch import Bunch

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads/medicine_photos'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['medilarm_db']

# Medicine collection
medicines_collection = db['medicines']

# Function to check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    form = MedicineForm()

    if form.validate_on_submit():
        # Handle file upload for medicine photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = 'default_medicine.png'

        medicine_data = {
            'name': form.name.data,
            'photo': filename,
            'before_breakfast': form.before_breakfast.data,
            'after_breakfast': form.after_breakfast.data,
            'breakfast': form.breakfast.data,
            'before_lunch': form.before_lunch.data,
            'after_lunch': form.after_lunch.data,
            'lunch': form.lunch.data,
            'before_dinner': form.before_dinner.data,
            'after_dinner': form.after_dinner.data,
            'dinner': form.dinner.data,
            'morning': form.morning.data,  # Save the value of the new checkboxes
            'afternoon': form.afternoon.data,  # Save the value of the new checkboxes
            'evening': form.evening.data,  # Save the value of the new checkboxes
            'notes': form.notes.data,
        }

        # Insert the medicine document into the MongoDB collection
        medicines_collection.insert_one(medicine_data)

        return redirect(url_for('dashboard'))

    return render_template('add_medicine.html', form=form)

@app.route('/delete_medicine/<medicine_id>', methods=['POST'])
def delete_medicine(medicine_id):
    # Find the medicine with the given ID and remove it from the database
    medicines_collection.delete_one({'_id': ObjectId(medicine_id)})
    return redirect(url_for('dashboard'))

@app.route('/edit_medicine/<medicine_id>', methods=['GET', 'POST'])
def edit_medicine(medicine_id):
    medicine_data = medicines_collection.find_one({"_id": ObjectId(medicine_id)})
    form = MedicineForm()

    if form.validate_on_submit():
        # Convert medicine_data to Bunch and populate the form
        medicine = Bunch(medicine_data)
        form.populate_obj(medicine)

        # Handle file upload
        if form.photo.data:  # Check if a new file was uploaded
            file = form.photo.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Update the file path in the medicine data
            medicine.photo = filename

        # Update medicine data in the collection
        medicines_collection.update_one({"_id": ObjectId(medicine_id)}, {"$set": medicine})

        return redirect(url_for('dashboard'))

    # Populate form fields with existing medicine data
    form.process(data=medicine_data)

    return render_template('edit_medicine.html', form=form, medicine=medicine_data)

@app.route('/', methods=['GET', 'POST'])
@app.route('/dashboard/<meal>', methods=['GET', 'POST'])
def dashboard(meal=None):
    if meal:
        # Filter medicines by the selected meal option
        filtered_medicines = medicines_collection.find({f"{meal}": True})
    else:
        # Get all medicines
        filtered_medicines = medicines_collection.find()

    return render_template('dashboard.html', medicines=filtered_medicines)

def get_next_scheduled_time(medicine):
    now = datetime.now()
    meal_times = [
        ('before_breakfast', 'Before Breakfast'),
        ('after_breakfast', 'After Breakfast'),
        ('breakfast', 'During Breakfast'),
        ('before_lunch', 'Before Lunch'),
        ('after_lunch', 'After Lunch'),
        ('lunch', 'During Lunch'),
        ('before_dinner', 'Before Dinner'),
        ('after_dinner', 'After Dinner'),
        ('dinner', 'During Dinner'),
        # Add similar entries for other meal times
    ]
    next_scheduled_time = None  # Initialize the variable
    for attribute, meal_time in meal_times:
        is_scheduled = medicine.get(attribute)
        if is_scheduled:
            meal_time_preference = time(hour=8, minute=0)  # Adjust this time according to the meal time preference
            if attribute.startswith('after_'):
                meal_time_preference = time(hour=10, minute=0)  # Adjust this time according to the meal time preference
            # You can adjust the meal_time_preference based on the actual meal times
            scheduled_time = datetime.combine(now.date(), meal_time_preference)
            if scheduled_time >= now and (not next_scheduled_time or scheduled_time < next_scheduled_time):
                next_scheduled_time = scheduled_time
    return next_scheduled_time

@app.route('/medicine_details/<medicine_id>', methods=['GET', 'POST'])
def medicine_details(medicine_id):
    medicine = medicines_collection.find_one({'_id': ObjectId(medicine_id)})
    if not medicine:
        return redirect(url_for('dashboard'))

    # Calculate the next scheduled intake time
    next_scheduled_time = get_next_scheduled_time(medicine)

    return render_template('medicine_details.html', medicine=medicine, next_scheduled_time=next_scheduled_time)


@app.route('/uploads/medicine_photos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True)