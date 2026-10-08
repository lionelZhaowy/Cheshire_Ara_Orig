# L01 全站标题规范修正

日期2026-10-08；分支mp/ara-pulp-v2；HEAD 459f9d6f5748e39063f7bb67e959c2f27859915d。用户在系统教材实施收尾时指出标题风格严重违例，并通过附件明确授权立即修正。依据[2026-09-23编排约定](handoffs/2026-09-23_L01_editorial_revision.md)：**正式标题使用陈述性、名词性技术主题；问题保留在正文、自测与实验。**

## 范围、规则与结果

本轮完整审阅9个篇标题、51个页面标题、51个副标题、504个H1–H4实际源标题和49个正式入口标签，共664项。content中实际标题层级为H2/H3，H1/浏览器标题由页面元数据生成；无额外H4漏项。检查所有summary：除首页历史路线折叠导航外，其余为自测问题，均保持原样。

实际修改319处源字段：1个篇标题、2个页面标题、50个副标题、189个H2、73个H3、4个入口标签。其余345项保留。生成页中的H1/浏览器标题、目录、侧边栏、面包屑及上下章导航自动同步，不把传播次数重复计入319。首页导航与正文可见引用的单独同步在文末列出。

采用“技术对象＋组成/接口/流程/时序/条件/影响”，必要时保留客观陈述句；没有把所有标题机械改成“机制”。例如异常入口保存状态、机器态定时中断流程、SBA装载、SRAM读延迟适配均与正文实际范围一致，候选启动链/RTOS方案/物理映射/未验证限制保留。关键词只筛查候选；“时钟节拍、主动让出与设备事件”中的“主动让出”是yield技术语义，人工复核后保留。

用户要求保持的技术正文、代码块、技术表格、自测、图形与顺序均未因标题修正改变。标题/入口标签及下表引用差异归一化后，51页其余字节完全一致；全部ID、href/src、slug、页面顺序、篇归属和迁移映射不变。九篇42章仍是同一课程，不把本次修正称为再次完成技术审计。

## 协调与保护

软件子Agent负责9页，OS子Agent负责OS及Ara/RVV/共享存储9页，ASIC子Agent负责10页；主管负责其余页面、全部元数据、全量标题复核、引用同步与生成验收。子Agent不修改共享导航/生成页。主管保留timing-physical#constraints原有合规陈述句，撤回不必要的纯措辞替换；各组交付清单作为过程记录保留，总表以最终源差异为准。

标题前快照在[title-style-20261008](learning/evidence/title-style-20261008/)，包含3080个原有文件哈希、51页正文副本、pages.json、Git状态及用户附件哈希；不复制整段聊天。保护检查确认2971个既有文件不变，其余109项仅限授权正文标题/导航/当前维护与状态。历史报告/交接/证据、learning_backup、图形和PPTX没有改写；当前主管实施报告只补收尾链接并修正其运行调用锚点拼写，不回填此前的检查结果。

维护说明已明确恢复规范。寄存器索引group-11标题中的“见章节内各读/写子块”改为“BusErr读写错误记录子块”，同步build_registers的标题输出；结构检查只对这一处批准标题做归一化后比较原字节哈希，429项寄存器数据和检查强度保留。没有修改工程构建入口或生产源码。

## 验证记录

[标题保护与全量清单](reviews/L01_title_style_20261008/check-result.json)、[664项清单](reviews/L01_title_style_20261008/inventory.json)包含标题数量、逐页哈希、非标题内容保护及关键词候选裁决。标题检查、生成、链接和浏览器的最终结果见本报告末尾与[独立交接](handoffs/2026-10-08_L01_title_style_revision.md)。未运行目标软件构建、RTL仿真、综合或板测；未新增技术功能验证，也未进行真人试读。

## 全量已修改标题对照

路径均位于当前教材维护源，锚点不变。符合规范的345项未修改，完整保留清单在inventory.json。

