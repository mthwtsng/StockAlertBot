import discord
from discord.ext import commands, tasks
import asyncio
import yfinance as yf
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd



mongo_client = MongoClient(uri)
db = mongo_client["StockAlertBot"]
alerts_collection = db["alerts"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_stock_prices.start()

@bot.command(name="ping")
async def ping(ctx):
    try:
        await ctx.send("Pong!")
    except Exception as e:
        await ctx.send(f"Error in ping command: {e}")

@bot.command(name="add_alert")
async def add_alert(ctx, ticker: str, price: float):
    try:
        alert = {
            "server_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "ticker": ticker.upper(),
            "price": price,
        }
        alerts_collection.insert_one(alert)
        await ctx.send(f"Alert added: {ticker.upper()} at ${price:.2f}")
    except Exception as e:
        await ctx.send(f"Add_alert error: {e}")

@bot.command(name="list_alerts")
async def list_alerts(ctx):
    try:
        channel_alerts = list(alerts_collection.find({"server_id": ctx.guild.id, "channel_id": ctx.channel.id}))
        if not channel_alerts:
            await ctx.send("No alerts set for this channel.")
            return

        page = 0
        items_per_page = 5
        total_pages = (len(channel_alerts) - 1) // items_per_page + 1

        def create_embed():
            start = page * items_per_page
            end = start + items_per_page
            current_alerts = channel_alerts[start:end]
            description = "\n".join([f"**{a['ticker']}** at ${a['price']:.2f}" for a in current_alerts])
            embed = discord.Embed(title="Stock Alerts", description=description, color=discord.Color.blue())
            embed.set_footer(text=f"Page {page + 1}/{total_pages}")
            return embed

        message = await ctx.send(embed=create_embed())

        if total_pages > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

        def check_reaction(reaction, user):
            return (
                user == ctx.author
                and reaction.message.id == message.id
                and str(reaction.emoji) in ["⬅️", "➡️"]
            )

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
                if str(reaction.emoji) == "⬅️" and page > 0:
                    page -= 1
                elif str(reaction.emoji) == "➡️" and page < total_pages - 1:
                    page += 1
                else:
                    await message.remove_reaction(reaction.emoji, user)
                    continue

                await message.edit(embed=create_embed())
                await message.remove_reaction(reaction.emoji, user)
            except asyncio.TimeoutError:
                break

        if total_pages > 1:
            await message.clear_reactions()

    except Exception as e:
        await ctx.send(f"List_alerts error: {e}")

@bot.command(name="remove_alert")
async def remove_alert(ctx, ticker: str, price: float):
    try:
        result = alerts_collection.delete_one({
            "server_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "ticker": ticker.upper(),
            "price": price,
        })
        if result.deleted_count > 0:
            await ctx.send(f"Alert removed: {ticker.upper()} at ${price:.2f}")
        else:
            await ctx.send(f"No alert found for {ticker.upper()} at ${price:.2f}")
    except Exception as e:
        await ctx.send(f"Remove_alert error: {e}")

@tasks.loop(seconds=5)
async def check_stock_prices():
    try:
        alerts = list(alerts_collection.find())
        if not alerts:
            print("No alerts found.")
            return

        alerts_df = pd.DataFrame(alerts)
        print(f"Fetched {len(alerts)} alerts from the database.")

        tickers = alerts_df["ticker"].unique()
        stock_data = {ticker: yf.Ticker(ticker).info.get("regularMarketPrice", None) for ticker in tickers}

        alerts_df["current_price"] = alerts_df["ticker"].map(stock_data)

        alerts_df = alerts_df.dropna(subset=["current_price"])

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
            alerts_collection.delete_one({"_id": alert["_id"]})
    except Exception as e:
        print(f"Error in check_stock_prices task: {e}")

bot.run(BOT_TOKEN)
