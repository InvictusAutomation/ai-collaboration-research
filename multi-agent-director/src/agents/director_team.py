"""
导演创作 Agent 团队 - 核心实现
基于 Multi-Agent 最佳实践构建
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio


# ==================== Agent 基类 ====================

class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    SCREENWRITER = "screenwriter"
    DIRECTOR = "director"
    CHARACTER = "character"
    VISUAL = "visual"
    MUSIC = "music"
    VOICE = "voice"
    REVIEWER = "reviewer"


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str
    role: AgentRole
    description: str
    expertise: List[str]
    system_prompt: str
    model: str = "gpt-4o"


@dataclass
class Message:
    """Agent 间消息"""
    sender: str
    receiver: str
    content: Any
    type: str = "task"  # task, result, query, feedback
    metadata: Dict = field(default_factory=dict)


@dataclass
class Context:
    """创作上下文网络"""
    user_request: str
    theme: str = ""
    genre: str = ""
    tone: str = ""
    story_world: Dict = field(default_factory=dict)
    characters: Dict = field(default_factory=dict)
    scenes: Dict = field(default_factory=dict)
    memory: List[Dict] = field(default_factory=list)
    
    def add_memory(self, key: str, value: Any):
        """添加记忆到上下文网络"""
        self.memory.append({"key": key, "value": value})
    
    def get_related(self, key: str) -> List[Any]:
        """获取相关记忆"""
        return [m["value"] for m in self.memory if key in m.get("key", "")]


# ==================== Agent 基类 ====================

class BaseAgent:
    """Agent 基类"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.role = config.role
        self.expertise = config.expertise
        self.context = None
    
    async def think(self, prompt: str, context: Context) -> str:
        """思考"""
        # 构建系统提示
        system_prompt = f"""
{self.config.system_prompt}

你的专业领域: {', '.join(self.expertise)}
你的角色: {self.config.description}

当前创作上下文:
- 主题: {context.theme}
- 类型: {context.genre}
- 基调: {context.tone}
- 已有人物: {list(context.characters.keys())}
- 已有场景: {list(context.scenes.keys())}

请基于你的专业领域提供创意。
"""
        # 这里调用 LLM
        return f"[{self.name} 的思考]"
    
    async def execute(self, task: str, context: Context) -> Dict:
        """执行任务"""
        result = await self.think(task, context)
        return {
            "agent": self.name,
            "role": self.role.value,
            "result": result,
            "context_update": {}
        }
    
    async def receive_message(self, message: Message):
        """接收消息"""
        pass
    
    async def send_message(self, receiver: str, content: Any, msg_type: str = "task"):
        """发送消息"""
        return Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            type=msg_type
        )


# ==================== 专业化 Agent ====================

