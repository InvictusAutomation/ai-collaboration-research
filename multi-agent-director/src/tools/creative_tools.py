"""
上下文网络与创意碰撞机制
Multi-Agent 协作的核心基础设施
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio


# ==================== 上下文网络 ====================

@dataclass
class ContextNode:
    """上下文节点"""
    id: str
    type: str  # theme, character, scene, dialogue, etc.
    content: Any
    connections: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)
    
    def connect(self, node_id: str):
        """建立连接"""
        self.connections.add(node_id)


class ContextNetwork:
    """
    创作上下文网络
    将所有创作元素连接成网状结构
    """
    
    def __init__(self):
        self.nodes: Dict[str, ContextNode] = {}
        self.node_index: Dict[str, List[str]] = defaultdict(list)  # type -> node_ids
    
    def add_node(self, node: ContextNode):
        """添加节点"""
        self.nodes[node.id] = node
        self.node_index[node.type].append(node.id)
    
    def connect(self, node_id1: str, node_id2: str):
        """连接两个节点"""
        if node_id1 in self.nodes and node_id2 in self.nodes:
            self.nodes[node_id1].connect(node_id2)
            self.nodes[node_id2].connect(node_id1)
    
    def get_related(self, node_id: str, depth: int = 1) -> List[ContextNode]:
        """获取相关节点"""
        if node_id not in self.nodes:
            return []
        
        related = []
        visited = {node_id}
        queue = [(node_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            if current_depth >= depth:
                continue
            
            for connected_id in self.nodes[current_id].connections:
                if connected_id not in visited:
                    visited.add(connected_id)
                    related.append(self.nodes[connected_id])
                    queue.append((connected_id, current_depth + 1))
        
        return related
    
    def get_by_type(self, node_type: str) -> List[ContextNode]:
        """按类型获取节点"""
        return [self.nodes[nid] for nid in self.node_index.get(node_type, [])]
    
    def visualize(self) -> str:
        """可视化网络结构"""
        lines = ["Context Network:", "=" * 50]
        
        for node_type in self.node_index:
            nodes = self.node_index[node_type]
            lines.append(f"\n[{node_type.upper()}] ({len(nodes)} nodes)")
            for node in nodes[:5]:  # 只显示前5个
                connections = len(node.connections)
                lines.append(f"  - {node.id} ({connections} connections)")
        
        return "\n".join(lines)


# ==================== 创意碰撞机制 ====================

@dataclass
class CreativePerspective:
    """创意视角"""
    agent_name: str
    agent_role: str
    perspective: str
    keywords: List[str] = field(default_factory=list)
    weight: float = 1.0


class CreativeCollision:
    """
    创意碰撞机制
    让多个 Agent 从不同角度思考并产生创意叠加
    """
    
    def __init__(self):
        self.perspectives: List[CreativePerspective] = []
        self.collision_log: List[Dict] = []
    
    def add_perspective(self, perspective: CreativePerspective):
        """添加视角"""
        self.perspectives.append(perspective)
    
    async def collide(self, topic: str, context: ContextNetwork) -> Dict:
        """
        执行创意碰撞
        
        过程:
        1. 各 Agent 独立思考
        2. 观点交叉
        3. 灵感叠加
        4. 整合输出
        """
        # 阶段1: 独立思考
        individual_thoughts = await self._independent_thinking(topic, context)
        
        # 阶段2: 观点交叉
        cross_pollination = await self._cross_pollinate(individual_thoughts)
        
        # 阶段3: 灵感叠加
        synthesized = await self._synthesize(cross_pollination)
        
        # 记录碰撞过程
        self.collision_log.append({
            "topic": topic,
            "individual": individual_thoughts,
            "cross": cross_pollination,
            "synthesized": synthesized
        })
        
        return synthesized
    
    async def _independent_thinking(self, topic: str, context: ContextNetwork) -> Dict:
        """独立思考阶段"""
        thoughts = {}
        
        # 获取相关上下文
        themes = context.get_by_type("theme")
        characters = context.get_by_type("character")
        
        for perspective in self.perspectives:
            # 根据角色生成独特视角
            if perspective.agent_role == "screenwriter":
                thought = f"从故事角度: {topic} 的核心冲突是什么?"
            elif perspective.agent_role == "director":
                thought = f"从视觉角度: 如何用镜头语言表达 {topic}?"
            elif perspective.agent_role == "character":
                thought = f"从人物角度: {topic} 如何影响角色?"
            elif perspective.agent_role == "music":
                thought = f"从音乐角度: {topic} 应该有什么情绪?"
            elif perspective.agent_role == "reviewer":
                thought = f"从审查角度: {topic} 有什么潜在问题?"
            
            thoughts[perspective.agent_name] = {
                "perspective": perspective.perspective,
                "thought": thought,
                "keywords": perspective.keywords
            }
        
        return thoughts
    
    async def _cross_pollinate(self, thoughts: Dict) -> Dict:
        """观点交叉阶段 - 让不同视角互相激发"""
        cross = {}
        
        perspective_keys = list(thoughts.keys())
        
        for i, key1 in enumerate(perspective_keys):
            for key2 in perspective_keys[i+1:]:
                # 找出两个视角的关键词重叠
                kw1 = set(thoughts[key1]["keywords"])
                kw2 = set(thoughts[key2]["keywords"])
                common = kw1.intersection(kw2)
                
                if common:
                    # 发现共同点，创建融合思考
                    cross[f"{key1}+{key2}"] = {
                        "synthesis": f"结合 {thoughts[key1]['perspective']} 和 {thoughts[key2]['perspective']}",
                        "common_keywords": list(common),
                        "new_perspective": f"当 {key1} 的 {list(kw1)[0]} 遇到 {key2} 的 {list(kw2)[0]}"
                    }
        
        return cross
    
    async def _synthesize(self, cross_pollination: Dict) -> Dict:
        """整合阶段"""
        # 整合所有思考，形成最终创意
        synthesis = {
            "core_concepts": [],
            "visual_ideas": [],
            "character_ideas": [],
            "emotional_arcs": [],
            "unique_perspectives": []
        }
        
        # 从交叉思考中提取
        for key, value in cross_pollination.items():
            synthesis["unique_perspectives"].append(value["new_perspective"])
        
        return synthesis


# ==================== 因果推理链 ====================

@dataclass
class CausalityNode:
    """因果节点"""
    cause: str
    effect: str
    confidence: float
    depth: int  # 推理深度


class CausalityReasoner:
    """
    因果推理器
    Multi-Agent 协作进行深层因果分析
    """
    
    def __init__(self):
        self.reasoning_chains: List[List[CausalityNode]] = []
    
    async def reason(self, question: str, agents: List[Any]) -> Dict:
        """
        执行因果推理
        
        多个 Agent 协作进行多层次因果分析:
        - Agent 1: 表层因果
        - Agent 2: 深层原因
        - Agent 3: 远因追溯
        - Agent 4: 社会因素
        - Agent 5: 哲学升华
        """
        chains = []
        
        # 多层推理
        surface = await self._surface_reason(question, agents[0])
        chains.append(surface)
        
        deep = await self._deep_reason(question, agents[1], surface)
        chains.append(deep)
        
        remote = await self._remote_reason(question, agents[2], deep)
        chains.append(remote)
        
        social = await self._social_reason(question, agents[3], remote)
        chains.append(social)
        
        philosophical = await self._philosophical_reason(question, agents[4], social)
        chains.append(philosophical)
        
        return {
            "question": question,
            "chains": chains,
            "summary": await self._summarize(chains)
        }
    
    async def _surface_reason(self, question: str, agent: Any) -> CausalityNode:
        """表层因果"""
        return CausalityNode(
            cause="表面直接原因",
            effect="表面结果",
            confidence=0.9,
            depth=1
        )
    
    async def _deep_reason(self, question: str, agent: Any, prev: CausalityNode) -> CausalityNode:
        """深层原因"""
        return CausalityNode(
            cause="深层心理动机",
            effect="行为模式",
            confidence=0.8,
            depth=2
        )
    
    async def _remote_reason(self, question: str, agent: Any, prev: CausalityNode) -> CausalityNode:
        """远因追溯"""
        return CausalityNode(
            cause="童年/成长经历",
            effect="深层性格",
            confidence=0.7,
            depth=3
        )
    
    async def _social_reason(self, question: str, agent: Any, prev: CausalityNode) -> CausalityNode:
        """社会因素"""
        return CausalityNode(
            cause="社会环境/文化",
            cause="价值观形成",
            confidence=0.6,
            depth=4
        )
    
    async def _philosophical_reason(self, question: str, agent: Any, prev: CausalityNode) -> CausalityNode:
        """哲学升华"""
        return CausalityNode(
            cause="人性/存在",
            effect="普遍意义",
            confidence=0.5,
            depth=5
        )
    
    async def _summarize(self, chains: List[CausalityNode]) -> str:
        """总结推理链"""
        summary = "因果推理链:\n"
        for i, chain in enumerate(chains):
            summary += f"\n{i+1}. {chain.cause} → {chain.effect}"
        return summary


# ==================== 迭代优化器 ====================

class IterativeOptimizer:
    """
    迭代优化器
    评估-优化循环
    """
    
    def __init__(self):
        self.iterations: List[Dict] = []
    
    async def optimize(
        self, 
        content: Any, 
        evaluators: List[Any], 
        generators: List[Any],
        max_iterations: int = 3
    ) -> Dict:
        """
        迭代优化流程
        
        循环:
        1. 评估 Agent 审查
        2. 生成 Agent 优化
        3. 检查是否达标
        """
        
        for i in range(max_iterations):
            # 评估
            evaluation = await self._evaluate(content, evaluators)
            
            if evaluation["approved"]:
                break
            
            # 优化
            content = await self._optimize(
                content, 
                evaluation["feedback"],
                generators
            )
            
            self.iterations.append({
                "iteration": i + 1,
                "evaluation": evaluation,
                "optimized": content
            })
        
        return {
            "final_content": content,
            "iterations": self.iterations,
            "converged": evaluation["approved"]
        }
    
    async def _evaluate(self, content: Any, evaluators: List[Any]) -> Dict:
        """评估内容"""
        feedback = []
        
        for evaluator in evaluators:
            # 审查并给出反馈
            review = {
                "agent": evaluator.name,
                "issues": ["问题1", "问题2"],
                "suggestions": ["建议1", "建议2"]
            }
            feedback.append(review)
        
        return {
            "approved": False,  # 假设需要优化
            "feedback": feedback,
            "overall_score": 7.5
        }
    
    async def _optimize(self, content: Any, feedback: List[Dict], generators: List[Any]) -> Any:
        """根据反馈优化"""
        # 汇总反馈
        all_suggestions = []
        for f in feedback:
            all_suggestions.extend(f.get("suggestions", []))
        
        # 让生成 Agent 优化
        optimized = f"{content}\n\n[已根据反馈优化]"
        
        return optimized


# ==================== 使用示例 ====================

async def main():
    """使用示例"""
    
    # 1. 创建上下文网络
    network = ContextNetwork()
    
    # 添加节点
    network.add_node(ContextNode(
        id="theme_1",
        type="theme",
        content="AI觉醒"
    ))
    network.add_node(ContextNode(
        id="character_1", 
        type="character",
        content="陪伴型AI"
    ))
    
    # 连接
    network.connect("theme_1", "character_1")
    
    print(network.visualize())
    
    # 2. 创意碰撞
    collision = CreativeCollision()
    collision.add_perspective(CreativePerspective(
        agent_name="编剧",
        agent_role="screenwriter",
        perspective="故事角度",
        keywords=["冲突", "转折", "节奏"]
    ))
    
    result = await collision.collide("AI觉醒", network)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
