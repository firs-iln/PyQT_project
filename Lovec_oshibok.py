def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    PyQt5.QtWidgets.QMessageBox.critical(None, 'Error', text)
    quit()

sys.excepthook = log_uncaught_exceptions


#  впиши после импортов и наслаждайся