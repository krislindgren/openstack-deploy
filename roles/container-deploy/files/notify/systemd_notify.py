import os
import socket
import select
import sys
import shutil
import tempfile
import errno

socket_filename = "notify.socket"

def main():

  if len(sys.argv) != 3:
    sys.stderr.write("%s <service-name> <wait timeout> arguments required\n" % sys.argv[0])
    sys.exit(1)

  img = sys.argv[1]
  wait_timeout = float(sys.argv[2])

  tmp_dir = os.path.join(tempfile.gettempdir(), img)
  try:
    os.makedirs(tmp_dir)
  except OSError as exception:
    if exception.errno == errno.EEXIST and os.path.isdir(tmp_dir):
      pass
    else:
      raise
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
  sock_path = os.path.join(tmp_dir, socket_filename)
  sock.bind(sock_path)
  os.chmod(sock_path, 0777)

  print("Waiting up to %s seconds for %s to notify its ready" % (wait_timeout, img))
  rlist, wlist, xlist = select.select([sock], [], [], wait_timeout)
  started = False
  if rlist:
    blob = sock.recv(4096)
    blob = blob.strip()
    if blob == b'READY=1':
      started = True
  if tmp_dir is not None:
    shutil.rmtree(tmp_dir)

  if not started:
    print("%s did not start..." % img)
    exit(1)
  else:
    print("%s started!" % img)
    exit(0)

if __name__ == '__main__':
  main()
