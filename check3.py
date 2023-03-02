#!/bin/env python

__author__ = "Mariem Kammoun"
__copyright__ = "Copyright (c) 2023 STMicroelectronics."
__version__ = "0.0.1"
__email__ = "mariem.kammoun@actia-engineering.tn"

"""
Package License
"""

import os
import argparse
import pathlib
import chardet
import sys
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from io import StringIO
from pathlib2 import Path
from simple_file_checksum import get_checksum
import re
from urllib.parse import *
import requests #helpful for making HTTP connections
from http.client import responses #providing a small description for HTTP response codes
import validators #for validating the URL
from urllib.request import Request, urlopen
from Lib import gen_func

###extract table
def table_extract (file_path):
    # Opening and reading the html file
    try:
        html_file = open(file_path, "r", encoding="utf-8")
    except FileNotFoundError:
        print("The specified file was not found.")
    html = html_file.read() 
    # Parse the html file
    soup = BeautifulSoup(html, 'html.parser')
    
    table = soup.find("table")
    rows = table.find_all("tr")
    tableau =[]
    components=[]
    copyrights=[]
    licenses=[]
    for row in rows:
        cells = row.find_all("td")
        row_contents = [cell.text for cell in cells]
        #print (row_contents)
        
        if row_contents == [] :
            pass
        else :
            component = row_contents[0]
            copyright = row_contents[1]
            license = row_contents[2]
            tableau.append(row_contents)
            components.append(component)
            copyrights.append(copyright)
            licenses.append(license)

    return tableau, components, copyrights, licenses 

def st_component(copyrights, components):
    st_cmpn=[]
    cpright=list(enumerate(copyrights))
    for cpr_itr, cpr in cpright:
        if cpr == 'STMicroelectronics':
            repo=components[cpr_itr]
            st_cmpn.append(repo)
    return st_cmpn

#returns paths, all directories and files, and check repo_existence_with_st_component_name
def firmware_hierarchy(frmw_dir_path,component_names,st_cmpn):  
    status_check_component_existence=''
    error_check_component_existence='NA'
    diff_existence_componets=[]
    components_inputs=[]
    #open and read input file that contains correct name of components as in the frmw directory 
    with open(component_names, "r") as file:
        lines = file.read().splitlines()     

    for line in lines:
        components_inputs.append(line)
    print('components_inputs',components_inputs)  
    compteur=0
    len_components_inputs=len(components_inputs)
    l_dir_not_found=[]
    components_not_found=''
    for target_dir in components_inputs:
        
        for root, dirs, files in os.walk(frmw_dir_path) :
            #Check existence of component
            if target_dir in dirs:
                print('yes, there is a directory with this name', target_dir ,'and its path is:',root)
                status_check_component_existence='OK'
                compteur+=1
                l_dir_not_found.append(target_dir)
                break
    if compteur<len_components_inputs :
        diff_existence_componets =list(set(components_inputs)-set(l_dir_not_found))
        print('diff0',diff_existence_componets)
    else:
        status_check_component_existence='OK'   
    if diff_existence_componets !=[]:    
        diff_st=list(set(diff_existence_componets)-set(st_cmpn))  #verify if not existence components are st copyright
        if diff_st !=[]:  
            status_check_component_existence='ERROR'
            for st_iterator in diff_st:
                if len(components_not_found)==0:
                    components_not_found=components_not_found +' '+st_iterator
            else:
                    components_not_found=components_not_found +', '+st_iterator
        error_check_component_existence='Directories not found:'+components_not_found
                
    else:
        status_check_component_existence='OK'                
    print(error_check_component_existence)

    return root, dirs, files, status_check_component_existence, error_check_component_existence #, dic_dirs_files

