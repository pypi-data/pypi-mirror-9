__author__ = 'admin'

def run(argv):
    try:
      opts, args = getopt.getopt(argv,"hp:o:",["path=","ofile="])
      os.environ["stub_files_path"] = args[0]
      if len(args) < 2: raise Exception("Correct Exception")
      stubbing_engine.start(port_number=args[1])
    except:
      print 'Usage : python -m webmocker.server <folderpath> <portNumber>'
      traceback.print_exc(file=sys.stdout)
      sys.exit(2)


if __name__ == '__main__':
    import stubbing_engine
    import os,getopt,sys,traceback
    run(sys.argv[1:])




