# web_aikif.py	written by Duncan Murray 25/5/2014
# web interface for AIKIF
import sys
import os

print ("sys.version = ", sys.version)
print ("os.getcwd() = ", os.getcwd())

from os import environ

#AIKIF_WEB_VERSION = "PROD"
AIKIF_WEB_VERSION = "DEV"
AIKIF_VERSION_NUM = "Version 0.1.1 (alpha) - updated 27-May-2014"

import aikif.web_app.web_utils as web

import flask
from flask import Flask
from flask import request
    
app = Flask(__name__)
menu = [
	['/',        'Home',     'This is the admin web interface for AIKIF (Artificial Intelligence Knowledge Information Framework)'],
	['/todo',    'Todo',     'Project overview showing current list of tasks being worked on'],
	['/data',    'Data',     'Shows the available data sets for AIKIF'],
	['/agents',  'Agents',   'Describes the agents capabilities, and last run status'],
	['/programs','Programs', 'Details of the modules in AIKIF'],
	['/about',   'About',    'About AIKIF and author contact']
	]


###################### HELPER FUNCTIONS#################
def start_server():
	if AIKIF_WEB_VERSION == "DEV":
		print("WARNING - DEBUG MODE ACTIVE")
		app.debug = True	# TURN THIS OFF IN PRODUCTION
	app.run()

###################### ROUTING #########################

@app.route("/")
def page_home():
	txt = aikif_web_menu()
	txt += web.build_search_form()
	
	txt += "<H3>Pages on this site</h3><TABLE width=80% border=0 align=centre>\n"
	for m in menu:
		txt += '<TR><TD><a href="' + m[0] + '">' + m[1] + '</a></td><td>' + m[2] + '</td></tr>\n'
	txt += "</table><BR>\n"
	txt += "<H3>Status</h3>\n"
	txt += "Pre-Alpha stage\n"
	txt += "<BR><BR>\n"
	txt += get_footer()
	return txt

@app.route('/', methods=['POST'])
def search_post():
	search_text = request.form['search_text']
	txt = aikif_web_menu()
	txt += web.build_search_form()
	import page_search
	txt += page_search.get_page(search_text)
	return txt

	
@app.route("/todo")
def page_todo():
	txt = aikif_web_menu('Todo')
	txt += web.build_search_form()
	txt += "<H3>Dev Tasks</h3>\n"
	txt += "<LI>get basic web functionality working in this app web_aikif</LI>\n"
	txt += "<LI>Split to standard MVC layout once implemention works</LI>\n"
	txt += "<LI>check install of Python 2.7 and 3.3, ensure startup checks this</LI>\n"
	txt += "<H3>Data Tasks</h3>\n"
	txt += "<LI>confirm overwrite of existing data files by checking source of creation (ok to overwrite if done via Create_AIKIF.py)</LI>\n"
	txt += "<LI>collect data output from existing proc_*.py needs to be properly integrated</LI>\n"
	txt += "<LI>finish function to completely import random spreadsheet</LI>\n"
	txt += "<H3>Config Tasks</h3>\n"
	txt += "<LI>get webserver running, deploy to restricted site</LI>\n"
	txt += "<LI>schedule collection tasks to run daily</LI>\n"
	txt += "<BR><BR>\n"
	txt += get_footer()
	return txt

@app.route("/data")
def page_data():
	txt = aikif_web_menu('Data')
#	try:
	import page_data
	txt += page_data.get_page()
#	except:
#		txt += page_error('data')
	txt += get_footer()
	return txt

@app.route("/data/<dataFile>")
def page_data_show(dataFile):
	txt = aikif_web_menu('Data')
	import page_data
	txt += page_data.get_page(dataFile)
	txt += get_footer()
	return txt
	
	

@app.route("/agents")
def page_agents():
	txt = aikif_web_menu('Agents')
	import page_agents as agt
	txt += agt.get_page()
	txt += get_footer()
	return txt
	
@app.route("/programs")
def page_programs():
	txt = aikif_web_menu('Programs')
	import page_programs as prg
	txt += prg.get_page()
	return txt
	
