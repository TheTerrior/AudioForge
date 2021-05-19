import sys
import os
import subprocess
import PySimpleGUIQt as sg
import tempfile
import shutil
from pathlib import Path

def setup():
    global layout, window, temp_folder, filetypes
    
    temp_folder = ""
    filetypes = [".wav", ".flac", ".wv", ".aiff"]

    comparetab = [[sg.Text('Please choose two files to compare.', font = ("Helvetica", 12))], [sg.InputText(size = (200,30)), sg.FileBrowse(size = (70, 30))], 
        [sg.InputText(size = (200,30)), sg.FileBrowse(size = (70, 30))], 
        [sg.Button("OK", size = (70, 30), key = "_COMPAREOK_"), 
        sg.Radio("Simple", "COMPARERADIO", default = False, font = ("Helvetica", 10), size = (7,0.5)), 
        sg.Radio("Advanced", "COMPARERADIO", default = True, font = ("Helvetica", 10), enable_events = True, key = "_COMPARERADIO_", size = (9,0.5))], 
        [sg.Text('Result:', size = (20,1), key = '_OUTPUT_', font = ("Helvetica", 12))]]
    converttab = [[sg.Text('Please choose a file to convert.', font = ("Helvetica", 12))], [sg.InputText(size = (200,30)), sg.FileBrowse(size = (70, 30))], 
        [sg.InputText(size = (200,30), disabled = True, background_color = "grey", key = "_CONVERTFILEINPUT_"), 
        sg.FileBrowse(size = (70, 30), disabled = True, button_color = ("white", "#606060"), key = "_CONVERTFILEBROWSE_")], 
        [sg.Button("OK", size = (70, 30), key = "_CONVERTOK_"), 
        sg.Checkbox('Custom', default = False, key = "_CONVERTCUSTOM_", enable_events = True, size = (80, 20)),
        sg.Combo(["AIFF", "FLAC", "WAV", "WV"], default_value = "WAV", size = (60, 20), key = "_CONVERTCOMBO_")], 
        [sg.Text('Result:', size = (30,1), key = '_OUTPUT2_', font = ("Helvetica", 12))]]
    convertplustab = [[sg.Text('Please choose a folder to convert.', font = ("Helvetica", 12))], [sg.InputText(size = (200,30)), sg.FileBrowse(size = (70, 30))],
        [sg.Text('From', size = (40,30), font = ("Helvetica", 12)), 
        sg.Combo(["ANY", "AIFF", "FLAC", "WAV", "WV"], default_value = "ANY", size = (60, 20), key = "_CONVERT+COMBO_"), 
        sg.Text('to', size = (15,30), font = ("Helvetica", 12)),
        sg.Combo(["AIFF", "FLAC", "WAV", "WV"], default_value = "WV", size = (60, 20), key = "_CONVERT+COMBO1_")],
        [sg.Button("OK", size = (70, 30), key = "_CONVERT+OK_"),
        sg.Checkbox('Include subdirectories', default = False, key = "_CONVERT+CUSTOM_", enable_events = True, size = (160, 20))], 
        [sg.Text('Result:', size = (30,1), key = '_OUTPUT3_', font = ("Helvetica", 12))]]
    layout = [[sg.TabGroup([[sg.Tab('Compare', comparetab), sg.Tab('Convert', converttab), sg.Tab('Convert+', convertplustab)]], 
        key = "_TAB_")]]
    window = sg.Window('AudioForge', layout, size = (10,50))

def fixfilenames(filenames): #if files were dragged n dropped, this will fix, otherwise unaffected
    files = []
    for x in filenames: #some quick conversion in case the file was loaded via drag and drop
        if (len(x) > 8 and x[0:8] == "file:///"):
            # file:///mnt/sdb2/.My%20Files/Music/temporarily/wavpack%20untagged/Hayami%20-%20Blood%20Rain%20VIP.wv
            # /mnt/sdb2/.My Files/Music/temporarily/wavpack untagged/Hayami - Blood Rain VIP.wv
            # x = x[7:-2].replace("%20", " ").replace("%5B", "[").replace("%5D", "]")
            x = x[7:].rstrip().replace("%20", " ").replace("%5B", "[").replace("%5D", "]")
        else:
            x = x.rstrip()
        files.append(x)
    return files

def getextension(filename):
    location = filename.rfind(".")
    if location == -1: return ""
    return filename[location:]

def removeextension(filename):
    location = filename.rfind(".")
    if location == -1: return filename
    return filename[:location]

def getfilename(filename):
    location = filename.rfind("/")
    if location == -1: return filename
    return filename[location + 1:]

