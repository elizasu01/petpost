from flask import Flask, render_template, request, redirect
import boto3
import json
import os

app = Flask(__name__)

# Replace with your actual S3 bucket name
BUCKET_NAME = 'petpost-images'
REGION = 'ca-central-1'

# Set up S3 client (assumes IAM role or local credentials)
s3 = boto3.client('s3', region_name=REGION)

# Helper: Load pets from JSON file
def load_pets():
    if os.path.exists('pets.json'):
        with open('pets.json', 'r') as f:
            return json.load(f)
    return []

# Helper: Save pets to JSON file
def save_pets(pets):
    with open('pets.json', 'w') as f:
        json.dump(pets, f)

# Home route - list of all pets
@app.route('/')
def index():
    pets = load_pets()
    return render_template('index.html', pets=pets)

# Upload form and handler
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        name = request.form['name']
        breed = request.form['breed']
        age = request.form['age']
        image = request.files['image']

        if image:
            filename = image.filename

            # Upload image to S3
            s3.upload_fileobj(
                image,
                BUCKET_NAME,
                filename,
                ExtraArgs={'ACL': 'public-read'}  # Needed if ACLs are enabled
            )

            # Construct the public image URL
            image_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{filename}"

            # Create pet entry
            new_pet = {
                'name': name,
                'breed': breed,
                'age': age,
                'image_url': image_url
            }

            pets = load_pets()
            pets.append(new_pet)
            save_pets(pets)

            return redirect('/')

    return render_template('upload.html')

# Run the Flask app on port 80 so EC2 can serve it
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
