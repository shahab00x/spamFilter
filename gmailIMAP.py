import imaplib, re
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login('spam.iut', 'getalifegmail')
unreadCount = re.search("UNSEEN (\d+)", conn.status("INBOX", "(UNSEEN)")[1][0]).group(1)

conn.select()
typ, data = conn.search(None, 'ALL')
#for num in data[0].split():
typ, data = conn.fetch(1, '(RFC822)')
print 'Message %s\n%s\n' % (1, data[0][1])
conn.close()
conn.logout()