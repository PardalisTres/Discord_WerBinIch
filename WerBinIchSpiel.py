import asyncio

import discord
from WerBinIchMitspieler import Mitspieler
from WerBinIchNamenSammler import WerBinIchNamenSammler
from WerBinIchSpielStatus import Spielstatus
from derange import derange


class WerBinIchSpiel:

    def __init__(self):
        self.spielerliste = []
        self.channel = None
        self.permutation = None
        self.status = Spielstatus.KEIN_SPIEL

    async def on_command(self, kommando, discorduser, channel):
        if kommando == 'neu':  # wird das überhaupt manuell aufgerufen?
            self.on_neu()
        elif kommando == 'mitspielen':
            await self.on_mitspielen(discorduser)
        elif kommando == 'start':
            await self.on_start()
        elif kommando == 'ende':
            await self.on_ende()
        elif kommando == 'hilfe':
            await self.on_hilfe(channel)
        elif kommando == 'credits':
            await self.on_credits(channel)
        elif kommando == 'liste':
            await self.on_liste(discorduser, channel)
        elif kommando.startswith('nv '):
            name = kommando.split(' ', 1)[1]
            await self.on_namensvorschlag(name, discorduser, channel)
        else:
            nachricht = 'Den Befehl verstehe ich leider nicht. '
            nachricht += 'Eine kurze Bedienungsübersicht liefert \'/wbi hilfe\'.'
            await channel.send(nachricht)

    def on_neu(self):
        self.spielerliste.clear()
        self.permutation = None
        self.status = Spielstatus.KEIN_SPIEL

    async def on_start(self):
        """Startet das Spiel, sobald sich alle Mitspieler angemeldet haben."""

        if self.status != Spielstatus.KEIN_SPIEL:
            print('ERR: on_start(), obwohl nicht KEIN_SPIEL')
            return

        if len(self.spielerliste) < 2:
            await self.channel.send('Spieleranzahl noch nicht ausreichend zum Starten!')
            return

        self.bilde_permutation()
        await self.schreibe_startnachricht()
        await self.frage_spieler_nach_namensvorschlaegen()
        self.status = Spielstatus.WARTE_AUF_VORSCHLÄGE

    async def on_ende(self):
        if self.status != Spielstatus.SPIEL_IM_BETRIEB:
            print('ERR: on_ende, obwohl nicht SPIEL_IM_BETRIEB')
            return

        nachricht = '* * * * *   Spielende!   * * * * *'
        for spieler in self.spielerliste:
            nachricht += '\n{0} war {1}.'.format(spieler.discorduser.display_name, spieler.zuratendername)
        await self.channel.send(nachricht)
        # TODO: an jeden Spieler einzeln senden

        # Bedingungen wie vor dem Spiel schaffen
        self.on_neu()

    @staticmethod
    async def on_hilfe(channel):
        nachricht = 'Hilfe zur Bedienung des rudimentären WerBinIch-Bots:'
        nachricht += '\n Aufruf via: \'/wbi <befehl>\', wobei <befehl> einer der folgenden sein kann:'
        nachricht += '\n     mitspielen :   meldet den Spieler fürs nächste Spiel an'
        nachricht += '\n     start.sh :   beginnt das Spiel (ab zwei Spielern)'
        nachricht += '\n     nv <name> :   reicht (per Direktnachricht!) einen Namensvorschlag ein'
        nachricht += '\n     liste :   listet die Mitspieler auf (sobald ein Spiel begonnen hat)'
        nachricht += '\n     ende :   beendet das Spiel'
        nachricht += '\n     hilfe :   zeigt diesen Text hier an'
        # nachricht += '\n     credits :   zeigt Informationen zur Programmierung an'

        await channel.send(nachricht)

    async def on_liste(self, discorduser, channel):
        if self.status == Spielstatus.KEIN_SPIEL:
            nachricht = 'Es besteht noch kein laufendes Spiel.'
            nachricht += '\nMitspielen wollen:'
            for mitspieler in self.spielerliste:
                nachricht += '\n - {0}'.format(mitspieler.discorduser.display_name)
            await channel.send(nachricht)
            return

        if channel.type == discord.ChannelType.private:
            await self.sende_namensliste_an(discorduser)
        else:
            await self.print_spielerreihenfolge()

    async def on_namensvorschlag(self, name, discorduser, channel):
        """ Nimmt den Namensvorschlag von einem Spieler entgegen.
        Sobald der letzte Vorschlag einging, beginnt das Spiel. """

        if self.status != Spielstatus.WARTE_AUF_VORSCHLÄGE:
            await discorduser.dm_channel.send('Das Spiel wartet gerade nicht auf Vorschläge.')
            return

        # Ist dieser DiscordUser ein Mitspieler?
        id_des_vorschlagenden = -1
        for mitspieler in self.spielerliste:
            if mitspieler.discorduser == discorduser:
                id_des_vorschlagenden = mitspieler.id
                break
        if id_des_vorschlagenden == -1:
            await discorduser.dm_channel.send('Du spielst leider nicht mit! Somit kannst du keinen Vorschlag abgeben.')
            return

        if channel.type != discord.ChannelType.private:
            nachricht = 'Namensvorschläge über einen öffentlichen Kanal nehme ich nicht entgegen. '
            nachricht += 'Da nun jeder diese Idee lesen konnte, denk dir bitte eine andere Person aus '
            nachricht += 'und schreibe sie mir privat.'
            await channel.send(nachricht)
            nachricht = 'Hier können wir privat schreiben. Teil mir hier deinen Namensvorschlag mit.'
            await discorduser.dm_channel.send(nachricht)
            return

        # TODO: Namensvorschlag auf bestimmte Kriterien testen (Mindestlänge)

        # Suche den Spieler, der den Namen raten muss, und speichere ihn dort.
        id_des_ratenden = self.permutation[id_des_vorschlagenden]
        self.spielerliste[id_des_ratenden].zuratendername = name

        await channel.send('Danke für deine Einsendung. Das Spiel kann gleich beginnen.')

        # Überprüfe, ob alle Vorschläge eingereicht sind.
        for mitspieler in self.spielerliste:
            if not mitspieler.zuratendername:
                return
        await self.on_allevorschlaegebereit()

    async def on_mitspielen(self, discorduser):
        if self.status != Spielstatus.KEIN_SPIEL:
            return

        # niemanden doppelt hinzufügen
        for mitspieler in self.spielerliste:
            if mitspieler.discorduser == discorduser:
                print('ERR: Nutzer wollte sich doppelt eintragen')
                return
        self.spielerliste.append(Mitspieler(discorduser, len(self.spielerliste)))

        await self.channel.send('{0} spielt nun auch mit.'.format(discorduser.display_name))

    def bilde_permutation(self):
        self.permutation = derange(list(range(0, len(self.spielerliste))))
        print('Die Permutation ist: {0}'.format(self.permutation))

    async def schreibe_startnachricht(self):
        await self.channel.send('* * * * *   Spielbeginn!   * * * * *')

    async def frage_spieler_nach_namensvorschlaegen(self):
        await self.channel.send('Ich frage die Mitspieler in Direktnachrichten nach ihren Namensvorschlägen.')
        for mitspieler in self.spielerliste:
            ratender = self.spielerliste[self.permutation[mitspieler.id]].discorduser.display_name
            nachricht = 'Bitte teile mir deinen Namensvorschlag für {0} mit,'.format(ratender)
            nachricht += 'indem du ihn mit folgendem Befehl hier in den Chat schreibst:'
            nachricht += '\n/wbi nv <Name, der erraten werden soll>'
            nachricht += '\n(also beispielsweise: \'/wbi nv Ingolf Lück\')'
            if not mitspieler.discorduser.dm_channel:
                await mitspieler.discorduser.create_dm()
            await mitspieler.discorduser.dm_channel.send(nachricht)
            # TODO: Spieler eine Antwort geben, dass sein Vorschlag ankam

    async def print_spielerreihenfolge(self):
        """ Schreibt die Reihenfolge aller Spieler in den Hauptkanal des Spiels. """

        nachricht = 'Reihenfolge der Spieler:'
        for i in range(0, len(self.spielerliste)):
            nachricht += '\n - {0}. {1}'.format(i + 1, self.spielerliste[self.permutation[i]].discorduser.display_name)
        await self.channel.send(nachricht)

    async def on_allevorschlaegebereit(self):
        nachricht = 'Alle Vorschläge wurden eingereicht; es kann losgehen. Viel Spaß!'
        nachricht += '\n(Ihr bekommt die Namen eurer Mitspieler als Direktnachricht.)'
        await self.channel.send(nachricht)

        self.status = Spielstatus.SPIEL_IM_BETRIEB

        # for mitspieler in self.spielerliste:
        #     await self.sende_namensliste_an(mitspieler.discorduser)
        # await self.print_spielerreihenfolge()

        # TODO: ausprobieren, ob das auch wie folgt funktioniert
        # tasks = []
        for mitspieler in self.spielerliste:
            await self.sende_namensliste_an(mitspieler.discorduser)
            # tasks += asyncio.create_task(self.sende_namensliste_an(mitspieler.discorduser))
        await self.print_spielerreihenfolge()

        self.speicherevorschlaegeab()

    async def sende_namensliste_an(self, discorduser):
        nachricht = 'Alle Mitspieler und ihre zu erratenden Namen in Spielreihenfolge:'
        for i in range(0, len(self.spielerliste)):
            spieler_an_position_i = self.spielerliste[self.permutation[i]]
            name = spieler_an_position_i.discorduser.display_name
            if spieler_an_position_i.discorduser == discorduser:
                alias = '<dir unbekannt>'
            else:
                alias = spieler_an_position_i.zuratendername
            nachricht += '\n - {0}. {1} ist {2}'.format(i+1, name, alias)
        await discorduser.dm_channel.send(nachricht)

    @staticmethod
    async def on_credits(channel):
        nachricht = 'Credits dieses minimalistischen WerBinIch-Bots:'
        nachricht += '\nProgrammierung: Sascha Ozelot_3 Kook'
        nachricht += '\nDanke fürs Testen an: Sabrina, Katja'
        nachricht += '\nUnd fürs Testspielen an: Seyda, Robin, Jule'
        await channel.send(nachricht)

    def speicherevorschlaegeab(self):
        sammler = WerBinIchNamenSammler()
        namen = []
        for spieler in self.spielerliste:
            namen.append(spieler.zuratendername)
        print('INF: speichere {0} Vorschläge ab'.format(len(namen)))
        sammler.fuege_namen_hinzu(namen)

    async def on_ready(self):
        """ Wird direkt nach dem Anschluss an den Server aufgerufen
         und gibt eine Willkommensnachricht aus. """
        nachricht = 'Hallo. Ich bin ein rudimentärer Discord-Bot, der dazu genutzt werden kann,'
        nachricht += ' "Wer bin ich" zu spielen.'
        nachricht += '\nHier soll nicht über die Spielregeln aufgeklärt werden, aber eine'
        nachricht += ' kurze Information zur Bedienung kann vielleicht nicht schaden...'
        await self.channel.send(nachricht)
        await self.on_hilfe(self.channel)