|文件/锚点|原标题或副标题|新标题或副标题|理由|
|---|---|---|---|
|learning/content/accelerators.html#frame-walkthrough|图像进入模型的一次系统协作|图像采集与模型计算的系统协作流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/accelerators.html#ip-contracts|逐 IP 的数据与控制交付|各类 IP 的数据与控制接口交付|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/accelerators.html#delivery-contracts|每个 IP 共同需要的集成交付|IP 集成交付的共通要求|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/accelerators.html#stream-budget|用数据率反推 FIFO 与 DDR 压力|数据率与 FIFO、DDR 带宽需求|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/accelerators.html#buffer-lifetime|同一预算分别约束流量、停顿和容量|帧流量、服务间隔与缓冲容量预算|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/address-map.html#spaces|三种“地址正确”需要分别核对|地址路由、资源容量与访问属性|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/address-map.html#address-translation-example|一次地址访问的逐层解释|地址访问与路径解析示例|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/ara.html#array-task|同一数组，标量与向量怎样分工|数组计算中的标量与向量分工|明确运算对象与软硬件分工，删除提问和同一泛指。|
|learning/content/ara.html#integer-model|先定义装多少、做多少和怎样解释元素|向量寄存器容量、执行长度与元素类型|以 VLEN、vl、SEW 等对应的技术概念代替装多少、做多少。|
|learning/content/ara.html#external-ports|Ara真实顶层接口与当前接线|Ara 顶层接口与本地连接|保持当前实现范围，统一规范术语与空格。|
|learning/content/ara.html#capacity|用当前配置算容量，再讨论并行|Ara 存储容量与并行执行资源|以计算容量和资源比较的技术内容命名。|
|learning/content/ara.html#internals|加载—计算—存储在 Ara 内部怎样流动|Ara 加载、计算与存储的数据流|概括本节内部模块沿操作的数据流，删除疑问。|
|learning/content/ara.html#interface|从 CPU 译码到 Ara 请求|CVA6 译码与 Ara 请求分派|以本地协作主体和请求机制命名。|
|learning/content/ara.html#walkthrough|把同一轮五种动作连起来|向量数组循环的 CVA6–Ara 协作流程|明确五种动作所属程序和协作对象，删除教学动作。|
|learning/content/ara.html#buffer-handoff|在CPU观察c之前完成结果交接|Ara 结果写入与 CPU 数据交接|以结果可见性与交接主题命名，消除变量泛指和操作指令。|
|learning/content/architecture.html#system|从计算单元到可运行系统|计算单元与片上系统的组成|以计算、存储和设备的具体组成替代泛化的过渡表述。|
|learning/content/architecture.html#paths|先跟随一个程序，再读完整互连|程序执行与 SoC 模块协作|删除跟随程序、阅读互连的授课指令，概括数组、UART和事件路径。|
|learning/content/architecture.html#four-views|同一系统的四种视角|SoC 的功能、事务、地址与实现视角|明确四种视角的技术内容，避免目录依赖前文指代。|
|learning/content/asic-memory.html#consumer-first|先问谁在等这笔读数据|VRF 读数据的消费者与传输路径|明确请求、bank和操作数队列的实际对象|
|learning/content/asic-memory.html#bank-contract|把当前实例换算成一个可核对的 bank|当前 VRF bank 的容量与接口契约|以尺寸与接口内容替代换算教学指令|
|learning/content/asic-memory.html#read-latency|连续跟读一次读、一次局部写|SRAM 读取与字节掩码写入时序|直接命名连续读与局部写过程|
|learning/content/asic-memory.html#k-plus-two|宏多一拍时，具体哪里不再成立|SRAM 读延迟变化与响应时序适配|明确宏增延迟影响，不使用口语疑问|
|learning/content/asic-memory.html#macro-tiling|容量匹配之后，才讨论拼接|SRAM 宏拼接与写掩码适配|涵盖横纵拼接与整字写约束，去掉授课顺序|
|learning/content/asic-memory.html#views-and-initialization|一份宏需要几种视图|存储宏视图、初始化与测试接口|涵盖本节实际资料与接口范围|
|learning/content/axi.html#timing|用 WaveDrom 检查背压|AXI 背压的 WaveDrom 时序示例|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/axi.html#read-write-evidence|从协议语义形成检查点|AXI 协议语义与验证观察点|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/boot-debug.html#debug-workflow|调试同时需要程序描述与目标连接|程序描述与目标调试连接|直接命名符号文件与目标连接两个调试条件。|
|learning/content/boot-debug.html#elf-load|ELF 段怎样通过 SBA 到达内存|基于 SBA 的 ELF 段装载|将疑问式标题改为实际装载路径。|
|learning/content/boot-debug.html#loader-limits|段内字节与 BSS 各有责任|ELF 段装载与 BSS 清零的责任划分|明确段字节与BSS对应的操作，删除各有责任的口语。|
|learning/content/boot-debug.html#observe-program|在已确认入口和存储条件后观察同一程序|数组程序的断点、寄存器与内存观察|准确概括GDB步骤，条件仍留在正文，不把先确认后观察写进标题。|
|learning/content/boot-debug.html#halt-boundary|暂停 CPU 时，系统中还有什么在前进|CPU 暂停期间的系统运行状态|去掉疑问和模糊动作，直接表达halt边界。|
|learning/content/boot.html#default-path|先固定一次启动的输入和目标|默认 ROM/JTAG 启动的输入与目标|保留默认配置和应用输入的限定，去掉先固定的授课指令。|
|learning/content/boot.html#rom|ROM 先建立可用的片上环境|Boot ROM 的片上环境初始化|用初始化主题替代先建立可用环境的叙事。|
|learning/content/boot.html#default-load|存储准备好后，由装载者交接应用|JTAG 装载与应用入口交接|明确本地默认装载主体与交接目标。|
|learning/content/boot.html#normal-result|把程序结果与运行结束一起核对|程序结果校验与运行结束判据|用校验对象及判据命名，不指示读者把两者一起核对。|
|learning/content/boot.html#boot-compare|默认过程之后，再扩展平台与装载来源|平台初始化扩展与程序装载方式|按正文平台钩子及路径比较命名，去掉默认之后再扩展的阅读顺序指令。|
|learning/content/boot.html#gpt-raw|共同镜像格式与 SPM 装载|GPT/raw 镜像格式与 SPM 装载|用实际镜像格式替代依赖相邻小节的共同指代。|
|learning/content/boot.html#boot-growth|程序变大后，由下一阶段继续组织启动|多阶段启动与大型镜像装载|明确ZSL继续装载的技术用途，替代程序变大后的口语叙述。|
|learning/content/build.html#translation-units|从翻译单元到最终映像|翻译单元、对象文件与最终映像|明确构建过程的产物层次。|
|learning/content/build.html#elf|ELF 把机器码和装载信息放在一起|ELF 的代码数据与装载信息|以ELF内容命名，避免放在一起的口语说明。|
|learning/content/build.html#layout|从 C 对象追到输出地址|C 对象与链接地址布局|以对象和链接布局的对应关系命名，删除追到的阅读动作。|
|learning/content/build.html#options-reference|已有产物可以解释后，再选择工程选项|软件构建选项及其作用|删除先解释产物再选择的教学指令，保留选项实际作用范围。|
|learning/content/build.html#practice|完成一次可解释的构建|隔离构建与产物验证|明确本节实践范围，删除可解释的教学评价。|
|learning/content/build.html#source-to-hardware|从源文件到执行结果的责任交接|软件构建、装载与执行的责任交接|直接列出责任交接涉及的三个阶段。|
|learning/content/cdc-rdc.html#sampling|从一次必须被接收的命令开始|异步采样与跨域命令传递|明确亚稳采样和事件/配置传输对象|
|learning/content/cdc-rdc.html#handshake|让配置保持到对方确认|多位配置的保持与两相握手|准确命名完整快照保持与确认协议|
|learning/content/cdc-rdc.html#choose-by-signal|从控制扩展到连续数据|不同信号类型的跨域传递方式|以信号分类和交接方式命名对比内容|
|learning/content/cdc-rdc.html#local-ddr|沿当前 DDR wrapper 找跨域边界|当前 DDR wrapper 的 AXI 跨域路径|使用已核对接口路径替代源码查找指令|
|learning/content/cdc-rdc.html#reset-domains|为什么复位也要有两端协议|跨域接口的复位协调机制|直接命名两端复位状态一致性要求|
|learning/content/cdc-rdc.html#constraints-and-review|交付时怎样证明选对了|CDC/RDC 约束与验收范围|具体区分约束、检查和证据边界|
|learning/content/clocks.html#clocks|先让 CPU 有时钟，才有软件配置时钟|安全启动时钟与软件配置前提|以安全取指和软件配置的依赖关系替代先后授课句式|
|learning/content/clocks.html#clock-domains|把时钟域、分频和同步器区分开|时钟域、分频与同步结构|以技术对象概括正文的分类说明|
|learning/content/clocks.html#clock-inputs|输入、消费者与观察点|时钟与异步输入的使用条件|明确输入类型及表格的正常使用条件|
|learning/content/clocks.html#pll-loop|锁相反馈与两域教学例|PLL 锁相反馈与候选双域时钟示例|明确PLL对象并保留候选双域示例限定|
|learning/content/clocks.html#clock-inventory|先标真实采样时钟，再标派生关系|采样时钟与派生关系|以实际记录对象替代先标再标的阅读指令|
|learning/content/clocks.html#normal-frequency-change|一次受控调频怎样完成|受控调频流程示例|以流程主题替代疑问并保留教学示例身份|
|learning/content/configuration.html#first-program-contract|先为同一个标量程序配齐运行条件|标量数组程序的运行配置|保留本节标量SPM/UART实例范围，去掉先配齐的教学指令。|
|learning/content/configuration.html#configuration-contract|三个入口与一份系统契约|CPU、SoC 与软件配置的系统契约|把三个入口替换为实际配置对象，目录可独立理解。|
|learning/content/configuration.html#elaboration|从常量配置到硬件实例|常量配置与硬件实例生成|用展开过程的技术主题替代叙事过渡。|
|learning/content/configuration.html#advanced-configurations|学完相关设备后的组合回查|进阶配置组合参考|保留进阶定位，将学习后回查的指令移交既有正文。|
|learning/content/configuration.html#fields|按字段、消费者和约束核对配置|配置字段、消费者与取值约束|以核对对象命名，不向读者下达操作指令。|
|learning/content/configuration.html#configuration-candidates|按用途选择配置候选|不同用途的配置候选|保留候选限定，删除选择动作。|
|learning/content/configuration.html#case-baseline|三个独立案例的共同基线|扩展配置案例的共同基线|说明AXI RT、CLIC和Router所属扩展案例范围，不以三个指代内容。|
|learning/content/cva6.html#functional-units|以软件可见状态解释执行|程序执行与软件可见状态|直接陈述技术对象，去掉解释执行的教学动作。|
|learning/content/cva6.html#programmer-state|从一条数组赋值认识寄存器与 PC|数组赋值中的通用寄存器与 PC|以实例中的程序状态命名，删除认识寄存器的教学动作。|
|learning/content/cva6.html#privilege|M、S、U 是执行权限，不是三颗 CPU|M、S、U 特权级与执行权限|保留特权级主题，将口语化纠误留在正文。|
|learning/content/cva6.html#implementation-reference|可选回查：profile 与实现资源|CPU profile 与实现资源参考|将可选回查的阅读安排转为参考内容名称。|
|learning/content/ddr.html#ddr-subsystem|DDR 子系统：控制器、PHY 与软件如何衔接|DDR 控制器、PHY 与软件的职责划分|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/ddr.html#spm-diagnostics|先建立独立于DDR的启动环境|独立于 DDR 的早期启动环境|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/ddr.html#software-init|从初始化到第一个可用缓冲区|DDR 初始化与缓冲区可用条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/ddr.html#vendor-inputs|控制器和 PHY 的逐项资料|DDR 控制器与 PHY 的接口资料|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/ddr.html#acceptance|从数据正确到并发和错误|DDR 数据、并发与错误处理验收|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/dma.html#copy-task|为什么不让 CPU 逐字节复制|DMA 内存搬运与 CPU 控制职责|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/dma.html#normal-copy|完整任务的正常交接|DMA 拷贝任务与缓冲区交接|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/dma.html#lanes|本工程执行条件|本地 iDMA 示例的执行条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/future.html#extract|先让另一台机器得到同一个系统|独立工程的固定输入与可搬迁性|明确固定配置和跨目录交付主题|
|learning/content/future.html#asic|从数字接口走向工艺实现|数字接口与工艺资源映射|将迁移口语改为接口与资源关系|
|learning/content/future.html#resource-mapping|顺着一个消费者找到平台责任|数字系统消费者与平台实现职责|明确消费者和平台责任，不使用阅读路径指令|
|learning/content/future.html#sram-example|用 k+1/k+2 检查替换是否保持行为|SRAM 读延迟对消费者时序的影响|准确概括k+1/k+2消费者错配关系|
|learning/content/future.html#implementation-deliverables|每种接口交出可以检查的条件|平台接口的交付与验收条件|概括接口表的交付和验收职责|
|learning/content/future.html#verification-layers|对同一笔 SRAM 读，不同检查回答什么|SRAM 读接口的分层验证与证据范围|以共同接口和方法范围替代疑问|
|learning/content/future.html#acceptance-gates|按依赖进入下一阶段|ASIC 工程阶段与准入条件|以阶段依赖的正式技术主题替代推进指令|
|learning/content/i2c.html#purpose|为什么要读一片 EEPROM|EEPROM 用途与读取任务|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#device|先把一次读取讲完整|EEPROM 读取流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#transaction|EEPROM 地址如何变成总线事务|EEPROM 地址与 I2C 总线事务|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#controller|让控制器代替 CPU 逐位操作|I2C 控制器的字节传输|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#structure|从寄存器到命令状态机|寄存器接口与命令状态机|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#register-contract|关键访问的意义|关键寄存器的访问语义|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#software|从应用参数走到引脚|EEPROM 读取的软件调用链|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#limits|本只读例的范围|EEPROM 只读示例的适用范围|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/i2c.html#target-mode|进阶：让 SoC 成为被访问的设备|I2C Target 模式与 SoC 访问接口|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/index.html#route|先把一个程序运行过程讲完整|程序构建、启动与运行流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/index.html#example|用同一任务连接各层|贯穿示例与系统层次|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/index.html#part-software|第二篇 · 从C程序到可观察结果|第二篇 · 裸机软件构建、启动与运行|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/index.html#diagnostics|独立的症状与问题入口|故障诊断与已知问题索引|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/integration.html#control-path|一个设备操作的控制闭环|Reg 设备的控制流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/integration.html#unit|先定义一个完整的设备操作|寄存器加法设备的操作示例|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/integration.html#control|接入 Reg 扩展端口|Reg 扩展端口接入|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/integration.html#irq|接入中断并验证完成协议|中断接入与完成协议验证|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/integration.html#master|加入主动 AXI 数据口|AXI 主接口接入|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/integration.html#verification|从单元到系统的验证递进|单元与系统集成的验证层次|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/interconnect.html#slow-fast|同 ID 先慢后快与读返回|同 ID 事务的目标延迟与返回顺序|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/interconnect.html#validation|由修改影响设计验证|结构变更与验证范围|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/interrupts.html#event-task|让 CPU 同时观察 GPIO 事件与时间经过|GPIO 事件与定时器的协同使用|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/interrupts.html#trap|从异步事件到处理程序|异步事件与中断处理入口|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/interrupts.html#extensions|完成基本事件后再选择其他中断路径|可选中断路径的适用条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/labs.html#rvv-depth|递进：尾部、归约与三种编程入口|RVV 尾部、归约与三种编程入口|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/linux.html#why-linux|数组程序需要的环境发生了什么变化|裸机与 Linux 用户程序的运行环境|明确正文对比对象与内容。|
|learning/content/linux.html#software-products|先把主机生成的文件与目标运行的软件分开|Linux 软件组成与构建产物|覆盖运行软件和主机产物分类，删除先后指令。|
|learning/content/linux.html#firmware-to-kernel|沿一条有本地依据的候选链交接|本地固件与内核的候选启动链|保留候选限定；当前只有源码关联，不是已跑通启动链。|
|learning/content/linux.html#kernel-to-init|内核怎样走到第一个用户进程|Linux 内核初始化与首个用户进程启动|以具体启动过程取代疑问。|
|learning/content/linux.html#dts-is-contract|设备树把硬件事实交给软件|设备树的硬件描述与适用条件|明确设备树内容及与当前硬件一致的条件。|
|learning/content/linux.html#user-program|让同一个数组算法成为用户程序|Linux 用户态数组计算示例|用技术示例名称代替教学指令。|
|learning/content/linux.html#version-evidence|本地版本能证明什么|本地软件版本与验证边界|以版本和证据范围命名，删除提问。|
|learning/content/linux.html#goals/strong|从平台固件走到第一个用户程序|Linux 启动与用户程序运行|正式入口标签；保留或改为技术主题，任务正文不变|
|learning/content/manufacturing-test.html#why-test|相同程序为何不能覆盖所有制造缺陷|功能回归与制造缺陷检测的职责|按正文区分两类验证目标|
|learning/content/manufacturing-test.html#scan-process|逻辑扫描怎样进入和观察一个内部状态|逻辑扫描的移位、捕获与响应观察|直接列明scan正常流程|
|learning/content/manufacturing-test.html#memory-test|对一个 bank 逐地址写读|SRAM bank 的 MBIST 流程示例|明确存储对象并保留教学算法不等于量产方案的限定|
|learning/content/manufacturing-test.html#local-scope|当前源码实际提供了哪些入口|当前扫描与存储自测接口的实现边界|明确本地scan绑值和tag BIST覆盖范围|
|learning/content/manufacturing-test.html#test-handoff|从 RTL 接口走到可交给测试机的产物|制造测试的网表、图样与 ATE 交付|以实际交付物概括测试流程|
|learning/content/measurement.html#question|先固定“完成了同一个什么任务”|计算任务定义与结果正确性|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/measurement.html#boundaries|在一次正常操作上放三个计时窗口|算法内核、设备服务与端到端计时边界|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/measurement.html#observation|当前工程已经有什么观测入口|本地计数器、日志与事务观测接口|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/measurement.html#units|周期、时间、吞吐和延迟怎样换算|周期数、执行时间、吞吐率与延迟的换算|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/measurement.html#repeat|把一次结果变成可复查的实验|性能实验的可重复性条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/measurement.html#record|一份可以交给另一位工程师的记录|实验输入、结果与测量记录|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/memory.html#usage-contract|从启动 SPM 到共享缓冲区|启动 SPM 与共享缓冲区的使用条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/models.html#model-case|一个完整的 Ara→NPU→Ara 候选片段|Ara–NPU–Ara 协作的候选流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/models.html#budget|先估容量与数据量，再讨论性能|存储容量、数据流量与性能预算|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/os-debug.html#locate-stage|先定位停在哪个交接边界|OS 启动与设备服务的分阶段定位|以诊断对象及方法命名，删除先后指令。|
|learning/content/os-debug.html#boot-inputs|启动输入及镜像溯源尚未闭合|启动输入与镜像溯源的验证缺口|保留未验证状态，使用明确的缺口主题。|
|learning/content/os-debug.html#description|设备树描述与当前硬件需要逐项对齐|设备树与硬件配置的一致性核对|以所需核对对象命名，不在标题部署任务。|
|learning/content/os-debug.html#vector-context|向量上下文代码存在，当前组合安全抢占仍待验证|向量上下文实现与安全抢占验证缺口|同时保留代码存在与安全抢占尚未验证的边界。|
|learning/content/os-debug.html#dma-boundary|OS 不会自动补齐 DMA 一致性|DMA 映射与平台一致性限制|以正常 API 契约和本地限制命名，删除拟人化表述。|
|learning/content/os-debug.html#evidence-levels|后续记录须写清证据级别|OS 验证记录的证据等级|明确证据主题，删除写作指令。|
|learning/content/os-devices.html#same-uart|外部设备没有因为换 OS 而改变|UART 连接、配置与资源所有权|概括本节接线、配置和所有权内容，删除口语对比。|
|learning/content/os-devices.html#baremetal-uart|裸机：应用自己承担等待|裸机 UART 轮询发送流程|以软件行为和流程命名。|
|learning/content/os-devices.html#rtos-uart|RTOS：先由一个服务任务独占 UART|RTOS UART 独占服务任务方案|保留方案性质，不将条件化 RTOS 教学写成本地实现。|
|learning/content/os-devices.html#rtos-irq|正常进阶：发送中断推进缓冲|UART 发送中断与缓冲管理|保留正常进阶机制，删除教学层级前缀。|
|learning/content/os-devices.html#linux-uart|Linux：应用提交字节，内核管理设备|Linux TTY 与串口驱动调用链|准确命名应用到串口驱动的数据路径。|
|learning/content/os-devices.html#linux-lifecycle|打开、配置、写入、排空、关闭|Linux 串口操作流程与完成条件|为打开至关闭的一组动作补充对象和完成语义。|
|learning/content/os-devices.html#driver-and-description|设备描述如何让驱动找到控制器|设备树与 UART 驱动绑定|以设备描述匹配机制代替疑问。|
|learning/content/os-devices.html#buffer-ownership|大数据设备多了一层缓冲所有权|设备缓冲区的地址与所有权管理|明确虚拟地址、DMA 地址及生命周期主题。|
|learning/content/os-devices.html#completion-check|用五个完成点复述整条链|UART 数据交接的分层完成条件|以正文五种完成语义命名，删除复述指令。|
|learning/content/os-devices.html#goals/strong|同样发出一行文本，软件责任怎样改变|裸机、RTOS 与 Linux 的 UART 软件职责|正式入口标签；保留或改为技术主题，任务正文不变|
|learning/content/peripheral-debug.html#layers|从最后一个已确认的动作向下定位|外设故障的分层定位方法|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#uart|UART：没有文本、文本不完整或乱码|UART 无输出、文本截断与乱码诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#gpio|GPIO：输出已写却无电平变化|GPIO 输出与引脚状态不一致诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#interrupts|定时器/PLIC：不进处理函数或反复进入|定时器与 PLIC 中断缺失、重复响应诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#i2c|I2C：没有应答、收不到指定字节或短读越界|I2C 无应答、数据缺失与短读越界诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#spi|SPI：全0xff、错位或等待不结束|SPI 全 0xff 数据、字节错位与等待停滞诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#dma|iDMA：当前示例为何保持 BLOCKED|本地 iDMA 示例的执行限制|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#bus-errors|BusErr 与 AXI RT：保留记录后再消费|BusErr 与 AXI RT 的状态读取及副作用|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#link|Serial Link：本地接受但没有远端结果|Serial Link 远端访问未完成诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#vga|VGA：无图、错色或欠载|VGA 无显示、颜色错误与欠载诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/peripheral-debug.html#usb|USB：寄存器可读但控制传输不完成|USB 控制传输未完成诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/physical-interfaces.html#ack-path|一个 ACK 为什么需要同时看输出和输入|I2C ACK 的输出控制与输入反馈|明确ACK位的双向逻辑通路|
|learning/content/physical-interfaces.html#pad-package-board|沿当前 FPGA 连接理解未来边界|FPGA IO 与 ASIC PAD、封装及板级边界|概括现有参考与待实现物理边界|
|learning/content/physical-interfaces.html#open-drain|释放线路如何形成高电平|I2C 开漏、上拉与高电平形成|将疑问改为电气原理主题|
|learning/content/physical-interfaces.html#pinmux|复用和上电状态也是正常操作的一部分|候选引脚复用与上电状态管理|保留本节pinmux为未来契约而非当前能力|
|learning/content/physical-interfaces.html#lvds-boundary|差分图像输入要先确定物理接收职责|候选 LVDS 图像接口的物理接收职责|明确未来图像接口及资料未定边界|
|learning/content/power.html#asic-clock-power|一帧结束后，哪些东西可以暂时不工作|候选计算域的帧间关断|明确未来NPU示例对象与候选关电范围|
|learning/content/power.html#current-boundary|现有代码能证明什么|当前 RTL 的电源控制边界|直接命名当前实现边界，避免提问|
|learning/content/power.html#power-table|未来域表需要哪些输入|候选电源域的设计输入|将未来资料问句改为带候选限定的技术主题|
|learning/content/power.html#sequence|关断、保持和恢复|候选电源域的关断、保持与恢复|补足独立目录所需对象并明确候选实现状态|
|learning/content/power.html#shutdown|关断前的所有权边界|关断前的事务与缓冲区所有权|明确正文排空和帧缓冲交接两个对象|
|learning/content/power.html#isolation-example|从设备完成信号理解隔离和恢复|设备完成信号的隔离与恢复示例|保留示例性质，以技术过程替代理解指令|
|learning/content/power.html#wake|恢复后先建立可用状态，再发布新任务|电源域恢复与任务重新开放条件|以恢复过程和任务准入条件替代先再指令|
|learning/content/registers.html#group-11|Bus error 单元 · 见章节内各读/写子块|BusErr 读写错误记录子块|正式技术主题；范围与正文一致|
|learning/content/reset.html#sources|复位先建立控制状态，再由启动流程建立可用系统|复位状态与启动就绪条件|概括复位状态和后续启动条件，移除先再句式|
|learning/content/reset.html#system-reset|当前几个复位入口分别控制什么|当前复位入口及作用范围|明确现有实现对象和范围|
|learning/content/reset.html#release|为什么释放必须等本域时钟|复位同步释放与时钟有效条件|直接陈述同步释放的时钟前提|
|learning/content/reset.html#readiness|用可观察里程碑连接硬件和软件|启动阶段及软硬件就绪条件|以实际阶段和就绪条件替代连接里程碑的教学动作|
|learning/content/reset.html#rom-ready|从第一条指令到应用 main|ROM 执行、片上存储与栈初始化|明确段落覆盖的启动对象|
|learning/content/reset.html#external-ready|外存前提放在首次访问之前|首次外存访问的初始化前提|以访问条件表达前置依赖|
|learning/content/reset.html#bringup-milestones|每一步应该交出什么|启动阶段的交付条件与观察依据|为目录列明阶段表格的对象与列义|
|learning/content/reset.html#transaction-reset|一次正常重启，怎样把接口先停下来|候选设备域的受控重启流程|移除疑问并保留独立设备域重启尚属候选的边界|
|learning/content/reset.html#drain|停止新请求，再等待已接受事务|新请求停止与在途事务排空|以两个协议动作命名正文内容|
|learning/content/reset.html#reset-validation|验证正常重启及异常边界|正常重启与异常边界的验证范围|使用名词性验证范围，不表示验证已经执行|
|learning/content/rtos.html#two-tasks|为什么不把所有工作写进一个循环|RTOS 任务划分与实时性要求|以任务划分和截止期要求概括循环例，不保留疑问句。|
|learning/content/rtos.html#state-and-stack|暂停一个任务，要把什么留在原处|任务上下文的组成与保存|明确暂停任务所需保存对象与机制。|
|learning/content/rtos.html#switch-walk|沿 A→B→A 走一遍|任务切换与上下文恢复流程|以 A→B→A 展示的切换和恢复流程命名，删除走读指令。|
|learning/content/rtos.html#tick-and-event|时间到、主动让出与设备到达是三种触发|时钟节拍、主动让出与设备事件|并列列出正文三类调度触发，不用口语描述。|
|learning/content/rtos.html#queue-example|把 137 个元素交给计算任务|基于消息队列的数组计算示例|明确示例的通信机制与计算对象。|
|learning/content/rtos.html#synchronization|从一份共享计数理解同步|共享数据同步与优先级反转|覆盖正文临界区、互斥和优先级继承相关内容。|
|learning/content/rtos.html#fp-vector-context|整数切换成立后，再增加 FP 与 RVV 状态|FP 与 RVV 上下文管理及支持范围|以扩展上下文及本地支持边界命名，删除学习次序指令。|
|learning/content/rtos.html#local-boundary|把教学闭环交给本平台|本平台 RTOS 适配条件与验证边界|突出尚待适配和验证的条件，不将教学闭环写成本地完成状态。|
|learning/content/rtos.html#goals/strong|让两个任务各自继续执行|RTOS 任务调度与上下文管理|正式入口标签；保留或改为技术主题，任务正文不变|
|learning/content/runtime.html#software-stack|同一个程序有四种关系|程序的组成、构建、启动与运行关系|把四种关系的具体内容写入标题，避免模糊计数与同一程序指代。|
|learning/content/runtime.html#abi|ABI 约定软件之间的边界|ABI 与软件调用边界|以二进制调用约定的实际范围命名。|
|learning/content/runtime.html#initialization|有初值与零初始化的不同责任|数据初值装载与零初始化的责任划分|明确文件初值装载与BSS清零的责任，消除有初值的口语表达。|
|learning/content/runtime.html#sections|用节名表达存储用途|存储用途与节的划分|用存储组织主题替代用节名表达的教学动作。|
|learning/content/runtime.html#section-purpose|按初始化和访问方式分组|节的初始化属性与访问方式|明确分组对象和依据，避免指令式标题。|
|learning/content/runtime.html#runtime-call|从 main 的第一项检查连续走到 UART 输出|数组程序的初始化、计算与 UART 输出|覆盖正文从初态校验、测频、计算到输出的完整范围，删除连续走到的授课动作。|
|learning/content/runtime.html#beyond-baremetal|沿相同职责进入操作系统|裸机与操作系统的软件职责|直接命名两类环境的职责，删除沿相同职责进入的阅读安排。|
|learning/content/runtime.html#object-lifetime|进阶回查：数组、栈与共享缓冲的边界|数组、栈与共享缓冲区的使用边界|保留对象边界主题，去掉进阶回查的教学指令。|
|learning/content/sharing.html#sharing|当前 CPU/Ara 协作覆盖到哪里|当前 CPU/Ara 协作机制的适用范围|保留当前实现范围，以主题代替提问。|
|learning/content/sharing.html#handoff|从取得缓冲区到交还缓冲区|候选缓冲区所有权与交接协议|正文包含未来 NPU/DDR 旁路的候选协议，保留方案限定。|
|learning/content/silicon-bringup.html#observable-first|先让最小系统可观察|最小启动系统的可观察性|直接表达正常启动所需观察条件|
|learning/content/silicon-bringup.html#staged-run|从安全取指走到独立结果校验|候选首硅启动与结果校验流程|保留尚无样片、未运行的方案身份|
|learning/content/silicon-bringup.html#normal-observability|记录状态，是为了连接相邻阶段|启动阶段标志与状态观察|命名版本/阶段/PC等实际观察对象|
|learning/content/silicon-bringup.html#measure-next|正确性闭环之后再问性能和功耗|正确性、性能与功耗的测量边界|直接表达测量前提和范围|
|learning/content/silicon-bringup.html#records|把一次运行留下的证据交给下一阶段|启动验证证据与后续交付条件|概括证据等级和后续负责方输入|
|learning/content/simulation.html#flow|一次运行所需的四类输入|仿真运行的输入组成|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/simulation.html#vector-trace|为向量实验建立最小动态证据链|向量实验的动态验证证据|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/software-debug.html#locate-stage|先确定停止在哪一次责任交接|软件构建、装载与运行的分层诊断|将定位指令变为完整的软件责任层次范围。|
|learning/content/software-debug.html#load-stop|装载没有继续：分开观察三个完成条件|JTAG 装载停顿与阶段完成条件|保留装载停顿症状，明确SPM、halt与SBA完成条件的范围。|
|learning/content/software-debug.html#stack-handoff|装载成功后，应用仍需要有效 sp|应用入口的栈有效性与对齐条件|准确概括继承栈、暂停位置和ABI对齐的诊断内容。|
|learning/content/software-debug.html#trap-stop|停在 trap：先保存原因，再解释恢复条件|trap 停顿的原因记录与恢复条件|保留诊断对象与条件，删除先再指令。|
|learning/content/software-debug.html#no-output|main 已进入，但没有正确字符|main 运行期间的 UART 无输出与乱码诊断|用具体症状替代没有正确字符，限定main运行期间，避免误指函数返回以后。|
|learning/content/software-debug.html#wrong-result|有日志仍要检查同一次执行的数据|应用数据、日志与退出码的一致性检查|明确结果检查对象，删除有日志仍要的口语提醒。|
|learning/content/software-debug.html#known-issues|证据与尚未关闭的事项|已知软件问题的证据与验证状态|明确事项所属软件问题及状态，不暗示已修复。|
|learning/content/spi.html#read-task|从保存程序的 Flash 读出已知字节|NOR Flash 的已知数据读取|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/spi.html#transaction|一段命令为什么不能分成三次片选|SPI 命令、地址与数据的片选连续性|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/spi.html#segments|把一次设备操作分成事务段|SPI 设备操作与事务分段|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/spi.html#controller|控制器怎样执行这条读取|SPI 控制器的读取流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/spi.html#devices|应用如何调用 NOR 驱动|NOR Flash 的软件调用链|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/spi.html#sd|同一个 SPI 上的 SD 协议|SPI 总线上的 SD 协议|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#link|Serial Link：把本地写变成远端写|Serial Link 的远端访问|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#link-registers|先配置发送节拍，再开始事务|Serial Link 的发送时序配置|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#link-validation|一次写读的全过程与现有加载实例|Serial Link 写读流程与加载实例|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#vga|VGA：把 RAM 的彩条变成连续像素|VGA 帧缓冲与像素输出|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#vga-validation|正常输出的连续观察|VGA 输出与结果观察|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#usb|USB OHCI：让控制器读取一条传输任务|USB OHCI 控制器与传输任务|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#usb-init|从描述符准备到接收数据|USB 描述符准备与数据接收|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#usb-validation|该例还需要什么|USB 示例的执行条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/stream-io.html#device-contracts|三种完成条件不能互换|链路、显示与 USB 的完成语义|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/system-debug.html#locate|先找到最早没有完成的责任交接|系统故障的责任边界与定位顺序|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/system-debug.html#ddr|DDR没有响应、数据不一致或初始化停滞|DDR 无响应、数据不一致与初始化停滞诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/system-debug.html#simulation|从目标运行最早失败的阶段定位|目标运行失败的阶段定位|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/system-debug.html#integration|控制寄存器正确，系统任务却没有完成|设备控制访问与系统任务完成状态诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/system-debug.html#frames|丢帧、半帧或吞吐不足|帧丢失、数据不完整与吞吐不足诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/system-debug.html#measurement|计时跳变、零耗时或“加速”不可复现|计时异常与性能结果复现诊断|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/timing-physical.html#real-path|从一个真实起点和终点读时序|VRF 地址与数据返回的时序路径|明确真实时序起终点对应的路径对象|
|learning/content/timing-physical.html#setup-hold|先理解建立与保持，再给时钟周期|建立时间、保持时间与时钟周期约束|以技术量和关系替代先理解再给的指令|
|learning/content/timing-physical.html#physical-feedback|把十六个 bank 放到版图后会发生什么|VRF 宏布局的时序影响|准确概括摆放、线长和扇出反馈|
|learning/content/timing-physical.html#evidence|形成一份可复查的时序结论|静态时序分析的输入与证据范围|明确分析资料和结论边界，避免要求读者形成结论|
|learning/content/traps.html#call-versus-trap|从普通函数调用走向异常和中断|函数调用、异常与中断的控制流|将走向的授课过渡改为三种控制转移的技术范围。|
|learning/content/traps.html#trap-entry|硬件先留下最小的返回线索|异常与中断入口的硬件状态更新|用CSR/PC状态更新替代返回线索比喻。|
|learning/content/traps.html#software-context|入口汇编为什么还要保存整数状态|异常入口的整数寄存器保存与恢复|依据当前整数包装范围命名，删除为什么还要的疑问口语。|
|learning/content/traps.html#normal-service|连续追踪一次定时服务|机器态定时器中断处理流程|明确机器态timer服务范围，不扩成调度实现。|
|learning/content/traps.html#syscall-scheduling|由 trap 连接到任务和系统调用|trap、任务切换与系统调用的关系|陈述技术关系，去掉连接到的阅读过渡。|
|learning/content/traps.html#local-handler|当前实现的适用范围|本地 trap handler 的适用范围|明确当前实现所指对象，保留适用范围限定。|
|learning/content/uart-gpio.html#use-and-connection|从终端上的 ready 到一根发送线|UART 用途与设备连接|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/uart-gpio.html#registers|CPU 怎样把字符交给设备|MMIO 字符输出与寄存器访问语义|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/uart-gpio.html#uart-device|把 ready 连续发送出去|UART 文本发送流程|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/uart-gpio.html#uart-recovery|本例执行条件|UART 示例的执行条件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/uart-gpio.html#gpio-device|从一个输出位到一个输入事件|GPIO 输出控制与输入事件|以具体技术对象、过程或适用条件替代口语、教学动作或模糊指代；正文范围不变|
|learning/content/vector-debug.html#layers|先定位失败阶段，再看对应证据|向量程序的分阶段诊断与证据|明确诊断对象和分层方法，删除先后指令。|
|learning/content/vector-debug.html#configuration|首条向量指令陷入：先核对有效组合|首条向量指令陷入的配置核对|保留具体症状与诊断范围，删除先核对指令。|
|learning/content/vector.html#concepts|从同一数组继续到可校验程序|向量数组程序与校验任务|明确数组程序及可校验目标，删除依赖前文的同一。|
|learning/content/vector.html#work|同一任务的两种表达|数组计算的标量与向量表达|给出两种表达的具体名称。|
|learning/content/vector.html#configuration|配置到运行许可|RVV 配置与运行前提|明确有效配置与启动许可条件的技术对象。|
|learning/content/vector.html#loop|vl 决定每轮处理多少元素|实际 vl 与数组分块循环|以运行时 vl 和分块循环关系命名。|
|learning/content/vector.html#advanced-state|基本整数循环之后再扩展状态与操作|RVV 进阶状态与运算|保留进阶层次，删除先后教学指令。|
|learning/content/vector.html#rvv-model|从数组位置理解 vtype、寄存器分组与 mask|RVV 掩码、访存模式与数值规则|覆盖所属段落的掩码、地址模式、整数及浮点数值规则。|
|learning/content/vector.html#validation|分层建立正确性与性能证据|RVV 正确性与性能验证|以验证对象命名，删除建立证据的教学动作。|
|learning/content/vector.html#performance|结果与性能分别建立证据|数值校验与性能测量方法|区分结果正确性和实际性能测量两个技术主题。|
|learning/content/virtual-memory.html#from-physical|裸机数组先占用一块真实存储|裸机数组的物理存储与访问条件|明确裸机数组作为地址空间教学起点的技术内容。|
|learning/content/virtual-memory.html#protection|PMA、PMP 与页权限各回答一类问题|PMA、PMP 与页权限的职责|以各保护机制职责概括段落。|
|learning/content/virtual-memory.html#translation-walk|一次 4 KiB 页内访问如何落到 RAM|Sv39 的 4 KiB 页地址翻译示例|保留 4 KiB 限定并明确正文使用的 Sv39 教学推演。|
|learning/content/virtual-memory.html#two-spaces|进程切换时，地址解释也要切换|进程地址空间与页表切换|命名地址空间切换机制，去除依赖上下文的口语表达。|
|learning/content/virtual-memory.html#normal-page-fault|页异常也可能是正常的按需建立过程|按需分页与页异常处理|明确正常按需建立映射的技术主题。|
|learning/content/virtual-memory.html#device-addresses|为什么一个用户 buffer 不能直接变成 DMA 地址|用户虚拟地址与设备 DMA 地址|并列地址类型，保留正文映射契约而不在标题提问。|
|learning/content/virtual-memory.html#address-exercise|完成一次纸面推演，再设计目标验证|地址空间切换的推演与验证条件|区分纸面推演和有前提的目标验证，不再指挥读者操作。|
|learning/content/virtual-memory.html#goals/strong|解释同一个指针为何能指向不同的数据|进程地址空间与地址翻译|正式入口标签；保留或改为技术主题，任务正文不变|
|learning/scripts/pages.json#parts/software/title|从C程序到可观察结果|裸机软件构建、启动与运行|以软件阶段概括知识领域，去除阅读过程表达|
|learning/scripts/pages.json#pages/index/subtitle|沿同一程序建立系统理解，按明确任务深入OS与ASIC。|程序执行、系统接口、操作系统与 ASIC 实现的学习路线。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/architecture/subtitle|沿取指、数组与字符输出辨认模块职责。|取指、数组计算与字符输出中的 SoC 模块协作。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/cva6/subtitle|先掌握指令、状态、特权与存储接口。|指令集、处理器状态、特权级与存储接口。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/configuration/subtitle|按真实字段及消费者建立自洽组合。|硬件字段、参数消费者与软件配置的一致性。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/runtime/subtitle|从对象、调用和初始化理解存储布局。|C 对象、函数调用、初始化与存储布局。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/build/subtitle|让同一数组程序形成可解释的装载产物。|源文件、对象文件、链接布局与 ELF 装载产物。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/boot/subtitle|分别追踪 ROM 服务、自主加载和应用入口。|ROM 服务、程序装载与应用入口的执行关系。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/boot-debug/subtitle|核实外部调试接管的真实等待条件。|外部调试、程序装载与执行接管条件。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/address-map/subtitle|分别核对路由窗口、实际容量和 CPU 属性。|地址路由窗口、实际资源容量与 CPU 访问属性。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/axi/subtitle|沿真实握手语义理解一笔读写事务。|AXI 读写事务的通道握手与完成语义。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/interconnect/subtitle|追踪译码、仲裁、W 路由、ID 与响应。|地址译码、仲裁、写数据路由与 ID 响应关系。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/adapters/subtitle|解释位宽、协议、ID 转换及跨域边界。|位宽、协议、ID 转换与跨时钟域接口。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/memory/subtitle|区分缓存副本、地址别名与共享物理阵列。|缓存副本、地址别名与共享物理阵列。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/traps/subtitle|从函数调用到trap和任务切换，区分硬件与软件责任。|函数调用、异常中断与任务上下文的保存责任。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/uart-gpio/subtitle|从寄存器语义推进到初始化与引脚行为。|寄存器访问、设备初始化与引脚行为。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/interrupts/subtitle|建立计时、使能、服务、清源与返回闭环。|计时、中断使能、服务、清源与返回流程。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/i2c/subtitle|从线路、FIFO 和控制寄存器到器件读取。|I2C 线路、FIFO、控制寄存器与 EEPROM 读取。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/spi/subtitle|把控制器事务和外部设备协议分开。|SPI 控制器事务与 NOR、SD 设备协议。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/dma/subtitle|理解搬运提交、完成、限流与故障门槛。|数据搬运提交、完成、流量管理与本地执行条件。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/stream-io/subtitle|按设备追踪控制、数据、时钟及验证条件。|串行链路、显示与 USB 的控制、数据和验证条件。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/ara/subtitle|分清请求、应答、CPU 提交和实际完成。|向量请求、应答、CPU 提交与执行完成的协作关系。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/vector/subtitle|用同一数组比较汇编、intrinsics 和自动向量化。|数组运算的汇编、intrinsics 与自动向量化实现。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/sharing/subtitle|建立可见性、所有权和有界恢复协议。|共享数据的可见性、所有权与交接协议。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/rtos/subtitle|沿两个任务的运行、阻塞和唤醒理解实时系统。|任务运行、阻塞、唤醒与同步的状态转换。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/virtual-memory/subtitle|从物理布局走到虚拟地址，再辨认设备地址。|物理布局、虚拟地址翻译与设备地址语义。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/linux/subtitle|从平台固件到第一个用户进程，解释每次交接。|平台固件、内核与首个用户进程的启动关系。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/os-devices/subtitle|比较裸机、RTOS和Linux的同一次设备使用。|裸机、RTOS 与 Linux 的设备调用和缓冲区管理。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/integration/subtitle|从独立 Reg 单元逐步进入系统。|独立 Reg 设备与系统控制、数据及中断接口。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/ddr/subtitle|从平台初始化到软件可用建立交付条件。|DDR 平台初始化、访问放行与接口交付条件。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/accelerators/subtitle|逐 IP 明确接口、缓冲、跨域和验收交付。|图像处理 IP 的接口、缓冲、跨域与集成条件。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/models/subtitle|用透明假设衡量 Ara/NPU 协作成本。|明确假设下的 Ara/NPU 协作与数据搬运成本。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/clocks/subtitle|区分时钟域、使能、同步器和平台时钟源。|时钟域、使能、同步器与平台时钟源。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/reset/subtitle|从请求生命周期定义复位、就绪与恢复。|复位、平台就绪与在途事务的生命周期。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/power/subtitle|区分现有 RTL 边界和待实现的电源契约。|现有 RTL 的电源边界与候选低功耗契约。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/asic-memory/title|从VRF实例到SRAM宏接口|Ara VRF 与 SRAM 宏接口|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/asic-memory/subtitle|沿真实消费者推演容量、时序与技术映射。|VRF 消费者的容量、时序与候选技术映射。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/cdc-rdc/subtitle|按信号和协议选择同步机制，保持任务生命周期。|跨域信号同步、事务传输与生命周期协调。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/physical-interfaces/title|从逻辑信号到PAD、封装与设备|外设逻辑接口、PAD 与封装连接|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/physical-interfaces/subtitle|沿I2C连接解释方向、电气和板级责任。|I2C 连接的信号方向、电气条件与板级职责。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/timing-physical/subtitle|沿存储接口路径理解约束、分析和布局影响。|存储接口路径的时序约束、分析与布局影响。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/manufacturing-test/subtitle|区分功能行为与可制造测试的交付。|Scan、存储测试与功能验证的交付范围。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/silicon-bringup/subtitle|从早期可见状态逐步建立存储和计算证据。|首硅早期状态观测与存储、计算能力的分阶段验证。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/future/subtitle|冻结可搬迁输入并形成分阶段实现证据。|固定配置、可搬迁输入与 ASIC 分阶段验收。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/simulation/subtitle|按阶段检查输入、运行、数值和退出。|仿真输入、目标运行、结果数据与退出判据。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/measurement/subtitle|明确计时边界、数据条件和可重复的比较。|计时边界、数据条件与可重复的性能比较。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/labs/subtitle|六项有明确输入、产物和判据的连续实践。|六项连续实验与系统推演的输入、步骤和判据。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/registers/subtitle|本地头文件中的偏移和字段；访问语义回到对应设备章。|本地寄存器偏移、字段与对应设备访问语义。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/software-debug/subtitle|按最早未完成阶段定位装载、初始化和运行问题。|装载、初始化与软件运行问题的阶段定位。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/peripheral-debug/subtitle|按应用、寄存器和线路定位症状，保留已知问题证据。|外设应用、寄存器与线路症状的分层诊断。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/vector-debug/subtitle|分开构建、执行、访存和结果证据。|Ara/RVV 构建、执行、访存与结果的诊断证据。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/system-debug/subtitle|按症状追踪就绪、事务、数据与证据边界。|平台就绪、事务执行、数据与测量问题的定位。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|
|learning/scripts/pages.json#pages/os-debug/subtitle|核对镜像、平台描述和上下文支持的真实边界。|OS 镜像、平台描述与上下文支持的适用边界。|以对应技术对象及关系概括本页范围，取消口语或授课指令；不扩大实现状态|