#Check the presence of LICENSE.md/.txt in each component
def license_presence_each_component(frmw_dir_path,component_names,st_cmpn):  
    status_presence_lic_in_each_component=''
    error_presence_lic_in_each_component='NA' 
    components_inputs=[]
    l_md_txt_lcs_present=[]
    #open and read input file that contains correct name of components as in the frmw directory 
    with open(component_names, "r") as file:
        lines = file.read().splitlines()     

    for line in lines:
        components_inputs.append(line)
    print('components_inputs',components_inputs) 
    for target_dir in components_inputs:
       
        dic_dirs_files = {}
        for root, dirs, files in os.walk(frmw_dir_path) : 
            lcs = ['LICENSE.md', 'LICENSE.txt']   
            key = root
            if all(item in files for item in lcs):
                dic_dirs_files[key] = files
                
                l_folder_name=[]
                l_bsp_components=[]
                cle=dic_dirs_files.keys() #retrieve keys that contains paths of directories which have LICENCE.md/.txt
                bsp_components='BSP'+ os.sep +'Components' #exception : path of BSP\Components

                for x in cle : 
                    folder_name= os.path.basename(x) # directories which have LICENCE.md/.txt
                    if bsp_components in x:  #BSP\Components exception
                        l_bsp_components.append(folder_name) #common, etc...
                    else:  
                        l_folder_name.append(folder_name)

            else:
                pass 
        
        if target_dir in l_folder_name:
            l_md_txt_lcs_present.append(target_dir)
        print('l_md_txt_lcs_present',l_md_txt_lcs_present)     
    if l_bsp_components :           
            l_md_txt_lcs_present.append('Components') #for example common is under BSP\Components

    print ('dic_dirs_files.keys',cle)   
    print("la liste des dosssiers ", l_folder_name)    
    print("la liste des dosssiers components bsp",l_bsp_components)
    print ('length',len(cle),len(l_folder_name))           
    print('l_md_txt_lcs_present',l_md_txt_lcs_present)     
          
    set_components_inputs = set(components_inputs)
    set_md_txt_lcs_present = set(l_md_txt_lcs_present)
    diff = list(set_components_inputs-set_md_txt_lcs_present)
   
    print ('diff',diff)
    if not diff:
        status_presence_lic_in_each_component ='OK'
    else:
        diff_st_lcs_presence=list(set(diff)-set(st_cmpn))  #verify if there are components which aren't st copyright, we will remove them
        print ('diff_st_lcs_presence',diff_st_lcs_presence)
        if diff_st_lcs_presence ==[]: #if there aren't components which aren't st copyright => all components are st copyright 
            status_presence_lic_in_each_component="WARNING"
            error_presence_lic_in_each_component = "Both LICENSE.md & LICENSE.txt aren't presents in each component"
        else:
            status_presence_lic_in_each_component ='OK'
    print('dic_dirs_files', dic_dirs_files)
    return root, dirs, files, dic_dirs_files, status_presence_lic_in_each_component, error_presence_lic_in_each_component  
     

def check_licenses_values(copyrights, licenses):
    status_check_licenses_values=''
    error_check_licenses_values='NA'
    licenses_values_st_component=['BSD-3-Clause','Apache-2.0','MIT','SLA0044','SLA0047'] 
    correct_license = True
    st_lic=[]
    lic_errone=''
    #l_stop_analyze_components=[]
    cpright=list(enumerate(copyrights))
    print ('cpright',cpright)
    for cpr_itr, cpr in cpright:
        if cpr == 'STMicroelectronics':
            lic_st=licenses[cpr_itr]
            st_lic.append(lic_st)
    print ("st_lic",st_lic)   

    for i in st_lic:
        if i in licenses_values_st_component:
            correct_license = correct_license and True
        else:
            if len(lic_errone)==0:
                lic_errone=lic_errone+' '+i
            else:    
                lic_errone=lic_errone+', '+i
            
            correct_license = correct_license and False
        #print ('lic_errone',lic_errone)
        error_check_licenses_values="Unknown license: incorrect license name: " + lic_errone
    if correct_license == True:
        status_check_licenses_values='OK'
    else:
        status_check_licenses_values="WARNING"           
    return status_check_licenses_values, error_check_licenses_values, correct_license      


