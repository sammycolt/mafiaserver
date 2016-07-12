from flask import jsonify


def SUCCESS():
    return jsonify({"result" : "success"})


def ERROR():
    return jsonify({"result" : "error"})