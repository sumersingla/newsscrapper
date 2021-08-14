import requests
from bs4 import BeautifulSoup
import redis
from secrets import password
import datetime

class Scraper:
    def __init__(self, keywords):
        self.markup = requests.get('https://techcrunch.com/').text   #https://news.ycombinator.com/    class==storylink
        self.keywords = keywords

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll("a", {"class": "post-block__title__link"})
        self.saved_links = []
        for link in links:
            for keyword in self.keywords:
                if keyword in link.text:
                    self.saved_links.append(link)

    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        for link in self.saved_links:
            r.set(link.text, str(link))

    def email(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        links = [str(r.get(k)) for k in r.keys()]
        
        # email
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        # me == my email address
        # you == recipient's email address
        fromEmail = 'chillingbruhh@gmail.com'
        toEmail = 'sumersingla14@gmail.com'
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg["From"] = fromEmail
        msg["To"] = toEmail
        # Create the body of the message (a plain-text and an HTML version).
        html = """
            <h4> %s links you might find interesting today:</h4>
            
            %s
        """ % (len(links), '<br/><br/>'.join(links))

        # Record the MIME types of both parts - text/plain and text/html.
        mime = MIMEText(html, 'html')
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(mime)

        try:
            # Send the message via local SMTP server.
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(fromEmail, password)
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            mail.sendmail(fromEmail, toEmail, msg.as_string())
            mail.quit()
            print('Email sent!')
        except Exception as e:
            print('Something went wrong... %s' % e)

        # flush redis
        r.flushdb()

        
s = Scraper(['AMD', 'database', 'facebook', 'python', 'twitter', 'Indian', 'India', 'Amazon', 'Elon', 'C++', 'software'])
s.parse()
s.store()
if datetime.datetime.now().hour == 13:
    s.email()



    