import smtplib
import asyncio


class EmailNotificator:
    def __init__(self, host, port, login, password, receiver, sender_name, use_ssl, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.login = login
        self.password = password
        self.receiver = receiver
        self.sender_name = sender_name

    @asyncio.coroutine
    def send(self, text, subject='', sender_name=None):
        server = yield from self._loop.run_in_executor(
            None, smtplib.SMTP, self.host, int(self.port))

        if self.use_ssl:
            yield from self._loop.run_in_executor(None, server.starttls)

        to = self.receiver
        sender_name = sender_name or self.sender_name
        server.login(self.login, self.password)
        from_mail = '{} <{}>'.format(sender_name, self.login)

        header = 'To: {}\nFrom: {}\nSubject:{}\n'.format(to, from_mail, subject)
        msg = '{}\n{}\n\n'.format(header,text)
        yield from self._loop.run_in_executor(
            None, server.sendmail, from_mail, to, msg)
