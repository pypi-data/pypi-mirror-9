#=============================================================================
# Class OWTextableTextFiles
# Copyright 2012-2015 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the Textable (v1.5) extension to Orange Canvas.
#
# Textable v1.5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Textable v1.5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Textable v1.5. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

__version__ = '0.17'

"""
<name>Text Files</name>
<description>Import data from raw text files</description>
<icon>icons/TextFiles.png</icon>
<priority>2</priority>
"""

import codecs, os.path, textwrap, re, json
from unicodedata        import normalize

from LTTL.Segmentation  import Segmentation
from LTTL.Segmenter     import Segmenter
from LTTL.Input         import Input

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget  import *
import OWGUI

class OWTextableTextFiles(OWWidget):

    """Orange widget for loading text files"""
    
    settingsList = [
            'files',
            'encoding',
            'autoSend',
            'label',
            'autoNumber',
            'autoNumberKey',
            'importFilenames',
            'importFilenamesKey',
            'lastLocation',
            'displayAdvancedSettings',
            'file',
            'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )

        # Input and output channels...
        self.inputs  = [
            ('Message', JSONMessage, self.inputMessage, Single)
        ]
        self.outputs = [('Text data', Segmentation)]
        
        # Settings...
        self.files                      = []
        self.encoding                   = 'iso-8859-1'
        self.autoSend                   = True
        self.label                      = u'file_content'
        self.autoNumber                 = False
        self.autoNumberKey              = u'num'
        self.importFilenames            = True
        self.importFilenamesKey         = u'filename'
        self.lastLocation               = '.'
        self.displayAdvancedSettings    = False
        self.file                       = u''
        self.uuid                       = None
        self.loadSettings()
        self.uuid                       = getWidgetUuid(self)

        # Other attributes...
        self.segmenter              = Segmenter()
        self.segmentation           = None
        self.createdInputs          = []
        self.fileLabels             = []
        self.selectedFileLabels     = []
        self.newFiles               = u''
        self.newAnnotationKey       = u''
        self.newAnnotationValue     = u''
        self.infoBox                = InfoBox(widget=self.controlArea)
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                sendIfPreCallback   = self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendButton.settingsChanged,
        )

        # GUI...

        # Advanced settings checkbox...
        self.advancedSettings.draw()

        # BASIC GUI...

        # Basic file box
        basicFileBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Source',
                orientation         = 'vertical',
        )
        basicFileBoxLine1 = OWGUI.widgetBox(
                widget              = basicFileBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.lineEdit(
                widget              = basicFileBoxLine1,
                master              = self,
                value               = 'file',
                orientation         = 'horizontal',
                label               = u'File path:',
                labelWidth          = 101,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The path of the file."
                ),
        )
        OWGUI.separator(
                widget              = basicFileBoxLine1,
                width               = 5,
        )
        basicBrowseButton = OWGUI.button(
                widget              = basicFileBoxLine1,
                master              = self,
                label               = u'Browse',
                callback            = self.browse,
                tooltip             = (
                        u"Open a dialog for selecting file."
                ),
        )
        OWGUI.separator(
                widget              = basicFileBox,
                height              = 3,
        )
        encodingCombo = OWGUI.comboBox(
                widget              = basicFileBox,
                master              = self,
                value               = 'encoding',
                items               = getPredefinedEncodings(),
                sendSelectedValue   = True,
                orientation         = 'horizontal',
                label               = u'Encoding:',
                labelWidth          = 101,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Select input file(s) encoding."
                ),
        )
        OWGUI.separator(
                widget              = basicFileBox,
                height              = 3,
        )
        self.advancedSettings.basicWidgets.append(basicFileBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # (Basic) options box...
        basicOptionsBox = BasicOptionsBox(self.controlArea, self)
        self.advancedSettings.basicWidgets.append(basicOptionsBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # ADVANCED GUI...

        # File box
        fileBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Sources',
                orientation         = 'vertical',
        )
        fileBoxLine1 = OWGUI.widgetBox(
                widget              = fileBox,
                box                 = False,
                orientation         = 'horizontal',
                addSpace            = True,
        )
        self.fileListbox = OWGUI.listBox(
                widget              = fileBoxLine1,
                master              = self,
                value               = 'selectedFileLabels',
                labels              = 'fileLabels',
                callback            = self.updateFileBoxButtons,
                tooltip             = (
                        u"The list of files whose content will be imported.\n"
                        u"\nIn the output segmentation, the content of each\n"
                        u"file appears in the same position as in the list.\n"
                        u"\nColumn 1 shows the file's name.\n"
                        u"Column 2 shows the file's annotation (if any).\n"
                        u"Column 3 shows the file's encoding."
                ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.fileListbox.setFont(font)
        fileBoxCol2 = OWGUI.widgetBox(
                widget              = fileBoxLine1,
                orientation         = 'vertical',
        )
        self.moveUpButton = OWGUI.button(
                widget              = fileBoxCol2,
                master              = self,
                label               = u'Move Up',
                callback            = self.moveUp,
                tooltip             = (
                        u"Move the selected file upward in the list."
                ),
        )
        self.moveDownButton = OWGUI.button(
                widget              = fileBoxCol2,
                master              = self,
                label               = u'Move Down',
                callback            = self.moveDown,
                tooltip             = (
                        u"Move the selected file downward in the list."
                ),
        )
        self.removeButton = OWGUI.button(
                widget              = fileBoxCol2,
                master              = self,
                label               = u'Remove',
                callback            = self.remove,
                tooltip             = (
                        u"Remove the selected file from the list."
                ),
        )
        self.clearAllButton = OWGUI.button(
                widget              = fileBoxCol2,
                master              = self,
                label               = u'Clear All',
                callback            = self.clearAll,
                tooltip             = (
                        u"Remove all files from the list."
                ),
        )
        self.importButton = OWGUI.button(
                widget              = fileBoxCol2,
                master              = self,
                label               = u'Import List',
                callback            = self.importList,
                tooltip             = (
                        u"Open a dialog for selecting a file list to\n"
                        u"import (in JSON format). Files from this list\n"
                        u"will be added to those already imported."
                ),
        )
        self.exportButton = OWGUI.button(
                widget              = fileBoxCol2,
                master              = self,
                label               = u'Export List',
                callback            = self.exportList,
                tooltip             = (
                        u"Open a dialog for selecting a file where the file\n"
                        u"list can be exported in JSON format."
                ),
        )
        fileBoxLine2 = OWGUI.widgetBox(
                widget              = fileBox,
                box                 = False,
                orientation         = 'vertical',
        )
        # Add file box
        addFileBox = OWGUI.widgetBox(
                widget              = fileBoxLine2,
                box                 = True,
                orientation         = 'vertical',
        )
        addFileBoxLine1 = OWGUI.widgetBox(
                widget              = addFileBox,
                orientation         = 'horizontal',
        )
        OWGUI.lineEdit(
                widget              = addFileBoxLine1,
                master              = self,
                value               = 'newFiles',
                orientation         = 'horizontal',
                label               = u'File path(s):',
                labelWidth          = 101,
                callback            = self.updateGUI,
                tooltip             = (
                        u"The paths of the files that will be added to the\n"
                        u"list when button 'Add' is clicked.\n\n"
                        u"Successive paths must be separated with ' / ' \n"
                        u"(whitespace + slash + whitespace). Their order in\n"
                        u"the list will be the same as in this field."
                ),
        )
        OWGUI.separator(
                widget              = addFileBoxLine1,
                width               = 5,
        )
        browseButton = OWGUI.button(
                widget              = addFileBoxLine1,
                master              = self,
                label               = u'Browse',
                callback            = self.browse,
                tooltip             = (
                        u"Open a dialog for selecting files.\n\n"
                        u"To select multiple files at once, either draw a\n"
                        u"selection box around them, or use shift and/or\n"
                        u"ctrl + click.\n\n"
                        u"Selected file paths will appear in the field to\n"
                        u"the left of this button afterwards, ready to be\n"
                        u"added to the list when button 'Add' is clicked."
                ),
        )
        OWGUI.separator(
                widget              = addFileBox,
                height              = 3,
        )
        encodingCombo = OWGUI.comboBox(
                widget              = addFileBox,
                master              = self,
                value               = 'encoding',
                items               = getPredefinedEncodings(),
                sendSelectedValue   = True,
                orientation         = 'horizontal',
                label               = u'Encoding:',
                labelWidth          = 101,
                callback            = self.updateGUI,
                tooltip             = (
                        u"Select input file(s) encoding."
                ),
        )
        OWGUI.separator(
                widget              = addFileBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = addFileBox,
                master              = self,
                value               = 'newAnnotationKey',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 101,
                callback            = self.updateGUI,
                tooltip             = (
                        u"This field lets you specify a custom annotation\n"
                        u"key associated with each file that is about to be\n"
                        u"added to the list."
                ),
        )
        OWGUI.separator(
                widget              = addFileBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = addFileBox,
                master              = self,
                value               = 'newAnnotationValue',
                orientation         = 'horizontal',
                label               = u'Annotation value:',
                labelWidth          = 101,
                callback            = self.updateGUI,
                tooltip             = (
                        u"This field lets you specify the annotation value\n"
                        u"associated with the above annotation key."
                ),
        )
        OWGUI.separator(
                widget              = addFileBox,
                height              = 3,
        )
        self.addButton = OWGUI.button(
                widget              = addFileBox,
                master              = self,
                label               = u'Add',
                callback            = self.add,
                tooltip             = (
                        u"Add the file(s) currently displayed in the\n"
                        u"'Files' text field to the list.\n\n"
                        u"Each of these files will be associated with the\n"
                        u"specified encoding and annotation (if any).\n\n"
                        u"Other files may be selected afterwards and\n"
                        u"assigned a different encoding and annotation."
                ),
        )
        self.advancedSettings.advancedWidgets.append(fileBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()
        
        # Options box...
        optionsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Options',
                orientation         = 'vertical',
        )
        OWGUI.lineEdit(
                widget              = optionsBox,
                master              = self,
                value               = 'label',
                orientation         = 'horizontal',
                label               = u'Output segmentation label:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Label of the output segmentation."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        optionsBoxLine2 = OWGUI.widgetBox(
                widget              = optionsBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = optionsBoxLine2,
                master              = self,
                value               = 'importFilenames',
                label               = u'Import filenames with key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Import filenames as annotations."
                ),
        )
        self.importFilenamesKeyLineEdit = OWGUI.lineEdit(
                widget              = optionsBoxLine2,
                master              = self,
                value               = 'importFilenamesKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for importing filenames."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        optionsBoxLine3 = OWGUI.widgetBox(
                widget              = optionsBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = optionsBoxLine3,
                master              = self,
                value               = 'autoNumber',
                label               = u'Auto-number with key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotate files with increasing numeric indices."
                ),
        )
        self.autoNumberKeyLineEdit = OWGUI.lineEdit(
                widget              = optionsBoxLine3,
                master              = self,
                value               = 'autoNumberKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for file auto-numbering."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.sendButton.sendIf()


    def inputMessage(self, message):
        """Handle JSON message on input connection"""
        if not message:
            return
        self.displayAdvancedSettings = True
        self.advancedSettings.setVisible(True)
        self.clearAll()
        self.infoBox.inputChanged()
        try:
            json_data = json.loads(message.content)
            temp_files = list()
            for entry in json_data:
                path                = entry.get('path', '')
                encoding            = entry.get('encoding', '')
                annotationKey       = entry.get('annotation_key', '')
                annotationValue     = entry.get('annotation_value', '')
                if path == '' or encoding == '':
                    m =   "JSON message on input connection doesn't " \
                        + "have the right keys and/or values."
                    m = '\n\t'.join(textwrap.wrap(m, 35))
                    self.infoBox.noDataSent(m)
                    self.send('Text data', None, self)
                    return
                temp_files.append((
                    path,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.files.extend(temp_files)
            self.sendButton.settingsChanged()
        except ValueError:
            m = "Message content is not in JSON format."
            m = '\n\t'.join(textwrap.wrap(m, 35))
            self.infoBox.noDataSent(m)
            self.send('Text data', None, self)
            return


    def sendData(self):
    
        """Load files, create and send segmentation"""
        
        # Check that there's something on input...
        if (
                (self.displayAdvancedSettings and not self.files)
             or not (self.file or self.displayAdvancedSettings)
        ):
            self.infoBox.noDataSent(u'No input.')
            self.send('Text data', None, self)
            return

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Text data', None, self)
            return

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey  = self.autoNumberKey
            else:
                self.infoBox.noDataSent(
                        u'No annotation key was provided for auto-numbering.'
                )
                self.send('Text data', None, self)
                return
        else:
            autoNumberKey = None

        # Clear created Inputs...
        self.clearCreatedInputs()

        fileContents    = []
        annotations     = []
        counter         = 1

        if self.displayAdvancedSettings:
            myFiles = self.files
        else:
            myFiles = [
                    [
                            self.file,
                            self.encoding,
                            u'',
                            u'',
                    ]
            ]

        # Open and process each file successively...
        for myFile in myFiles:
            filePath            = myFile[0]
            encoding            = myFile[1]
            annotation_key      = myFile[2]
            annotation_value    = myFile[3]

            # Try to open the file...
            self.error()
            try:
                fileHandle = codecs.open(filePath, encoding=encoding)
                try:
                    fileContent = fileHandle.read()
                except UnicodeError:
                    m = u'Encoding of %s does not look like %s.' % (
                        filePath,
                        encoding,
                    )
                    m = '\n\t'.join(textwrap.wrap(m, 35))
                    self.infoBox.noDataSent(m)
                    self.send('Text data', None, self)
                    return
                finally:
                    fileHandle.close()
            except IOError:
                m = '\n\t'.join(textwrap.wrap(
                        u"Cannot open %s." % filePath,
                        35
                ))
                self.infoBox.noDataSent(m)
                self.send('Text data', None, self)
                return

            # Replace newlines with '\n'...
            fileContent = fileContent.replace('\r\n', '\n').replace('\r','\n')

            # Remove utf-8 BOM if necessary...
            if encoding == u'utf-8':
                fileContent = fileContent.lstrip(
                        unicode(codecs.BOM_UTF8, 'utf-8')
                )

            # Normalize text (canonical decomposition then composition)...
            fileContent = normalize('NFC', fileContent)
            
            fileContents.append(fileContent)

            # Annotations...
            annotation = {}
            if self.displayAdvancedSettings:
                if annotation_key and annotation_value:
                    annotation[annotation_key] = annotation_value
                if self.importFilenames and self.importFilenamesKey:
                    filename = os.path.basename(filePath)
                    annotation[self.importFilenamesKey] = filename
                if self.autoNumber and self.autoNumberKey:
                    annotation[self.autoNumberKey] = counter
                    counter += 1
            annotations.append(annotation)
            
        # Create an LTTL.Input for each file...
        if len(fileContents) == 1:
            label = self.label
        else:
            label = None
        for index in xrange(len(fileContents)):
            myInput = Input(fileContents[index], label)
            myInput.segments[0].annotations.update(annotations[index])
            self.createdInputs.append(myInput)

        # If there's only one file, the widget's output is the created Input.
        if len(fileContents) == 1:
            self.segmentation = self.createdInputs[0]
        # Otherwise the widget's output is a concatenation...
        else:
            self.segmentation = Segmenter().concatenate(
                    segmentations       = self.createdInputs,
                    label               = self.label,
                    copy_annotations    = True,
                    import_labels_as    = None,
                    auto_numbering_as   = None,
                    sort                = False,
                    merge_duplicates    = False,
                    progress_callback   = None,
            )

        message = u'Data contains %i segment@p ' % len(self.segmentation)
        message = pluralize(message, len(self.segmentation))
        numChars = 0
        for segment in self.segmentation:
            segmentLength = len(Segmentation.data[segment.address.str_index])
            numChars += segmentLength
        message += u'and %i character@p.' % numChars
        message = pluralize(message, numChars)
        self.infoBox.dataSent(message)

        self.send( 'Text data', self.segmentation, self )
        self.sendButton.resetSettingsChangedFlag()


    def clearCreatedInputs(self):
        for i in self.createdInputs:
            i.clear()
        del self.createdInputs[:]
        for i in reversed(xrange(len(Segmentation.data))):
            if Segmentation.data[i] is None:
                Segmentation.data.pop(i)
            else:
                break


    def importList(self):
        """Display a FileDialog and import file list"""
        filePath = unicode(
                QFileDialog.getOpenFileName(
                        self,
                        u'Import File List',
                        self.lastLocation,
                        u'Text files (*.*)'
                )
        )
        if not filePath:
            return
        self.file = os.path.normpath(filePath)
        self.lastLocation = os.path.dirname(filePath)
        self.error()
        try:
            fileHandle = codecs.open(filePath, encoding='utf8')
            fileContent = fileHandle.read()
            fileHandle.close()
        except IOError:
            QMessageBox.warning(
                    None,
                    'Textable',
                    "Couldn't open file.",
                    QMessageBox.Ok
            )
            return
        try:
            json_data = json.loads(fileContent)
            temp_files = list()
            for entry in json_data:
                path                = entry.get('path', '')
                encoding            = entry.get('encoding', '')
                annotationKey       = entry.get('annotation_key', '')
                annotationValue     = entry.get('annotation_value', '')
                if path == '' or encoding == '':
                    QMessageBox.warning(
                            None,
                            'Textable',
                            "Selected JSON file doesn't have the right keys "
                            "and/or values.",
                            QMessageBox.Ok
                    )
                    return
                temp_files.append((
                    path,
                    encoding,
                    annotationKey,
                    annotationValue,
                ))
            self.files.extend(temp_files)
            if temp_files:
                self.sendButton.settingsChanged()
        except ValueError:
            QMessageBox.warning(
                    None,
                    'Textable',
                    "Selected file is not in JSON format.",
                    QMessageBox.Ok
            )
            return


    def exportList(self):
        """Display a FileDialog and export file list"""
        toDump = list()
        for myfile in self.files:
            toDump.append({
                    'path':     myfile[0],
                    'encoding': myfile[1],
            })
            if myfile[2] and myfile[3]:
                toDump[-1]['annotation_key']    = myfile[2]
                toDump[-1]['annotation_value']  = myfile[3]
        filePath = unicode(
                QFileDialog.getSaveFileName(
                        self,
                        u'Export File List',
                        self.lastLocation,
                )
        )
        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            outputFile = codecs.open(
                    filePath,
                    encoding    = 'utf8',
                    mode        = 'w',
                    errors      = 'xmlcharrefreplace',
            )
            outputFile.write(
                    normalizeCarriageReturns(
                            json.dumps(toDump, sort_keys=True, indent=4)
                    )
            )
            outputFile.close()
            QMessageBox.information(
                    None,
                    'Textable',
                    'File list correctly exported',
                    QMessageBox.Ok
            )


    def browse(self):
        """Display a FileDialog and select files"""
        if self.displayAdvancedSettings:
            filePathList = QFileDialog.getOpenFileNames(
                    self,
                    u'Select Text File(s)',
                    self.lastLocation,
                    u'Text files (*.*)'
            )
            if not filePathList:
                return
            filePathList = [os.path.normpath(unicode(f)) for f in filePathList]
            self.newFiles = u' / '.join(filePathList)
            self.lastLocation = os.path.dirname(filePathList[-1])
            self.updateGUI()
        else:
            filePath = unicode(
                    QFileDialog.getOpenFileName(
                            self,
                            u'Open Text File',
                            self.lastLocation,
                            u'Text files (*.*)'
                    )
            )
            if not filePath:
                return
            self.file = os.path.normpath(filePath)
            self.lastLocation = os.path.dirname(filePath)
            self.updateGUI()
            self.sendButton.settingsChanged()


    def moveUp(self):
        """Move file upward in Files listbox"""
        if self.selectedFileLabels:
            index = self.selectedFileLabels[0]
            if index > 0:
                temp                = self.files[index-1]
                self.files[index-1] = self.files[index]
                self.files[index]   = temp
                self.selectedFileLabels.listBox.item(index-1).setSelected(1)
                self.sendButton.settingsChanged()


    def moveDown(self):
        """Move file downward in Files listbox"""
        if self.selectedFileLabels:
            index = self.selectedFileLabels[0]
            if index < len(self.files)-1:
                temp                = self.files[index+1]
                self.files[index+1] = self.files[index]
                self.files[index]   = temp
                self.selectedFileLabels.listBox.item(index+1).setSelected(1)
                self.sendButton.settingsChanged()


    def clearAll(self):
        """Remove all files from files attr"""
        del self.files[:]
        del self.selectedFileLabels[:]
        self.sendButton.settingsChanged()
        

    def remove(self):
        """Remove file from files attr"""
        if self.selectedFileLabels:
            index = self.selectedFileLabels[0]
            self.files.pop(index)
            del self.selectedFileLabels[:]
            self.sendButton.settingsChanged()


    def add(self):
        """Add files to files attr"""
        filePathList = re.split(r' +/ +', self.newFiles)
        for filePath in filePathList:
            self.files.append((
                filePath,
                self.encoding,
                self.newAnnotationKey,
                self.newAnnotationValue,
            ))
        self.sendButton.settingsChanged()


    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedFileLabels:
                cachedLabel = self.selectedFileLabels[0]
            else:
                cachedLabel = None
            del self.fileLabels[:]
            if self.files:
                filePaths       = [f[0] for f in self.files]
                filenames       = [os.path.basename(p) for p in filePaths]
                encodings       = [f[1] for f in self.files]
                annotations     = [
                        '{%s: %s}' % (f[2], f[3]) for f in self.files
                ]
                maxFilenameLen  = max([len(n) for n in filenames])
                maxAnnoLen      = max([len(a) for a in annotations])
                for index in xrange(len(self.files)):
                    format      = u'%-' + unicode(maxFilenameLen + 2) + u's'
                    fileLabel   = format % filenames[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format    = u'%-' + unicode(maxAnnoLen + 2) + u's'
                            fileLabel += format % annotations[index]
                        else:
                            fileLabel += u' ' * (maxAnnoLen + 2)
                    fileLabel += encodings[index]
                    self.fileLabels.append(fileLabel)
            self.fileLabels = self.fileLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedFileLabels.listBox.item(
                        cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newFiles:
                if (
                   (    self.newAnnotationKey and     self.newAnnotationValue)
                or (not self.newAnnotationKey and not self.newAnnotationValue)
                ):
                    self.addButton.setDisabled(False)
                else:
                    self.addButton.setDisabled(True)
            else:
                self.addButton.setDisabled(True)
            if self.autoNumber:
                self.autoNumberKeyLineEdit.setDisabled(False)
            else:
                self.autoNumberKeyLineEdit.setDisabled(True)
            if self.importFilenames:
                self.importFilenamesKeyLineEdit.setDisabled(False)
            else:
                self.importFilenamesKeyLineEdit.setDisabled(True)
            self.updateFileBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)


    def updateFileBoxButtons(self):
        """Update state of File box buttons"""
        if self.selectedFileLabels:
            self.removeButton.setDisabled(False)
            if self.selectedFileLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedFileLabels[0] < len(self.files) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if len(self.files):
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)


    def onDeleteWidget(self):
        self.clearCreatedInputs()


    def getSettings(self, *args, **kwargs):
        settings = OWWidget.getSettings(self, *args, **kwargs)
        settings["settingsDataVersion"] = __version__.split('.')
        return settings

    def setSettings(self, settings):
        if settings.get("settingsDataVersion", None) == __version__.split('.'):
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


if __name__ == '__main__':
    appl = QApplication(sys.argv)
    ow   = OWTextableTextFiles()
    ow.show()
    appl.exec_()
    ow.saveSettings()
