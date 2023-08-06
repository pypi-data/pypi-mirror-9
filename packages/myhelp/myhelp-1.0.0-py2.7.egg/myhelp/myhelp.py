from xml.dom.minidom import parse, parseString
import xml.dom.minidom,commands,xml.etree.ElementTree as ET
from optparse import OptionParser
from os import environ

def run():
    parser = OptionParser()

    parser.add_option("-e","--edit",action="store",type="string",dest="editfile",help="edits/adds a notes")
    parser.add_option("-o","--open",action="store",type="string",dest="openfile",help="opens a notes")
    parser.add_option("-r","--remove",action="store",type="string",dest="remove",help="removes a notes")

    options,args = parser.parse_args()

    tree = ET.parse(environ["HOME"]+"/.mypy/myhelp/tags.xml")

    root = tree.getroot()
    roottags=root.find('tags')
    tags = root.iter('tag')

    if options.editfile:
        commands.getoutput("cat "+options.editfile+" >> "+environ["HOME"]+"/.mypy/myhelp/notes/"+options.editfile+";rm -rf "+options.editfile)
        definedtags=raw_input("Define Tags (separated by spaces): ").split(" ")
        definedtags.append(options.editfile)
        for tag in tags:
            value=tag.attrib['value']
            if value in definedtags:
                fileelement=ET.Element('file')
                fileelement.text=options.editfile
                tag.append(fileelement)
                definedtags.pop(definedtags.index(value))
                if definedtags != []:
                    for tag in definedtags:
                        newtag=ET.Element('tag')
                        newtag.set("value",tag)
                        newfileelement =ET.SubElement(newtag,'file')
                        newfileelement.text=options.editfile
                        roottags.append(newtag)
                        tree.write(environ["HOME"]+"/.mypy/myhelp/tags.xml")
                        quit()

    if options.remove:
        pass

    if options.openfile:
        commands.getoutput("vim "+environ["HOME"]+"/.mypy/myhelp/notes/"+options.openfile)

    for tag in tags:
        if tag.attrib["value"] == args[0]:
            fileelements=tag.iter("file")
            print "-------------------------------------"
            for fileelement in fileelements:
                f=open(environ["HOME"]+"/.mypy/myhelp/notes/"+fileelement.text,"r")
                print f.read()
                f.close()
                print "-------------------------------------"
