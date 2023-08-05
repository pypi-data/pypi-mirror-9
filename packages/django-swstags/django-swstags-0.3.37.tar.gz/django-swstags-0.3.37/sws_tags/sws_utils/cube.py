# import olap.xmla.xmla as xmla
# import time
# import simplejson
# import types
# from suds import WebFault
import ujson
# import types
# import pytz
# from types import *
# import re
# import string
from datetime import  datetime, timedelta#,date

from pytz import timezone as timezonepytz
# import time
# import sys,traceback
from django.utils.datastructures import SortedDict
# from django_tools.middlewares import ThreadLocal



# import collections
# import ordereddict
from ordereddict import OrderedDict


from sws_tags.sws_utils.messages import *
from sws_tags.sws_utils.cube_utils import *
from sws_tags.sws_utils.date import *
from sws_tags.sws_utils.__init__ import *


def simboloYvalorTZ(date):
    ##extrae de objeto del tipo datetime el valor y signo de la franja horaria.
    date_str = str(date)

    try:
        if (date_str.find('+')>-1):
            tz=date_str[date_str.find('+')+1:]
            tz=int(tz[:tz.find(':')])
            simbolo='+'
        else:
            tz=date_str[date_str.find(' ')+1:]
            tz=tz[tz.find('-')+1:]
            tz=int(tz[:tz.find(':')])
            simbolo='-'
    except:
        simbolo='+'
        tz=0
    return simbolo,tz

def compruebaFranjaHoraria2(dates,actual_tz_request,time_zone):
    
    madrid = timezonepytz(time_zone)
 
    ##Obtenemos la franja horario de cada fecha para el time zone del settings , por separado simbolo y valor.
    from_date=madrid.localize(datetime(int(dates[0][0:4]), int(dates[0][4:6]), int(dates[0][6:8]),int(dates[0][8:10]),int(dates[0][10:12]) ))    
    from_simbolo,from_tz=simboloYvalorTZ(from_date)
   
    to_date=madrid.localize(datetime(int(dates[1][0:4]), int(dates[1][4:6]), int(dates[1][6:8]),int(dates[1][8:10]),int(dates[1][10:12]) ))
    to_simbolo,to_tz=simboloYvalorTZ(to_date)
    
    actual_date= madrid.localize(datetime.now())
    actual_simbolo,actual_tz=simboloYvalorTZ(actual_date) 
   
    ##Con los valoes obtenidos anteriormente vemos si la fecha consultada tiene una franja horaria diferente a la actual, si es asi procedemos a cambiar las fechas
    if (actual_tz!=to_tz):
        if (to_tz==from_tz):

            diferencia=(int(actual_simbolo+str(actual_tz))-int(from_simbolo+str(from_tz)))*(-1)
            
            from_date=from_date-timedelta(hours=diferencia)
            to_date=to_date-timedelta(hours=diferencia)
                        
    ##Ponemos estas fechas que hemos conseguido en formato string solo con numeros.
    string_date_to=str(to_date)
    string_date_to=string_date_to[:string_date_to.find('+')]
    string_date_to=string_date_to.replace(' ','').replace('-','').replace(':','')

    string_date_from=str(from_date)
    string_date_from=string_date_from[:string_date_from.find('+')]
    string_date_from=string_date_from.replace(' ','').replace('-','').replace(':','')


    return string_date_from,string_date_to

def preCompruebaFranjaHoraria (part_where,actual_tz,time_zone):
    tiempo={'Time':False,'Date':False}
    for i in part_where:
        if i[0]in tiempo:
            tiempo[i[0]]=i
            dim_time=i
    
    aux_fecha0,aux_fecha1=compruebaFranjaHoraria2(part_where[dim_time],actual_tz,time_zone)

    part_where_aux_fechas = {}
    for i in part_where:
        if i == dim_time:
            part_where_aux_fechas[i]=(aux_fecha0,aux_fecha1)
        else:
            part_where_aux_fechas[i]=part_where[i]

    part_where=part_where_aux_fechas
    
    return part_where

