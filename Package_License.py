#!/bin/env python

__author__ = "Mariem Kammoun"
__copyright__ = "Copyright (c) 2023 STMicroelectronics."
__version__ = "0.0.1"
__email__ = "mariem.kammoun@actia-engineering.tn"

"""
Package License
Note:We should have python 3.10 to use "match" for "Swich case" (https://docs.python.org/3/whatsnew/3.10.html#pep-634-structural-pattern-matching)
"""

import os
import argparse
import pathlib
import chardet
import sys
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from io import StringIO
from simple_file_checksum import get_checksum
from Lib import check3,gen_func

#************************CHECK 1 ****************

def check1_existence_licenses_files():

    status = ''
    error = 'NA'
    check_title=": Check the presence of the two package license files in the firmware directory"

    list_pkg=["Package_license.html","Package_license.md"]

    check1_result= gen_func.files_presence_in_directory(frmw_dir_path, list_pkg)

    check1_result_values = check1_result.values()

    if list(check1_result_values)[0] == list(check1_result_values)[1] =="exist":
        status = 'OK'
    elif list(check1_result_values)[0] == list(check1_result_values)[1] == "not exist":
        status = 'ERROR'
        error = "Package_license.html not exist.<br>" + "Package_license.md not exist."
    else:
        # Get the key corresponding to value not exist
        key = list(filter(lambda x: check1_result[x] == "not exist", check1_result))[0]
        status = 'ERROR'
        error = str(key) + " not exist."

    return check_title, status, error

### Check if text exist or removed
def search_str(file_path, word):
    with open(file_path, 'r', encoding="utf-8") as file:
        removed= False
        # read all content of a file
        content = file.read()
        # check if string present in a file
        if word in content:
            removed= True
        else:
            removed= False
    return removed

def check2_conformity_license_files_templates():
    status = ''
    error = 'NA'
    text0="OVERVIEW"
    text1= "This Software Bill Of Material (SBOM) lists the software components of this software package, including the copyright owner and license terms for each component."
    text2= "The full text of these licenses are below the SBOM."
    text3="SOFTWARE BILL OF MATERIALS"
    text4="<p><strong>Notes:</strong> If the license is an open source license, then you can access the terms at <a href=\"https://opensource.org/\">www.opensource.org</a>. Otherwise, the full license terms are below. If a component is not listed in the SBOM, then the SLA shall apply unless other terms are clearly stated in the package.</p>"

    html_file_path=frmw_dir_path + os.sep + "Package_license.html"

    existence0=search_str(html_file_path, text0)
    existence1=search_str(html_file_path, text1)
    existence2=search_str(html_file_path, text2)
    existence3=search_str(html_file_path, text3)
    existence4=search_str(html_file_path, text4)


    if existence0 and existence1 and existence2 and existence3 and existence4:
        existence_msg ='Template contains all the sentences of SBOM.'
        Status_check2_existence = True
    else:
        existence_msg ='Template don\'t contain all the sentences of SBOM.'
        status = 'ERROR'
        Status_check2_existence = False
        error = existence_msg


    text5="The License column of the SBOM could include hyperlinks:"
    text6="internal hyperlinks to quickly go down to the place where that license starts in same document – i.e. for SLA or ANNEX X,"
    text7="License ID when OSI"
    text8="to avoid any issue (e.g. which terms really apply?), the ID in this column should be exactly the same as in OSI and not any other deviation (e.g. “GPLv2+” is NOT OK)."
    text9="The “main” SLA for the software package should be called “SLA” to maintain consistency with the above Note regarding default terms."


    guidance1=search_str(html_file_path, text5)
    guidance1_1=search_str(html_file_path, text6)
    guidance1_2=search_str(html_file_path, text7)
    guidance1_3=search_str(html_file_path, text8)
    guidance2=search_str(html_file_path, text9)


    if guidance1 and guidance1_1 and guidance1_2 and guidance1_3 and guidance2:
        guidance_msg ='Guidances aren\'t removed from the template.'
        status = 'ERROR'
        Status_check2_guidance= False
        error = guidance_msg
    else:
        guidance_msg ='Guidances are removed from the template.'
        Status_check2_guidance= True

    if Status_check2_existence and Status_check2_guidance:
        status = 'OK'
    elif not(Status_check2_existence)  and not(Status_check2_guidance) :
        status = 'ERROR'
        error = existence_msg +'<br>'+ guidance_msg

    check_title=": Check the conformity of license files and templates "


    return check_title, status, error

