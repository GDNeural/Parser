import asyncio
import aiohttp
import pandas as pd


async def get_eth_price():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    parameters = {
        "id": "1027",
    }
    headers = {
        'Accepts': 'application/json',
        'Accept-Encoding': 'deflate,gzip',
        'X-CMC_PRO_API_KEY': '9cbbe935-c869-4d8b-9afc-4d14888d0842',
    }
    data_frame = pd.DataFrame()
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers, params=parameters) as resp:
                data = await resp.json()

                temp_data_frame = pd.json_normalize(data['data']['1027'])
                temp_data_frame['last_updated'] = pd.to_datetime(temp_data_frame['last_updated'])
                temp_data_frame.set_index('last_updated', inplace=True)
                data_frame = pd.concat([data_frame, temp_data_frame])

                percent_change_1h = data['data']['1027']['quote']['USD']['percent_change_1h']
                if (percent_change_1h >= 0.01) or (percent_change_1h <= -0.01):
                    print(f"Basic rate is over 10% per hour and now equals to {percent_change_1h}")
                # Basic plan on CoinMarketCap is 30 requests per 1 minute. So I just cut it speed with sleep.
                data_frame.to_csv('ethereum.csv')
                await asyncio.sleep(2)


loop = asyncio.get_event_loop()
loop.run_until_complete(get_eth_price())