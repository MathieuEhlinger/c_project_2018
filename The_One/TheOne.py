# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import pandas as pd
import os

import datetime
import numpy
import shutil
import copy


def highlight(s):
    return 'color: yellow' 

def style(x, file, directory):
    x=x.reset_index(drop=True)
    styled = x.style.applymap\
        (lambda v: 'background-color: %s' % '#70AD47', subset = ['Speed [µm/h]'])\
        .applymap(lambda v: 'background-color: %s' % '#FFC000', subset = ['Straightness'])
        
#    styled = x.style.applymap\
#        (lambda v: 'background-color: %s' % 'yellow', subset = ['Straightness'])
#    styled.to_excel('./'+directory+'/'+file[:-5]+' (styled).xlsx', engine='openpyxl', index=False)    
    return styled

def style_stat(x, file, directory):
    x=x.reset_index(drop=True)
    styled = x.style.applymap\
        (lambda v: 'background-color: %s' % '#70AD47', subset = ['Speed [µm/h]'])\
        .applymap(lambda v: 'background-color: %s' % '#FFC000', subset = ['Straightness'])
#    styled = x.style.applymap\
#        (lambda v: 'background-color: %s' % 'yellow', subset = ['Straightness'])
#    styled.to_excel('./'+directory+'/'+file[:-5]+' stat'+' (styled).xlsx', engine='openpyxl', index=False)
    return styled



def date_time_proc(s):

    if s<= 61:
        return '10h'
    else :
        return '24h'


def sheet_duo_production(i):
    i = i.drop(['ND.M','Generation','Elevation [°]'], axis=1)
    i['Speed [µm/h]']=i['Speed [µm/s]'].apply(lambda x:round((x*3600),2))
    x = list(i.columns)
    x.insert(9,'Speed [µm/h]')
    x.pop()
    i = i [x]
    stat_sheet=i[:-5]
    i.at[i.index[-1], 'Speed [µm/h]'] = round(stat_sheet['Speed [µm/h]'].std(),2)
    return i, stat_sheet

def stat_alteration(i):
    speed, num = pd.Series(index=i.columns), i.shape[0]
    for _ in range (4):
        i= i.append(speed, ignore_index=True)
        
    v = 'Speed [µm/h]'
    mean,std,sem = round(i[v].mean(),2), round(i[v].std(),2), round(i[v].sem(),2)
    i[v][num+1], i[v][num+2], i[v][num+3]= mean,std,sem
    
    v = 'Straightness'
    mean,std,sem = round(i[v].mean(),3), round(i[v].std(),3), round(i[v].sem(),3)  
    i[v][num+1], i[v][num+2], i[v][num+3]= mean,std,sem
    
    return i

def normal_alteration(i):
    speed = pd.Series(index=i.columns)
    i= i.append(speed, ignore_index=True)
    index= i.columns.to_series()
    i= i.append(index, ignore_index=True)
    return i

def file_processor(file, directory):
    control = pd.DataFrame(columns = ['Excel', 'Detected'])
    xl =pd.ExcelFile(file)
    writer = pd.ExcelWriter('./'+directory+'/'+file[:-5]+' (modif).xlsx')
    
    sheet_set, sheet,processed_sheets = set(),dict(), dict()
    
    for name in xl.sheet_names:
        df = xl.parse(name)
        if df.empty==False :
            i = date_time_proc((df['No.Segments'][0]))
#            print(i)
            control = control.append({'Excel':df['Duration [s]'][0],'Detected':i},ignore_index=True)
            sheet_set.add(i)
#    print(sheet_set)
    del df
    for x in sheet_set :
        sheet[x]=[]
        processed_sheets[x]=[]

    for name in xl.sheet_names:
        df = xl.parse(name)
        if df.empty == False:
            time = date_time_proc((df['No.Segments'][0]))
            sheet[time].append(df)
            
        else : print("Warning - Empty sheet detected")
#    print(sheet.keys())
    for time in sheet_set:
        total, stat = pd.DataFrame(), pd.DataFrame()
        for tbp_sheet in sheet[time]:
            x,y = sheet_duo_production(tbp_sheet)
            x = normal_alteration(x)
            total, stat= total.append(x),stat.append(y)
#        total[:-1].to_excel(writer, time)
#        stat_alteration(stat).to_excel(writer, (time+' Stat'))
#        
        style(total[:-1],file, directory).to_excel(writer, time,  engine='openpyxl', index=False)
        style_stat(stat_alteration(stat),file, directory).to_excel(writer, (time+' Stat'),  engine='openpyxl', index=False)
        

    writer.save()
    control.to_csv(path_or_buf=('./'+directory+'/control/'+file[:-5]+' (controle).csv'))


def main_twg(directory):
    error, processed, unprocessed = 0, [], []
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists((directory+'/control')):
        os.makedirs((directory+'/control'))

    for filename in os.listdir():
        if filename.endswith(".xlsx") : 
         print(os.path.join(directory, filename))
        try :
            print(filename +" is being processed...")
            file_processor(filename, directory)
            processed.append(filename)
        except KeyError:
                print (filename,' could not be processed - KeyError. Empty sheet at the end of file ?')
                continue
        except :
            print(filename,' could not be processed - Unexpected Error. Write your beloved support ! :3')
            error = 1
            unprocessed.append(filename)
            continue

    print("\n")
    print("----------------------------------")
    print("Processed files :")
    for name in processed : print (name)
    if error ==1 :
        print("\n")
        print("----------------------------------")
        print("Errors occured for :")
        for name in unprocessed :
            print(name)
    print("----------------------------------")

