import os
import threading
import requests


class TursoDB:
    def __init__(self):
        self._lock = threading.Lock()

    def _get_creds(self):
        url = os.environ["TURSO_DATABASE_URL"].replace("libsql://", "https://")
        token = os.environ["TURSO_AUTH_TOKEN"]
        return url, token

    def _parse_value(self, v):
        if v["type"] == "null":
            return None
        if v["type"] == "integer":
            return int(v["value"])
        if v["type"] == "float":
            return float(v["value"])
        return v["value"]

    def execute(self, sql, *args):
        sql = sql.replace('"', "'")
        url, token = self._get_creds()

        response = requests.post(
            f"{url}/v2/pipeline",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {
                            "sql": sql,
                            "args": [
                                {"type": "null"} if a is None
                                else {"type": "integer", "value": str(a)} if isinstance(a, int)
                                else {"type": "float", "value": str(a)} if isinstance(a, float)
                                else {"type": "text", "value": str(a)}
                                for a in args
                            ],
                        },
                    }
                ]
            },
        )
        response.raise_for_status()
        data = response.json()

        result = data["results"][0]
        if result["type"] == "error":
            raise Exception(result["error"]["message"])

        rows_data = result["response"]["result"]
        sql_upper = sql.strip().upper()

        if sql_upper.startswith("SELECT"):
            cols = [c["name"] for c in rows_data["cols"]]
            return [
                dict(zip(cols, [self._parse_value(v) for v in row]))
                for row in rows_data["rows"]
            ]

        if sql_upper in ("BEGIN", "COMMIT", "ROLLBACK"):
            return None

        last_id = rows_data.get("last_insert_rowid")
        return int(last_id) if last_id else None