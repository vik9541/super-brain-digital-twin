# 📊 Social Network Analyzer - PHASE 2
# Анализ социальных нетей контактов

# Community detection, influencer identification, path finding

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Types of connections between contacts"""

    DIRECT = "direct"  # Same organization
    COLLEAGUES = "colleagues"  # Work together
    MEETING = "meeting"  # Met at event
    SOCIAL = "social"  # Social media connection
    FAMILY = "family"  # Family relation
    FREQUENT = "frequent"  # Frequent interaction
    PROXIMITY = "proximity"  # Same location


@dataclass
class Connection:
    """Connection between two contacts"""

    contact_id_1: str
    contact_id_2: str
    connection_type: ConnectionType
    strength: float = 1.0  # 0.0 to 1.0 (interaction frequency)
    weight: float = 1.0  # Calculated weight
    shared_attributes: List[str] = field(default_factory=list)
    first_interaction: datetime = None
    last_interaction: datetime = None
    interaction_count: int = 1


@dataclass
class ContactNode:
    """Node in the social network graph"""

    contact_id: str
    name: str
    organization: str
    location: str
    connections: List[Connection] = field(default_factory=list)
    influence_score: float = 0.0
    betweenness_centrality: float = 0.0
    degree_centrality: float = 0.0
    community_id: int = -1  # Community detection result


class SocialNetworkAnalyzer:
    """Главный анализатор социальных сетей"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.graph: Dict[str, ContactNode] = {}

    async def build_graph(self, contacts: List[Dict]) -> Dict[str, ContactNode]:
        """Построить граф социальных нетей"""

        # Создать вузлы
        for contact in contacts:
            if contact["id"] not in self.graph:
                self.graph[contact["id"]] = ContactNode(
                    contact_id=contact["id"],
                    name=f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                    organization=contact.get("organization", ""),
                    location=contact.get("location", ""),
                )

        # Найти связи
        for i, c1 in enumerate(contacts):
            for c2 in contacts[i + 1 :]:
                connection_type, strength, shared = self._detect_connection(c1, c2)

                if connection_type:
                    conn = Connection(
                        contact_id_1=c1["id"],
                        contact_id_2=c2["id"],
                        connection_type=connection_type,
                        strength=strength,
                        shared_attributes=shared,
                    )

                    # Односторонняя связь (добавляем в обе стороны)
                    self.graph[c1["id"]].connections.append(conn)
                    self.graph[c2["id"]].connections.append(
                        Connection(
                            contact_id_1=c2["id"],
                            contact_id_2=c1["id"],
                            connection_type=connection_type,
                            strength=strength,
                            shared_attributes=shared,
                        )
                    )

        logger.info(f"Граф построен: {len(self.graph)} вузлов")
        return self.graph

    def _detect_connection(
        self, c1: Dict, c2: Dict
    ) -> Tuple[Optional[ConnectionType], float, List[str]]:
        """Определить тип связи и её стренгтс"""
        shared = []
        strength = 0.0
        connection_type = None

        # Одна организация
        if c1.get("organization") and c1.get("organization") == c2.get("organization"):
            shared.append("organization")
            strength += 0.5
            connection_type = ConnectionType.COLLEAGUES

        # Один город
        if c1.get("location") and c1.get("location") == c2.get("location"):
            shared.append("location")
            strength += 0.3
            if not connection_type:
                connection_type = ConnectionType.PROXIMITY

        # Одни теги/группы
        tags1 = set(c1.get("tags", []))
        tags2 = set(c2.get("tags", []))
        shared_tags = tags1 & tags2

        if shared_tags:
            shared.extend(list(shared_tags))
            strength += 0.2 * len(shared_tags)
            if not connection_type:
                connection_type = ConnectionType.SOCIAL

        # Ключ для выхода если есть связь
        if connection_type:
            strength = min(strength, 1.0)
            return connection_type, strength, shared

        return None, 0.0, []

    def calculate_centrality_measures(self) -> Dict[str, Dict]:
        """Рассчитать центральность для каждого вузла"""

        results = {}
        total_nodes = len(self.graph)

        for contact_id, node in self.graph.items():
            # Degree centrality (сколько связей)
            degree = len(node.connections)
            node.degree_centrality = degree / (total_nodes - 1) if total_nodes > 1 else 0.0

            # Betweenness centrality (нода как "поворотная точка")
            # Прымой сдвиговые пути
            betweenness = self._calculate_betweenness(contact_id)
            node.betweenness_centrality = betweenness

            # Influence score (влияние)
            node.influence_score = (
                node.degree_centrality * 0.4
                + node.betweenness_centrality * 0.4
                + (
                    sum(c.strength for c in node.connections) / len(node.connections)
                    if node.connections
                    else 0
                )
                * 0.2
            )

            results[contact_id] = {
                "degree_centrality": node.degree_centrality,
                "betweenness_centrality": node.betweenness_centrality,
                "influence_score": node.influence_score,
                "connections_count": degree,
            }

        return results

    def _calculate_betweenness(self, node_id: str) -> float:
        """Построить график Betweenness centrality
        Определяет ноду как 'мост' в сети
        """
        # Найти количество кратчайших путей, подождаўщих через тот же нод
        betweenness = 0.0
        shortest_paths = self._all_pairs_shortest_paths()

        for source in self.graph:
            for target in self.graph:
                if source != target and source != node_id and target != node_id:
                    # Если путь проходит через node_id
                    path_key = (source, target)
                    if path_key in shortest_paths and node_id in shortest_paths[path_key]:
                        betweenness += 1.0

        # Нормализация
        max_betweenness = (len(self.graph) - 1) * (len(self.graph) - 2) / 2.0
        return betweenness / max_betweenness if max_betweenness > 0 else 0.0

    def _all_pairs_shortest_paths(self) -> Dict[Tuple, List[str]]:
        """Найти все кратчайшие пути между всеми парами вузлов
        BFS algorithm
        """
        paths = {}

        for start_id in self.graph:
            # BFS из каждого вузла
            distances, predecessors = self._bfs(start_id)

            for end_id in self.graph:
                if start_id != end_id:
                    path = self._reconstruct_path(start_id, end_id, predecessors)
                    paths[(start_id, end_id)] = path

        return paths

    def _bfs(self, start_id: str) -> Tuple[Dict, Dict]:
        """Ширинный поиск в ширину"""
        distances = {node_id: float("inf") for node_id in self.graph}
        distances[start_id] = 0
        predecessors = {node_id: None for node_id in self.graph}

        queue = deque([start_id])

        while queue:
            current = queue.popleft()

            for connection in self.graph[current].connections:
                neighbor = connection.contact_id_2

                if distances[neighbor] > distances[current] + 1:
                    distances[neighbor] = distances[current] + 1
                    predecessors[neighbor] = current
                    queue.append(neighbor)

        return distances, predecessors

    def _reconstruct_path(self, start_id: str, end_id: str, predecessors: Dict) -> List[str]:
        """Реконструировать путь из вспомогательных данных"""
        path = []
        current = end_id

        while current is not None:
            path.append(current)
            current = predecessors[current]

        path.reverse()
        return path if path[0] == start_id else []

    def find_influencers(self, top_n: int = 10) -> List[Dict]:
        """Найти топ влиятелей"""
        influencers = []

        for contact_id, node in self.graph.items():
            influencers.append(
                {
                    "contact_id": contact_id,
                    "name": node.name,
                    "influence_score": node.influence_score,
                    "connections": len(node.connections),
                    "organization": node.organization,
                }
            )

        # Сортировать по influence_score
        influencers.sort(key=lambda x: x["influence_score"], reverse=True)

        return influencers[:top_n]

    def detect_communities(self, resolution: float = 1.0) -> Dict[int, List[str]]:
        """Найти коммунитеты (группы тесно связанных контактов)
        Конитец Louvain algorithm (simplified)
        """
        # Определить каждым нодам откытою коммунитета
        community_id = 0
        assigned = set()
        communities = defaultdict(list)

        # Простое равъждательное воскох (удар)
        for node_id, node in self.graph.items():
            if node_id not in assigned:
                # BFS для нахождения коннектед компоненты
                component = self._dfs_component(node_id, assigned)

                for component_node in component:
                    communities[community_id].append(component_node)
                    self.graph[component_node].community_id = community_id

                community_id += 1

        return dict(communities)

    def _dfs_component(self, start_id: str, assigned: Set[str]) -> List[str]:
        """Найти все вузлы в коннектед компоненте
        DFS algorithm
        """
        component = []
        stack = [start_id]

        while stack:
            current = stack.pop()

            if current not in assigned:
                assigned.add(current)
                component.append(current)

                for connection in self.graph[current].connections:
                    neighbor = connection.contact_id_2
                    if neighbor not in assigned:
                        stack.append(neighbor)

        return component

    def find_shortest_path(self, start_id: str, end_id: str) -> Tuple[List[str], float]:
        """Найти кратчайший путь между двумя контактами
        Возвращает: (path, distance)
        """
        distances, predecessors = self._bfs(start_id)
        path = self._reconstruct_path(start_id, end_id, predecessors)
        distance = distances[end_id]

        return path, distance

    async def save_to_database(self) -> Dict:
        """Сохранить граф связей в Supabase"""

        # Сохранить связи
        connections_data = []

        for node in self.graph.values():
            for conn in node.connections:
                # Обработать дубликаты (save only one direction)
                if conn.contact_id_1 < conn.contact_id_2:  # Применить канонический порядок
                    connections_data.append(
                        {
                            "contact_id_1": conn.contact_id_1,
                            "contact_id_2": conn.contact_id_2,
                            "connection_type": conn.connection_type.value,
                            "strength": conn.strength,
                            "weight": conn.weight,
                            "shared_attributes": conn.shared_attributes,
                        }
                    )

        # Обработать все связи
        response = (
            await self.supabase.table("contact_connections").insert(connections_data).execute()
        )

        # Обновить метрики контактов
        for contact_id, node in self.graph.items():
            await self.supabase.table("apple_contacts").update(
                {
                    "influence_score": node.influence_score,
                    "community_id": node.community_id,
                    "degree_centrality": node.degree_centrality,
                    "betweenness_centrality": node.betweenness_centrality,
                }
            ).eq("id", contact_id).execute()

        logger.info(f"Сохранено {len(connections_data)} связей")

        return {"connections_saved": len(connections_data), "contacts_updated": len(self.graph)}

    async def get_statistics(self) -> Dict:
        """Получить статистику социальной сети"""

        total_connections = sum(len(node.connections) for node in self.graph.values()) // 2

        influencers = self.find_influencers(top_n=10)
        communities = self.detect_communities()

        return {
            "total_nodes": len(self.graph),
            "total_connections": total_connections,
            "average_connections": total_connections * 2 / len(self.graph) if self.graph else 0,
            "top_influencers": influencers,
            "communities": {k: len(v) for k, v in communities.items()},
            "network_density": (
                (total_connections * 2) / (len(self.graph) * (len(self.graph) - 1))
                if len(self.graph) > 1
                else 0
            ),
        }


# Usage example:
"""
async def example_usage():
    analyzer = SocialNetworkAnalyzer(supabase_client)
    
    # Получить все контакты
    contacts = supabase.table('apple_contacts').select('*').execute().data
    
    # Построить граф
    graph = await analyzer.build_graph(contacts)
    
    # Обновить центральность
    centrality = analyzer.calculate_centrality_measures()
    
    # Найти влиятелей
    influencers = analyzer.find_influencers(top_n=20)
    
    # Найти коммунитеты
    communities = analyzer.detect_communities()
    
    # Найти путь
    path, distance = analyzer.find_shortest_path('id1', 'id2')
    
    # Сохранить в БД
    await analyzer.save_to_database()
    
    # Получить статистику
    stats = await analyzer.get_statistics()
    print(stats)
"""
