import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  AlertTriangle, Clock, FileCode, Layers, Zap, GitBranch, TestTube,
  CheckCircle2, ArrowRight, Workflow, Package, Gauge, BookOpen,
} from 'lucide-react'

type Priority = 'P0' | 'P1' | 'P2' | 'P3'
type Status = 'ready' | 'in-progress' | 'planned'

interface RoadmapItem {
  id: string
  title: string
  priority: Priority
  status: Status
  effort: string
  description: string
  problem: string
  solution: string
  files: string[]
  impact: string
  icon: React.ReactNode
}

const roadmapData: RoadmapItem[] = [
  {
    id: 'dead-code',
    title: '清理死代码与架构违规',
    priority: 'P0',
    status: 'ready',
    effort: '1-2 天',
    description: '移除无效代码、修复层依赖违规',
    problem: 'tkinter_ui_framework.py 和 iuiframework.py 等文件无人引用但仍在维护；i18n/preferences_dialog.py 反向依赖 main 层，破坏了分层架构。',
    solution: '删除 tkinter_ui_framework.py 和 iuiframework.py；创建 i18n 专用的配置对话框接口，消除对 main 层的反向依赖。',
    files: [
      'src/battery_analysis/ui/frameworks/tkinter_ui_framework.py',
      'src/battery_analysis/ui/interfaces/iuiframework.py',
      'src/battery_analysis/i18n/preferences_dialog.py',
    ],
    impact: '消除技术债务，降低认知负荷，修复架构违规',
    icon: <FileCode className="w-5 h-5" />,
  },
  {
    id: 'utils-split',
    title: 'utils 包拆分与层修复',
    priority: 'P0',
    status: 'ready',
    effort: '2-3 天',
    description: '将 4187 行的 utils 包拆分为职责清晰的模块',
    problem: 'utils 包 4187 行代码混合作者、处理、读取逻辑，且反向依赖 main 层 (imports main_window 等)，导致循环依赖风险。',
    solution: '拆分为 writers/、processors/、readers/ 三个独立子包，各自承担单一职责；通过依赖注入消除对 main 层的编译期依赖。',
    files: [
      'src/battery_analysis/utils/writers/',
      'src/battery_analysis/utils/processors/',
      'src/battery_analysis/utils/readers/',
    ],
    impact: '消除循环依赖，提升可测试性，降低单包复杂度',
    icon: <Package className="w-5 h-5" />,
  },
  {
    id: 'main-window',
    title: 'main_window.py 瘦身',
    priority: 'P1',
    status: 'planned',
    effort: '2-3 天',
    description: '将 852 行 / 69 方法的 main_window.py 拆分到子模块',
    problem: 'main_window.py 852 行、69 个方法，包含 UI 初始化、事件处理、状态管理、日志等混杂职责；_get_component 使用 8 个串行 except 子句。',
    solution: '按职责拆分：MainWindow 保持协调，UI 构建→MainViewBuilder，事件→MainEventHandler，状态→MainStateManager，日志→LogPanelController。',
    files: [
      'src/battery_analysis/main/main_window.py',
    ],
    impact: '降低单文件复杂度至 <400 行，提升可维护性',
    icon: <Layers className="w-5 h-5" />,
  },
  {
    id: 'clean-arch',
    title: 'Clean Architecture 层充实',
    priority: 'P1',
    status: 'planned',
    effort: '3-4 天',
    description: '充实 domain/application 层，建立可靠边界',
    problem: 'domain 和 application 层几乎为空，业务逻辑散落在 infrastructure 和 main 层中，领域概念没有显式建模。',
    solution: '识别核心领域实体 (BatterySample, TestResult, ReportConfig) 并建模到 domain 层；将业务规则提取到 application 层的 use-case 中。',
    files: [
      'src/battery_analysis/domain/',
      'src/battery_analysis/application/',
    ],
    impact: '业务逻辑集中化，架构边界清晰，领域知识显式化',
    icon: <BookOpen className="w-5 h-5" />,
  },
  {
    id: 'service-simplify',
    title: 'Service Container + Event Bus 简化',
    priority: 'P2',
    status: 'planned',
    effort: '2-3 天',
    description: '精简 741 行 ServiceContainer 和 448 行 EventBus',
    problem: 'ServiceContainer 741 行，支持复杂 DI 但项目实际只需要简单服务注册；EventBus 448 行，大量功能未被使用。',
    solution: '简化 ServiceContainer 为核心 DI 功能（去除非必要的生命周期管理），EventBus 保留核心发布/订阅接口。',
    files: [
      'src/battery_analysis/main/services/service_container/container.py',
      'src/battery_analysis/main/services/event_bus.py',
    ],
    impact: '减少约 50% 基础设施代码，降低维护成本',
    icon: <Zap className="w-5 h-5" />,
  },
  {
    id: 'init-pipeline',
    title: '初始化流水线整合',
    priority: 'P2',
    status: 'planned',
    effort: '1-2 天',
    description: '将 12 步初始化流程压缩至 4 个阶段',
    problem: '12 步初始化过于细碎，启动流程难以理解和调试，各步骤间顺序依赖不透明。',
    solution: '整合为 4 阶段：环境准备 → 核心服务 → UI 构建 → 启动完成，每阶段内部可并行执行。',
    files: [
      'src/battery_analysis/main/init_pipeline.py',
    ],
    impact: '启动流程清晰化，便于调试与扩展',
    icon: <GitBranch className="w-5 h-5" />,
  },
  {
    id: 'test-coverage',
    title: '测试覆盖补齐',
    priority: 'P3',
    status: 'planned',
    effort: '3-4 天',
    description: '为 6 个未覆盖模块补充测试',
    problem: '6 个核心模块无测试覆盖：utils 包（特别是 excel_report_writer）、main_window、i18n、event_bus、command 模块、pipeline 初始化。',
    solution: '按优先级分批补充：先 P0/P1 模块（utils、main_window），再基础设施（event_bus、pipeline），最后工具类。',
    files: [
      'tests/battery_analysis/',
    ],
    impact: '测试覆盖率目标 >60%，降低回归风险',
    icon: <TestTube className="w-5 h-5" />,
  },
]