def removefilename(filename):
    location = filename.rfind("/")
    if location == -1: return filename
    return filename[:location + 1]

def convert(filename, filename1):   #actual conversion program, converts filename to filename1
    global temp_folder, filetypes
    alter = False
    extension = getextension(filename)
    extension1 = getextension(filename1)
    if extension == filename or extension1 == filename1:    #if the provided file is just a file extension
        print("Inputs contain an empty filename.")
        return ["Error Occurred", "#770000"] 
    elif extension in filetypes and extension1 in filetypes:    #a valid file is provided, now check if it exists, and handle same type conversion
        try:
            #create a check for the existence of the folder it's in, otherwise create it
            if not os.path.isdir(removefilename(filename1)):
                os.mkdir(removefilename(filename1))
            if filename == filename1:   #duplicated item, copy and rename filename, add "_1" at the end########################################
                print("duplicate")
                copyfile(filename, removeextension(filename1) + "_1" + getextension(filename1))
                return ["Successful Convert", "#44FF44"]
            #here use a while loop to ensure that filename1 is not in use, tag on _i and keep incrementing i, shouldn't affect temporary folders
            if os.path.isfile(filename1):
                print("The file exists already, adjusting")
                alter = True
                smallfilename1 = removeextension(filename1)
                i = 1
                while os.path.isfile(smallfilename1 + "_" + str(i) + extension1):
                    i += 1
                filename1 = smallfilename1 + "_" + str(i) + extension1
            if extension == extension1:   #same-type conversion, just copy filename and rename to filename1
                print("same-type")
                shutil.copyfile(filename, filename1)
            else:   #this case scenario could have different conversions that may require different commandline programs, flac wvpack ffmpeg
                #wav -> wv      wvpack -h -v "filename.wav" "filename.wv"
                #wv -> wav      wavunpack "filename.wv" "filename.wav"
                #wav -> flac    flac --best --verify "filename.wav" -o "filename.flac"      Note, these flacs work for .aiff too
                #flac -> wav    flac -d "filename.flac" -o "filename.wav"
                #otherwise      ffmpeg -i "filename.x" "filename.y"
                if extension != ".wav": #you want to convert to wav first before converting to something else
                    if extension1 == ".wav":
                        print("alternate to wav, extension = " + extension)
                        print("filename is " + filename)
                        print("filename1 is " + filename1)
                        if extension == ".wv": x = subprocess.check_output(['wvunpack', filename, '-o', filename1])
                        elif extension == ".flac": x = subprocess.check_output(['flac', '-d', filename, '-o', filename1])
                        else: x = subprocess.check_output(['ffmpeg', '-i', filename, filename1])
                        print("Terminal Output: ")
                        print(x)
                    else: #convert to wav, then update filename and extension to reflect this change
                        print("Doing recursive conversions")
                        if temp_folder != "":
                            print("temp_folder already exists, using it")
                            #run convert from filename to filename inside of temp_folder and as a .wav, then update filename to be .wav and continue
                            newfilename = temp_folder + getfilename(removeextension(filename) + ".wav")
                            convert(filename, newfilename)
                            #filename = newfilename
                            #extension = ".wav"
                        else:
                            print("temp_folder doesn't exist, creating it")
                            print("filename is " + filename)
                            print("filename1 is " + filename1)
                            with tempfile.TemporaryDirectory() as temp_folder:  #create a temp folder, then handle the rest of the conversions with it
                                newfilename = temp_folder + getfilename(removeextension(filename) + ".wav")
                                convert(filename, newfilename)
                                filename = newfilename
                                print("filename updated to " + filename)
                                print("filename1 is " + filename1)
                                convert(filename, filename1)
                            temp_folder = ""
                else: #first extension is wav
                    print("wav to else")
                    if extension1 == ".wv": x = subprocess.check_output(['wavpack', '-h', '-v', filename, '-o', filename1])
                    elif extension1 == ".flac": x = subprocess.check_output(['flac', '--best', '--verify', filename, '-o', filename1])
                    else: x = subprocess.check_output(['ffmpeg', '-i', filename, filename1])
                    print("Terminal Output: ")
                    print(x)
                print("normal conversion")

            print("returning success")
            returnlist = ["Conversion Successful", "#44FF44"] #if filename1 has been altered, return the new name in the return list, can check for size of return
            if alter:
                returnlist.append(filename1)
            return returnlist
        except:
            print("Error occurred during conversion.")
            return ["Error Occurred", "#770000"]
    else:
        print("Inputs contain an unsupported filetype.")    #if the filetypes provided are unsupported
        return ["Error Occurred", "#770000"]

