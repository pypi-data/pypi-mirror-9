#!/usr/bin/python

import commands
import os
import subprocess

git_base_dir = commands.getstatusoutput('git rev-parse --show-toplevel')[1]

def find_file_above_file(needle, haystack):
  path = os.path.split(haystack)[0]
  if path == git_base_dir:
    print "couldn't find %s file for %s" % (needle, haystack)
    return None

  candidate_build_file = os.path.join(path, needle)
  if os.path.exists(candidate_build_file):
    return path
  else:
    return find_file_above_file(needle, os.path.split(haystack)[0])

def find_build_file(f):
  return find_file_above_file('BUILD', f)

def find_pants(f):
  return find_file_above_file('pants', f)

def main():
  changed_files_cmd = 'git diff --name-only --cached $(git rev-list --boundary ...master | grep ^- | cut -c2-)'
  files = commands.getstatusoutput(changed_files_cmd)[1].split('\n')

  if len(files) == 0:
    return 'No files found'

  build_files = set([
    find_build_file(os.path.join(git_base_dir, f)) for f in files
  ])

  print 'need to compile %s paths:\n%s' % (
    len(build_files),
    '\n'.join(['    ' + f for f in build_files])
  )

  for build_file in build_files:
    pants_path = find_pants(build_file)
    if not pants_path:
      print 'could not find pants binary for %s' % build_file
      sys.exit(1)
    cmd = '%s compile %s' % (os.path.join(pants_path, 'pants'), build_file)
    print cmd
    subprocess.check_call(cmd.split(' '))

  print 'SUCCESS!!!!!!'
