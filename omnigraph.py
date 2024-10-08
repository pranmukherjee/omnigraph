"""Module providing flexible plotting options for multi-page, variable-scale subplots."""

import argparse
import configparser
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def graphconfig(filename,data):
  """Load and parse the config file."""
  config = configparser.ConfigParser()
  config.read(filename)

  # Initialize data structure
  for graphname in config['BASE']['Graphnames'].split():
    data[graphname]={}
    for dataset in config['BASE']['Datasets'].split():
      data[graphname][dataset]           = {}
      data[graphname][dataset]['XYdata'] = []
      data[graphname][dataset]['Legend'] = config.get(dataset,'Legend',fallback=None)
      data[graphname][dataset]['Marker'] = config[dataset]['Marker'].strip()
      data[graphname][dataset]['Color']  = config[dataset]['Color'].strip()
      data[graphname][dataset]['Style']  = config[dataset]['Linestyle'].strip()
      prefix=config[dataset]['Prefix'].strip()
      suffix=config[dataset]['Suffix'].strip()
      data[graphname][dataset]['Filename']=f"{prefix}{graphname}{suffix}"
  return config

def dataload(data,graphname,dataset):
  """Load one line of xy data from a file."""
  with open(data[graphname][dataset]['Filename'], 'r', encoding='utf-8') as file:
    for line in file:
      clean = line.strip().split()
      (x,y) = (float(clean[0].strip(',')), float(clean[1].strip(',')))
      data[graphname][dataset]['XYdata'].append((x,y))
    file.close()

def dataround(data,graphname,dataset,numplaces):
  """Truncate float data for easier y-axis readability."""
  mydata = data[graphname][dataset]['XYdata']
  rounded = [(elem1, np.round(elem2,numplaces)) for elem1, elem2 in mydata]
  data[graphname][dataset]['XYdata']=rounded

def datasort(data,graphname,dataset):
  """Sort data by x-axis element to avoid spaghetti graph."""
  mydata = data[graphname][dataset]['XYdata']
  mydata.sort(key=lambda tup: tup[0])
  data[graphname][dataset]['XYdata']=mydata

def datamultiply(data,graphname,dataset,multiplier):
  """Scale y data by a given multiplier."""
  mydata = data[graphname][dataset]['XYdata']
  for n, tup in enumerate(mydata):
    data[graphname][dataset]['XYdata'][n]=(tup[0], tup[1]*multiplier)

def dataadd(data,graphname,dataset,addend):
  """Bias y data by a given additive factor."""
  mydata = data[graphname][dataset]['XYdata']
  for n, tup in enumerate(mydata):
    data[graphname][dataset]['XYdata'][n]=(tup[0], tup[1]+addend)

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

def getaxes(config,page,ha,i,j):
  """Figure out axes based on config; this is a workaround for matplotlib."""
  numv = config.getint(page,'Numvertical',fallback=1)
  numh = config.getint(page,'Numhorizontal',fallback=1)
  if numv==1 and numh==1:
    ax=ha
  elif numv>1 and numh>1:
    ax=ha[i,j]
  elif numv==1:
    ax=ha[j]
  else:
    ax=ha[i]
  return ax

def makeplot(ax,graphdata,config,plot):
  """Create a single graph on a page."""
  mylabel      = config.get(plot,'Ylabel',fallback=None)
  annotation   = config.get(plot,'Annotation',fallback=None)
  graphstyle   = config.get(plot,'Style',fallback='linear')

  # Plot the data, one line per Dataset
  for dataset, elements in graphdata.items():
    mydata   = elements['XYdata']
    mylegend = elements['Legend']
    mymarker = elements['Marker']
    mycolor  = elements['Color']
    mystyle  = elements['Style']
    # plot data
    if mylegend is not None:
      ax.plot(*zip(*mydata), marker=mymarker, color=mycolor, linestyle=mystyle, label=mylegend)

  setscale(ax,graphstyle)

  # Decorate the plotted data
  ax.set(xlabel='Number of threads')
  if mylabel is not None:
    ax.set(ylabel=mylabel)
  ax.legend(loc='best', fontsize='xx-small')

  # Annotate the selected dataset's line
  # TODO: Make this cleaner and more applicable to other data sets
  if annotation is not None and annotation in graphdata:
    for i in graphdata[annotation]['XYdata']:
      ax.annotate(int(i[0]), (i[0]*1.1, i[1]*1.1))

def makegraph(data,config,plot,ax):
  """Wrapper for makeplot."""
  graphname  = config.get(plot,'Graphname',fallback=None)

  # Plot data
  if graphname is not None:
    makeplot(ax,data[graphname],config,plot)
  else:
    ax.axis('off')

def makegraphs(data,config,ha,page):
  """Create all graphs on one page."""
  numvertical   = config.getint(page,'Numvertical',fallback=1)
  numhorizontal = config.getint(page,'Numhorizontal',fallback=1)
  for i in range(numvertical):
    for j in range(numhorizontal):
      plot = page+'.'+str(i)+'.'+str(j)
      ax   = getaxes(config,page,ha,i,j)
      makegraph(data,config,plot,ax)

def makepages(data,config):
  """Create pages."""
  pagenames = config['BASE']['Pagenames'].split()
  for page in pagenames:
    title         = config.get(page,'Title',fallback=None)
    numvertical   = config.getint(page,'Numvertical',fallback=1)
    numhorizontal = config.getint(page,'Numhorizontal',fallback=1)
    directory     = config.get('BASE','Outputdir',fallback='./')
    filename      = config.get(page,'Filename',fallback=None)

    hf,ha = plt.subplots(numvertical,numhorizontal)
    if title is not None:
      hf.suptitle(title)
      makegraphs(data,config,ha,page)
    if filename is not None:
      location = directory+'/'+filename
      plt.savefig(location)
      plt.clf()

def writecsv(data,filename):
  """Write out XY data to CSV format for each graph and dataset"""
  with open(filename, 'w', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',', dialect='excel', quoting=csv.QUOTE_MINIMAL)
    for graphname, datasets in data.items():
      for dataset, elements in datasets.items():
        if elements['Legend'] is not None:
          writer.writerow([dataset,graphname])
          writer.writerows(elements['XYdata'])
    file.close()


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
  for graphname, datasets in data.items():
    for dataset, elements in datasets.items():
      if elements['Legend'] is not None:
        dataload(data,graphname,dataset)

  # Prepare data
  if 'runtime' in data:
    for dataset in data['runtime']:
      datamultiply(data,'runtime',dataset,1/60000)
  for graphname, datasets in data.items():
    for dataset, elements in datasets.items():
      if elements['Legend'] is not None:
        dataround(data,graphname,dataset,3)
        datasort(data,graphname,dataset)

  path = Path(config.get('BASE','Outputdir'))
  path.mkdir(parents=True, exist_ok=True)

  makepages(data,config)
  filename='output/collated.csv'
  writecsv(data,filename)

main()
