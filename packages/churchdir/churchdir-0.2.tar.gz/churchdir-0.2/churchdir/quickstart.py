#!/usr/bin/env python
"""
Created on Sat Sep 27 03:35:06 2014

@author: kcarlton

From a CSV (comma separated values) file containing information for a 
directory (name, address, city, state, phone, etc.), create an html file and
a vCard file from that information.

Typically this program is run from your personal computer; after which the
results are copied, usually with an ftp program like filezilla, up to a web
site.

The location on the internet where directory html file is stored should be 
password protected, but the location on the internet where photos are stored
should NOT be password protected (otherwise the photos derived for a vCard file
won't display).

This program can be run from a command line, or can be run from a python 
interactive shell.  For example, from a command line:

C:\> python direc /h
    
(With Linux, use a dash (-); With Windows you a slash (/)).  And from a python 
interactive shell:

>>> direc("-h")    
    
Both show help about how to use the program.  
"""

from __future__ import division
from __future__ import print_function
import os
import datetime
import csv
from operator import itemgetter
import sys
from colorama import init, deinit, Fore, Back, Style
init()

# these comments are put into the conf.py file, and they are uses when 
# interrogating the user for data input.
comment = {
'input':
    ('# Input file name (csv format).  If the file is not found, a sample file will\n'
     '# be created.  You can edit this file using a spreadsheet program and add your\n'
     '# address list. The value must be surrounded by quotes (\" or \', \' preferred).\n'),
'output':
    ('# Output file name (html format).\n'),   
'vcard':
    ('# Output vcard file name (vcf format).  This file can be imported into an\n'
     '# address book.\n'),
'csv_url':
    ('# URL address for the csv file.  This is used to create a link to the csv file\n'
    '# (or a copy thereof) that you used for your input file. Therefore you will be\n'
    '# providing a link to allow users to download the csv file (which can be imported\n'
    '# into an address book.)\n'),
'vcard_url':
    ('# URL address from for the vcard file.  This is used to create a link to the\n'
    '# vcard file (or a copy thereof) that you created. Therefore you will be\n'
    '# providing a link to allow users to download the vcard file.\n'),    
'number_table_columns':
    ('# Number of columns to be shown in the directory (i.e., in the html file)\n')
}


def write_default_config():
    ''' If conf.py doen't exist, write one.  The file is put in the folder that
    is currently active.
    ''' 
    cwd = os.getcwd()
    config_pathname = os.path.join(cwd, 'conf.py')                                
    s = '# Default settings.  Edit the appropriate lines.\n\n'  
    s += comment['input']
    s += "input = 'directory.csv'\n\n\n" 
    s += comment['number_table_columns']
    s += 'number_table_columns = 2  \n\n\n' 
    s += comment['output']
    s += "output = 'index.html'\n\n\n"           
    s += comment['vcard']
    s += "vcard = 'directory.vcf'\n\n\n"       
    s += comment['csv_url']
    s += "csv_url = ''\n\n\n"      
    s += comment['vcard_url']
    s += "vcard_url = ''\n\n\n" 

    s += '# Header lines.  Add text and/or html code to the beginning of the\n' 
    s += '# directory. (Adding <br> within the value means "new line")\n'
    s += '# The value must be surrounded by quotes (\" or \', \' preferred).\n'
    s += "header_line_1 = '<h3>Directory</h3>'\n"
    s += "header_line_2 = ''\n" 
    s += "header_line_3 = ''\n"
    s += "header_line_4 = ''\n"
    s += "header_line_5 = ''\n\n\n"

    s += '# Footer lines.  Add text and/or html code to the end of the\n' 
    s += '# directory.  (Adding <br> within the value means "new line")\n'
    s += '# The value must be surrounded by quotes (\" or \', \' preferred).\n'
    s += "footer_line_1 = ''\n"
    s += "footer_line_2 = ''\n"
    s += "footer_line_3 = ''\n"
    s += "footer_line_4 = ''\n"
    s += "footer_line_5 = ''\n\n\n"

    s += '# Note: Add files named favicon.gif (16x16 or 32x32) and background.jpg in\n'
    s += '# your working directory to add a background to your web page and an icon\n'
    s += '# that shows in the tab of a web browser.'                         
                                                                   
    outfile = open(config_pathname, 'w') # open the output file for writing.
    outfile.write(s)  # place all the garnered html code into the output file.
    outfile.close() # done... close the file.
    print(Fore.GREEN + '\n# A configuration file (conf.py) was NOT found, so one was created for you.')
    print('# You may edit this file with a text editor (like notepad) for the program to' )
    print('# better suit your needs.')
    print(Style.BRIGHT + 'file created: ' + config_pathname  + Style.RESET_ALL)
    
    