def check_checksum_licenses_templates(frmw_path,licences_list,checksum_algorithm):
    
    licences_tmpl_dict_chks={}
   
    sub_directory = 'License_templates'

    full_path = os.path.join(frmw_path, sub_directory)
    if os.path.isdir(full_path):
        print(f"{full_path} exists and is a directory.")
        lcs_presence = gen_func.files_presence_in_directory(full_path, licences_list)
        print ('lcs_presence',lcs_presence)
        for key in licences_list:
            template_license_path=os.path.join(frmw_path, sub_directory,key)
            #print (template_license_path)
            chks_tmpl=get_checksum(template_license_path,algorithm=checksum_algorithm)
            #print('chks_tmpl',chks_tmpl)
            licences_tmpl_dict_chks[key]=chks_tmpl
        print ('licences_dict_tmpl_chks', licences_tmpl_dict_chks)     

    else:
        print(f"{full_path} does not exist or is not a directory.")
    
    return lcs_presence, licences_tmpl_dict_chks


def check_checksum_MD_licenses_templates(frmw_path,checksum_algorithm):
    
    md_licences_tmpl_dict_chks={}
    dict_search_text = {
                "Apache-2.0_LICENSE.md": "Copyright [yyyy] [name of copyright owner]",
                "BSD-3-Clause_LICENSE.md": "Copyright CCCC(-UUUU) STMicroelectronics.", 
                #"BSD-3-Clause_LICENSE_without_EOL.md": "Copyright CCCC(-UUUU) STMicroelectronics.",       #added 01/03/2023        
                "MIT_LICENSE.md": "Copyright CCCC(-UUUU) STMicroelectronics."
                }

    sub_directory = 'License_templates'

    full_path = os.path.join(frmw_path, sub_directory)
    if os.path.isdir(full_path):
        print(f"{full_path} exists and is a directory.")
        for key in dict_search_text.keys() :
            template_license_path=os.path.join(frmw_path, sub_directory,key)
            nv_template_license_path=os.path.join(frmw_path, sub_directory) #without copyrights
        
            with open(template_license_path, "r") as file:
                file_content = file.read()
                search_text = dict_search_text[key]
            
                license_file_treated=nv_template_license_path+os.sep+'Treated_'+key
                new_content = file_content.replace(search_text, "")
            with open(license_file_treated, 'w') as file:
                file.write(new_content)
                
            chks_tmpl=get_checksum(license_file_treated,algorithm=checksum_algorithm)
            #print('chks_tmpl',chks_tmpl)
            md_licences_tmpl_dict_chks[key]=chks_tmpl
        print ('md_licences_dict_tmpl_chks', md_licences_tmpl_dict_chks)     

    else:
        print(f"{full_path} does not exist or is not a directory.")
    
    return md_licences_tmpl_dict_chks


def check_checksum_licenses (dic_dirs_files,checksum_algorithm):
    license_cks=[]
    lcs_list=['LICENSE.txt', 'LICENSE.md']
    vl=dic_dirs_files.values()
    path_dir_lcs=list(dic_dirs_files.keys())

 #license cks is a list of the license.txt/.md of the dic_dirs_files
    count = len(path_dir_lcs)
    iterator=0
    while (iterator < count):
        for sublist in vl:
            for i in sublist:
        
                if i in lcs_list:

                    dir_path=path_dir_lcs[iterator]
                    
                    lcs_path=dir_path + os.sep + i
                    #Cheksum calculation of LICENCE.md/.txt
                    chks_lcs=get_checksum(lcs_path,algorithm=checksum_algorithm)
                    #print('chks_lc',chks_lcs)
                    license_cks.append(lcs_path)
                    license_cks.append(chks_lcs)  
            iterator+=1    
    return license_cks


def checksum_calcul_without_copyright(dic_dirs_files,checksum_algorithm):                          
    license_cks_no_cp=[]
    l_paths_license_cks_no_cp=[]
    lcs_list=['LICENSE.txt', 'LICENSE.md']
    vl=dic_dirs_files.values()
    #print ('vl',vl)
    #print("len vl",len(vl))
    path_dir_lcs=list(dic_dirs_files.keys())

  
