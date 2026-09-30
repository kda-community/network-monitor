from .server import start_app

#async def amain():
#    async with aiohttp.ClientSession() as session:
#        cut = await get_hashes(session, "https://pl-1.chainweb-community.org")
#        cut = await get_current_blocks_time(session, "https://pl-1.chainweb-community.org")
#        print([diff_time(x) for x in cut])

def main() -> None:
    start_app()