from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)

@app.route("/shows", methods=['POST'])
def create_show():
    data = request.form
    if (data['name'] is None) or (data['episodes_seen'] is None):
        return create_response(status=422, message="name and/or episodes_seen are missing.")
    show = db.create('shows', data)
    return create_response({'shows': show}, status = 201)

@app.route("/shows/minEpisodes/<episodes>", methods=['GET'])
def get_min_episodes(episodes):
    episodes_seen = db.getByEpisodes('shows', int(episodes))
    if episodes_seen is None:
        return create_response(status=404, message="No show with this number of episodes exists")
    return create_response({'shows': episodes_seen})

@app.route("/shows", methods=['GET'])
def get_all_shows():
    return create_response({"shows": db.get('shows')})

@app.route("/shows/<id>", methods=['DELETE'])
def delete_show(id):
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    db.deleteById('shows', int(id))
    return create_response(message="Show deleted")
    
@app.route("/shows/<id>", methods=['GET'])
def get_show(id):
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    return create_response({'show': db.getById('shows', int(id)) })

@app.route('/shows/')
def get_episodes():
    episodes = (request.args.get('minEpisodes',''))
    episodes_seen = db.getByEpisodes('shows', int(episodes))
    if episodes_seen is None:
        return create_response(status=404, message="No show with this number of episodes exists")
    return create_response({'shows': episodes_seen})

@app.route("/shows/<id>", methods=['PUT'])
def get_show_update(id):
    if db.getById('shows', int(id)) is None:
        print("update: NOPE\n")
        return create_response(status=404, message="No show with this id exists")

    data = request.get_json()
    if data is  None:
        print("update: no data")
        return create_response(status=404, message="No data")

    name = request.args.get('name')
    episodes_seen = request.args.get('episodes_seen')
    payload = {}
    if name is None:
        payload = {'episodes_seen': episodes_seen}
    else:
        payload = {'name': name}

    new_data = db.updateById('shows', int(id), data)
    
    return create_response({'shows': db.getById(int(id))})

"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(port=8080, debug=True)
