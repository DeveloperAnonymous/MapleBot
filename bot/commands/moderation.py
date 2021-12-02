from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nospoil(self, ctx: commands.Context):
        spoiler = ctx.message.reference
        spoiler_id = spoiler.message_id
        spoiler_message = await ctx.channel.fetch_message(spoiler_id)
        spoiler_author = spoiler_message.author
        await spoiler_message.delete()
        await ctx.send(f"Please, {spoiler_author.mention}, don't spoil the others!")