def modifyNameBddCubes(name_bbdd,request_data):
    
    if name_bbdd[0]=='ing' or name_bbdd[0]=='sultan':
        
        yearFrom = request_data['from_calldate'].strftime("%Y-%m-%d %H:%M:%S")[0:4]
        yearTo = request_data['to_calldate'].strftime("%Y-%m-%d %H:%M:%S")[0:4]

        monthFrom = request_data['from_calldate'].strftime("%Y-%m-%d %H:%M:%S")[5:7]
        # monthTo = request_data['to_calldate'].strftime("%Y-%m-%d %H:%M:%S")[5:7]
        
        if (yearTo==yearFrom):
            year=yearFrom
        else:
            if int(monthFrom)>=10 :
                year=yearTo
            else:
                year=0
        
        for i in range(len(name_bbdd)):
           
            name_bbdd[i]=name_bbdd[i]+str(year)
    # print '--++ '*100
    # print name_bbdd
    return name_bbdd

def reorderColCube(col_cube,data_order):
    col_cube_aux=[]
    if col_cube:
        if data_order in col_cube:
            col_cube.remove(data_order)
            col_cube=sorted(list(set(col_cube)))
            col_cube_aux.append(data_order)
            for i in col_cube:
                col_cube_aux.append(i)

            return col_cube_aux
        else:
            return col_cube
    return col_cube


def add_MDX_redis(ide,value,r,seconds):            
            
    return r.set(ide+'_MDXS',value,seconds)
    
def get_MDXS_redis(ide,r):

    value = eval(r.get(ide+'_MDXS'))
    
    return value
def is_MDXS_Added_redis(ide,r):                                                                                    
    return not (r.get(ide+'_MDXS') == None)

def segundosHastaY5oEnPunto(minute,seconds):
    if len(str(minute))==1:
        aux=str(minute).zfill(2)
    else:
        aux=str(minute)

    digit1=int(aux[1])
    digit0=int(aux[0])

    if digit1<5:
        digit1=5
    else:
        digit1=0
        digit0=digit0+1

    return ((int(str(digit0)+str(digit1))-minute)*60)-seconds





