import xml.etree.ElementTree as ET
import subprocess
from itertools import chain

__all__ = ["Parameter", "ParameterGroup", "Executable", "XMLArgumentNotSupportedByExecutable"]


class ParameterGroup(list):
    """A list of multiple :py:class:`Parameter`.

    XML: Starts a group of parameters.
    """

    def __init__(self, label=None, description=None, advanced=None, parameters=None):
        self.parameters = parameters
        """

        :type: list[Parameter]
        """

        self.label = label
        """Label text of the parameter section
                            <xsd:documentation>A short string used as the label for this group.</xsd:documentation>

        :type: str
        """

        self.description = description
        """Description text of this parameter section
                            <xsd:documentation>A description of this parameter group.</xsd:documentation>

        :type: str
        """
        self.advanced = advanced
        """marks if this paramter section is marked as advanced.

        XML::
            This value is usually used in GUI generators to decide
            if the parameters belonging to this group should be initially hidden to the user or not.

        :type: bool
        """

    def as_xml(self):
        root = ET.Element("parameters", {'advanced': str(self.advanced)})
        ET.SubElement(root, "label").text = str(self.label)
        ET.SubElement(root, "description").text = str(self.description)

        for p in self.parameters:
            root.append(p.as_xml())

        return root

    def __repr__(self):
        return "ParameterGroup(label=%(label)r, description=%(description)r, advanced=%(advanced)r, parameters=%(parameters)s )" % \
               self.__dict__

    def __getitem__(self, item):
        if isinstance(item, str):
            for p in self:
                if p.name == item:
                    return p
            raise KeyError("Could not find Parameter %s" % item)
        else:
            return self.parameters.__getitem__(item)

    def __setitem__(self, key, value):
        return self.parameters.__setitem__(key, value)

    def __setslice__(self, i, j, sequence):
        return self.parameters.__setslice__(i, j, sequence)

    def __iter__(self):
        return self.parameters.__iter__()

    def __getslice__(self, i, j):
        return self.parameters.__getslice__(i, j)

    def __eq__(self, other):
        if isinstance(other, ParameterGroup) and other is not None:
            try:
                l = True
                for p in self.parameters:
                    po = other[p.name]
                    l = l and po == p

                for p in other.parameters:
                    po = self[p.name]
                    l = l and po == p

            except KeyError:
                l = False

            return l and self.advanced == other.advanced and self.label == other.label and \
                   self.description == other.description
        else:
            return False


