import traceback, re, ast, importlib, inspect
from inspect import signature

SEQDIAG_RETURN_TAG = ":seqdiag_return"
SEQDIAG_SELECT_METHOD_TAG = ":seqdiag_select_method"

SEQDIAG_RETURN_TAG_PATTERN = r"%s (.*)" % SEQDIAG_RETURN_TAG
SEQDIAG_SELECT_METHOD_TAG_PATTERN = r"%s(.*)" % SEQDIAG_SELECT_METHOD_TAG
PYTHON_FILE_AND_FUNC_PATTERN = r"([\w:\\]+\\)(\w+)\.py, line \d* in (.*)"
FRAME_PATTERN = r"(?:<FrameSummary file ([\w:\\,._\s]+)(?:>, |>\]))"

INDEX_MODULE_NAME = 0
INDEX_CLASS_NAME = 1
INDEX_METHOD_NAME = 2
INDEX_METHOD_SIGNATURE = 3
INDEX_METHOD_RETURN_DOC = 4

INDENT = '\t'


class FlowEntry:
    def __init__(self, fromClass='', toClass='', method='', signature='', returnType=''):
        self.fromClass = fromClass
        self.toClass = toClass
        self.method = method
        self.signature = signature
        self.returnType = returnType


    def __eq__(self, other):
        return self.fromClass == other.fromClass and \
               self.toClass == other.toClass and \
               self.method == other.method and \
               self.signature == other.signature and \
               self.returnType == other.returnType


    def match(self, targetClass, method):
        '''
        Returns True if the passed class/method are equal to the toClass and method of
        the flow entry.

        :param targetClass:
        :param method:
        :return:
        '''
        return self.toClass == targetClass and \
               self.method == method


    def __str__(self):
        return "{}, {}, {}, {}, {}".format(self.fromClass, self.toClass, self.method, self.signature, self.returnType)


class RecordedFlowPath:
    def __init__(self):
        self.list = []


    def addIfNotIn(self, newFlowEntry):
        if self.list == []:
            self.list.append(newFlowEntry)
            return

        for flowEntry in self.list:
            if flowEntry == newFlowEntry:
                return

        self.list.append(newFlowEntry)


    def stripFlowBeforeEntryPoint(self, entryClass, entryMethod):
        '''
        This method removes from the recorded flow path all flow entries which are
        before the sequence diagram entry point, defined by the passed entry class name
        and entry method. In case the passed entry point is not in the recorded flow
        path, nothing is stripped.

        IMPORTANT: the passed entryClass is matched against the toClass of the flow entries !

        :param entryClass:
        :param entryMethod:
        :return:
        '''
        index = 0
        entryPointFound = False

        for flowEntry in self.list:
            if flowEntry.match(entryClass, entryMethod):
                entryPointFound = True
                break
            else:
                index += 1

        if entryPointFound:
            self.list = self.list[index:]


    def size(self):
        return len(self.list)


    def is_empty(self):
        return self.size() == 0


    def __str__(self):
        outStr = ''

        for flowEntry in self.list:
            outStr += str(flowEntry) + '\n'

        return outStr


class SeqDiagCommandStack:
    '''
    This list stores the embeded calls used to build the sequence diagram commands. It is
    used to build the return commands of the diagram.
    '''


    def __init__(self):
        self.stack = []


    def pop(self):
        if self.is_empty():
            return None
        else:
            return self.stack.pop()


    def push(self, flowEntry):
        '''
        Push on the list a 2 elements list, the first element being the couple <class name>.<method name>
        and the second one being the string denoting the information returned to the caller by the method.
        :param flowEntry:
        :return:
        '''
        classMethodStr = self._buildClassMethodStr(flowEntry)
        self.stack.append([classMethodStr, flowEntry[INDEX_METHOD_RETURN_DOC]])

        return self.stack


    def _buildClassMethodStr(self, flowEntry):
        '''
        Build the class method string which is the first element of the list pushed in
        the SeqDiagCommandStack.
        :param flowEntry:
        :return:
        '''
        return "{}.{}".format(flowEntry[INDEX_CLASS_NAME], flowEntry[INDEX_METHOD_NAME])


    def peek(self):
        if self.is_empty():
            return None
        else:
            return self.stack[-1]


    def size(self):
        return len(self.stack)


    def is_empty(self):
        return self.size() == 0


    def contains(self, flowEntry):
        '''
        Return True if the passed flow entry is in the SeqDiagCommandStack.
        :param flowEntry:
        :return:
        '''
        classMethodStr = self._buildClassMethodStr(flowEntry)

        for entry in self.stack:
            if entry[0] == classMethodStr:
                return True

        return False