def write_sample_csv():
    ''' Writes a default directory.csv file in the same folder as the program
    file.
    '''  
    s = ('Last Name,First Name,Middle Name,Suffix,Member,Home Street,' + 
        'Home City,Home State,Home Postal Code,Business Phone,' + 
        'Home Phone,Mobile Phone,E-mail Address,Photo URL,Photo secondary,' +
        'Spouse,Children,Notes,Job Title\n')
    s += ('Doe,Jane,,,Y,123 Elm St.,Lafayette,IN,47906,,765-444-1234,,' +
          'johnandjanedoe@aol.com,Doe-Jane.png,Doe-family.jpg,John,"Jack,' +
          'Jill",,\n')
    s += ('Doe,John,,,Y,123 Elm St.,Lafayette,IN,47906,,765-444-1234,,' +
          'johnandjanedoe@aol.com~,Doe-John.png,Doe-family.jpg,Jane,"Jack,' +
          'Jill",,\n')
    outfile = open(input, 'w') # open the output file for writing.
    outfile.write(s)  # place all the garnered html code into the output file.
    outfile.close() # done... close the file.
    print(Fore.GREEN + Style.BRIGHT  + 'file created: ', input, Style.RESET_ALL, '\n')
    
    
def test_csv_file(names):
    ''' On the top of each column within the csv file is the name of the
    columnn (Last Name, First Name, Middle Name, etc.).  Test and see if all
    the appropriate names are present.
 
    argements:
    names -- list of column headers that comes from the csv file, i.e.,
    ['Last Name', 'First Name', etc.]    
    
    '''    
    appropriate_names = ['Last Name', 'First Name', 'Middle Name', 'Suffix',
             'Member', 'Home Street', 'Home City', 'Home State',
             'Home Postal Code', 'Business Phone', 'Home Phone', 
             'Mobile Phone', 'E-mail Address', 'Photo URL', 'Photo secondary',
             'Spouse', 'Children', 'Notes', 'Job Title']            
    s1 = set(names)
    s2 = set(appropriate_names)   
    if len(s2 - s1) > 0:
        print("\nYour csv file's structure is not correct. These categories "
              'not being present \nand/or not utilized may be part of the problem: ')
        print(list(s2 - s1))
        return list(s2 - s1)
        #raise Exception('program stopped at "test_csv_file()... invalid csv file.') 
    

def read_csv():
    ''' Extract data from a csv file that contain's directory raw info.
    
    Global variable:
    input -- where the directory csv file is located.
    
    Returns a sorted list.  Each item of the list is a person's data in
    dictionary form such as {'First Name': 'Ken', 'Last Name': ;Carlton', 
    'Home Street': '117 Tamiami Dr.', etc.}
    '''
    global input                      
    with open(input, 'r') as cvsfile:
        c = csv.DictReader(cvsfile) # [{'Last Name':'Doe...}, {'Last name...}]
        d = []
        for i in c:  # i = {'Last Name':' Carlton ', 'First Name':'Ken ', etc.}
           e = {} # transfer dic i to e, but with spaces removed
           for j in i:  # j = 'family name' and so forth
               if i[j]:
                   e[j] = i[j].strip()  # remove leading and trailing spaces
           d.append(e) 
    k = d[0].keys() # list of the column header names
    missing = test_csv_file(k) # find missing missing column header names            
    appropriate_names = ['Last Name', 'First Name', 'Middle Name', 'Suffix',
             'Member', 'Home Street', 'Home City', 'Home State',
             'Home Postal Code', 'Business Phone', 'Home Phone', 
             'Mobile Phone', 'E-mail Address', 'Photo URL', 'Photo secondary',
             'Spouse', 'Children', 'Notes', 'Job Title']
    for i in range(len(d)):
        for n in appropriate_names:
            if not n in d[i]:
                d[i][n] = ''            
    return sorted(d, key=itemgetter('Last Name', 'First Name', 'Middle Name')) 