def generate_html(gen_date, header, rows , report_name, f_results):
    """ Generate the html results report """

    file_loader = FileSystemLoader(os.path.abspath(
        os.path.dirname(__file__)) + '/templates', encoding='utf8')

    env = Environment(loader=file_loader)
    template = env.get_template('template.html')
    output = template.render(
        gen_date=gen_date, header=header, rows=rows, report_name=report_name)

    with open(f_results, 'w') as results_html:
        results_html.write(output)

    print("compilation report generated under : ", f_results)


def get_args():
    """ get input args """
    parser = argparse.ArgumentParser(
        description='Get the firmware directory to do different Package licenses checks : ./Package_License.py --input <firmware_directory_path>')
    parser.add_argument(
        '--input', help='path to firmware_directory_path', required=True)
    parser.add_argument(
        '--check', help='optional args, check number to do, must be in [1,5,all], you can enter multiple choice with space(default: all)',choices=['1','2','3','4','5','all'],nargs='*')
    parser.add_argument(
        '--components', help='optional args, check components_folder_names, (default: inputs.txt)')   
    parser.add_argument(
        '--checksum_algorithm', help='optional args, algorithm to use to compare licenses templates and licenses of different directories of the firmware, (default: MD5)')  
    parser.add_argument(
        '--output', help='optional args, output html file path (default: results.html)')
    parser.add_argument(
        '--report', help='optional args, title (default: "License Package Checks")')

    args = parser.parse_args()

    return args.input, args.check, args.components, args.checksum_algorithm, args.output, args.report