class SeqDiagBuilder:
    '''
    This class contains a static utility methods used to build a sequence diagram from the
    call list as at the point in the python code were it is called.

    To build the diagram, type seqdiag -Tsvg list.txt in a command line window.
    This build a svg file which can be displayed in a browsxer.
    '''

    recordedFlowPath = RecordedFlowPath()
    sequDiagWarningList = []
    isBuildMode = False
    seqDiagEntryClass = 'ClassA'
    seqDiagEntryMethod = 'doWork'

    @staticmethod
    def buildCommandFileHeaderSection():
        '''
        This method write the first line of the PlantUML command file,
        adding a header section in case of warnings.
        :return:
        '''
        commandFileHeaderSectionStr = "@startuml\n"

        if len(SeqDiagBuilder.sequDiagWarningList) > 0:
            # building a header containing the warnings
            commandFileHeaderSectionStr += "left header\n<b><font color=red >Warnings</font></b>\n"

            for warning in SeqDiagBuilder.sequDiagWarningList:
                commandFileHeaderSectionStr += "<font color=red>{}</font>\n".format(warning)

            commandFileHeaderSectionStr += "endheader\n\n"

        return commandFileHeaderSectionStr


    @staticmethod
    def createSeqDiaqCommands(actorName):
        '''
        To build the diagram, type java -jar plantuml.jar -tsvg seqdiagcommands.txt in a
        command line window. This build a svg file which can be displayed in a browsxer.

        :param actorName:
        :return:
        '''
        isStackDataAvailable = True

        if len(SeqDiagBuilder.recordedFlowPath) == 0:
            SeqDiagBuilder.issueWarning("No control flow recorded. Seq diag entry point was {}.{}() and isBuildMode was {}".format(SeqDiagBuilder.seqDiagEntryClass, SeqDiagBuilder.seqDiagEntryMethod, SeqDiagBuilder.isBuildMode))
            isStackDataAvailable = False

        indentStr = ''
        seqDiagCommandStr = SeqDiagBuilder.buildCommandFileHeaderSection()

        if isStackDataAvailable:
            classMethodReturnStack = SeqDiagCommandStack()
            seqDiagCommandStr += "\nactor {}\n".format(actorName)

            firstFlowEntry = SeqDiagBuilder.recordedFlowPath[0]
            classMethodReturnStack.push(firstFlowEntry)
            fromClass = actorName
            toClass = firstFlowEntry[INDEX_CLASS_NAME]
            method = firstFlowEntry[INDEX_METHOD_NAME]
            signature = firstFlowEntry[INDEX_METHOD_SIGNATURE]
            seqDiagCommandStr += SeqDiagBuilder.addMessage(fromClass, toClass, method, signature, indentStr)

            for flowEntry in SeqDiagBuilder.recordedFlowPath[1:]:
                if not classMethodReturnStack.contains(flowEntry):
                    classMethodReturnStack.push(flowEntry)
                    fromClass = toClass
                    toClass = flowEntry[INDEX_CLASS_NAME]
                    method = flowEntry[INDEX_METHOD_NAME]
                    signature = flowEntry[INDEX_METHOD_SIGNATURE]
                    indentStr += INDENT
                    seqDiagCommandStr += SeqDiagBuilder.addMessage(fromClass, toClass, method, signature, indentStr)
                else:
                    returnEntry = classMethodReturnStack.pop()
                    fromClass = toClass
                    toClass = returnEntry[INDEX_CLASS_NAME]
                    method = returnEntry[INDEX_METHOD_RETURN_DOC]
                    indentStr -= INDENT
                    seqDiagCommandStr += SeqDiagBuilder.addMessage(fromClass, toClass, method, signature, indentStr)

        with open("c:\\temp\\ess.diag", 'w') as f:
            f.write(seqDiagCommandStr)
        seqDiagCommandStr += "@enduml"