## 必要标题引用同步

只同步首页章节导航中的正式名称/副标题和UART正文的小节链接文字；非标题教学解释不作全局词语替换。当前关联Markdown没有需要改名的章节级标题；旧报告中的原标题属于历史记录，保持原样。

|文件/位置|旧可见文字|新可见文字|次数|
|---|---|---|---|
|learning/content/index.html#chapter-list|沿取指、数组与字符输出辨认模块职责。|取指、数组计算与字符输出中的 SoC 模块协作。|1|
|learning/content/index.html#chapter-list|先掌握指令、状态、特权与存储接口。|指令集、处理器状态、特权级与存储接口。|1|
|learning/content/index.html#chapter-list|按真实字段及消费者建立自洽组合。|硬件字段、参数消费者与软件配置的一致性。|1|
|learning/content/index.html#chapter-list|从对象、调用和初始化理解存储布局。|C 对象、函数调用、初始化与存储布局。|1|
|learning/content/index.html#chapter-list|让同一数组程序形成可解释的装载产物。|源文件、对象文件、链接布局与 ELF 装载产物。|1|
|learning/content/index.html#chapter-list|分别追踪 ROM 服务、自主加载和应用入口。|ROM 服务、程序装载与应用入口的执行关系。|1|
|learning/content/index.html#chapter-list|核实外部调试接管的真实等待条件。|外部调试、程序装载与执行接管条件。|1|
|learning/content/index.html#chapter-list|分别核对路由窗口、实际容量和 CPU 属性。|地址路由窗口、实际资源容量与 CPU 访问属性。|1|
|learning/content/index.html#chapter-list|沿真实握手语义理解一笔读写事务。|AXI 读写事务的通道握手与完成语义。|1|
|learning/content/index.html#chapter-list|追踪译码、仲裁、W 路由、ID 与响应。|地址译码、仲裁、写数据路由与 ID 响应关系。|1|
|learning/content/index.html#chapter-list|解释位宽、协议、ID 转换及跨域边界。|位宽、协议、ID 转换与跨时钟域接口。|1|
|learning/content/index.html#chapter-list|区分缓存副本、地址别名与共享物理阵列。|缓存副本、地址别名与共享物理阵列。|1|
|learning/content/index.html#chapter-list|从函数调用到trap和任务切换，区分硬件与软件责任。|函数调用、异常中断与任务上下文的保存责任。|1|
|learning/content/index.html#chapter-list|从寄存器语义推进到初始化与引脚行为。|寄存器访问、设备初始化与引脚行为。|1|
|learning/content/index.html#chapter-list|建立计时、使能、服务、清源与返回闭环。|计时、中断使能、服务、清源与返回流程。|1|
|learning/content/index.html#chapter-list|从线路、FIFO 和控制寄存器到器件读取。|I2C 线路、FIFO、控制寄存器与 EEPROM 读取。|1|
|learning/content/index.html#chapter-list|把控制器事务和外部设备协议分开。|SPI 控制器事务与 NOR、SD 设备协议。|1|
|learning/content/index.html#chapter-list|理解搬运提交、完成、限流与故障门槛。|数据搬运提交、完成、流量管理与本地执行条件。|1|
|learning/content/index.html#chapter-list|按设备追踪控制、数据、时钟及验证条件。|串行链路、显示与 USB 的控制、数据和验证条件。|1|
|learning/content/index.html#chapter-list|分清请求、应答、CPU 提交和实际完成。|向量请求、应答、CPU 提交与执行完成的协作关系。|1|
|learning/content/index.html#chapter-list|用同一数组比较汇编、intrinsics 和自动向量化。|数组运算的汇编、intrinsics 与自动向量化实现。|1|
|learning/content/index.html#chapter-list|建立可见性、所有权和有界恢复协议。|共享数据的可见性、所有权与交接协议。|1|
|learning/content/index.html#chapter-list|沿两个任务的运行、阻塞和唤醒理解实时系统。|任务运行、阻塞、唤醒与同步的状态转换。|1|
|learning/content/index.html#chapter-list|从物理布局走到虚拟地址，再辨认设备地址。|物理布局、虚拟地址翻译与设备地址语义。|1|
|learning/content/index.html#chapter-list|从平台固件到第一个用户进程，解释每次交接。|平台固件、内核与首个用户进程的启动关系。|1|
|learning/content/index.html#chapter-list|比较裸机、RTOS和Linux的同一次设备使用。|裸机、RTOS 与 Linux 的设备调用和缓冲区管理。|1|
|learning/content/index.html#chapter-list|从独立 Reg 单元逐步进入系统。|独立 Reg 设备与系统控制、数据及中断接口。|1|
|learning/content/index.html#chapter-list|从平台初始化到软件可用建立交付条件。|DDR 平台初始化、访问放行与接口交付条件。|1|
|learning/content/index.html#chapter-list|逐 IP 明确接口、缓冲、跨域和验收交付。|图像处理 IP 的接口、缓冲、跨域与集成条件。|1|
|learning/content/index.html#chapter-list|用透明假设衡量 Ara/NPU 协作成本。|明确假设下的 Ara/NPU 协作与数据搬运成本。|1|
|learning/content/index.html#chapter-list|区分时钟域、使能、同步器和平台时钟源。|时钟域、使能、同步器与平台时钟源。|1|
|learning/content/index.html#chapter-list|从请求生命周期定义复位、就绪与恢复。|复位、平台就绪与在途事务的生命周期。|1|
|learning/content/index.html#chapter-list|区分现有 RTL 边界和待实现的电源契约。|现有 RTL 的电源边界与候选低功耗契约。|1|
|learning/content/index.html#chapter-list|从VRF实例到SRAM宏接口|Ara VRF 与 SRAM 宏接口|1|
|learning/content/index.html#chapter-list|沿真实消费者推演容量、时序与技术映射。|VRF 消费者的容量、时序与候选技术映射。|1|
|learning/content/index.html#chapter-list|按信号和协议选择同步机制，保持任务生命周期。|跨域信号同步、事务传输与生命周期协调。|1|
|learning/content/index.html#chapter-list|从逻辑信号到PAD、封装与设备|外设逻辑接口、PAD 与封装连接|1|
|learning/content/index.html#chapter-list|沿I2C连接解释方向、电气和板级责任。|I2C 连接的信号方向、电气条件与板级职责。|1|
|learning/content/index.html#chapter-list|沿存储接口路径理解约束、分析和布局影响。|存储接口路径的时序约束、分析与布局影响。|1|
|learning/content/index.html#chapter-list|区分功能行为与可制造测试的交付。|Scan、存储测试与功能验证的交付范围。|1|
|learning/content/index.html#chapter-list|从早期可见状态逐步建立存储和计算证据。|首硅早期状态观测与存储、计算能力的分阶段验证。|1|
|learning/content/index.html#chapter-list|冻结可搬迁输入并形成分阶段实现证据。|固定配置、可搬迁输入与 ASIC 分阶段验收。|1|
|learning/content/index.html#chapter-list|按阶段检查输入、运行、数值和退出。|仿真输入、目标运行、结果数据与退出判据。|1|
|learning/content/index.html#chapter-list|明确计时边界、数据条件和可重复的比较。|计时边界、数据条件与可重复的性能比较。|1|
|learning/content/uart-gpio.html#uart-recovery|<a href="#uart-recovery">本例执行条件</a>|<a href="#uart-recovery">UART 示例的执行条件</a>|1|

