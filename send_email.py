import smtplib
import encoder

smtp_host = "smtp-mail.outlook.com"
smtp_port = "587"
my_email = "go.sync@outlook.com"
my_password = "Fuckth3systemE@"


def send_user_email(user_id):
    type = "users"
    id = user_id
    encoded_id = encoder.encode(id)
    connection = smtplib.SMTP(smtp_host)
    connection.starttls()
    connection.login(user=my_email, password=my_password)
    connection.sendmail(from_addr=my_email, to_addrs="andrei_andreir96@yahoo.com",

                        msg=f"Subject:Welcome to Sync!\n\n"
                            f"Please login into this page: http://127.0.0.1:5000/register/?type={type}&id={encoded_id}")
    connection.close()
