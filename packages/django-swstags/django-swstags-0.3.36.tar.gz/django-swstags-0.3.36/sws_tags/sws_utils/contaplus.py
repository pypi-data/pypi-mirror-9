
##### FUNCTION TO EXPORT CONTAPLUS ################

#!/usr/bin/env python
# -*- coding:utf-8 -*-


# import sys
# sys.path.insert(0, '../')
# import os
# os.environ['DJANGO_SETTINGS_MODULE'] = 'ooint.settings'
# from views import *




# from ooint import settings
# from billing.models import *
# from django.core.context_processors import csrf
# from ooint.settings import *

# from billing.models import VAT

from datetime import date, datetime, timedelta
import time



def addSpace(data_type,new_value):
	# type of data -->number N # CARACTER C # FECHA F # LOGICO L
	for d in data_type:
		if d[0] in new_value:
			if len(new_value[d[0]]) <= d[2]:
				a= len(new_value[d[0]])
				for i in range(a,d[2]):
					if d[1]=='C':
						new_value[d[0]] = new_value[d[0]] + ' '
					elif d[1] == 'N':
						new_value[d[0]] = ' '+ new_value[d[0]] 
					elif d[1] == 'N2':
						new_value[d[0]] = ' '+ new_value[d[0]] 
					elif d[1] == 'N6':
						new_value[d[0]] = ' '+ new_value[d[0]] 
					elif d[1] == 'F':
						new_value[d[0]] = ' '+ new_value[d[0]] 
					else:
						error = 'error'
						# print 'ERROR IN TYPE OF DATA',d[1]

	return new_value



def createFileContaplus(data_export):
	data_type_seat = [('Asien','N',6),
				('Fecha','F',8),
				('SubCta','C',12),
				('Contra','C',12),
				('PtaDebe','N2',16),
				('Concepto','C',25),
				('PtaHaber','N2',16),				
				('Factura','N',8),
				('Baseimpo','N2',16),
				('IVA','N2',5),
				('Recequiv','N2',5),	
				('Documento','C',10),
				('Departamento','C',3),
				('Clave','C',6),
				('Estado','C',1),				
				('Ncasado','N',6),
				('Tcasado','N',1),
				('Trans','N',6),
				('Cambio','N6',16),	
				('DebeME','N2',16),
				('HaberME','N2',16),
				('Auxiliar','C',1),
				('Serie','C',1),				
				('Sucursal','C',4),
				('CodDivisa','C',5),
				('ImpAuxME','N2',16),
				('MonedaUso','C',1),
				('EuroDebe','N2',16),
				('EuroHaber','N2',16),
				('BaseEuro','N2',16),
				('NoConv','L',1),				
				('NumeroInv','C',10),
				('Serie_RT','C',1),
				('Factu_RT','N',8),
				('Baseimpo_RT','N2',16),	
				('Baseimpo_RF','N2',16),	
				('Rectifica','L',1),
				('Fecha_RT','C',8),
				('NIC','C',1),
				('Libre','L',1),				
				('Libre2','C',6), # en la tabla esta mal
				('Interrump','C',1), # en la tabla esta mal
				('SegActiv','C',6),
				('SegGeog','C',6),	
				('Irect349','L',1),
				('Fecha_OP','F',8),
				('Fecha_EX','F',8),
				('Departa5','C',5),				
				('Factura10','C',10),
				('Porcen_Ana','N2',5),
				('Porcen_Seg','N2',5),
				('NumApunte','N',6),
				('EuroTotal','N2',16),
				('RazonSoc','C',100),
				('Apellido1','C',50),
				('Apellido2','C',50),				
				('TipoOpe','C',1),
				('nFacTick','N',8),
				('NumAcuIni','C',40),
				('NumAcuFin','C',40),	
				('TerIdNif','N',1),
				('TerNif','C',15),
				('TerNom','C',40),
				('TerNif14','C',9),				
				('TBienTran','L',1),
				('TBienCod','C',10),
				('TransInm','L',1),
				('Metal','L',1),	
				('MetalImp','N2',16),
				('Cliente','C',12),
				('OpBienes','N',1),
				('FacturaEx','C',40),				
				('TipoFac','C',1),
				('TipoIVA','C',1),
				('GUID','C',40),
				('L340','L',1),
				('MetalEje','N',4),
				('Document15','C',15),
				('ClientSup','C',12),
				('FechaSup','F',8),
				('ImporteSup','N2',16),
				('DocSup','C',40),
				('ClientePro','C',12),
				('FechaPro','F',8),
				('ImportePro','N2',16),
				('DocPro','C',40),
				('nClaveIRPF','N',2),
				# ('final_file','C',108),
				('new1','L',1),
				('new2','N',1),
				('new3','N',26),
				('new4','N',2),
				('new5','N',2),
				('new6','L',1),
				('new7','N2',24),
				('new8','N2',48),
				('new9','C',53),
			]

	data_type_account = [
				('Cod','C',12),
				('Titulo','C',40),	
				('Nif','C',15),
				('Domicilio','C',35),
				('Poblacion','C',25),
				('Provincia','C',20),	
				('CodPostal','C',5),
				('Divisa','L',1),
				('CodDivisa','C',5),
				('Documento','L',1),	
				('Ajustame','L',1),
				('TipoIVA','C',1),
				('Proye','C',9),
				('SubEquiv','C',12),	
				('SubCierre','C',12),
				('Linterrump','C',1),
				('Segmento','C',12),
				('TPC','N2',5),	
				('RecEquiv','N2',5),
				('Fax01','C',15),
				('Email','C',50),
				('TituloL','C',100),	
				('IdNif','N',1),
				('CodPais','C',2),
				('Rep14NIF','C',9),
				('Rep14Nom','C',40),
				('MetCobro','L',1),	
				('MetCobFre','L',1),
				('Suplido','L',1),
				('Provision','L',1),
				('IEsIRPF','L',1),	
				('nIRPF','N2',5),
				('nClaveIRPF','N',2),
				('IEsMod130','L',1),
				('IDeducible','L',1),	
				('New1','L',1),
				('New2','C',12),
				('New3','L',1),
				]


	if data_export['seat'] != None: 
		f = open(data_export['name_file_seat'],'w') 
		print 'data export accounting',data_export['seat']
		writeInFile(data_type_seat,data_export['seat'],f)

	if data_export['account'] != None: 
		f = open(data_export['name_file_account'],'w') 
		writeInFile(data_type_account,data_export['account'],f)

	# print 'CREATE FILE CONTAPLUS OK'