#license cks is a list of the license.txt/.md of the dic_dirs_files
    count = len(path_dir_lcs)
    iterator=0
    s = 0
    while (iterator < count):
        for sublist in vl:
            for i in sublist:
        
                if i in lcs_list:

                    dir_path=path_dir_lcs[iterator]
                    
                    lcs_path=dir_path + os.sep + i
                    print('lcs_path',lcs_path)
                    print (i)                                                     

                    if i =='LICENSE.md':
                        s= s+1
                        print(s)
                        with open(lcs_path, "r",encoding="utf-8") as file:
                            file_content = file.read()
                            test=False
                            yi=0
                            sentence='Copyright \[\d{4}\] \[[a-zA-Z]+\]'                          
                            while (test==False) and (yi<2) :
                                l_search_md_lic_copyrights_sentences=re.findall(sentence, file_content)
                                print ("sssssssssssssssss",l_search_md_lic_copyrights_sentences)
                                if l_search_md_lic_copyrights_sentences!=[] :
                                    print('sentence',sentence)
                                    license_file_treated=dir_path+os.sep+'LICENSE_treated.md'
                                    print(license_file_treated)
                                    new_content = file_content.replace(l_search_md_lic_copyrights_sentences[0], "")
                                    with open(license_file_treated, 'w',encoding="utf-8") as file:
                                        file.write(new_content)
                                    #Cheksum calculation of LICENCE.md
                                    chks_lcs=get_checksum(license_file_treated,algorithm=checksum_algorithm)
                                    l_paths_license_cks_no_cp.append(license_file_treated)
                                    #license_cks_no_cp.append(license_file_treated)
                                    license_cks_no_cp.append(chks_lcs) 
                                    test=True   
                                if ((yi!=0) and (l_search_md_lic_copyrights_sentences==[])): #cas du projet 8 et 9                                   
                                    chks_lcs=get_checksum(lcs_path,algorithm=checksum_algorithm)
                                    l_paths_license_cks_no_cp.append(lcs_path)
                                    #license_cks_no_cp.append(lcs_path)
                                    license_cks_no_cp.append(chks_lcs) 
                                    test=True
                                sentence='Copyright\s\d{4}\sSTMicroelectronics\.'                                
                                yi+=1
                               
                        pass            

                    else:
                        #Cheksum calculation of LICENCE.txt
                        chks_lcs=get_checksum(lcs_path,algorithm=checksum_algorithm)
                        l_paths_license_cks_no_cp.append(lcs_path)
                        #license_cks_no_cp.append(lcs_path)
                        license_cks_no_cp.append(chks_lcs)
            iterator+=1    
    return license_cks_no_cp, l_paths_license_cks_no_cp   


def st_license_name(tableau):
    st_license_name={}
    for line in tableau:
        for item in line:
            if item=='STMicroelectronics':
                st_license_name[line[0]] = line[2]
    print (st_license_name)
    return st_license_name     

def st_license_name_verification(st_license_name):   
    #License names according to SPDX
    SPDX_ID=['Apache-2.0','BSD-3-Clause','MIT'] 
    st_component_correct_license_name={}
    st_component_incorrect_license_name={}
    print ('st_license_name.items()',st_license_name.items())
    print (type(st_license_name.items()))
    for key, value in st_license_name.items():
        if value in SPDX_ID:
            st_component_correct_license_name[key]=value
        else:
            st_component_incorrect_license_name[key]=value
    print('st_component_correct_license_name',st_component_correct_license_name)
    print('st_component_incorrect_license_name',st_component_incorrect_license_name)
    return st_component_correct_license_name, st_component_incorrect_license_name

##### URLs

def url_validation(st_license_name):
    scheme='https' 
    netloc='opensource.org' 
    path='/license/'+ st_license_name+'/' 
    url = urlunparse((scheme, netloc, path, '', '', '')) 
    print(url)

    valid_url= True
    if validators.url(url) is valid_url:
        status = requests.head(url).status_code
        try:
            print(url, status,responses[status], "\n")
            url_valid_status=status
            url_valid_http_description=responses[status]
        except:
            print(url, status, "Not an Standard HTTP Response code\n")
            url_valid_status=status
            url_valid_http_description="Not an Standard HTTP Response code\n"
    else:
        print(url, "Not an valid URL\n")
        valid_url= False

    return url, valid_url, url_valid_status, url_valid_http_description

