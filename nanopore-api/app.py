from flask import Flask, render_template, request
from FAST5_api import Fast5Event
from flask_cors import CORS, cross_origin
import os, errno, sys, h5py, pickle, simplejson, json, jsonify
from os import listdir
from os.path import isfile, join
import pandas as pd
from operator import itemgetter
from SAMParse import *
# import pysam

app = Flask(__name__)
cors = CORS(app)


@app.route('/test/<path:sam>', methods = ['GET'])
def test(sam):

	return str(len(cigar)), 201


@app.route('/generatejson/<string:name>&<path:directory>&<path:ref>&<path:sam>', methods = ['GET'])
# @cross_origin()
def generatejson(name, directory, ref, sam):
	name = name[5:]
	directory = directory[10:]
	ref = ref[4:]
	sam = sam[4:]
	dir_path = "./data/"+name
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	else:
		return 'Project Already Exists', 406

	for i in listdir(directory):
		if isfile(join(directory, i)):
			base = i.split('.fast')[0]
			path = "./data/"+name+"/"+base+".record"
			# sys.stdout = open(path, 'w')
			f = Fast5Event(directory+"/"+i)
			record, max_min,a,b = f.get_list_event_data(file_path=sam)
			for i in range(len(record)):
				if i % 2 == 1 or i == 0:
					continue
				else:
					leng = len(record[i])
					diff = 1.0/float(leng)
					for id in range(leng):
						record[i][id][0] = float(record[i-1]) + float(diff)*float(id)
			record.append(max_min)
			# print(record[0])
			print(a)
			print(b)
			with open(path, 'wb') as outfile:
				pickle.dump(record, outfile)
				pickle.dump(max_min, outfile)
	return "Project Successfully Created", 201
	return json.dumps(record), 201


@app.route('/removeproject/<string:existing>', methods = ['POST'])
def removeproject(existing):
	name = existing[9:]
	try:
		os.system('rm -rf data/'+name)
		return 'Project Successfully Removed', 201
	except ValueError:
		return 'Error Removing Project:' + name, 406


@app.route('/getrange/<string:start>&<string:end>&<string:name>', methods = ['GET'])
# @cross_origin()
def getrange(start, end, name):
	mami = []
	start = start[6:]
	end = end[4:]
	start_i = int(start)
	end_i = int(end)
	name = name[5:]
	started = 0
	directory = "./data/"+name
	final_record = "["
	first = 0
	for i in listdir(directory):
		if isfile(join(directory, i)):
			with open(directory+"/"+i, 'rb') as infile:
				record = pickle.load(infile)
			mami.append(record[-1])
			final_record +=   json.dumps(record[0]) + ","
			final_record += json.dumps(record[(start_i*2)+1:(end_i*2)+1]) + ","
			# final_record += json.dumps(record[-1]) + ","
	max_mami = max(mami,key=itemgetter(1))[0]
	min_mami = min(mami,key=itemgetter(1))[1]
	final_record += "["+max_mami+", "+min_mami+"]]"
	# final_record = final_record[:-1]
	# final_record+= "]"
	return final_record, 201
	# return json.dumps(max_mami), 201


@app.route('/getprojects/', methods = ['GET'])
def dataselect():
	sub = os.listdir('./data')
	projects = {}
	for i in range(len(sub)):
		projects[i] = sub[i]
	return json.dumps(projects), 200


@app.after_request
def after_request(response):
	# header['Access-Control-Allow-Origin'] = '*'
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
	return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