class DirectorAgent(BaseAgent):
    """总导演 Agent - 统筹协调"""
    
    def __init__(self):
        super().__init__(AgentConfig(
            name="总导演",
            role=AgentRole.ORCHESTRATOR,
            description="统筹全局，协调各 Agent 工作",
            expertise=["故事结构", "节奏把控", "创意整合"],
            system_prompt="你是资深导演兼编剧，能从全局角度把握创作方向。"
        ))
    
    async def orchestrate(self, user_request: str, agents: List[BaseAgent], context: Context) -> Dict:
        """统筹工作流程"""
        # 1. 理解用户意图
        context.user_request = user_request
        await self._parse_intent(user_request, context)
        
        # 2. 分发任务给各 Agent
        tasks = await self._decompose_tasks(user_request, agents, context)
        
        # 3. 收集结果
        results = await self._collect_results(tasks, agents, context)
        
        # 4. 整合创意
        final_result = await self._integrate_creative(results, context)
        
        return {
            "orchestrated": True,
            "result": final_result,
            "agents_activated": [a.name for a in agents]
        }
    
    async def _parse_intent(self, request: str, context: Context):
        """解析用户意图"""
        # 提取主题、类型、基调
        context.theme = self._extract_theme(request)
        context.genre = self._extract_genre(request)
        context.tone = self._extract_tone(request)
    
    async def _decompose_tasks(self, request: str, agents: List[BaseAgent], context: Context) -> List[Dict]:
        """分解任务"""
        tasks = []
        for agent in agents:
            if agent.role == AgentRole.SCREENWRITER:
                tasks.append({"agent": agent, "task": "创作故事结构"})
            elif agent.role == AgentRole.CHARACTER:
                tasks.append({"agent": agent, "task": "设计角色"})
            elif agent.role == AgentRole.VISUAL:
                tasks.append({"agent": agent, "task": "视觉设计"})
            # ... 更多任务分解
        return tasks
    
    async def _collect_results(self, tasks: List[Dict], agents: List[BaseAgent], context: Context) -> List[Dict]:
        """收集各 Agent 结果"""
        results = []
        for task in tasks:
            result = await task["agent"].execute(task["task"], context)
            results.append(result)
        return results
    
    async def _integrate_creative(self, results: List[Dict], context: Context) -> Dict:
        """整合创意"""
        # 融合各 Agent 的创意
        integrated = {
            "story": [],
            "characters": [],
            "visual": [],
            "music": [],
            "review": []
        }
        
        for result in results:
            role = result.get("role")
            if role == "screenwriter":
                integrated["story"].append(result.get("result"))
            elif role == "character":
                integrated["characters"].append(result.get("result"))
            # ... 更多整合
        
        return integrated


class ScreenwriterAgent(BaseAgent):
    """编剧 Agent"""
    
    def __init__(self):
        super().__init__(AgentConfig(
            name="✍️ 编剧",
            role=AgentRole.SCREENWRITER,
            description="负责剧本结构、对话、故事节奏",
            expertise=["剧本结构", "对话撰写", "故事节奏", "情节设计"],
            system_prompt="你是专业编剧，擅长构建引人入胜的故事。"
        ))
    
    async def write_script(self, context: Context, feedback: str = "") -> Dict:
        """撰写剧本"""
        prompt = f"""
基于以下信息撰写剧本:
- 主题: {context.theme}
- 类型: {context.genre}
- 基调: {context.tone}
- 角色: {context.characters}
{f'- 反馈: {feedback}' if feedback else ''}
"""
        
        result = await self.think(prompt, context)
        
        return {
            "script": result,
            "structure": self._extract_structure(result),
            "dialogue": self._extract_dialogue(result)
        }


class DirectorVisualAgent(BaseAgent):
    """分镜导演 Agent"""
    
    def __init__(self):
        super().__init__(AgentConfig(
            name="🎥 分镜导演",
            role=AgentRole.DIRECTOR,
            description="负责镜头语言、场景调度、视觉风格",
            expertise=["镜头语言", "场景调度", "视觉风格", "分镜设计"],
            system_prompt="你是资深分镜导演，擅长用视觉讲故事。"
        ))
    
    async def design_shots(self, script: Dict, context: Context) -> List[Dict]:
        """设计分镜"""
        shots = []
        
        # 为每个场景设计镜头
        for scene in context.scenes.values():
            shot = {
                "scene": scene.get("name"),
                "shots": [
                    {"type": "全景", "description": "建立场景"},
                    {"type": "中景", "description": "人物互动"},
                    {"type": "特写", "description": "情感表达"}
                ],
                "camera_movement": "横移",
                "duration": "5s"
            }
            shots.append(shot)
        
        return shots


class CharacterAgent(BaseAgent):
    """角色设计 Agent"""
    
    def __init__(self):
        super().__init__(AgentConfig(
            name="👤 角色设计",
            role=AgentRole.CHARACTER,
            description="负责人物塑造、关系构建、心理深度",
            expertise=["人物设定", "角色弧光", "关系构建", "心理分析"],
            system_prompt="你是角色设计大师，擅长创造有深度的角色。"
        ))
    
    async def create_character(self, name: str, role_type: str, context: Context) -> Dict:
        """创建角色"""
        # 分析已有角色，避免重复
        existing_chars = context.characters.values()
        
        # 构建新角色
        character = {
            "name": name,
            "type": role_type,
            "background": await self._generate_background(name, context),
            "motivation": await self._generate_motivation(name, context),
            "arc": await self._generate_arc(name, context),
            "relationships": await self._generate_relationships(name, existing_chars),
            "dialogue_style": await self._generate_dialogue_style(name)
        }
        
        return character
    
    async def _generate_background(self, name: str, context: Context) -> str:
        """生成背景"""
        return f"{name} 的背景故事..."