def all_url_validation(st_component_correct_license_name):
    st_component_all_url_validation={}
    url_results=[]
    corrcet_licenses_names_url_valid=True
    #corrcet_licenses_names_url_valid=False
    
    for key, value in st_component_correct_license_name.items():
        url_results=[]
        url, valid_url, url_valid_status, url_valid_http_description=url_validation(value)
        url_results.append(url)
        url_results.append(valid_url)
        url_results.append(url_valid_status)
        url_results.append(url_valid_http_description)
        st_component_all_url_validation[key]=url_results
    print ('st_component_all_url_validation',st_component_all_url_validation) 
    
    for iter_st_cmp_url_valid in st_component_all_url_validation.values():
        if iter_st_cmp_url_valid[2] != 200:
            corrcet_licenses_names_url_valid = False
            break
    return st_component_all_url_validation, corrcet_licenses_names_url_valid 

def website_reading(st_license_name):
    http_errors=[]
    webpage=''
    scheme='https' 
    netloc='opensource.org' 
    path='/license/'+ st_license_name+'/'
    url = urlunparse((scheme, netloc, path, '', '', '')) #Join different components of URL
    print(url)
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        web_byte = urlopen(req).read()
        webpage = web_byte.decode('utf-8')
        #print (webpage)
    # Catching the exception generated     
    except Exception as e :
        print(str(e))
        http_errors.append(str(e))
        pass
    print ('http_errors',http_errors)
    return webpage,http_errors

def website_parsing(st_component_correct_license_name):
    st_component_website_parse={}
    regex_errors=[]
    correct_website_license= True
    for key, value in st_component_correct_license_name.items():
        if value == 'BSD-3-Clause':
            regex = 'The 3-Clause BSD License'
        elif value == 'Apache-2.0':
            regex = 'Apache License, Version 2.0'   
        elif value == 'MIT':
            regex= 'The MIT License'
        
        #value = value +'WXC' #for testing
        webpage,http_errors=website_reading(value)
        
        if webpage !='' and len(webpage)!=0:
            title=''
            try: 
                title = re.findall(r'<title>'+regex,webpage)
                print ('ttttttttttttttt',title) 
            # Catching the exception generated     
            except Exception as e :
                print(str(e))
                regex_errors.append(str(e))
                print('regex_errors',regex_errors)
                pass   
            if title !='' and not regex_errors:
                st_component_website_parse[key]=title
            else:
                st_component_website_parse[key]='Not correct website' 
        #else: #http errors not empty 
        if http_errors:
                st_component_website_parse[key]='Not correct website'      
    print (st_component_website_parse)   
    
    #to verify if all are good websites, useful to identify STATUS and ERROR 
    for key, value in st_component_website_parse.items():
        if value == 'Not correct website':
            correct_website_license= False
    print('There are incorrect website licences')
        
    return st_component_website_parse, correct_website_license 

###### Release Notes files
def search_word(file_path, word):
    with open(file_path, 'r', encoding="utf-8") as file:
        presence= False
        # read all content of a file
        content = file.read()
        # check if string present in a file
        l_occurences=re.findall(word, content, flags=re.IGNORECASE)
        print('l_occurences',l_occurences)
        if l_occurences:
            presence= True
        else:
            presence= False
    return presence

def check_license_in_release_notes(frmw_dir_path,lic_existence,word):
    error_rl_notes='NA'
    l_presence=[]
    lic_present=0  
    for key, value in lic_existence.items():
        if value =='exist':
            release_notes_path=frmw_dir_path+os.sep+key
            presence=search_word(release_notes_path, word)
            print(key,presence)
            print ('l_presence',l_presence)
            #put the 2 results of the function in a list
            l_presence.append(presence)
        print('l_presence',l_presence)   

    # if the word existe in the 2 files or just one or no one
    for itr in l_presence:
            if itr == True:   
                lic_present += 1
    print ('lic_present',lic_present)    


    if lic_present >=1: 
        status_rl_notes = 'WARNING'
        error_rl_notes = 'Release Notes files contains the word license'
    else:
        status_rl_notes = 'OK'        

    return status_rl_notes, error_rl_notes

