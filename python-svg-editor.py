import sys
import tkinter
from tkinter import font
import cairosvg
from PIL import Image, ImageTk
from io import BytesIO
from pathlib import Path
import tkinter.filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import duckdb
import math

filepath = ""
svgText = ""
fontSize = 12
lastCursorPosition = 1.0
autoCompleteSelectionIndex = -1
autoCompleteItemsG = []


def UpdateCursorPosition(event):
    global lastCursorPosition
    global listbox
    global autoCompleteItemsG
    print(event.keysym)
    downPressed = False
    upPressed = False
    rightPressed = False
    if len(autoCompleteItemsG) > 0:
        if event.keysym == "Down":
            downPressed = True
            sourceText.mark_set("insert", lastCursorPosition)
        if event.keysym == "Up":
            upPressed = True
            sourceText.mark_set("insert", lastCursorPosition)
        if event.keysym == "Right" or event.keysym == "Return":
            rightPressed = True
            sourceText.mark_set("insert", lastCursorPosition)
    cursorPosition = sourceText.index("insert")
    print("cursorPosition", cursorPosition)
    print("lastCursorPosition", lastCursorPosition)
    lineStart = float(cursorPosition.split('.')[0])
    lineUpToPosition = sourceText.get(lineStart, cursorPosition)
    currentSequence = lineUpToPosition.rpartition(' ')[2]
    print("currentSequence", currentSequence)
    listbox.destroy()
    if currentSequence != " " and currentSequence != "":
        # TODO: Try to keep the connection open while the program is open.
        con = duckdb.connect("auto_complete.duckdb")
        con.load_extension("marisa.duckdb_extension")
        lst = con.sql("select marisa_predictive(trie, '" + currentSequence + "', 10) from keywords_trie;").fetchall()
        print(lst)
        autoCompleteItems = lst[0][0]
        if len(autoCompleteItems) != 0:
            listbox = tkinter.Listbox(main, height=len(autoCompleteItems), width=30)
            pos = lineStart * (fontSize+6)
            listbox.place(x=10, y=pos)
            count = 0
            autoCompleteItemsG = []
            for item in autoCompleteItems:
                count = count + 1
                listbox.insert(count, item)
                autoCompleteItemsG.append(item)
            global autoCompleteSelectionIndex
            if downPressed:
                autoCompleteSelectionIndex = autoCompleteSelectionIndex + 1
                itemCount = len(autoCompleteItemsG)
                if itemCount <= autoCompleteSelectionIndex:
                    autoCompleteSelectionIndex = itemCount - 1
                listbox.selection_set(autoCompleteSelectionIndex)
            if upPressed:
                autoCompleteSelectionIndex = autoCompleteSelectionIndex - 1
                if autoCompleteSelectionIndex == -1:
                    autoCompleteSelectionIndex = 0
                listbox.selection_set(autoCompleteSelectionIndex)
            if rightPressed:
                if autoCompleteSelectionIndex != -1:
                    selectionText = listbox.get(autoCompleteSelectionIndex)
                    print("selectionText",selectionText)
                    lineNumber = float(cursorPosition.split('.')[0])
                    lineColumn = float(cursorPosition.split('.')[1])
                    sequenceLength = float(len(currentSequence))
                    linePosition = lineColumn - sequenceLength
                    linePositionDecimal = 0.0
                    if linePosition <= 0.0:
                        linePositionDecimal = 0.0
                    else:
                        # Gets the length of linePosition
                        linePositionLength = math.ceil(math.log10(linePosition))
                        # put linePosition behind the '.' ie 17.0 => 0.17
                        linePositionDecimal = linePosition / math.pow(10,linePositionLength)
                    insertStart = lineNumber + linePositionDecimal
                    sourceText.delete(insertStart, cursorPosition)
                    sourceText.insert(insertStart, selectionText)
                    cursorPosition = sourceText.index("insert")
                    autoCompleteSelectionIndex = -1
                    autoCompleteItemsG = []
                    listbox.destroy()
    lastCursorPosition = cursorPosition


# TODO: Handle click on listbox item
# TODO: Figure out how to draw the auto-complete box when you are near the bottom of the source code.
# TODO: Add colors to trie
# TODO: Add /> and ="" to trie


def on_drop(event):
    """
    Support for drag-and-drop of files onto the UI.
    """
    global svgText
    global filepath
    dropPath = event.data
    print(dropPath)
    if dropPath[:1] == "{":
        dropPath = dropPath[1:-1]
        print(dropPath)
    if dropPath != '' and dropPath[-4:] == ".svg":
        filepath = dropPath
        svgText = ReadSvgFile(filepath)
        filename = Path(filepath).name
        main.title(f"SVG Editor - {filename}")
        DisplayImage(svgText)


def WriteSvgFile(filename, text):
    svgFile = open(filename, 'w')
    svgFile.write(text)
    svgFile.close()


def ReadSvgFile(filename):
    svgFile = open(filename, 'r')
    text = svgFile.read()
    svgFile.close()
    return text


def CreateDisplayImage(svgText, scale, dpi):
    svg = cairosvg.svg2svg(svgText, dpi=(dpi / scale))
    bytes = cairosvg.svg2png(svg)
    img = Image.open(BytesIO(bytes))
    return img


def setFilePathGlobal(path):
    global filepath
    filepath = path


def setSvgTextGlobal(text):
    global svgText
    svgText = text


