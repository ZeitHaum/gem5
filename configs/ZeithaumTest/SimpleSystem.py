import m5
from m5.objects import *
system = System() # 创造一个计算机系统对象
#设置时钟域
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz' #时钟频率
system.clk_domain.voltage_domain = VoltageDomain() #电压域
#设置内存仿真方式
system.mem_mode = 'timing' #最常用的模式
system.mem_ranges = [AddrRange('512MB')] #内存大小
#创造CPU
system.cpu = X86TimingSimpleCPU() # 单周期X86CPU, 每周期执行一条指令(除了访存), 其他ISA可更改CPU类型
#设置内存总线
system.membus = SystemXBar()
#连接对应端口, 由于无Cache直接将端口连到CPU端口上.
'''
gem5的MemObject请求和响应模型: 每个MemObject都有一个请求者(端口)和一个响应者(端口), 请求端口向响应端口请求数据, 响应端口返回数据. 使用'='可将某个请求端口和响应端口连接(无左右值区别). 响应端口可以为一组响应者, 此时将会新建一个新的响应端口和请求者相连. 
'''
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
#设置CPU和I/O端口的连接
system.cpu.createInterruptController()
#以下三行是X86的需求, 不同的ISA需求不同. 
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports
#设置Mem控制器
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0] #呼应Line 12.
system.mem_ctrl.port = system.membus.mem_side_ports

#使用模拟的计算机系统运行二进制项目
binary = 'tests/test-progs/hello/bin/x86/linux/hello'
# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary) ## 使用SE 模式
process = Process() # 运行负载, 也是SimObject对象.
process.cmd = [binary] # 编译命令, 类似argv, 文件位置放首位, 其他参数放后位.
"""
C 语言 argc 和argv: 
C main函数声明:main(int argc, char *argv[]), argc表示命令参数个数,argv表示命令数组. 如命令./argtest 1234 abcd将被解析为argc为3, 参数列表为{"./argtest", "1234", "abcd"}.
"""
system.cpu.workload = process
system.cpu.createThreads()

#开始仿真
root = Root(full_system = False, system = system) #Root传递实例化需要的参数
m5.instantiate() #实例化对象
print("Beginning simulation!")
exit_event = m5.simulate() #开始仿真
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause())) #打印程序结束原因