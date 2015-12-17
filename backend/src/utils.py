import argparse
import logging
import datetime
import py
import requests
import sys

log = logging.getLogger(__name__)

from config import MAILGUN_API_KEY

def send_email_error_report(subject, body):

	log.info('Sending error report via e-mail...')

	excinfo = py.code.ExceptionInfo()
	info = str(excinfo.getrepr(showlocals=True)) + "\n\n"

	return requests.post(
        "https://api.mailgun.net/v3/sandbox9ac9162e2fc54d83bbaf813ac042be80.mailgun.org/messages",
        auth=(
	        "api",
	        MAILGUN_API_KEY
        ),
        data={
	        "from": "Mailgun Sandbox <postmaster@sandbox9ac9162e2fc54d83bbaf813ac042be80.mailgun.org>",
	        "to": "Someone Who Cares <admin@windlogger.se>",
	        "subject": subject,
	        "text": info
        }
    )


def prune_old_samples(days=31):

	import sqlite3 as lite

	time_limit = datetime.datetime.utcnow() - datetime.timedelta(days=days)
	time_str = time_limit.strftime('%Y-%m-%d')

	def count_samples(cur):
		cur.execute("SELECT count(*) FROM samples WHERE date_reported < '{}'".format(
			time_str))
		data = cur.fetchone()
		print 'Samples to prune: {}'.format(data[0])

	def prune_samples(cur):
		cur.execute("DELETE FROM samples WHERE date_reported<'{}'".format(
			time_str
		))
		cur.execute("VACUUM")
		cur.execute("SELECT count(*) FROM samples".format(
			time_str
		))
		data = cur.fetchone()
		print 'Samples remaining: {}'.format(data[0])

	con = None
	try:
		con = lite.connect('data.db')
		cur = con.cursor()
		count_samples(cur)
		prune_samples(cur)

	except lite.Error, e:
		print "Error %s:" % e.args[0]
		sys.exit(1)

	finally:
		if con:
			con.close()


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'mode',
		help='Operation to run',
		choices=[
			'prune-old-samples',
		])
	parser.add_argument(
		'days',
		help='Keep samples younger than X days',
		type=int
	)

	args = parser.parse_args()

	if args.mode == 'prune-old-samples':
		prune_old_samples(args.days)

