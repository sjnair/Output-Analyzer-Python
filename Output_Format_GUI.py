# load tkinter
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import linecache
import xlsxwriter
from xlsxwriter.utility import xl_range

fileDirectory="C:/"
# create GUI window
window = Tk()
window.geometry("1200x600")
window.title("Output Analyzer V1.1")

topFrame = Frame(window, height=50, width=906, bg="#EEE")
middleFrame = Frame(window, height=100, width=906, bg="#DDD")
middleFrame2 = Frame(window, width=906, bg="#EEE")
bottomFrame = Frame(window, height=600, width=906, bg="#CCC")
topFrame.pack(fill = X)
middleFrame.pack(fill = X)
middleFrame2.pack(fill = X)
bottomFrame.pack(side=LEFT, fill=Y)

# declare global variables
dutList = []
failingDUTSboolmaster = []
lineIndex = []
failLines = []
fileName=""
bits = 5
cores = 7
passString="10010"
patternCountString = StringVar()
linecount = 0
patternCountString.set("                                                                                                                   Patterns: ")
reportWIP = False
reportPatterns = []

def lineBreaks(step):
	global linecount
	outputList=[]
	global failLines
	global passString
	global bits
	global cores
	failLines = []
	passString = passingString.get()
	linecount = 0
	for n in range(0, len(DUTSelect.formatOutput),step):
		linecount+=1
		if n+step<len(DUTSelect.formatOutput):
			output = DUTSelect.formatOutput[n:(n+step)] + " " + str(linecount) + "\n"
			outputList.append(output)
			if passString not in output:
				failingUI.insert(END, linecount)
				failLines.append(linecount)

		else:
			output = DUTSelect.formatOutput[n:(n+step)] 
			outputList.append(output)

	patternCountString.set("                                                                                                                   Patterns: "+str(linecount-1)+"              "+str((linecount-1)*int(bits)*int(cores))+" / "+str(len(DUTSelect.formatOutput)-1)+" bits")
	return ''.join(outputList)

def patternSelect(event):
	global dutList
	global failingDUTSboolmaster
	global masterTDONotFound
	global masterDUTDisabled
	patternSelect.patternSelected = int((''.join(map(str,patternListUI.curselection()))))
	outputDisplay.delete('1.0', END)
	#Empty out the DUT list
	DUTListUI.delete(0,'end')
	#Empty out the failing line list
	failingUI.delete(0, END)
	patternCountString.set("                                                                                                                   Patterns: ")
	reportPatterns.append(patternSelect.patternSelected)
	for x in range(len(dutList)):
		#dutArray is a list that contains boolean values of whether each DUT is passing or not for a specific pattern
		#it draws its values from a list of lists, failingDUTSboolmaster
		dutArray = failingDUTSboolmaster[patternSelect.patternSelected]
		if dutArray[x]:
			DUTListUI.insert(END, dutList[x] + '\n')
			DUTListUI.itemconfig(x, foreground="green")
		else:
			DUTListUI.insert(END, dutList[x] + '\n')
			DUTListUI.itemconfig(x, foreground="red")
		if dutList[x] in masterTDONotFound[patternSelect.patternSelected]:
			DUTListUI.itemconfig(x, foreground="orange")
		if dutList[x] in masterDUTDisabled[patternSelect.patternSelected]:
			DUTListUI.itemconfig(x, foreground="black")

def highlight():
	global bits
	global cores
	global passString
	failingCores = []
	totalChar = str(int(bits)*int(cores))
	for x in range(linecount):
		for y in range(0,int(totalChar),int(bits)*2):
			outputDisplay.tag_add("cores", str(x)+"."+str(y), str(x)+"."+str(y+int(bits)))
	
	if (len(passString) == int(bits)*int(cores)):

		for z in failLines:
			coreCount=0
			for x in range(0,int(bits)*int(cores),int(bits)):
				failingCoreBool=False
				coreCount+=1
				for y in range(0,int(bits)):
				
					if (outputDisplay.get(str(z)+"."+str(x+y),str(z)+"."+str(x+y+1))) == passString[x+y]:
						
						pass
					else:
						
						failingCoreBool=True
				if (failingCoreBool):
					outputDisplay.tag_add("fail", str(z)+"."+str(x), str(z)+"."+str(x+int(bits)) )
					failingCores.append(coreCount)
				
			failingCoresString = str(failingCores).strip('[]')
			failingCoresString = failingCoresString.replace(" ", "")
			outputDisplay.insert(str(z)+".0 lineend", " ("+failingCoresString+") ")
			failingCores=[]
	else:
		messagebox.showinfo("Warning", "Passing string does not match core/bit length")