def requestCube(ip_connect,name_bbdd,name_cube,col_cube,med_cube,request_data,ifDate,dimension_filters,database_cube_dict,total_data = False,where_tupla=('Date','Id','Id'),request_date_previous = False,complete_name=False,format_cube=False,n_c=[],time_zone="",redis=""):
    

    # name_carrier=''
    if 'cube_config' in request_data :
        cube_config=request_data['cube_config']
        ip_connect=cube_config['cube_ip']
        name_bbdd=[cube_config['cube_db']]
        name_cube=request_data['cube_name']
        # name_carrier= name_bbdd[0][name_bbdd[0].index('carrier_')+8:]+'_'
        
        
    
    cube=CUBE()
    
    mdx_class=MDX()
    
    # name_bbdd=modifyNameBddCubes(name_bbdd,request_data)    
    
    
    cube.connect(ip_connect,name_bbdd,n_c,redis) 
    exclude_rows={}
    where={}
    data_order = ''
    part_order={}
    mdx=''
    
    
    part_where ={}
    part_where = filterWhere(dimension_filters,request_data,database_cube_dict)
    for i in part_where:
        where[i]=part_where[i]

    
    if ifDate==True:
       
        if request_date_previous == False:
            where[where_tupla]=(formatDateCube(request_data ['from_Date']),formatDateCube(request_data ['to_Date']))
        else:
            where[where_tupla]=(formatDateCube(request_data ['from_Date_previous']),formatDateCube(request_data ['to_Date_previous']))          
    
   
    sord = request_data['sord'].upper()
   
    sord = 'B'+sord
    for i in col_cube:
        if i[0] == 'Date':
            dato=i[1]
        else:
            dato=i[0]
        if request_data['sidx'] == dato:
            data_order= i

    for i in med_cube:
        if request_data['sidx'] == i[1]:
            data_order= i
            

    col_cube = namesColCube(col_cube)

    data_order = namesColCube(data_order)

    
    part_order[data_order]=sord
    
    # print 'where antes',where
    # where=preCompruebaFranjaHoraria(where,request_data['django_timezone'],time_zone)
    # print 'where despues', where    
    

    col_cube=reorderColCube(col_cube,data_order)


    key=name_bbdd[0]+'MDXS_'+str(col_cube)+str(exclude_rows)+str(med_cube)+str(name_cube)+str(where)+str(part_order)+str(name_bbdd)+str(ip_connect)+str(format_cube)

    
    minute=datetime.now().minute
    second=datetime.now().second
    seconds=segundosHastaY5oEnPunto(minute,second)
    
    if (is_MDXS_Added_redis(name_bbdd[0],redis)):
        MDXS=get_MDXS_redis(name_bbdd[0],redis)
    else:
        MDXS={}



    if not (key in  MDXS.keys()):
        
        mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where,part_order=part_order) #ASC or DESC  ('measure','calls')
        
        # print 'MDX',mdx
        res=cube.launch_query(mdx)
        # print ' '*30
        # print res
        
        grid=Salida_Grid()
      
        if format_cube:
        
            json_data=grid.result_to_json(cube,res,database_cube_dict,False,request_data ['row_num'],request_data['page'],total_data,complete_name,format_cube,col_cube)
        
            mdx_total='select ([Client].[Client]) on rows,'+mdx_class.without_rows(mdx)
            
            
            res=cube.launch_query(mdx_total)

          
            json_data_footer=grid.result_to_json(cube,res,database_cube_dict,False,request_data ['row_num'],request_data['page'],total_data,complete_name,format_cube)

            json_data=json.loads(json_data)

            if json.loads(json_data_footer)['rows']:
                json_data['footerData']=json.loads(json_data_footer)['rows'][0]

                try:
                    json_data['footerData'][request_data['group_by']] = 'ALL'
                except:
                    pass


                try:
                    json_data['footerData'][request_data['and_by']] = 'ALL'
                except:
                    pass


            json_data=json.dumps(json_data)

        else:
        
            json_data=grid.result_to_json(cube,res,database_cube_dict,False,request_data ['row_num'],request_data['page'],total_data,complete_name,format_cube,col_cube)
        
       
        if data_order:

            if data_order in col_cube:
        
                if 'ASC' in sord:
                    json_data= ujson.loads(json_data)
                    json_data=reverseJson(json_data)                    
                    json_data=ujson.dumps(json_data)
        MDXS[key]=ujson.loads(json_data)
        add_MDX_redis(name_bbdd[0],MDXS,redis,seconds)
        

    else:
        
        json_data=MDXS[key]
        json_data=ujson.dumps(json_data)

  
    return json_data
def reverseJson(json_data):
    rows=json_data['rows']
    rows.reverse()
    json_data['rows']=rows
    return json_data
def reorderJson(json_data,col_cube,data_order):
    dim1=col_cube[0][0]+'*'+col_cube[0][1]
    dim2=col_cube[1][0]+'*'+col_cube[1][1]

    # rows=[]
   
    for row in json_data['rows']:
        value_dim1=row[dim1]
        value_dim2=row[dim2]
        row[dim1]=value_dim2
        row[dim2]=value_dim1

    if len(col_cube)>2:
        if data_order==col_cube[2]:
            dim1=col_cube[1][0]+'*'+col_cube[1][1]
            dim2=col_cube[2][0]+'*'+col_cube[2][1]

            # rows=[]
           
            for row in json_data['rows']:
                value_dim1=row[dim1]
                value_dim2=row[dim2]
                row[dim1]=value_dim2
                row[dim2]=value_dim1        

  
    return json_data