def generate_directory_beginning():
    ''' Generate html code for the first part of the directory.
    
    Global variables:
    csv_url
    vcard_url
    
    Returns a string (html code)
    '''
    global header_line_1, header_line_2, header_line_3, header_line_4, header_line_5
    now = datetime.datetime.now()
    todaysDate = now.strftime('%m-%d-%Y')
    s = '<!DOCTYPE html>' + '\n'
    s += '<html>' + '\n'
    s += '<head>' + '\n'
    s += '<title>directory</title>' + '\n'
    s += '<meta name="description" content="Church Directory">' + '\n'
    s += '<meta name="ROBOTS" content="NOINDEX, NOFOLLOW">' + '\n'
    s += '<meta http-equiv="content-type" content="text/html; charset=UTF-8">' + '\n'
    s += '<meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8">' + '\n'
    s += '<meta http-equiv="expires" content="0">' + '\n'
    s += '<meta name="viewport" content="width=device-width, initial-scale=1">' + '\n'
    s += '<link rel="icon" type="image/gif" href="http://directory.c-c-church.net/favicon.gif"/>\n'  
    s += '<style>'
    s += 'img.box'
    s += '{'
    s += 'border:3px solid green;'
    s += 'margin-right:3px;'
    s += 'margin-bottom:3px;'
    s += 'float:left;'
    s += '}'
 
    # ref http://davidwalsh.name/css-page-breaks:
    s += '@media all {' + '\n'
    s += '	.page-break	{ display: none; }' + '\n'
    s += '}' + '\n'
    s += '@media print {' + '\n'
    s += '	.page-break	{ display: block; page-break-before: always; }' + '\n'
    s += '}' + '\n'       
    
    s += '</style>'      
    s += '</head>' + '\n'
    s += '<body background="background.jpg">' + '\n'
    if header_line_1:
        s += header_line_1
    if header_line_2:
        s += header_line_2
    if header_line_3:
        s += header_line_3
    if header_line_4:
        s += header_line_4
    if header_line_5:
        s += header_line_5
    s += 'Directory last updated: ' + todaysDate  + '.\n'
    if vcard_url or csv_url:
        s += '<br>For importing to mobile phones or email contact lists: '
    if vcard_url:
        s += '<a href="' + vcard_url + '">Download vCard</a>'
    if csv_url:
        s += ', <a href="' + csv_url + '">Download CSV file</a>.\n'
    s += '<hr>'
    return s


