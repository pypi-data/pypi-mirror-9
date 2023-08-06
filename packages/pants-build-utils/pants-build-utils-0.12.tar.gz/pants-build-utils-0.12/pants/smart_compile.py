#!/usr/bin/python

import sys
import commands
import os
import subprocess

def find_file_above_file(needle, haystack, stop):
  if os.path.isdir:
    path = haystack
  else:
    path = os.path.split(haystack)[0]

  candidate_build_file = os.path.join(path, needle)
  if os.path.exists(candidate_build_file):
    return path
  else:
    if path == stop:
      return None

    return find_file_above_file(needle, os.path.split(haystack)[0], stop)

def find_build_file(f, stop):
  file = find_file_above_file('BUILD', f, stop)
  if not file:
    print 'could not find BUILD for %s' % f
    sys.exit(1)
  return file

def find_pants(f, stop):
  file = find_file_above_file('pants', f, stop)
  if not file:
    print 'could not find pants for %s' % f
    sys.exit(1)
  return file

def test_main():
  main('test')

def compile_main():
  main('compile')

def main(default_goal='compile'):
  base_dir = find_file_above_file('pants.ini', os.getcwd(), '/')
  print 'base dir: ' + base_dir
  #commands.getstatusoutput('git rev-parse --show-toplevel')[1]

  files = sys.argv[1:]

  if len(files) == 0:
    changed_files_cmd = 'git diff --name-only --cached $(git rev-list --boundary ...master | grep ^- | cut -c2-) | grep scala$'
    files = commands.getstatusoutput(changed_files_cmd)[1].split('\n')

  if len(files) == 0:
    return 'No files found'

  goal = default_goal
  if files[0] in ['test', 'compile']:
    goal = files[0]
    files = files[1:]

  print 'found %s changed files:\n%s' % (
    len(files),
    '\n'.join(['    ' + f for f in files])
  )

  build_files = set([
    find_build_file(os.path.join(base_dir, f), base_dir) for f in files
  ])

  print 'need to %s %s paths:\n%s' % (
    goal,
    len(build_files),
    '\n'.join(['    ' + f for f in build_files])
  )

  for build_file in build_files:
    pants_path = find_pants(build_file, base_dir)
    if not pants_path:
      print 'could not find pants binary for %s' % build_file
      sys.exit(1)
    cmd = '%s %s %s' % (os.path.join(pants_path, 'pants'), goal, build_file)
    print cmd
    subprocess.check_call(cmd.split(' '))

  print 'SUCCESS!!!!!!'

if __name__ == "__main__":
  main()