def requestCubeHighcharts(ip_connect,name_bbdd,name_cube,col_cube,med_cube,request_data,ifDate,dimension_filters,database_cube_dict,total_data = True,where_tupla=('Date','Id','Id'),request_date_previous = False, format_cube=False,n_c=[],time_zone="",redis=""):
    
    # name_carrier=''
    if 'cube_config' in request_data :
        cube_config=request_data['cube_config']
        ip_connect=cube_config['cube_ip']
        name_bbdd=[cube_config['cube_db']]
        name_cube=request_data['cube_name']
        # name_carrier= name_bbdd[0][name_bbdd[0].index('carrier_')+8:]+'_'
  
    cube=CUBE()
    mdx_class=MDX()
  
    # name_bbdd=modifyNameBddCubes(name_bbdd,request_data)    
    
    
    
    cube.connect(ip_connect,name_bbdd,n_c,redis) 
    exclude_rows={}
    where={}
    part_where = filterWhere(dimension_filters,request_data,database_cube_dict)

    for i in part_where:
        where[i]=part_where[i]
    
    if ifDate==True:
        if request_date_previous == False:
            where[where_tupla]=(formatDateCube(request_data['from_Date']),formatDateCube(request_data['to_Date']))
        else:
            where[where_tupla]=(formatDateCube(request_data['from_Date_previous']),formatDateCube(request_data['to_Date_previous']))

 
    new_col_cube=[]
    
    
    for i in col_cube:
        new_col_cube.append((i[0],i[1],i[2]))
    col_cube=new_col_cube
    
       
  
    
    request_data['int_all_time']=0

    
    key=name_bbdd[0]+'MDXS_'+str(col_cube)+str(exclude_rows)+str(med_cube)+str(name_cube)+str(where)+str(name_bbdd)+str(ip_connect)+str(request_data['button'])

    minute=datetime.now().minute
    second=datetime.now().second
    seconds=segundosHastaY5oEnPunto(minute,second)
    
    if (is_MDXS_Added_redis(name_bbdd[0],redis)):
        MDXS=get_MDXS_redis(name_bbdd[0],redis)
    else:
        MDXS={}

    if not (key in  MDXS.keys()):
        
    
        mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where) #ASC or DESC  ('measure','calls')

        # print 'MDX HIGHCHARTS',mdx
        
        # print ' '*30
        
        res=cube.launch_query(mdx)
       
        high=Salida_Highcharts()

        types = request_data['representation_type']

        if request_data['button']=='ALL':
            json_data=high.result_to_json(cube,res,types,dimension_v_name='Client',format_cube= format_cube)
        else:
            json_data=high.result_to_json(cube,res,types,dimension_v_name=request_data['button'],exclude=exclude_rows,format_cube= format_cube)

        MDXS[key]=json_data
        add_MDX_redis(name_bbdd[0],MDXS,redis,seconds)

    else:
        
        json_data=MDXS[key]
        

    return json_data