def DUTSelect(event):
	global lineIndex
	global fileName
	global bits
	global cores
	DUTSelected = int((''.join(map(str,DUTListUI.curselection()))))
	outputDisplay.delete('1.0', END)
	failingUI.delete(0, END)
	outputLine = lineIndex[patternSelect.patternSelected]+len(dutList)+DUTSelected+1
	rawOutput = linecache.getline(fileName,outputLine)
	sepOutput = rawOutput.split(",")
	sepOutput = sepOutput[3].split(' ')
	if (sepOutput[2]=='was'):
		failingUI.delete(0, END)
		outputDisplay.insert(END, "TDO not found")
	elif (sepOutput[2]=='DUT'):
		failingUI.delete(0, END)
		outputDisplay.insert(END, "DUT was disabled")
	else:
		bits = bitsInput.get()
		cores = coresInput.get()
		DUTSelect.formatOutput = sepOutput[2]
		DUTSelect.count=0
		outputDisplay.insert(END, lineBreaks(int(bits)*int(cores)))
		highlight()

def failSelect(event):
	outputDisplay.see(str(failingUI.get(failingUI.curselection()))+".0")

def readFile(fileName):
	global file

	#If Report Mode checked, execute excel() function
	

	file = open(fileName,"r")
	process()



def reportCallback():
	global reportWIP

	#actions that get triggered when you click/unclick checkbox
	if (reportCheckVar.get()):
		#when you click the report mode checkbox
		pass
	else:
		#when you unclick the report mode checkbox
		#write the data from the selected patterns (reportPatterns) to the current sheet
		createNewSheet()
		if reportWIP:
			workbook.close()
		reportWIP = False
		#close file
		#open file in excel?
def excel():
	global reportWIP

	#If reportWIP is false, that means this is a new report, so create the file
	if not reportWIP:
		createNewFile()
	#If reportWIP is true, that means this report is in progress, so push the selected data to a sheet
	else:	
		createNewSheet()

		

def createNewFile():
	global workbook, reportWIP, failFormat, passFormat, rightAlign, disabledFormat, DUTFormat, borderFormat, fileDirectory

	if not reportWIP:
		#pop-up to define name of report
		reportFileName = simpledialog.askstring("Input", "Report Name:", parent=window)
		#create new excel file
		workbook = xlsxwriter.Workbook(fileDirectory + reportFileName + '.xlsx')
		failFormat = workbook.add_format()
		failFormat.set_bg_color("e74c3c")
		failFormat.set_align('center')
		passFormat = workbook.add_format()
		passFormat.set_bg_color("2ecc71")
		passFormat.set_align('center')
		rightAlign = workbook.add_format()
		rightAlign.set_align('right')
		disabledFormat = workbook.add_format()
		disabledFormat.set_bg_color("a9a9a9")
		disabledFormat.set_align('center')
		DUTFormat = workbook.add_format()
		DUTFormat.set_align('center')
		DUTFormat.set_bg_color("C2C5CC")
		borderFormat = workbook.add_format({'border': 1})
		reportWIP = True

def createNewSheet():
	global workbook
	global worksheet
	global reportWIP
	global rightAlign
	global passFormat
	global failFormat
	global sheetName
	global disabledFormat
	global DUTFormat
	global borderFormat
	global reportPatterns 
	global patternList
	global dutList
	global failingDUTSboolmaster
	global masterDUTDisabled
	
	worksheet = workbook.add_worksheet(sheetName)

	for x in range(len(reportPatterns)):
			worksheet.write(x+1, 0, patternList[reportPatterns[x]], rightAlign)

	for x in range(len(dutList)):
		worksheet.write(0,1+x,dutList[x], DUTFormat)

	for x in range(0,len(reportPatterns)):
		for y in range(len(dutList)):
			if failingDUTSboolmaster[reportPatterns[x]][y]:
				worksheet.write(x+1, y+1, "PASS", passFormat)

			else:
				worksheet.write(x+1, y+1, "FAIL", failFormat)

			#if dutList for this x matches a value in masterDUTDisabled, write "OFF"
			if dutList[y] in masterDUTDisabled[reportPatterns[x]]:
				worksheet.write(x+1, y+1, "OFF", disabledFormat)

	worksheet.conditional_format( xl_range(0,0,len(reportPatterns),len(dutList)) , { 'type' : 'cell' , 'criteria' : '>=', 'value' : 0, 'format' : borderFormat} )
	worksheet.set_column('A:A', 40)
	worksheet.set_column(xl_range(1,1,len(reportPatterns),len(dutList)), 5)
	reportPatterns = []

	
	#write data


