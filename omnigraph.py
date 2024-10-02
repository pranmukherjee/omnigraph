"""Module providing flexible plotting options for multi-page, variable-scale subplots."""

import argparse
import configparser
import matplotlib.pyplot as plt
import numpy as np

def graphconfig(filename,data):
  """Load and parse the config file."""
  config = configparser.ConfigParser()
  config.read(filename)

  # Initialize data structure
  for graphname in config['BASE']['Graphnames'].split():
    data[graphname]={}
    for graphline in config['BASE']['Datasets'].split():
      data[graphname][graphline]={}
      data[graphname][graphline]['XYdata']=[]
      data[graphname][graphline]['Legend'] = config.get(graphline,'Legend',fallback=None)
      data[graphname][graphline]['Marker'] = config[graphline]['Marker'].strip()
      data[graphname][graphline]['Color']  = config[graphline]['Color'].strip()
      data[graphname][graphline]['Style']  = config[graphline]['Linestyle'].strip()
      data[graphname][graphline]['Filename']=f"{config[graphline]['Prefix'].strip()}{graphname}{config[graphline]['Suffix'].strip()}"
  return config

def dataload(data,graphname,graphline):
  """Load one line of xy data from a file."""
  file = open(data[graphname][graphline]['Filename'],'r', encoding="utf-8")
  for line in file:
    clean = line.strip().split()
    (x,y) = (float(clean[0].strip(',')), float(clean[1].strip(',')))
    data[graphname][graphline]['XYdata'].append((x,y))
  file.close()

def datatruncate(data,graphname,graphline):
  """Truncate float data for easier y-axis readability."""
  mydata = data[graphname][graphline]['XYdata']
  truncated = [(elem1, np.trunc(elem2)) for elem1, elem2 in mydata]
  data[graphname][graphline]['XYdata']=truncated

def datasort(data,graphname,graphline):
  """Sort data by x-axis element to avoid spaghetti graph."""
  mydata = data[graphname][graphline]['XYdata']
  mydata.sort(key=lambda tup: tup[0])
  data[graphname][graphline]['XYdata']=mydata

def datamultiply(data,graphname,graphline,multiplier):
  """Scale y data by a given multiplier."""
  mydata = data[graphname][graphline]['XYdata']
  for n, tup in enumerate(mydata):
    data[graphname][graphline]['XYdata'][n]=(tup[0], tup[1]*multiplier)

def dataadd(data,graphname,graphline,addend):
  """Bias y data by a given additive factor."""
  mydata = data[graphname][graphline]['XYdata']
  for n, tup in enumerate(mydata):
    data[graphname][graphline]['XYdata'][n]=(tup[0], tup[1]+addend)

def setscale(ax,style):
  """Set the axis scales for a given graph (e.g. semilogx)."""
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
  """Create a single graph on a page."""
  for dataline in indata:
    mydata   = indata[dataline]['XYdata']
    mylegend = indata[dataline]['Legend']
    mymarker = indata[dataline]['Marker']
    mycolor  = indata[dataline]['Color']
    mystyle  = indata[dataline]['Style']
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
    for i in indata[annotate]['XYdata']:
      ax.annotate(int(i[0]), (i[0]*1.1, i[1]*1.1))
  ax.set(xlabel='Number of threads')
  if name is not None:
    ax.set(ylabel=name)
  ax.legend(loc='best', fontsize='xx-small')

def makegraph(data,config,page,hf,ha,numv,numh,i,j):
  """Wrapper function for makeplot."""
  plot       = page+'.'+str(i)+'.'+str(j)
  graphname  = config.get(plot,'Graphname',fallback=None)
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

def makegraphs(data,config):
  """Create all graphs, page by page."""
  pagenames = config['BASE']['Pagenames'].split()
  for page in pagenames:
    title         = config.get(page,'Title',fallback=None)
    numvertical   = config.getint(page,'Numvertical',fallback=1)
    numhorizontal = config.getint(page,'Numhorizontal',fallback=1)
    directory  = config.get('BASE','Outputdir',fallback='./')
    filename   = config.get(page,'Filename',fallback=None)
    hf,ha = plt.subplots(numvertical,numhorizontal)
    if title is not None:
      hf.suptitle(title)
    for i in range(numvertical):
      for j in range(numhorizontal):
        makegraph(data,config,page,hf,ha,numvertical,numhorizontal,i,j)
    if filename is not None:
      location = directory+'/'+filename
      plt.savefig(location)
      plt.clf()


def main():
  """Main function; wraps up everything else."""

  ## USAGE: Anyone adapting this will likely want a custom
  #  graphsetup.cfg and associated graphconfig function,
  #  and will likely prepare their data differently below,
  #  and if the data aren't in (int,float) format a modification
  #  to the dataload function might be needed,
  #  but the rest should work just fine with other x,y data
  ##

  parser = argparse.ArgumentParser(description='Multi-page, multi-graph subplot graphing tool.')
  parser.add_argument('-c', '--conf', help='Config file to use', type=str, 
                      dest='config_file', default='graphsetup.cfg')
  args = parser.parse_args()

  data = {}

  # Input configuration
  config = graphconfig(args.config_file,data)

  # Read in xy data from files
  # for graphname in data:
  #   for graphline in data[graphname]:
  for graphname, graphlines in data.items():
    for graphline, elements in graphlines.items():
      if elements['Legend'] is not None:
        dataload(data,graphname,graphline)

  # Prepare data
  for graphline in data['runtime']:
    datamultiply(data,'runtime',graphline,1/60000)
  for graphname, graphlines in data.items():
    for graphline, elements in graphlines.items():
      datatruncate(data,graphname,graphline)
      datasort(data,graphname,graphline)

  makegraphs(data,config)

main()