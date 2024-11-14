from functools import wraps
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
import random
import string
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from utils import PCA, User


from bson import ObjectId


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
bcrypt = Bcrypt(app)
# This should be moved to .env in production
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DEBUG'] = True
TIME_SLOT_FILE = 'time_slot.txt'

# MongoDB connection
client = MongoClient(
    "mongodb+srv://cs5200439:Ueqewn3pQZIMghUT@cluster0.3eyw7.mongodb.net/")
db = client['newsrep']
users_collection = db['users']
posts_collection = db['posts']
rep_dec = db['rep_dec']

pca = PCA()


def read_time_slot():
    """Read the time slot from the time_slot.txt file."""
    try:
        with open(TIME_SLOT_FILE, 'r') as file:
            time_slot = int(file.read().strip())  # Read and convert to integer
            return time_slot
    except FileNotFoundError:
        print("time_slot.txt not found.")
        return None
    except ValueError:
        print("Invalid time slot format.")
        return None


@app.route('/api/get_time_slot', methods=['GET'])
def get_time_slot():
    """API endpoint to get the time slot from time_slot.txt."""
    time_slot = read_time_slot()

    if time_slot is not None:
        return jsonify({"success": True, "timeSlot": time_slot})
    else:
        return jsonify({"success": False, "message": "Failed to read time slot"}), 500


# Middleware to verify token in request headers
def authMiddleware(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Remove "Bearer " from the token string
            token = token.replace("Bearer ", "")
            # Decode the token
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Set the username in the request object
            request.username = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)

    return decorated_function

# Register endpoint


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    users_collection.insert_one({"username": username, "password": hashed_password,
                                 "pseudonym": None  # Initialize pseudonym as null
                                 })
    return jsonify({"message": "User registered successfully"}), 201

# Login endpoint


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = users_collection.find_one({"username": username})
    if user and bcrypt.check_password_hash(user["password"], password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=1)  # Expire after 1 hour
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"token": token})  # Send the token back in response
    return jsonify({"error": "Invalid username or password"}), 401

# Post News endpoint (protected by authMiddleware)

@app.route('/api/post', methods=['POST'])
@authMiddleware
def post_news():
    data = request.json
    news_text = data.get('newsText')

    # Check if news text is provided
    if not news_text:
        return jsonify({"error": "News text cannot be empty"}), 400

    # Retrieve user data from the database
    user_data = users_collection.find_one({"username": request.username})
    ct = 0  # Initialize counter for reputation decrement

    if user_data and 'rep_dec' in user_data:
        rep_dec_list = user_data['rep_dec']
        
        # Iterate over the reputation decrement list
        for entry in rep_dec_list:
            # Check if pseudonym matches and increment counter if so
            if entry['Cipib'].get('pseudonym') == user_data.get('pseudonym'):
                ct += 1
    
    # Default to "Anonymous" if no pseudonym is set
    pseudonym = user_data.get("pseudonym", "Anonymous")

    # Insert the news post in the posts collection
    posts_collection.insert_one({
        "username": pseudonym,  # Use pseudonym instead of username
        "newsText": news_text,
        "timestamp": datetime.utcnow(),
        "User_rep": ct  # Store count of reputation decrement
    })

    return jsonify({"message": "News posted successfully under pseudonym"}), 201

