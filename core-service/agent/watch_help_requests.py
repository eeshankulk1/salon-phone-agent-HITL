# agent/help_watcher.py
import asyncio, json, logging, os, asyncpg
logger = logging.getLogger("agent.helpwatch")
CHANNEL = "help_request_updates"

class HelpWatcher:
    def __init__(self):
        self._conn = None
        self._pending = {}
        self._lock = asyncio.Lock()

    async def start(self):
        if self._conn: return
        self._conn = await asyncpg.connect(os.environ["DATABASE_URL"])
        await self._conn.add_listener(CHANNEL, self._on_notify)
        await self._conn.execute(f"LISTEN {CHANNEL};")
        logger.info({"event":"help_listen_started", "channel": CHANNEL})

    async def stop(self):
        if not self._conn: return
        try:
            await self._conn.remove_listener(CHANNEL, self._on_notify)
            await self._conn.execute(f"UNLISTEN {CHANNEL};")
        finally:
            await self._conn.close()
            self._conn = None

    def _on_notify(self, _conn, _pid, _channel, payload: str):
        try:
            data = json.loads(payload)
            rid = str(data.get("id"))
        except Exception as e:
            logger.warning({"event":"help_bad_payload", "payload": payload, "error": str(e)})
            return
        fut = self._pending.pop(rid, None)
        if fut and not fut.done():
            fut.set_result((data.get("answer_text") or "(no answer_text)", data))

    async def wait(self, request_id: str, timeout: float | None = None):
        await self.start()
        async with self._lock:
            fut = self._pending.get(request_id)
            if not fut:
                fut = asyncio.get_running_loop().create_future()
                self._pending[request_id] = fut
        return await asyncio.wait_for(fut, timeout) if timeout else await fut

# usage helper
async def wait_and_callback(watcher: HelpWatcher, request_id: str, on_answer):
    answer, payload = await watcher.wait(request_id)
    await on_answer(answer, payload)