def compile_persons_data(persons_data):
    ''' Take a person's info, obtained from the read_csv function, and create
    html code from it.  
    
    Keyword arguments:
    persons_data -- a dictionary containing a person's info for the direcotory.
    
    persons_data is a dictionary similar to:
    {'Business Phone': '',
     'Children': '',
     'E-mail Address': 'kcarlton@c-c-church.net',
     'First Name': 'Ken',
     'Home City': 'West Lafayette',
     'Home Phone': '765-416-3142',
     'Home Postal Code': '47906',
     'Home State': 'IN',
     'Home Street': '107 Tamiami Tr.',
     'Job Title': '',
     'Last Name': 'Carlton',
     'Member': 'Y',
     'Middle Name': '',
     'Mobile Phone': '',
     'Notes': '',
     'Photo URL': 'Carlton-Ken.png',
     'Spouse': 'Dottie',
     'Suffix': ''}
    
    Returns a string (html code).  (String is written with hcard data which
    can be used to generate a vcard  
    ref: http://http://microformats.org/code/hcard/creator)
    '''
    pd = persons_data # pd is a dictionary containing a person's data
    id_list = ['hcard', pd['First Name'], pd['Middle Name'],pd['Last Name'], pd['Suffix']]
    id_str = '"' + '-'.join(id_list).replace('--', '-').strip('-') + '"'
    s = '\n<div id=' + id_str + ' class="vcard">\n'
    #if url_for_photos:
    s += compile_persons_photo_data(pd)
    s += '    <b><span class="fn">'
    if pd['Middle Name'] and pd['Suffix']:
        s += ' '.join([pd['First Name'], pd['Middle Name'], pd['Last Name'], pd['Suffix']])
    elif pd['Suffix']:
        s += ' '.join([pd['First Name'], pd['Last Name'], pd['Suffix']])
    elif pd['Middle Name']:
        s += ' '.join([pd['First Name'], pd['Middle Name'], pd['Last Name']])
    else:
        s += ' '.join([pd['First Name'], pd['Last Name']])
    s += '</span>'
    if ((pd['Member'].strip() + ' ')[0].upper() == 'Y'
         or (pd['Member'].strip() + ' ')[0] == '*'):
        s += '*'
    s += '</b>\n'
    s += '    <div class="adr">\n'
    s += '        <div class="street-address">' + pd['Home Street'] +'</div>\n'
    if pd['Home City']:
        s += '        <span class="locality">' + pd['Home City'] +'</span>,\n'
    s += '        <span class="region">' + pd['Home State'] + '</span>\n'
    s += '        <span class="postal-code">' + pd['Home Postal Code'] + '</span>\n'
    s += '    </div>\n'
    if pd['Home Phone']:
        s += '    <div class="tel">\n'
        s += '        ' + pd['Home Phone'] + '<span class="type"> home</span>\n'
        s += '    </div>\n'
    if pd['Mobile Phone']:
        s += '    <div class="tel">\n'
        s += '        ' + pd['Mobile Phone'] + '<span class="type"> cell</span>\n'
        s += '    </div>\n'
    if pd['Business Phone']:
        s += '    <div class="tel">\n'
        s += '        ' + pd['Business Phone'] +'<span class="type"> office</span>\n'
        s += '    </div>\n'
    s += '    <div class="note">\n'
    if pd['Spouse']:
        s += '        <div class="note1">Spouse: ' + pd['Spouse'] + ' </div>\n'
    if pd['Children']:
        s += '        <div class="note2">Children: ' + pd['Children'] + ' </div>\n'
    if pd['Notes']:
        s += '        <div class="note3">' + pd['Notes'] + ' </div>\n'
    s += '    </div>\n'
    if pd['Job Title']:
        s += '    <div class="title">Title: ' + pd['Job Title'] + ' </div>\n'
    s += '    <a class="email" href="mailto:'
    s +=          pd['E-mail Address'] +'">'
    s +=          pd['E-mail Address'] +'</a>\n'
    s += '</div>\n'
    s += '<br>\n'
    return s
    

def compile_persons_photo_data(persons_data):
    ''' Generate html code for a person's photo.  Only photos with jpg of png
    format are valit.
    
    Global variables:
    persons_data -- a dictionary containing a person's info for the direcotory.
    
    Returns a string (html code).  If no photo, return a nul string ('')
    '''     
    pd = persons_data
    photo_alt = 'photo not found'
    photo_html = ''
   
    src = pd['Photo URL'].strip()
    if pd['Photo URL'].strip() and pd['Photo secondary'].strip():
        url_photo_2 = pd['Photo secondary'].strip()
        photo_html = ('<a href="' + url_photo_2
            + '" title="Click to see secondary photo. "\n'
            + 'style="background-color:#FFFFFF;color:#000000;text-decoration:none"> '
            + '<img class="box" src="' + src + '" alt="' + photo_alt + '"></a>\n'
            + '</div>\n')
    elif pd['Photo URL'].strip():
        photo_html = ('    <img style="float:left; margin-right:4px" src="'
                + src + '" alt="' + photo_alt + '" class="photo"/>\n')
    else:
        photo_html = ''
    
    return photo_html

    
