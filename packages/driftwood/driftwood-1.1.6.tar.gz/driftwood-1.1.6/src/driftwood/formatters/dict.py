import logging

class DictFormatter(logging.Formatter):
    """Used for formatting log records into a dict."""
    def __init__(self, *args, regular_attrs=None, extra_attrs=[], **kwargs):
        """
        :param list regular_attrs: A list of strings specifying built-in python
            logging args that should be included in each output dict.
            If not specified, all args will be used.  Setting to an empty list
            will disable regular args.
        :param list extra_attrs: A list of strings specifying additional
            arguments that may exist on the log record instances and
            should be included in the messages.
        """
        super().__init__(*args, **kwargs)
        if regular_attrs == None:
            regular_attrs = ["name","levelno","levelname","pathname","filename","module","lineno",
                "funcName","created","asctime","msecs","relativeCreated","thread","threadName",
                "process"]
        self.useful_attrs = regular_attrs + extra_attrs

    def format(self, record):
        """
        Formats a log record into a dictionary using the arguments given to __init__.
        """
        message = super().format(record)
        msg_dict = {}
        for attr in self.useful_attrs:
            if hasattr(record, attr):
                msg_dict[attr] = getattr(record, attr)
        msg_dict["message"] = message
        return msg_dict
