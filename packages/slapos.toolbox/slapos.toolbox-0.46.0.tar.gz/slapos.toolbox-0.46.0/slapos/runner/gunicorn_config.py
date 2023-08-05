import slapos.runner.process

#def on_exit(server):
def worker_exit(worker, server):
  print 'exit!'
  print worker.app.prout