@app.route("/programs/rebuild")
def page_programs_rebuild():
	txt = aikif_web_menu('Programs')
	import page_programs as prg
	prg.rebuild()
	txt += prg.get_page()
	return txt
	
	return txt

@app.route("/about")
def page_about():
	txt = aikif_web_menu('About')
	import page_about as abt
	txt += abt.get_page()
	txt += get_footer()
	return txt

	
def page_error(calling_page):
	txt = '<BR><BR>'
	txt += '<H2>Error - problem calling ' + calling_page + '</H2>'
	txt += get_footer()
	return txt
	
def aikif_web_menu(cur=''):
	""" returns the web page header containing standard AIKIF top level web menu """
	pgeHdg = ''
	pgeBlurb = ''
	if cur == '': 
		cur = 'Home'
	txt = get_header(cur) #"<div id=top_menu>"
	txt += '<div id = "container">\n'
	txt += '   <div id = "header">\n'
	txt += '   <!-- Banner -->\n'
	txt += '   <img src = "' + os.path.join('/static','aikif_banner.jpg') + '" alt="AIKIF Banner"/>\n'
	txt += '   <ul id = "menu_list">\n'
	for m in menu:
		if m[1] == cur:
			txt += '      <LI id="top_menu_selected"><a href=' + m[0] + '>' + m[1] + '</a></li>\n'
			pgeHdg = m[1]
			try:
				pgeBlurb = m[2]
			except:
				pass
		else:
			txt += '      <LI id="top_menu"><a href=' + m[0] + '>' + m[1] + '</a></li>\n'
	txt += "    </ul>\n    </div>\n\n"
	txt += '<H1>AIKIF ' + pgeHdg + '</H1>\n'
	txt += '<H4>' + pgeBlurb + '</H4>\n'
	return txt

###################### TEMPLATES #########################

def get_header(pge=''):
	txt = '<HTML><HEAD>\n'
	txt += '<title>AIKIF:' + pge + '</title>\n'
	txt += '<!-- Stylesheets for responsive design -->\n'
	txt += '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
	txt += '<link rel="stylesheet" type="text/css" href="' + os.path.join('/static','aikif.css') + '" media="screen" />\n'
	txt += '<link rel="stylesheet" href="' + os.path.join('/static','aikif_mob.css') + '" media="only screen and (min-device-width : 320px) and (max-device-width : 480px)">\n'
	txt += '</HEAD>\n'
	txt += '<body>\n'
	return txt
	
def get_footer(pge=''):
	txt = '\n\n<BR><BR><BR>\n<div id="footer">\n'
	txt += '<HR><a href="http://www.acutesoftware.com.au/aikif/index.html">AIKIF web interface</a> - '
	txt += 'written by Duncan Murray : djmurray@acutesoftware.com.au<BR>\n'
	txt += AIKIF_WEB_VERSION + ':' + AIKIF_VERSION_NUM + '\n'
	txt += 'Python version:' + sys.version + '\n'
	txt += '</div></BODY></HTML>\n'
	return txt

def escape_html(s):
    res = s
    res = res.replace('&', "&amp;")
    res = res.replace('>', "&gt;")
    res = res.replace('<', "&lt;")
    res = res.replace('"', "&quot;")
    return res

def format_list_as_html_table_row(lst):
	txt = '<TR>'
	for i in lst:
		txt = txt + '<TD>' + i + '</TD>'
	txt = txt + '</TR>'	
	return txt
    
def format_csv_to_html(csvFile, opHTML):
    txt = BuildHTMLHeader(csvFile)
    with open(csvFile) as csv_file:
        for row in csv.reader(csv_file, delimiter=','):
            txt += "<TR>"
            for col in row:
                txt += "<TD>"
                txt += escape_html(col)
                txt += "</TD>"
            txt += "</TR>"
        txt += "</TABLE>"
    return txt
    
def DisplayImagesAsHTML(imageList):
    pass

	
if __name__ == "__main__":
	start_server()
