import discord
from discord.ext import commands, tasks
import asyncio
import yfinance as yf

BOT_TOKEN = "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

alerts = {}

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
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
        if ctx.channel.id not in alerts:
            alerts[ctx.channel.id] = []
        alerts[ctx.channel.id].append({"ticker": ticker.upper(), "price": price})
        await ctx.send(f"Alert added: {ticker.upper()} at ${price:.2f}")
    except Exception as e:
        await ctx.send(f"Add_alert error: {e}")

@bot.command(name="list_alerts")
async def list_alerts(ctx):
    try:
        channel_alerts = alerts.get(ctx.channel.id, [])
        if not channel_alerts:
            await ctx.send("No alerts set for this channel.")
        else:
            alert_list = "\n".join([f"{a['ticker']} at ${a['price']:.2f}" for a in channel_alerts])
            await ctx.send(f"Current alerts:\n{alert_list}")
    except Exception as e:
        await ctx.send(f"List_alerts error: {e}")

@bot.command(name="remove_alert")
async def remove_alert(ctx, ticker: str, price: float):
    try:
        channel_alerts = alerts.get(ctx.channel.id, [])
        for alert in channel_alerts:
            if alert["ticker"] == ticker.upper() and alert["price"] == price:
                channel_alerts.remove(alert)
                await ctx.send(f"Alert removed: {ticker.upper()} at ${price:.2f}")
                return
        await ctx.send(f"No alert found for {ticker.upper()} at ${price:.2f}")
    except Exception as e:
        await ctx.send(f"Remove_alert error: {e}")

@tasks.loop(seconds=5)
async def check_stock_prices():
    try:
        for channel_id, channel_alerts in alerts.items():
            for alert in channel_alerts:
                ticker = alert["ticker"]
                target_price = alert["price"]
                stock = yf.Ticker(ticker)
                current_price = stock.info.get("regularMarketPrice", None)

                if current_price is None:
                    print(f"Failed to fetch price for {ticker}.")
                    continue

                if current_price == target_price:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send(f"🚨 Alert: {ticker} has reached ${current_price:.2f} (target: ${target_price:.2f})")
                    channel_alerts.remove(alert)  
    except Exception as e:
        print(f"Error in check_stock_prices task: {e}")


bot.run(BOT_TOKEN)
