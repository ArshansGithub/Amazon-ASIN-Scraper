import noble_tls, asyncio, json
from noble_tls import Client

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=4',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

async def make_request(client, url, headers, retries = 5):
    if retries == 0: return None
    try:
        response = await client.get(url, headers=headers)
    except:
        await asyncio.sleep(1)
        return await make_request(client, url, headers, retries - 1)
    
    return response

async def main(session, keyword):
    keyword = keyword.replace(" ", "+")
    home_url = "https://www.amazon.com"
    home = await make_request(session, home_url, headers)
    print(f"Home - Status Code: {home.status_code}")

    pages = 20
    asins = []
    tasks = []

    for page in range(pages):
        
        url = f"https://www.amazon.com/s?k={keyword}&page={page + 1}"

        tasks.append(make_request(session, url, headers))


    responses = await asyncio.gather(*tasks)

    for response in responses:
        if response.status_code == 200:
            print(f"Page {page + 1}")
            lines = response.text.split("\n")
            for line in lines:
                if "<div data-asin" in line:
                    asin = line.split("data-asin=\"")[1].split("\"")[0]
                    if asin not in asins and asin != "":
                        print(f"Found ASIN: {asin}")
                        asins.append(asin)
        else:
            print(f"Page {page + 1} - Status Code: {response.status_code}")
            print(response.text)

        print(f"Page {page + 1} done")

    keyword = keyword.replace("+", "_")
    # Save the results
    with open(f"asins_{keyword}.json", "w") as file:
        json.dump(asins, file)
    


                


    


if __name__ == '__main__':
    proxies = ["proxy"]
    
    keyword = "apple iphone"

    session = noble_tls.Session(
        client=Client.FIREFOX_120,
        random_tls_extension_order=True
    )

    asyncio.run(main(session, keyword))