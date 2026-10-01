import os
import sys

if getattr(sys, 'frozen', False):
    DIRETORIO_EXECUCAO = os.path.dirname(sys.executable)
else:
    DIRETORIO_EXECUCAO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.chdir(DIRETORIO_EXECUCAO)

if DIRETORIO_EXECUCAO not in sys.path:
    sys.path.insert(0, DIRETORIO_EXECUCAO)

import servicemanager
import win32event
import win32service
import win32serviceutil

from agente.nucleo import iniciar_agente

class SysMonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SysMonitorAgente"
    _svc_display_name_ = "SysMonitor Agente"
    _svc_description_ = (
        "Agente responsável por coletar e enviar informações "
        "do computador para o servidor SysMonitor."
    )

    def __init__(self, args):
        super().__init__(args)

        self.evento_parada = win32event.CreateEvent(
            None,
            0,
            0,
            None
        )
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        win32event.SetEvent(self.evento_parada)

        servicemanager.LogInfoMsg(
            "SysMonitor Agente: solicitação de parada recebida."
        )

    def SvcDoRun(self):
        servicemanager.LogInfoMsg(
            "SysMonitor Agente: serviço iniciado."
        )

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        try:
            iniciar_agente(self.deve_parar)
        
        except Exception as erro:
            servicemanager.LogErrorMsg(
                f"SysMonitor Agente: erro no serviço: {erro}"
            )

            raise

        finally:
            servicemanager.LogInfoMsg(
            "SysMonitor Agente: serviço encerrado."
        )

    def deve_parar(self):
        resultado = win32event.WaitForSingleObject(
            self.evento_parada,
            0
        )

        return resultado == win32event.WAIT_OBJECT_0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SysMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SysMonitorService)