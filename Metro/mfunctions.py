import smtplib 
from email.message import EmailMessage

#This file contains custom built functions for the Metro2.0 project

def metro_send_mail(user, code):
	'''
	Parameters : Recipient Object, ForgotCode Code.
	Return : None

	This function sends via smtp an email using gmail's api.
	'''
	EmailAdd = "metroofficialreply@gmail.com" #senders Gmail id over here
	Pass = "metropassword343" #senders Gmail's Password over here 
	metro_message = f"Hello {user.username}, Your password reset code is : {code} . This Code will expire in the next 3 days. If you did not issue this request please contact the support team."

	msg = EmailMessage()
	msg['Subject'] = 'Metro Password Recovery' # Subject of Email
	msg['From'] = EmailAdd
	msg['To'] = user.email # Reciver of the Mail
	msg.set_content(metro_message) # Email body or Content

	#### >> Code from here will send the message << ####
	with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp: #Added Gmails SMTP Server
			smtp.login(EmailAdd,Pass) #This command Login SMTP Library using your GMAIL
			smtp.send_message(msg) #This Sends the message