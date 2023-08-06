#!/usr/bin/python -tt
# vim: set fileencoding=utf-8
# Pavel Odvody <podvody@redhat.com>
#
# libdoug - DOcker Update Guard
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
import argparse, os, shlex
from libdoug.docker_api import DockerLocal, UserInfo
from libdoug.history import ImageHistory, HistoryDiff
from libdoug.registry import Registry
from libdoug.vr_solver import VRConflictSolver
from libdoug.dependency_walker import DependencyWalker
from libdoug.optimistic_solver import OptimisticConflictSolver
from libdoug.graph import DependencyType
from libdoug.values import EmptyDiff, RootImage
from libdoug.utils import Console, get_image, wipe_newlines
from libdoug.api.flags import parse_cli

docker, registry, user = DockerLocal(), None, None

def dumplocal_action(args):
	print "Local tags:"
	local = docker.getimages(args.repo)
	localhistory = ImageHistory(local)
	localhistory.printout()

def dumpremote_action(args):
	print "Remote tags:"
	remotehistory = ImageHistory.fromjson(registry.querytags(args.repo, user))
	remotehistory.printout()

def dependencies_action(args):
	print "Dependency Walker:"
	allimages = docker.getallimages()
	image = get_image(args.image, allimages)

	walker = DependencyWalker(image, DependencyType.IMAGE)
	walker.walk(docker.getallimages())

def update_action(args):
	localhistory = ImageHistory(docker.getimages(args.repo))
	remotehistory = ImageHistory.fromjson(registry.querytags(args.repo, user))
	solver = args.solver

	if solver == 'optimistic':
		differ = HistoryDiff(localhistory, remotehistory)
		imgdelta = differ.diff()
		if imgdelta != EmptyDiff:
			print 'Local and Remote Diffs:'
			HistoryDiff.printout(imgdelta)

			if raw_input("Resolve conflicts [y/n]? [y] ") in ['', 'y', 'Y'] or args.force:
				conflict = OptimisticConflictSolver(docker.getallimages(), imgdelta, args.repo)
				resolve = conflict.solve()
				if resolve:
					print 'Resolutions: '
					for r in resolve:
						if not args.no_push or r.gettype() != ResolutionType.PUSH:
							r.execute(docker)
		else:
			print 'Local and Remote are up to date!'
	elif solver == 'vr':
		print "VR Conflict Status:"
		nevsolver = VRConflictSolver(docker.getallimages(), (localhistory, remotehistory), args.repo)
		nevsolver.solve()
	else:
		raise Exception('Unsupported solver: %s' % solver)

def dockercli_action(args):
	if len(args.cli) == 1:
		args.cli = shlex.split(args.cli[0])
	if args.cli[0] == 'docker':
		args.cli = args.cli[1:]
	cli = parse_cli(args.cli)
	print 'Flags:   ', "\n	  ".join(["%s = %s"%a for a in cli.flags])
	print 'Verb:    ', cli.verb
	print 'Context: ', cli.context
	print 'Workdir: ', os.getcwd()

def cli_command(args):
	action = args.action.replace('-', '')
	actionfunc = globals()[action+'_action']
	actionfunc(args)

if __name__ == '__main__':
	args = argparse.ArgumentParser(description='doug-cli libdoug interface')
	args.add_argument('-f', '--force', action='store_true', help='Do not ask for confirmations')
	args.add_argument('-u', '--user', help='Username for the Hub')
	args.add_argument('-p', '--password', help='Password for the Hub')
	args.add_argument('-e', '--email', help='Email for the Hub')
	args.add_argument('-r', '--registry', help='Registry URL we target', default='docker.io')
	args.add_argument('-a', '--baseauth', help='HTTP Basic Auth string')
	args.add_argument('-n', '--no-push', action='store_true', help='Do not push local changes upstream')
	subargs = args.add_subparsers(help='sub-command help', dest='action')

	localparser = subargs.add_parser('dump-local', help='Dump locally present tags')
	localparser.add_argument('repo', help='Target repository')

	remoteparser = subargs.add_parser('dump-remote', help='Dump remotely present tags')
	remoteparser.add_argument('repo', help='Target repository')

	cliparser = subargs.add_parser('docker-cli', help='Parse Dockers CLI')
	cliparser.add_argument('cli', nargs='*', help='Docker command')
	
	depparser = subargs.add_parser('dependencies', help='Visualize dependencies of target Image')
	depparser.add_argument('image', help='Target image ID or Repo[:Tag]')

	updateparser = subargs.add_parser('update', help='Update Local/Remote tags')
	updateparser.add_argument('-s', '--solver', help='Solver to use (vr = Version-Release)', default='optimistic', choices=['optimistic', 'vr'])
	updateparser.add_argument('repo', help='Target repository')

	parsed = args.parse_args()
	if hasattr(parsed, 'repo'):
		if parsed.repo.count('/') == 0:
			parsed.repo = "stackbrew/" + parsed.repo
	registry = Registry(parsed.registry)

	if parsed.action in ['update', 'dump-remote']:
		if parsed.user == None:
			parsed.user, parsed.password, parsed.email = wipe_newlines(open(os.getenv("HOME") + '/.douguserinfo').readline().split(':'))
	user = UserInfo(parsed.user, parsed.password, parsed.email)

	cli_command(parsed)
