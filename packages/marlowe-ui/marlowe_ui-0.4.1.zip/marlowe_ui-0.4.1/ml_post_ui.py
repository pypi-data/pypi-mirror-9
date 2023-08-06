#!/usr/bin/env python

import re
import logging

import tkinter as tk

import marlowe_ui.tktool.askfilename
import marlowe_ui.postprocess.dumper
import marlowe_ui.logconsole

logger = logging.getLogger('ml_post_ui')

if __name__ == '__main__':
    app = tk.Tk()

    # input file chooser
    labelframe = tk.LabelFrame(app, text='Input Filename')
    labelframe.pack(fill=tk.X)

    filepath = marlowe_ui.tktool.askfilename.OpenFileName(
        labelframe,
        diagfiletypes=[('Marlowe output', '*.lst'), ('All', '*')])
    filepath.pack(fill=tk.X)

    def runbutton():
        try:
            inputf = filepath.get()
            logger.info('input file: {}'.format(inputf))
            if not inputf:
                raise Exception('input file is Null')

            # generate output dirname
            output = re.sub('\.lst$', '.post', inputf)
            logger.info('output directory: {}'.format(output))

            if inputf == output:
                raise Exception('input and output have same name,'
                                'input file should have ".lst" suffix, currently')
            p = marlowe_ui.postprocess.dumper.Parser(outputdir=output)
            with open(inputf, 'rt') as f:
                logger.info('expanding')
                p.parse(f)
            logger.info('finished.')
        except Exception as e:
            logger.error(str(e))
        logger.info('ready')

    # run button
    button = tk.Button(app, text='Expand Data', command=runbutton)
    button.pack()

    # msgbox
    logtext = tk.scrolledtext.ScrolledText(app)
    logtext.pack(expand=True, fill=tk.BOTH)

    # bind logging handler
    h = marlowe_ui.logconsole.LogConsoleHandler(logtext)
    h.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(h)

    # initial logging message
    logger.setLevel(logging.INFO)
    logger.info('ml_post_ui is ready. Select input file to be expanded')

    app.mainloop()