def generate_directory_ending():
    ''' Finishes off the html code for the directory.
    
    Returns: A string (html code)
    '''
    s = '<hr>' + '\n'
    if footer_line_1:
        s += footer_line_1
    if footer_line_2:
        s += footer_line_2
    if footer_line_3:
        s += footer_line_3
    if footer_line_4:
        s += footer_line_4
    if footer_line_5:
        s += footer_line_5
    s += '\n</body>' + '\n'
    s += '</html>' + '\n'
    return s
    

def compile_vcard_data(persons_data):
    ''' Take a person's directory data and create a vcard for that person.'''
    pd = persons_data
    s = 'BEGIN:VCARD\n'
    s += 'NAME:directory\n'
    s += 'VERSION:3.0\n'
    #Family; Given; Middle; Prefix; Suffix.
    s += ('N;CHARSET=utf-8:' + pd['Last Name'] + ';' + pd['First Name']
          + ';' + pd['Middle Name'] + ';;' + pd['Suffix'] + '\n')
    if pd['Middle Name'] and pd['Suffix']:
        s += ('FN;CHARSET=utf-8:' + pd['First Name'] + ' ' +
              pd['Middle Name'] + ' ' + pd['Last Name'] + ' ' + 
              pd['Suffix'] + '\n')
    elif pd['Middle Name'].strip():
        s += ('FN;CHARSET=utf-8:' + pd['First Name'] + ' ' +
              pd['Middle Name'] + ' ' + pd['Last Name'] + '\n')
    elif pd['Suffix'].strip():
        s += ('FN;CHARSET=utf-8:' + pd['First Name'] + ' ' +
              pd['Last Name'] + ' ' + pd['Suffix'] + '\n')    
    else:
        s += ('FN;CHARSET=utf-8:' + pd['First Name'] + ' '
              + pd['Last Name'] + '\n')
    if pd['Job Title']:
        s += 'TITLE;CHARSET=utf-8:' + pd['Job Title']
    if pd['E-mail Address']:
        s += 'EMAIL:' + pd['E-mail Address'] + '\n'
    if pd['Home Street']:
        s += ('ADR;CHARSET=utf-8:;;' + pd['Home Street'] + ';' +
              pd['Home City'] + ';' + pd['Home State'] + ';' +
              pd['Home Postal Code'] + '\n')
    if pd['Home Phone']:
        s += 'TEL;TYPE=home:' + pd['Home Phone'] + '\n'
    if pd['Mobile Phone']:
        s += 'TEL;TYPE=cell:' + pd['Mobile Phone'] + '\n'
    if pd['Business Phone']:    
        s += 'TEL:' + pd['Business Phone'] + '\n'
    s2 = ''
    if pd['Spouse']:
        s2 += 'Spouse: ' + pd['Spouse'] + '   '
    if pd['Children']:
        s2 += 'Children: ' + pd['Children'] + '   '
    if pd['Notes']:
        s2 += pd['Notes']
    if s2:
        s += 'NOTE;CHARSET=utf-8:' + s2.replace(',', '\,')  + '\n'
    if pd['Photo URL'].strip():
        src = pd['Photo URL'].strip()
        s += 'PHOTO;VALUE=uri:' + src + '\n'
    s += 'END:VCARD\n\n' 
    return s                    