def writeInFile(data_type,new_values,f):
	
	class Contaplus:
		def __init__(self,data_type_seat,value,index):
			self.name  = data_type_seat[0]
			self.type = data_type_seat[1]
			self.len = data_type_seat[2]
			self.value = value
			self.index = index

	try:
		for new_value in new_values:
			new_value = addSpace(data_type,new_value) ## complete the new value with spaces

			data = []
			cont = 1
			for d in data_type:
				data.append(Contaplus(d,'0',cont));
				cont = cont+1
			for d in data:

				if d.name in new_value:

					if len(new_value[d.name]) > d.len:

						# print '*****WARNING--> too length in field ',d.name
						# print 'len--max',d.len
						# print 'len_value',len(new_value[d.name])
						sub_val = new_value[d.name][0:d.len]
						f.write(sub_val)						
					else:
						f.write(new_value[d.name])
				else:
					if d.type == 'C':
						for i in range(0,d.len):
							f.write(' ') 
					elif d.type == 'L':
						for i in range(0,d.len):
							f.write('F') 	

					elif d.type == 'F':
						for i in range(0,8):
							f.write(' ') 	


					elif d.type == 'N':
						value = '0'
						for i in range(1,d.len):
							value = ' '+value	
						f.write(value)
					elif d.type == 'N2':
						value = '0.00'
						for i in range(4,d.len):
							value = ' '+value	
						# print d.name,'----',value
						f.write(value)
					elif d.type == 'N6':
						value = '0.000000'
						for i in range(8,d.len):
							value = ' '+value	
						f.write(value)
					else:
						error = 'ERROR DISTINT VALUE'
						# print 'ERROR DISTINT VALUE'
			# print '-----------------',new_value			
			f.write('\r\n')
		f.write('')
		f.close()
	except e:
		error = e
		# print e


