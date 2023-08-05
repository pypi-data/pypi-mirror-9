#=============================================================================
# Class OWTextableSegment
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

__version__ = '0.21'

"""
<name>Segment</name>
<description>Subdivide a segmentation using regular expressions</description>
<icon>icons/Segment.png</icon>
<priority>4002</priority>
"""

import re, codecs, textwrap, json

from LTTL.Segmenter    import Segmenter
from LTTL.Segmentation import Segmentation

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableSegment(OWWidget):

    """Orange widget for regex-based tokenization"""
    
    settingsList = [
            'regexes',
            'importAnnotations',
            'mergeDuplicates',
            'autoSend',
            'label',
            'autoNumber',
            'autoNumberKey',
            'displayAdvancedSettings',
            'regex',
            'lastLocation',
            'mode',
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
            ('Segmentation', Segmentation, self.inputData, Single),
            ('Message', JSONMessage, self.inputMessage, Single)
        ]
        self.outputs = [('Segmented data', Segmentation)]
        
        # Settings...
        self.regexes                    = []
        self.importAnnotations          = True
        self.mergeDuplicates            = True
        self.autoSend                   = True
        self.label                      = u'segmented_data'
        self.autoNumber                 = False
        self.autoNumberKey              = u'num'
        self.displayAdvancedSettings    = False
        self.lastLocation               = '.'
        self.regex                      = u''
        self.mode                       = u'Tokenize'
        self.uuid                       = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.segmenter              = Segmenter()
        self.inputSegmentation      = None
        self.regexLabels            = []
        self.selectedRegexLabels    = []
        self.newRegex               = r''
        self.newAnnotationKey       = r''
        self.newAnnotationValue     = r''
        self.ignoreCase             = False
        self.unicodeDependent       = True
        self.multiline              = False
        self.dotAll                 = False
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

        self.advancedSettings.draw()

        # Regexes box
        regexBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Regexes',
                orientation         = 'vertical',
        )
        regexBoxLine1 = OWGUI.widgetBox(
                widget              = regexBox,
                box                 = False,
                orientation         = 'horizontal',
                addSpace            = True,
        )
        self.regexListbox = OWGUI.listBox(
                widget              = regexBoxLine1,
                master              = self,
                value               = 'selectedRegexLabels',
                labels              = 'regexLabels',
                callback            = self.updateRegexBoxButtons,
                tooltip             = (
                        u"The list of regexes that will be applied to each\n"
                        u"segment of the input segmentation.\n\n"
                        u"Regexes will be applied in the same order as they\n"
                        u"appear in the list.\n\n"
                        u"Column 1 shows the segmentation mode.\n"
                        u"Column 2 shows the regex pattern.\n"
                        u"Column 3 shows the associated annotation (if any).\n"
                        u"Column 4 shows the associated flags."
                ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.regexListbox.setFont(font)
        regexBoxCol2 = OWGUI.widgetBox(
                widget              = regexBoxLine1,
                orientation         = 'vertical',
        )
        self.moveUpButton = OWGUI.button(
                widget              = regexBoxCol2,
                master              = self,
                label               = u'Move Up',
                callback            = self.moveUp,
                tooltip             = (
                        u"Move the selected regex upward in the list."
                ),
        )
        self.moveDownButton = OWGUI.button(
                widget              = regexBoxCol2,
                master              = self,
                label               = u'Move Down',
                callback            = self.moveDown,
                tooltip             = (
                        u"Move the selected regex downward in the list."
                ),
        )
        self.removeButton = OWGUI.button(
                widget              = regexBoxCol2,
                master              = self,
                label               = u'Remove',
                callback            = self.remove,
                tooltip             = (
                        u"Remove the selected regex from the list."
                ),
        )
        self.clearAllButton = OWGUI.button(
                widget              = regexBoxCol2,
                master              = self,
                label               = u'Clear All',
                callback            = self.clearAll,
                tooltip             = (
                        u"Remove all regexes from the list."
                ),
        )
        self.importButton = OWGUI.button(
                widget              = regexBoxCol2,
                master              = self,
                label               = u'Import List',
                callback            = self.importList,
                tooltip             = (
                        u"Open a dialog for selecting a regex list to\n"
                        u"import (in JSON format). Regexes from this list\n"
                        u"will be added to the existing ones."
                ),
        )
        self.exportButton = OWGUI.button(
                widget              = regexBoxCol2,
                master              = self,
                label               = u'Export List',
                callback            = self.exportList,
                tooltip             = (
                        u"Open a dialog for selecting a file where the\n"
                        u"regex list can be exported in JSON format."
                ),
        )
        regexBoxLine2 = OWGUI.widgetBox(
                widget              = regexBox,
                box                 = False,
                orientation         = 'vertical',
        )
        # Add regex box
        addRegexBox = OWGUI.widgetBox(
                widget              = regexBoxLine2,
                box                 = True,
                orientation         = 'vertical',
        )
        self.modeCombo = OWGUI.comboBox(
                widget              = addRegexBox,
                master              = self,
                value               = 'mode',
                sendSelectedValue   = True,
                items               = [u'Tokenize', u'Split'],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 131,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Segmentation mode.\n\n"
                        u"'Tokenize': the regex specifies the form of\n"
                        u"segments themselves.\n\n"
                        u"'Split': the regex specifies the form of\n"
                        u"character sequences occuring between the segments."
                ),
        )
        self.modeCombo.setMinimumWidth(120)
        OWGUI.separator(
                widget              = addRegexBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = addRegexBox,
                master              = self,
                value               = 'newRegex',
                orientation         = 'horizontal',
                label               = u'Regex:',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"The regex pattern that will be added to the list\n"
                        u"when button 'Add' is clicked. Commonly used\n"
                        u"segmentation units include:\n"
                        u"1) .\tcharacters (except newline)\n"
                        u'2) \w\t"letters" (alphanumeric chars and underscores)\n'
                        u'3) \w+\t"words" (sequences of "letters")\n'
                        u"4) .+\tlines\n"
                        u"and so on."
                ),
        )
        OWGUI.separator(
                widget              = addRegexBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = addRegexBox,
                master              = self,
                value               = 'newAnnotationKey',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"This field lets you specify a custom annotation\n"
                        u"key for segments identified by the regex pattern\n"
                        u"about to be added to the list.\n\n"
                        u"Groups of characters captured by parentheses in\n"
                        u"the regex pattern may be inserted in the\n"
                        u"annotation value by using the form '&' (ampersand)\n"
                        u"immediately followed by a digit indicating the\n"
                        u"captured group number (e.g. '&1', '&2', etc.)."
                ),
        )
        OWGUI.separator(
                widget              = addRegexBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = addRegexBox,
                master              = self,
                value               = 'newAnnotationValue',
                orientation         = 'horizontal',
                label               = u'Annotation value:',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"This field lets you specify a custom annotation\n"
                        u"value for segments identified by the regex pattern\n"
                        u"about to be added to the list.\n\n"
                        u"Groups of characters captured by parentheses in\n"
                        u"the regex pattern may be inserted in the\n"
                        u"annotation value by using the form '&' (ampersand)\n"
                        u"immediately followed by a digit indicating the\n"
                        u"captured group number (e.g. '&1', '&2', etc.)."
                ),
        )
        OWGUI.separator(
                widget              = addRegexBox,
                height              = 3,
        )
        addRegexBoxLine1 = OWGUI.widgetBox(
                widget              = addRegexBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = addRegexBoxLine1,
                master              = self,
                value               = 'ignoreCase',
                label               = u'Ignore case (i)',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"Regex pattern is case-insensitive."
                ),
        )
        OWGUI.checkBox(
                widget              = addRegexBoxLine1,
                master              = self,
                value               = 'unicodeDependent',
                label               = u'Unicode dependent (u)',
                callback            = self.updateGUI,
                tooltip             = (
                        u"Built-in character classes are Unicode-aware."
                ),
        )
        addRegexBoxLine2 = OWGUI.widgetBox(
                widget              = addRegexBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = addRegexBoxLine2,
                master              = self,
                value               = 'multiline',
                label               = u'Multiline (m)',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"Anchors '^' and '$' match the beginning and\n"
                        u"end of each line (rather than just the beginning\n"
                        u"and end of each input segment)."
                ),
        )
        OWGUI.checkBox(
                widget              = addRegexBoxLine2,
                master              = self,
                value               = 'dotAll',
                label               = u'Dot matches all (s)',
                callback            = self.updateGUI,
                tooltip             = (
                        u"Meta-character '.' matches any character (rather\n"
                        u"than any character but newline)."
                ),
        )
        OWGUI.separator(
                widget              = addRegexBox,
                height              = 3,
        )
        self.addButton = OWGUI.button(
                widget              = addRegexBox,
                master              = self,
                label               = u'Add',
                callback            = self.add,
                tooltip             = (
                        u"Add the regex pattern currently displayed in the\n"
                        u"'Regex' text field to the list."
                ),
        )
        self.advancedSettings.advancedWidgets.append(regexBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Advanced) options box...
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
                value               = 'autoNumber',
                label               = u'Auto-number with key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotate output segments with increasing numeric\n"
                        u"indices."
                ),
        )
        self.autoNumberKeyLineEdit = OWGUI.lineEdit(
                widget              = optionsBoxLine2,
                master              = self,
                value               = 'autoNumberKey',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Annotation key for output segment auto-numbering."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = optionsBox,
                master              = self,
                value               = 'importAnnotations',
                label               = u'Import annotations',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Add to each output segment the annotation keys\n"
                        u"and values associated with the corresponding\n"
                        u"input segment."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = optionsBox,
                master              = self,
                value               = 'mergeDuplicates',
                label               = u'Fuse duplicates',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Fuse segments that have the same address.\n\n"
                        u"The annotation of merged segments will be fused\n"
                        u"as well. In the case where fused segments have\n"
                        u"distinct values for the same annotation key, only\n"
                        u"the value of the last one (in order of regex\n"
                        u"application) will be kept."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 2,
        )
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Basic) Regex box...
        basicRegexBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Regex',
                orientation         = 'vertical',
        )
        OWGUI.lineEdit(
                widget              = basicRegexBox,
                master              = self,
                value               = 'regex',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The regex that will be applied to each segment in\n"
                        u"the input segmentation. Commonly used segmentation\n"
                        u"units include:\n"
                        u"1) .\tcharacters (except newline)\n"
                        u'2) \w\t"letters" (alphanumeric chars and underscores)\n'
                        u'3) \w+\t"words" (sequences of "letters")\n'
                        u"4) .+\tlines\n"
                        u"and so on."
                ),
        )
        OWGUI.separator(
                widget              = basicRegexBox,
                height              = 3,
        )
        self.advancedSettings.basicWidgets.append(basicRegexBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        # (Basic) options box...
        basicOptionsBox = BasicOptionsBox(self.controlArea, self)
        self.advancedSettings.basicWidgets.append(basicOptionsBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

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
        self.regexes = list()
        self.infoBox.inputChanged()
        try:
            json_data = json.loads(message.content)
            temp_regexes = list()
            for entry in json_data:
                regex               = entry.get('regex', '')
                annotationKey       = entry.get('annotation_key', '')
                annotationValue     = entry.get('annotation_value', '')
                ignoreCase          = entry.get('ignore_case', False)
                unicodeDependent    = entry.get('unicode_dependent', False)
                multiline           = entry.get('multiline', False)
                dotAll              = entry.get('dot_all', False)
                mode                = entry.get('mode', '')
                if regex == '' or mode == '':
                    m =   "JSON message on input connection doesn't " \
                        + "have the right keys and/or values."
                    m = '\n\t'.join(textwrap.wrap(m, 35))
                    self.infoBox.noDataSent(m)
                    self.send('Segmentation', None, self)
                    return
                temp_regexes.append((
                    regex,
                    annotationKey,
                    annotationValue,
                    ignoreCase,
                    unicodeDependent,
                    multiline,
                    dotAll,
                    mode,
                ))
            self.regexes.extend(temp_regexes)
            self.sendButton.settingsChanged()
        except ValueError:
            m = "Message content is not in JSON format."
            m = '\n\t'.join(textwrap.wrap(m, 35))
            self.infoBox.noDataSent(m)
            self.send('Text data', None, self)
            return


    def sendData(self):
    
        """(Have LTTL.Segmenter) perform the actual tokenization"""

        # Check that there's something on input...
        if not self.inputSegmentation:
            self.infoBox.noDataSent(u'No input segmentation.')
            self.send('Segmented data', None, self)
            return

        # Check that there's at least one regex...
        if (
            (self.displayAdvancedSettings and not self.regexes)
            or not (self.regex or self.displayAdvancedSettings)
        ):
            self.infoBox.noDataSent(u'No regex defined.')
            self.send('Segmented data', None, self)
            return

        # Get regexes from basic or advanced settings...
        if self.displayAdvancedSettings:
            myRegexes = self.regexes
        else:
            myRegexes = [
                    [
                            self.regex,
                            None,
                            None,
                            False,
                            True,
                            False,
                            False,
                            u'Tokenize',
                    ]
            ]

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Segmented data', None, self)
            return

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey  = self.autoNumberKey
                num_iterations = (
                        len(self.inputSegmentation)
                      * (len(myRegexes) + 1)
                )
            else:
                self.infoBox.noDataSent(
                        u'No annotation key was provided for auto-numbering.'
                )
                self.send('Segmented data', None, self)
                return
        else:
            autoNumberKey = None
            num_iterations = len(self.inputSegmentation) * len(myRegexes)

        # Basic settings...
        if self.displayAdvancedSettings:
            importAnnotations   = self.importAnnotations
            mergeDuplicates     = self.mergeDuplicates
        else:
            importAnnotations   = True
            mergeDuplicates     = False

        # Prepare regexes...
        regexes = []
        for regex in myRegexes:
            regex_string = regex[0]
            if regex[3] or regex[4] or regex[5] or regex[6]:
                flags = ''
                if regex[3]:
                    flags += 'i'
                if regex[4]:
                    flags += 'u'
                if regex[5]:
                    flags += 'm'
                if regex[6]:
                    flags += 's'
                regex_string += '(?%s)' % flags
            if regex[1] and regex[2]:
                regexes.append((
                        re.compile(regex_string),
                        regex[7],
                        {regex[1]: regex[2]}
                ))
            else:
                regexes.append((re.compile(regex_string),regex[7],))

        # Perform tokenization...
        progressBar = OWGUI.ProgressBar(
                self,
                iterations = num_iterations
        )
        segmented_data = self.segmenter.tokenize(
            segmentation        = self.inputSegmentation,
            regexes             = regexes,
            label               = self.label,
            import_annotations  = importAnnotations,
            merge_duplicates    = mergeDuplicates,
            auto_numbering_as   = autoNumberKey,
            progress_callback   = progressBar.advance,
        )
        progressBar.finish()
        message = u'Data contains %i segment@p.' % len(segmented_data)
        message = pluralize(message, len(segmented_data))
        self.infoBox.dataSent(message)

        self.send( 'Segmented data', segmented_data, self)
        self.sendButton.resetSettingsChangedFlag()


    def inputData(self, segmentation):
        """Process incoming segmentation"""
        self.inputSegmentation = segmentation
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def importList(self):
        """Display a FileDialog and import regex list"""
        filePath = unicode(
                QFileDialog.getOpenFileName(
                        self,
                        u'Import Regex List',
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
            temp_regexes = list()
            for entry in json_data:
                regex               = entry.get('regex', '')
                annotationKey       = entry.get('annotation_key', '')
                annotationValue     = entry.get('annotation_value', '')
                ignoreCase          = entry.get('ignore_case', False)
                unicodeDependent    = entry.get('unicode_dependent', False)
                multiline           = entry.get('multiline', False)
                dotAll              = entry.get('dot_all', False)
                mode                = entry.get('mode', '')
                if regex == '' or mode == '':
                    QMessageBox.warning(
                            None,
                            'Textable',
                            "Selected JSON file doesn't have the right keys "
                            "and/or values.",
                            QMessageBox.Ok
                    )
                    return
                temp_regexes.append((
                    regex,
                    annotationKey,
                    annotationValue,
                    ignoreCase,
                    unicodeDependent,
                    multiline,
                    dotAll,
                    mode,
                ))
            self.regexes.extend(temp_regexes)
            if temp_regexes:
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
        """Display a FileDialog and export regex list"""
        toDump = list()
        for regex in self.regexes:
            toDump.append({
                    'regex': regex[0],
                    'mode':  regex[7],
            })
            if regex[1] and regex[2]:
                toDump[-1]['annotation_key']    = regex[1]
                toDump[-1]['annotation_value']  = regex[2]
            if regex[3]:
                toDump[-1]['ignore_case']       = regex[3]
            if regex[4]:
                toDump[-1]['unicode_dependent'] = regex[4]
            if regex[5]:
                toDump[-1]['multiline']         = regex[5]
            if regex[6]:
                toDump[-1]['dot_all']           = regex[6]
        filePath = unicode(
                QFileDialog.getSaveFileName(
                        self,
                        u'Export Regex List',
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
                    'Regex list correctly exported',
                    QMessageBox.Ok
            )


    def moveUp(self):
        """Move regex upward in Regexes listbox"""
        if self.selectedRegexLabels:
            index = self.selectedRegexLabels[0]
            if index > 0:
                temp                    = self.regexes[index-1]
                self.regexes[index-1]   = self.regexes[index]
                self.regexes[index]     = temp
                self.selectedRegexLabels.listBox.item(index-1).setSelected(1)
                self.sendButton.settingsChanged()


    def moveDown(self):
        """Move regex downward in Regexes listbox"""
        if self.selectedRegexLabels:
            index = self.selectedRegexLabels[0]
            if index < len(self.regexes)-1:
                temp                    = self.regexes[index+1]
                self.regexes[index+1]   = self.regexes[index]
                self.regexes[index]     = temp
                self.selectedRegexLabels.listBox.item(index+1).setSelected(1)
                self.sendButton.settingsChanged()


    def clearAll(self):
        """Remove all regexes from Regexes"""
        del self.regexes[:]
        del self.selectedRegexLabels[:]
        self.sendButton.settingsChanged()
        

    def remove(self):
        """Remove regex from regexes attr"""
        if self.selectedRegexLabels:
            index = self.selectedRegexLabels[0]
            self.regexes.pop(index)
            del self.selectedRegexLabels[:]
            self.sendButton.settingsChanged()


    def add(self):
        """Add regex to regexes attr"""
        self.regexes.append((
            self.newRegex,
            self.newAnnotationKey,
            self.newAnnotationValue,
            self.ignoreCase,
            self.unicodeDependent,
            self.multiline,
            self.dotAll,
            self.mode,
        ))
        self.sendButton.settingsChanged()


    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedRegexLabels:
                cachedLabel = self.selectedRegexLabels[0]
            else:
                cachedLabel = None
            del self.regexLabels[:]
            if len(self.regexes):
                regexes       = [r[0] for r in self.regexes]
                annotations   = [
                        '{%s: %s}' % (r[1], r[2]) for r in self.regexes
                ]
                maxRegexLen   = max([len(r) for r in regexes])
                maxAnnoLen    = max([len(a) for a in annotations])
                for index in range(len(self.regexes)):
                    regexLabel = u'(%s)  ' % self.regexes[index][7][0].lower()
                    format     = u'%-' + unicode(maxRegexLen + 2) + u's'
                    regexLabel += format % regexes[index]
                    if maxAnnoLen > 4:
                        if len(annotations[index]) > 4:
                            format      = u'%-' + unicode(maxAnnoLen+2) + u's'
                            regexLabel += format % annotations[index]
                        else:
                            regexLabel += u' ' * (maxAnnoLen + 2)
                    flags = []
                    if self.regexes[index][3]:
                        flags.append(u'i')
                    if self.regexes[index][4]:
                        flags.append(u'u')
                    if self.regexes[index][5]:
                        flags.append(u'm')
                    if self.regexes[index][6]:
                        flags.append(u's')
                    if len(flags):
                        regexLabel += u'[%s]' % ','.join(flags)
                    self.regexLabels.append(regexLabel)
            self.regexLabels = self.regexLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedRegexLabels.listBox.item(
                        cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newRegex:
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
            self.updateRegexBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)


    def updateRegexBoxButtons(self):
        """Update state of Regex box buttons"""
        if self.selectedRegexLabels:
            self.removeButton.setDisabled(False)
            if self.selectedRegexLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedRegexLabels[0] < len(self.regexes) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if self.regexes:
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)


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
    ow   = OWTextableSegment()
    ow.show()
    appl.exec_()
    ow.saveSettings()