#        print(seqDiagCommandStr)

        return seqDiagCommandStr


    @staticmethod
    def addMessage(fromClass, toClass, method, signature, indentStr):
        return "{}{} -> {}: {}{}\n{}activate {}\n".format(indentStr,
                                                        fromClass,
                                                        toClass,
                                                        method,
                                                        signature,
                                                        indentStr + INDENT,
                                                        toClass)


    @staticmethod
    def addReturnMessage(fromClass, toClass, method, indentStr):
        return "{}{} -> {}: {}{}\n{}\n".format(indentStr,
                                                        fromClass,
                                                        toClass,
                                                        method)

    @staticmethod
    def recordFlow(maxSigArgNum=None, maxSigArgCharLen=None):
        '''
        Records in a class list the control flow information which will be used to build
        the seqdiag creation commands.

        :param maxSigArgNum:        maximum arguments number of a called method
                                    signature
        :param maxSigArgCharLen:    maximum length a method signature can occupy
        :return:
        '''
        if not SeqDiagBuilder.isBuildMode:
            return

        frameListLine = repr(traceback.extract_stack())
        frameList = re.findall(FRAME_PATTERN, frameListLine)

        if frameList:
            fromClass = ''
            for frame in frameList[:-1]: #last line in frameList is the call to this method !
                match = re.match(PYTHON_FILE_AND_FUNC_PATTERN, frame)
                if match:
                    pythonClassFilePath = match.group(1)
                    moduleName =  match.group(2)
                    methodName = match.group(3)
                    with open(pythonClassFilePath + moduleName + '.py', "r") as sourceFile:
                        source = sourceFile.read()
                        parsedSource = ast.parse(source)
                        moduleClassNameList = [node.name for node in ast.walk(parsedSource) if isinstance(node, ast.ClassDef)]
                        instanceList = SeqDiagBuilder.getInstancesForClassSupportingMethod(methodName,
                                                                                           moduleName,
                                                                                           moduleClassNameList)
                        if instanceList == []:
                            continue
                        filteredInstanceList, methodReturnDoc, methodSignature = SeqDiagBuilder.getFilteredInstanceListAndMethodSignatureAndReturnDoc(instanceList, moduleName, methodName)
                        instance = filteredInstanceList[0]
                        if len(filteredInstanceList) > 1:
                            filteredClassNameList = []
                            for filteredInstance in filteredInstanceList:
                                filteredClassNameList.append(filteredInstance.__class__.__name__)
                            SeqDiagBuilder.issueWarning(
                                "More than one class {} found in module {} do support method {}{}. Class {} chosen by default for building the sequence diagram. To override this selection, put tag {} somewhere in the method documentation.".format(str(filteredClassNameList), moduleName, methodName, methodSignature, instance.__class__.__name__,
                                                                                                                                                                                                                                                       SEQDIAG_SELECT_METHOD_TAG))

                        toClass = instance.__class__.__name__
                        flowEntry = FlowEntry(fromClass, toClass, methodName, methodSignature, methodReturnDoc)
                        fromClass = toClass
                        SeqDiagBuilder.recordedFlowPath.addIfNotIn(flowEntry)
            SeqDiagBuilder.recordedFlowPath.stripFlowBeforeEntryPoint(SeqDiagBuilder.seqDiagEntryClass, SeqDiagBuilder.seqDiagEntryMethod)
            print(SeqDiagBuilder.recordedFlowPath)


    @staticmethod
    def stripInformationList(sequDiagInformationList):
        '''
        This methods strip from the passed recordedFlowPath all the calls preceeding
        the sequence diagram entry point.
        :param sequDiagInformationList:
        :return:
        '''
        index = 0

        for entry in sequDiagInformationList:
            if entry[INDEX_CLASS_NAME] == SeqDiagBuilder.seqDiagEntryClass and entry[INDEX_METHOD_NAME] == SeqDiagBuilder.seqDiagEntryMethod:
                break
            else:
                index += 1

        return sequDiagInformationList[index:]



    @staticmethod
    def issueWarning(warningStr):
        SeqDiagBuilder.sequDiagWarningList.append(warningStr)
        print('************* WARNING - ' + warningStr + ' *************')


    @staticmethod
    def getWarningList():
        return SeqDiagBuilder.sequDiagWarningList


    @staticmethod
    def getInstancesForClassSupportingMethod(methodName, moduleName, moduleClassNameList):
        '''
        Returns a list of instances of classes located in moduleName which support the method methodName.
        Normally, the returned list should contain only one instance. If more than one instance are
        returned, which is the case if the module contains a class hierarchy with method methodName
        defined in the base class (and so inherited or overridden by the subclasses) or if the module
        contains two unrelated classes with the same method name, the first encountered class will be
        selected by default, i.e. the first defined class in the module - the root class in case of
        a hierarchy.

        To override this choice, use the tag :seq_diag_select_method in the method documentation.

        :param moduleName:
        :param moduleClassNameList:
        :param methodName:
        :return:
        '''
        instanceList = []

        for className in moduleClassNameList:
            instance = SeqDiagBuilder.instanciateClass(className, moduleName)
            methodTupplesList = inspect.getmembers(instance, predicate=inspect.ismethod)

            for methodTupple in methodTupplesList:
                if methodName == methodTupple[0]:
                    # methodName is a member of className
                    instanceList.append(instance)

        return instanceList


    @staticmethod
    def printSeqDiagInstructions():
        for entry in SeqDiagBuilder.recordedFlowPath:
            lineStr = "{} {}.{}{} <-- {}".format(entry[INDEX_MODULE_NAME], entry[INDEX_CLASS_NAME], entry[INDEX_METHOD_NAME], entry[INDEX_METHOD_SIGNATURE], entry[INDEX_METHOD_RETURN_DOC])
            print(lineStr)


    @staticmethod
    def getSeqDiagInstructionsStr():
        seqDiagInstructionsStr = ''

        for entry in SeqDiagBuilder.recordedFlowPath:
            lineStr = "{} {}.{}{} <-- {}\n".format(entry[0], entry[1], entry[2], entry[3], entry[4])
            seqDiagInstructionsStr += lineStr

        return seqDiagInstructionsStr


    @staticmethod
    def getFilteredInstanceListAndMethodSignatureAndReturnDoc(instanceList, moduleName, methodName):
        '''
        This method returns the passed instance List filtered so that it only contains instances
        supporting the passed methodName. The string associated to the %s tag defined in
        the (selected) method documentation aswell as the (selected) method signature are returned.

        :param instanceList:    list of instances of the classes defined in the module moduleName
        :param moduleName:      name of module containing the class definitions of the passed instances
        :param methodName:      name of the method from the doc of which the :seqdiag_return tag value
                                is extracted and the %s tag is searched in
        :return: filteredInstanceList, methodReturnDoc, signatureStr
        ''' % (SEQDIAG_RETURN_TAG, SEQDIAG_SELECT_METHOD_TAG)

        filteredInstanceList = []
        methodReturnDoc = ''
        signatureStr = ''

        if not instanceList:
            return filteredInstanceList, methodReturnDoc, signatureStr

        for instance in instanceList:
            filteredInstanceList.append(instance)
            methodTupplesList = inspect.getmembers(instance, predicate=inspect.ismethod)
            relevantMethodTupple = [x for x in methodTupplesList if x[0] == methodName][0]
            methodObj = relevantMethodTupple[1]
            methodDoc = methodObj.__doc__

            if methodDoc:
                # get method return type from method doc
                match = re.search(SEQDIAG_RETURN_TAG_PATTERN, methodDoc)
                if match:
                    methodReturnDoc = match.group(1)

                # get method tagged by :seqdiag_select_method
                match = re.search(SEQDIAG_SELECT_METHOD_TAG_PATTERN, methodDoc)
                if match:
                    filteredInstanceList = [instance]
                    break

        # get method signature

        signatureStr = str(signature(methodObj))

        return filteredInstanceList, methodReturnDoc, signatureStr


    @staticmethod
    def instanciateClass(className, moduleName):
        '''
        This method instanciate the passed className dxfined in the passed module name
        whatever the number
        :param className:
        :param moduleName:
        :return:
        '''
        module = None

        try:
            module = importlib.import_module(moduleName)
        except ModuleNotFoundError:
            return None

        class_ = getattr(module, className)
        instance = None
        noneStr = ''

        try:
            instance = eval('class_(' + noneStr + ')')
        except TypeError:
            noneStr = 'None'
            while not instance:
                try:
                    instance = eval('class_(' + noneStr + ')')
                except TypeError:
                    noneStr += ', None'

        return instance


    @staticmethod
    def reset():
        '''
        Reinitialise the class level seq diag information list and seq diag warning list
        :return:
        '''
        SeqDiagBuilder.recordedFlowPath = RecordedFlowPath()
        SeqDiagBuilder.sequDiagWarningList = []

if __name__ == '__main__':
    pass