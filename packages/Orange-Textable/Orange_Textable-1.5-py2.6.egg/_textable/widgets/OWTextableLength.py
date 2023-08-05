#=============================================================================
# Class OWTextableLength
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

__version__ = '0.14'

"""
<name>Length</name>
<description>Compute the (average) length of segments</description>
<icon>icons/Length.png</icon>
<priority>8002</priority>
"""

from LTTL.Table        import Table
from LTTL.Processor    import Processor
from LTTL.Segmentation import Segmentation

from TextableUtils      import *

import Orange
from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableLength(OWWidget):

    """Orange widget for length computation"""

    contextHandlers = {
        '': SegmentationListContextHandler(
            '', [
                ContextInputListField('segmentations'),
                ContextInputIndex('units'),
                ContextInputIndex('averagingSegmentation'),
                ContextInputIndex('contexts'),
                'mode',
                'unitAnnotationKey',
                'contextAnnotationKey',
                'sequenceLength',
            ]
        )
    }

    settingsList = [
            'autoSend',
            'computeStdev',
            'mergeContexts',
            'computeAverage',
            'sequenceLength',
    ]

    def __init__(self, parent=None, signalManager=None):
        
        """Initialize a Length widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )
        
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Textable table', Table)]
        
        # Settings...
        self.autoSend                   = False
        self.computeAverage             = False
        self.computeStdev               = False
        self.autoSend                   = False
        self.mode                       = u'No context'
        self.mergeContexts              = False
        self.windowSize                 = 1
        self.loadSettings()

        # Other attributes...
        self.processor              = Processor()
        self.segmentations          = []
        self.units                  = None
        self.averagingSegmentation  = None
        self.contexts               = None
        self.contextAnnotationKey   = None
        self.settingsRestored       = False                                         
        self.infoBox                = InfoBox(
                widget          = self.controlArea,
                stringClickSend = u"Please click 'Compute' when ready.",
        )
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                buttonLabel         = u'Compute',
                checkboxLabel       = u'Compute automatically',
                sendIfPreCallback   = self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Units',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.unitSegmentationCombo = OWGUI.comboBox(
                widget              = self.unitsBox,
                master              = self,
                value               = 'units',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 190,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose segments constitute the\n"
                        u"units of length."
                ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
        OWGUI.separator(
                widget              = self.unitsBox,
                height              = 3,
        )

        # Averaging box...
        self.averagingBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Averaging',
                orientation         = 'vertical',
                addSpace            = True,
        )
        averagingBoxLine1 = OWGUI.widgetBox(
                widget              = self.averagingBox,
                box                 = False,
                orientation         = 'horizontal',
                addSpace            = True,
        )
        OWGUI.checkBox(
                widget              = averagingBoxLine1,
                master              = self,
                value               = 'computeAverage',
                label               = u'Average over segmentation:',
                labelWidth          = 190,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Check this box in order to measure the average\n"
                        u"length of segments.\n\n"
                        u"Leaving this box unchecked implies that no\n"
                        u"averaging will take place."
                ),
        )
        self.averagingSegmentationCombo = OWGUI.comboBox(
                widget              = averagingBoxLine1,
                master              = self,
                value               = 'averagingSegmentation',
                orientation         = 'horizontal',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose segment length will be\n"
                        u"measured and averaged (if the box to the left\n"
                        u"is checked)."
                ),
        )
        self.computeStdevCheckBox = OWGUI.checkBox(
                widget              = self.averagingBox,
                master              = self,
                value               = 'computeStdev',
                label               = u'Compute standard deviation',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Check this box to compute not only length average\n"
                        u"but also standard deviation (if the above box\n"
                        u"is checked).\n\n"
                        u"Note that computing standard deviation can be a\n"
                        u"lengthy operation for large segmentations."
                ),
        )
        OWGUI.separator(
                widget              = self.averagingBox,
                height              = 2,
        )

        # Contexts box...
        self.contextsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Contexts',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.modeCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'mode',
                sendSelectedValue   = True,
                items               = [
                        u'No context',
                        u'Sliding window',
                        u'Containing segmentation',
                ],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 190,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Context specification mode.\n\n"
                        u"Contexts define the rows of the resulting table.\n\n"
                        u"'No context': simply return the length of the\n"
                        u"'Units' segmentation, or the average length of\n"
                        u"segments in the 'Averaging' segmentation (if any),\n"
                        u"so that the output table contains a single row.\n\n"
                        u"'Sliding window': contexts are defined as all the\n"
                        u"successive, overlapping sequences of n segments\n"
                        u"in the 'Averaging' segmentation; this mode is\n"
                        u"available only if the 'Averaging' box is checked.\n\n"
                        u"'Containing segmentation': contexts are defined\n"
                        u"as the distinct segments occurring in a given\n"
                        u"segmentation (which may or may not be the same\n"
                        u"as the 'Units' and/or 'Averaging' segmentation)."
                ),
        )
        self.slidingWindowBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.slidingWindowBox,
                height              = 3,
        )
        self.windowSizeSpin = OWGUI.spin(
                widget              = self.slidingWindowBox,
                master              = self,
                value               = 'windowSize',
                min                 = 1,
                max                 = 1,
                step                = 1,
                orientation         = 'horizontal',
                label               = u'Window size:',
                labelWidth          = 190,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The length of segment sequences defining contexts."
                ),
        )
        self.containingSegmentationBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        self.contextSegmentationCombo = OWGUI.comboBox(
                widget              = self.containingSegmentationBox,
                master              = self,
                value               = 'contexts',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 190,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose segment types define\n"
                        u"the contexts in which length will be measured."
                ),
        )
        OWGUI.separator(
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        self.contextAnnotationCombo = OWGUI.comboBox(
                widget              = self.containingSegmentationBox,
                master              = self,
                value               = 'contextAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 190,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether context types are defined by\n"
                        u"the content of segments in the above specified\n"
                        u"segmentation (value 'none') or by their\n"
                        u"annotation values for a specific annotation key."
                ),
        )
        OWGUI.separator(
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = self.containingSegmentationBox,
                master              = self,
                value               = 'mergeContexts',
                label               = u'Merge contexts',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Check this box if you want to treat all segments\n"
                        u"of the above specified segmentation as forming\n"
                        u"a single context (hence the resulting crosstab\n"
                        u"contains a single row)."
                ),
        )
        OWGUI.separator(
                widget              = self.contextsBox,
                height              = 3,
        )

        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()

        self.sendButton.sendIf()



    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        self.closeContext()
        updateMultipleInputs(
                self.segmentations,
                newItem,
                newId,
                self.onInputRemoval
        )
        self.infoBox.inputChanged()
        self.updateGUI()


    def sendData(self):

        """Check input, compute (average) length table, then send it"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.noDataSent(u'No input.')
            self.send('Textable table', None)
            return

        # Units parameter...
        units = self.segmentations[self.units][1]

        # Averaging parameters...
        if self.computeAverage:
            averaging = {
                    'segmentation'
                    :
                    self.segmentations[self.averagingSegmentation][1]
            }
            if self.computeStdev:
                averaging['std_deviation'] = True
            else:
                averaging['std_deviation'] = False
        else:
            averaging = None
            
        # Case 1: sliding window...
        if self.mode == 'Sliding window':

            # Compute length...
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = len(units) - (self.windowSize - 1)
            )
            table = self.processor.length_in_window(
                    units,
                    averaging           = averaging,
                    window_size         = self.windowSize,
                    progress_callback   = progressBar.advance,
            )
            progressBar.finish()

        # Case 2: Containing segmentation or no context...
        else:

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                contexts = {
                    'segmentation':     self.segmentations[self.contexts][1],
                    'annotation_key':   self.contextAnnotationKey or None,
                    'merge':            self.mergeContexts,
                }
                if contexts['annotation_key'] == u'(none)':
                    contexts['annotation_key'] = None
                num_iterations = len(contexts['segmentation'])
            # Parameters for mode 'No context'...
            else:
                contexts = None
                num_iterations = 1

            # Compute frequency...
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = num_iterations
            )
            table = self.processor.length_in_context(
                    units,
                    averaging,
                    contexts,
                    progress_callback   = progressBar.advance,
            )
            progressBar.finish()

        self.send('Textable table', table)
        self.infoBox.dataSent()

        self.sendButton.resetSettingsChangedFlag()


    def onInputRemoval(self, index):
        """Handle removal of input with given index"""
        if index < self.units:
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations)-1:
            self.units -= 1
            if self.units < 0:
                self.units = None
        if self.mode == u'Containing segmentation':
            if index == self.contexts:
                self.mode       = u'No context'
                self.contexts   = None
            elif index < self.contexts:
                self.contexts -= 1
                if self.contexts < 0:
                    self.mode     = u'No context'
                    self.contexts = None
        if          self.computeAverage \
                and self.averagingSegmentation != self.units:
            if index == self.averagingSegmentation:
                self.computeAverage         = False
                self.averagingSegmentation  = None
            elif index < self.averagingSegmentation:
                self.averagingSegmentation -= 1
                if self.averagingSegmentation < 0:
                    self.computeAverage         = False
                    self.averagingSegmentation  = None


    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.averagingSegmentationCombo.clear()
        self.averagingSegmentationCombo.clear()

        if self.mode == u'No context':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)

        if len(self.segmentations) == 0:
            self.units              = None
            self.unitsBox.setDisabled(True)
            self.averagingBox.setDisabled(True)
            self.mode               = 'No context'
            self.contextsBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
                self.averagingSegmentation = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
                self.averagingSegmentationCombo.addItem(segmentation[1].label)
            self.units = self.units
            self.averagingSegmentation = self.averagingSegmentation
            self.unitsBox.setDisabled(False)
            self.averagingBox.setDisabled(False)
            self.contextsBox.setDisabled(False)
            if self.computeAverage:
                if self.modeCombo.itemText(1) != u'Sliding window':
                    self.modeCombo.insertItem(1, u'Sliding window')
                self.averagingSegmentationCombo.setDisabled(False)
                self.computeStdevCheckBox.setDisabled(False)
            else:
                self.averagingSegmentationCombo.setDisabled(True)
                self.computeStdevCheckBox.setDisabled(True)
                self.computeStdev = False
                if self.mode == u'Sliding window':
                    self.mode = u'No context'
                if self.modeCombo.itemText(1) == u'Sliding window':
                    self.modeCombo.removeItem(1)

        if self.mode == 'Sliding window':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)
            self.windowSizeSpin.control.setRange(
                    1,
                    len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize or 1

        elif self.mode == 'Containing segmentation':
            self.slidingWindowBox.setVisible(False)
            self.containingSegmentationBox.setVisible(True)
            self.contextSegmentationCombo.clear()
            for index in range(len(self.segmentations)):
                self.contextSegmentationCombo.addItem(
                        self.segmentations[index][1].label
                )
            self.contexts = self.contexts or 0
            segmentation = self.segmentations[self.contexts]
            self.contextAnnotationCombo.clear()
            self.contextAnnotationCombo.addItem(u'(none)')
            contextAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in contextAnnotationKeys:
                self.contextAnnotationCombo.addItem(key)
            if self.contextAnnotationKey not in contextAnnotationKeys:
                self.contextAnnotationKey = u'(none)'
            self.contextAnnotationKey = self.contextAnnotationKey
            
        self.adjustSize()



    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext("", self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()


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
    from LTTL.Segmenter import Segmenter
    from LTTL.Input     import Input
    appl = QApplication(sys.argv)
    ow   = OWTextableLength()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'wonderful world', label=u'text2')
    segmenter = Segmenter()
    seg3 = segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = segmenter.tokenize(seg3, [(r'\w+(?u)',u'Tokenize',)], label=u'words')
    seg5 = segmenter.tokenize(seg3, [(r'\w',u'Tokenize',)], label=u'letters')
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.inputData(seg5, 3)
    ow.show()
    appl.exec_()
    ow.saveSettings()
