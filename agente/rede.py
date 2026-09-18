import socket
import psutil 


def obter_interfaces_rede():
    interfaces = []
    informacoes = psutil.net_if_addrs()

    for nome_interface, enderecos in informacoes.items():
        interface = {
            "nome": nome_interface,
            "enderecos": [],
        }

        for endereco in enderecos:
            if endereco.family.name == "AF_INET":
                continue

            interface["enderecos"].append({
                "endereco": endereco.address,
                "mascara": endereco.netmask,
                "broadcast": endereco.broadcast
            })

            if interface["enderecos"]:
                interfaces.append(interface)
    
    return interfaces