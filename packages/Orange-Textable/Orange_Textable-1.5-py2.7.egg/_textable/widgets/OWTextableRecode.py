#=============================================================================
# Class OWTextableRecode
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

__version__ = '0.13'

"""
<name>Recode</name>
<description>Custom text recoding using regular expressions</description>
<icon>icons/Recode.png</icon>
<priority>2002</priority>
"""

import re, codecs, json, textwrap

from LTTL.Recoder      import Recoder
from LTTL.Segmentation import Segmentation

from TextableUtils      import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableRecode(OWWidget):

    """Orange widget for regex-based recoding"""
    
    settingsList = [
            'substitutions',
            'copyAnnotations',
            'autoSend',
            'label',
            'displayAdvancedSettings',
            'lastLocation',
            'regex',
            'replString',
            'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Recode widget"""

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
        self.outputs = [('Recoded data', Segmentation)]
        
        # Settings...
        self.substitutions              = []
        self.copyAnnotations            = True
        self.autoSend                   = True
        self.label                      = u'recoded_data'
        self.displayAdvancedSettings    = False
        self.lastLocation               = '.'
        self.regex                      = u''
        self.replString                 = u''
        self.uuid                       = None
        self.loadSettings()
        self.uuid                       = getWidgetUuid(self)

        # Other attributes...
        self.createdInputIndices    = []
        self.segmentation           = None
        self.recoder                = Recoder()
        self.substLabels            = []
        self.selectedSubstLabels    = []
        self.newRegex               = r''
        self.newReplString          = r''
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

        # Substitutions box
        substBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Substitutions',
                orientation         = 'vertical',
        )
        substBoxLine1 = OWGUI.widgetBox(
                widget              = substBox,
                box                 = False,
                orientation         = 'horizontal',
                addSpace            = True,
        )
        self.substListbox = OWGUI.listBox(
                widget              = substBoxLine1,
                master              = self,
                value               = 'selectedSubstLabels',
                labels              = 'substLabels',
                callback            = self.updateSubstBoxButtons,
                tooltip             = (
                        u"The list of substitutions that will be applied to\n"
                        u"each segment of the input segmentation.\n\n"
                        u"Substitutions will be applied in the same order\n"
                        u"as they appear in the list.\n\n"
                        u"Column 1 shows the regex pattern.\n"
                        u"Column 2 shows the associated replacement string\n"
                        u"(if not empty).\n"
                        u"Column 3 shows the associated flags."
                ),
        )
        font = QFont()
        font.setFamily('Courier')
        font.setStyleHint(QFont.Courier)
        font.setPixelSize(12)
        self.substListbox.setFont(font)
        substBoxCol2 = OWGUI.widgetBox(
                widget              = substBoxLine1,
                orientation         = 'vertical',
        )
        self.moveUpButton = OWGUI.button(
                widget              = substBoxCol2,
                master              = self,
                label               = u'Move Up',
                callback            = self.moveUp,
                tooltip             = (
                        u"Move the selected substitution upward in the list."
                ),
        )
        self.moveDownButton = OWGUI.button(
                widget              = substBoxCol2,
                master              = self,
                label               = u'Move Down',
                callback            = self.moveDown,
                tooltip             = (
                       u"Move the selected substitution downward in the list."
                ),
        )
        self.removeButton = OWGUI.button(
                widget              = substBoxCol2,
                master              = self,
                label               = u'Remove',
                callback            = self.remove,
                tooltip             = (
                        u"Remove the selected substitution from the list."
                ),
        )
        self.clearAllButton = OWGUI.button(
                widget              = substBoxCol2,
                master              = self,
                label               = u'Clear All',
                callback            = self.clearAll,
                tooltip             = (
                        u"Remove all substitutions from the list."
                ),
        )
        self.importButton = OWGUI.button(
                widget              = substBoxCol2,
                master              = self,
                label               = u'Import List',
                callback            = self.importList,
                tooltip             = (
                        u"Open a dialog for selecting a substitution list\n"
                        u"to import (in JSON format). Substitutions from\n"
                        u"this list will be added to the existing ones."
                ),
        )
        self.exportButton = OWGUI.button(
                widget              = substBoxCol2,
                master              = self,
                label               = u'Export List',
                callback            = self.exportList,
                tooltip             = (
                        u"Open a dialog for selecting a file where the\n"
                        u"substitution list can be exported in JSON format."
                ),
        )
        substBoxLine2 = OWGUI.widgetBox(
                widget              = substBox,
                box                 = False,
                orientation         = 'vertical',
        )
        # Add regex box
        addSubstBox = OWGUI.widgetBox(
                widget              = substBoxLine2,
                box                 = True,
                orientation         = 'vertical',
        )
        OWGUI.lineEdit(
                widget              = addSubstBox,
                master              = self,
                value               = 'newRegex',
                orientation         = 'horizontal',
                label               = u'Regex:',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"The regex pattern that will be added to the list\n"
                        u"when button 'Add' is clicked."
                ),
        )
        OWGUI.separator(
                widget              = addSubstBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = addSubstBox,
                master              = self,
                value               = 'newReplString',
                orientation         = 'horizontal',
                label               = u'Replacement string:',
                labelWidth          = 131,
                callback            = self.updateGUI,
                tooltip             = (
                        u"The (possibly empty) replacement string that will\n"
                        u"be added to the list when button 'Add' is clicked.\n\n"
                        u"Groups of characters captured by parentheses in\n"
                        u"the regex pattern may be inserted in the\n"
                        u"replacement string by using the form '&'\n"
                        u"(ampersand) immediately followed by a digit\n"
                        u" indicating the captured group number (e.g. '&1',\n"
                        u"'&2', etc.)."

                ),
        )
        OWGUI.separator(
                widget              = addSubstBox,
                height              = 3,
        )
        addSubstBoxLine3 = OWGUI.widgetBox(
                widget              = addSubstBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = addSubstBoxLine3,
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
                widget              = addSubstBoxLine3,
                master              = self,
                value               = 'unicodeDependent',
                label               = u'Unicode dependent (u)',
                callback            = self.updateGUI,
                tooltip             = (
                        u"Built-in character classes are Unicode-aware."
                ),
        )
        addSubstBoxLine4 = OWGUI.widgetBox(
                widget              = addSubstBox,
                box                 = False,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = addSubstBoxLine4,
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
                widget              = addSubstBoxLine4,
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
                widget              = addSubstBox,
                height              = 3,
        )
        self.addButton = OWGUI.button(
                widget              = addSubstBox,
                master              = self,
                label               = u'Add',
                callback            = self.add,
                tooltip             = (
                        u"Add the current substitution to the list."
                ),
        )
        self.advancedSettings.advancedWidgets.append(substBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Advanced) Options box...
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
        OWGUI.checkBox(
                widget              = optionsBox,
                master              = self,
                value               = 'copyAnnotations',
                label               = u'Copy annotations',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Copy all annotations from input to output segments."
                ),
        )
        OWGUI.separator(
                widget              = optionsBox,
                height              = 2,
        )
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # (Basic) Substitution box...
        basicSubstBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Substitution',
                orientation         = 'vertical',
        )
        OWGUI.lineEdit(
                widget              = basicSubstBox,
                master              = self,
                value               = 'regex',
                orientation         = 'horizontal',
                label               = u'Regex:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The regex that will be applied to each segment in\n"
                        u"the input segmentation."
                ),
        )
        OWGUI.separator(
                widget              = basicSubstBox,
                height              = 3,
        )
        OWGUI.lineEdit(
                widget              = basicSubstBox,
                master              = self,
                value               = 'replString',
                orientation         = 'horizontal',
                label               = u'Replacement string:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The string that will be used for replacing each\n"
                        u"match of the above regex in the input segmentation."
                ),
        )
        OWGUI.separator(
                widget              = basicSubstBox,
                height              = 3,
        )
        self.advancedSettings.basicWidgets.append(basicSubstBox)
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
        self.substitutions = list()
        self.infoBox.inputChanged()
        try:
            json_data = json.loads(message.content)
            temp_substitutions = list()
            for entry in json_data:
                regex               = entry.get('regex', '')
                replString          = entry.get('replacement_string', '')
                ignoreCase          = entry.get('ignore_case', False)
                unicodeDependent    = entry.get('unicode_dependent', False)
                multiline           = entry.get('multiline', False)
                dotAll              = entry.get('dot_all', False)
                if regex == '':
                    m =   "JSON message on input connection doesn't " \
                        + "have the right keys and/or values."
                    m = '\n\t'.join(textwrap.wrap(m, 35))
                    self.infoBox.noDataSent(m)
                    self.send('Segmentation', None, self)
                    return
                temp_substitutions.append((
                    regex,
                    replString,
                    ignoreCase,
                    unicodeDependent,
                    multiline,
                    dotAll,
                ))
            self.substitutions.extend(temp_substitutions)
            self.sendButton.settingsChanged()
        except ValueError:
            m = "Message content is not in JSON format."
            m = '\n\t'.join(textwrap.wrap(m, 35))
            self.infoBox.noDataSent(m)
            self.send('Text data', None, self)
            return


    def sendData(self):
    
        """(Have LTTL.Recoder) perform the actual recoding"""

        # Check that there's something on input...
        if not self.segmentation:
            self.infoBox.noDataSent(u'No input segmentation.')
            self.send('Recoded data', None, self)
            return

        # Check that segmentation is non-overlapping...
        if not self.segmentation.is_non_overlapping():
            self.infoBox.noDataSent(u'Input segmentation is overlapping.')
            self.send('Recoded data', None, self)
            return

        # Check that label is not empty...
        if not self.label:
            self.infoBox.noDataSent(u'No label was provided.')
            self.send('Recoded data', None, self)
            return

        # Get substitutions from basic or advanced settings...
        if self.displayAdvancedSettings:
            mySubstitutions = self.substitutions
        else:
            mySubstitutions = [
                    [
                            self.regex,
                            self.replString,
                            False,
                            True,
                            False,
                            False,
                    ]
            ]

        # Basic settings...
        if self.displayAdvancedSettings:
            copyAnnotations   = self.copyAnnotations
        else:
            copyAnnotations   = True

        # Prepare regexes...
        substitutions = []
        for subst in mySubstitutions:
            regex_string = subst[0]
            if subst[2] or subst[3] or subst[4] or subst[5]:
                flags = ''
                if subst[2]:
                    flags += 'i'
                if subst[3]:
                    flags += 'u'
                if subst[4]:
                    flags += 'm'
                if subst[5]:
                    flags += 's'
                regex_string += '(?%s)' % flags
            substitutions.append((re.compile(regex_string), subst[1]))
        self.recoder.substitutions = substitutions
        
        # Perform recoding...
        self.clearCreatedInputIndices()
        previousNumInputs = len(Segmentation.data)
        progressBar = OWGUI.ProgressBar(
                self,
                iterations = len(self.segmentation) * len(mySubstitutions)
        )
        recoded_data = self.recoder.apply(
            segmentation        = self.segmentation,
            mode                = 'custom',
            label               = self.label,
            copy_annotations    = self.copyAnnotations,
            progress_callback   = progressBar.advance,
        )
        progressBar.finish()
        newNumInputs = len(Segmentation.data)
        self.createdInputIndices = range(previousNumInputs, newNumInputs)
        self.send('Recoded data', recoded_data, self)
        message = u'Data contains %i segment@p.' % len(recoded_data)
        message = pluralize(message, len(recoded_data))
        self.infoBox.dataSent(message)
        self.sendButton.resetSettingsChangedFlag()


    def inputData(self, segmentation):
        """Process incoming segmentation"""
        self.segmentation = segmentation
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def importList(self):
        """Display a FileDialog and import substitution list"""
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
            temp_substitutions = list()
            for entry in json_data:
                regex               = entry.get('regex', '')
                replString          = entry.get('replacement_string', '')
                ignoreCase          = entry.get('ignore_case', False)
                unicodeDependent    = entry.get('unicode_dependent', False)
                multiline           = entry.get('multiline', False)
                dotAll              = entry.get('dot_all', False)
                if regex == '':
                    QMessageBox.warning(
                            None,
                            'Textable',
                            "Selected JSON file doesn't have the right keys "
                            "and/or values.",
                            QMessageBox.Ok
                    )
                    return
                temp_substitutions.append((
                    regex,
                    replString,
                    ignoreCase,
                    unicodeDependent,
                    multiline,
                    dotAll,
                ))
            self.substitutions.extend(temp_substitutions)
            if temp_substitutions:
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
        """Display a FileDialog and export substitution list"""
        toDump = list()
        for substitution in self.substitutions:
            toDump.append({
                    'regex':                substitution[0],
                    'replacement_string':   substitution[1],
            })
            if substitution[2]:
                toDump[-1]['ignore_case']       = substitution[2]
            if substitution[3]:
                toDump[-1]['unicode_dependent'] = substitution[3]
            if substitution[4]:
                toDump[-1]['multiline']         = substitution[4]
            if substitution[5]:
                toDump[-1]['dot_all']           = substitution[5]
        filePath = unicode(
                QFileDialog.getSaveFileName(
                        self,
                        u'Export Substitution List',
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
                    'Substitution list correctly exported',
                    QMessageBox.Ok
            )


    def moveUp(self):
        """Move substitution upward in Substitutions listbox"""
        if self.selectedSubstLabels:
            index = self.selectedSubstLabels[0]
            if index > 0:
                temp                          = self.substitutions[index-1]
                self.substitutions[index-1]   = self.substitutions[index]
                self.substitutions[index]     = temp
                self.selectedSubstLabels.listBox.item(index-1).setSelected(1)
                self.sendButton.settingsChanged()


    def moveDown(self):
        """Move substitution downward in Substitutions listbox"""
        if self.selectedSubstLabels:
            index = self.selectedSubstLabels[0]
            if index < len(self.substitutions)-1:
                temp                          = self.substitutions[index+1]
                self.substitutions[index+1]   = self.substitutions[index]
                self.substitutions[index]     = temp
                self.selectedSubstLabels.listBox.item(index+1).setSelected(1)
                self.sendButton.settingsChanged()


    def clearAll(self):
        """Remove all substitutions from Substitutions"""
        del self.substitutions[:]
        del self.selectedSubstLabels[:]
        self.sendButton.settingsChanged()
        

    def remove(self):
        """Remove substitution from substitutions attr"""
        if self.selectedSubstLabels:
            index = self.selectedSubstLabels[0]
            self.substitutions.pop(index)
            del self.selectedSubstLabels[:]
            self.sendButton.settingsChanged()


    def add(self):
        """Add substitution to substitutions attr"""
        self.substitutions.append((
            self.newRegex,
            self.newReplString,
            self.ignoreCase,
            self.unicodeDependent,
            self.multiline,
            self.dotAll,
        ))
        self.sendButton.settingsChanged()


    def clearCreatedInputIndices(self):
        for i in self.createdInputIndices:
            Segmentation.data[i] = None
        for i in reversed(xrange(len(Segmentation.data))):
            if Segmentation.data[i] is None:
                Segmentation.data.pop(i)
            else:
                break


    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            if self.selectedSubstLabels:
                cachedLabel = self.selectedSubstLabels[0]
            else:
                cachedLabel = None
            del self.substLabels[:]
            if len(self.substitutions):
                regexes          = [r[0] for r in self.substitutions]
                replStrings      = [r[1] for r in self.substitutions]
                maxRegexLen      = max([len(r) for r in regexes])
                maxReplStringLen = max([len(r) for r in replStrings])
                for index in range(len(self.substitutions)):
                    format      = u'%-' + unicode(maxRegexLen + 2) + u's'
                    substLabel  = format % regexes[index]
                    format      = u'%-' + unicode(maxReplStringLen + 2) + u's'
                    substLabel += format % replStrings[index]
                    flags = []
                    if self.substitutions[index][2]:
                        flags.append(u'i')
                    if self.substitutions[index][3]:
                        flags.append(u'u')
                    if self.substitutions[index][4]:
                        flags.append(u'm')
                    if self.substitutions[index][5]:
                        flags.append(u's')
                    if len(flags):
                        substLabel += u'[%s]' % ','.join(flags)
                    self.substLabels.append(substLabel)
            self.substLabels = self.substLabels
            if cachedLabel is not None:
                self.sendButton.sendIfPreCallback = None
                self.selectedSubstLabels.listBox.item(
                        cachedLabel
                ).setSelected(1)
                self.sendButton.sendIfPreCallback = self.updateGUI
            if self.newRegex:
                self.addButton.setDisabled(False)
            else:
                self.addButton.setDisabled(True)
            self.updateSubstBoxButtons()
            self.advancedSettings.setVisible(True)
        else:
            self.advancedSettings.setVisible(False)


    def updateSubstBoxButtons(self):
        """Update state of Regex box buttons"""
        if self.selectedSubstLabels:
            self.removeButton.setDisabled(False)
            if self.selectedSubstLabels[0] > 0:
                self.moveUpButton.setDisabled(False)
            else:
                self.moveUpButton.setDisabled(True)
            if self.selectedSubstLabels[0] < len(self.substitutions) - 1:
                self.moveDownButton.setDisabled(False)
            else:
                self.moveDownButton.setDisabled(True)
        else:
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
            self.removeButton.setDisabled(True)
        if self.substitutions:
            self.clearAllButton.setDisabled(False)
            self.exportButton.setDisabled(False)
        else:
            self.clearAllButton.setDisabled(True)
            self.exportButton.setDisabled(True)


    def onDeleteWidget(self):
        self.clearCreatedInputIndices()


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
    ow   = OWTextableRecode()
    ow.show()
    appl.exec_()
    ow.saveSettings()
