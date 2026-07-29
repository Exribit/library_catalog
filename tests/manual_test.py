import asyncio

from src.library_catalog.external.openlibrary.client import OpenLibraryClient


async def main():
    client = OpenLibraryClient()

    data = await client.search_by_isbn("9780132350884")
    print(data)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())