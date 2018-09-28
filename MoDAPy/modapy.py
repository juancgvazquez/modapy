#!../venv/bin/python
import argparse
from sys import argv
from os import path
from MoDAPy.modules import panelmdl, duosmdl, output, cfg

class Parser(object):

	def __init__(self):
		parser = argparse.ArgumentParser(description="Multi-Omics Data Analisis for Python", usage='''modapy <command> [<args>]
        
        Commands:
        single  Run study on a single patient
        duos    Run Duos analysis on two selected patients
        trios   Run Trios analysis on three selected patients
        
        For more info on any of these commands, use "modapy <command> -h"''')

		parser.add_argument("command", help="Select command to run")

		# exclude all arguments but the first one
		args = parser.parse_args(argv[1:2])
		if not hasattr(self, args.command):
			print('Unrecognized commands')
			parser.print_help()
			exit(1)

		# goes to each command
		getattr(self, args.command)()


	def single(self):
		# Description for panel usage
		parser = argparse.ArgumentParser(description="Run study on a single patient")
		parser.add_argument("-Panel", required=True, help="File name of Panel inside Panels folder")
		parser.add_argument("-Patient", required=True,
							help="Patient File Path - It needs to match exactly to the one found inside Patients folder")
		# ignore first argument
		args = parser.parse_args(argv[2:])
		panel = cfg.panelsPath + args.Panel + '.xlsx'
		patient = cfg.patientPath + args.Patient
		ptCheck = checkFile(patient, '.vcf')
		pnCheck = checkFile(panel, '.xlsx')

		if (ptCheck & pnCheck):
			return panelmdl.panelrun(panel, patient)


	def duos(self):
		# Description for duos usage
		parser = argparse.ArgumentParser(description="Run Duos Study on two patients")
		parser.add_argument("-Patient1", required=True,
							help="Patient 1 File Path - It needs to match exactly to the one found inside Patients folder")
		parser.add_argument("-Patient2", required=True,
							help="Patient 2 File Path - It needs to match exactly to the one found inside Patients folder")
		parser.add_argument("-VennPlace", required=True, default='ALL', choices=['A','B','A:B','ALL'],
							help="Place in a Venn Diagram to obtain variants from")
		parser.add_argument("--Panel", help="Panel to run on Duos study")
		# ignore first argument
		args = parser.parse_args(argv[2:])
		patient1 = cfg.patientPath + args.Patient1
		patient2 = cfg.patientPath + args.Patient2
		# Checks file existence and type for patients
		pt1Check = checkFile(patient1, '.vcf')
		pt2Check = checkFile(patient2, '.vcf')
		if (pt1Check & pt2Check):
			print("Running Duos Study on", args.Patient1, args.Patient2)
			if args.panel:
				panel = cfg.panelsPath + args.Panel + '.xlsx'
				duos = duosmdl.duos(patient1, patient2)
				result = panelmdl.panelrun(panel, duos)
				outpath = cfg.resultsPath + 'Duos/' + duos.name + args.panel + '.xlsx'
			else:
				result = duosmdl.duos(patient1, patient2)
				outpath = cfg.resultsPath + 'Duos/' + result.name + '.xlsx'


			output.df_to_excel(result, outpath)
		else:
			print("Patient VCF couldn't be found in", cfg.patientPath + args.PatientFile + ".",
				  "Please check that file exists and is a .vcf")


	def trios(self):
		parser = argparse.ArgumentParser(description="Run Trios Study on two patients")
		parser.add_argument("-Patient1", required=True,
							help="Patient 1 File Path - It needs to match exactly to the one found inside Patients folder")
		parser.add_argument("-Patient2", required=True,
							help="Patient 2 File Path - It needs to match exactly to the one found inside Patients folder")
		parser.add_argument("-Patient3", required=True,
							help="Patient 3 File Path - It needs to match exactly to the one found inside Patients folder")
		parser.add_argument("--Panel", help="Panel to run on Trios study")
		parser.add_argument("--Filter", nargs=2,
							help="Filter to apply. This function will filter out every row that includes the given text"
								 " in the given column. For filtering Empty data, TEXT keyword is 'Empty'", metavar=("COLUMN", "TEXT"), action='append')
		parser.add_argument("--VennPlace", default='ALL', choices=['A','B','C','A:B','A:C','B:C','A:B:C','ALL'],
							help="Place in a Venn Diagram to obtain variants from")
		# ignore first argument
		args = parser.parse_args(argv[2:])
		patient1 = cfg.patientPath + args.Patient1
		patient2 = cfg.patientPath + args.Patient2
		patient3 = cfg.patientPath + args.Patient3
		# Checks file existence and type for patients
		pt1Check = checkFile(patient1, '.vcf')
		pt2Check = checkFile(patient2, '.vcf')
		pt3Check = checkFile(patient3, '.vcf')
		if (pt1Check & pt2Check & pt3Check):
			print("Running Trios Study on", args.Patient1, args.Patient2, args.Patient3)
			result = duosmdl.trios(patient1, patient2, patient3)
			outpath = cfg.resultsPath + 'Trios/' + result.name
			#check if there is a Panel Requested
			if args.Panel:
				panel = cfg.panelsPath + args.Panel + '.xlsx'
				result = panelmdl.panelrun(panel, result)
				outpath = outpath + '_' + args.Panel
			# check if there is a Filter Requested
			if args.Filter:
				for x in args.Filter:
					if x[1] == 'Empty':
						result = result[result[x[0]] != '']
					else:
						result = result[~result[x[0]].str.contains(x[1])]
					outpath = outpath + '-f' + str(x[0]) + str(x[1])
			# check if there is a special Venn Place Requested
			if args.VennPlace == 'A':
				result = result[result['Trios'] == result.name.split(':')[0]]
			if args.VennPlace == 'B':
				result = result[result['Trios'] == result.name.split(':')[1]]
			if args.VennPlace == 'C':
				result = result[result['Trios'] == result.name.split(':')[2]]
			if args.VennPlace == 'A:B':
				result = result[result['Trios'] == ':'.join([result.name.split(':')[0],result.name.split(':')[1]])]
			if args.VennPlace == 'A:C':
				result = result[result['Trios'] == ':'.join([result.name.split(':')[0],result.name.split(':')[2]])]
			if args.VennPlace == 'B:C':
				result = result[result['Trios'] == ':'.join([result.name.split(':')[1],result.name.split(':')[2]])]
			if args.VennPlace == 'A:B:C':
				result = result[result['Trios'] == ':'.join([result.name.split(':')[0],result.name.split(':')[1],result.name.split(':')[2]])]

			outpath = outpath + '.xlsx'
			output.df_to_excel(result, outpath)
		else:
			print("Patient VCF couldn't be found in", cfg.patientPath + args.PatientFile + ".")


def checkFile(filePath, extension):
	if path.isfile(filePath):
		fileName, fileExtension = path.splitext(filePath)
		if extension == fileExtension:
			return True

	print(filePath, "couldn't be found. Please check if file exists and that it's extension is", "'" + extension + "'")
	exit(1)


if __name__ == "__main__":
	Parser()