def create_directory():
    ''' Creates a directory of people's names, addresses, etc., and places that 
    info in an html formated file.  The information for this directory is
    derived from a csv (comma delimited format) file that contains the raw
    data.  This function executes the following fucnctions:
    
    1. read_csv
    2. generate_directory_beginning
    3. compile_persons_data
    4. compile_persons_photo_data
    5. generate_directory_ending
     
    Returns: Nothing (instead creates an html file)   
    '''   
    global input, output            
    input = os.path.normpath(input)
    output = os.path.normpath(output)
    csv_data = read_csv()
    s = generate_directory_beginning()
    s += '<table border="0" cellpadding="5" width="100%">\n'
    j = 1
    for persons_data in csv_data:
        if j == 1:  # if column = 1, then start it with the <tr> html code
            s += '<tr>\n'
        s += '<td>'
        s += compile_persons_data(persons_data) # html string for person
        s += '</td>\n'
        j += 1
        if j > number_table_columns: # if a row is finished, close it off
            s += '</tr>\n'
            j = 1
    if j > 1:  # finish up the table with blank cells if necessary
        for k in range(10):
            if j == 1:
                s += '<tr>\n'
            s += '<td>\n'
            s += '</td>\n'
            j += 1
            if j > number_table_columns:
                s += '</tr>\n'
                break
    s += '</table>\n' # the table is complete
    s += generate_directory_ending() # finish off the code for the html file.
    s = s.replace('*',
        '<span style="color:#FF0000"><small><sup>*</sup></small></span>')
    s = s.replace('~</a>',
        '<span style="color:#FF0000"><small><sup>~</sup></small></span></a>')
    outfile = open(output, 'w') # open the output file for writing.
    outfile.write(s)  # place all the garnered html code into the output file.
    outfile.close() # done... close the file.
    print(Style.BRIGHT + 'created: ' + output + Style.RESET_ALL) # verify where you put your html file.

    
def create_vcard():
    ''' Creates a vcard file (with the extension vcf) of people's names, 
    addresses, etc. The information for this file is derived from a csv 
    (comma delimited format) file that contains the raw data.  This function
    executes the following fucnctions:
    
    1. read_csv
    2. compile_vcard_data

    Returns: Nothing (instead creates an vcf file)   
    '''
    global input, vcard    
    input = os.path.normpath(input)
    vcard = os.path.normpath(vcard)
    csv_data = read_csv()
    s = ''
    for persons_data in csv_data:
        s += compile_vcard_data(persons_data)
    print(Style.BRIGHT + 'created: ' + vcard + Style.RESET_ALL)
    outfile = open(vcard, 'w') # open the output file for writing.
    outfile.write(s)  # place all the garnered html code into the output file.
    outfile.close() # done... close the file.    

   
def remove_duplicates(values):
    ''' Remove duplicate items from a list.  (For example,
    ['jdoe@example.com', 'rsmith@comcast,com', 'jdoe@example.com'])
    
    Keyword argument: value (type: list)
    
    Returns a list (For example, ['jdoe@example.com', 'rsmith@comcast,com'])
    
    (This function is independant of other functions, except the "no_photo"
    function, of the module.  It is a directory manager's tool.)
    ''' 
    output = []
    seen = set()
    for value in values:
	  # If value has not been encountered yet,
	  # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

   
def no_photo(string=False, str_separator=', '):
    ''' Make a list of email addresses for people without their photo in the
    church directory
    
    Arguments:
    string: if set to True, then a string returned instead of a list
    str_separator: When string=True, the this element placed between valuse
    
    Returns a list, unless string=True, then returns a string

    (This function is independant of other functions of the module.  
    It is a directory manager's tool.)    
    '''
    csv_data = read_csv()
    email_list = []
    for persons_data in csv_data:
        if (persons_data['E-mail Address'] 
                and persons_data['E-mail Address'][-1] != '~'
                and not persons_data['Photo URL']):
            email_list.append(persons_data['E-mail Address'])
    email_list = remove_duplicates(email_list)
    if string:
        return str_separator.join(email_list)
    else:
        return email_list
        

