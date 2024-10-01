# importing required modules 
import matplotlib.pyplot as plt
import numpy as np
import csv,configparser
import argparse

def graphconfig(filename,data):
  config = configparser.ConfigParser()
  config.read(filename)

  # Initialize data structure
  for graphname in config['BASE']['Graphnames'].split():
    data[graphname]={}
    for graphline in config['BASE']['Datasets'].split():
      data[graphname][graphline]={}
      data[graphname][graphline]["xydata"]=[]
      data[graphname][graphline]["legend"]=config.get(graphline,'legend',fallback=None)
      data[graphname][graphline]["marker"]=config[graphline]['marker'].strip()
      data[graphname][graphline]["color"]=config[graphline]['color'].strip()
      data[graphname][graphline]["style"]=config[graphline]['linestyle'].strip()
      data[graphname][graphline]["filename"]="{}{}{}".format(config[graphline]['prefix'].strip(),graphname,config[graphline]['suffix'].strip())
  return config

def dataload(data,graphname,graphline):
    file = open(data[graphname][graphline]["filename"],"r")
    for line in file:
      clean = line.strip().split()
      (x,y) = (int(clean[0]), float(clean[1]))
      data[graphname][graphline]["xydata"].append((x,y))
    file.close()

def datatruncate(data,graphname,graphline):
  mydata = data[graphname][graphline]["xydata"]
  truncated = [(elem1, np.trunc(elem2)) for elem1, elem2 in mydata]
  data[graphname][graphline]["xydata"]=truncated

def datasort(data,graphname,graphline):
  mydata = data[graphname][graphline]["xydata"]
  mydata.sort(key=lambda tup: tup[0])
  data[graphname][graphline]["xydata"]=mydata

def datamultiply(data,graphname,graphline,multiplier):
  mydata = data[graphname][graphline]["xydata"]
  for n, tup in enumerate(mydata):
    data[graphname][graphline]["xydata"][n]=(tup[0], tup[1]*multiplier)

def dataadd(data,graphname,graphline,addend):
  mydata = data[graphname][graphline]["xydata"]
  for n, tup in enumerate(mydata):
    data[graphname][graphline]["xydata"][n]=(tup[0], tup[1]+addend)

def makegraph(data,config,page,hf,ha,numv,numh,i,j):
  plot       = page+"."+str(i)+"."+str(j)
  directory  = config.get('BASE','Outputdir',fallback='./')
  filename   = config.get(page,'filename',fallback=None)
  graphname   = config.get(plot,'Graphname',fallback=None)
  label      = config.get(plot,'Ylabel',fallback=None)
  annotation = config.get(plot,'Annotation',fallback=None)
  graphstyle = config.get(plot,'Style',fallback='linear')

  # Plot data
  if graphname is not None:
    makeplot(hf,ha,numv,numh,i,j,data[graphname],label,annotation,graphstyle)
  elif numv==1:
    ha[j].axis('off')
  elif numh==1:
    ha[i].axis('off')
  else:
    ha[i,j].axis('off')
  if filename is not None:
    location = directory+"/"+filename
    plt.savefig(location)

def makegraphs(data,config):
  pagenames = config['BASE']['Pagenames'].split()
  for page in pagenames:
    title         = config.get(page,'title',fallback=None)
    numvertical   = config.getint(page,'Numvertical',fallback=1)
    numhorizontal = config.getint(page,'Numhorizontal',fallback=1)
    hf,ha = plt.subplots(numvertical,numhorizontal)
    if title is not None:
      hf.suptitle(title)
    for i in range(numvertical):
      for j in range(numhorizontal):
        makegraph(data,config,page,hf,ha,numvertical,numhorizontal,i,j)
    plt.clf()

def setscale(ax,style):
    if style == 'loglog':
      ax.set_yscale('log')
      ax.set_xscale('log')
    elif style == 'semilogx':
      ax.set_xscale('log')
    elif style == 'semilogy':
      ax.set_yscale('log')
    elif style == 'linear':
      ax.set_xscale('linear')
      ax.set_yscale('linear')

def makeplot(hf,ha,numx,numy,x,y,indata,name,annotate,plotstyle):
  for dataline in indata:
    mydata   = indata[dataline]["xydata"]
    mylegend = indata[dataline]["legend"]
    mymarker = indata[dataline]["marker"]
    mycolor  = indata[dataline]["color"]
    mystyle  = indata[dataline]["style"]
    # plot data
    if numx==1 and numy==1:
      ax=ha
    elif numx>1 and numy>1:
      ax=ha[x,y]
    elif numx==1:
      ax=ha[y]
    else:
      ax=ha[x]
    ax.plot(*zip(*mydata), marker=mymarker, color=mycolor, linestyle=mystyle, label=mylegend)
    setscale(ax,plotstyle)

  if annotate is not None:
    for i in indata[annotate]["xydata"]:
      ax.annotate(i[0], (i[0]*1.1, i[1]*1.1))
  ax.set(xlabel="Number of threads")
  if name is not None:
    ax.set(ylabel=name)
  ax.legend(loc='best', fontsize='xx-small')

def main():
  ## USAGE: Anyone adapting this will likely want a custom
  #  graphsetup.cfg and associated graphconfig function,
  #  and will likely prepare their data differently below,
  #  and if the data aren't in (int,float) format a modification
  #  to the dataload function might be needed,
  #  but the rest should work just fine with other x,y data
  ##

  parser = argparse.ArgumentParser(description='Multi-page, multi-graph subplot graphing tool.')
  parser.add_argument('-c', '--conf', help='Config file to use', type=str, dest='config_file', default='graphsetup.cfg')
  args = parser.parse_args()

  data = {}

  # Input configuration
  config = graphconfig(args.config_file,data)

  # Read in xy data from files
  for graphname in data:
    for graphline in data[graphname]:
      if data[graphname][graphline]["legend"] is not None:
        dataload(data,graphname,graphline)

  # Prepare data
  for graphline in data["runtime"]:
    datamultiply(data,"runtime",graphline,1/60000)
  for graphname in data:
    for graphline in data[graphname]:
      datatruncate(data,graphname,graphline)
      datasort(data,graphname,graphline)

  makegraphs(data,config)

main()