def fileUpload():
	global dutList
	global fileName
	global reportPatterns
	global sheetName
	global fileDirectory

	#When you upload a new file, if Report mode is checked, write the selected data to the current sheet before opening new file

	linecache.clearcache()
	DUTListUI.delete(0, END)
	patternListUI.delete(0, END)
	outputDisplay.delete('1.0', END)
	filePathDisplay.delete('1.0', END)
	#if there is a file open, close it before opening the new one
	if (reportCheckVar.get() and reportWIP):
		excel()
	if dutList:
		file.close()
	dutList=[]
	reportPatterns = []
	fileName = askopenfilename(initialdir=fileDirectory, filetypes =(("All Files","*.*"),("Text File", "*.txt")), title = "Choose a file.")
	sheetName = fileName.split('/')
	sheetName = sheetName[-1]
	sheetName = sheetName.split('.')
	sheetName = sheetName[0]
	fileDirectory = fileName.split(sheetName)
	fileDirectory = fileDirectory[0]
	if (reportCheckVar.get() and not reportWIP):
		excel()
	readFile(fileName)
	filePathDisplay.insert(END, fileName)

def process():
	lineCount = 0
	passFailList = []
	passFailBool = True
	global patternList
	#dutList is just one list, with the list of DUTs for this file
	global dutList
	dutCount = False
	failingDUTS = []
	failingDUTSmaster = []
	DUTstring = ""
	disabledString = ""
	global lineIndex
	failingDUTSbool = []
	global failingDUTSboolmaster
	global masterDUTDisabled
	global masterTDONotFound
	patternList = []
	patternTDONotFound = []
	masterTDONotFound = []
	patternDUTDisabled = []
	masterDUTDisabled = []
	loopCountList = []
	loopNumber = 1

	failingDUTSboolmaster = []
	lineIndex=[]

	for line in file:
	
		if ("Loop " in line):
			lineCount += 1
			patternBool = False
			# splits up line by , delimiter
			fields = line.split(',')
			loopNumber = fields[0].split(' ')
			loopNumber = loopNumber[1]
			#add to list and empty list
			if "TDO was Not found on pattern" in fields[3]:
				TDOfail = fields[1].split(' ')
				patternTDONotFound.append(TDOfail[2])
				
			if "DUT was disabled" in fields[3]:
				DUTfail = fields[1].split(' ')
				patternDUTDisabled.append(DUTfail[2])
			#Check for fail
			if (fields[3] == " Failures 1"):
				dut = fields[1].split(' ')
				failingDUTS.append(dut[2])
				failingDUTSbool.append(0)
				passFailBool = False
			elif (fields[3] == " Failures 0"):
				failingDUTSbool.append(1)
			
			if (dutCount == False):
				
				dutNumber = fields[1].split(' ')
				if dutNumber[2] not in dutList:
					dutList.append(dutNumber[2])
				else:
					dutCount = True
		else:
			lineCount+=1
			loopCountList.append(loopNumber)
			fields = line.split(" ")
			patternList.append(fields[0])
			lineIndex.append(lineCount)
			passFailList.append(passFailBool)
			passFailBool = True
			failingDUTSmaster.append(failingDUTS)
			failingDUTSboolmaster.append(failingDUTSbool)
			failingDUTSbool=[]
			failingDUTS=[]
			masterTDONotFound.append(patternTDONotFound)
			masterDUTDisabled.append(patternDUTDisabled)
			patternTDONotFound=[]
			patternDUTDisabled=[]

	#This covers the final pattern run, making sure you update the lists with the final line
	#[1:] removes the first null entry to align with linecount
	passFailList.append(passFailBool)
	failingDUTSmaster.append(failingDUTS)
	failingDUTSboolmaster.append(failingDUTSbool)
	masterTDONotFound.append(patternTDONotFound)
	masterDUTDisabled.append(patternDUTDisabled)
	loopCountList.append(loopNumber)
	failingDUTSmaster = failingDUTSmaster[1:]
	passFailList = passFailList[1:]
	failingDUTSboolmaster = failingDUTSboolmaster[1:]
	masterTDONotFound=masterTDONotFound[1:]
	masterDUTDisabled=masterDUTDisabled[1:]

	for x in range(len(dutList)):
			DUTListUI.insert(END, dutList[x] + '\n')

	for x in range(len(patternList)):
		disabledString = ",".join(masterDUTDisabled[x])

		if passFailList[x]:
			if masterDUTDisabled[x]:
				patternListUI.insert(END, str(loopCountList[x]) + " " + patternList[x] + '\n' + " (" + disabledString + " OFF)")
				patternListUI.itemconfig(x, foreground="green")
			else:
				patternListUI.insert(END, str(loopCountList[x]) + " " + patternList[x] + '\n')
				patternListUI.itemconfig(x, foreground="green")
		else:
			DUTstring = ",".join(failingDUTSmaster[x])

			if masterDUTDisabled[x]:
				patternListUI.insert(END, str(loopCountList[x]) + " " + patternList[x] + " (" + DUTstring + ")" + " (" + disabledString + " OFF)")
			else:
				patternListUI.insert(END, str(loopCountList[x]) + " " + patternList[x] + " (" + DUTstring + ")")
			patternListUI.itemconfig(x, foreground="red")

