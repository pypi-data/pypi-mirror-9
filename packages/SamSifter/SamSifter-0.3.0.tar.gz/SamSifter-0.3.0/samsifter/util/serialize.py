# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 09:54:18 2015

@author: aldehoff
"""
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (FilterParameter, FilterThreshold,
                                        FilterFilepath, FilterSwitch)
from samsifter.version import samsifter_version


class WorkflowSerializer():
    """
    (De-)Serializing workflow data for permanent storage.
    """

    @classmethod
    def serialize(cls, workflow, filename):
        return cls.tree_to_file(cls.workflow_to_xml(workflow), filename)

    @classmethod
    def deserialize(cls, workflow, filename):
        return cls.workflow_from_xml(cls.tree_from_file(filename), workflow)

    @classmethod
    def tree_from_file(cls, filename):
        """
        Initialize element tree from XML file.
        """
        return ET.ElementTree(file=filename)

    @classmethod
    def tree_to_file(cls, tree, filename):
        """
        Write element tree to XML file.
        """
        return tree.write(filename, xml_declaration=True, encoding='UTF-8',
                          method='xml')

    @classmethod
    def workflow_to_xml(cls, workflow):
        """
        Generate XML tree from workflow container.
        """
        if workflow is None:
            return None

        root = ET.Element("workflow")

        in_file = ET.SubElement(root, 'filepath')
        in_file.set('type', 'input')
        in_file.text = workflow.getInFilename()

        out_file = ET.SubElement(root, 'filepath')
        out_file.set('type', 'output')
        out_file.text = workflow.getOutFilename()

        filters = ET.SubElement(root, 'pipeline')
        for position, fltr in enumerate(workflow.getModel().iterate_items()):
            elem = ET.SubElement(filters, 'tool')
            elem.set('index', str(position))
            elem.set('type', 'filter')
            elem.set('name', str(fltr.text()))
            elem.set('desc', str(fltr.desc))
            elem.set('command', str(fltr.command))
            elem.set('icon_path', str(fltr.icon_path))

            # store input/output restrictions
            elem.set('input_format', str(fltr.get_input_format()))
            elem.set('input_sorting', str(fltr.get_input_sorting()))
            elem.set('input_compression', str(fltr.get_input_compression()))
            elem.set('output_format', str(fltr.get_output_format()))
            elem.set('output_sorting', str(fltr.get_output_sorting()))
            elem.set('output_compression', str(fltr.get_output_compression()))

#            text = ET.SubElement(elem, 'text')
#            text.text = fltr.text()
#
#            desc = ET.SubElement(elem, 'desc')
#            desc.text = fltr.desc
#
#            command = ET.SubElement(elem, 'command')
#            command.text = fltr.command

#            # Testing automatic escaping of XML characters (works)
#            escape_test = ET.SubElement(elem, 'escape_test')
#            garbage = '$!@#$#@!%><>?////.,""'
#            escape_test.text = garbage
#            elem.set('test2', garbage)

            for param in fltr.parameters:
                sub = ET.SubElement(elem, 'parameter')
                if isinstance(param, FilterThreshold):
                    sub.set('type', 'threshold')
                    sub.set('minimum', str(param.getMinimum()))
                    sub.set('maximum', str(param.getMaximum()))
                    sub.set('precision', str(param.getPrecision()))
                    sub.set('unit', str(param.getUnit()))
                elif isinstance(param, FilterFilepath):
                    sub.set('type', 'filepath')
                    sub.set('to_open', str(param.to_open))
                    for idx, ext in enumerate(param.getExtensions()):
                        suffix = ET.SubElement(sub, 'suffix')
                        suffix.set('extension', ext)
                        suffix.set('index', str(idx))
                elif isinstance(param, FilterSwitch):
                    sub.set('type', 'switch')
                    for idx, opt in enumerate(param.getOptions()):
                        option = ET.SubElement(sub, 'option')
                        option.set('value', str(opt))
                        option.set('index', str(idx))
                        if isinstance(opt, bool):
                            option.set('type', 'bool')
                        elif isinstance(opt, int):
                            option.set('type', 'int')
                        elif isinstance(opt, float):
                            option.set('type', 'float')
                        elif isinstance(opt, str):
                            option.set('type', 'str')
                elif isinstance(param, FilterParameter):
                    sub.set('type', 'parameter')
                sub.set('name', param.text)
                sub.set('desc', param.getDesc())
                sub.set('cli_name', str(param.getCliName()))
                sub.set('required', str(param.isRequired()))
                sub.set('active', str(param.isActive()))
#                sub.set('value', str(param.getValue()))
#                sub.set('default', str(param.getDefault()))

                # multi-type attributes (can be None, str, int, float, bool)
                value = ET.SubElement(sub, 'value')
                typed_value = param.getValue()
                type_string = cls.determine_type(typed_value)
                value.set('type', type_string)
                value.text = str(typed_value)

                default = ET.SubElement(sub, 'default')
                typed_default = param.getDefault()
                type_string = cls.determine_type(typed_default)
                default.set('type', type_string)
                default.text = str(typed_default)

        tree = ET.ElementTree(root)
        return tree

    @classmethod
    def workflow_from_xml(cls, tree, wf):
        """
        Generate workflow from XML element tree.
        """
        if tree is None:
            return None

        root = tree.getroot()
        wf.clear()

        # retrieve input and output filepaths
        for filepath in root.iter(tag='filepath'):
            if filepath.attrib['type'] == 'input':
                wf.setInFilename(filepath.text)
            if filepath.attrib['type'] == 'output':
                wf.setOutFilename(filepath.text)

        # retrieve filter pipeline
        for pipeline in root.iter(tag='pipeline'):
            for tool in pipeline.iter(tag='tool'):
                text = cls.singletons(tool.get('name'))
                desc = cls.singletons(tool.get('desc'))
                command = cls.singletons(tool.get('command'))
                icon_path = cls.singletons(tool.get('icon_path'))

                # retrieve input and output restrictions
                input_format = cls.singletons(tool.get('input_format'))
                input_sorting = cls.singletons(tool.get('input_sorting'))
                input_compression = cls.singletons(
                    tool.get('input_compression'))
                output_format = cls.singletons(tool.get('output_format'))
                output_sorting = cls.singletons(tool.get('output_sorting'))
                output_compression = cls.singletons(
                    tool.get('output_compression'))

                item = FilterItem(text, desc, icon_path)
                item.setCommand(command)
                item.set_input_format(input_format)
                item.set_input_sorting(input_sorting)
                item.set_input_compression(input_compression)
                item.set_output_format(output_format)
                item.set_output_sorting(output_sorting)
                item.set_output_compression(output_compression)

                for param in tool.iter(tag='parameter'):
                    param_name = param.get('name')
                    param_desc = param.get('desc')
                    cli_name = param.get('cli_name')
                    required = cls.singletons(param.get('required'))
                    active = cls.singletons(param.get('active'))

#                    # debugging missing checkbox states
#                    print("setting active status: input %s (%s) is mangled "
#                          "to %s (%s)"
#                          % (param.get('active'), type(param.get('active')),
#                             active, type(active)), file=sys.stderr)

                    # retrieve value and desc, cast according to type
                    for val in param.iter(tag='value'):
                        val_type = val.get('type')
                        if val_type == 'None':
                            value = cls.singletons(val.text)
                        elif val_type == 'bool':
                            value = cls.singletons(val.text)
                        elif val_type == 'int':
                            value = int(cls.singletons(val.text))
                        elif val_type == 'float':
                            value = float(cls.singletons(val.text))
                        elif val_type == 'str':
                            value = str(cls.singletons(val.text))

                    for dflt in param.iter(tag='default'):
                        dflt_type = dflt.get('type')
                        if dflt_type == 'None':
                            default = cls.singletons(dflt.text)
                        elif dflt_type == 'bool':
                            default = cls.singletons(dflt.text)
                        elif dflt_type == 'int':
                            default = int(cls.singletons(dflt.text))
                        elif dflt_type == 'float':
                            default = float(cls.singletons(dflt.text))
                        elif dflt_type == 'str':
                            default = str(cls.singletons(dflt.text))

                    # check for parameter type, initialise subclasses
                    param_type = param.get('type')
                    parameter = None
                    if param_type == 'threshold':
                        minimum = float(cls.singletons(param.get('minimum')))
                        maximum = float(cls.singletons(param.get('maximum')))
                        precision = int(cls.singletons(param.get('precision')))
                        unit = cls.singletons(param.get('unit'))

                        parameter = FilterThreshold(param_name, param_desc,
                                                    cli_name, unit, required,
                                                    active)
                        parameter.setMinimum(minimum)
                        parameter.setMaximum(maximum)
                        parameter.setPrecision(precision)
                    elif param_type == 'filepath':
                        to_open = cls.singletons(param.get('to_open'))
                        extensions = []
                        for sffx in param.iter('suffix'):
                            extensions.append(cls.singletons(
                                              sffx.get('extension')))
                        if len(extensions) <= 0:
                            extensions = None

                        parameter = FilterFilepath(param_name, param_desc,
                                                   cli_name, extensions,
                                                   to_open, required, active)
                    elif param_type == 'switch':
                        options = []
                        for choice in param.iter(tag='option'):
                            opt_type = choice.get('type')
                            if opt_type == 'None':
                                option = cls.singletons(choice.get('value'))
                            elif opt_type == 'bool':
                                option = cls.singletons(choice.get('value'))
                            elif opt_type == 'int':
                                option = int(cls.singletons(
                                             choice.get('value')))
                            elif opt_type == 'float':
                                option = float(cls.singletons(
                                               choice.get('value')))
                            elif opt_type == 'str':
                                option = cls.singletons(choice.get('value'))
                            options.append(option)

                        if len(options) <= 0:
                            options = None

                        parameter = FilterSwitch(param_name, param_desc,
                                                 cli_name, options, required,
                                                 active)
                    elif param_type == 'parameter':
                        # no special parameters for this base class
                        parameter = FilterParameter(param_name, param_desc,
                                                    cli_name, required, active)
                    else:
                        print("failed to determine parameter type",
                              file=sys.stderr)
                        continue

                    parameter.setValue(value)
                    parameter.setDefault(default)
                    # set active to override prior setting of value
                    parameter.setActive(active)

                    item.addParameter(parameter)
                wf.getModel().insertItem(item)
        return wf

    @classmethod
    def singletons(cls, value):
        """
        Replace 'None', 'False' and 'True' strings with actual values.
        """
        if value == 'None':
            return None
        elif value == 'False':
            return False
        elif value == 'True':
            return True
        else:
            return value

    @classmethod
    def determine_type(cls, value):
        """
        Determine type of a typed value and return it as string.
        """
        if value is None:
            return 'None'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        else:
            return 'str'

    @classmethod
    def prettify(cls, elem, indent="  "):
        """
        Return a pretty-printed XML string for the Element.
        """
        rough_string = ET.tostring(elem, encoding='UTF-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent)

    @classmethod
    def tree_to_str(cls, tree, pretty=False):
        """
        Convert XML element tree to optionally indented text string.
        """
        root = tree.getroot()
        if pretty:
            return WorkflowSerializer.prettify(root)
        else:
            return ET.tostring(root, encoding='UTF-8', method='xml')


def main(argv):
    """
    Test of workflow serialization and deserialization.
    """
    outfilename = "/home/aldehoff/sandbox/serial_test.xml"
#    infilename = "/home/aldehoff/sandbox/serial_test_modified.xml"
    infilename = "/home/aldehoff/sandbox/serial_test2.xml"

    from samsifter.util.testing import create_workflow
    workflow = create_workflow()

    # serialization
#    tree = WorkflowSerializer.workflow_to_xml(workflow)
#    print(WorkflowSerializer.tree_to_str(tree, pretty=True))
#    result = WorkflowSerializer.tree_to_file(tree, outfilename)
    WorkflowSerializer.serialize(workflow, outfilename)

    print("*" * 40)

    # deserialization
#    tree2 = WorkflowSerializer.tree_from_file(infilename)
#    print(WorkflowSerializer.tree_to_str(tree2, pretty=True))
#    WorkflowSerializer.workflow_from_xml(tree2, workflow)
    WorkflowSerializer.deserialize(workflow, infilename)
    workflow.setFilename(infilename)

    # inspection of workflow for changes (filename should be in another dir)
    print(repr(workflow))

    exit()


if __name__ == '__main__':
    main(sys.argv)
