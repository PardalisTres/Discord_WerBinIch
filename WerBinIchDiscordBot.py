import asyncio
import discord
from WerBinIchSpiel import WerBinIchSpiel

client = discord.Client()
wbi_channel = None
werbinichspiel = WerBinIchSpiel()


@client.event
async def on_ready():
    global wbi_channel
    global werbinichspiel

    print('We have logged in as {0.user}'.format(client))

    # TODO: später mal Gedanken machen, wie das bei mehreren Guilds/Servern ist...
    #  Da wäre einige Umbauarbeit zu tun.
    #  Am einfachsten bekäme wohl jeder sein eigenes Spiel, und hier würde beim Aufruf
    #  je nach Server die Weiterleitung ans jeweilige Spiel unterschieden werden.
    for g in client.guilds:
        print ('guild found: {0}'.format(g.name))
        for c in g.text_channels:
            textkanalkategorie = c.category
            print('  channel found: {0} with category {1}'.format(c.name, c.category))
            if c.name == 'werbinich':
                wbi_channel = c
        if not wbi_channel:
            try:
                wbi_channel = await g.create_text_channel('werbinich', category=textkanalkategorie)
            except discord.Forbidden:
                print ('ERR: Erstellen des Kanals fehlgeschlagen wegen mangelnder Rechte.')
        werbinichspiel.channel = wbi_channel

        await werbinichspiel.on_ready()

        # activity = discord.Game('Moderator bei "Wer bin ich"')
        #
        # activity = discord.Streaming(name='YouTube', url='unkown')
        # activity.game = 'Stardew Valley'
        # activity.platform = 'Netflix'
        #
        activity = discord.Activity(name='auf WerBinIch-Anfragen', type=discord.ActivityType.listening)
        await client.change_presence(status=discord.Status.online, activity=activity)


@client.event
async def on_message(message):
    global wbi_channel
    global werbinichspiel

    if message.author == client.user:
        return

    # TODO: Würfeln einbauen

    if not message.content.startswith('/wbi '):
        if message.channel.type == discord.ChannelType.private:
            nachricht = 'Du kannst mir zwar gerne schreiben, aber bis auf wenige Kommandos'
            nachricht += ' werde ich dich nicht verstehen.'
            nachricht += '\nLass dir mehr erzählen, indem du mich mit \'wbi hilfe\' ansprichst.'
            await message.channel.send(nachricht)
        return

    # nur in privaten Nachrichten oder im werbinich-Channel überprüfen
    if (message.channel.type != discord.ChannelType.private) and (message.channel.name != 'werbinich'):
        return

    kommando = message.content.split(' ', 1)[1]

    # Die 'gehweg'-Funktion wird für die Server-Version (auf meinem Raspberry Pi)
    # auskommentiert, um den Bot nicht in die ewigen Jagdgründe zu schicken.
    #
    # if message.channel.type != discord.ChannelType.private and kommando == 'gehweg':
    #     print('INF: Bot durch Nutzeraufruf beendet.')
    #     try:
    #         await wbi_channel.delete()
    #     except discord.Forbidden:
    #         print('ERR: Löschen des Kanals fehlgeschlagen wegen mangelnder Rechte.')
    #
    #     await client.change_presence(status=discord.Status.offline, activity=None)
    #     await client.close()
    # else:
    #     await werbinichspiel.on_command(kommando, message.author, message.channel)
    #
    await werbinichspiel.on_command(kommando, message.author, message.channel)


client.run('NjkzODE0MDY3MzkwODQwOTE0.XoCitA.GBegT_dDjJxyJG8QsIgvN-DAvfU')
