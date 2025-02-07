import asyncio
import pandas as pd
from discord.ext import tasks
from utils import db, cache
import logging

logger = logging.getLogger(__name__)
price_cache = cache.PriceCache()  

def setup_stock_checker(bot):
    @tasks.loop(seconds=5)
    async def check_stock_prices():
        try:
            alerts = db.get_alerts({})  
            if not alerts:
                logger.info("No alerts found.")
                return

            alerts_df = pd.DataFrame(alerts)
            tickers = alerts_df["ticker"].unique()

            price_tasks = [price_cache.get_price(ticker) for ticker in tickers]
            prices_list = await asyncio.gather(*price_tasks)
            stock_data = dict(zip(tickers, prices_list))

            alerts_df["current_price"] = alerts_df["ticker"].map(stock_data)
            alerts_df.dropna(subset=["current_price"], inplace=True)

            alerts_df["tolerance"] = alerts_df["price"] * 0.0005
            alerts_df["lower_bound"] = alerts_df["price"] - alerts_df["tolerance"]
            alerts_df["upper_bound"] = alerts_df["price"] + alerts_df["tolerance"]

            matching_alerts = alerts_df[
                (alerts_df["current_price"] >= alerts_df["lower_bound"]) &
                (alerts_df["current_price"] <= alerts_df["upper_bound"])
            ]
            for _, alert in matching_alerts.iterrows():
                channel = bot.get_channel(alert["channel_id"])
                if channel:
                    await channel.send(
                        f"\ud83d\udea8 Alert: {alert['ticker']} is within 0.05% of the target price! "
                        f"Current price: ${alert['current_price']:.2f} (Target: ${alert['price']:.2f})"
                    )
                db.delete_alert({"_id": alert["_id"]})
        except Exception as e:
            logger.error(f"Error in check_stock_prices task: {e}")


    check_stock_prices.start()