def requestCubeFilters(ip_connect,name_bbdd,name_cube,col_cube,med_cube,request_data,ifDate,dimension_filters,database_cube_dict=False,where_tupla=('Date','Id','Id'),n_c=[],time_zone="",redis=""):
    
    # name_carrier=''
    if 'cube_config' in request_data :
        cube_config=request_data['cube_config']
        ip_connect=cube_config['cube_ip']
        name_bbdd=[cube_config['cube_db']]
        name_cube=request_data['cube_name']
        # name_carrier= name_bbdd[0][name_bbdd[0].index('carrier_')+8:]+'_'

    cube=CUBE()
    mdx_class=MDX()
   
    # name_bbdd=modifyNameBddCubes(name_bbdd,request_data)    
    
  
    
    cube.connect(ip_connect,name_bbdd,n_c,redis) 
    
    where = filterWhere(dimension_filters,request_data,database_cube_dict)
    
    exclude_rows={}
   
    if request_data[request_data['types']]!='NULL':

        
        
        if request_data['types']=='Hangupcode2':
            key=('Hangupcode2','Long Description','Long Description')
        elif request_data['types']=='Hangupcode':
            key=('Hangupcode','Description','Description')
        else:
            key=(str(request_data['types']),'Id','Id')
        col_cube.append(key)
        
       
        exclude_rows[key]=where[key].replace('+',' ')
        
        where_aux={}
        for i in where:
            if i!=key:
                where_aux[i]=where[i]
        where=where_aux
        exclude_rows=[exclude_rows]

    else:
        exclude_rows={}

    if ifDate==True:
        where[('Date','Id','Id')]=(formatDateCube(request_data ['from_Date']),formatDateCube(request_data ['to_Date']))
   
    # where=preCompruebaFranjaHoraria(where,request_data['django_timezone'],time_zone)

    
    key=name_bbdd[0]+'MDXS_'+str(col_cube)+str(exclude_rows)+str(med_cube)+str(name_cube)+str(where)+str(name_bbdd)+str(ip_connect)+str(dimension_filters)

    minute=datetime.now().minute
    second=datetime.now().second
    seconds=segundosHastaY5oEnPunto(minute,second)
    
    # if (is_MDXS_Added_redis(name_bbdd[0],redis)):
    #     MDXS=get_MDXS_redis(name_bbdd[0],redis)
    # else:
    #     MDXS={}

    MDXS={}

    if not (key in  MDXS.keys()):
        
    
        mdx=mdx_class.mdx(cube,part_rows=col_cube,exclude_rows=exclude_rows,part_columns=med_cube,part_from=name_cube,part_where=where)
        


        grid=Salida_Grid()
        
        dimension_filter=filterDimensionCube(dimension_filters,request_data['types'])
        
        if dimension_filter[0][0].find('_')>0:  # especial case two atributes same dimension, delete charts after '_'
            dimension_filter_new = []
            index = dimension_filter[0][0].find('_')
            dimension_filter_new.append((dimension_filter[0][0][0:index],dimension_filter[0][1],dimension_filter[0][2]))
            dimension_filter = dimension_filter_new
        
        if dimension_filter[0][0]=='Hangupcode':
            dimension_filter=[('Hangupcode','Description','Description')]
            filters_cube = grid.filters(mdx,cube,database_cube_dict,dimension_filter,exclude_rows,'None')
        elif dimension_filter[0][0]=='Hangupcode2':
            dimension_filter=[('Hangupcode2','Long Description','Long Description')]
            filters_cube = grid.filters(mdx,cube,database_cube_dict,dimension_filter,exclude_rows,'None')
        else:
            filters_cube = grid.filters(mdx,cube,database_cube_dict,dimension_filter,exclude_rows)

        MDXS[key]=filters_cube
        add_MDX_redis(name_bbdd[0],MDXS,redis,seconds)

    else:
        
        filters_cube=MDXS[key]

    
    json_data = json_encode({
        'more':False,
        'results': filters_cube
        })
 
    return json_data


def filterColCube(col_cube,col_group_by,col_and_by='',col_final_by=''):
    # exclusivas = ['Month Field','Week Field','Day Complete']

    col_cube_new = []
    if (col_group_by!='ALL')&(col_group_by!='All'):
        if (col_group_by!=''):
            added=False
            for c in col_cube:
                if (c[0]==col_group_by or c[2]==col_group_by) and not added:
                    col_cube_new.append((c[0],c[1],c[2]))             
                    added=True   
    else:
        col_cube_new.append(('Client', 'Client', 'All'))

    if (col_and_by!='ALL')&(col_and_by!='All'):
        if (col_and_by!='' and col_and_by!= col_group_by):
            added=False
            for c in col_cube:
                if (c[0]==col_and_by or c[2]==col_and_by) and not added:
                    col_cube_new.append((c[0],c[1],c[2]))
                    added=True
    else:
        col_cube_new.append(('Client', 'Client', 'All'))

    if (col_final_by!='ALL')&(col_final_by!='All'):
        if (col_final_by!='' and col_final_by!= col_and_by and col_final_by!= col_group_by):
            added=False
            for c in col_cube:
                if (c[0]==col_final_by or c[2]==col_final_by) and not added:
                    col_cube_new.append((c[0],c[1],c[2]))
                    added=True
    else:
        col_cube_new.append(('Client', 'Client', 'All'))
    return col_cube_new

