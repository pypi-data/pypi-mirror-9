#!/usr/bin/env python
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

import os, sys
import argparse
import numpy

import bob.io.base
from ..fusion import fusion
import antispoofing.utils.db 

def main():
    
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('-s', '--scores-dir', type=str, dest='scoresDir', default='', help='Base directory containing the scores of different countermeasures', nargs='+')
  
  parser.add_argument('--sn', '--scores-name', type=str, dest='scoresName', default='', help='Name of the features used for the scores of the different countermeasures. Should correspond by number and order to the -s argument', nargs='+')

  parser.add_argument('-e', '--end', action='store_true', default=False, help='Arg split')
  
  antispoofing.utils.db.Database.create_parser(parser, 'video')
  args = parser.parse_args() 
  
  scoresDir          = args.scoresDir
  scoresName = args.scoresName
  
  outputDir='results/Venn&scatter'
  sys.stdout.write('Computing intersection of errors between countermeasures...')
  sys.stdout.flush()
  cms=scoresName[0]
  import ipdb; ipdb.set_trace()
  for i in range(1,len(scoresName)):
    cms=cms + " & " + scoresName[i]
  # perform mutual error analysis
  tbl=[]
  tbl.append("Venn diagram as numbers:")  
  tbl.append("\n"+cms+":")
  tbl=tbl+fusion.Venn_analysis(scoresDir)
  
  txt = ''.join([k+'\n' for k in tbl])
  print txt
  
  # write results in text file  
  import ipdb; ipdb.set_trace()
  if not os.path.exists(outputDir): # if the output directory doesn't exist, create it
    bob.io.base.create_directories_safe(outputDir)

  tf = open(os.path.join(outputDir,cms+"_venn.txt"), 'w')
  tf.write(txt)
  print 'done.'

if __name__ == '__main__':
  main()
