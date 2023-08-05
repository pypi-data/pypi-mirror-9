#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
'''
messages.py

Processes messages utility library

Created by SWS on 2012-09-11.
Copyright (c) 2012 StoneWorkSolutions. All rights reserved.
'''
from django.conf import settings
import json
import logging
import re
import redis
import traceback
try:
	from stoneauth.middlewares import StoneThreadLocal as ThreadLocal
except:
	from django_tools.middlewares import ThreadLocal
# import ooint.settings

logger = logging.getLogger('sws-tags')

def processErrorsForm(form):
	
	message = ''
	messages = []

	for field in form:

		if field.errors:
			message = re.sub('</(.*)>', '', unicode(str(field.errors), 'utf-8'))
			message = re.sub('<(.*)>', '', message)
			message = field.html_name + ': ' + message
			messages.append(message)

	return messages


# ThreadLocal.get_current_user()
# si necesitaras toda la request..
# ThreadLocal.get_current_request()
	
def processMessages(message, typeMessage, timeOut=10000):

	msg = {}

	def getTraceBackInfo():
		info = inspect.stack()[2][3]
		return info 
		# print 'f_back',inspect.frame().f_back
		# mod = inspect.getmodule(frm[0])
		# print '[%s] %s' % (mod.__name__, msg)
	
	called_from_view = getTraceBackInfo()

	if typeMessage == 'error':
		try:
			logger.error(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		error = (message, timeOut)
		msg['error'] = error

	elif typeMessage == 'warning':
		try:
			logger.warning(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		warning = (message, timeOut)
		msg['warning'] = warning

	elif typeMessage == 'success':
		try:
			logger.info(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		success = (message, timeOut)
		msg['success'] = success

	elif typeMessage == 'info':
		try:
			logger.info(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		info = (message, timeOut)
		msg['info'] = info

	return msg

# Send message to the specific channel
# Parametres: 
# 	name channel (session_id or settings.CHANNEL_GLOBAL_MESSAGES)
# 	text message
# 	level (info, warning,error or debug)
# 	time visible
import inspect

def sendMessages(channel=settings.CHANNEL_GLOBAL_MESSAGES,message='No messages',level='broadcast',time=5000):
	cr = redis.Redis(settings.REDIS_IP,db=settings.REDIS_DB)
	message={"message":message,"level":level,"time":time}
	cr.publish(channel,json.dumps(['user_message',message]))

	if level == 'error':
		try:
			logger.error(' channel: '+channel+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
	elif level == 'warning':
		try:
			logger.warning(' channel: '+channel+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
	elif level == 'success':
		try:
			logger.info(' channel: '+channel+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
	elif level in ('info','broadcast'):
		try:
			logger.info(' channel: '+channel+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass

	return True

def sendEvent(channel=settings.CHANNEL_GLOBAL_MESSAGES,event='',data=''):

	cr = redis.Redis(settings.REDIS_IP,db=settings.REDIS_DB)
	cr.publish(channel,json.dumps([event,data]))

	try:
		logger.debug('New event\n-Channel: {0}\n-User: {1}\n-Event: {2}\n-Data: {3}'.format(channel,ThreadLocal.get_current_user(),event,data))
	except:
		pass

	return True

def sendProgressBarEvent(channel=None, view_name='', value='', message='', error=False):
	sendEvent(channel,'progressbar',{'view_name':view_name,'value':value,'message':message, 'error': error})	

def sendBubbleNotificationEvent(channel=None, view_name='', value='', mode='add'):
	sendEvent(channel,'bubblenotification',{'view_name':view_name,'value':value,'mode':mode})	

def sendBubbleNotificationBlinkEvent(channel=None, view_name=''):
	sendEvent(channel,'bubblenotificationblink',{'view_name':view_name})	


def sendDashboardEvent(channel=None, data=''):
	sendEvent(channel,'dashboard',{'data':data})	



def swslog(typeMessage,message,e):

	def getTraceBackInfo():
		info = inspect.stack()[2][3]
		return info 
	
	called_from_view = getTraceBackInfo()

	if typeMessage == 'error':
		try:
			logger.error(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE ERROR: '+message+ ' EXCEPTION: {0}'.format(traceback.format_exc()))		
			# logger.error('*FUNCTION: '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE ERROR: '+message)
			# logger.error('-----EXCEPTION: {0}'.format(traceback.format_exc()))

		except:
			pass

	elif typeMessage == 'warning':
		try:
			logger.warning(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE WARNING: '+message+ ' EXCEPTION: {0}'.format(traceback.format_exc()))
		except:
			pass

	elif typeMessage == 'success':
		try:
			logger.info(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE SUCCES: '+message+ 'EXCEPTION: {0}'.format(traceback.format_exc()))
		except:
			pass

	elif typeMessage == 'info':
		try:
			logger.info(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE INFO: '+message+ 'EXCEPTION: {0}'.format(traceback.format_exc()))
		except:
			pass

