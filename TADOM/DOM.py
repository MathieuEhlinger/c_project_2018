# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 15:45:17 2018

@author: Mathieu
"""

import pandas as pd
import os
import copy
from TO import style_stat
"""
size est le nombre de cellules que tu veux dans chaque échantillon
size = [50]
créera une liste de fichiers avec à chaque fois 50 cellules
size = [50,100]
créera, pour chaque fichier en entrée, une fois un fichier avec 50 cellules, puis un avec 100
size = [50, 75,100], size = [50,60,70,80]...
Ca devrait marcher à chaque fois, évite juste les doublons ^^

L'argument 'all' est remplacé par la valeur maximale.
Les valeurs trop élevées sont remplacées par la valeur max.
Les doubblons sont éliminés.

"""

size = [30, 200, 'all']

"""
Rand : tu peux le remplacer par n'importe quel entier positif si tu veux que 
d'autres cellules soit choisies ( on parle de changement de seed ).
"""

rand = 23
not_to_style = ['Pour graphe','Contrôle des cellules','Data']

def mean(df):
    if type(df)==int:
        return df
    else :
        return df.mean()

def median(df):
    if type(df)==int:
        return df
    else :
        return df.median()

def change_name_col(df, name,WCol):
    
    new = {WCol[0]:(name+'_T'),WCol[1]:(name+'_X'),WCol[2]:(name+'_Y')}
    df=df.rename(index=str,columns = new)
    return df

def stat(data):
    d={}
    d['mean']=data.mean()
    d['std']=data.std()
    d['min']=data.min()
    d['max']=data.max()
    d['median']=data.median()
    d['quantile (25%)']=data.quantile(q=0.25, interpolation='midpoint')
    d['quantile (75%)']=data.quantile(q=0.75, interpolation='midpoint')
    
    d=pd.DataFrame(d).transpose()
    return pd.concat([data,d],sort=True)

    


def subsample (df, size = 50, after_i='Age', after_f=mean, value=None, rand=23 ):
    
    
    i, size = 0, (size-5)
    df = df.sample(frac=1, random_state=rand).reset_index(drop=True)
    
    new_df = pd.DataFrame(df.iloc[0:5])
    df = df.drop(df.iloc[0:5].index)
#    print(new_df)
    
    while i<size :
        
        if after_f(new_df[after_i]) <= value:
            
#            print(after_f(new_df[after_i]), '<',value)
            new_val = pd.DataFrame(df.loc[(df[after_i] >= value)])
            
            ind = list(new_val.index)[0]
            new_val = new_val.iloc[0]
            
            new_df = new_df.append(new_val)
            df = df.drop(ind, axis=0)
#            df = df.drop(new_val.index)    
#            
        elif after_f(new_df[after_i]) > value:
            
#            print(after_f(new_df[after_i]), '>',value)
            new_val = pd.DataFrame(df.loc[(df[after_i] <= value)])
            
            ind = list(new_val.index)[0]
            new_val = new_val.iloc[0]
            
            new_df = new_df.append(new_val)
            df = df.drop(ind, axis=0)
            
        i+=1
    return new_df

    
def multiple_subsamples(df, size = 50, after_i='Age', second_i='SCOREBDI', 
                        after_f=mean, second_f=mean,
                        value_1=None, value_2=None, rand=23):
    current_ss = dict()
    current_ss[second_i] = -1000
    score= 1000
    
    while ((second_f(current_ss[second_i])-value_2) > df[second_i].std()) \
        or type(current_ss)==type(dict()):
        
        for i in range(10):
            ss = subsample(df, value=value_1, rand= (rand+i), size=size,after_i=after_i,after_f=after_f)
            n_score = abs (second_f(ss[second_i]) - value_2)
            if n_score < score :
                current_ss = ss
                score=n_score
                
        print(after_i,':', after_f(current_ss[after_i]),' | ', \
                  after_f(df[after_i]),' +/-',df[after_i].std())
        print('--------------')
        print(second_i,':', second_f(current_ss[second_i]),' | '\
                  , second_f(df[second_i]),' +/-',df[second_i].std())

    return current_ss


def cells_id(df, identifiers):
    
    col_list = pd.DataFrame(index = df.index)
    for i in identifiers:
        col_list[i] = df[i]
    return col_list.values.tolist()

def drop_ab(df, w_col):     #drops all columns but
    ind = list(df.columns)
    for i in w_col :
        ind.remove(i)
    return df.drop(ind, axis=1)

def search_cell(df, cell_id):
        
    return df.iloc()

def data_together(df, sheet_identifier='Data'):
    
    data_s = list()
    
    for i in df.sheet_names:    #list all Data sheets
        if sheet_identifier in i :
            data_s.append(df.parse(i))
    
    return pd.concat(data_s, axis=0,sort=True)

def adapt_sizes_to_df(df_size, sizes):
    sizes, = copy.deepcopy(sizes), 

    for i, size in enumerate(sizes) :
        if size == 'all':
            sizes[i] = df_size
        elif type(size) != int:
            continue
        elif size >= df_size:
            sizes[i] = df_size
    sizes = list(set(sizes))
    
    new_list=list()
    for size in sizes:
        if type(size) == int :
            if size > 0 :
                new_list.append(size)
        else :
            try :
                print('Warning - ', size, ' entry in sizes unknown. Entry will be ignored')
            except :
                print('An entry that can\'t be displayed was ignored')
                pass
            
    new_list.sort()
    return new_list
#    return list(set(sizes)).sort()
        
    

def transformer(file, directory, size=50, rand=23,not_to_style=not_to_style):

    xl =pd.ExcelFile(file)
#    first = 0

    
    IDs = ['Name', 'Tree ID', 'ID']
    WCol = ['Time [s]', 'Position X [%s]','Position Y [%s]']
    
    datas=data_together(xl)
    stat_sheet=xl.parse('24h Stat')[:-4]
    size=adapt_sizes_to_df(stat_sheet.shape[0], size)
    print('Running on sizes :', size)
#    writer = pd.ExcelWriter('./'+directory+'/'+file[:-5]+' '+ str(selected_size)+' .xlsx')
    writer = pd.ExcelWriter('./'+directory+'/'+file[:-5]+'_m2'+' .xlsx')
    for i in xl.sheet_names:
        to_style=True
        for nts in not_to_style:
            if nts in i :
                to_style=False
        if to_style :   style_stat(xl.parse(i)).to_excel(writer,i, \
                                  engine='openpyxl', index=False)
        else :          xl.parse(i).to_excel(writer,i,\
                                engine='openpyxl', index=False)
    
    for selected_size in size :    

        selection = multiple_subsamples(stat_sheet, size=selected_size, after_i='Speed [µm/h]', second_i='Straightness',
                        after_f=mean, second_f=mean, value_1 = stat_sheet['Speed [µm/h]'].mean(),
                        value_2 = stat_sheet['Straightness'].mean(), rand=rand)
#
        stat(selection).to_excel(writer, (str(selected_size)+' - Contrôle des cellules'))
        
        print(selection.shape)
        cell_df = pd.DataFrame()
        for ID in cells_id(selection, IDs):
#            print('IDs : ',IDs)
#            print('ID : ', ID)
#            
            cell_data = datas.loc[(datas[IDs[0]] == ID[0]) & (datas[IDs[1]] == ID[1]) & (datas[IDs[2]] == ID[2])].reset_index(drop=True)
            cell_data = cell_data.sort_values(['ND.T'], axis=0)
            cell_data = drop_ab(cell_data, WCol)
            new_name= (str(ID[0])+'_'+str(int(ID[2]))+'_')
            cell_data = change_name_col(cell_data, new_name,WCol)
#            print(cell_data)
            cell_data = pd.concat([cell_data, pd.DataFrame(columns=['','','','','','',''])],axis=1, sort=False)
            cell_df = pd.concat([cell_df,cell_data], axis=1,sort=False)
        cell_df.to_excel(writer, (str(selected_size)+' - Pour graphe'), index=False)
    writer.save()
#        final_list.append(lists)
        
    
    
    

def main_mom(file_processor = transformer, directory = 'output dom', size=50, rand=23, remove_org_data_dom=True):
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    processed, unprocessed, error = list(),list(), 0
    for filename in os.listdir():
        if filename.endswith(".xlsx") : 
            print(os.path.join(directory, filename))
            try :
                print(filename +" is being processed...")
                file_processor(filename, directory, size= size, rand=rand)
                processed.append(filename)
                if remove_org_data_dom : os.remove(filename)
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
                
#main_mom(size = size, rand=rand)