if __name__ == "__main__":

    frmw_dir_path, check_input, component_names, checksum_algorithm, report_file, report_name = get_args()

    if check_input == None or check_input ==[]:
        checks_list = ['all']
    else:
        #Eliminate duplicates
        checks_list = []
        check_input_sorted=sorted(check_input)

        if 'all' in check_input_sorted : #if all exist in the input list we ignore other cases
                checks_list = ['all']

        else:
            for item in check_input_sorted:
                if item not in checks_list:
                    if item != '': #empty case and check input cases
                        checks_list.append(item)

    # set default Value for results path
    if report_file is None:
        report_file = "results.html"
    else:
        output_dir = os.path.dirname(report_file)
        if os.path.isdir(output_dir) == False:
            print("create results output dir : ", output_dir)

        try:
            os.makedirs(output_dir, 0o755, exist_ok=True)

        except OSError:
            pass

    # set default Value for report name
    if report_name is None:
        report_name = "Package License Checks"

    # set default Value for checksum algorithm for check 3
    if checksum_algorithm is None:
        checksum_algorithm = "MD5"
    else:
        checksum_algorithms=['MD5','SHA1','SHA256','SHA384','SHA512']   
        if not checksum_algorithm in checksum_algorithms:
            STATUS3_Total='ERROR'
            error3='Checksum algorithm is invalid'

    if component_names is None:
        component_names = "inputs.txt"
    else:
        input_dir = os.path.dirname(component_names)
        if os.path.isdir(input_dir) == False:
            print("create input dir : ", input_dir)

        try:
            os.makedirs(input_dir, 0o755, exist_ok=True)
            print("ok")
        except OSError:
            pass
    gen_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')


    #Initialize the qa_table
    header, rows = gen_func.skeleton_qa_table ()
    rows_number=0


    for checks in checks_list:
        match checks:
            case "1":
                ###********** CHECK 1***********
                title_check_presence_file, results_status_check_presence_file, results_error_check_presence_file = check1_existence_licenses_files()
                rows[rows_number].append(checks + title_check_presence_file)
                rows[rows_number].append(results_status_check_presence_file)
                rows[rows_number].append(results_error_check_presence_file)
                rows_number += 1
                print(rows)

            case "2":
            ###********** CHECK 2***********
                title_check_presence_file, results_status_check_presence_file, results_error_check_presence_file = check1_existence_licenses_files()
                print(rows)

                if results_status_check_presence_file != 'ERROR':
                    title_check_conformity, results_status_check_conformity, results_error_check_conformity = check2_conformity_license_files_templates()
                    rows[rows_number].append(checks + title_check_conformity)
                    rows[rows_number].append(results_status_check_conformity)
                    rows[rows_number].append(results_error_check_conformity)
                    rows_number += 1
                print(rows)

            case "3":
                html_file_path=frmw_dir_path +"\Package_license.html"
                #Parse table
                tableau,components, copyrights, licenses =check3.table_extract (html_file_path)
                print ('tableau:',tableau)
                print ('components:',components)
                print ('copyrights:',copyrights)
                print ('licenses:',licenses)

                #Retrieve ST components from the table
                st=check3.st_component (copyrights,components)
                print('component with st copyright:',st)

                #*************** Component existence in the frmw
                title_check_component_existence=".1: Component existence in the firmware and presence of LICENSE.md/.txt in its repository"
                #root, dirs, files, dic_dirs_files, status_check_component_existence, error_check_component_existence, status_presence_lic_in_each_component, error_presence_lic_in_each_component=check3.firmware_hierarchy(frmw_dir_path,component_names)
                root, dirs, files, results_status_check_component_existence, results_error_check_component_existence =check3.firmware_hierarchy(frmw_dir_path,component_names,st)
                print('error_check_component_existence',results_error_check_component_existence)

                #*************** Presence of LICENSE.md/.txt in components repositories
                title_check_licenses_presence=".2: Presence of LICENSE.md/.txt in components repositories"
                root, dirs, files, dic_dirs_files, results_status_presence_lic_in_each_component, results_error_presence_lic_in_each_component=check3.license_presence_each_component(frmw_dir_path,component_names,st)
                print('error_presence_lic_in_each_component',results_error_presence_lic_in_each_component)

                #*************** Check licenses values
                title_check_licenses_values=".3: Check licenses values"
                results_status_check_licenses_values, results_error_check_licenses_values, correct_license=check3.check_licenses_values(copyrights,licenses)
                print('correct_license',correct_license)

                #*************** TEMPLATES & CHECKSUMS
                template_licences_list=['Apache-2.0_LICENSE.txt','BSD-3-Clause_LICENSE.txt','MIT_LICENSE.txt','SLA0044_LICENSE.txt','SLA0044_LICENSE.md','SLA0047_LICENSE.txt','SLA0047_LICENSE.md']
                lcs_presence,licences_tmpl_dict_chks=check3.check_checksum_licenses_templates(frmw_dir_path,template_licences_list,checksum_algorithm)
                template_licences_list_with_cpr_declaration=['Apache-2.0_LICENSE.md','BSD-3-Clause_LICENSE.md','MIT_LICENSE.md'] #to add 'Apache-2.0_LICENSE.md' 
                #template_licences_list_with_cpr_declaration=['Apache-2.0_LICENSE.md','BSD-3-Clause_LICENSE_without_EOL.md','MIT_LICENSE.md'] ##added 01/03/2023
                #original md template checksums without any modification 
                print('original md template checksums without any modification')
                lcs_presence_md,licences_md_tmpl_dict_chks=check3.check_checksum_licenses_templates(frmw_dir_path,template_licences_list_with_cpr_declaration,checksum_algorithm)
                #md template checksums with replacing copyright lines with an empty text
                print('md template checksums with replacing copyright lines with an empty text')
                md_licences_tmpl_dict_chks=check3.check_checksum_MD_licenses_templates(frmw_dir_path,checksum_algorithm)
                license_cks= check3.check_checksum_licenses (dic_dirs_files,checksum_algorithm)
                print('license_cks',license_cks)
                #license_cks without copyright sentences:
                license_cks_without_copyright_sentences,l_paths_license_cks_without_copyright_sentences= check3.checksum_calcul_without_copyright(dic_dirs_files,checksum_algorithm)
                print('license_cks without copyright sentences',license_cks_without_copyright_sentences)
                print('PATHS license_cks without copyright sentences',l_paths_license_cks_without_copyright_sentences)

                title_cks_templates=".4: Comparison of checksum of different licenses that do not contain copyrights"
                title_cks_md_templates=".5: Comparison of checksum of licenses that contain copyrights"

                #test_md,test_txt=check3.test_result_checksum(license_cks_without_copyright_sentences,licences_tmpl_dict_chks,md_licences_tmpl_dict_chks)
                license_cks_without_copyright_sentences==check3.test_result_checksum(license_cks_without_copyright_sentences,licences_tmpl_dict_chks,md_licences_tmpl_dict_chks)

                family,st_cmpn_treated=check3.cpr_st_treatment(st)

                l_st_paths, st_license_cks_without_copyright_sentences=check3.checksum_list_st(st_cmpn_treated,license_cks_without_copyright_sentences,l_paths_license_cks_without_copyright_sentences)

                #*************** URLS LICENCES
                results_status_urls_licenses = ''
                results_error_urls_licenses = ''
                error_st_component_incorrect_license_name=''
                error_correct_website_license=''

                st_license_name=check3.st_license_name(tableau)
                st_component_correct_license_name, st_component_incorrect_license_name=check3.st_license_name_verification(st_license_name)
                #If licenses names aren't correct
                lic_incorrcet_name=''
                if st_component_incorrect_license_name:
                    #status_licenses_names ='ERROR'
                    results_status_urls_licenses ='WARNING'
                    for itr_incorrcet_name in st_component_incorrect_license_name:
                        if len (lic_incorrcet_name)==0:
                            lic_incorrcet_name=lic_incorrcet_name+' '+itr_incorrcet_name
                        else:
                            lic_incorrcet_name=lic_incorrcet_name+', '+itr_incorrcet_name    
                        
                    error_st_component_incorrect_license_name="Incorrect licenses names:"+lic_incorrcet_name
                print ('error_st_component_incorrect_license_name',error_st_component_incorrect_license_name)

                url_parsing,corrcet_licenses_names_url_valid=check3.all_url_validation(st_component_correct_license_name)
              

                if corrcet_licenses_names_url_valid==True:
                    st_component_website_parse,correct_website_license=check3.website_parsing(st_component_correct_license_name) 
                    print('st_component_website_parse',st_component_website_parse)
                    print('correct_website_license',correct_website_license)
                    if correct_website_license == False:
                        #status_correct_website_license='ERROR'
                        results_status_urls_licenses='ERROR'
                        error_correct_website_license='There are incorrect website licences.'
                    else:
                        #status_correct_website_license='OK'
                        if len(results_status_urls_licenses)==0:
                            results_status_urls_licenses='OK'
                            results_error_urls_licenses = 'NA'
                        else:
                            results_status_urls_licenses ='WARNING'    
                else:
                    #status_licenses_names_url_valid='ERROR'
                    results_status_urls_licenses='ERROR'
                    results_error_urls_licenses = 'There are not valid URLs.'

                if results_status_urls_licenses == 'ERROR':
                    if len(error_st_component_incorrect_license_name) >0 and len(error_correct_website_license) >0:
                        results_error_urls_licenses = error_st_component_incorrect_license_name+' '+error_correct_website_license
                    elif len(error_st_component_incorrect_license_name) >0 and len(error_correct_website_license) ==0:
                        results_error_urls_licenses = error_st_component_incorrect_license_name
                    elif len(error_st_component_incorrect_license_name) ==0 and len(error_correct_website_license) >0:   
                        results_error_urls_licenses = error_st_component_incorrect_license_name 
                elif results_status_urls_licenses =='WARNING':  
                    results_error_urls_licenses = error_st_component_incorrect_license_name      


                title_url_licenses=".6: Check of URL licences"

                #*************** Release Notes
                word='license'
                l_release_notes=['Release_Notes.md','Release_Notes.html']
                lic_existence= gen_func.files_presence_in_directory(frmw_dir_path, l_release_notes)
                print (lic_existence)
                results_status_rl_notes, results_error_rl_notes=check3.check_license_in_release_notes(frmw_dir_path,lic_existence,word)
                title_release_notes=".7: The Release_notes.md/html files don\'t contain the word \"license\""


                #************************************************************ HTML Result ************************************************************ 
                title_check_presence_file, results_status_check_presence_file, results_error_check_presence_file = check1_existence_licenses_files()

                if results_status_check_presence_file != 'ERROR':
                    #*************** Component existence in the frmw
                    rows[rows_number].append(checks +title_check_component_existence)
                    rows[rows_number].append(results_status_check_component_existence)
                    rows[rows_number].append(results_error_check_component_existence)
                    rows_number += 1
                    print(rows)
                    #*************** Presence of LICENSE.md/.txt in components repositories
                    rows[rows_number].append(checks +title_check_licenses_presence)
                    rows[rows_number].append(results_status_presence_lic_in_each_component)
                    rows[rows_number].append(results_error_presence_lic_in_each_component)
                    rows_number += 1
                    print(rows)
                    #*************** Check licenses values
                    rows[rows_number].append(checks +title_check_licenses_values)
                    rows[rows_number].append(results_status_check_licenses_values)
                    rows[rows_number].append(results_error_check_licenses_values)
                    rows_number += 1
                    print(rows)
                    #*************** Comparison of checksum of different licenses that do not contain copyrights
                    rows[rows_number].append(checks +title_cks_templates)
                    rows[rows_number].append('test cks temp')
                    rows[rows_number].append('test cks temp')
                    rows_number += 1
                    print(rows)
                    #*************** Comparison of checksum of licenses that contain copyrights
                    rows[rows_number].append(checks +title_cks_md_templates)
                    rows[rows_number].append('test cks md temp')
                    rows[rows_number].append('test cks md temp')
                    rows_number += 1     
                    print(rows)           
                    #*************** URLS LICENCES
                    rows[rows_number].append(checks +title_url_licenses)
                    rows[rows_number].append(results_status_urls_licenses)
                    rows[rows_number].append(results_error_urls_licenses)
                    rows_number += 1     
                    print(rows) 
                    #*************** Release Notes
                    rows[rows_number].append(checks +title_release_notes)
                    rows[rows_number].append(results_status_rl_notes)
                    rows[rows_number].append(results_error_rl_notes)
                    rows_number += 1     
                    print(rows) 
                    

            case default:

                title_check_presence_file, results_status_check_presence_file, results_error_check_presence_file = check1_existence_licenses_files()

                rows[rows_number].append(str(rows_number+1) + title_check_presence_file)

                rows[rows_number].append(results_status_check_presence_file)
                rows[rows_number].append(results_error_check_presence_file)
                print(rows)
                rows_number += 1


                if results_status_check_presence_file != 'ERROR':

                    title_check_conformity, results_status_check_conformity, results_error_check_conformity = check2_conformity_license_files_templates()
                    rows[rows_number].append(str(rows_number+1) + title_check_conformity)
                    rows[rows_number].append(results_status_check_conformity)
                    rows[rows_number].append(results_error_check_conformity)

                    rows_number += 1
                    rows[rows_number].append(str(rows_number+1) )
                    rows[rows_number].append('test check3')
                    rows[rows_number].append('test check3')
                print(rows)

    generate_html(gen_date, header, rows, report_name, report_file)
    if results_status_check_presence_file == 'ERROR':
        sys.exit(1)