@app.route('/api/like', methods=['POST'])
@authMiddleware
def like_post():
    try:
        data = request.json
        post_id = data.get('post_id')
        # Use the username set by the middleware
        username = data.get('username')
        # time_slot = read_time_slot()

        if not post_id:
            return jsonify({"success": False, "message": "Post ID is required"}), 200

        # Fetch the post to check if the user is trying to like their own post
        post = db.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            return jsonify({"success": False, "message": "Post not found"}), 200

        user_a_data = users_collection.find_one({"username": username})
        user_a_pseudonym = user_a_data.get('pseudonym')

        print(post['username'])
        print(user_a_pseudonym)
        if post["username"] == user_a_pseudonym:
            return jsonify({"success": False, "message": "You cannot like your own post"}), 200
        
        # # Check if the like already exists for the post by the current user
        if db.likes.find_one({"post_id": post_id, "username": username}):
            return jsonify({"success": False, "message": "You have already liked this post"}), 200
        else :
            print("couldnt find!")
        # user_a_data = users_collection.find_one({"username": username})
        try:
            user_b_data = users_collection.find_one(
                {"pseudonym": post["username"]})
        except Exception as e:
            return jsonify({"success": True, "message": "Post Liked but Pseudonym doesn't exist anymore"}), 200
        if not user_b_data:
            return jsonify({"success": True, "message": "Post Liked but Pseudonym doesn't exist anymore"}), 200

        # Process the repu tation declaration and validation
        user_a = User(username, pca)
        user_b = User(user_b_data.get('username'), pca)

        user_a.private_key = RSA.import_key(user_a_data.get('private_key'))
        user_a.public_key = RSA.import_key(user_a_data.get('public_key'))
        user_b.private_key = RSA.import_key(user_b_data.get('private_key'))
        user_b.public_key = RSA.import_key(user_b_data.get('public_key'))

        user_a.pseudonyms[user_a_data.get("time_slot")] = int(user_a_data.get(
            "pseudonym", "Anonymous"))  # Default to "Anonymous" if no pseudonym is set
        user_b.pseudonyms[user_b_data.get('time_slot')] = int(user_b_data.get(
            "pseudonym", "Anonymous"))  # Default to "Anonymous" if no pseudonym is set

        user_a.signed_pseudonym = int(user_a_data.get("signed_pseudonym"))
        user_b.signed_pseudonym = int(user_b_data.get("signed_pseudonym"))

        reputation_info = username.encode('utf-8')
        reputation_declaration = user_a.create_reputation_declaration(
            reputation_info, user_a_data.get("time_slot"))
        cipib = (user_b.pseudonyms[user_b_data.get(
            'time_slot')], user_b.public_key, user_b_data.get("time_slot"))
        is_valid = pca.verify_reputation_declaration(
            reputation_declaration, reputation_info, cipib, user_b.signed_pseudonym)

        if not is_valid:
            return jsonify({"success": False, "message": "Reputation validation failed"}), 200

        # Insert the like into the likes collection
        db.likes.insert_one({
            "post_id": post_id,
            "username": username,
            "timestamp": datetime.utcnow()
        })
        serial_no = random.randint(100000, 999999)

        # Insert the reputation declaration into the rep_dec collection
        rep_dec_entry = {
            "serial_no": serial_no,
            "Cipia": {
                "pseudonym": str(reputation_declaration[0][0]),
                "public_key": str(reputation_declaration[0][1].export_key().decode()),
                "time_slot": str(reputation_declaration[0][2])
            },
            "Cipib": {
                "pseudonym": str(user_b.pseudonyms[user_b_data.get("time_slot")]),
                "public_key": str(user_b.public_key.export_key().decode()),
                "time_slot": user_b_data.get("time_slot")
            },
            "signed_reputation": reputation_declaration[1].hex(),
            "timestamp": datetime.utcnow()
        }

        # Insert the reputation declaration into the rep_dec collection

        # Append the reputation declaration to the user's rep_dec array
        users_collection.update_one(
            {"username": user_b_data.get('username')},
            {"$push": {"rep_dec": rep_dec_entry}}
        )

        db.rep_dec.insert_one(rep_dec_entry)
        return jsonify({"success": True, "message": "Post liked successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "An error occurred while liking the post"}), 200


@app.route('/api/user_time_slot', methods=['GET'])
def get_user_time_slot():
    username = request.args.get('username')
    user = users_collection.find_one({"username": username})

    if user and 'time_slot' in user:
        return jsonify({"success": True, "time_slot": user["time_slot"]})
    else:
        return jsonify({"success": False, "message": "User or time_slot not found"}), 404


@app.route('/api/get_rep_dec', methods=['GET'])
@authMiddleware
def get_rep_dec():
    username = request.username  # Assuming authMiddleware provides this
    print("Fetched username =", username)

    if not username:
        return jsonify({"success": False, "error": "Username is required"}), 400

    # Fetch the user from the database
    user = users_collection.find_one({"username": username})

    if user and 'rep_dec' in user:
        # Get the 10 most recent reputation declarations
        rep_dec_list = user['rep_dec'][:10]

        # Convert timestamps and ObjectIds to strings for JSON serialization
        for entry in rep_dec_list:
            if 'timestamp' in entry:
                # Convert datetime to string
                entry['timestamp'] = entry['timestamp'].isoformat()
            if '_id' in entry:
                entry['_id'] = str(entry['_id'])  # Convert ObjectId to string
            if 'Cipi' in entry and 'public_key' in entry['Cipi']:
                entry['Cipi']['public_key'] = str(entry['Cipi']['public_key'])
            if 'pseudonym' in entry:
                entry['Cipi']['pseudonym'] = entry['Cipi'].get('pseudonym')
                entry['Cipi']['time_slot'] = entry['Cipi'].get('time_slot')

        return jsonify(success=True, rep_dec=rep_dec_list), 200
    else:
        return jsonify(success=True, rep_dec=[]), 200


@app.route('/api/get_trv', methods=['GET'])
@authMiddleware
def get_trv():
    username = request.username  # Assuming authMiddleware provides this
    print("Fetched username =", username)

    if not username:
        return jsonify({"success": False, "error": "Username is required"}), 400

    # Fetch the user from the database
    user = users_collection.find_one({"username": username})

    if user and 'trv' in user:
        # Get the 10 most recent reputation declarations
        trv_list = user['trv'][:10]
        print(trv_list)

        # Convert timestamps and ObjectIds to strings for JSON serialization

        return jsonify(success=True, trv=trv_list), 200
    else:
        return jsonify(success=True, trv=[]), 200

@app.route('/api/posts', methods=['GET'])
@authMiddleware
def get_posts():
    posts = posts_collection.find()
    posts_list = [
        {
            "_id": str(post.get("_id", "")),  # Convert ObjectId to string or empty if not found
            "username": post.get("username", "Anonymous"),  # Default to "Anonymous" if not found
            "newsText": post.get("newsText", ""),  # Default to empty string if not found
            "timestamp": post.get("timestamp", ""),  # Default to empty string if not found
            "User_rep": post.get("User_rep", 0)  # Default to 0 if not found
        }
        for post in posts
    ]
    return jsonify(posts_list), 200

@app.route('/api/user_info', methods=['GET'])
@authMiddleware
def user_info_signed_pseudonym():
    user_data = users_collection.find_one({"username": request.username})
    pseudonym = user_data.get("pseudonym", 'Not Assigned')

    return jsonify({"success": True, "pseudonym": pseudonym}), 200
# Endpoint to issue a pseudonym


@app.route('/api/issue_pseudonym', methods=['POST'])
@authMiddleware
def issue_pseudonym():
    # Retrieve user data from MongoDB
    user_data = users_collection.find_one({"username": request.username})
    if not user_data:
        return jsonify({"success": False, "error": "User not found"}), 200

    user = User(request.username, pca)
    time_slot = read_time_slot()

    try:
        # Issue the pseudonym

        pca.issue_pseudonym(user, time_slot)
        pseudonym = str(user.pseudonyms[time_slot])

        # Convert signed pseudonym to string to handle large values
        signed_pseudonym = str(user.signed_pseudonym)

        # Update user record in MongoDB
        users_collection.update_one(
            {"username": request.username},
            {"$set": {"pseudonym": pseudonym,
                      "signed_pseudonym": signed_pseudonym,
                      "public_key": user.public_key.export_key().decode(),
                      "private_key": user.private_key.export_key().decode(),
                      "time_slot": time_slot
                      }}
        )
        return jsonify({"success": True, "message": "Pseudonym issued", "pseudonym": pseudonym}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 200


@app.route('/api/verify_pseudonym', methods=['POST'])
@authMiddleware
def verify_pseudonym():
    time_slot = read_time_slot()
    user_data = users_collection.find_one({"username": request.username})

    if not user_data or not user_data.get("signed_pseudonym"):
        return jsonify({"success": False, "error": "Pseudonym not found"}), 200

    user = User(request.username, pca)
    user.signed_pseudonym = int(user_data["signed_pseudonym"])
    user.pseudonyms[time_slot] = int(user_data["pseudonym"])

    is_valid = user.send_for_verification(time_slot)
    if is_valid:
        return jsonify({"success": True, "message": "The pseudonym is valid."}), 200
    else:
        return jsonify({"success": False, "error": "The pseudonym is invalid."}), 200


@app.route('/api/anonymity_step', methods=['POST'])
@authMiddleware
def anonymity_step():

    data = request.json
    username = data.get('username')
    serial_no = data.get('serial_no')
    rep_dec_entry = db.rep_dec.find_one({
        "serial_no": serial_no,
    })

    if not rep_dec_entry:
        print('here')
        return jsonify({"success": False, "message": "Rep_dec entry not found"}), 200

    trv_serial_no = random.randint(100000, 999999)

    user_b_data = users_collection.find_one({"username": username})
    user_b = User(username, pca)
    user_b.private_key = RSA.import_key(user_b_data.get('private_key'))
    user_b.public_key = RSA.import_key(user_b_data.get('public_key'))

    blinded_trv_serial_no = user_b.blind_TRV(trv_serial_no)

    blinded_trv_sign = pca.sign_blinded_trv(blinded_trv_serial_no)

    trv_signature = user_b.unblind_trv_sign(blinded_trv_sign)

    trv = {
        "trv_serial_no": str(trv_serial_no),
        "rep_dec_serial_no": str(serial_no),
        "signature": str(trv_signature)
    }
    print(trv_serial_no)
    print(trv_signature)
    print(pca.verify_trv(trv_serial_no, trv_signature))
    user_b_data.setdefault("trv", []).append(trv)

    updated_rep_dec = [entry for entry in user_b_data.get(
        "rep_dec", []) if entry.get('serial_no') != serial_no]
    print(updated_rep_dec)
    print(serial_no)
    user_b_data["rep_dec"] = updated_rep_dec
    users_collection.replace_one({"_id": user_b_data["_id"]}, user_b_data)

    return jsonify({"success": True, "message": "TRV issued"}), 200

    # call pca.signtrv(rep_dec , blinded TRV)
    # store with the rep_dec object that TRV is created so that only endorese step can be done for this now
    # also create another TRV object (append in another array of objects in teh users table)


@app.route('/api/endorsement_step', methods=['POST'])
@authMiddleware
def endorsement_step():

    data = request.json
    username = data.get('username')
    trv_serial_no = data.get('trv_serial_no')
    user_b_data = users_collection.find_one({"username": username})

    trv = [entry for entry in user_b_data.get(
        "trv", []) if entry.get('trv_serial_no') == trv_serial_no][0]

    rep_dec_serial_no = trv.get('rep_dec_serial_no')
    trv_signature = trv.get('signature')
    
    reputation_info = 'PCA'.encode('utf-8')
    # verify the signature of trv ,
    print(trv_serial_no ) 
    print(trv_signature)
    if not pca.verify_trv(int(trv_serial_no), int(trv_signature)):
        print('here')

        return jsonify({"success": False, "message": "TRV signature not verified!!"}), 200
    new_rep_dec_serial_no = random.randint(100000, 999999)
    rep_dec_entry = {
            "serial_no": new_rep_dec_serial_no,
            "Cipia": {
                "pseudonym": str("PCA"),
                "public_key": str(pca.key.publickey().export_key().decode()),
                "time_slot": str(read_time_slot())
            },
            "Cipib": {
                "pseudonym": str(user_b_data.get('pseudonym')),
                "public_key": str(user_b_data.get('public_key')),
                "time_slot": user_b_data.get("time_slot")
            },
            "signed_reputation": pca.sign_reputation_info(reputation_info).hex(),
            "timestamp": datetime.utcnow()
        }

        # Insert the reputation declaration into the rep_dec collection



        # Append the reputation declaration to the user's rep_dec array
    users_collection.update_one(
        {"username": user_b_data.get('username')},
        {"$push": {"rep_dec": rep_dec_entry}}
    )
    
    

    
    # Remove the used TRV entry from the user's trv array
    updated_trv_list = [entry for entry in user_b_data.get("trv", []) if entry.get('trv_serial_no') != trv_serial_no]
    users_collection.update_one(
        {"username": username},
        {"$set": {"trv": updated_trv_list}}
    )
    
    
    return jsonify({"success": True, "message": "Rep Dec saved!!"}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
#
