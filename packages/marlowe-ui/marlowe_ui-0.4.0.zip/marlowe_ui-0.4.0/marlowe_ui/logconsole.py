import tkinter as tk
import tkinter.scrolledtext

import logging


def getLogConsoleWindow(name):
    """create logging window, which is available by
    logging.getLogger(name)  (or name + .suffix)
    returns toplevel window object
    """
    logger = logging.getLogger(name)

    logwin = tk.Toplevel()
    # disable 'WM_DELETE_WINDOW' but iconify
    logwin.protocol('WM_DELETE_WINDOW', lambda: logwin.iconify())

    logtext = tkinter.scrolledtext.ScrolledText(logwin)
    h = LogConsoleHandler(logtext)

    # expose console.widget to Toplevel window
    logtext.pack(expand=True)

    # register handler and formatter
    h.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(h)

    return logwin


# from http://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget
class LogConsoleHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self, record):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        self.widget.insert(tk.END, self.format(record) + '\n')
        self.widget.see(tk.END)  # Scroll to the bottom
        self.widget.config(state='disabled')

if __name__ == '__main__':
    app = tk.Tk()

    # set default logging level
    logging.basicConfig(level=logging.NOTSET)

    logwin = getLogConsoleWindow('logconsole')

    logger = logging.getLogger('logconsole.sub')

    def action():
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warning message')
        logger.error('error message')
        logger.critical('critcal message')

        logwin.deiconify()

    tk.Button(app, text='output to logconsole', command=action).pack()

    app.mainloop()
