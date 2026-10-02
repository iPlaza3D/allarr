from __future__ import annotations

import httpx


class DownloadStation:
    """Cliente de la Web API de Synology Download Station (DSM 6/7, XPEnology)."""

    def __init__(self, url: str, user: str, password: str, destination: str = ""):
        if not url:
            raise ValueError("Falta la URL de DSM")
        self.base = url.rstrip("/") + "/webapi"
        self.user, self.password, self.dest = user, password, destination
        self.sid: str | None = None
        self.http = httpx.Client(timeout=30, verify=False)  # DSM suele usar certificado autofirmado

    def _check(self, r: httpx.Response) -> dict:
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            raise RuntimeError(f"DSM error {data.get('error', {}).get('code')}")
        return data.get("data") or {}

    def _call(self, path: str, **params) -> dict:
        if self.sid:
            params["_sid"] = self.sid
        return self._check(self.http.get(f"{self.base}/{path}", params=params))

    def __enter__(self):
        data = self._call(
            "auth.cgi", api="SYNO.API.Auth", version=3, method="login",
            account=self.user, passwd=self.password, session="DownloadStation", format="sid",
        )
        self.sid = data["sid"]
        return self

    def __exit__(self, *exc):
        try:
            if self.sid:
                self._call("auth.cgi", api="SYNO.API.Auth", version=1, method="logout", session="DownloadStation")
        finally:
            self.http.close()

    def _task(self, method: str, **params) -> dict:
        return self._call("DownloadStation/task.cgi", api="SYNO.DownloadStation.Task", version=1, method=method, **params)

    def list_tasks(self) -> list[dict]:
        out = []
        for t in self._task("list", additional="transfer").get("tasks", []):
            size = t.get("size") or 0
            tr = (t.get("additional") or {}).get("transfer") or {}
            out.append({
                "id": t["id"], "title": t["title"], "status": t["status"], "size": size,
                "progress": round(tr.get("size_downloaded", 0) / size * 100, 1) if size else 0,
                "speed": tr.get("speed_download", 0),
            })
        return out

    def add_uri(self, uri: str) -> None:
        params = {"uri": uri}
        if self.dest:
            params["destination"] = self.dest
        self._task("create", **params)

    def add_torrent_file(self, filename: str, content: bytes) -> None:
        """Sube el .torrent (descargado vía VPN) para que DS no tenga que acceder al sitio bloqueado."""
        form = {"api": "SYNO.DownloadStation.Task", "version": "1", "method": "create"}
        if self.dest:
            form["destination"] = self.dest
        r = self.http.post(
            f"{self.base}/DownloadStation/task.cgi", params={"_sid": self.sid}, data=form,
            files={"file": (filename, content, "application/x-bittorrent")},
        )
        self._check(r)

    def pause(self, task_id: str) -> None:
        self._task("pause", id=task_id)

    def resume(self, task_id: str) -> None:
        self._task("resume", id=task_id)

    def delete(self, task_id: str) -> None:
        self._task("delete", id=task_id, force_complete="false")