def readFile(name_file,list_import_book_account):

	data_type_account = [
		('Cod','C',12),
		('Titulo','C',40),	
		('Nif','C',15),
		('Domicilio','C',35),
		('Poblacion','C',25),
		('Provincia','C',20),	
		('CodPostal','C',5),
		('Divisa','L',1),
		('CodDivisa','C',5),
		('Documento','L',1),	
		('Ajustame','L',1),
		('TipoIVA','C',1),
		('Proye','C',9),
		('SubEquiv','C',12),	
		('SubCierre','C',12),
		('Linterrump','C',1),
		('Segmento','C',12),
		('TPC','N2',5),	
		('RecEquiv','N2',5),
		('Fax01','C',15),
		('Email','C',50),
		('TituloL','C',100),	
		('IdNif','N',1),
		('CodPais','C',2),
		('Rep14NIF','C',9),
		('Rep14Nom','C',40),
		('MetCobro','L',1),	
		('MetCobFre','L',1),
		('Suplido','L',1),
		('Provision','L',1),
		('IEsIRPF','L',1),	
		('nIRPF','N2',5),
		('nClaveIRPF','N',2),
		('IEsMod130','L',1),
		('IDeducible','L',1),	
		('New1','L',1),
		('New2','C',12),
		('New3','L',6),
	]



	fc1 = open(name_file,'rU')
	data = fc1.read()

	# for i in range(0,len(data)):
		# print data[i]

	list_book_account=[]

	dict_book_account = {}
	cont_local = 0
	cont_element = 0
	pepe = 0
	intro = False

	data_element = ''
	for j in range(0,len(data)):
		if cont_local == data_type_account[cont_element][2]:
			dict_book_account[str(data_type_account[cont_element][0])] = data_element
			# print str(data_type_account[cont_element][0]),'---',cont_element,'---',data_element
			# print data_element
			data_element = ''

			cont_local = 0
			cont_element = cont_element+1


		data_element = data_element + data[j]


		cont_local = cont_local+1


		if cont_element == 38:
			if dict_book_account['Cod'][0:3] in list_import_book_account:
				list_book_account.append(dict_book_account)
			dict_book_account = {}
			cont_element = 0
			pepe = pepe+1
			intro = True

		# if pepe == 10:
		# 	exit()


	return list_book_account
	# for i in range (0,len(list_book_account)):
	# 	print i,'--', list_book_account[i]['Cod']
	# 	print i,'--', list_book_account[i]['Titulo']

	# 	new_account_number = BookAccount()
	# 	new_account_number.account_number = list_book_account[i]['Cod']
	# 	new_account_number.description = list_book_account[i]['Titulo']
	# 	new_account_number.company_id = 1
	# 	new_account_number.account_number_id = 1
	# 	# new_account_number.account_type= BookAccountType.objects.get(name = request_data['account_type'] )
	# 	new_account_number.creation_date = date(date.today().year,date.today().month,date.today().day) 
	# 	# new_account_number.entity_type_object =  Client.objects.get(id = 1)

	# 	new_account_number.save()



	# print ' OKkkkkkkk',list_book_account



# readFile('sultan.txt')


def testerFile(name_file_checked,name_file_to_tester,tester_type):
	fc1 = open(name_file_checked,'rb')
	data1 = fc1.read()

	fc2 = open(name_file_to_tester,'rb')
	data2 = fc2.read()


	if tester_type == 'length':
		if len(data1) == len(data2):
			# print ' **** CHECK OK --> The file have the same length ***  ',len(data1)
			error = 'error'
		else: 
			error = 'errror'
			# print ' **** ERROR IN CHECK ******'
			# print '- Length file checked-->',len(data1)
			# print '- Length file to tester-->',len(data2)			


	else:
		first_error = False
		for i in range(0,len(data1)):
			if data1[i] !=data2[i]:
				if first_error == False:
					# print ' **** ERROR IN CHECK ******'
					# print 'Character in file 1 is {0} and in file 2 is {1}'.format(data1[i],data2[i])
					# print 'POSITION--->',i, 'VALUE---->',data2[i-100:i+100] 
					first_error = True

		if first_error == False:
			error = '**** CHECK OK****'
			# print '**** CHECK OK****'




def ImportBookAccountToContaplus(file_book_account,book_account_to_export,book_account_class,book_accounts_types):
	list_book_account = readFile(file_book_account,book_account_to_export)

	for i in range (0,len(list_book_account)):
		print list_book_account[i]['Cod']
		new_account_number = book_account_class()
		new_account_number.account_number = list_book_account[i]['Cod']
		new_account_number.description = list_book_account[i]['Titulo']
		new_account_number.company_id = 1
		new_account_number.account_number_id = 1

		for n in book_accounts_types:
			if str(n.prefix) == list_book_account[i]['Cod'][0:3]:
				new_account_number.account_type = n

		# new_account_number.account_type= book_accounts_types.objects.get(prefix = list_book_account[i]['Cod'][0:3] )
		new_account_number.creation_date = date(date.today().year,date.today().month,date.today().day) 
		# new_account_number.entity_type_object =  Client.objects.get(id = 1)
		try:
			new_account_number.save()
		except Exception,e:
			print e
			Error = 'Warning',e



