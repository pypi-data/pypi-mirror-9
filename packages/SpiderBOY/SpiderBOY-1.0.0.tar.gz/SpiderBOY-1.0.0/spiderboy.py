#!/usr/bin/python

# Copyright (C) 2011 Diego Pardilla Mata
#
#	This file is part of SpiderBOY.
#
# 	SpiderBOY is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import argparse
import tempfile
from BeautifulSoup import BeautifulSoup as Soup
import os
import signal
from color import colorstr
from pdf import getPDFlinks
from spinslash import spin



parser = argparse.ArgumentParser (description="Let's spiderBOY the Internet")
parser.add_argument ( 'url' , nargs=1 , help = 'target URL')
parser.add_argument ( '-n' , '--number-of-levels' , type=int , default=1 , help = 'how deep the spiderBOY program must track')
parser.add_argument ( '-p' , '--type-of-protocol' , type=str , default='http' , help = 'what type of protocol to use, only one (e.g. http or https or ftp)')
args = parser.parse_args()

# Input parameters
target_url = args.url.pop()
deep = args.number_of_levels
type_proto = args.type_of_protocol

# Function that get links
def get_links(target):
	user_agent = 'Mozilla/5.0 (X11;U;Linux x86_64;en-US) AppleWebKit/534.7 ( KHTML , like Gecko ) Chrome/7.0.517.41 Safari/534.7'
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', user_agent)]
	# Get protocol
	if type_proto != 'file':
		proto_filter = type_proto + '://'
	else:
		proto_filter = 	type_proto + ':///'
	# Let's see if it is a pdf file
	if '.pdf' in target:
		raw_code = urllib2.urlopen(target.encode("utf-8")).read()
		opener.close()
		temp = tempfile.NamedTemporaryFile(prefix='spiderBOY_', suffix='.tmp', dir='/tmp', delete=False)
		temp.write(raw_code)
		temp.close()
		links = getPDFlinks(temp.name,proto_filter)
		
	else:	
		# Catch an URL exception	
		try:
			raw_code = opener.open(target.encode("utf-8")).read()
			opener.close()
		except urllib2.URLError, e:
			if hasattr(e, 'reason'):
				print colorstr('\nWe failed to reach a server.', 'RED')
				print colorstr('This url: ' + target + ' has a problem and the reason is: ' + repr(e.reason), 'RED')
			elif hasattr(e, 'code'):
				print colorstr('\nThe server couldn\'t fulfill the request.', 'RED')
				print colorstr('This url: ' + target + ' has a problem and the error code is: ' + repr(e.code), 'RED')
			links = []
		else:
			soup_code = Soup (raw_code)
			links = [ link ['href'] for link
					in soup_code.findAll ('a')
					if (link.has_key ('href') and (link['href'].find(proto_filter)==0))]
	return links

# Function that input is a list and an output is a dictionary with the level of proof
def read_list (elements_list,level,dict_out,proof):
	level = level + 1
	proof = proof - 1
	# Cover the list of links
	for node in elements_list:
		aux_list = get_links(node)
		# trace program
		#print 'node:' + node
		#print 'list:' + str(aux_list)
		#print 'deep:' + str(proof)
		if proof > 0:
			dict_out[node] = level 
			read_list(aux_list,level,dict_out,proof)
		else:
			dict_out[node] = level	
	return dict_out

# Function that paint the dictionary with {url, proof}
def paint_list (dict2print):
	element = '\n'
	aux_list = dict2print.keys()

	for key in aux_list:
		level = dict2print[key]
		for i in range(level): 
			element = element + '*'
		if '\n' in key:
			element = element + ' ' + str(key.encode("utf-8"));
		else:
			element = element + ' ' + str(key.encode("utf-8")) + '\n';
	print element
	# trace print dictionary
	#print 'Dictionary (url, level of proof):', dict2print
	return 0	

# Spinning slash for wait process
child_pid = os.fork()
if child_pid == 0:
	print ("Please wait "),
	spin()
else:
	# Initialize the list of links
	list_links = get_links(target_url)	

# Read the list of links
level = 0
dict_out = {}
out_dict = read_list (list_links,level,dict_out,deep)
# Paint the dictionary
paint_list(out_dict)
os.kill(child_pid, signal.SIGTERM)
os.waitpid(child_pid, 0) # need