def compare(filename, filename1): #the actual comparison between the two files
    if not (os.path.isfile(filename) and os.path.isfile(filename1)):
        print("At least one of the two files being compared does not exist.")
        return ["Error Occurred", "#770000"]
    try:
        string = subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', filename, '-map', '0', '-f', 'hash', '-'])  #tell the command line to compare
        string1 = subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', filename1, '-map', '0', '-f', 'hash', '-'])
        if (string == string1): return ["Bit-Perfect", "#44FF44"]
        else: return ["Not Bit-Perfect", "#AA0000"]
    except:
        print("Error during checking, either one of the files doesn't exist or there was an issue reading it.") #if we run into an issue
        return ["Error Occurred", "#770000"]

def comparemain(key):    #prepares program to compare files, but may be used by different parts of the program
    global event, values
    if key == "_OUTPUT_": keys = [0, 1]
    if values[keys[0]] == "" or values[keys[1]] == "":  #if at least one field is missing, dont activate the command line
        results = ["Missing Fields", "#FFFFFF"]
    else:   #if no fields are missing, then continue with the comparison process
        window.FindElement(key).update("Result: Processing...", visible = True, text_color = "#FFFFFF")
        window.Refresh()
        files = fixfilenames([values[keys[0]], values[keys[1]]])
        results = compare(files[0], files[1])
    window.FindElement(key).update("Result: " + results[0], visible = True, text_color = results[1]) #update the output

def convertmain(key):
    global event, values, temp_folder, filetypes
    if key == "_OUTPUT2_": keys = [2, "_CONVERTFILEINPUT_"]
    elif key == "_OUTPUT_" and values["_COMPARERADIO_"]: keys = [0, 1]
    elif key == "_OUTPUT3_": keys = [3, 3]
    if values[keys[0]] == "" or values[keys[1]] == "":  #if at least one field is missing, dont activate the command line
        results = ["Missing Fields", "#FFFFFF"]
    else:   #if no fields are missing, then continue with the conversion process
        window.FindElement(key).update("Result: Processing...", visible = True, text_color = "#FFFFFF")
        window.Refresh()
        files = fixfilenames([values[keys[0]], values[keys[1]]])
        if key == "_OUTPUT_" and values["_COMPARERADIO_"]:  #if output1, then convert both keys to wav, else convert key 1 to key 2
            print(files)
            newfiles = []
            for x in files:
                newfiles.append(temp_folder + "/" + removeextension(getfilename(x)) + ".wav") #newfiles contains the new wavs in the temp folder
            values[0] = newfiles[0]
            values[1] = newfiles[1]
            print(newfiles)
            results = convert(files[0], newfiles[0])    #try to convert the first file, see if it bugged or not
            if results[0] != "Error Occurred":
                moreresults = []
                if len(results) == 3:
                    moreresults.append(results[2])
                results = convert(files[1], newfiles[1])
                print(results)
                print(moreresults)
                if len(results) == 3:
                    moreresults.append(results[2])
                    print(moreresults)
                if len(moreresults) > 0:
                    results = [results[0], results[1]] #this is to return a list of max of 4, with the two changed files in order
                    results.extend(moreresults)
                    print(results)
        elif key == "_OUTPUT2_":
            results = convert(files[0], files[1])
        elif key == "_OUTPUT3_":
            #need to check all files in the folder and see if they match the selected "from" type
            #if so, then convert that file to the "to" type

            error = False
            errors = []

            folder = files[0]
            for root, dirs, files in os.walk(folder): 
                #create a new folder, convert
                newfolder = folder + "_converted"
                if not values["_CONVERT+CUSTOM_"] and root != folder: #if subdirectories disabled, and root != folder, then skip that subdirectory
                    continue
                else:
                    newroot = root.replace(folder, newfolder)
                for filename in files: #all files we plan to convert and move
                    if ((values["_CONVERT+COMBO_"] == "ANY" and getextension(filename) in filetypes) or
                        (values["_CONVERT+COMBO_"] == "WAV" and getextension(filename) == ".wav") or
                        (values["_CONVERT+COMBO_"] == "WV" and getextension(filename) == ".wv") or
                        (values["_CONVERT+COMBO_"] == "FLAC" and getextension(filename) == ".flac") or
                        (values["_CONVERT+COMBO_"] == "AIFF" and getextension(filename) == ".aiff")):
                        file = os.path.join(root, filename) #the filename is stored in filename, and its path is stored in root
                        newfile = removeextension(os.path.join(newroot, filename)) + "." + values["_CONVERT+COMBO1_"].lower()
                        print(file)
                        print(newfile)
                        if not os.path.isdir(newroot): #this whole loop can be highly optimized, but this works for now
                            os.mkdir(newroot)
                        result = convert(file, newfile)
                        if result[0] != "Conversion Successful":
                            print("Error Occurred during conversion")
                            errors.append(newfile.replace(folder + "_converted/", ""))
                            error = True
                    else:
                        print("rejected " + filename)
                if error:
                    print("List of failed conversions: ")
                    for x in errors: print(x)
                    results = ["Finished With Errors", "#770000"]
                else: results = ["Conversion Successful", "#44FF44"]

    print(results)
    window.FindElement(key).update("Result: " + results[0], visible = True, text_color = results[1]) #update the output
    return results



