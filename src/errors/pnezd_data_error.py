class DOT39PNEZDDataError(Exception):
    def __init__(self, message='Provided data is either corrupted or incorrectly formatted. Please use PNEZD '
                               'formatted data.'):
        super().__init__(message)
