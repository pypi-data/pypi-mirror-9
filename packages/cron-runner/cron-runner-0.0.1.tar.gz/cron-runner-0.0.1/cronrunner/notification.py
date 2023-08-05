from base import Base
import registry


class Notification(Base):
    log = None
    config = None

    def __init__(self, log):
        super(Notification, self).__init__()
        self.log = log
        self.jobname = self.log.job.name

    def send(self):
        self.config = registry.config.get("notifications")

        if self.config["hubot"]["enabled"]:
            self._send_to_hubot()

        if self.config["email"]["enabled"]:
            self._send_to_email()

    def _send_to_hubot(self):
        self.debug("hubot notification enabled")

        import requests

        url = "%s/%s" % (self.config["hubot"]["url"], self.config["hubot"]["room"])
        message = "*Cron '%s' on _%s_ has status _%s_*\n>Started at: %s\n>Ended at: %s\n>Runtime: %s" % (
            self.log.job.name, self.log.server, self.log.status.upper(), self.log.starttime, self.log.endtime,
            str(self.log.endtime - self.log.starttime))
        headers = {"content-type": "application/x-www-form-urlencoded"}

        self.debug("hubot url: %s" % self.config["hubot"]["url"],
                   "send message to room: %s" % self.config["hubot"]["room"])

        try:
            requests.post(url, data="message=%s" % message, headers=headers)
        except requests.ConnectionError, e:
            self.logger.error("unable to connect to Hubot, %s" % e)
        except requests.HTTPError, e:
            self.logger.error("HTTP error, %s" % e)

    def _send_to_email(self):
        self.debug("email notification enabled")

        import smtplib
        from email.mime.text import MIMEText

        mail_from = "cron-runner@%s" % self.log.server
        mail_to = self.config["email"]["address"]
        mail_data = [
            "CRON %s\n" % self.log.status.upper(),
            "name: %s" % self.log.job.name,
            "command: %s" % self.log.job.command,
            "server: %s" % self.log.server,
            "started at: %s" % str(self.log.starttime),
            "ended at: %s" % str(self.log.endtime),
            "runtime: %s" % str(self.log.endtime - self.log.starttime),
            "return code: %s" % str(self.log.returncode),
            "\noutput:",
            "-" * 80,
            "%s" % str(self.log.output),
            "\nerror:",
            "-" * 80,
            "%s" % str(self.log.error),
        ]

        msg = MIMEText("\n".join(mail_data))
        msg["From"] = mail_from
        msg["To"] = mail_to
        msg["Subject"] = "CRON %s" % self.log.status.upper()

        self.debug("send email to: %s" % mail_to)

        try:
            mail = smtplib.SMTP(self.config["email"]["server"], 25)
            mail.starttls()
            mail.sendmail(mail_from, mail_to, msg.as_string())
            mail.quit()
        except smtplib.SMTPConnectError, e:
            self.logger.error("unable to connect to smtp server, %s" % e)
        except smtplib.SMTPException, e:
            self.logger.error("SMTP error, %s" % e)