class Parameter(object):
    """Represents a CLI parameter.

    You must either specify "flag" or "longflag" (or both) or "index".
    """

    XML_FIELDS = ('name', 'default', 'description', 'channel',
                  'index', 'label', 'longflag')

    def __init__(self, name, type, default, description=None, channel=None, values=None,
                 flag=None, index=None, label=None, longflag=None, file_ext=None):
        self.name = name
        """The unique name (within this module) of the parameter. This is only used internally.
        Pattern::
            [_a-zA-Z][_a-zA-Z0-9]*

        :type: str
        """

        self.type = type
        """type of this parameter (interger, float, ... )

        :type: str
        """

        self.default = default
        """A default value for the parameter. The default must be a type that is compatible
                        with the
                        parameter type. The vector parameters are specified as comma separated values of the atomic
                        parameter type.

        :type: str
        """

        self.description = description
        """A brief description of the parameter.

        :type: str
        """

        self.hidden = False
        """not documentated


        :type: bool
        """

        self.channel = channel
        """Specifies whether the parameter is an input or output parameter. Output
                        parameters can for
                        example specify file paths where to write output data (e.g. using the "image" element) or they
                        can represent
                        "simple return parameters", indicated by providing an "index" of 1000. The current values of
                        suche simple return
                        parameters are not passed to the module during its execution. Rather, the module itself reports
                        these parameter
                        values during execution.


        :type: str
        """

        self.values = values
        """Enumerable values


        :type: str
        """

        self.flag = flag
        """

        :type: str
        """

        self.label = label
        """ label for parameter.


        :type: str
        """

        self.index = index
        """An integer starting at 0, that specifies a module argument that has no flags.

        The index value 1000 is reserved as a marker for output parameters (see the "channel" element) to indicate that this parameter is used to return results during the execution of this module and does not need to be set.

        :type: int
        """

        self.longflag = longflag
        """long flag

        :type: str
        """

        self.file_ext = file_ext
        """acceptable file extensions

        :type: str
        """

    def __repr__(self):
        return "Parameter(name=%(name)r, type=%(type)r, default=%(default)r, " \
               "description=%(description)r, channel=%(channel)r, values=%(values)r," \
               "index=%(index)r, label=%(label)r, longflag=%(longflag)r, file_ext=%(file_ext)r)" % self.__dict__


    def __eq__(self, other):
        if isinstance(other, Parameter):
            return self.__dict__ == other.__dict__
        return False

    def as_xml(self):
        root = ET.Element(self.type, {'fileExtension': self.file_ext} if self.file_ext else {})

        for attrib in Parameter.XML_FIELDS:
            e = ET.SubElement(root, attrib)
            e.text = str(getattr(self, attrib))

        return root

    @staticmethod
    def from_xml_node(xml_node):
        """constructs a CLI.Parameter from an xml node.
        :param xml_node:
        :type xml_node: xml.etree.ElementTree.Element
        :rtype: Executable.Parameter
        :return:
        """

        def gather_enum_values():
            l = []
            for element in xml_node.iterfind('element'):
                l.append(element.text)
            return l

        name = xml_node.findtext("name")
        type = xml_node.tag

        if type in ("label", "description"): return None

        default = xml_node.findtext("default")

        longflag = xml_node.findtext('longflag')

        if default:
            default = default.replace('"', '').replace("'", '')

        index = xml_node.findtext('index')

        label = xml_node.findtext('label') or name or longflag

        doc = xml_node.findtext('description')

        values = gather_enum_values()

        channel = xml_node.findtext('channel')

        file_ext = xml_node.attrib.get('fileExtensions', None)

        return Parameter(name, type, default, doc, channel, values=values, index=index, label=label,
                         longflag=longflag, file_ext=file_ext)


