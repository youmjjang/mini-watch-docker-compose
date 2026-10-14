def make_event(data):
    if not isinstance(data, dict):
        return None
    method, path, status = data.get("method"), data.get("path"), data.get("status_code")
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"} or not isinstance(method, str):
        return None
    if not isinstance(path, str) or not path.startswith("/") or len(path) > 500:
        return None
    if type(status) is not int or not 100 <= status <= 599:
        return None
    if method == "GET" and path == "/" and status == 200:
        kind = "post_list"
    elif status == 404:
        kind = "request_error"
    elif method == "POST" and path in {"/auth/login", "/api/auth/login"} and status in (200, 401):
        kind = "login_success" if status == 200 else "login_failure"
    else:
        kind = "http_request"
    return {"method": method, "path": path, "status_code": status, "event_type": kind}
