#include "iface.h"

void free_iface(struct iface *ifa){
    free(ifa->name);
    free(ifa->inet_addr);
    free(ifa->inet6_addr);
    free(ifa->hw_addr);
}

void init_iface(struct iface *ifa){
    ifa->name = malloc(sizeof(char)*IFACE_NAME_LENGTH);
    (ifa->name)[0] = '\0'; 
    ifa->inet_addr = malloc(sizeof(char)*NI_MAXHOST);
    (ifa->inet_addr)[0] = '\0';
    ifa->inet6_addr = malloc(sizeof(char)*NI_MAXHOST);
    (ifa->inet6_addr)[0] = '\0';
    ifa->hw_addr = malloc(sizeof(char)*HW_ADDR_LENGTH);
    (ifa->hw_addr)[0] = '\0';
    ifa->inet_mask = malloc(sizeof(char)*NI_MAXHOST);
    (ifa->inet_mask)[0] = '\0';
    ifa->inet6_mask = malloc(sizeof(char)*NI_MAXHOST);
    (ifa->inet6_mask)[0] = '\0';
    ifa->broad_addr = malloc(sizeof(char)*NI_MAXHOST);
    (ifa->broad_addr)[0] = '\0';
    
    ifa->running = 0;
    ifa->updown = 0;
    
    ifa->mtu = 0;
    ifa->metric = 0;
    
    ifa->tx_bytes = 0;
    ifa->rx_bytes = 0;
    ifa->tx_packets = 0;
    ifa->rx_packets = 0;
}

int get_info_interface(struct iface* ifa, const char *name_iface){
    struct ifaddrs *ifaddr, *aux;
    struct rtnl_link_stats *stats;
    
    init_iface(ifa);
    
    if (getifaddrs(&ifaddr) == -1) {
        return -1;
    }
    
    for(aux=ifaddr; aux!=NULL; aux=aux->ifa_next){
        if (aux->ifa_addr == NULL){
            continue;
        }
        
        if(strcmp(aux->ifa_name, name_iface) == 0){
            if(aux->ifa_addr->sa_family == AF_PACKET){
                strcpy(ifa->name, aux->ifa_name);
                ifa->hw_addr = get_mac(name_iface);
                
                if(aux->ifa_flags & IFF_RUNNING){
                    ifa->running = 1;
                }
                
                if(aux->ifa_flags & IFF_UP){
                    ifa->updown = 1;
                }
                
                ifa->flags = aux->ifa_flags;
                
                stats = aux->ifa_data;

                ifa->tx_bytes =  stats->tx_bytes;
                ifa->rx_bytes =  stats->rx_bytes;
                ifa->tx_packets =  stats->tx_packets;
                ifa->rx_packets =  stats->rx_packets;
            }else if(aux->ifa_addr->sa_family == AF_INET){
                getnameinfo(aux->ifa_addr, sizeof(struct sockaddr_in), 
                            ifa->inet_addr, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
                getnameinfo(aux->ifa_netmask, sizeof(struct sockaddr_in), 
                            ifa->inet_mask, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
                getnameinfo(aux->ifa_ifu.ifu_broadaddr, sizeof(struct sockaddr_in), 
                            ifa->broad_addr, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
            }else if(aux->ifa_addr->sa_family == AF_INET6){
                getnameinfo(aux->ifa_addr, sizeof(struct sockaddr_in6), 
                            ifa->inet6_addr, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
                getnameinfo(aux->ifa_netmask, sizeof(struct sockaddr_in6), 
                            ifa->inet6_mask, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
            }
        }
    }
    freeifaddrs(ifaddr);
    
    return 0;
}

int get_list_interfaces(char *** list_ifaces){
    char **aux_list_ifaces;
    struct ifaddrs *ifaddr, *ifa;
    int i = 0, j = -1;

    aux_list_ifaces = malloc(sizeof(char*)*MAX_IFACE);

    if (getifaddrs(&ifaddr) == -1) {
        return -1;
    }
   
    for(ifa=ifaddr; ifa!=NULL; ifa=ifa->ifa_next){
        if (ifa->ifa_addr == NULL){
            continue;
        }
        
        for(j=0; j<i; j++){
            //Check if it already exists the interface inside the list
            if(strcmp(ifa->ifa_name, aux_list_ifaces[j]) == 0){
                break;
            }
        }
        
        if(j < i){
            //If j < i, it means that last loop was broken before it finishes
            //Then, it means that was found a equal string inside the list
            continue;
        }
        
        aux_list_ifaces[i] = malloc(sizeof(char)*IFACE_NAME_LENGTH);
        strcpy(aux_list_ifaces[i], ifa->ifa_name);
        i++;
    }
    
    *list_ifaces = aux_list_ifaces;
    
    freeifaddrs(ifaddr);
    
    return j+1;
}

char * get_mac(const char *name_iface){
    //TODO Try to simplify this function
    int i;
    char *ret = malloc(sizeof(char)*HW_ADDR_LENGTH);
    struct ifreq s;
    int fd = socket(PF_INET, SOCK_DGRAM, IPPROTO_IP);

    strcpy(s.ifr_name, name_iface);
    if (fd >= 0 && ret && 0 == ioctl(fd, SIOCGIFHWADDR, &s)){
        for(i=0; i<6; ++i){
            sprintf(ret+i*3, "%02x",(unsigned char) s.ifr_addr.sa_data[i]);
            if(i < 5){
                sprintf(ret+2+i*3,":");
            }
        }
    }else{
        return NULL;
    }
    return ret;
}

int update_tx_rx(struct iface* ifa){
    //TODO Verify errors
    
    struct ifaddrs *ifaddr, *aux;
    struct rtnl_link_stats *stats;
    
    if (getifaddrs(&ifaddr) == -1) {
        return -1;
    }
    
    for(aux=ifaddr; aux!=NULL; aux=aux->ifa_next){
        if (aux->ifa_addr == NULL){
            continue;
        }
        
        if(strcmp(aux->ifa_name, ifa->name) == 0){
            if(aux->ifa_addr->sa_family == AF_PACKET){
                stats = aux->ifa_data;

                ifa->tx_bytes =  stats->tx_bytes;
                ifa->rx_bytes =  stats->rx_bytes;
                ifa->tx_packets =  stats->tx_packets;
                ifa->rx_packets =  stats->rx_packets;
                
                break;
            }
        }
    }
    freeifaddrs(ifaddr);
    
    return 0;
}