################################ Test checksum
def test_result_checksum(license_cks_without_copyright_sentences,licences_tmpl_dict_chks,md_licences_tmpl_dict_chks):
    '''for i in license_cks_without_copyright_sentences:
        if i in licences_tmpl_dict_chks.values():
            i='''''
    test_txt=[]
    test_md=[]
    for i in range(0, len(license_cks_without_copyright_sentences), 2):
        if i in licences_tmpl_dict_chks.values() or i in md_licences_tmpl_dict_chks.values():
            #print(license_cks_without_copyright_sentences[i])
            license_cks_without_copyright_sentences[license_cks_without_copyright_sentences.index(i)]='MDMDMDMDMDMDMDMDMDMDMDMDMDMDMDMD'
            #test_md.append(license_cks_without_copyright_sentences[i])   
            license_cks_without_copyright_sentences.append(license_cks_without_copyright_sentences[license_cks_without_copyright_sentences.index(i)]) 
    #print('test md',test_md)
    print('test md',license_cks_without_copyright_sentences)
    for i in range(1, len(license_cks_without_copyright_sentences), 2):
        #print(license_cks_without_copyright_sentences[i])
        #test_txt.append(license_cks_without_copyright_sentences[i])  
       if i in licences_tmpl_dict_chks.values() or i in md_licences_tmpl_dict_chks.values(): 
           license_cks_without_copyright_sentences[license_cks_without_copyright_sentences.index(i)]='TXTXTXTXTXTXTXTXTXTXTXTXTXTXTXTX'
           license_cks_without_copyright_sentences.append(license_cks_without_copyright_sentences[license_cks_without_copyright_sentences.index(i)]) 
    #print('test txt',test_txt)
    print('test txt',license_cks_without_copyright_sentences)
    #return test_md, test_txt    
    return license_cks_without_copyright_sentences    

def cpr_st_treatment(st_cmpn):
    st_cmpn_treated=[]
    family_pattern = r"STM32[A-Za-z]\d+x*"
    for i in st_cmpn:
        if "HAL" in i or "LL" in i or "Drivers" in i:
            matches = re.findall(family_pattern, i)
            family=matches[0]
            i=family+'_HAL_Driver'
            st_cmpn_treated.append(i)
        elif "BSP" in i:
            i = i.replace("BSP", "").strip()
            print('BSPPPPPPPPPPPP',i) 
            st_cmpn_treated.append(i)  
        elif "Projects" in i:
            #i = i.replace("Projects", "").strip()
            i="Projects"
            st_cmpn_treated.append(i)  
        elif "Utilities" in i:
            #i = i.replace("Utilities", "").strip() 
                i="Utilities"
                st_cmpn_treated.append(i)   
        else:
            st_cmpn_treated.append(i)  
    print('family',family) 
    print('st_cmpn_treated',st_cmpn_treated)         
    return family, st_cmpn_treated        

def checksum_list_st(st_cmpn_treated,license_cks_without_copyright_sentences,l_paths_license_cks_without_copyright_sentences): #remove the paths that are not st copyrights

    l_st_paths=[]
    st_license_cks_without_copyright_sentences=[]

    
    for i in l_paths_license_cks_without_copyright_sentences :
        l=i.split(os.sep)
        for j in l :
            if j in st_cmpn_treated:
                l_st_paths.append(os.sep.join(l))
                st_license_cks_without_copyright_sentences.append(license_cks_without_copyright_sentences[l_paths_license_cks_without_copyright_sentences.index(i)])
                break

    print('l_paths_license_cks_without_copyright_sentences',len (l_paths_license_cks_without_copyright_sentences))
    print('l_st_paths',len (l_st_paths))
    print('longueur st_license_cks_without_copyright_sentences',len (st_license_cks_without_copyright_sentences))
                    
    #print('total_st_paths',l_paths_license_cks_without_copyright_sentences)
    print('l_st_paths',l_st_paths)
    print('st_license_cks_without_copyright_sentences',st_license_cks_without_copyright_sentences)
    return l_st_paths, st_license_cks_without_copyright_sentences



