# pydpt-test.py
# Copyright 2007 - 2015 Roger Marsh
# See www.dptoolkit.com for details of DPT (site expired 15 January 2015)
# License: DPToolkit license

"""Sample code to do deferred and non-deferred updates.

An attempt is made to force DPT to store enough records, by volume, that it has
to do deferred updates in multiple chunks.

Some chess game scores, converted to a non-standard but easily processed form,
are used repeatedly to store a large volume of records.

The chess game scores are in a form convenient for generating DPT test data.

A set of moves assumes an empty board.

Three character instructions state put a piece on a square. 'e4P' means put a
white pawn on e4.

Four character instructions state move the piece on the first square to the
second square. 'e2e4' means move the piece on e2 to e4.

Five character instructions state move the piece on the first square to the
second square and turn in into the named piece. 'e7e8q' means move the piece on
e7 to e8 and turn it into a black queen. (Yes, that is illegal in chess, but
not here.)

Castling and en-passant captures are done by a sequence of individual piece
moves.  There is no requirement that an instruction to move a white piece is
followed by an instruction to move a black piece.

The idea is to construct a database where each record gives the location of a
piece after application of an instruction.  The number of records created by an
instruction is the number of pieces on the board after its application.  A real
game will generate just over 1800 records.

"""

if __name__=='__main__':

    import os
    import random

    # Neither multiprocessing nor subprocess used despite allowing unresponsive
    # widgets.  An earlier version of this module used subprocess to control
    # multi-step deferred updates.
    # threading not used because the Global Interpreter Lock is held at
    # inconvenient times.
    import sys
    pyversion3 = False
    version = '.'.join((str(s) for s in sys.version_info[:2]))
    if sys.version_info[:1] >= (3,):
        pyversion3 = True
    del sys

    if pyversion3:
        import tkinter as tki
        import tkinter.messagebox as tkimb
        import tkinter.filedialog as tkifd
    else:
        import Tkinter as tki
        import tkMessageBox as tkimb
        import tkFileDialog as tkifd
    
    from dptdb import dptapi

    scores = (
        ('a1R', 'b1N', 'c1L', 'd1Q', 'e1K', 'f1L', 'g1N', 'h1R',
         'a2P', 'b2P', 'c2P', 'd2P', 'e2P', 'f2P', 'g2P', 'h2P',
         'a7p', 'b7p', 'c7p', 'd7p', 'e7p', 'f7p', 'g7p', 'h7p',
         'a8r', 'b8n', 'c8l', 'd8q', 'e8k', 'f8l', 'g8n', 'h8r', # initial position
         'd2d4', # first move
         'f7f5',
         'g2g3',
         'e7e6',
         'f1g2',
         'g8f6',
         'c2c4',
         'f8e7',
         'b1c3',
         'd7d6',
         'g1f3',
         'e8g8', 'h8f8', # black castles king-side
         'e1g1', 'h1f1', # white castles king-side
         'a7a5',
         'b2b3',
         'f6e4',
         'c1b2',
         'e4c3',
         'b2c3',
         'd8e8',
         'a2a3',
         'e8h5',
         'f3e1',
         'b8d7',
         'e2e3',
         'h5h6',
         'e1d3',
         'd7f6',
         'd1e2',
         'f6g4',
         'h2h3',
         'g4f6',
         'f2f3',
         'g7g5',
         'e3e4',
         'f6h5',
         'c3e1',
         'f5f4',
         'g3g4',
         'h5g7',
         'e1f2',
         'h6g6',
         'b3b4',
         'c8d7',
         'b4b5',
         'h7h5',
         'e4e5',
         'd6d5',
         'd3c5',
         'd7c8',
         'f1c1',
         'c7c6',
         'a3a4',
         'g7e8',
         'f2e1',
         'b7b6',
         'c5b3',
         'c6b5',
         'c4b5',
         'c8d7',
         'g2f1',
         'h5g4',
         'h3g4',
         'g8g7',
         'a1a2',
         'f8h8',
         'e2d3',
         'g6h6',
         'a2g2',
         'e7d8',
         'g1f2',
         'e8c7',
         'f2e2',
         'g7f7',
         'e2d1',
         'h6f8',
         'c1c2',
         'f7g7',
         'g2h2',
         'd7e8',
         'h2h8',
         'f8h8',
         'd3d2',
         'e8g6',
         'f1d3',
         'h8h1',
         'd2e2',
         'h1h7',
         'd3g6',
         'h7g6',
         'd1c1',
         'a8b8',
         'c1c6',
         'c7e8',
         'e2d2',
         'b8b7',
         'd2c3',
         'g6f7',
         'c1b2',
         'f7d7',
         'c3c2',
         'b7c7',
         'b3d2',
         'd8e7',
         'c6c7',
         ),
        ('a1R', 'b1N', 'c1L', 'd1Q', 'e1K', 'f1L', 'g1N', 'h1R',
         'a2P', 'b2P', 'c2P', 'd2P', 'e2P', 'f2P', 'g2P', 'h2P',
         'a7p', 'b7p', 'c7p', 'd7p', 'e7p', 'f7p', 'g7p', 'h7p',
         'a8r', 'b8n', 'c8l', 'd8q', 'e8k', 'f8l', 'g8n', 'h8r',
         'g1f3',
         'g7g6',
         'e2e4',
         'f8g7',
         'd2d4',
         'c7c6',
         'h2h3',
         'd7d5',
         'b1d2',
         'g8f6',
         'e4e5',
         'f6e4',
         'f1d3',
         'c8f5',
         'g2g4',
         'e4d2',
         'g4f5',
         'd2f3',
         'd1f3',
         'c6c5',
         'f5f6',
         'e7f6',
         'e5f6',
         'd8f6',
         'f3f6',
         'g7f6',
         'd4c5',
         'e8g8', 'h8f8',
         'c2c3',
         'b8d7',
         'c1e3',
         'f8c8',
         'e1c1', 'a1d1',
         'd7c5',
         'd3e2',
         'c5a4',
         'e3d4',
         'f6d4',
         'd1d4',
         'a4b6',
         'e2f3',
         'c8c5',
         'h1d1',
         'a8d8',
         'c1c2',
         'd8d7',
         'b2b4',
         'c5c6',
         'f3d5',
         'c6f6',
         'f2f4',
         'b6d5',
         'd4d5',
         'd7c7',
         'd5d7',
         'f6c6',
         'd7c7',
        ),
        ('a1R', 'b1N', 'c1L', 'd1Q', 'e1K', 'f1L', 'g1N', 'h1R',
         'a2P', 'b2P', 'c2P', 'd2P', 'e2P', 'f2P', 'g2P', 'h2P',
         'a7p', 'b7p', 'c7p', 'd7p', 'e7p', 'f7p', 'g7p', 'h7p',
         'a8r', 'b8n', 'c8l', 'd8q', 'e8k', 'f8l', 'g8n', 'h8r',
         'd2d4',
         'g8f6',
         'c2c4',
         'g7g6',
         'b1c3',
         'd7d5',
         'c4d5',
         'f6d5',
         'e2e4',
         'd5c3',
         'b2c3',
         'f8g7',
         'a1b1',
         'e8g8', 'h8f8',
         'c1e3',
         'c7c5',
         'b1b5',
         'b7b6',
         'g1f3',
         'c8a6',
         'b5b1',
         'a6f1',
         'e1f1',
         'c5d4',
         'c3d4',
         'd8d7',
         'f1e2',
         'f8d8',
         'd1b3',
         'b8c6',
         'd4d5',
         'c6a5',
         'b3d3',
         'a8c8',
         'h1c1',
         'd7a4',
         'e3d4',
         'g7h6',
         'c1c3',
         'a4a2',
         'e2f1',
         'c8c3',
         'd4c3',
         'a2c4',
         'd3c4',
         'a5c4',
         'b1a1',
         'a7a5',
         'f3d4',
         'h6d2',
         'd4c6',
         'd2c3',
         'a1c1',
         'd8d7',
         'f1e2',
         'c4e5',
         'c1c3',
         'e5c6',
         'c3c6',
         'd7b7',
         'e4e5',
         'b7d7',
         'd5d6',
         'e7d6',
         'e5d6',
         'b6b5',
         'e2d3',
         'f7f6',
         'd3d4',
         'g8f7',
         'd4d5',
         'f7e8',
         'c6b6',
         'b5b4',
         'd5e6',
         'd7d8',
         'b6b7',
         'd8a8',
         'b7h7',
        ),
        ('a1R', 'b1N', 'c1L', 'd1Q', 'e1K', 'f1L', 'g1N', 'h1R',
         'a2P', 'b2P', 'c2P', 'd2P', 'e2P', 'f2P', 'g2P', 'h2P',
         'a7p', 'b7p', 'c7p', 'd7p', 'e7p', 'f7p', 'g7p', 'h7p',
         'a8r', 'b8n', 'c8l', 'd8q', 'e8k', 'f8l', 'g8n', 'h8r',
         'f2f4',
         'g7g6',
         'g1f3',
         'f8g7',
         'b1c3',
         'd7d5',
         'e2e3',
         'c7c5',
         'f1b5',
         'c8d7',
         'e1g1', 'h1f1',
         'd7b5',
         'c3b5',
         'a7a6',
         'b5c3',
         'g8f6',
         'b2b3',
         'f6e4',
         'c1b2',
         'e4c3',
         'b2c3',
         'g7c3',
         'd2c3',
         'b8c6',
         'd1e2',
         'd8a5',
         'c3c4',
         'd5c4',
         'e2c4',
         'a5b4',
         'c4e2',
         'e8g8', 'h8f8',
         'e2f2',
         'a8d8',
         'a2a4',
         'b4c3',
         'h2h4',
         'e7e5',
         'f2e1',
         'c3e1',
         'f3e1',
         'e5f4',
         'e3f4',
         'c6d4',
         'f1f2',
         'f8e8',
         'g1f1',
         'h7h5',
         'a1b1',
         'd4f5',
         'e1f3',
         'f5e3',
         'f1g1',
         'e3g4',
         'f2f1',
         'e8e2',
         'f3e1',
         'd8d2',
         'b1c1',
         'g4e3',
         'g2g3',
         'e3f1',
        ),
        )

    def execute():

        def write_record(piecesquare, token, game, pid, gid):
            """"""
            fieldvalue = dptapi.APIFieldValue()
            storerecordtemplate = dptapi.APIStoreRecordTemplate()
            fieldvalue.Assign(piecesquare[0])
            storerecordtemplate.Append(piece, fieldvalue)
            fieldvalue.Assign(piecesquare)
            storerecordtemplate.Append(location, fieldvalue)
            fieldvalue.Assign(token)
            storerecordtemplate.Append(movenum, fieldvalue)
            fieldvalue.Assign(game)
            storerecordtemplate.Append(scorenum, fieldvalue)
            fieldvalue.Assign(pid)
            storerecordtemplate.Append(positionid, fieldvalue)
            fieldvalue.Assign(gid)
            storerecordtemplate.Append(gameid, fieldvalue)
            csgoc.StoreRecord(storerecordtemplate)
            storerecordtemplate.Clear()

        def process_games():
            """Generate lots of games.dpt file records from a few games"""
            # outer and inner loops generate neither pseudo-random nor completely
            # uniform record patterns, but do mix it up a little.
            # write the records for each game factor times and repeat the number
            # of times given by factor * size_factor // 2
            # Get the highest POSITIONID on file to set next to be used.
            c = csgoc.OpenDirectValueCursor(
                dptapi.APIFindValuesSpecification(positionid))
            c.SetDirection(dptapi.CURSOR_DESCENDING)
            c.GotoFirst()
            count = (c.GetCurrentValue().ExtractNumber() + 1
                     if c.Accessible() else 0)
            csgoc.CloseDirectValueCursor(c)
            # Get the highest GAMEID on file to set next to be used.
            c = csgoc.OpenDirectValueCursor(
                dptapi.APIFindValuesSpecification(gameid))
            c.SetDirection(dptapi.CURSOR_DESCENDING)
            c.GotoFirst()
            gamecount = (c.GetCurrentValue().ExtractNumber() + 1
                     if c.Accessible() else 0)
            csgoc.CloseDirectValueCursor(c)
            for outer in range(factor * size_factor // 2):
                for eg, g in enumerate(scores):
                    board = {}
                    for file in 'abcdefgh':
                        board[file] = {}
                        for rank in '12345678':
                            board[file][rank] = None
                    for em, move in enumerate(g):
                        if len(move) == 3:
                            tofile, torank, topiece = move
                            fromfile = tofile
                            fromrank = torank
                        elif len(move) == 4:
                            fromfile, fromrank, tofile, torank = move
                            topiece = board[fromfile][fromrank]
                        elif len(move) == 5:
                            fromfile, fromrank, tofile, torank, topiece = move
                        board[fromfile][fromrank] = None
                        board[tofile][torank] = topiece
                        position = [''.join((board[f][r], f, r))
                                    for f in 'abcdefgh'
                                    for r in '12345678'
                                    if board[f][r]]
                        for inner in range(factor):
                            for p in position:
                                write_record(
                                    p,
                                    em,
                                    eg,
                                    count,
                                    gamecount + inner)
                            count += 1
                gamecount += factor

        def get_psm(score, movenum):
            """Return the new piece location generated on movenum in score"""
            board = {}
            for file in 'abcdefgh':
                board[file] = {}
                for rank in '12345678':
                    board[file][rank] = None
            for e, move in enumerate(score):
                if len(move) == 3:
                    tofile, torank, topiece = move
                    fromfile = tofile
                    fromrank = torank
                elif len(move) == 4:
                    fromfile, fromrank, tofile, torank = move
                    topiece = board[fromfile][fromrank]
                elif len(move) == 5:
                    fromfile, fromrank, tofile, torank, topiece = move
                board[fromfile][fromrank] = None
                board[tofile][torank] = topiece
                if e == movenum:
                    return (topiece, fromfile, fromrank, tofile, torank)

        # File size increments
        table_b_size = 740
        table_d_size = 288
        records_per_page = 320

        size = sizeopts.get(filesize.get())
        mode = modeopts.get(defermode.get())
        loadmemp = loadmempmax if size is None else force_multi_chunk_loadmemp

        if mode is None:
            tkimb.showerror(
                title=''.join(
                    ('DPT API test on Python', version, ' - Execute')),
                message='Select an update mode',
                )
            return
        elif mode == deferred:
            # Attempt to force multi-chunk deferred update, if requested, by
            # doing more record insertions.  Probably a lot more.
            size_factor = 2 * (2 ** filesize.get())
        else:
            size_factor = 2
        # See function process_games() for effect of factor.
        factor = 5

        folder = tkifd.askdirectory()
        if not folder:
            return
        # Necessary at Python2.7, and probably Python2.6, to coerce folder from
        # unicode to str so that later os.path.join()s return str not unicode.
        # APIDatabaseServices(), and DPT API calls in general, accept str but
        # not unicode.  The coercion is not needed at earlier and later Python
        # versions.
        folder = str(folder)
        # On some Python2.6 distributions the following test always evaluates
        # True because the underlying comparison is booleanString with str
        # (according to my note dated 2009-08-01).
        # The work around is wrap the underlying _show() call as str(_show()).
        if not tkimb.askokcancel(
            title=''.join(
                ('DPT API test on Python', version, ' - Execute')),
            message=''.join(
                ('Please confirm that you want to use folder\n',
                 folder,
                 )),
            ):
            return

        # File names
        games = os.path.join(folder, 'games.dpt')
        ddgames = os.path.splitext(os.path.basename(games))[0].upper()

        # Cannot open uninitialized file in deferred update mode (and a file
        # that does not exist is uninitialized).
        defer_not_exists = mode == deferred and not os.path.exists(games)
        if defer_not_exists:
            if not tkimb.askyesno(
                title=''.join(
                    ('DPT API test on Python', version, ' - Execute')),
                message=''.join(
                    ('Cannot open uninitialized file for ', mode, ' update.',
                     '\n\nDo you want to create an empty initialised file?',
                     )),
                ):
                return
        elif size is None and mode == deferred:
            text.insert(
                tki.END,
                ''.join(
                    ('\n',
                     'Execute ', mode, ' update using folder:\n',
                     folder,
                     '\nwithout attemting to force multi-chunk.\n',
                     )))
        elif mode == deferred:
            text.insert(
                tki.END,
                ''.join(
                    ('\n',
                     'Execute ', mode, ' update using folder:\n',
                     folder,
                     '\nattemting to force multi-chunk on a ',
                     size, ' memory PC.\n',
                     )))
        else:
            text.insert(
                tki.END,
                ''.join(
                    ('\n',
                     'Execute ', mode, ' update using folder:\n',
                     folder, '.'
                     '\n',
                     )))

        dptsys = os.path.join(folder, 'sys')
        parms = os.path.join(dptsys, 'parms.ini')
        msgctl = os.path.join(dptsys, 'msgctl.ini')
        sysprint = os.path.join(dptsys, 'sysprint.txt')
        audit = os.path.join(dptsys, 'audit.txt')

        # Create the folders.
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists(dptsys):
            os.makedirs(dptsys)
            
        # Set parms for normal or single-step deferred update mode
        if mode == deferred:
            pf = open(parms, 'w')
            try:
                pf.write("RCVOPT=X'00' " + os.linesep)
                pf.write("MAXBUF=200 " + os.linesep)
                pf.write("LOADMEMP=" + loadmemp + ' ' + os.linesep)
            finally:
                pf.close()
        elif os.path.exists(parms):
            os.remove(parms) # assume delete will work here

        # Ensure checkpoint.ckp file and #SEQTEMP folder are created in correct
        # folder (change current working directory).
        pycwd = os.getcwd()
        os.chdir(dptsys)
        # Use CONSOLE rather than sysprint because SYSPRNT is not fully released
        # unless Python is restarted as a new command line command.
        # To see CONSOLE run this script by python.exe rather than pythonw.exe
        ds = dptapi.APIDatabaseServices(
            'CONSOLE',
            'pyapitest',
            parms,
            msgctl,
            audit)
        os.chdir(pycwd)

        # Allocate, create, and open context on file, followed by initialize
        # file and create fields if it does not yet exist.
        disp = os.path.exists(games)
        # Either explicit FILEDISP_OLD or FILEDISP_NEW, or just FILEDISP_COND.
        if disp:
            ds.Allocate(ddgames, games, dptapi.FILEDISP_OLD)
        else:
            ds.Allocate(ddgames, games, dptapi.FILEDISP_NEW)
            # Create the file very small for deferred update requests because
            # a later update request will increase the size as required.
            # This request will create the file but not do any record updates
            # if the request is for deferred updates.
            ds.Create(ddgames,
                      10 if mode == deferred else table_b_size * size_factor,
                      records_per_page,
                      -1,
                      -1,
                      30 if mode == deferred else table_d_size * size_factor,
                      -1,
                      -1,
                      dptapi.FILEORG_UNORD_RRN)
        csg = dptapi.APIContextSpecification(ddgames)
        if mode == deferred and not defer_not_exists:
            csgoc = ds.OpenContext_DUSingle(csg)
        else:
            csgoc = ds.OpenContext(csg)
        if not disp:
            csgoc.Initialize()
            # SCORENUM
            fascore = dptapi.APIFieldAttributes()
            fascore.SetInvisibleFlag()
            fascore.SetOrderedFlag()
            csgoc.DefineField(scorenum, fascore)
            # LOCATION
            falocation = dptapi.APIFieldAttributes()
            falocation.SetOrderedFlag()
            csgoc.DefineField(location, falocation)
            # PIECE
            fapiece = dptapi.APIFieldAttributes()
            fapiece.SetOrderedFlag()
            csgoc.DefineField(piece, fapiece)
            # MOVENUM
            famovenum = dptapi.APIFieldAttributes()
            famovenum.SetFloatFlag()
            famovenum.SetOrderedFlag()
            famovenum.SetOrdNumFlag()
            csgoc.DefineField(movenum, famovenum)
            # POSITIONID
            fapositionid = dptapi.APIFieldAttributes()
            fapositionid.SetFloatFlag()
            fapositionid.SetOrderedFlag()
            fapositionid.SetOrdNumFlag()
            csgoc.DefineField(positionid, fapositionid)
            # GAMEID
            fagameid = dptapi.APIFieldAttributes()
            fagameid.SetFloatFlag()
            fagameid.SetOrderedFlag()
            fagameid.SetOrdNumFlag()
            csgoc.DefineField(gameid, fagameid)

        if defer_not_exists:
            # See binding defer_not_exists for notes on why this code exists.
            # See end of this function for some notes on this sequence.
            ds.CloseContext(csgoc)
            ds.Free(ddgames)
            pycwd = os.getcwd()
            os.chdir(dptsys)
            ds.Destroy()
            os.chdir(pycwd)
            text.insert(
                tki.END,
                ''.join(
                    ('\n',
                     'New empty ', ddgames, ' file created in normal mode ',
                     'in response to ', mode, ' update request.',
                     '\n',
                     )))
            return

        # Increase the file size if it existed before allocation.
        # Here the necessary amount is easy to predict.  In most cases this will
        # be difficult, at least.  It may be necessary to do a try increase,
        # recover if exception, loop until the update suceeds while avoiding
        # making the file bigger, possibly by orders of magnitude, than needed.
        if disp:
            # Do not bother to optimize, here, by looking to see which kind of
            # extent is currently last in the file.
            csgoc.Increase(table_b_size * size_factor, False)
            csgoc.Increase(table_d_size * size_factor, True)

        # Count records.
        gfs1 = csgoc.FindRecords()
        text.insert(
            tki.END,
            ''.join(
                ('\n',
                 'Number of records on ', ddgames, ' file is: ',
                 str(gfs1.Count()),
                 '\n',
                 )))
        csgoc.DestroyRecordSet(gfs1)

        # Close and open context then count records again.
        ds.CloseContext(csgoc)
        if mode == deferred:
            csgoc = ds.OpenContext_DUSingle(csg)
        else:
            csgoc = ds.OpenContext(csg)
        gfs1 = csgoc.FindRecords()
        text.insert(
            tki.END,
            ''.join(
                ('Close and open context\n',
                 'Number of records on ', ddgames, ' file is: ',
                 str(gfs1.Count()),
                 '\n',
                 )))
        csgoc.DestroyRecordSet(gfs1)

        # Free and allocate file then count records again.
        ds.CloseContext(csgoc)
        ds.Free(ddgames)
        ds.Allocate(ddgames, games, dptapi.FILEDISP_OLD)
        if mode == deferred:
            csgoc = ds.OpenContext_DUSingle(csg)
        else:
            csgoc = ds.OpenContext(csg)
        gfs1 = csgoc.FindRecords()
        text.insert(
            tki.END,
            ''.join(
                ('Free and allocate file\n',
                 'Number of records on ', ddgames, ' file is: ',
                 str(gfs1.Count()),
                 '\n',
                 )))
        csgoc.DestroyRecordSet(gfs1)

        # Close and free file.
        ds.CloseContext(csgoc)
        ds.Free(ddgames)

        # Allocate and open file then store records.
        ds.Allocate(ddgames, games, dptapi.FILEDISP_OLD)
        if mode == deferred:
            csgoc = ds.OpenContext_DUSingle(csg)
        else:
            csgoc = ds.OpenContext(csg)
        process_games()

        # Close and free file to apply deferred updates
        ds.CloseContext(csgoc)
        ds.Free(ddgames)

        # Allocate and open file then count the stored records.
        # Open context in normal mode
        ds.Allocate(ddgames, games, dptapi.FILEDISP_OLD)
        csgoc = ds.OpenContext(csg)
        gfs1 = csgoc.FindRecords()
        text.insert(
            tki.END,
            ''.join(
                ('Store some records\n',
                 'Number of records on ', ddgames, ' file is: ',
                 str(gfs1.Count()),
                 '\n',
                 )))
        csgoc.DestroyRecordSet(gfs1)

        # Setup for some finds
        recranges = [0]
        for s in scores:
            recranges.append(len(s) + recranges[-1])
        interval = sum(recranges)
        random.seed()
        
        # Do a few random finds.
        fieldvalue = dptapi.APIFieldValue()
        for e, s in enumerate(scores):
            sm = random.randrange(32, len(s) - 1)
            topiece, fromfile, fromrank, tofile, torank = get_psm(s, sm)
            try:
                fieldvalue.Assign(''.join((topiece, tofile, torank)))
            except:
                text.insert(
                    tki.END,
                    ''.join(
                        ('Problem constructing key from ',
                         str(topiece), ' ', str(tofile), ' ', str(torank), ' ',
                         'for move ', str(sm), '\n',
                         )))
                continue
            fslocation = csgoc.FindRecords(location, dptapi.FD_EQ, fieldvalue)
            fieldvalue.Assign(sm)
            fsmovenum = csgoc.FindRecords(movenum, dptapi.FD_EQ, fieldvalue)
            # Cannot use the style
            # FindRecords(APIFindSpecification & APIFindSpecification)
            # to express the find criterion.
            # Get TypeError: unsupported operand type(s) for &.
            # Shame because __iand__ and __ior__ are supported.
            #fspsm = csgoc.FindRecords(
            #    dptapi.APIFindSpecification(
            #        movenum, dptapi.FD_EQ, dptapi.APIFieldValue(sm)),
            #    fslocation)
            # But here the commented FindRecords statement is probably best
            fdspec1 = dptapi.APIFindSpecification(
                movenum, dptapi.FD_EQ, dptapi.APIFieldValue(sm))
            fdspec1 &= dptapi.APIFindSpecification(
                location,
                dptapi.FD_EQ,
                dptapi.APIFieldValue(''.join((topiece, tofile, torank))))
            fspsm = csgoc.FindRecords(fdspec1)
            text.insert(
                tki.END,
                ''.join(
                    ('\nRandom location for ', movenum, ' ', str(sm),
                     ' in ', scorenum, ' ', str(e), ' is: ',
                     ''.join((fromfile, fromrank, tofile, torank, ' ',topiece)),
                     '\nNumber of records for ', movenum, ' ', str(sm),
                     ' in ', scorenum, ' ', str(e), ' is: ',
                     str(fsmovenum.Count()),
                     '\n',
                     'Number of records for ', location, ' ',
                     str(''.join((topiece, tofile, torank))),
                     ' in ', scorenum, ' ', str(e), ' is: ',
                     str(fslocation.Count()),
                     '\n',
                     'Number of records for ', location, ' ',
                     str(''.join((topiece, tofile, torank))), ' at ', movenum,
                     ' ', str(sm), ' in ', scorenum, ' ', str(e), ' is: ',
                     str(fspsm.Count()),
                     '\n',
                     )))
            # Pick a record at random from those created from current score and
            # reconstruct the game from the value of POSITIONID on that record.
            # Not the newer random access pseudo-cursors because the selection
            # is by position in set rather than record number.
            gamerecs = csgoc.FindRecords(
                scorenum, dptapi.FD_EQ, dptapi.APIFieldValue(e))
            recpos = random.randrange(0, gamerecs.Count() - 1)
            c = gamerecs.OpenCursor()
            c.GotoFirst()
            while c.Accessible():
                if recpos > 0:
                    recpos -= 1
                    c.Advance(1)
                    continue
                fsrecpos = csgoc.FindRecords(
                    dptapi.APIFindSpecification(
                        dptapi.FD_SINGLEREC, c.LastAdvancedRecNum()))
                reconstruct_position(fsrecpos)
                csgoc.DestroyRecordSet(fsrecpos)
                break
            gamerecs.CloseCursor(c)
            csgoc.DestroyRecordSet(gamerecs)
            # Tidy up loop
            csgoc.DestroyRecordSet(fslocation)
            csgoc.DestroyRecordSet(fsmovenum)
            csgoc.DestroyRecordSet(fspsm)
        text.insert(
            tki.END,
            ''.join(
                ('\nNote that each score is used many times to generate ',
                 'records.\n\n',
                 )))

        # Close and free file.
        ds.CloseContext(csgoc)
        ds.Free(ddgames)

        # Destroy the APIDatabaseServices object and ensure the
        # checkpoint.ckp file and #SEQTEMP folder are removed.
        # (If all file allocation and so forth are removed then the zero length
        #  checkpoint file is not deleted.)
        pycwd = os.getcwd()
        os.chdir(dptsys)
        # Repeated calls to the execute() function are fine for any sequence of
        # Normal or Deferred selections except for the first Deferred call after
        # a Normal call; which generates a RuntimeError in the ds.Destroy()
        # call immediately following.
        # This may be true only when no records are stored in the call because
        # the problem disappeared when process_games function was added.
        ds.Destroy()
        os.chdir(pycwd)

        filesize.set(0)
        defermode.set(0)

    def quit_():
        root.quit()
    
    def testapp():

        def force_chunk(opt):
            return ' '.join(("Try to force 'multi-chunk' on", opt, 'memory'))
        
        root.wm_title(''.join(('DPT API test on Python', version)))
        choiceframe = tki.Frame(master=root)
        textframe = tki.Frame(master=root)
        buttonframe = tki.Frame(master=root)
        buttonframe.pack(side=tki.BOTTOM)
        choiceframe.pack(side=tki.TOP, fill=tki.X)
        textframe.pack(side=tki.TOP, fill=tki.BOTH, expand=tki.TRUE)
        text = tki.Text(master=textframe, wrap='word', undo=tki.FALSE)
        scrollbar = tki.Scrollbar(
            master=textframe, orient=tki.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tki.RIGHT, fill=tki.Y)
        text.pack(side=tki.LEFT, fill=tki.BOTH, expand=tki.TRUE)
        sizeframe = tki.Frame(master=choiceframe)
        deferframe = tki.Frame(master=choiceframe)
        sizeframe.pack(side=tki.LEFT, fill=tki.BOTH, expand=tki.TRUE)
        deferframe.pack(side=tki.LEFT, fill=tki.BOTH, expand=tki.TRUE)
        tki.Radiobutton(
            master=sizeframe,
            text=force_chunk(sizeopts[1]),
            variable=filesize,
            value=1,
            ).pack(side=tki.TOP, padx=30)
        tki.Radiobutton(
            master=sizeframe,
            text=force_chunk(sizeopts[2]),
            variable=filesize,
            value=2,
            ).pack(side=tki.TOP, padx=30)
        tki.Radiobutton(
            master=sizeframe,
            text=force_chunk(sizeopts[3]),
            variable=filesize,
            value=3,
            ).pack(side=tki.TOP, padx=30)
        tki.Radiobutton(
            master=sizeframe,
            text=force_chunk(sizeopts[4]),
            variable=filesize,
            value=4,
            ).pack(side=tki.TOP, padx=30)
        tki.Radiobutton(
            master=sizeframe,
            text=force_chunk(sizeopts[5]),
            variable=filesize,
            value=5,
            ).pack(side=tki.TOP, padx=30)
        tki.Radiobutton(
            master=deferframe,
            text=modeopts[1].title(),
            variable=defermode,
            value=1,
            ).pack(side=tki.TOP, padx=40)
        tki.Radiobutton(
            master=deferframe,
            text=modeopts[2].title(),
            variable=defermode,
            value=2,
            ).pack(side=tki.TOP, padx=40)
        tki.Button(master=buttonframe, text='Quit', command=quit_,
                   ).pack(side=tki.RIGHT, padx=20, ipadx=20, ipady=4)
        tki.Button(master=buttonframe, text='Execute', command=execute,
                   ).pack(side=tki.LEFT, padx=20, ipadx=20, ipady=4)
        text.insert(
            tki.END,
            ''.join(
                ('Select Normal or Deferred Update mode.\n\n',
                 'A selected force multi-chunk option will be used for ',
                 'deferred updates.  By default deferred updates are done ',
                 'in a single chunk if possible.\n\n',
                 'Without forcing, multi-chunk deferred updates would need ',
                 'runs lasting many minutes to be demonstrated.  Forcing ',
                 'consists of doing lots of record inserts and imposing an ',
                 'upper limit on the percentage of memory used.\n\n',
                 'The multi-chunk option is ignored in Normal mode.\n',
                 )))
        return text

    def reconstruct_position(fs):
        """Get position from value of field on first record on Foundset fs"""
        c = fs.OpenCursor()
        c.GotoFirst()
        if not c.Accessible():
            fs.CloseCursor()
            return
        r = c.AccessCurrentRecordForRead()
        text.insert(
            tki.END,
            ' '.join(
                ('Position for', positionid,
                 r.GetFieldValue(positionid).ExtractString(),
                 ',', movenum,
                 r.GetFieldValue(movenum).ExtractString(),
                 'from', gameid,
                 r.GetFieldValue(gameid).ExtractString(),
                 'is:\n',
                 )))
        oc = r.GetHomeFileContext()
        moves = oc.FindRecords(
            positionid, dptapi.FD_EQ, r.GetFieldValue(positionid))
        # Sort the moves by MOVENUM and display them in the text widget in
        # sorted order.
        spec = dptapi.APISortRecordsSpecification()
        spec.AddDataField(location)
        spec.AddKeyField(movenum)
        sortmoves = moves.Sort(spec)
        position = []
        smc = sortmoves.OpenCursor()
        smc.GotoFirst()
        while smc.Accessible():
            mr = smc.AccessCurrentRecordForRead()
            position.append(mr.GetFieldValue(location).ExtractString())
            smc.Advance(1)
        text.insert(tki.END, ' '.join(position))
        text.insert(tki.END, '\n')
        # Close recordsets
        sortmoves.CloseCursor(smc)
        fs.CloseCursor(c)
        oc.DestroyRecordSet(sortmoves)
        oc.DestroyRecordSet(moves)

    # Field names
    piece = 'PIECE'
    location = 'LOCATION'
    movenum = 'MOVENUM'
    scorenum = 'SCORENUM'
    positionid = 'POSITIONID'
    gameid = 'GAMEID'

    # User interface options
    deferred = 'deferred'
    sizeopts = {1:'2GB', 2:'4GB', 3:'8GB', 4:'16GB', 5:'32GB'}
    modeopts = {1:'normal', 2:deferred}
    # On my 2GB memory PC values of 5, the minimum allowed LOADMEMP, or 6 lead
    # to a RuntimeError reporting file is physically inconsistent.
    force_multi_chunk_loadmemp = '7'
    loadmempmax = '75' # the default value
    root = tki.Tk() # So IntVar items can be outside testapp
    filesize = tki.IntVar(value=0) # outside testapp so initial value shown
    defermode = tki.IntVar(value=0) # outside testapp so initial value shown
    # But both are zero initially so no practical difference in this case.
    text = testapp()
    root.mainloop()
    try:
        root.destroy()
    except:
        # Assume use of a destroy widget tool, or Alt+F4, not the Quit button.
        pass
    # Tidy up. Often not done.
    del quit_, execute, pyversion3, version, testapp, scores
    del text, root, filesize, defermode, sizeopts, modeopts, deferred
    del force_multi_chunk_loadmemp, loadmempmax
    del piece, location, movenum, scorenum, positionid, gameid
    del tki, tkimb, tkifd
