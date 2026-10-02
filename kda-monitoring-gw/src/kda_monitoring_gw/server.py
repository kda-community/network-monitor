from aiohttp import ClientSession, TCPConnector, web
import asyncio
from decimal import Decimal
from .client import get_current_blocks_time
from .eth_client import get_eth_balance_gwei, get_erc20_balance, mailbox_get_latest_dispath_id, mailbox_delivered, get_erc20_total_supply, get_tree_hook_count
from datetime import datetime, timezone
from pypact.chainweb import Chainweb
from pypact.kadena_exceptions import KadenaChainError
from string import Template

def diff_time(x):
    now = datetime.now(timezone.utc)
    return (now-x).seconds

def current_time():
  dt = datetime.now(timezone.utc)
  return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

async def client_session_ctx(app):
  async with ClientSession(connector=TCPConnector(ssl=False)) as session:
    async with Chainweb(server="https://api.chainweb-community.org") as chainweb:
      app["chainweb"] = chainweb
      app["http"] = session
      yield

async def handle_root(request):
  return web.Response(text="OK")

async def handle_pact(request):
  data = await request.json()
  print(data["cmd"])
  cmd = Template(data["cmd"]).substitute(current_time=current_time())
  print(cmd)
  async def __do_request(chain):
    try:
      data = await request.app["chainweb"].chains[chain].local_result(cmd, gasLimit=125000)
      if isinstance(data, Decimal):
        return float(data)
      if isinstance(data,dict) and 'decimal' in data:
        return float(data["decimal"])
      else:
        return data

    except KadenaChainError as e:
      print(str(e))
      return None

  result = await asyncio.gather(*map(__do_request, data["chains"]))
  print(result)
  return web.json_response({"results":result})

async def handle_age(request):
  data = await request.post()
  times = await get_current_blocks_time(request.app["http"], data["node"])
  diffs = [diff_time(x) for x in times]
  return web.json_response({"age":diffs})

async def handle_max_age(request):
  data = await request.post()
  times = await get_current_blocks_time(request.app["http"], data["node"])
  diff_max = max(map(diff_time,times))
  return web.json_response({"max_age":diff_max})

async def handle_eth_balance_gwei(request):
  data = await request.post()
  print(list(data.keys()))
  bal = await get_eth_balance_gwei(data["address"])
  return web.json_response({"balance":int(bal)})

async def handle_erc_20_balance(request):
  data = await request.post()
  print(list(data.keys()))
  bal = await get_erc20_balance(data["token"], data["address"])
  return web.json_response({"balance":int(bal)})

async def handle_erc_20_total_supply(request):
  data = await request.post()
  supply = await get_erc20_total_supply(data["token"])
  return web.json_response({"balance":int(supply)})

async def handle_latest_dispatch_id(request):
  data = await request.post()
  print(list(data.keys()))
  _id = await mailbox_get_latest_dispath_id(data["address"])
  return web.json_response({"id":_id})

async def handle_tree_hook_count(request):
  data = await request.post()
  print(list(data.keys()))
  cnt = await get_tree_hook_count(data["address"])
  return web.json_response({"count":cnt})

async def handle_mailbox_delivered(request):
  data = await request.post()
  print(list(data.keys()))
  result = await mailbox_delivered(data["address"], data["id"])
  return web.json_response({"delivered":result})

def start_app():
  app = web.Application()
  app.cleanup_ctx.append(client_session_ctx)
  app.add_routes([web.get('/', handle_root)])
  app.add_routes([web.post('/pact', handle_pact)])
  app.add_routes([web.post('/age', handle_age)])
  app.add_routes([web.post('/max_age', handle_max_age)])
  app.add_routes([web.post('/eth_balance_gwei', handle_eth_balance_gwei)])
  app.add_routes([web.post('/erc_20_balance', handle_erc_20_balance)])
  app.add_routes([web.post('/erc_20_total_supply', handle_erc_20_total_supply)])
  app.add_routes([web.post('/latest_dispatch_id', handle_latest_dispatch_id)])
  app.add_routes([web.post('/mailbox_delivered', handle_mailbox_delivered)])
  app.add_routes([web.post('/tree_hook_count', handle_tree_hook_count)])
  web.run_app(app, port=8090)
