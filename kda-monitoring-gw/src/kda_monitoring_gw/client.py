import asyncio
import base64
from datetime import datetime, timezone

def decode_unpadded_base64(s: str) -> bytes:
    s += '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)

async def get_cut(session, node):
  async with session.get(node + "/chainweb/0.0/mainnet01/cut") as resp:
    return await resp.json()

async def get_hashes(session, node):
  cut = await get_cut(session, node)
  return [  cut["hashes"][str(x)]['hash'] for x in range(0,20) ]

async def get_header(session, node, chain, _hash):
  async with session.get("{}/chainweb/0.0/mainnet01/chain/{!s}/header/{!s}".format(node, chain, _hash)) as resp:
    return decode_unpadded_base64(await resp.text())

async def get_block_time(session, node, chain, _hash):
  header = await get_header(session, node, chain, _hash)
  micros = int.from_bytes(header[8:16], "little")
  return datetime.fromtimestamp(micros / 1_000_000, tz=timezone.utc)

async def get_current_blocks_time(session, node):
  hashes = await get_hashes(session, node)
  futs = [get_block_time(session, node, c, h) for c,h in zip(range(0,20), hashes)]
  return await asyncio.gather(*futs)