const priorityColors: Record<Priority, string> = {
  P0: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  P1: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  P2: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  P3: 'bg-slate-100 text-slate-600 dark:bg-slate-800/30 dark:text-slate-400',
}

const statusConfig: Record<Status, { label: string; className: string }> = {
  'ready': { label: '可开始', className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  'in-progress': { label: '进行中', className: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  'planned': { label: '规划中', className: 'bg-slate-100 text-slate-600 dark:bg-slate-800/30 dark:text-slate-400' },
}

const allPriorities: Priority[] = ['P0', 'P1', 'P2', 'P3']

function SummaryCards() {
  const totalEffort = roadmapData.reduce((acc, item) => {
    const days = parseInt(item.effort.split('-')[1] || item.effort.split('-')[0])
    return acc + days
  }, 0)

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">待解决问题</CardTitle>
          <AlertTriangle className="w-4 h-4 text-red-500" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">7</div>
          <p className="text-xs text-muted-foreground mt-1">
            P0: 2 · P1: 2 · P2: 2 · P3: 1
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">预估工作量</CardTitle>
          <Clock className="w-4 h-4 text-amber-500" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">13-16 天</div>
          <p className="text-xs text-muted-foreground mt-1">
            约 {Math.ceil(totalEffort / 2)} 人周
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">测试缺口</CardTitle>
          <TestTube className="w-4 h-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">6</div>
          <p className="text-xs text-muted-foreground mt-1">
            模块无测试覆盖
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">当前进度</CardTitle>
          <Gauge className="w-4 h-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">2/7</div>
          <Progress value={28.5} className="mt-2" />
          <p className="text-xs text-muted-foreground mt-1">
            P0 项已可开始
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

function ArchitectureDiagram() {
  return (
    <Card className="mb-8 overflow-hidden">
      <CardHeader className="border-b pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Workflow className="w-4 h-4" />
          架构依赖现状 → 目标
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid grid-cols-2 gap-8">
          {/* Current State */}
          <div>
            <h4 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-3 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              当前状态
            </h4>
            <div className="space-y-1.5 text-sm">
              <div className="flex items-center gap-2 p-2 rounded bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900">
                <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
                <span>main</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
                <span>ui (含死代码)</span>
                <Badge variant="outline" className="text-[10px] h-4">P0</Badge>
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
                <span>utils (4187行, 反向依赖)</span>
                <Badge variant="outline" className="text-[10px] h-4">P0</Badge>
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-orange-500 shrink-0" />
                <span>infrastructure</span>
              </div>
              <div className="border-l-2 border-dashed border-slate-300 dark:border-slate-600 h-3 ml-[17px]" />
              <div className="flex items-center gap-2 p-2 rounded bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 ml-6">
                <span className="w-2 h-2 rounded-full bg-slate-400 shrink-0" />
                <span className="text-muted-foreground">application (几乎为空)</span>
                <Badge variant="outline" className="text-[10px] h-4">P1</Badge>
              </div>
              <div className="border-l-2 border-dashed border-slate-300 dark:border-slate-600 h-3 ml-[17px]" />
              <div className="flex items-center gap-2 p-2 rounded bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 ml-6">
                <span className="w-2 h-2 rounded-full bg-slate-400 shrink-0" />
                <span className="text-muted-foreground">domain (几乎为空)</span>
                <Badge variant="outline" className="text-[10px] h-4">P1</Badge>
              </div>
              <div className="flex justify-center mt-3">
                <Badge variant="secondary" className="text-xs">
                  箭头方向: utils → main (违规反向依赖)
                </Badge>
              </div>
            </div>
          </div>

          {/* Target State */}
          <div>
            <h4 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-3 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              目标状态
            </h4>
            <div className="space-y-1.5 text-sm">
              <div className="flex items-center gap-2 p-2 rounded bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900">
                <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                <span>main</span>
              </div>
              <div className="border-l-2 border-green-300 dark:border-green-700 h-1 ml-[17px]" />
              <div className="flex items-center gap-2 p-2 rounded bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                <span>ui (精简)</span>
              </div>
              <div className="border-l-2 border-green-300 dark:border-green-700 h-1 ml-[17px]" />
              <div className="flex items-center gap-2 p-2 rounded bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                <span>infrastructure</span>
              </div>
              <div className="border-l-2 border-green-300 dark:border-green-700 h-1 ml-[17px]" />
              <div className="flex items-center gap-2 p-2 rounded bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                <span>application (use-cases)</span>
              </div>
              <div className="border-l-2 border-green-300 dark:border-green-700 h-1 ml-[17px]" />
              <div className="flex items-center gap-2 p-2 rounded bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 ml-3">
                <span className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                <span>domain (实体 + 规则)</span>
              </div>
              <div className="flex justify-center mt-3">
                <Badge variant="secondary" className="text-xs">
                  箭头方向: main → infrastructure → domain (遵循依赖倒置)
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function RoadmapAccordion({ items }: { items: RoadmapItem[] }) {
  return (
    <Accordion type="single" collapsible className="w-full">
      {items.map((item) => (
        <AccordionItem key={item.id} value={item.id} className="border-b">
          <AccordionTrigger className="hover:no-underline py-4">
            <div className="flex items-center gap-3 text-left w-full">
              <div className="shrink-0 w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
                {item.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">{item.title}</div>
                <div className="text-xs text-muted-foreground mt-0.5">{item.description}</div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Badge className={`${priorityColors[item.priority]} border-none text-[11px]`}>
                  {item.priority}
                </Badge>
                <Badge variant="secondary" className={`${statusConfig[item.status].className} border-none text-[11px]`}>
                  {statusConfig[item.status].label}
                </Badge>
                <span className="text-xs text-muted-foreground whitespace-nowrap">{item.effort}</span>
              </div>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pl-12 pr-4 pb-2">
              <div>
                <h5 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">问题</h5>
                <p className="text-sm text-foreground">{item.problem}</p>
              </div>
              <div>
                <h5 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">解决方案</h5>
                <p className="text-sm text-foreground">{item.solution}</p>
              </div>
              <div>
                <h5 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">影响范围</h5>
                <p className="text-sm text-foreground">{item.impact}</p>
              </div>
              <div>
                <h5 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">涉及文件</h5>
                <div className="flex flex-wrap gap-1.5">
                  {item.files.map((f) => (
                    <Badge key={f} variant="secondary" className="text-[11px] font-mono">
                      {f}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )
}

function ExecutionPlan() {
  return (
    <Card className="mt-8">
      <CardHeader className="border-b pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <GitBranch className="w-4 h-4" />
          执行计划
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-0">
          {[
            {
              phase: 'Phase 1',
              title: '基础设施清理',
              items: ['清理死代码 (P0)', 'utils 包拆分 (P0)'],
              duration: '3-5 天',
              color: 'bg-red-500',
            },
            {
              phase: 'Phase 2',
              title: '架构重构',
              items: ['main_window 瘦身 (P1)', 'Clean Architecture 充实 (P1)'],
              duration: '5-7 天',
              color: 'bg-amber-500',
            },
            {
              phase: 'Phase 3',
              title: '基础设施精简',
              items: ['ServiceContainer 简化 (P2)', '初始化流水线整合 (P2)'],
              duration: '3-5 天',
              color: 'bg-blue-500',
            },
            {
              phase: 'Phase 4',
              title: '质量加固',
              items: ['测试覆盖补齐 (P3)'],
              duration: '3-4 天',
              color: 'bg-slate-500',
            },
          ].map((phase, idx) => (
            <div key={phase.phase} className="relative pb-6 last:pb-0">
              {idx < 3 && (
                <div className="absolute left-[19px] top-10 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700" />
              )}
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-full ${phase.color} flex items-center justify-center text-white text-xs font-bold shrink-0 mt-0.5`}>
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-semibold">{phase.phase}</span>
                    <Badge variant="outline" className="text-[10px]">{phase.duration}</Badge>
                  </div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">{phase.title}</p>
                  <ul className="space-y-1">
                    {phase.items.map((item) => (
                      <li key={item} className="text-sm text-muted-foreground flex items-center gap-2">
                        <ArrowRight className="w-3 h-3" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('all')

  const filteredItems = activeTab === 'all'
    ? roadmapData
    : roadmapData.filter((item) => item.priority === activeTab)

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="max-w-5xl mx-auto px-4 py-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Gauge className="w-6 h-6 text-slate-700 dark:text-slate-300" />
            <h1 className="text-2xl font-bold tracking-tight">Battery Analysis 优化路线图</h1>
          </div>
          <p className="text-sm text-muted-foreground">
            基于 Clean Architecture 审计发现的 7 项改进措施，按优先级排列的全面优化计划
          </p>
        </div>

        {/* Summary Cards */}
        <SummaryCards />

        {/* Execution Plan Timeline */}
        <ExecutionPlan />

        {/* Architecture Diagram */}
        <ArchitectureDiagram />

        {/* Detailed Roadmap */}
        <Card className="mt-8">
          <CardHeader className="border-b pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <GitBranch className="w-4 h-4" />
                详细优化项
              </CardTitle>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="h-8">
                  <TabsTrigger value="all" className="text-xs px-3">全部</TabsTrigger>
                  {allPriorities.map((p) => (
                    <TabsTrigger key={p} value={p} className="text-xs px-3">{p}</TabsTrigger>
                  ))}
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            <RoadmapAccordion items={filteredItems} />
            {filteredItems.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-8">
                暂无此优先级的优化项
              </p>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <Alert className="mt-8">
          <AlertTriangle className="w-4 h-4" />
          <AlertDescription className="text-sm">
            建议按 Phase 1 → 4 顺序执行，每个 Phase 完成后运行完整测试套件验证无回归。
            P0 项可直接开始，P1 项需要设计评审，P2/P3 可穿插进行。
          </AlertDescription>
        </Alert>
      </div>
    </div>
  )
}