class Executable(object):
    """Represents an CLI executable.

    The root element for each module XML description. It must contain
                at least one "parameters" element.

    """

    def __init__(self, xml=None, executable=None, category=None, title=None, description=None, version=None,
                 license=None, contributor=None, acknowledgements=None, documentation_url=None,
                 parameter_groups=None):

        """Creates a model about every fact from the CLI XML
        :param xml:
        :type xml: xml.etree.ElementTree.ElementTree
        :return:
        """

        self._xml = xml
        """XML datastructure

        :type: xml.etree.ElementTree.ElementTree
        """

        self.executable = executable
        """Path to the executable

        :type: str
        """

        self.parameter_groups = parameter_groups or []
        """list of :py:class:`Parameters`

        :type: list[Parameters]
        """

        self.category = category
        """Classifies the module (e.g. Filtering, Segmentation). The value can be a dot separated string to create category hierarchies.

        :type: str
        """

        self.title = title
        """A human-readable name for the module

        :type: str
        """

        self.description = description
        """A detailed description of the modules purpose

        :type: str
        """

        self.version = version
        """The modules version number.

        A suggested format is: `major.minor.patch.build.status`
        * vc: version controlled (pre-alpha), build can be a serial revision number, if any (like svn might have).
        * a: alpha
        * b: beta
        * rc: release candidate
        * fcs: first customer ship

        :type: str
        """

        self.license = license
        """The type of license or a URL containing the license
        :type: str
        """

        self.contributor = contributor
        """The author(s) of the command line module
        :type: str
        """

        self.documentation_url = documentation_url
        """A URL pointing to a documentation or home page of the module.

        :type: str
        """

        self.acknowledgements = acknowledgements
        """Acknowledgements for funding agency, employer, colleague, etc

        :type: str
        """

    XML_FIELDS = ('version', 'description', 'title', 'category', 'license',
                  'contributor', 'documentation_url', 'acknowledgements')

    def as_xml(self):
        root = ET.Element("executable")

        for attrib in self.XML_FIELDS:
            se = ET.SubElement(root, attrib)
            se.text = getattr(self, attrib)

        for element in self.parameter_groups:
            root.append(element.as_xml())

        return root

    def __iter__(self):
        """Iterate over all parameters in this executable
        :returns: Iterable
        """
        return chain(*self.parameter_groups)


    def __repr__(self):
        return "Executable(executable=%(executable)r, category=%(category)r, title=%(title)r, description=%(description)r, version=%(version)r," \
               "license=%(license)r, contributor=%(contributor)r, acknowledgements=%(acknowledgements)r, documentation_url=%(documentation_url)r," \
               "parameter_groups=%(parameter_groups)r)" % self.__dict__


    def cmdline(self, **kwargs):
        """Generates a valid command line call for the executable given by call arguments in `kwargs`
        :param kwargs: values to call the executable
        :return: the command line
        :rtype: list
        """

        args = [self.executable]
        indexed_args = []

        for key, value in kwargs.iteritems():
            parameter = self[key]
            if value != parameter.default:
                if parameter.longflag:  # use longflag where possible
                    args.append("--%s" % parameter.longflag)
                    args.append(str(value))
                elif parameter.flag:
                    args.append("-%s" % parameter.flag)
                    args.append(str(value))
                elif parameter.index:
                    indexed_args.insert(int(parameter.index), str(value))

        return args + indexed_args

    def __getitem__(self, item):
        for p in self:
            if p.name == item:
                return p
        raise KeyError("Parameter %s not found" % item)

    def __eq__(self, other):
        if isinstance(other, Executable) and other is not None:
            return all((other.executable == self.executable,
                        other.version == self.version,
                        other.acknowledgements == self.acknowledgements,
                        other.contributor == self.contributor,
                        other.documentation_url == self.documentation_url,
                        other.description == self.description,
                        other.title == self.title,
                        other.parameter_groups == self.parameter_groups))
        else:
            return False

    @staticmethod
    def from_exe(executable):
        """

        :param executable:
        :return:
        """
        command = "%s --xml" % executable
        sp = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        sp.wait()

        if sp.returncode == 0:
            xml = sp.stdout.read()
            tree = ET.fromstring(xml)
            e = Executable.from_etree(tree)
            e.executable = executable
            return e
        else:
            raise XMLArgumentNotSupportedByExecutable("called %s got %s" % (command, sp.returncode))

    @staticmethod
    def from_xml(filename):
        """

        :param filename:
        :return:
        """
        tree = ET.parse(filename)
        return Executable.from_etree(tree)

    @staticmethod
    def from_etree(tree):
        """Constructs an executable form a given ElementTree structure.

        :param tree:
        :type tree: xml.etree.ElementTree.ElementTree

        :rtype: Executable
        """
        exe = Executable(tree)

        exe.category = tree.findtext('category')
        exe.version = tree.findtext('version')
        exe.title = tree.findtext('title') or exe.name
        exe.description = tree.findtext('description')
        exe.license = tree.findtext('license') or "unknown"
        exe.contributor = tree.findtext('contributor')

        for ps in tree.iterfind("parameters"):
            assert isinstance(ps, ET.Element)
            paras = ParameterGroup(
                ps.findtext("label"),
                ps.findtext("description"),
                ps.attrib.get('advanced', "false") == "true",
                filter(lambda x: x is not None,
                       map(Parameter.from_xml_node, list(ps))))

            exe.parameter_groups.append(paras)

            return exe


class XMLArgumentNotSupportedByExecutable(Exception):
    """

    """
    pass