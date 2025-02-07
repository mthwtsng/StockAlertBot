# commands/alerts.py

from discord.ext import commands
from utils import db 

class AlertsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="add_alert")
    async def add_alert(self, ctx, ticker: str, price: float):
        alert = {
            "server_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "ticker": ticker.upper(),
            "price": price,
        }
        db.insert_alert(alert)
        await ctx.send(f"Alert added: {ticker.upper()} at ${price:.2f}")

    @commands.command(name="list_alerts")
    async def list_alerts(self, ctx):
        channel_alerts = db.get_alerts({"server_id": ctx.guild.id, "channel_id": ctx.channel.id})
        if not channel_alerts:
            await ctx.send("No alerts set for this channel.")
            return
        alerts_message = "\n".join([f"{a['ticker']} at ${a['price']:.2f}" for a in channel_alerts])
        await ctx.send(f"**Alerts:**\n{alerts_message}")

    @commands.command(name="delete_alert")
    async def delete_alert(self, ctx, ticker: str, price: float):
        result = db.delete_alert({
            "server_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "ticker": ticker.upper(),
            "price": price,
        })
        if result.deleted_count > 0:
            await ctx.send(f"Alert removed: {ticker.upper()} at ${price:.2f}")
        else:
            await ctx.send(f"No alert found for {ticker.upper()} at ${price:.2f}")

    @commands.command(name="delete_all")
    @commands.has_permissions(administrator=True)
    async def delete_all_alerts(self, ctx, scope: str = "channel"):

        if scope.lower() == "server":
            result = db.delete_alerts({"server_id": ctx.guild.id})
            await ctx.send(f"Deleted {result.deleted_count} alerts for the entire server.")
        else:
            result = db.delete_alerts({
                "server_id": ctx.guild.id,
                "channel_id": ctx.channel.id
            })
            await ctx.send(f"Deleted {result.deleted_count} alerts for this channel.")
    

async def setup(bot: commands.Bot):
    await bot.add_cog(AlertsCog(bot))