class ReviewerAgent(BaseAgent):
    """审查 Agent - 质量把关"""
    
    def __init__(self):
        super().__init__(AgentConfig(
            name="🔍 审查团队",
            role=AgentRole.REVIEWER,
            description="逻辑审查、创意评估、一致性检查",
            expertise=["逻辑分析", "创意评估", "质量把控", "一致性检查"],
            system_prompt="你是严格的创意审查员，确保作品质量。"
        ))
    
    async def review(self, content: Dict, context: Context) -> Dict:
        """审查内容"""
        reviews = {
            "logic": await self._check_logic(content, context),
            "creativity": await self._check_creativity(content, context),
            "consistency": await self._check_consistency(content, context),
            "quality": await self._check_quality(content, context)
        }
        
        # 生成改进建议
        suggestions = self._generate_suggestions(reviews)
        
        return {
            "reviews": reviews,
            "suggestions": suggestions,
            "approved": all(r["passed"] for r in reviews.values())
        }
    
    async def _check_logic(self, content: Dict, context: Context) -> Dict:
        """逻辑审查"""
        # 检查因果关系、情节合理性
        return {"passed": True, "issues": []}
    
    async def _check_creativity(self, content: Dict, context: Context) -> Dict:
        """创意评估"""
        # 检查是否有新意
        return {"passed": True, "score": 8.5}
    
    async def _check_consistency(self, content: Dict, context: Context) -> Dict:
        """一致性检查"""
        return {"passed": True, "issues": []}
    
    async def _check_quality(self, content: Dict, context: Context) -> Dict:
        """质量检查"""
        return {"passed": True, "score": 8.0}


# ==================== 团队管理器 ====================

class DirectorTeam:
    """导演创作团队管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.context = Context(user_request="")
        self._init_agents()
    
    def _init_agents(self):
        """初始化 Agent 团队"""
        self.agents["orchestrator"] = DirectorAgent()
        self.agents["screenwriter"] = ScreenwriterAgent()
        self.agents["director_visual"] = DirectorVisualAgent()
        self.agents["character"] = CharacterAgent()
        self.agents["reviewer"] = ReviewerAgent()
    
    async def create_project(self, user_request: str) -> Dict:
        """创建项目"""
        # 获取总导演
        orchestrator = self.agents["orchestrator"]
        
        # 获取所有执行 Agent
        executors = [
            self.agents["screenwriter"],
            self.agents["director_visual"],
            self.agents["character"],
            self.agents["reviewer"]
        ]
        
        # 协调工作
        result = await orchestrator.orchestrate(
            user_request=user_request,
            agents=executors,
            context=self.context
        )
        
        return result
    
    async def iterate(self, feedback: str) -> Dict:
        """迭代优化"""
        # 收集审查意见
        reviewer = self.agents["reviewer"]
        
        # 将反馈发送给相关 Agent
        screenwriter = self.agents["screenwriter"]
        updated_result = await screenwriter.write_script(
            context=self.context,
            feedback=feedback
        )
        
        return updated_result


# ==================== 使用示例 ====================

async def main():
    """使用示例"""
    team = DirectorTeam()
    
    # 创建项目
    result = await team.create_project(
        "帮我创作一个关于AI觉醒的科幻短片"
    )
    
    print("项目创建成功!")
    print(f"激活的 Agent: {result.get('agents_activated')}")
    
    # 迭代优化 (如果有反馈)
    # await team.iterate("让主角更复杂一些")

if __name__ == "__main__":
    asyncio.run(main())