############################ TEST FOR CHECK FUNCTION TO EXPORT CONTAPLUS ##################################


# def test():

# 	account_type = {}

# 	account_type['proveedores'] = 400
# 	account_type['clientes'] = 430
# 	account_type['venta'] = 705
# 	account_type['compra'] = 607
# 	account_type['iva_soportado'] = 472
# 	account_type['iva_repercutico'] = 477
# 	account_type['gasto_operacion'] = 626
# 	account_type['diferencias_negativas_cambio'] = 668
# 	account_type['diferencias_positivas_cambio'] = 768






# 	seat_tuples=[
# 		('1','20131223','Emision 1','430998001','','2','2420','0','E','1'),
# 		('1','20131223','Emision 1','705998001','','2','0','2000','E','1'),
# 		('1','20131223','Emision 1','477998021','430998001','2','0','420','E','1'),	
										
# 		('2','20131223','Recibo 1','607998021','','2','1000','0','E','1'),
# 		('2','20131223','Recibo 1','472998021','400998001','2','210','0','E','1'),	
# 		('2','20131223','Recibo 1','400998001','','2','0','1000','E','1'),
# 		('2','20131223','Recibo 1','477998021','400998001','2','0','210','E','1'),
										
# 		('3','20131223','Cobro 1','572998001','','2','2420','0','E','1'),
# 		('3','20131223','Cobro 1','430998001','','2','0','2420','E','1'),
										
# 		('4','20131223','Cobro 2','572998001','','2','2320','0','E','1'),
# 		('4','20131223','Cobro 2','430998001','','2','0','2420','E','1'),
# 		('4','20131223','Cobro 2','668998001','','2','100','0','E','1'),
										
# 		('5','20131223','Pago 1','400998001','','2','1021','0','E','1'),
# 		('5','20131223','Pago 1','572998001','','2','0','1021','E','1'),
										
# 		('6','20131223','Pago 2','400998001','','2','3000','0','E','1'),
# 		('6','20131223','Pago 2','573998001','','2','0','2800','E','1'),
# 		('6','20131223','Pago 2','768998001','','2','0','200','E','1'),
										
# 		('7','20131223','Pago 3','400998001','','2','2525','0','E','1'),
# 		('7','20131223','Pago 3','573998001','','2','0','2500','E','1'),
# 		('7','20131223','Pago 3','626998001','','2','0','25','E','1'),
# 	]

# 	seat_dict=[]

# 	for t in seat_tuples:
# 		seat = {}
# 		seat['Asien'] = t[0]
# 		seat['Fecha'] = t[1]
# 		seat['Concepto'] = t[2]
# 		seat['SubCta'] = t[3]
# 		seat['Contra'] = t[4]
# 		seat['MonedaUso'] = t[5]
# 		seat['EuroDebe'] = t[6]
# 		seat['EuroHaber'] = t[7]
# 		seat['NIC'] = 'E'
# 		seat['nFacTick'] = '1'
# 		seat_dict.append (seat)


# 	# seat_dict=[]
# 	# seat = {}
# 	# seat['Asien'] = '22'
# 	# seat['Fecha'] = '20131115'
# 	# seat['Concepto'] = 'Prueba asiento 22'
# 	# seat['SubCta'] = '400900004   ' #'607000000   '
# 	# seat['Contra'] = '400900003   ' #'400000032   '
# 	# seat['MonedaUso'] = '2'
# 	# seat['EuroDebe'] = '2319.87'
# 	# seat['EuroHaber'] = '0'
# 	# seat['NIC'] = 'E'
# 	# seat['nFacTick'] = '1'
# 	# seat_dict.append (seat)
	
# 	# seat = {}
# 	# seat['Asien'] = '22'
# 	# seat['Concepto'] = 'Prueba asiento el asiento mas largo del mundo'
# 	# seat['Fecha'] = '20131115'
# 	# seat['SubCta'] = '400900003   ' #'400000032   '
# 	# seat['Contra'] = '400900004   ' #'607000000   '
# 	# seat['EuroDebe'] = '0'
# 	# seat['EuroHaber'] = '2319.87'
# 	# seat['MonedaUso'] = '2'
# 	# seat['NIC'] = 'E'
# 	# seat['nFacTick'] = '1'
# 	# seat_dict.append (seat)

