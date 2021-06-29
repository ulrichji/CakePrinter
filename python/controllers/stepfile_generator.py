
def duplicateStep(step, number_of_repetitions):
	for i in range(number_of_repetitions):
		yield step

import sys
def main():
	if len(sys.argv) <= 1:
		print('Usage: python {} <step-output-file>'.format(sys.argv[0]))
		return

	stepslist = []
	stepslist.append(duplicateStep("(0,0,0)", 100))
	stepslist.append(duplicateStep("(1,0,0)", 300)) #This is about 300 mm
	stepslist.append(duplicateStep("(-1,0,0)", 400)) #To x - 100 mm
	stepslist.append(duplicateStep("(0,0,0)", 100))
	stepslist.append(duplicateStep("(0,1,1)", 200)) 
	stepslist.append(duplicateStep("(0,-1,1)", 300)) 
	stepslist.append(duplicateStep("(1,0,1)", 200))
	stepslist.append(duplicateStep("(0,0,0)", 100))
	stepslist.append(duplicateStep("(0,1,0)", 200))
	stepslist.append(duplicateStep("(0,0,0)", 200))
	stepslist.append(duplicateStep("(-1,-1,1)", 200))
	stepslist.append(duplicateStep("(0,1,0)", 200))
	stepslist.append(duplicateStep("(0,0,0)", 200))
	
	output_file_path = sys.argv[1]
	out = open(output_file_path,"w")
	out.write(','.join([','.join(sublist) for sublist in stepslist]))
	out.write('\n')
	out.close()
	

if __name__ == "__main__":
	main()