def namesColCube(col_cube_new):

    if type(col_cube_new) == list:
        col_cube=[]
        for c in col_cube_new:
            index = c[0].find('_')
            if index>0:
                col_cube.append((c[0][0:index],c[1],c[2]))
            else:
                col_cube.append((c[0],c[1],c[2]))
        return col_cube  
    else:
        if len(col_cube_new)>0:
            try:
                index = col_cube_new[0].find('_')
                if index>0:
                    new_name = col_cube_new[0][0:index]
                    col_cube_new=(new_name,col_cube_new[1],col_cube_new[2])
            except Exception, e:
                swslog('error','Index out range',e)
        return col_cube_new


def adjustementData(dict_higcharts,value_adjustement):

    list_index = []
    i=0

    for data in dict_higcharts['v_name']:
        for name in value_adjustement:
            if data.find(name[0]) > 0:
                list_index.append((data,i,name[1]))
                i = i+1

    list_data = []
    list_aux = []

    j = 0
    for data in dict_higcharts['v_data']:

        for i in range(0,len(data)):
    
            try:
        
                list_aux.append(data[i]*list_index[j][2])
            except:
                list_aux.append(data[i])
        j = j+1
        list_data.append(list_aux)
        list_aux = []


    dict_higcharts['v_data'] = list_data

    return dict_higcharts


#return tuple with column and id of the dimemsion selected
def filterDimensionCube(dimension_filters,dimension):
    new_dimension_filters=[]
    for d in dimension_filters:
        if d[0]== dimension:
            new_dimension_filters.append(d[0:3])
    return new_dimension_filters

def filterWhere(filters,request_data,database_cube_dict): 
    
    where={}
 
    for f in filters:
   
        if f[0]!='calldate':
       
            if f[0] in request_data:
                if  request_data[f[0]]!='NULL':
                    if f[0]=='Hangupcode':
                        where[(f[0],'Description','Description')]=request_data[f[0]]
                    elif f[0]=='Hangupcode2':
                        where[(f[0],'Long Description','Long Description')]=request_data[f[0]]
                    else:    
                        where[(f[0],'Id','Id')]=request_data[f[0]]
          
  

    if request_data['param_exclude'] == '1': 

        where[('Hangupcode','Id','Id')]=('-',['34','41'])
        # TODOMAS NO DELETE EXAMPLE USE
        # where[('Hangupcode','Id','Id')]=('-','34')
        # where[('Hangupcode','Id','Id')]=('',['34','41'])  
        # where[('Hangupcode','Id','Id')] = '34'

    return where   

def filterDataCube(filters,request,database_cube_dict): 
    where={}
    for f in filters:
        if f[0]!='calldate':
            if f[0] in request.GET:
                if  request.GET[f[0]]!='NULL':
                    where[(f[0],'id')]=request.GET[f[0]]
    return where

def filterMed(med_cube,select_med):

    if select_med.lower() == 'asr':
        med_cube=[('Measures','ASR'),('Measures','Attempts')]
        return med_cube
    elif select_med.lower() == 'acd' :
        med_cube=[('Measures','ACD'),('Measures','ASR'),('Measures','Attempts')]
        return med_cube
    else:
        return med_cube


def atributeAdjustement(json_data,col_cube,request_data):
    if len(json_data)>70:
        json_data = json_data.replace('Date*','')
        
        #especial case when the query have two atributtes of the same dimension
        if request_data['group_by'].find('_')>0 :
            group_by_plus= request_data['group_by'].replace('_','*')
            json_data = json_data.replace(group_by_plus,request_data['group_by'])

        if 'and_by' in request_data:
            try:
                if request_data['and_by'].find('_')>0:
                    and_by_plus = request_data['and_by'].replace('_','*')
                    json_data = json_data.replace(and_by_plus,request_data['and_by'])
            except Exception, e:
                swslog('error', 'non request_data[and_by]',e)

        for name in col_cube:
            json_data = json_data.replace('*'+name[1]+'"','"')
   
    return json_data


