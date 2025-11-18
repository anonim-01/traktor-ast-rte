import asyncio
import ngrok

async def main():
    session = await ngrok.SessionBuilder().authtoken('34YFt95ZdebUT1z2IhJSkQwUWwE_kQY6XFjPHPvb5KybPyCj').connect()
    print('Session connected')

    # Create tunnel without custom domain (free plan)
    tunnel = await session.http_endpoint().listen()
    print(f"Tunnel established: {tunnel.url()}")

    # Keep running
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
