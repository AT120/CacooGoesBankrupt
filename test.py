import cacoo_api
import asyncio
from aiohttp import web



app = web.Application()
cacoo = cacoo_api.Cacoo("NPe56xOBYkzbVNcRf3fZ")
app.cleanup_ctx.append(cacoo.create_session)

web.run_app(app)
asyncio.run(c.get_organization_key())