def OpenCommand():
    global filepath
    global svgText
    filepath = openFile()
    svgText = ReadSvgFile(filepath)
    filename = Path(filepath).name
    main.title(f"SVG Editor - {filename}")
    DisplayImage(svgText)


def DisplayImage(svgText):
    sourceText.delete("1.0", tkinter.END)
    sourceText.insert(tkinter.END, svgText)
    img = CreateDisplayImage(svgText, 1, 96)
    tkimg = ImageTk.PhotoImage(img)
    imageLabel.config(image=tkimg)
    imageLabel.image = tkimg


def SaveCommand():
    global filepath
    global svgText
    svgText = sourceText.get("1.0", "end-1c")
    WriteSvgFile(filepath, svgText)
    svgText = ReadSvgFile(filepath)
    filename = Path(filepath).name
    main.title(f"SVG Editor - {filename}")
    DisplayImage(svgText)


def SaveAsCommand():
    global filepath
    global svgText
    svgText = sourceText.get("1.0", "end-1c")
    newFilepath = tkinter.filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".svg",
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
    )
    filepath = newFilepath
    WriteSvgFile(newFilepath, svgText)
    filename = Path(newFilepath).name
    main.title(f"SVG Editor - {filename}")


def NewCommand():
    global filepath
    global svgText
    svgText = '''<svg height="100" width="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
</svg>
        '''
    newFilepath = tkinter.filedialog.asksaveasfilename(
        title="New SVG",
        defaultextension=".svg",
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
    )
    filepath = newFilepath
    WriteSvgFile(newFilepath, svgText)
    filename = Path(newFilepath).name
    main.title(f"SVG Editor - {filename}")
    DisplayImage(svgText)


def openFile():
    global filepath
    filepath = tkinter.filedialog.askopenfilename(
        filetypes=[("SVG Files", "*.svg"), ("All Files", "*.*")]
    )
    return filepath


def SavePNGCommand():
    global svgText
    if svgText != "":
        newFilepath = tkinter.filedialog.asksaveasfilename(
            title="PNG",
            defaultextension=".png",
            filetypes=[("SVG files", "*.png"), ("All files", "*.*")]
        )
        img = CreateDisplayImage(svgText, 1, 96)
        img.save(newFilepath)


def SaveICOCommand():
    global svgText
    if svgText != "":
        newFilepath = tkinter.filedialog.asksaveasfilename(
            title="ICO",
            defaultextension=".ico",
            filetypes=[("SVG files", "*.ico"), ("All files", "*.*")]
        )
        img = CreateDisplayImage(svgText, 1, 96)
        img.save(newFilepath,
                 format='ICO',
                 sizes=[
                    (32, 32),
                    (48, 48),
                    (64, 64),
                    (128, 128),
                    (256, 256),
                    (512, 512)
                 ])


main = TkinterDnD.Tk()
# main = tkinter.Tk()
main.title("SVG Editor")
main.geometry("1000x400")
main.grid_columnconfigure(0, weight=1, uniform="equal")
main.grid_columnconfigure(1, weight=1, uniform="equal")
main.grid_rowconfigure(0, weight=1)

menubar = tkinter.Menu(main)
main.config(menu=menubar)
filemenu = tkinter.Menu(menubar, tearoff=False)
exportMenu = tkinter.Menu(filemenu, tearoff=False)

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=NewCommand)
filemenu.add_command(label="Open", command=OpenCommand)
filemenu.add_command(label="Save As", command=SaveAsCommand)

filemenu.add_cascade(label="Export", menu=exportMenu)

exportMenu.add_command(label="Export to PNG", command=SavePNGCommand)
exportMenu.add_command(label="Export to ICO", command=SaveICOCommand)
filemenu.add_command(label='Exit', command=main.destroy)
menubar.add_command(label="Save", command=SaveCommand)

sourceFrame = tkinter.Frame(master=main, bg="orange")
sourceFrame.grid(row=0, column=0, sticky='nsew')

vScrollbar = tkinter.Scrollbar(sourceFrame, orient="horizontal")
vScrollbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
hScrollbar = tkinter.Scrollbar(sourceFrame)
hScrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
sourceTextFont = font.Font(size=fontSize)
sourceText = tkinter.Text(
    sourceFrame,
    yscrollcommand=hScrollbar.set,
    xscrollcommand=vScrollbar.set,
    wrap="none",
    font=sourceTextFont)
hScrollbar.config(command=sourceText.yview)
vScrollbar.config(command=sourceText.xview)
sourceText.pack(fill=tkinter.BOTH, expand=True)
sourceText.insert(tkinter.END, svgText)

sourceText.bind("<KeyRelease>", UpdateCursorPosition)

imageFrame = tkinter.Frame(master=main, bg="pink")
imageFrame.grid(row=0, column=1, sticky='nsew')
imageLabel = tkinter.Label(imageFrame)  # , image=tkimg)
imageLabel.pack(fill=tkinter.BOTH, expand=True)

startingPath = sys.argv[1] if len(sys.argv) >= 2 else ''

if startingPath != '' and startingPath[-4:] == ".svg":
    setFilePathGlobal(startingPath)
    svgText = ReadSvgFile(startingPath)
    setSvgTextGlobal(svgText)
    filename = Path(startingPath).name
    main.title(f"SVG Editor - {filename}")
    DisplayImage(svgText)

main.drop_target_register(DND_FILES)
main.dnd_bind("<<Drop>>", on_drop)

# This only exists to be destroyed so that there is only one auto-complete
# listbox at a time.
listbox = tkinter.Listbox(main)

main.mainloop()
