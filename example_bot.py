import discord

DiscordClientToken = 'TOKEN'

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # print('Erster Server: {0}'.format(client.guilds[0].name))
    # print('Sein Systemkanal: {0}'.format(client.guilds[0].system_channel.name))


# @client.event
# async def on_member_join(member):
#     print('Nutzer {0} kam dazu.'.format(member.nick))
#     client.guilds[0].system_channel.send("Herzlich Willkommen von Saschas Billow-Bot, {0}!".format(member.nick))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #print('Die Channel-ID war übrigens {0.channel.id}.'.format(message))

    if message.channel.type == discord.ChannelType.private:
        print('private Nachricht')
        await message.channel.send('danke für deine Privatnachricht. leider weiß ich damit noch nichts anzufangen')
        return

    if message.channel.name != 'werbinich':
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')
        await message.author.send('hallo auch privat')
    # else:
    #     print('Message from {0.author}: {0.content}'.format(message))


client.run(DiscordClientToken)
