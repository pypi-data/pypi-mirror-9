#=============================================================================
# Class OWTextableConvert
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

__version__ = '0.18'

"""
<name>Convert</name>
<description>Convert, transform, or export Orange Textable tables</description>
<icon>icons/Convert.png</icon>
<priority>10001</priority>
"""

import os, codecs

from LTTL.Table         import *
from TextableUtils      import *
from LTTL.Segmentation  import Segmentation
from LTTL.Input         import Input

from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableConvert(OWWidget):

    """Orange widget for converting a Textable table to an Orange table"""

    settingsList = [
            'conversionEncoding',
            'exportEncoding',
            'colDelimiter',
            'includeOrangeHeaders',
            'sortRows',
            'sortRowsReverse',
            'sortCols',
            'sortColsReverse',
            'normalize',
            'normalizeMode',
            'normalizeType',
            'convert',
            'conversionType',
            'associationBias',
            'transpose',
            'reformat',
            'unweighted',
            'autoSend',
            'lastLocation',
            'displayAdvancedSettings',
    ]

    # Predefined list of available encodings...
    encodings = getPredefinedEncodings()

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Convert widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )

        self.inputs  = [('Textable table', Table, self.inputData, Single)]
        self.outputs = [
                ('Orange table', Orange.data.Table, Default),
                ('Textable table', Table),
                ('Segmentation', Segmentation)
        ]

        # Settings...
        self.sortRows                   = False
        self.sortRowsReverse            = False
        self.sortCols                   = False
        self.sortColsReverse            = False
        self.normalize                  = False
        self.normalizeMode              = 'rows'
        self.normalizeType              = 'l1'
        self.convert                    = False
        self.conversionType             = 'association matrix'
        self.associationBias            = 'neutral'
        self.transpose                  = False
        self.reformat                   = False
        self.unweighted                 = False
        self.autoSend                   = True
        self.conversionEncoding         = 'iso-8859-15'
        self.exportEncoding             = 'utf-8'
        self.colDelimiter               = u'\t'
        self.includeOrangeHeaders       = False
        self.lastLocation               = '.'
        self.displayAdvancedSettings    = False
        self.loadSettings()

        # Other attributes...
        self.sortRowsKeyId          = None
        self.sortColsKeyId          = None
        self.table                  = None
        self.segmentation           = Input(label=u'table', text=u'')
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

        # Transform box
        self.transformBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Transform',
                orientation         = 'vertical',
        )
        self.transformBoxLine1 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine1,
                master              = self,
                value               = 'sortRows',
                label               = u'Sort rows by column:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort table rows."
                ),
        )
        self.sortRowsKeyIdCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine1,
                master              = self,
                value               = 'sortRowsKeyId',
                items               = [],
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Column whose values will be used for sorting rows."
                ),
        )
        self.sortRowsKeyIdCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine1,
                width               = 5,
        )
        self.sortRowsReverseCheckBox = OWGUI.checkBox(
                widget              = self.transformBoxLine1,
                master              = self,
                value               = 'sortRowsReverse',
                label               = u'Reverse',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort rows in reverse (i.e. decreasing) order."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine2 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine2,
                master              = self,
                value               = 'sortCols',
                label               = u'Sort columns by row:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort table columns."
                ),
        )
        self.sortColsKeyIdCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine2,
                master              = self,
                value               = 'sortColsKeyId',
                items               = [],
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Row whose values will be used for sorting columns."
                ),
        )
        self.sortColsKeyIdCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine2,
                width               = 5,
        )
        self.sortColsReverseCheckBox = OWGUI.checkBox(
                widget              = self.transformBoxLine2,
                master              = self,
                value               = 'sortColsReverse',
                label               = u'Reverse',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort columns in reverse (i.e. decreasing) order."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transposeCheckBox = OWGUI.checkBox(
                widget              = self.transformBox,
                master              = self,
                value               = 'transpose',
                label               = u'Transpose',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Transpose table (i.e. exchange rows and columns)."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine4 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine4,
                master              = self,
                value               = 'normalize',
                label               = u'Normalize:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Normalize table."
                ),
        )
        self.normalizeModeCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine4,
                master              = self,
                value               = 'normalizeMode',
                items               = [
                                            u'rows',
                                            u'columns',
                                            u'quotients',
                                            u'TF-IDF',
                                            u'presence/absence'
                                    ],
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Normalization mode:\n\n"
                        u"Row: L1 or L2 normalization by rows.\n\n"
                        u"Column: L1 or L2 normalization by columns.\n\n"
                        u"Quotients: the count stored in each cell is\n"
                        u"divided by the corresponding theoretical count\n"
                        u"under independence: the result is greater than 1\n"
                        u"in case of attraction between line and column,\n"
                        u"lesser than 1 in case of repulsion, and 1 if\n"
                        u"there is no specific interaction between them.\n\n"
                        u"TF-IDF: the count stored in each cell is multiplied\n"
                        u"by the natural log of the ratio of the number of\n"
                        u"rows (i.e. contexts) having nonzero count for this\n"
                        u"column (i.e. unit) to the total number of rows.\n\n"
                        u"Presence/absence: counts greater than 0 are\n"
                        u"replaced with 1."
                ),
        )
        self.normalizeModeCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine4,
                width               = 5,
        )
        self.normalizeTypeCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine4,
                master              = self,
                orientation         = 'horizontal',
                value               = 'normalizeType',
                items               = [u'L1', u'L2'],
                sendSelectedValue   = True,
                label               = u'Norm:',
                labelWidth          = 40,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Norm type.\n\n"
                        u"L1: divide each value by the sum of the enclosing\n"
                        u"normalization unit (row/column)\n\n"
                        u"L2: divide each value by the sum of squares of the\n"
                        u"enclosing normalization unit, then take square root."
                ),
        )
        self.normalizeTypeCombo.setMinimumWidth(70)
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine5 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'horizontal',
        )
        OWGUI.checkBox(
                widget              = self.transformBoxLine5,
                master              = self,
                value               = 'convert',
                label               = u'Convert to:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Apply crosstab conversions."
                ),
        )
        self.conversionTypeCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine5,
                master              = self,
                value               = 'conversionType',
                items               = [
                                            'document frequency',
                                            'association matrix',
                                    ],
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Crosstab conversions.\n\n"
                        u"'document frequency': based on a pivot crosstab,\n"
                        u"return a new crosstab giving, for each column,\n"
                        u"the number of distinct rows that have nonzero\n"
                        u"frequency (hence the resulting crosstab contains\n"
                        u"a single row).\n\n"
                        u"'association matrix': based on a pivot crosstab,\n"
                        u"return a symmetric table with a measure of\n"
                        u"associativity between each pair of columns of the\n"
                        u"original table (see also the effect of the 'bias'\n"
                        u"parameter)."
                ),
        )
        self.conversionTypeCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = self.transformBoxLine5,
                width               = 5,
        )
        self.associationBiasCombo = OWGUI.comboBox(
                widget              = self.transformBoxLine5,
                master              = self,
                orientation         = 'horizontal',
                value               = 'associationBias',
                items               = [u'frequent', u'none', u'rare'],
                sendSelectedValue   = True,
                label               = u'Bias:',
                labelWidth          = 40,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Association bias (alpha parameter in Deneulin,\n"
                        u"Gautier, Le Fur, & Bavaud 2014).\n\n"
                        u"'frequent': emphasizes strong associations\n"
                        u"between frequent units (alpha=1).\n\n"
                        u"'none': balanced compromise between\n"
                        u"frequent and rare units (alpha=0.5).\n\n"
                        u"'rare': emphasizes strong associations\n"
                        u"between rare units (alpha=0). Note that in this\n"
                        u"particular case, values greater than 1 express an\n"
                        u"attraction and values lesser than 1 a repulsion."
                ),
        )
        self.associationBiasCombo.setMinimumWidth(70)
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.transformBoxLine6 = OWGUI.widgetBox(
                widget              = self.transformBox,
                orientation         = 'vertical',
        )
        self.reformatCheckbox = OWGUI.checkBox(
                widget              = self.transformBoxLine6,
                master              = self,
                value               = 'reformat',
                label               = u'Reformat to sparse crosstab',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Reformat a crosstab to sparse format, where each\n"
                        u"row corresponds to a pair 'row-column' of the\n"
                        u"original crosstab."
                ),
        )
        OWGUI.separator(
                widget              = self.transformBoxLine6,
                height              = 3,
        )
        iBox = OWGUI.indentedBox(
                widget              = self.transformBoxLine6,
        )
        self.unweightedCheckbox = OWGUI.checkBox(
                widget              = iBox,
                master              = self,
                value               = 'unweighted',
                label               = u'Encode counts by repeating rows',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"This option (only available for crosstabs with\n"
                        u"integer values) specifies that values will be\n"
                        u"encoded in the sparse matrix by the number of\n"
                        u"times each row (i.e. each pair row-column of the\n"
                        u"original crosstab) is repeated. Otherwise each\n"
                        u"row-column pair will appear only once and the\n"
                        u"corresponding value will be stored explicitely\n"
                        u"in a separate column with label '__weight__'.\n"
                ),
        )
        OWGUI.separator(
                widget              = self.transformBox,
                height              = 3,
        )
        self.advancedSettings.advancedWidgets.append(self.transformBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # This "dummy" box is the reason why an extra (and unwanted) pixel
        # appears just below the Advanced Settings checkbox. It is necessary
        # for the widget's size to adjust properly when switching between
        # modes...
        dummyBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                addSpace            = False,
        )
        self.advancedSettings.basicWidgets.append(dummyBox)

        # Conversion box
        encodingBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Encoding',
                orientation         = 'vertical',
                addSpace            = True,
        )
        encodingBoxLine1 = OWGUI.widgetBox(
                widget              = encodingBox,
                orientation         = 'horizontal',
        )
        OWGUI.widgetLabel(
                widget              = encodingBoxLine1,
                labelWidth          = 180,
                label               = u'Orange table:',
        )
        conversionEncodingCombo = OWGUI.comboBox(
                widget              = encodingBoxLine1,
                master              = self,
                value               = 'conversionEncoding',
                items               = type(self).encodings,
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                orientation         = 'horizontal',
                tooltip             = (
                        u"Select the encoding of the Orange table that is\n"
                        u"sent on the widget's output connections.\n\n"
                        u"Note that utf-8 and other variants of Unicode are\n"
                        u"usually not well supported by standard Orange\n"
                        u"widgets."
                ),
        )
        conversionEncodingCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = encodingBoxLine1,
                width               = 5,
        )
        dummyLabel = OWGUI.widgetLabel(
                widget              = encodingBoxLine1,
                label               = '',
        )
        OWGUI.separator(
                widget              = encodingBox,
                height              = 3,
        )
        encodingBoxLine2 = OWGUI.widgetBox(
                widget              = encodingBox,
                orientation         = 'horizontal',
        )
        OWGUI.widgetLabel(
                widget              = encodingBoxLine2,
                labelWidth          = 180,
                label               = u'Output file:',
        )
        conversionEncodingCombo = OWGUI.comboBox(
                widget              = encodingBoxLine2,
                master              = self,
                value               = 'exportEncoding',
                items               = type(self).encodings,
                sendSelectedValue   = True,
                callback            = self.sendButton.settingsChanged,
                orientation         = 'horizontal',
                tooltip             = (
                        u"Select the encoding of the table that can be\n"
                        u"saved to a file by clicking the 'Export' button\n"
                        u"below.\n\n"
                        u"Note that the table that is copied to the\n"
                        u"clipboard by clicking the 'Copy to clipboard'\n"
                        u"button below is always encoded in utf-8."
                ),
        )
        conversionEncodingCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = encodingBoxLine2,
                width               = 5,
        )
        dummyLabel = OWGUI.widgetLabel(
                widget              = encodingBoxLine2,
                label               = '',
        )
        OWGUI.separator(
                widget              = encodingBox,
                height              = 3,
        )

        # Export box
        exportBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Export',
                orientation         = 'vertical',
                addSpace            = False,
        )
        exportBoxLine2 = OWGUI.widgetBox(
                widget              = exportBox,
                orientation         = 'horizontal',
        )
        OWGUI.widgetLabel(
                widget              = exportBoxLine2,
                labelWidth          = 180,
                label               = u'Column delimiter:',
        )
        colDelimiterCombo = OWGUI.comboBox(
                widget              = exportBoxLine2,
                master              = self,
                value               = 'colDelimiter',
                callback            = self.sendButton.settingsChanged,
                orientation         = 'horizontal',
                items               = [
                                            u'tabulation (\\t)',
                                            u'comma (,)',
                                            u'semi-colon (;)',
                                    ],
                sendSelectedValue   = True,
                control2attributeDict = {
                                            'tabulation (\\t)': u'\t',
                                            'comma (,)': u',',
                                            'semi-colon (;)': u';',
                                        },
                tooltip             = (
                        u"Select the character used for delimiting columns."
                ),
        )
        colDelimiterCombo.setMinimumWidth(150)
        OWGUI.separator(
                widget              = exportBoxLine2,
                width               = 5,
        )
        dummyLabel = OWGUI.widgetLabel(
                widget              = exportBoxLine2,
                label               = '',
        )
        OWGUI.separator(
                widget              = exportBox,
                height              = 2,
        )
        OWGUI.checkBox(
                widget              = exportBox,
                master              = self,
                value               = 'includeOrangeHeaders',
                label               = u'Include Orange headers',
                tooltip             = (
                        u"Include Orange table headers in output file."
                ),
        )
        OWGUI.separator(
                widget              = exportBox,
                height              = 2,
        )
        exportBoxLine3 = OWGUI.widgetBox(
                widget              = exportBox,
                orientation         = 'horizontal',
        )
        self.exportButton = OWGUI.button(
                widget              = exportBoxLine3,
                master              = self,
                label               = u'Export to file',
                callback            = self.exportFile,
                tooltip             = (
                        u"Open a dialog for selecting the output file to\n"
                        u"which the table will be saved."
                ),
        )
        self.copyButton = OWGUI.button(
                widget              = exportBoxLine3,
                master              = self,
                label               = u'Copy to clipboard',
                callback            = self.copyToClipboard,
                tooltip             = (
                        u"Copy table to clipboard, in order to paste it in\n"
                        u"another application (typically in a spreadsheet)."
                        u"\n\nNote that the only possible encoding is utf-8."
                ),
        )
        OWGUI.separator(
                widget              = exportBox,
                height              = 2,
        )
        self.advancedSettings.advancedWidgets.append(exportBox)

        # Export box
        basicExportBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Export',
                orientation         = 'vertical',
                addSpace            = True,
        )
        basicExportBoxLine1 = OWGUI.widgetBox(
                widget              = basicExportBox,
                orientation         = 'horizontal',
        )
        self.basicExportButton = OWGUI.button(
                widget              = basicExportBoxLine1,
                master              = self,
                label               = u'Export to file',
                callback            = self.exportFile,
                tooltip             = (
                        u"Open a dialog for selecting the output file to\n"
                        u"which the table will be saved."
                ),
        )
        self.basicCopyButton = OWGUI.button(
                widget              = basicExportBoxLine1,
                master              = self,
                label               = u'Copy to clipboard',
                callback            = self.copyToClipboard,
                tooltip             = (
                        u"Copy table to clipboard, in order to paste it in\n"
                        u"another application (typically in a spreadsheet)."
                        u"\n\nNote that the only possible encoding is utf-8."
                ),
        )
        OWGUI.separator(
                widget              = basicExportBox,
                height              = 2,
        )
        self.advancedSettings.basicWidgets.append(basicExportBox)


        # Info box...
        self.infoBox.draw()

        # Send button and checkbox
        self.sendButton.draw()

        self.sendButton.sendIf()


    def inputData(self, newInput):
        """Process incoming data."""
        self.table = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()


    def sendData(self):

        """Convert and send table"""

        # Check that there is something on input...
        if not self.table:
            self.infoBox.noDataSent(u'No input.')
            self.send('Orange table', None)
            self.send('Textable table', None)
            self.send('Segmentation', None)
            self.segmentation.clear()
            return

        transformed_table = self.table

        if self.displayAdvancedSettings:

            # Precompute number of iterations...
            numIterations = 0
            if self.normalize:
                if self.normalizeMode == 'rows':
                    numIterations += len(transformed_table.row_ids)
                elif self.normalizeMode == 'columns':
                    numIterations += len(transformed_table.col_ids)
                elif self.normalizeMode == 'presence/absence':
                    numIterations += (
                            len(transformed_table.col_ids)
                          * len(transformed_table.row_ids)
                    )
                elif self.normalizeMode == 'quotients':
                    numIterations += len(transformed_table.col_ids) + (
                            len(transformed_table.col_ids)
                          * len(transformed_table.row_ids)
                    )
                elif self.normalizeMode == 'TF-IDF':
                    numIterations += len(transformed_table.col_ids)
            elif self.convert:
                numIterations += len(transformed_table.col_ids)
            if self.reformat:
                numIterations += len(transformed_table.row_ids)
            progressBar = OWGUI.ProgressBar(self, numIterations)

            # Sort if needed...
            if self.sortRows or self.sortCols:
                rows = {'reverse': self.sortRowsReverse}
                cols = {'reverse': self.sortColsReverse}
                if self.sortRows:
                    if self.sortRowsKeyId == 0:
                        rows['key_id'] = transformed_table.header_col['id']
                    else:
                        rows['key_id'] = transformed_table.col_ids[
                                self.sortRowsKeyId - 1
                        ]
                if self.sortCols:
                    if self.sortColsKeyId == 0:
                        cols['key_id'] = transformed_table.header_row['id']
                    else:
                        cols['key_id'] = transformed_table.row_ids[
                                self.sortColsKeyId - 1
                        ]
                transformed_table = transformed_table.to_sorted(rows, cols)

            # Transpose if needed...
            if self.transpose:
                transformed_table = transformed_table.to_transposed()

            # Normalize if needed...
            if self.normalize:
                transformed_table = transformed_table.to_normalized(
                        self.normalizeMode,
                        self.normalizeType.lower(),
                        progressBar.advance
                )

            # Convert if needed...
            elif self.convert:
                if self.conversionType == 'document frequency':
                    transformed_table=transformed_table.to_document_frequency(
                            progress_callback = progressBar.advance
                    )
                elif self.conversionType == 'association matrix':
                    transformed_table=transformed_table.to_association_matrix(
                            bias              = self.associationBias,
                            progress_callback = progressBar.advance
                    )

            # Reformat if needed...
            if self.reformat:
                if self.unweighted:
                    transformed_table = transformed_table.to_flat(
                            progress_callback = progressBar.advance
                    )
                else:
                    transformed_table = transformed_table.to_weighted_flat(
                            progress_callback = progressBar.advance
                    )

            progressBar.finish()

        self.transformed_table = transformed_table

        orangeTable = transformed_table.to_orange_table(
                encoding = self.conversionEncoding,
        )

        self.send('Orange table', orangeTable)
        self.send('Textable table', transformed_table)
        if self.displayAdvancedSettings:
            colDelimiter         = self.colDelimiter
            includeOrangeHeaders = self.includeOrangeHeaders
        else:
            colDelimiter         = '\t'
            includeOrangeHeaders = False
        outputString = transformed_table.to_string(
                output_orange_headers = includeOrangeHeaders,
                col_delimiter         = colDelimiter,
        )
        self.segmentation.update(outputString, label=u'table')
        self.send('Segmentation', self.segmentation)
        message = 'Table has %i rows and %i columns.' % (
                len(transformed_table.row_ids),
                len(transformed_table.col_ids)+1,
        )
        self.infoBox.dataSent(message)
        self.sendButton.resetSettingsChangedFlag()


    def exportFile(self):
        """Display a FileDialog and save table to file"""
        if getattr(self, self.sendButton.changedFlag):
            QMessageBox.warning(
                    None,
                    'Textable',
                    'Input data and/or settings have changed.\nPlease click '
                    "'Send' or check 'Send automatically' before proceeding.",
                    QMessageBox.Ok
            )
            return
        filePath = unicode(
                QFileDialog.getSaveFileName(
                        self,
                        u'Export Table to File',
                        self.lastLocation,
                )
        )
        if filePath:
            self.lastLocation = os.path.dirname(filePath)
            outputFile = codecs.open(
                    filePath,
                    encoding    = self.exportEncoding,
                    mode        = 'w',
                    errors      = 'xmlcharrefreplace',
            )
            outputFile.write(self.segmentation[0].get_content())
            outputFile.close()
            QMessageBox.information(
                    None,
                    'Textable',
                    'Table successfully exported to file.',
                    QMessageBox.Ok
            )


    def copyToClipboard(self):
        """Copy output table to clipboard"""
        if getattr(self, self.sendButton.changedFlag):
            QMessageBox.warning(
                    None,
                    'Textable',
                    'Input data and/or settings have changed.\nPlease click '
                    "'Send' or check 'Send automatically' before proceeding.",
                    QMessageBox.Ok
            )
            return
        QApplication.clipboard().setText(self.segmentation[0].get_content())
        QMessageBox.information(
                None,
                'Textable',
                'Table successfully copied to clipboard.',
                QMessageBox.Ok
        )


    def updateGUI(self):

        """Update GUI state"""
        if not self.table:
            if self.displayAdvancedSettings:
                self.transformBox.setDisabled(True)
                self.exportButton.setDisabled(True)
                self.copyButton.setDisabled(True)
            else:
                self.basicExportButton.setDisabled(True)
                self.basicCopyButton.setDisabled(True)
        else:
            if self.displayAdvancedSettings:
                self.transformBox.setDisabled(False)
                self.exportButton.setDisabled(False)
                self.copyButton.setDisabled(False)
            else:
                self.basicExportButton.setDisabled(False)
                self.basicCopyButton.setDisabled(False)

            if self.displayAdvancedSettings:
                self.normalizeTypeCombo.setDisabled(True)
                self.associationBiasCombo.setDisabled(True)
                if self.sortRows:
                    self.sortRowsKeyIdCombo.clear()
                    self.sortRowsKeyIdCombo.addItem(
                        self.table.header_col['id']
                    )
                    for col_id in self.table.col_ids:
                        self.sortRowsKeyIdCombo.addItem(col_id)
                    self.sortRowsKeyId = self.sortRowsKeyId or 0
                    self.sortRowsKeyIdCombo.setDisabled(False)
                    self.sortRowsReverseCheckBox.setDisabled(False)
                else:
                    self.sortRowsKeyIdCombo.setDisabled(True)
                    self.sortRowsKeyIdCombo.clear()
                    self.sortRowsReverseCheckBox.setDisabled(True)

                if self.sortCols:
                    self.sortColsKeyIdCombo.clear()
                    self.sortColsKeyIdCombo.addItem(
                        self.table.header_row['id']
                    )
                    if isinstance(self.table.row_ids[0], (int, long)):
                        tableRowIds = [str(i) for i in self.table.row_ids]
                    else:
                        tableRowIds = self.table.row_ids
                    for row_id in tableRowIds:
                        self.sortColsKeyIdCombo.addItem(row_id)
                    self.sortColsKeyId = self.sortColsKeyId or 0
                    self.sortColsKeyIdCombo.setDisabled(False)
                    self.sortColsReverseCheckBox.setDisabled(False)
                else:
                    self.sortColsKeyIdCombo.setDisabled(True)
                    self.sortColsKeyIdCombo.clear()
                    self.sortColsReverseCheckBox.setDisabled(True)

                # Crosstab...
                if isinstance(self.table, Crosstab):
                    self.transposeCheckBox.setDisabled(False)
                    self.transformBoxLine4.setDisabled(False)
                    self.transformBoxLine5.setDisabled(False)
                    self.transformBoxLine6.setDisabled(False)
                    self.normalizeModeCombo.setDisabled(True)
                    self.normalizeTypeCombo.setDisabled(True)
                    self.conversionTypeCombo.setDisabled(True)
                    self.associationBiasCombo.setDisabled(True)
                    self.reformatCheckbox.setDisabled(False)
                    self.unweightedCheckbox.setDisabled(False)
                    # IntPivotCrosstab...
                    if isinstance(self.table, IntPivotCrosstab):
                        # Normalize...
                        if self.normalize:
                            self.normalizeModeCombo.setDisabled(False)
                            self.transformBoxLine5.setDisabled(True)
                            self.convert = False
                            self.unweightedCheckbox.setDisabled(True)
                            self.unweighted = False
                            if (
                                    self.normalizeMode == u'rows'
                                or  self.normalizeMode == u'columns'
                            ):
                                self.normalizeTypeCombo.setDisabled(False)
                        # Convert...
                        elif self.convert:
                            self.conversionTypeCombo.setDisabled(False)
                            self.transformBoxLine4.setDisabled(True)
                            self.normalize = False
                            self.unweightedCheckbox.setDisabled(True)
                            self.unweighted = False
                            if self.conversionType == 'association matrix':
                                self.associationBiasCombo.setDisabled(False)
                        # Reformat...
                        if self.reformat:
                            # Flat crosstab
                            if self.unweighted:
                                self.transformBoxLine4.setDisabled(True)
                                self.normalize = False
                                self.transformBoxLine5.setDisabled(True)
                                self.convert = False
                        else:
                            self.unweightedCheckbox.setDisabled(True)
                    # Not IntPivotCrosstab...
                    else:
                        self.transformBoxLine4.setDisabled(True)
                        self.normalize = False
                        self.transformBoxLine5.setDisabled(True)
                        self.convert = False
                    # PivotCrosstab...
                    if isinstance(self.table, PivotCrosstab):
                        self.transposeCheckBox.setDisabled(False)
                # Not Crosstab...
                else:
                    self.transposeCheckBox.setDisabled(True)
                    self.transpose = False
                    self.transformBoxLine4.setDisabled(True)
                    self.normalize = False
                    self.transformBoxLine5.setDisabled(True)
                    self.convert = False
                    self.transformBoxLine6.setDisabled(True)
                    self.reformat = False

        self.advancedSettings.setVisible(self.displayAdvancedSettings)


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
    from LTTL.Table import *
    appl = QApplication(sys.argv)
    ow   = OWTextableConvert()
    ow.show()
    t = IntPivotCrosstab(
            ['c', 'a', 'b'],
            ['B', 'C', 'A'],
            {
                    ('a', 'A'): 2,
                    ('a', 'B'): 3,
                    ('b', 'A'): 4,
                    ('b', 'C'): 2,
                    ('c', 'A'): 1,
                    ('c', 'B'): 4,
                    ('c', 'C'): 1,
            },
            header_row = {
                    'id':   u'__unit__',
                    'type': u'discrete',
            },
            header_col = {
                    'id':   u'__context__',
                    'type': u'discrete',
            },
            missing = 0
    )
    ow.inputData(t)
    appl.exec_()
    ow.saveSettings()
