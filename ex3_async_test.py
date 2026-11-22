import asyncio, httpx, time


async def fetch_report(client, url):
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.status_code

    except httpx.HTTPStatusError as exc:
        print(f"Error {exc.response.status_code} while requesting {exc.request.url}")
        return None


# def fetch_report_seq(name: str) -> str:
#   return


async def main():
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
        "https://jsonplaceholder.typicode.com/posts/4",
        "https://jsonplaceholder.typicode.com/posts/5",
    ]

    # async test start
    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [fetch_report(client, url) for url in urls]
        result = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start_time
    print(f"async: {result} made in {elapsed:.2f} seconds")

    second_start_time = time.perf_counter()
    # /async test end

    # synchronous test
    results = []

    with httpx.Client(follow_redirects=True) as client:
        for url in urls:
            response = client.get(url)
            response.raise_for_status()
            results.append({"url": str(response.url), "status": response.status_code})

    elapsed = time.perf_counter() - second_start_time
    print(f"sync: {result} made in {elapsed:.2f} seconds")
    # /synchronous test end


if __name__ == "__main__":
    asyncio.run(main())