def obtainMargin(json_data):
    json_data_dict = ujson.loads(json_data)
    
    for data in json_data_dict['rows']:
        if float(data['Total Income']) != 0:
            # benefit = float(data['Total Income']) - float(data['Total Cost'])
            # margin = benefit / float(data['Total Income']) * 100
            dif = random.randrange(0,9)
            data['Margin'] = dif
        else:
            data['Margin'] = 0
    json_data = json.dumps(json_data_dict)

    return json_data


def orderDataCube(request,json_data):
    json_data_dict = ujson.loads(json_data)
    name_order = request['sidx']
    if request['sord'] == 'asc':
        rev = False
    else:
        rev = True
    sorted_json = sorted(json_data_dict['rows'], key=lambda d: d[name_order],reverse = rev)
    json_data_dict['rows'] = sorted_json
    json_data_dict = json.dumps(json_data_dict)

    return json_data_dict


def accuratelyAdjustment(json_data,med_cube_prec,dict_type_data = False,request_data=False,format_excel= False):

    # request = ThreadLocal.get_current_request()

    if len(med_cube_prec[0])==3:
        ind = 0
    else:
        ind = 1

    json_data_dict = json.loads(json_data,object_pairs_hook=OrderedDict)

    new_list_data = []
    for i in range(len(json_data_dict['rows'])):
        new_dict = SortedDict()
        for k,v in json_data_dict['rows'][i].items():
            for m in med_cube_prec:
                if m[ind] == k:

                    v = str(v)
                    
                    is_ip = False
                    ini_v = v.find('.')
                    sub_v= v[ini_v+1:]
                    
                    if sub_v.find('.')>=0:
                        is_ip=True

                    if v.find('.')>=1 and v != '0.0.0.0' and is_ip==False:

                        index = v.find('.');
                        if m[ind+1] != 0:
                            v = v[0:index+1+m[ind+1]]
                        else:
                            v = v[0:index]
                        
                        if format_excel == True:
                            v = float(v)
                        else :
                            v = v.replace('.',',')
                            if dict_type_data:
                                if k in dict_type_data and dict_type_data[k]:

                                    try:    
                                        float(v)             
                                        v = numberFormatter(v)
                                    except Exception, e:
                                        pass
                                        # swslog('error','Number formater not float:'+str(type(v))+str(v),e)
                            try:
                                v = v + m[ind+2]
                            except Exception, e:
                                swslog('error','Add type data for measure cube',e)
                # new_dict[k] = v

            new_dict[k] = v
        new_list_data.append(new_dict)
    json_data_dict['rows'] = new_list_data

    try:

        new_dict_footer={}
        if 'footerData' in json_data_dict:
            for k,v in json_data_dict['footerData'].items():
                for m in med_cube_prec:
                    if m[ind] == k:
                        v = str(v)
                        v = v.replace(',','.')
                        if v.find('.')>=1 and v != '0.0.0.0':
                            index = v.find('.');
                            if m[ind+1] != 0:
                                v = v[0:index+1+m[ind+1]]
                            else:
                                v = v[0:index]

                            if dict_type_data:
                                if dict_type_data[k]:
                                    try:
                                        float(v)             
                                        v = numberFormatter(v)
                                    except Exception, e:
                                        swslog('error','Number formater not float:'+str(type(v))+str(v),e)
                        try:
                            v = v + m[ind+2]
                        except Exception, e:
                            # logger.error('ERROR: in add type data for measure cube')
                            # logger.error('Exception: {0}'.format(e))
                            swslog('error','Add type data for measure cube',e)
                    # new_dict[k] = v
        
                new_dict_footer[k] = v
            json_data_dict['footerData'] = new_dict_footer
    except Exception,e:
        swslog('info','json without footerData',e)



    json_data = json.dumps(json_data_dict)  
    return json_data
    # else:

    #     for i in range(0,len(queryset_detail)):
    #         for j in field_query_detail:
    #             data = str(queryset_detail[i][j[0]])
    #             if data.find('.')>0:
    #                 index = data.find('.')
    #                 queryset_detail[i][j[0]] = data[0:index+1+j[1]]+j[2]


