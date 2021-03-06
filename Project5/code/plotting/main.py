import numpy as np
import sys, argparse, subprocess, os

import optimalStepFitter, plotAcceptancerate, plotStability, plotEvarEvsAlpha, plot3DVarBeta, plotVarBetaParallel, plotVirial


class fakeStr(str):
	def __init__(self, val):
		self.val = val
	def __str__(self):
		return ""

class CapitalisedHelpFormatter(argparse.HelpFormatter):
	def add_usage(self, usage, actions, groups, prefix=None):
		return None
	
class FakeArgumentParser(argparse.ArgumentParser):
	def error(self, message):
		self.print_help(sys.stderr)

parser = FakeArgumentParser(description="Usage: main.py {prog} [args]", add_help=False, formatter_class=CapitalisedHelpFormatter)
parser._positionals.title = 'Plots'
parser._optionals.title = 'args'
comp = parser.add_argument_group("compile all programs")
comp.add_argument(fakeStr("-fakecompile"), metavar = "compile", required=False, action="append", help="Compiles all C++ programs")

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
argparse._HelpAction(option_strings=['-h', '--help'], dest='help', default='==SUPPRESS==', help='Show this help message and exit.')

parser.add_argument('type',type=str,  choices = ["single", "variateAlpha", "variateBeta","stability", "acceptance-rate", "optimal-step-fit", "E-varE", "3D-beta", "beta-parallel", "virial"],help="Follow program name by optional program specific parameters listed below")
parser.add_argument("-omega", metavar="", type=float, help="float. ω, frequency of H.O")
parser.add_argument("-alpha", metavar = "", type=float, help="float. α, variational parameter")
parser.add_argument("-beta", metavar="", type=float, help="float. β, variational parameter")
parser.add_argument("-a0", metavar = "", type=float, help="float. Start value of α")
parser.add_argument("-a1", metavar = "", type=float, help="float. End value of α")
parser.add_argument("-da", metavar = "", type=float, help="float. Increment value of α")
parser.add_argument("-b0", metavar = "", type=float, help="float. Start value of β")
parser.add_argument("-b1", metavar = "", type=float, help="float. End value of β")
parser.add_argument("-db", metavar = "", type=float, help="float. Increment value of β")
parser.add_argument("-step0", metavar = "", type=float, help="float. Start value of step sizes to use in metropolis")
parser.add_argument("-step1", metavar = "", type=float, help="float. End valuue of step size")
parser.add_argument("-dstep", metavar = "", type=float, help="float. Increment value step size")
parser.add_argument("-psi", metavar = "", type=str, help="string. What trial wave functions to run, T1 or T2")
parser.add_argument("-EL", metavar = "", type=str, help="string. What local energy to run, E0 (H0), E1 or E2 (with interactions)")
parser.add_argument("-outfile", metavar = "", type=str, help="string. Filename to be saved to ../data/")
parser.add_argument("-solvemode", metavar="", type=str, help="For variating alpha, to run 'noninteractive' or 'interactive'")

parser.add_argument("-MCCs", metavar="",type=int, help="int. Number of Monte Carlo cycles to perform")
parser.add_argument("--sim", action="store_true", help="Re-run simulations in plotting code with default parameters. May take time")
#parser.add_argument("--compile", metavar="", type=str, help="str. compile individual C++ programs")



plots = parser.add_argument_group("Program plots \nFrom here you can recreate the plots as seen in the report")
plots.add_argument(fakeStr("-fakeplotStability"), metavar = "stability [--sim] [-a0] [-a1] [-da] [-MCCs]", required=False, action="append", help="Plots energy and its variance againt MCCs for both systems")
plots.add_argument(fakeStr("-fakeplotoptimalstep"), metavar = "acceptance-rate [--sim] [-a0] [-a1] [-da] [-omega] [-step0] [-step1] [-dstep] [-MCCs]", required=False, action="append", help="Plots the Acceptance rate")
plots.add_argument(fakeStr("-fakeplotoptimalstepfit"), metavar = "optimal-step-fit", required=False, action="append", help="Plots the optimal step fit of the m parameter.")
plots.add_argument(fakeStr("-fakeplotEvarE"), metavar = "E-varE [--sim] [-a0] [-a1] [-da] [-MCCs]", required=False, action="append", help="Plots E and its variance against alpha for both systems")
plots.add_argument(fakeStr("-fakeplot3Dbeta"), metavar = "3D-beta [--sim] [-a0] [-a1] [-da] [-b0] [-b1] [-db] [-omega] [-MCCs]", required=False, action="append", help="3D plot of energy for several alpha and beta")
# plots.add_argument(fakeStr("-fakeplotbetaparalell"), metavar = "beta-par [--sim]", required=False, action="append", help="Plots the number of accepted flips as a function of MCCs for T = 1.00, 1.35, 1.70, 2.05 and 2.40")
plots.add_argument(fakeStr("-fakeplotvirial"), metavar = "virial [--sim] ", required=False, action="append", help="Plots the virial ratio for both systems")

progparams = parser.add_argument_group("C++ Program parameters (specifics) \nNOTE: C++ programs must be run individually from terminal")
progparams.add_argument(fakeStr("-fakesingle"), metavar = "single ", required=False, action="append", help="Runs a single wave function for a single local energy. Default psi = T2, EL=E2, log10(MCCs)=7, omega=1, outfile=dump.dat")
progparams.add_argument(fakeStr("-fakeAlpha"), metavar = "variateAlpha ", required=False, action="append", help="Variates psi_T1 for noninteractive/interactive case. Default log10(MCCs)=7, a0=0.8, a1=1.2, da=0.1, solvmode 'noninteractive'")
progparams.add_argument(fakeStr("-fakeBeta"), metavar="variateBeta", required=False, action="append", help="Runs the individual variatons for α and β.")

