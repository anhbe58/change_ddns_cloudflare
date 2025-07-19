import configparser, logging, datetime
import smtplib
import os

script_path = os.path.dirname(os.path.abspath(__file__))
config_file = "cfauth.ini"
log_file = "ipchanges.log"
config_path = os.path.join(script_path, config_file)
log_path = os.path.join(script_path, log_file)

# Reading the keys from the cfauth.ini file
config = configparser.ConfigParser()
config.read(config_path)
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

email_stmp_key = config.get('tokens', 'email_stmp_key')
email_send = config.get('tokens', 'email_send')

def send_email(currentactualip):
    for dest in config['email']:
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(email_send, email_stmp_key)
            SUBJECT="Home lab is ON, IP is {}".format(currentactualip)
            TEXT = """
    username: HoangAnh
    pass: hoanganh01

    username: freelance
    pass: freelance001            
    """
            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
            s.sendmail("sender_email_id", config['email'][dest], message)
            s.quit()
            logging.info(f"{now} An email has been sent successfully.")
        except:
            logging.info(f"{now} An exception occurred when sending mail.")