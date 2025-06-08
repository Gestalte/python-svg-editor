import tkinter
import cairosvg
from PIL import Image, ImageTk
from io import BytesIO
from pathlib import Path
import tkinter.filedialog

filepath = ""
svgText = ""


def WriteSvgFile(filename, text):
    svgFile = open(filename, 'w')
    svgFile.write(text)
    svgFile.close()


def ReadSvgFile(filename):
    global svgFile
    svgFile = open(filename, 'r')
    text = svgFile.read()
    svgFile.close()
    return text


def CreateDisplayImage(svgText, scale, dpi):
    svg = cairosvg.svg2svg(svgText, dpi=(dpi / scale))
    bytes = cairosvg.svg2png(svg)
    img = Image.open(BytesIO(bytes))
    return img


def OpenCommand():
    global filepath
    global svgText
    filepath = openFile()
    svgText = ReadSvgFile(filepath)
    filename = Path(filepath).name
    main.title(f"SVG Editor - {filename}")
    DisplayImage()


def DisplayImage():
    global svgText
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
    DisplayImage()


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
    DisplayImage()


def openFile():
    global filepath
    filepath = tkinter.filedialog.askopenfilename(
        filetypes=[("SVG Files", "*.svg"), ("All Files", "*.*")]
    )
    return filepath


def savePNG():
    global svgText
    newFilepath = tkinter.filedialog.asksaveasfilename(
        title="PNG",
        defaultextension=".png",
        filetypes=[("SVG files", "*.png"), ("All files", "*.*")]
    )
    img = CreateDisplayImage(svgText, 1, 96)
    img.save(newFilepath)


main = tkinter.Tk()
main.title("SVG Editor")
main.geometry("1000x400")
main.grid_columnconfigure(0, weight=1, uniform="equal")
main.grid_columnconfigure(1, weight=1, uniform="equal")
main.grid_rowconfigure(0, weight=1)

menubar = tkinter.Menu(main)
main.config(menu=menubar)
filemenu = tkinter.Menu(menubar, tearoff=False)

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=NewCommand)
filemenu.add_command(label="Open", command=OpenCommand)
filemenu.add_command(label="Save As", command=SaveAsCommand)
filemenu.add_command(label='Exit', command=main.destroy)
menubar.add_command(label="Save", command=SaveCommand)
menubar.add_command(label="Create PNG", command=savePNG)

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

main.mainloop()
