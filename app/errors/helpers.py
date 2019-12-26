from flask import request


def wants_json_response():
	return request.accept_mimetypes['application/json'] >= \
		request.accept_mimetypes['text/html']