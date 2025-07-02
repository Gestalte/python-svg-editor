import sys
import tkinter
import cairosvg
from PIL import Image, ImageTk
from io import BytesIO
from pathlib import Path
import tkinter.filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

filepath = ""
svgText = ""


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
sourceText = tkinter.Text(
    sourceFrame,
    yscrollcommand=hScrollbar.set,
    xscrollcommand=vScrollbar.set,
    wrap="none")
hScrollbar.config(command=sourceText.yview)
vScrollbar.config(command=sourceText.xview)
sourceText.pack(fill=tkinter.BOTH, expand=True)
sourceText.insert(tkinter.END, svgText)

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

main.mainloop()