# def accuratelyNumber(v):
#     v = v.replace('.',',')
#     index = v.find(',')
#     if index > 0:
#         sub_v = v[0:index]   #parte entera            
#         if len(sub_v)>3: 
#             new_name = ''
#             i = 0
#             for t in range(len(sub_v),0,-1):
#                 t = t-1
#                 new_name = sub_v[t] +new_name 
#                 i = i+1
#                 if (i%3)==0 and i!=0:
#                     new_name =  '.'+new_name 
#             v = new_name+v[index:]
#         if v[0] == '.':
#             v = v[1:]
#     return v


def filterFormat(new_queryset):
    dict_type_data={}
    try:

        if len(new_queryset)>0:
            for k,v in new_queryset[0].items():
                if (type(v) is not unicode) and (type(v) is not datetime): 
                    dict_type_data [k] = type(v)
    except Exception,e:

        swslog('debug','List index out range',e)
        dict_type_data=False

    return dict_type_data   


def numberFormatter(number):
  # Nos aseguramos de que sea un string
  a = str(number)
  # Buscamos la posicion donde esta el separador de decimales
  p = a.find('.')
  # Guardamos el string con los decimales sustituyendo el punto por una coma (si es que hay)
  if p == -1:
    decimales = ''
  else:
    decimales = a[p:].replace('.',',')
    # Cogemos el entero
    a = a[:p]
  # Variables auxiliares
  b = ''
  c = ''
  i = 0
  # Generamos el numero/string con los miles
  while i < len(a)/3:
    b = a[len(a)-(3*(i+1)):len(a)-(len(c)-i)] 
    c = '.'+b + c
    i+=1
  # Concatenamos los decimales al resultado
  c = a[:len(a)-(3*i)] + c + decimales
  # Devolvemos el resultado

  if c[0]=='.':
    c = c[1:]

  c = c.replace('.',',')

  return c






def getTableDict(json_data, title_dict, value_group_by_data):
    # table_dict = SortedDict({'titles_table':title_dict})
    json_data_dict = ujson.loads(json_data)  
    data = json_data_dict['rows']

    first_element = True
    for key,value in title_dict.items():
        if first_element == True:
            title_dict.pop(key)
            title_dict.insert(0,value_group_by_data,value_group_by_data.capitalize())
            first_element = False

    # table_dict = SortedDict({'titles_table':title_dict})
    cont = 0
    series_dict = SortedDict()
    for d in data:
        exists = False
        for key,value in series_dict.items():
            if value_group_by_data == 'ALL':
                value_group_by_data = 'Client'
            if(value[value_group_by_data] == d[value_group_by_data]):
                row_dict = SortedDict()
                for v in value:
                    element = series_dict.get(key)
                    if v == value_group_by_data:
                        element_value = d[v]
                    elif v == 'ASR':
                        # try:
                        #     element_value = float(element[v]) + float(d[v])
                        #     element_value = str(round(element_value,3))
                        # except:
                        element_value = str(float(element[v]) + float(d[v]))

                    elif v == 'ACD':
                        element_value = str(float(element[v]) + float(d[v]))
                    elif v == 'answer_calls':

                        # element_value = element[v]
                        if value['ASR'] == '0.0' or value['Calls'] == '0.0':
                            element_value = '0'
                        else:
                            if float (value['Calls']) != 0:
                                element_value = str(float(value['ASR']) / float(value['Calls'])) 
                            else:
                                element_value = '0';
                    elif v == 'calls':
                        element_value = str(int(element[v]) + int(d[v]))
                    

                    row_dict[v] = element_value
                
                series_dict[serie] = row_dict
                exists = True

        if not(exists):
            cont = cont + 1
            serie = 'serie' + str(cont)

            row_dict = SortedDict()
            for e in title_dict.keys():
                if e == 'answer_calls':
                    row_dict[e] = '0'
                else:
                    if e == 'ALL':
                        e = 'Client'


                    row_dict[e] = d[e]
            series_dict[serie] = row_dict