#insert any commands that you want to execute when the window is closed
def windowClose(*args):
	global dutList
	if dutList:
		file.close()

	if reportWIP:
		createNewSheet()
		workbook.close()

#this defines updates that execute when user presses return

def func(event):
	DUTSelect('<<ListboxSelect>>')

window.bind('<Return>', func)

#GUI elements

patternScroll = Scrollbar(bottomFrame)
patternListUI = Listbox(bottomFrame, width = 60)
patternListUI.bind('<<ListboxSelect>>', patternSelect)
DUTScroll = Scrollbar(bottomFrame)
DUTFrame = Frame(bottomFrame, width = 100,bg="#DDD")
DUTListUI = Listbox(DUTFrame, width = 10, height = 10)
DUTListUI.bind('<<ListboxSelect>>', DUTSelect)
outputDisplay = Text(bottomFrame, width = 80)
outputScroll = Scrollbar(bottomFrame)
filePathDisplay = Text(topFrame, height=1, width=800,background="#EEE")
uploadButton = Button(topFrame, text="Upload file", command = fileUpload)
passLabel = Label(middleFrame, text="Pass:")
passingString = Entry(middleFrame, width = 700)
passingString.bind("<Return>", DUTSelect)
bitsLabel = Label(middleFrame2, text="Bits:")
bitsInput = Entry(middleFrame2, width = 5)
coresLabel = Label(middleFrame2, text="Cores:")
coresInput = Entry(middleFrame2, width = 5)
patternCount = Label(middleFrame2, textvariable=patternCountString)
failingUI = Listbox(bottomFrame, width = 10, fg="red")
failingUI.bind('<<ListboxSelect>>', failSelect)
failingScroll = Scrollbar(bottomFrame)
reportCheckVar = IntVar()
reportCheck = Checkbutton(middleFrame2, text="Report mode", variable=reportCheckVar, command=reportCallback)

bitsInput.insert(END,bits)
coresInput.insert(END,cores)
passingString.insert(END,passString)

patternListUI.config(yscrollcommand=patternScroll.set, exportselection=False)
patternScroll.config(command=patternListUI.yview)
DUTListUI.config(yscrollcommand=DUTScroll.set,  exportselection=False)
DUTScroll.config(command=DUTListUI.yview)
outputDisplay.config(yscrollcommand=outputScroll.set)
outputScroll.config(command=outputDisplay.yview)
failingUI.config(yscrollcommand=failingScroll.set, justify=RIGHT, exportselection=False)
failingScroll.config(command=failingUI.yview)
outputDisplay.tag_config("fail", foreground="red")
outputDisplay.tag_config("cores", background="#f2f2f2")

patternListUI.pack(side=LEFT, fill=Y)
patternScroll.pack(side=LEFT, fill=Y)
DUTListUI.pack(side=TOP)
DUTFrame.pack(side=LEFT, fill=Y)
outputDisplay.pack(side=LEFT, fill=Y)
outputScroll.pack(side=LEFT, fill=Y)
uploadButton.pack(side=LEFT)
filePathDisplay.pack(side=LEFT)
passLabel.pack(side=LEFT)
passingString.pack(side=LEFT)
coresInput.pack(side=RIGHT)
coresLabel.pack(side=RIGHT)
bitsInput.pack(side=RIGHT)
bitsLabel.pack(side=RIGHT)
reportCheck.pack(side=LEFT, fill=Y)
patternCount.pack(side=LEFT, fill=X)
failingUI.pack(side=LEFT, fill=Y)
failingScroll.pack(side=LEFT, fill=Y)

#this binds the window closing to a function
uploadButton.bind('<Destroy>', windowClose)
window.mainloop()