# 	# seat = {}
# 	# seat['Asien'] = '23'
# 	# seat['Concepto'] = 'Prueba asiento el asiento mas largo del mundo'
# 	# seat['Fecha'] = '20131115'
# 	# seat['SubCta'] = '400900004   ' #'607000000   '
# 	# seat['Contra'] = '400900003   ' #'400000032   '
# 	# seat['MonedaUso'] = '2'
# 	# seat['EuroDebe'] = '2319.87'
# 	# seat['NIC'] = 'E'
# 	# seat['nFacTick'] = '1'
# 	# seat_dict.append (seat)
	
# 	# seat = {}
# 	# seat['Asien'] = '23'
# 	# seat['Concepto'] = 'Prueba asiento 23'
# 	# seat['Fecha'] = '20131115'
# 	# seat['SubCta'] = '400900003   ' #'400000032   '
# 	# seat['Contra'] = '400900004   ' #'607000000   '
# 	# seat['MonedaUso'] = '2'
# 	# seat['EuroHaber'] = '2319.87'
# 	# seat['NIC'] = 'E'
# 	# seat['nFacTick'] = '1'
# 	# seat_dict.append (seat)


# 	account_tuples = [
# 		('572998001','Banco Euros','A23346789','c/ Maletines n 1','Nosedonde','Madrid','28027','Banco yo no robo','1','ES'),	
# 		('573998001','Banco Dolares','A45214862','c/ Comisiones n 25','Getafe','Madrid','28002','Banco dolares','1','ES'),
# 		('400998001','Proveedor A VOCES','A45896145','c/Pinganillo ','Madrid','Madrid','28002','','1','ES'),
# 		('430998001','Cliente Perico','A12312378','c/No me acuerdo 32 ','Madrid','Madrid','28002','','1','ES'),
# 		('705998001','Venta','','','','','','','1','ES'),
# 		('607998001','Compra','','','Madrid','Madrid','28002','','1','ES'),
# 		('472998021','Iva Soportado','','','','','','','1','ES'),
# 		('477998021','Iva Repercutido','','','Madrid','Madrid','28002','','1','ES'),
# 		('626998001','Gasto Operacion','',' ','Madrid','Madrid','28002','','1','ES'),
# 		('668998001','Diferencias negativas cambio','',' ','Madrid','Madrid','28002','','1','ES'),
# 		('768998001','Diferencias positivas cambio','',' ','Madrid','Madrid','28002','','1','ES'),

# 	]


# 	account_list=[]
# 	for t in account_tuples:
# 		account = {}
# 		account['Cod'] = t[0]
# 		account['Titulo'] = t[1]
# 		account['Nif'] = t[2]
# 		account['Domicilio'] = t[3]
# 		account['Poblacion'] = t[4]
# 		account['Provincia'] = t[5]
# 		account['CodPostal'] = t[6]  
# 		account['TituloL'] = t[7]
# 		account['IdNif'] = t[8]
# 		account['CodPais'] = t[9]  
# 		account_list.append (account)





# 	print account_list










# 	# account_list=[]
# 	# account = {}
# 	# account['Cod'] = '400900003'  
# 	# account['Titulo'] = 'DISTRIBCION NOMEMIRES'
# 	# account['Nif'] = 'A84835388'
# 	# account['Domicilio'] = 'C/ no me acuerdo ,23'
# 	# account['Poblacion'] = 'Villaralto	'
# 	# account['Provincia'] = 'Cordoba'
# 	# account['CodPostal'] = '14471'  
# 	# account['TituloL'] = 'La cuenta mas larga del mundo'
# 	# account['IdNif'] = '1'
# 	# account['CodPais'] = 'ES'  
# 	# account_list.append (account)

# 	# account = {}
# 	# account['Cod'] = '400900004'  
# 	# account['Titulo'] = 'TELECOMUNICACIONES A VOCES'
# 	# account['Nif'] = 'B86638989'
# 	# account['Domicilio'] = 'C/Todo en siliencio,22'
# 	# account['Poblacion'] = 'Guarroman 78'
# 	# account['Provincia'] = 'Cordoba' 
# 	# account['IdNif'] = '2'
# 	# account['CodPais'] = 'ES'  
# 	# account_list.append (account)



# 	data_export = {}
# 	data_export['seat'] = seat_dict
# 	data_export['account'] =account_list
# 	data_export['name_file_seat'] = 'test_seat_01.txt'
# 	data_export['name_file_account'] = 'test_account_01.txt'
# 	createFileContaplus(data_export)

# 	testerFile('seat_example.txt','test_seat_01.txt','length')# 'length' or 'character'
# 	# testerFile('account_example.txt','test_account_01.txt','le