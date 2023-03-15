from time import sleep
import socket

def main():
    # udp 通信地址，IP+端口号
<<<<<<< HEAD
    udp_addr = ('10.12.96.138', 5000)
    #udp_addr = ('192.168.1.120', 5000)
=======
    udp_addr = ('192.168.1.120', 5000)
>>>>>>> a1f35d0f12bd31c9fb3e44cadf461846d2a80831
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送数据到指定的ip和端口,每隔1s发送一次，发送10次
    for i in range(10):
<<<<<<< HEAD
        udp_socket.sendto(("Hello,I am a UDP socket for: " + str(i)) .encode('utf-8'), udp_addr)
        #udp_socket.sendto("AT+FT".encode('utf-8'), udp_addr)
=======
        udp_socket.sendto(input("Hello,I am a UDP socket for: " + str(i)) .encode('utf-8'), udp_addr)
        udp_socket.sendto("AT+FT".encode('utf-8'), udp_addr)
>>>>>>> a1f35d0f12bd31c9fb3e44cadf461846d2a80831
        print("send %d message" % i)
        sleep(1)

    # 5. 关闭套接字
    udp_socket.close()


if __name__ == '__main__':
    print("当前版本： ")
    print("udp client ")
    main()
