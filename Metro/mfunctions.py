import smtplib 
from email.message import EmailMessage

def metro_send_mail(user, code):
	'''
	Parameters : Recipient Object, ForgotCode Code.
	Return : None

	This function sends via smtp an email using gmail's api.
	'''
	EmailAdd = "metroofficialreply@gmail.com" #senders Gmail id over here
	Pass = "GMAILPASSWORD" #senders Gmail's Password over here 
	messagefunny = f"Hello {user.username}!"

	msg = EmailMessage()
	msg['Subject'] = 'Subject of the Email' # Subject of Email
	msg['From'] = EmailAdd
	msg['To'] = 'byzeintrove@gmail.com' # Reciver of the Mail
	msg.set_content(messagefunny) # Email body or Content

	#### >> Code from here will send the message << ####
	with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp: #Added Gmails SMTP Server
			smtp.login(EmailAdd,Pass) #This command Login SMTP Library using your GMAIL
			smtp.send_message(msg) #This Sends the message