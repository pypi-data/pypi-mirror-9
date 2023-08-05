
#python standard library
import re
from abc import ABCMeta, abstractproperty

#this code
from baseclass import BaseClass
import oatbran as bran


class ExpressionBase(BaseClass):
    """
    An Abstract Base class for regular expression containers
    """
    __metaclass__ = ABCMeta
    def __init__(self):
        super(ExpressionBase, self).__init__()
        self._logger = None
        self._expression = None
        self._regex = None
        return

    @abstractproperty
    def expression(self):
        """
        :rtype: String
        :return: regular expression to match given input
        """
        return self._expression

    @property
    def regex(self):
        """
        A compiled version of the expression
        
        :rtype: re.RegexObject
        :return: compiled regex object
        """
        if self._regex is None:
            self._regex = re.compile(self.expression)
        return self._regex


class HumanExpression(ExpressionBase):
    """
    The Human Expression matches the human-readable iperf output
    """
    def __init__(self):
        super(HumanExpression, self).__init__()
        self._thread_column = None
        return

    @property
    def thread_column(self):
        """
        an expression for the thread-number column
        
        :return: the expression to match the thread column        
        """
        if self._thread_column is None:
            self._thread_column = (bran.L_BRACKET + bran.OPTIONAL_SPACES +
                                   bran.NAMED(n=ParserKeys.thread, e=bran.INTEGER) +
                                   bran.R_BRACKET)
        return self._thread_column
    
    @property
    def expression(self):
        """
        The regular expression for Human-Readable iperf output
        
        :rtype: String
        :return: regular expression to match iperf output
        """
        if self._expression is None:
            interval_column = (bran.NAMED(n=ParserKeys.start, e=bran.FLOAT) +
                               bran.DASH + bran.OPTIONAL_SPACES +
                               bran.NAMED(n=ParserKeys.end, e=bran.FLOAT) +
                               bran.SPACES + 'sec')
            transfer_column = (bran.NAMED(n=ParserKeys.transfer, e=bran.REAL)
                               + bran.SPACES
                               + bran.NAMED(n=ParserKeys.transfer_units,
                                            e=(bran.CLASS('GKM'))
                                            + bran.ZERO_OR_ONE + "Bytes"))
            bandwidth_column = (bran.NAMED(n=ParserKeys.bandwidth, e=bran.REAL) +
                                bran.SPACES + bran.NAMED(n=ParserKeys.units, e=bran.CLASS(e="GKM")
                                + bran.ZERO_OR_ONE + bran.GROUP( "bits" + bran.OR + "Bytes")) + "/sec")

            self._expression = bran.SPACES.join([self.thread_column, interval_column,
                                                 transfer_column, bandwidth_column])
            self.logger.debug('HumanExpression: {0}'.format(self._expression))
        return self._expression
# end class HumanExpression


class CsvExpression(ExpressionBase):
    """
    The Csv Expression holds the expression to match iperf's csv format
    """
    def __init__(self):
        super(CsvExpression, self).__init__()
        self._thread_column = None
        return

    @property
    def thread_column(self):
        """
        :return: the expression to match the thread id
        """
        if self._thread_column is None:
            self._thread_column = bran.NAMED(ParserKeys.thread, bran.NATURAL)
        return self._thread_column
    
    @property
    def expression(self):
        """
        :return: string regular expression to match csv-format
        """
        if self._expression is None:
            COMMA = ","
            timestamp = bran.NAMED(ParserKeys.timestamp, bran.INTEGER)
            sender_ip = bran.NAMED(ParserKeys.sender_ip, bran.IP_ADDRESS)
            sender_port = bran.NAMED(ParserKeys.sender_port, bran.INTEGER)
            receiver_ip = bran.NAMED(ParserKeys.receiver_ip, bran.IP_ADDRESS)
            receiver_port = bran.NAMED(ParserKeys.receiver_port, bran.INTEGER)

            start = bran.NAMED(ParserKeys.start, bran.FLOAT)
            end = bran.NAMED(ParserKeys.end, bran.FLOAT)
            interval = start + bran.DASH  + end
            transfer = bran.NAMED(ParserKeys.transfer, bran.INTEGER)
            bandwidth = bran.NAMED(ParserKeys.bandwidth, bran.INTEGER)
            self._expression = COMMA.join([timestamp,
                                               sender_ip,
                                               sender_port,
                                               receiver_ip,
                                               receiver_port,
                                               self.thread_column,
                                               interval,
                                               transfer,
                                               bandwidth])
            
        return self._expression

    @property
    def regex(self):
        """
        :return: compiled regular expression to match csv-format
        """
        if self._regex is None:
            self._regex = re.compile(self.expression)
        return self._regex
# end class CsvExpression


class CombinedExpression(ExpressionBase):
    """
    A Combined expression matches either case (but doesn't break up the line).

    This is intended for implemetations that set the expression type on first match.
    """
    @property
    def expression(self):
        """
        :rtype: String
        :return: regular expression that matches both formats
        """
        if self._expression is None:
            thread_column = (bran.L_BRACKET + bran.OPTIONAL_SPACES +
                             bran.INTEGER +
                             bran.R_BRACKET)
            interval_column = (bran.FLOAT +
                               bran.DASH + bran.OPTIONAL_SPACES +
                               bran.FLOAT +
                               bran.SPACES + 'sec')
            transfer_column = (bran.REAL
                               + bran.SPACES + bran.CLASS('GKM')
                               + bran.ZERO_OR_ONE + "Bytes")
            bandwidth_column = (bran.REAL +
                                bran.SPACES + bran.CLASS(e="GKM")
                                + bran.ZERO_OR_ONE + bran.GROUP( "bits" + bran.OR + "Bytes") + "/sec")
            human = bran.NAMED(n=ParserKeys.human,
                               e=bran.SPACES.join([thread_column,
                                                   interval_column,
                                                   transfer_column,
                                                   bandwidth_column]))
            COMMA = ","
            csv = bran.NAMED(n=ParserKeys.csv,
                             e=COMMA.join([bran.NOT(COMMA)] * 5 + [bran.INTEGER]
                                          + [bran.NOT(COMMA)] * 3))

            self._expression = human + bran.OR + csv
        return self._expression
    
    @property
    def regex(self):
        """
        :return: compiled regex that matches both formats
        """
        if self._regex is None:
            self._regex = re.compile(self.expression)
        return self._regex
# end class CombinedExpression


class ParserKeys(object):
    """
    A holder of the keys to the groupdict
    """
    __slots__ = ()
    units = "units"
    thread = "thread"
    start = "start"
    end = "end"
    transfer = "transfer"
    transfer_units = 'transfer_units'
    bandwidth = 'bandwidth'

    #csv-only
    timestamp = "timestamp"
    sender_ip = "sender_ip"
    sender_port = "sender_port"
    receiver_ip = "receiver_ip"
    receiver_port = "receiver_port"

    # combined
    human = "human"
    csv = "csv"
# end class ParserKeys
