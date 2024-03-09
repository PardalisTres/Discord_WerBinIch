class WerBinIchNamenSammler:
    """Der Sammler verwaltet online eingegebene Namensvorschläge in einer Textdatei.
    So soll mit der Zeit eine größere Sammlung entstehen,
    sodass das Spiel auch von sich Vorschläge verteilen kann.
    """
    def __init__(self):
        self.dateiname = 'namenskollektion.txt'

    def fuege_namen_hinzu(self, namen):
        try:
            datei = open(self.dateiname, 'a')
        except IOError:
            print('Datei kann nicht geöffnet werden.')
            return

        if isinstance(namen, list):
            for name in namen:
                datei.write(name)
                datei.write('\n')
        else:
            datei.write(namen)
            datei.write('\n')

        print('Namen müssten abgespeichert sein')
        datei.close()

    def sortiere_namensdatei(self):
        # TODO
        pass