系统教材的实际技术实施结果仍见[主管实施报告](L01_System_Textbook_Implementation_2026-10-08.md)，M01/P01手册及既有目标验证缺口保持原状态。

## 修正后发布验收结果

以下命令均在仓库根实际执行，退出码0；证据目录新建，未覆盖系统教材实施阶段或更早记录。

|检查|结果|
|---|---|
|build_registers.py / build_site.py|12组429项寄存器；51主页面+20旧入口。寄存器数据完全保留|
|check_titles.py|664项全量清单；319改名与45引用同步；51页非标题内容/链接目标/顺序保护通过。新增--out-dir后再次在final-protection检查通过|
|check_site.py|71 HTML、5068本地链接/资源、108 SVG XML；标题/H1/导航/TOC/面包屑/上下章和Markdown锚点通过|
|check_structure.py --check-generated|[生成检查](learning/evidence/title-style-20261008/release-generated/checks.txt)：九篇42章、373原迁移、143产物临时重生成一致，37结构SVG及manifest一致；429寄存器数据哈希经唯一批准标题归一化后不变|
|preview_structure_site.py|[浏览器检查](learning/evidence/title-style-20261008/release-browser/browser.txt)：51页桌面/手机、12无脚本页、199跨页旧书签；交互、图片、429项寄存器查询通过，无页面横向溢出/JS异常/网络渲染依赖|
|主管截图复核|查看traps手机版、physical-interfaces手机版、asic-memory桌面与measurement手机版，正式目录、较长标题和副标题的断行/布局可读；这是4张视觉抽查，自动布局检查覆盖全站|
|最终输入保护|[final-protection](reviews/L01_title_style_20261008/final-protection/check-result.json)：3080原文件中2971不变，109项授权变化；全站非标题正文不变，Git分支/HEAD不变，无docs_codex外修改；git diff --check退出0|

当前参考Markdown中未找到两个改名章标题的旧可见引用；历史报告、图中原文字、自测问句均按范围保留。网站页头仍链接系统实施证据入口，该入口的主管报告已明确链接本标题修正结果，原检查截图不冒充新版本截图。
