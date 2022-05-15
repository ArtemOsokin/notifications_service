import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridMailer:

    sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

    def send_mail(self, sender, recipient, subj, msg_content):
        print("MAILER STUB")
        # return
        mail = Mail(from_email=sender,
                    to_emails=recipient,
                    subject=subj,
                    html_content=msg_content)
        response = self.sg.send(mail)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)