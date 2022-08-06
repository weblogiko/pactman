import logging

from colorama import Fore, Style

from .paths import format_path

log = logging.getLogger(__name__)


class Result:
    PASS = True
    FAIL = False
    success = PASS

    def start(self, message):
        self.success = self.PASS

    def end(self):
        pass

    def warn(self, message):
        raise NotImplementedError()

    def fail(self, message, path=None):
        raise NotImplementedError()  # pragma: no cover


class LoggedResult(Result):
    def start(self, interaction):
        super().start(interaction)
        log.info(f"Verifying {interaction}")

    def warn(self, message):
        log.warning(f" {message}")

    def fail(self, message, path=None):
        self.success = self.FAIL
        log.warning(f" {message}")
        return not message


class PytestResult(Result):  # pragma: no cover
    def __init__(self, *, level=logging.WARNING):
        self.records = []
        self.level = level
        self.current_consumer = None

    def start(self, interaction):
        super().start(interaction)
        log = logging.getLogger("pactman")
        log.handlers = [self]
        log.setLevel(logging.DEBUG)
        log.propagate = False
        self.records[:] = []

    def handle(self, record):
        self.records.append(record)

    def fail(self, message, path=None):
        from _pytest.outcomes import Failed

        __tracebackhide__ = True
        self.success = self.FAIL
        if path:
            message += f" at {format_path(path)}"
        log.error(message)
        raise Failed(message) from None

    def warn(self, message):
        log.warning(message)

    def results_for_terminal(self):
        for record in self.records:
            if record.levelno > logging.WARN:
                yield record.msg, dict(red=True)
            elif record.levelno > logging.INFO:
                yield record.msg, dict(yellow=True)
            else:
                yield record.msg, {}


class CaptureResult(Result):
    def __init__(self, *, level=logging.WARNING):
        self.messages = []
        self.level = level
        self.current_consumer = None

    def start(self, interaction):
        super().start(interaction)
        log = logging.getLogger("pactman")
        log.handlers = [self]
        log.setLevel(logging.DEBUG)
        self.messages[:] = []
        if self.current_consumer != interaction.pact.consumer:
            print(f"{Style.BRIGHT}Consumer: {interaction.pact.consumer}")
            self.current_consumer = interaction.pact.consumer
        print(f'Request: "{interaction.description}" ... ', end="")

    def end(self):
        if self.success:
            print(f"{Fore.GREEN}PASSED")
        else:
            print(f"{Fore.RED}FAILED")
        if self.messages:
            print((Fore.RESET + "\n").join(self.messages))

    def warn(self, message):
        log.warning(message)

    def fail(self, message, path=None):
        self.success = self.FAIL
        if path:
            message += f" at {format_path(path)}"
        log.error(message)
        return not message

    def handle(self, record):
        color = ""
        if record.levelno >= logging.ERROR:
            color = Fore.RED
        elif record.levelno >= logging.WARNING:
            color = Fore.YELLOW
        self.messages.append(f" {color}{record.msg}")
