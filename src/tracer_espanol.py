from pypdevs.util import runTraceAtController
import sys

class TracerEspanol(object):
    def __init__(self, uid, server, filename):
        if server.getName() == 0:
            self.filename = filename
        else:
            self.filename = None
        self.server = server
        self.prevtime = (-1, -1)
        self.uid = uid

    def startTracer(self, recover):
        if self.filename is None:
            self.verb_file = sys.stdout
        elif recover:
            self.verb_file = open(self.filename, 'a+', encoding='utf-8')
        else:
            self.verb_file = open(self.filename, 'w', encoding='utf-8')

    def stopTracer(self):
        self.verb_file.flush()

    def trace(self, time, text):
        string = ""
        if time > self.prevtime:
            string = ("\n__  TIEMPO ACTUAL: %10.2f " + "_"*42 + " \n\n") % (time[0])
            self.prevtime = time
        string += "%s\n" % text
        try:
            self.verb_file.write(string)
        except TypeError:
            self.verb_file.write(string.encode())

    def traceInternal(self, aDEVS):
        text = "\n"
        text += "\tTRANSICIÓN INTERNA en el modelo <%s>\n" % aDEVS.getModelFullName()
        text += "\t\tNuevo Estado: %s\n" % str(aDEVS.state)
        text += "\t\tConfiguración de Puertos de Salida:\n"
        for I in range(len(aDEVS.OPorts)):
            text += "\t\t\tpuerto <" + str(aDEVS.OPorts[I].getPortName()) + ">:\n"
            for msg in aDEVS.my_output.get(aDEVS.OPorts[I], []):
                text += "\t\t\t\t" + str(msg) + "\n"
        text += "\t\tSiguiente transición interna programada para el tiempo %.2f\n" % (aDEVS.time_next[0])
        runTraceAtController(self.server, self.uid, aDEVS, [aDEVS.time_last, '"' + text + '"'])

    def traceConfluent(self, aDEVS):
        text = "\n"
        text += "\tTRANSICIÓN CONFLUENTE en el modelo <%s>\n" % aDEVS.getModelFullName()
        text += "\t\tConfiguración de Puertos de Entrada:\n"
        for I in range(len(aDEVS.IPorts)):
            text += "\t\t\tpuerto <" + str(aDEVS.IPorts[I].getPortName()) + ">: \n"
            for msg in aDEVS.my_input.get(aDEVS.IPorts[I], []):
                text += "\t\t\t\t" + str(msg) + "\n"
        text += "\t\tNuevo Estado: %s\n" % str(aDEVS.state)
        text += "\t\tConfiguración de Puertos de Salida:\n"
        for I in range(len(aDEVS.OPorts)):
            text += "\t\t\tpuerto <" + str(aDEVS.OPorts[I].getPortName()) + ">:\n"
            for msg in aDEVS.my_output.get(aDEVS.OPorts[I], []):
                text += "\t\t\t\t" + str(msg) + "\n"
        text += "\t\tSiguiente transición interna programada para el tiempo %.2f\n" % (aDEVS.time_next[0])
        runTraceAtController(self.server, self.uid, aDEVS, [aDEVS.time_last, '"' + text + '"'])

    def traceExternal(self, aDEVS):
        text = "\n"
        text += "\tTRANSICIÓN EXTERNA en el modelo <%s>\n" % aDEVS.getModelFullName()
        text += "\t\tConfiguración de Puertos de Entrada:\n"
        for I in range(len(aDEVS.IPorts)):
            text += "\t\t\tpuerto <" + str(aDEVS.IPorts[I].getPortName()) + ">:\n"
            for msg in aDEVS.my_input.get(aDEVS.IPorts[I], []):
                text += "\t\t\t\t" + str(msg) + "\n"
        text += "\t\tNuevo Estado: %s\n" % str(aDEVS.state)
        text += "\t\tSiguiente transición interna programada para el tiempo %.2f\n" % (aDEVS.time_next[0])
        runTraceAtController(self.server, self.uid, aDEVS, [aDEVS.time_last, '"' + text + '"'])

    def traceInit(self, aDEVS, t):
        text = "\n"
        text += "\tCONDICIONES INICIALES en el modelo <%s>\n" % aDEVS.getModelFullName()
        text += "\t\tEstado Inicial: %s\n" % str(aDEVS.state)
        text += "\t\tSiguiente transición interna programada para el tiempo %.2f\n" % (aDEVS.time_next[0])
        runTraceAtController(self.server, self.uid, aDEVS, [t, '"' + text + '"'])

    def traceUser(self, time, aDEVS, variable, value):
        text = "\n"
        text += "\tCAMBIO DE USUARIO en el modelo <%s>\n" % aDEVS.getModelFullName()
        text += "\t\tAtributo alterado <%s> al valor <%s>\n" % (variable, value)
        self.trace(time, text)