examples = parser.add_argument_group("#Examples#")
examples.add_argument(fakeStr("-ex1"), metavar = "3D-beta", required=False, action="append", help="Plots D alpha/beta plot, given data files already exist")
examples.add_argument(fakeStr("-ex2"), metavar = "stability --sim -MCCs 4", required=False, action="append", help="Simulates the systems for default parameters with 10^4 MCCs and plots the stability")
examples.add_argument(fakeStr("-ex3"), metavar = "E-varE --sim -da 0.01", required=False, action="append", help="Calculates E and the variance for default alpha parameters, except for da=0.01")



def assignDefaults(args, defaults):
	for (arg,val),(darg, dval) in zip(args.__dict__.items(),defaults.items()):
		if (val == None) and (dval != None):
			args.__dict__[arg] = dval
	newargs = dict()
	for key, val in args.__dict__.items():
		if val != None:
			newargs[key] = val
	return newargs

def compile(name):
	os.chdir("../VMC/")
	os.system(f"make {name}")
	os.chdir("../plotting/")

if __name__ == "__main__":
	if not os.path.isdir("../data/"):
		subprocess.run(f"mkdir ../data".split())
	if not os.path.isdir("../compiled/"):
		subprocess.run(f"mkdir ../compiled".split())

	if len(sys.argv) == 2:
		if sys.argv[1] == "compile":
			compile("all")
			exit()

	args = parser.parse_args()
	defaults = {}
	for arg in args.__dict__.keys():
		defaults[arg] = None

	if args.type=="single":
		defaults["psi"] = "T2"
		defaults["EL"] = "E2"
		defaults["MCCs"] = 7
		defaults["omega"] = 1
		defaults["outfile"] = "dump.dat"

		args = assignDefaults(args,defaults)
		
		if not "runSingle.exe" in os.listdir("../compiled/"):
			compile("single")
		subprocess.run(f'../compiled/runSingle.exe {args["psi"]} {args["EL"]} {args["MCCs"]} {args["omega"]} {args["outfile"]}'.split())
	
	elif args.type =="variateAlpha":
		defaults["MCCs"] = 7
		defaults["a0"] = 0.8
		defaults["a1"] = 1.2
		defaults["da"] = 0.1
		defaults["solvemode"] = "noninteractive"

		args = assignDefaults(args,defaults)

		if not "variateAlpha.exe" in os.listdir("../compiled/"):
			compile("alpha")
		subprocess.run(f'../compiled/variateAlpha.exe {args["MCCs"]} {args["a0"]} {args["a1"]} {args["da"]} {args["solvemode"]}'.split())

	elif args.type=="variateBeta":
		if not "variateBeta.exe" in os.listdir("../compiled"):
			compile("beta")

		subprocess.run(f'../compiled/variateBeta.exe')

	elif args.type == "stability":
		defaults["sim"] = False
		defaults["MCCs"] = 7
		defaults["a0"] = 0.5
		defaults["a1"] = 1.5
		defaults["da"] = 0.05
		args = assignDefaults(args,defaults)
		plotStability.main(args["sim"], args["MCCs"], args["a0"], args["a1"], args["da"])

	elif args.type == "acceptance-rate":
		defaults["sim"] = False
		defaults["MCCs"] = 6
		defaults["a0"] = 0.9
		defaults["a1"] = 3
		defaults["da"] = 0.05
		defaults["step0"] = 7
		defaults["step1"] = 0.5
		defaults["dstep"] = 1.5
		defaults["omega"] = 1

		args = assignDefaults(args,defaults)
		plotAcceptancerate.main(args["sim"], args["omega"], args["a0"], args["a1"], args["da"], args["step0"], args["step1"], args["dstep"], args["MCCs"])
 
	elif args.type == "optimal-step-fit":
		optimalStepFitter.main()

	elif args.type == "E-varE":
		defaults["sim"] = False
		defaults["MCCs"] = 6
		defaults["a0"] = 0.5
		defaults["a1"] = 1.5
		defaults["da"] = 0.01
		args = assignDefaults(args, defaults)
		plotEvarEvsAlpha.main(args["sim"], args["a0"], args["a1"], args["da"], args["MCCs"])
	
	
	elif args.type == "3D-beta":
		defaults["sim"] = False
		defaults["MCCs"] = 6
		defaults["a0"] = 0.8
		defaults["a1"] = 1.4
		defaults["da"] = 0.00024
		defaults["b0"] = 0
		defaults["b1"] = 1
		defaults["db"] = 0.004
		defaults["omega"] = 1
		args = assignDefaults(args, defaults)
		plot3DVarBeta.main(args["sim"],args["a0"], args["a1"], args["da"],args["b0"], args["b1"], args["db"],args["omega"],args["MCCs"] )

	elif args.type == "beta-parallel":
		defaults["sim"] = False
		args = assignDefaults(args, defaults)
		plotVarBetaParallel.main(args["sim"])

	elif args.type == "virial":
		defaults["sim"] = False
		args = assignDefaults(args, defaults)
		plotVirial.main(args["sim"])

	