def set_global_variables():
    ''' Store file locations, etc.  First the configuration file, 
    conf.py, is read in.  Then if any new, differing info was supplied
    by the user on the command line, that info is used instead of info
    derived from the configuration file.  This information is stored in
    global variables (info from the variable can be obtained from outside of
    this function)
    '''
    global input, number_table_columns, output   
    global vcard, csv_url, vcard_url
    global header_line_1, header_line_2, header_line_3
    global header_line_4, header_line_5, footer_line_1, footer_line_2
    global footer_line_3, footer_line_4, footer_line_5
    
    cwd = os.getcwd()
    config_pathname = os.path.join(cwd, 'conf.py')                           
    if not os.path.exists(config_pathname):
        write_default_config()
        
    config_pathname_pyc = os.path.join(cwd, 'config.pyc')
    if os.path.exists(config_pathname_pyc):
        os.remove(config_pathname_pyc)
    
    sys.path.insert(1, cwd)
    import conf
    del sys.path[1]  


    def get_variable(comment, question, default):
        ''' variable = Name of variable that user gets asked for.
        comment = a comment to preceed the question.
        question = Statement or question preceeding the request for user input.
        default = default value that comes from the conf.py file.
        
        All argements are strings.  Defaults come from the are derived type
        import the conf.py file just above.
        '''
        print(comment, end="")
        if not default:
            print(Style.BRIGHT + question + ' <' + "''" + '>: ' + Style.RESET_ALL, end="")
        else:
            print(Style.BRIGHT + question + ' <' + str(default) + '>: ' + Style.RESET_ALL, end="")
        try:    
            try:
                answer = raw_input() # if python 2.x
            except NameError:
                answer = input()     # if python 3.x
        except KeyboardInterrupt:
            print('\n\nprogram aborted\n')
            sys.exit()
        print("")
        if answer.strip():
            variable = answer
        else:
            variable = default
        return variable
        
    print('\n# You will be asked six questions.  Hit Enter to accept the default.  Hit\n'
          '# Ctrl-C to exit the questioning (Command-C on Mac OS).\n')
                 
    input = get_variable(comment['input'], 
                         'csv file to  process', conf.input)
    input = os.path.normpath(input)
    
    if not os.path.exists(input):
        print(Fore.GREEN + '# A csv file was NOT found, '
              'so one was created for you.  You may edit this')
        print('# file with a spreadsheet program like Excel in order to add '
               'your own addresses.' + Style.RESET_ALL) 
        write_sample_csv() 

    number_table_columns = get_variable(comment['number_table_columns'], 
                            'number of columns', conf.number_table_columns)                                                         
    output = get_variable(comment['output'], 
                          'output file name', conf.output)
    vcard = get_variable(comment['vcard'], 
                         'output vcard file name', conf.vcard)
    csv_url = get_variable(comment['csv_url'], 
                           'url address for the csv file', conf.csv_url)
    vcard_url = get_variable(comment['vcard_url'], 
                             'url address for vcard file', conf.vcard_url)
                            
    header_line_1 = conf.header_line_1
    header_line_2 = conf.header_line_2
    header_line_3 = conf.header_line_3
    header_line_4 = conf.header_line_4
    header_line_5 = conf.header_line_5    
    footer_line_1 = conf.footer_line_1
    footer_line_2 = conf.footer_line_2 
    footer_line_3 = conf.footer_line_3 
    footer_line_4 = conf.footer_line_4 
    footer_line_5 = conf.footer_line_5                  
                              

def main():
    '''When the program is initiated from the command line, as is intended
    for this program to be used, this function is the first to run and thereby
    get the ball rolling.
    '''
    set_global_variables()
    if output:
        create_directory()
    if vcard:
        create_vcard() 
        
    cwd = os.getcwd()
    config_pathname_pyc = os.path.join(cwd, 'conf.pyc')
    try:
        os.remove(config_pathname_pyc)
    except OSError:
        pass
    deinit() # ref: https://pypi.python.org/pypi/colorama
    
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)    
    
    global output
    output = os.path.normpath(output)
    abspath = os.path.abspath(output)
    dirname = os.path.dirname(abspath)
    background = os.path.join(dirname, 'background.jpg')
    favicon = os.path.join(dirname, 'favicon.gif')
    if not os.path.exists(background):
        touch(background)
    if not os.path.exists(favicon):
        touch(favicon)
        
    
                  
    
if __name__ == '__main__': 
    main()



