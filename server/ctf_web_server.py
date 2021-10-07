import os
import json
import sys

from .db_access import DBAccess
from .validate_user import validate_user, _get_user_secret
from flask import Flask, abort, render_template, request, redirect, jsonify
import logging

DB_FILE = 'server/ctf_db.db'
URL_STRUCTURE = "/{user_type}/{token}/{path}"

db = DBAccess(DB_FILE)
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            static_url_path='/static/',
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'))


###################################################################################################
# Main login page and actions (including password reset):
###################################################################################################
@app.route("/", methods=['GET'])
def login_page():
    """
    The main login page:
    :return:
    """
    return render_template("login.html")


@app.route('/login', methods=['GET'])
def login():
    """
    Check the login attempt
    :return:
    """
    username = request.args.get('username')
    password = request.args.get('passwd')
    user = db.get_user_by_name(username)
    if user and (user['password'] == password):
        # Login success! Redirect to the path with the token:
        secret = _get_user_secret(user)
        token = f"{user['id']}/{secret}"
        if user['is_admin']:
            user_type = 'admin'
            path = 'users'
        else:
            user_type = 'user'
            path = "products"
        redir_url = URL_STRUCTURE.format(user_type=user_type,
                                         token=token,
                                         path=path)
        return redirect(redir_url, code=302)
    else:
        # Failed login!
        abort(401)

@app.route('/forgot_password', methods=['GET'])
def forgot_password():
    """
    Forgot password page
    :return:
    """
    return render_template('forgot_passwd.html')

@app.route('/recovery_qs', methods=["POST"])
def recovery_questions():
    """
    Answers to recovery questions - check their validity
    :return:
    """
    user = db.get_user_by_name(request.form.get('name'))
    if user:
        # Check the answers:
        if (user['first_car'] == request.form.get('first_car')) & (
                user['birth_place'] == request.form.get('birth_place')):
            # Matched! Return the reset password URL:
            secret = _get_user_secret(user)
            token = f"{user['id']}/{secret}"
            reset_pass_loc = URL_STRUCTURE.format(user_type='user',
                                                  token=token,
                                                  path='reset_passwd')
            return redirect(reset_pass_loc)
    # Mismatch / user not found
    abort(403)

@app.route('/forgot_password', methods=['GET'])
def forgot_passwd(user_id, token):
    """
    Return the reset password form
    :param user_id:
    :param token:
    :return:
    """
    return render_template("forgot_passwd.html", base_path=f'/user/{user_id}/{token}')

@app.route('/user/<user_id>/<token>/submit_new_passwd', methods=['POST'])
def submit_new_passwd(user_id, token):
    """
    Reset password to a new value
    :param user_id:
    :param token:
    :return:
    """
    user = db.get_user_by_id(user_id)
    passwd = request.form.get('passwd')
    db.set_user_password(user['id'], passwd)
    return b"/"


###################################################################################################
# User product page and actions:
###################################################################################################
@app.route('/user/<user_id>/<token>/products', methods=['GET'])
def products_page(user_id, token):
    """
    Return the products page. Validate the user, then render the page from the template
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])

    # User is valid. Render the template:
    return render_template('products.html', base_path=f'/user/{user_id}/{token}')

@app.route('/user/<user_id>/<token>/search', methods=['POST'])
def search_product(user_id, token):
    """
    Search the product DB for a product by name
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])

    # User is valid. Run the search:
    search_str = request.form.get('q')
    products = db.get_products(search_str)
    # Respond with the JSON result:
    return jsonify({'prods': products})

@app.route('/user/<user_id>/<token>/checkout', methods=['POST'])
def checkout(user_id, token):
    """
    Checkout the shopping cart
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])

    # User is valid. Run the checkout:
    user_id = validation_res['user']['id']
    data = request.form.to_dict()
    selected_prod_ids = request.form.getlist('selected[]')
    print("Got selected_prod_ids:", selected_prod_ids)
    for prod_id in selected_prod_ids:
        db.add_purchase(prod_id, user_id)
    return "Success!"

@app.route('/user/<user_id>/<token>/thank_you', methods=['GET'])
def thankyou(user_id, token):
    return render_template("thank_you.html", base_path=f'/user/{user_id}/{token}')

###################################################################################################
# Admin endpoints
###################################################################################################
@app.route('/admin/<user_id>/<token>/users', methods=['GET'])
def view_users(user_id, token):
    """
    Main Admin view for users and actions
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token, admin_requested=True)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])

    return render_template("user_profiles.html", base_path=f'/admin/{user_id}/{token}')

@app.route('/admin/<user_id>/<token>/view', methods=['POST'])
def view_file(user_id, token):
    """
    View a file with a given path anywhere on our disk (admin only!)
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token, admin_requested=True)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])

    # Valid admin user. Load the file and return it:
    file_path = request.form.get('src')
    try:
        logging.info(f"Reading file from {file_path}...")
        with open(file_path, 'r') as fp:
            res = fp.read().encode('utf8')
        return res
    except Exception as e:
        # Failed - the path is not there
        print(e)
        abort(404)

@app.route('/admin/<user_id>/<token>/upload_file', methods=['POST'])
def upload_file(user_id, token):
    """
    Upload a file to the file system
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token, admin_requested=True)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])

    # Upload the file:
    print("Got upload request. Form is:")
    print(request.form)
    file_path = request.form.get('file_name')
    try:
        # Try to get the data from the form directly:
        file_content = request.form.get('payload')
    except:
        file_content = None
        pass

    if file_content is None:
        # Get the data from the file upload parts:
        print("Trying to get file...")
        file_content = request.files.get('payload').read()

    if isinstance(file_content, str):
        mode = "w"
    else:
        mode = "wb"
    with open(file_path, mode) as fp:
        fp.write(file_content)
    return b"success"

@app.route('/admin/<user_id>/<token>/restart', methods=['POST'])
def restart_server(user_id, token):
    """
    Restart the server process
    :param user_id:
    :param token:
    :return:
    """
    validation_res = validate_user(db, user_id, token, admin_requested=True)
    if not validation_res['valid']:
        # Return the error status code:
        abort(validation_res['status'])
    os.execl(sys.executable, 'python', sys.argv[0], *sys.argv[1:])
