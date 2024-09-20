import contextlib
import pathlib
def savePythonSourceStringIntoMultipleFiles(sourceString:str,targetFolder:pathlib.Path,filePrefix="stub",linesPerFile=500,printProgressToConsole=True,stringToInsertAtTopOfEachFile=""):
    """By saving the source code into multiple files in a way where each file imports the next at the bottom of the file, PyLance can parse the code much much faster
    
    Its key that the import is at the bottom and not at the top (counterintuitive, isn't it?)"""
    with contextlib.suppress(FileNotFoundError):
        for file in targetFolder.glob('*'):
            file.unlink()
        targetFolder.rmdir() 
    targetFolder.mkdir(parents=True)
    fileNameFromIndex=lambda i: f'{filePrefix}{i}.pyi'
    stringParts=[""]
    i=-1
    lineCount=-1
    fileCount=0
    tryToSplit=False
    if printProgressToConsole:
        print(f"Processing file '{fileNameFromIndex(0)}'",end='\r')
    for char in sourceString:
        i+=1
        if char=='\n':
            lineCount+=1
            if lineCount%linesPerFile+1==linesPerFile:
                tryToSplit=True
        with contextlib.suppress(IndexError):
            if tryToSplit and char=='\n' and sourceString[i+1].isalpha():
                stringParts.append("")
                fileCount+=1
                tryToSplit=False
                if printProgressToConsole:
                    print(f"Processing file '{fileNameFromIndex(fileCount)}'",end='\r')
        stringParts[-1]+=char
    if len(stringToInsertAtTopOfEachFile) and stringToInsertAtTopOfEachFile[-1]!='\n':
        stringToInsertAtTopOfEachFile+='\n'
    i=-1 
    for stringPart in stringParts:
        i+=1
        prefixTypeChecking=f"\nif not typing.TYPE_CHECKING:\n    from .{filePrefix}{i-1} import *" if i != 0 else ""
        suffixTypeChecking=f"\nif typing.TYPE_CHECKING:\n    from .{filePrefix}{i+1} import *" if i!=len(stringParts)-1 else ""
        stringParts[i]=f"""import typing{prefixTypeChecking}
{stringToInsertAtTopOfEachFile}{stringPart}
{suffixTypeChecking}"""
    importStr=""
    i=-1
    for stringPart in stringParts:
        i+=1
        pathlib.Path(targetFolder/fileNameFromIndex(i)).open(mode='w+').write(stringPart)
        importStr+=f"from .{filePrefix}{i} import *"
    pathlib.Path(targetFolder/f"{filePrefix}.py").open(mode='w+').write(stringToInsertAtTopOfEachFile+sourceString)
    pathlib.Path(targetFolder/'__init__.py').open(mode='w+').write(f"""import typing
if typing.TYPE_CHECKING:
    del typing
    from .{filePrefix}0 import *
else:
    del typing
    from .{filePrefix} import *""")
    if printProgressToConsole:
        print(f"Success! generated files now available in '{targetFolder.resolve()}'")