def main():
    global event, values, temp_folder
    running = True
    convertstorage = ""
    convertplusstorage = ""
    while (running):
        event, values = window.read(timeout = 10)
        #print(values)
        if event == sg.WIN_CLOSED or event == "Exit" or event == None:
            running = False
            window.close()
            break
        elif event == "_COMPAREOK_" and not values["_COMPARERADIO_"]:    #pressed ok on the compare tab, simple mode (compare two files)
            comparemain('_OUTPUT_')
        elif event == "_COMPAREOK_" and values["_COMPARERADIO_"]:   #pressed ok on the compare tab, advanced mode (convert and compare two files)
            print(values)
            files = fixfilenames([values[0], values[1]])
            print(files)
            if not (os.path.isfile(files[0]) and os.path.isfile(files[1])):
                results = ["Invalid Fields", "#FFFFFF"]
                window.FindElement("_OUTPUT_").update("Result: " + results[0], visible = True, text_color = results[1])
                continue
            with tempfile.TemporaryDirectory() as temp_folder: #if temp_folder equals an index, then that temporary folder is still active
                print(temp_folder)
                results = convertmain('_OUTPUT_')
                if results[0] != "Error Occurred" and results[0] != "BETA":  #continue if no error occurred and beta is complete
                    if len(results) > 2: #if there were file names changed, change them now
                        print("Changing filenames according to conversion process")
                        values[0] = results[2]
                        if len(results) == 4: 
                            values[1] = results[3]
                        print("Comparing " + values[0] + " and " + values[1])
                    comparemain('_OUTPUT_')
                else:
                    window.FindElement("_OUTPUT_").update("Result: " + results[0], visible = True, text_color = results[1]) #update the output if error found
            temp_folder = "" #rest temp_folder to signal that there is no temp_folder in existence
        elif event == "_CONVERTOK_":    #pressed ok on the convert tab
            print(values)
            if not os.path.isfile(fixfilenames([values[2]])[0]):
                results = ["Invalid Fields", "#FFFFFF"]
                window.FindElement("_OUTPUT2_").update("Result: " + results[0], visible = True, text_color = results[1])
                continue
            convertmain('_OUTPUT2_')
        elif event == "_CONVERTCUSTOM_":       #flicked the checkbox on the convert tab
            if values["_CONVERTCUSTOM_"]:
                window.FindElement('_CONVERTFILEINPUT_').update(disabled = False, background_color = "white")
                window.FindElement('_CONVERTFILEBROWSE_').update(disabled = False, button_color = ("white", "#283b5b")) #default button color
                window.FindElement('_CONVERTCOMBO_').update(disabled = True, visible = False)
            else:
                window.FindElement('_CONVERTFILEINPUT_').update(disabled = True, background_color = "grey")
                window.FindElement('_CONVERTFILEBROWSE_').update(disabled = True, button_color = ("white", "#606060"))
                window.FindElement('_CONVERTCOMBO_').update(disabled = False, visible = True)
        elif event == "_CONVERT+OK_":   #pressed ok on the convert+ tab
            print(values)
            if not os.path.isdir(fixfilenames([values[3]])[0]):
                results = ["Invalid Fields", "#FFFFFF"]
                window.FindElement("_OUTPUT3_").update("Result: " + results[0], visible = True, text_color = results[1])
                continue
            convertmain('_OUTPUT3_')
        elif event != "__TIMEOUT__":
            pass

        #we need to update the conversion fields as the user types

        if not values["_CONVERTCUSTOM_"] and values[2] != convertstorage:
            newfile = removeextension(values[2]) + "." + values["_CONVERTCOMBO_"].lower()
            window.FindElement('_CONVERTFILEINPUT_').update(newfile)

setup()
main()