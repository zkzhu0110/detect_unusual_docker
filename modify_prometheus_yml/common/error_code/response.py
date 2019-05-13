from flask import jsonify
def make_success_response(data):
    response = {"message": {"status": 200, "code": 0, "message": 'success'}}
    response['data'] = data
    return jsonify(response)

def make_no_data_response(status, code, message):
    response = {"message": {"status": status, "code":code, "message": message}}

    return jsonify(response)

def make_error_response(status, code, message):
    response = {"message": {"status": status, "code":code, "message": str(message)}}

    return jsonify(response)