def data_processing( file, directory_data, directory_tracks, directory_stats, \
                    save_tracks=False):
    xl =pd.ExcelFile(file)
    
    writer_data, writer_tracks = \
        pd.ExcelWriter('./'+directory_data+'/'+file[:-5]+' data.xlsx'),\
        pd.ExcelWriter('./'+directory_tracks+'/'+file[:-5]+' tracks.xlsx')
        
    for name in xl.sheet_names:
        df = xl.parse(name)
        if df.empty==False :
            if 'Data' in name :
                df.to_excel(writer_data, (file[:-5]+name),  engine='openpyxl', index=False)
            else :
                df.to_excel(writer_tracks, (file[:-5]+name),  engine='openpyxl', index=False)
        else :
            print('Warning : Empty sheet detected')

    writer_data.save()
    if save_tracks : writer_tracks.save()

def main_to(directory_data, directory_tracks, directory_stats, save_tracks=False):
    
    if not os.path.exists(directory_data):
        os.makedirs(directory_data)
        
    if save_tracks :
        if not os.path.exists(directory_tracks):
            os.makedirs(directory_tracks)
            
    if not os.path.exists(directory_stats):
        os.makedirs(directory_stats)

    error, processed, unprocessed = 0, [], []
    for filename in os.listdir():
        if filename.endswith(".xlsx") : 

            try :
                print(filename +" is being processed...")
                data_processing(filename, directory_data, directory_tracks, directory_stats, save_tracks=save_tracks)
                processed.append(filename)
            except KeyError:
                print (filename,' could not be processed - KeyError. Empty sheet at the end of file ?')
                continue
            except :
                print(filename,' could not be processed - Unexpected Error. Write your beloved support ! :3')
                error = 1
                unprocessed.append(filename)
                continue
        print("\n")
        
    print("----------------------------------")
    print("Processed files :")
    for name in processed : print (name)
    if error ==1 :
        print("\n")
        print("----------------------------------")
        print("Errors occured for :")
        for name in unprocessed :
            print(name)
    print("----------------------------------")

def new_conf_processor(file_o, directory_data, directory_tracks, directory_stats, \
                  del_tracks=True, del_origin=False, suffix='_fm'):
    
    file = copy.deepcopy(file_o)
    if suffix==None:
        suffix='temp'

    data_xl=pd.ExcelFile('./'+directory_data+'/'+file[:-5]+' data.xlsx')
    modif_xl = pd.ExcelFile('./'+directory_stats+'/'+file[:-5]+ ' ' +\
                            directory_tracks+' (modif).xlsx')
    
    writer=pd.ExcelWriter('./'+file[:-5]+suffix+'.xlsx')
    
    for name in modif_xl.sheet_names:
        df = modif_xl.parse(name)
        df.to_excel(writer, name,  engine='openpyxl', index=False)
    
    for name in data_xl.sheet_names:
        df = data_xl.parse(name)
        df.to_excel(writer, name,  engine='openpyxl', index=False)
    
    writer.save()
    
def main_new_conf(directory_data, directory_tracks, directory_stats, \
                  suffix='fm', \
                  remove_org_data=True, \
                  death_to_the_old_ways=True):
    
    '''
    To be run after main_to and main_twg. WIll gather the 24h, 24h_stats and Data
    sheets together.
    
    death_to_the_old_ways=  True will delete the stats, tracks and data directory
    remove_org_data =       True will delete the original xlsx.
    suffix will decide the particle at the end of the file. Please input one.
    ex : suffix='monjolisuffixe'
    
    '''    
    if suffix == None or suffix=='':
        suffix= '_temp'
        
    error, processed, unprocessed = 0, [], []
    for filename in os.listdir():
        if filename.endswith(".xlsx") : 

            try :
                print(filename +" is being processed...")
                new_conf_processor(filename, directory_data, directory_tracks, directory_stats)
                processed.append(filename)
                if remove_org_data : os.remove(filename)
                
            except KeyError:
                print (filename,' could not be processed - KeyError. Empty sheet at the end of file ?')
                continue
            except :
                print(filename,' could not be processed - Unexpected Error. Write your beloved support ! :3')
                error = 1
                unprocessed.append(filename)
                continue
            print("\n")
    
    print("----------------------------------")
    print("Processed files :")
    
    for name in processed : print (name)  
    
    if death_to_the_old_ways :
        try : 
            shutil.rmtree(directory_tracks)
            shutil.rmtree(directory_data)
            shutil.rmtree(directory_stats)
        except :
            print('Something went wrong while deleting tracks, data and stats- the old ways are tenacious')
            
        
    if error ==1 :
        print("\n")
        print("----------------------------------")
        print("Errors occured for :")
        for name in unprocessed : print(name)
    print("----------------------------------")

            
def run_to(keep_files=True, use_new_format=True):
    
    directory_data, directory_tracks, directory_stats =  'data', 'tracks', 'stats'
    directory = 'output'
    main_to(directory_data, directory_tracks, directory_stats, save_tracks=True)
    os.chdir(('./'+directory_tracks))
    print(os.listdir())
    main_twg(directory)
    for f in os.listdir(('./'+directory)):
        shutil.move(('./'+directory+'/'+f), ('./../'+directory_stats)) 
    os.rmdir('./'+directory)
    os.chdir(('./..'))
    
    if use_new_format:main_new_conf(directory_data, directory_tracks,directory_stats,
                                    death_to_the_old_ways=True, remove_org_data=True)
    
run_to()